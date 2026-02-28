from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..db import connect
import sqlite3
from datetime import datetime

bp = Blueprint("pedidos", __name__)

ESTADOS_PERMITIDOS = ["En preparación", "Listo", "Entregado", "Cancelado"]


# ---------- Ruta: listado de pedidos ----------
@bp.route("/")
def index():
    estado = (request.args.get("estado") or "").strip()

    with connect() as conn:
        if estado:
            pedidos = conn.execute("""
                SELECT p.id, p.fecha, p.estado, p.total,
                       c.nombre AS cliente_nombre
                FROM pedidos p
                JOIN clientes c ON c.id = p.cliente_id
                WHERE p.estado = ?
                ORDER BY p.id DESC
            """, (estado,)).fetchall()
        else:
            pedidos = conn.execute("""
                SELECT p.id, p.fecha, p.estado, p.total,
                       c.nombre AS cliente_nombre
                FROM pedidos p
                JOIN clientes c ON c.id = p.cliente_id
                ORDER BY p.id DESC
            """).fetchall()

    return render_template("pedidos_list.html", titulo="Pedidos", pedidos=pedidos, estado=estado)


# ---------- Ruta: nuevo pedido ----------
@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    pre_producto = (request.args.get("producto") or "").lower().strip()

    # GET
    if request.method == "GET":
        with connect() as conn:
            productos = conn.execute("""
                SELECT slug, nombre, precio, stock
                FROM productos
                ORDER BY nombre
            """).fetchall()

            clientes = conn.execute("""
                SELECT id, nombre, email
                FROM clientes
                ORDER BY nombre
            """).fetchall()

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

    # Validar producto
    if not producto_slug:
        flash("Debes seleccionar un producto.", "error")
        return redirect(url_for("pedidos.nuevo"))

    # Validar cantidad
    try:
        cantidad = int(cantidad_raw)
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        flash("La cantidad debe ser un número entero positivo.", "error")
        return redirect(url_for("pedidos.nuevo", producto=producto_slug))

    with connect() as conn:
        # 1) Determinar cliente: nuevo o existente
        if cliente_nombre:
            # Crear cliente nuevo (opcionalmente con email único)
            try:
                cur = conn.execute(
                    "INSERT INTO clientes (nombre, cedula, email, telefono) VALUES (?, ?, ?, ?)",
                    (cliente_nombre, cliente_cedula, cliente_email, cliente_telefono),
                )
                cliente_id = cur.lastrowid
            except sqlite3.IntegrityError:
                flash("No se pudo crear el cliente (email duplicado o restricción).", "error")
                return redirect(url_for("pedidos.nuevo", producto=producto_slug))
        else:
            # Usar cliente existente
            if not cliente_id_raw.isdigit():
                flash("Selecciona un cliente existente o escribe un cliente nuevo.", "error")
                return redirect(url_for("pedidos.nuevo", producto=producto_slug))
            cliente_id = int(cliente_id_raw)

        cliente = conn.execute(
            "SELECT id, nombre FROM clientes WHERE id = ?",
            (cliente_id,),
        ).fetchone()

        if not cliente:
            flash("Cliente no encontrado.", "error")
            return redirect(url_for("pedidos.nuevo", producto=producto_slug))

        # 2) Obtener producto + validar stock
        producto = conn.execute(
            "SELECT id, nombre, precio, stock FROM productos WHERE slug = ?",
            (producto_slug,),
        ).fetchone()

        if not producto:
            flash("Producto no encontrado.", "error")
            return redirect(url_for("pedidos.nuevo"))

        if producto["stock"] < cantidad:
            flash(
                f"Stock insuficiente para {producto['nombre']}. Disponible: {producto['stock']}.",
                "error",
            )
            return redirect(url_for("pedidos.nuevo", producto=producto_slug))

        # 3) Crear pedido + item + descontar stock
        subtotal = round(producto["precio"] * cantidad, 2)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur = conn.execute(
            "INSERT INTO pedidos (cliente_id, fecha, estado, notas, total) VALUES (?, ?, ?, ?, ?)",
            (cliente["id"], fecha, "En preparación", notas, subtotal),
        )
        pedido_id = cur.lastrowid

        conn.execute(
            "INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (pedido_id, producto["id"], cantidad, producto["precio"], subtotal),
        )

        # Descontar stock al crear el pedido
        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (cantidad, producto["id"]),
        )

        conn.commit()

    flash(f"Pedido #{pedido_id} registrado correctamente para {cliente['nombre']}.", "success")
    return redirect(url_for("pedidos.detalle", pedido_id=pedido_id))


# ---------- Ruta: detalle de pedido ----------
@bp.route("/<int:pedido_id>")
def detalle(pedido_id: int):
    with connect() as conn:
        pedido = conn.execute("""
            SELECT p.id, p.fecha, p.estado, p.notas, p.total,
                   c.nombre AS cliente_nombre
            FROM pedidos p
            JOIN clientes c ON c.id = p.cliente_id
            WHERE p.id = ?
        """, (pedido_id,)).fetchone()

        if not pedido:
            flash("Pedido no encontrado.", "error")
            return redirect(url_for("pedidos.index"))

        items = conn.execute("""
            SELECT pr.nombre AS producto_nombre,
                   pi.producto_id,
                   pi.precio_unitario,
                   pi.cantidad,
                   pi.subtotal
            FROM pedido_items pi
            JOIN productos pr ON pr.id = pi.producto_id
            WHERE pi.pedido_id = ?
        """, (pedido_id,)).fetchall()

    return render_template(
        "pedido_detalle.html",
        titulo=f"Pedido #{pedido_id}",
        pedido=pedido,
        items=items,
        estados=ESTADOS_PERMITIDOS,
    )


# ---------- Ruta: cambiar estado de un pedido (con devolución de stock al cancelar) ----------
@bp.route("/<int:pedido_id>/estado", methods=["POST"])
def cambiar_estado(pedido_id: int):
    nuevo_estado = (request.form.get("estado") or "").strip()

    if nuevo_estado not in ESTADOS_PERMITIDOS:
        flash("Estado no válido.", "error")
        return redirect(url_for("pedidos.detalle", pedido_id=pedido_id))

    with connect() as conn:
        pedido = conn.execute(
            "SELECT id, estado FROM pedidos WHERE id = ?",
            (pedido_id,),
        ).fetchone()

        if not pedido:
            flash("Pedido no encontrado.", "error")
            return redirect(url_for("pedidos.index"))

        estado_anterior = pedido["estado"]

        # Si ya está Cancelado, lo tratamos como final (evita doble devolución)
        if estado_anterior == "Cancelado" and nuevo_estado != "Cancelado":
            flash("No se permite cambiar un pedido cancelado.", "error")
            return redirect(url_for("pedidos.detalle", pedido_id=pedido_id))

        # ✅ Si pasa a Cancelado desde otro estado => devolver stock (una sola vez)
        if estado_anterior != "Cancelado" and nuevo_estado == "Cancelado":
            items = conn.execute("""
                SELECT producto_id, cantidad
                FROM pedido_items
                WHERE pedido_id = ?
            """, (pedido_id,)).fetchall()

            for it in items:
                conn.execute(
                    "UPDATE productos SET stock = stock + ? WHERE id = ?",
                    (it["cantidad"], it["producto_id"]),
                )

        # Actualizar estado
        conn.execute(
            "UPDATE pedidos SET estado = ? WHERE id = ?",
            (nuevo_estado, pedido_id),
        )

        conn.commit()

    flash(f"Estado actualizado a '{nuevo_estado}'.", "success")
    return redirect(url_for("pedidos.detalle", pedido_id=pedido_id))