from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Pedido, Cliente, Producto, PedidoItem
from ..extensions import db
from datetime import datetime

bp = Blueprint("pedidos", __name__)

ESTADOS_PERMITIDOS = ["En preparación", "Listo", "Entregado", "Cancelado"]


@bp.route("/")
def index():
    estado = (request.args.get("estado") or "").strip()
    if estado:
        pedidos = Pedido.query.filter_by(estado=estado).order_by(Pedido.id.desc()).all()
    else:
        pedidos = Pedido.query.order_by(Pedido.id.desc()).all()

    pedidos_list = []
    for p in pedidos:
        pedidos_list.append({
            "id": p.id,
            "fecha": p.fecha,
            "estado": p.estado,
            "total": p.total,
            "cliente_nombre": p.cliente.nombre if p.cliente else "Desconocido",
        })
    return render_template("pedidos_list.html", titulo="Pedidos", pedidos=pedidos_list, estado=estado)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    pre_producto = (request.args.get("producto") or "").lower().strip()

    if request.method == "GET":
        productos = Producto.query.order_by(Producto.nombre).all()
        clientes = Cliente.query.order_by(Cliente.nombre).all()
        return render_template(
            "pedido_nuevo.html",
            titulo="Nuevo pedido",
            productos=productos,
            clientes=clientes,
            pre_producto=pre_producto,
        )

    # POST
    cliente_id_raw = (request.form.get("cliente_id") or "").strip()
    cliente_nombre = (request.form.get("cliente_nombre") or "").strip()
    cliente_cedula = (request.form.get("cliente_cedula") or "").strip() or None
    cliente_email = (request.form.get("cliente_email") or "").strip() or None
    cliente_telefono = (request.form.get("cliente_telefono") or "").strip() or None
    producto_slug = (request.form.get("producto") or "").lower().strip()
    cantidad_raw = (request.form.get("cantidad") or "1").strip()
    notas = (request.form.get("notas") or "").strip()

    if not producto_slug:
        flash("Debes seleccionar un producto.", "error")
        return redirect(url_for("pedidos.nuevo"))

    try:
        cantidad = int(cantidad_raw)
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        flash("La cantidad debe ser un número entero positivo.", "error")
        return redirect(url_for("pedidos.nuevo", producto=producto_slug))

    try:
        # Determinar cliente
        if cliente_nombre:
            cliente = Cliente(
                nombre=cliente_nombre,
                cedula=cliente_cedula,
                email=cliente_email,
                telefono=cliente_telefono
            )
            db.session.add(cliente)
            db.session.flush()
        else:
            if not cliente_id_raw.isdigit():
                flash("Selecciona un cliente existente o escribe un cliente nuevo.", "error")
                return redirect(url_for("pedidos.nuevo", producto=producto_slug))
            cliente = Cliente.query.get(int(cliente_id_raw))
            if not cliente:
                flash("Cliente no encontrado.", "error")
                return redirect(url_for("pedidos.nuevo", producto=producto_slug))

        # Producto
        producto = Producto.query.filter_by(slug=producto_slug).first()
        if not producto:
            flash("Producto no encontrado.", "error")
            return redirect(url_for("pedidos.nuevo"))

        if producto.stock < cantidad:
            flash(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}.", "error")
            return redirect(url_for("pedidos.nuevo", producto=producto_slug))

        # Crear pedido
        subtotal = round(producto.precio * cantidad, 2)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pedido = Pedido(
            cliente_id=cliente.id,
            fecha=fecha,
            estado="En preparación",
            notas=notas,
            total=subtotal
        )
        db.session.add(pedido)
        db.session.flush()

        item = PedidoItem(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=subtotal
        )
        db.session.add(item)
        producto.stock -= cantidad
        db.session.commit()

        flash(f"Pedido #{pedido.id} registrado correctamente para {cliente.nombre}.", "success")
        return redirect(url_for("pedidos.detalle", pedido_id=pedido.id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el pedido: {str(e)}", "error")
        return redirect(url_for("pedidos.nuevo", producto=producto_slug))


@bp.route("/<int:pedido_id>")
def detalle(pedido_id: int):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        flash("Pedido no encontrado.", "error")
        return redirect(url_for("pedidos.index"))

    items = []
    for it in pedido.items:
        items.append({
            "producto_nombre": it.producto.nombre,
            "producto_id": it.producto_id,
            "precio_unitario": it.precio_unitario,
            "cantidad": it.cantidad,
            "subtotal": it.subtotal,
        })

    pedido_dict = {
        "id": pedido.id,
        "fecha": pedido.fecha,
        "estado": pedido.estado,
        "notas": pedido.notas,
        "total": pedido.total,
        "cliente_nombre": pedido.cliente.nombre if pedido.cliente else "Desconocido",
    }
    return render_template(
        "pedido_detalle.html",
        titulo=f"Pedido #{pedido_id}",
        pedido=pedido_dict,
        items=items,
        estados=ESTADOS_PERMITIDOS,
    )


@bp.route("/<int:pedido_id>/estado", methods=["POST"])
def cambiar_estado(pedido_id: int):
    nuevo_estado = (request.form.get("estado") or "").strip()
    if nuevo_estado not in ESTADOS_PERMITIDOS:
        flash("Estado no válido.", "error")
        return redirect(url_for("pedidos.detalle", pedido_id=pedido_id))

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        flash("Pedido no encontrado.", "error")
        return redirect(url_for("pedidos.index"))

    estado_anterior = pedido.estado
    if estado_anterior == "Cancelado" and nuevo_estado != "Cancelado":
        flash("No se permite cambiar un pedido cancelado.", "error")
        return redirect(url_for("pedidos.detalle", pedido_id=pedido_id))

    try:
        if estado_anterior != "Cancelado" and nuevo_estado == "Cancelado":
            for item in pedido.items:
                producto = item.producto
                producto.stock += item.cantidad
        pedido.estado = nuevo_estado
        db.session.commit()
        flash(f"Estado actualizado a '{nuevo_estado}'.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al cambiar estado: {str(e)}", "error")

    return redirect(url_for("pedidos.detalle", pedido_id=pedido_id))