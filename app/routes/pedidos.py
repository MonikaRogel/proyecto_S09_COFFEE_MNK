from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db, admin_required
from ..models import Pedido, Cliente, Producto, PedidoItem
from datetime import datetime
import re

bp = Blueprint("pedidos", __name__)
ESTADOS_PERMITIDOS = ["En preparación", "Listo", "Entregado", "Cancelado"]

# Validaciones para cliente
def validar_cedula(cedula):
    return re.match(r'^\d{10}$', cedula) is not None

def validar_telefono(telefono):
    return re.match(r'^09\d{8}$', telefono) is not None

# ---------- Listado de pedidos (solo admin) ----------
@bp.route("/")
@admin_required
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

# ---------- Crear pedido ----------
@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    pre_producto = (request.args.get("producto") or "").lower().strip()

    if request.method == "GET":
        productos = Producto.query.order_by(Producto.nombre).all()

        if current_user.es_admin:
            # Admin: puede elegir cliente existente o crear nuevo
            clientes = Cliente.query.order_by(Cliente.nombre).all()
            return render_template(
                "pedido_nuevo.html",
                titulo="Nuevo pedido",
                productos=productos,
                clientes=clientes,
                pre_producto=pre_producto
            )
        else:
            # Cliente normal: usar su propio cliente
            cliente = Cliente.query.filter_by(email=current_user.mail).first()
            if not cliente:
                # Crear automáticamente si no existe
                cliente = Cliente(nombre=current_user.nombre, email=current_user.mail)
                db.session.add(cliente)
                db.session.commit()
                flash("Se ha creado tu perfil de cliente automáticamente.", "info")
            return render_template(
                "pedido_nuevo_cliente.html",
                titulo="Nuevo pedido",
                productos=productos,
                cliente=cliente,
                pre_producto=pre_producto
            )

    # --- Procesar POST ---
    # Determinar cliente_id
    if current_user.es_admin:
        cliente_id_raw = (request.form.get("cliente_id") or "").strip()
        cliente_nombre = (request.form.get("cliente_nombre") or "").strip()
        cliente_cedula = (request.form.get("cliente_cedula") or "").strip() or None
        cliente_email = (request.form.get("cliente_email") or "").strip() or None
        cliente_telefono = (request.form.get("cliente_telefono") or "").strip() or None

        if cliente_nombre:
            # Crear nuevo cliente (validaciones)
            if cliente_cedula and not validar_cedula(cliente_cedula):
                flash("La cédula debe tener 10 dígitos numéricos.", "error")
                return redirect(url_for("pedidos.nuevo", producto=pre_producto))
            if cliente_telefono and not validar_telefono(cliente_telefono):
                flash("El teléfono debe comenzar con 09 y tener 10 dígitos.", "error")
                return redirect(url_for("pedidos.nuevo", producto=pre_producto))
            if cliente_email and Cliente.query.filter_by(email=cliente_email).first():
                flash("El email ya está registrado para otro cliente.", "error")
                return redirect(url_for("pedidos.nuevo", producto=pre_producto))
            try:
                cliente = Cliente(
                    nombre=cliente_nombre,
                    cedula=cliente_cedula,
                    email=cliente_email,
                    telefono=cliente_telefono
                )
                db.session.add(cliente)
                db.session.flush()
                cliente_id = cliente.id
            except Exception as e:
                db.session.rollback()
                flash(f"Error al crear cliente: {str(e)}", "error")
                return redirect(url_for("pedidos.nuevo", producto=pre_producto))
        else:
            # Usar cliente existente
            if not cliente_id_raw.isdigit():
                flash("Selecciona un cliente existente o escribe un cliente nuevo.", "error")
                return redirect(url_for("pedidos.nuevo", producto=pre_producto))
            cliente = Cliente.query.get(int(cliente_id_raw))
            if not cliente:
                flash("Cliente no encontrado.", "error")
                return redirect(url_for("pedidos.nuevo", producto=pre_producto))
            cliente_id = cliente.id
    else:
        # Cliente normal: usar su propio cliente
        cliente = Cliente.query.filter_by(email=current_user.mail).first()
        if not cliente:
            # Crear automáticamente si no existe
            cliente = Cliente(nombre=current_user.nombre, email=current_user.mail)
            db.session.add(cliente)
            db.session.commit()
            flash("Se ha creado tu perfil de cliente automáticamente.", "info")
        cliente_id = cliente.id

    # Producto y cantidad
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
        cliente_id=cliente_id,
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

    flash(f"Pedido #{pedido.id} registrado correctamente.", "success")
    return redirect(url_for("pedidos.detalle", pedido_id=pedido.id))

# ---------- Detalle de pedido ----------
@bp.route("/<int:pedido_id>")
@login_required
def detalle(pedido_id: int):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        flash("Pedido no encontrado.", "error")
        return redirect(url_for("pedidos.index"))

    # Solo admin o el propio cliente puede ver el pedido
    if not current_user.es_admin and pedido.cliente_id != current_user.id:
        flash("No tienes permiso para ver este pedido.", "error")
        return redirect(url_for("main.home"))

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

# ---------- Cambiar estado (solo admin) ----------
@bp.route("/<int:pedido_id>/estado", methods=["POST"])
@admin_required
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