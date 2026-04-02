from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from extensions import db, admin_required
from forms.cliente_form import ClienteForm
from services.cliente_service import get_all, get_by_id, create, update, delete
from models import Cliente
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
        clientes = get_all()

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
    return render_template("clientes/list.html", titulo="Clientes", clientes=clientes_list, q=q)

@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    form = ClienteForm()
    if form.validate_on_submit():
        data = {
            'nombre': form.nombre.data,
            'cedula': form.cedula.data or None,
            'email': form.email.data or None,
            'telefono': form.telefono.data or None
        }
        if data['cedula'] and _cedula_ya_existe(data['cedula']):
            flash("La cédula ya está registrada para otro cliente.", "error")
            return redirect(url_for("clientes.nuevo"))
        if data['email'] and _email_ya_existe(data['email']):
            flash("Ese email ya está registrado para otro cliente.", "error")
            return redirect(url_for("clientes.nuevo"))
        try:
            create(data)
            flash("Cliente creado.", "success")
            return redirect(url_for("clientes.index"))
        except Exception as e:
            flash(f"Error al crear cliente: {str(e)}", "error")
    return render_template("clientes/form.html", form=form, titulo="Nuevo Cliente")

@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(cliente_id: int):
    cliente = get_by_id(cliente_id)
    form = ClienteForm(obj=cliente)
    if form.validate_on_submit():
        data = {
            'nombre': form.nombre.data,
            'cedula': form.cedula.data or None,
            'email': form.email.data or None,
            'telefono': form.telefono.data or None
        }
        if data['cedula'] and _cedula_ya_existe(data['cedula'], exclude_id=cliente_id):
            flash("La cédula ya está registrada para otro cliente.", "error")
            return redirect(url_for("clientes.editar", cliente_id=cliente_id))
        if data['email'] and _email_ya_existe(data['email'], exclude_id=cliente_id):
            flash("Ese email ya está registrado para otro cliente.", "error")
            return redirect(url_for("clientes.editar", cliente_id=cliente_id))
        try:
            update(cliente_id, data)
            flash("Cliente actualizado.", "success")
            return redirect(url_for("clientes.index"))
        except Exception as e:
            flash(f"Error al actualizar cliente: {str(e)}", "error")
    return render_template("clientes/form.html", form=form, titulo="Editar Cliente")

@bp.route("/<int:cliente_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(cliente_id: int):
    try:
        delete(cliente_id)
        flash("Cliente eliminado.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("clientes.index"))