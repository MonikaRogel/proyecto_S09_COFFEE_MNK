from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db, admin_required
from ..models import Cliente
from sqlalchemy import or_

bp = Blueprint("clientes", __name__)

def _email_ya_existe(email: str, exclude_id: int | None = None) -> bool:
    if not email:
        return False
    query = Cliente.query.filter_by(email=email)
    if exclude_id:
        query = query.filter(Cliente.id != exclude_id)
    return query.first() is not None

def _cedula_ya_existe(cedula: str, exclude_id: int | None = None) -> bool:
    if not cedula:
        return False
    query = Cliente.query.filter_by(cedula=cedula)
    if exclude_id:
        query = query.filter(Cliente.id != exclude_id)
    return query.first() is not None

@bp.route("/")
@admin_required
def index():
    q = (request.args.get("q") or "").strip()
    if q:
        like = f"%{q}%"
        clientes = Cliente.query.filter(
            or_(
                Cliente.nombre.ilike(like),
                Cliente.cedula.ilike(like),
                Cliente.email.ilike(like),
                Cliente.telefono.ilike(like)
            )
        ).order_by(Cliente.nombre).all()
    else:
        clientes = Cliente.query.order_by(Cliente.nombre).all()

    clientes_list = []
    for c in clientes:
        clientes_list.append({
            "id": c.id,
            "nombre": c.nombre,
            "cedula": c.cedula,
            "email": c.email,
            "telefono": c.telefono,
            "pedidos_count": len(c.pedidos)
        })
    return render_template("clientes_list.html", titulo="Clientes", clientes=clientes_list, q=q)

@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    if request.method == "GET":
        return render_template("cliente_form.html", titulo="Nuevo cliente", cliente=None)

    nombre = (request.form.get("nombre") or "").strip()
    cedula = (request.form.get("cedula") or "").strip() or None
    email = (request.form.get("email") or "").strip() or None
    telefono = (request.form.get("telefono") or "").strip() or None

    if not nombre:
        flash("El nombre es obligatorio.", "error")
        return redirect(url_for("clientes.nuevo"))

    if cedula and _cedula_ya_existe(cedula):
        flash("La cédula ya está registrada para otro cliente.", "error")
        return redirect(url_for("clientes.nuevo"))

    if email and _email_ya_existe(email):
        flash("Ese email ya está registrado para otro cliente.", "error")
        return redirect(url_for("clientes.nuevo"))

    try:
        cliente = Cliente(nombre=nombre, cedula=cedula, email=email, telefono=telefono)
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente creado.", "success")
        return redirect(url_for("clientes.index"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear cliente: {str(e)}", "error")
        return redirect(url_for("clientes.nuevo"))

@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(cliente_id: int):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("clientes.index"))

    if request.method == "GET":
        return render_template("cliente_form.html", titulo="Editar cliente", cliente=cliente)

    nombre = (request.form.get("nombre") or "").strip()
    cedula = (request.form.get("cedula") or "").strip() or None
    email = (request.form.get("email") or "").strip() or None
    telefono = (request.form.get("telefono") or "").strip() or None

    if not nombre:
        flash("El nombre es obligatorio.", "error")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))

    if cedula and _cedula_ya_existe(cedula, exclude_id=cliente_id):
        flash("La cédula ya está registrada para otro cliente.", "error")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))

    if email and _email_ya_existe(email, exclude_id=cliente_id):
        flash("Ese email ya está registrado para otro cliente.", "error")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))

    try:
        cliente.nombre = nombre
        cliente.cedula = cedula
        cliente.email = email
        cliente.telefono = telefono
        db.session.commit()
        flash("Cliente actualizado.", "success")
        return redirect(url_for("clientes.index"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar cliente: {str(e)}", "error")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))

@bp.route("/<int:cliente_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(cliente_id: int):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("clientes.index"))

    if len(cliente.pedidos) > 0:
        flash("No se pudo eliminar: el cliente tiene pedidos asociados.", "error")
        return redirect(url_for("clientes.index"))

    try:
        db.session.delete(cliente)
        db.session.commit()
        flash("Cliente eliminado.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar cliente: {str(e)}", "error")

    return redirect(url_for("clientes.index"))