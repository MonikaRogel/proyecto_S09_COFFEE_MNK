from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..extensions import db, admin_required
from ..forms.usuario_form import UsuarioForm
from ..services.usuario_service import get_all, get_by_id, create, update, delete
from ..models import Usuario

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@bp.route("/")
@admin_required
def index():
    usuarios = get_all()
    return render_template("usuarios/list.html", titulo="Usuarios", usuarios=usuarios)

@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    form = UsuarioForm()
    if form.validate_on_submit():
        # Verificar si ya existe un usuario con ese email
        if Usuario.query.filter_by(mail=form.mail.data).first():
            flash("Ya existe un usuario con ese email", "error")
            return redirect(url_for("usuarios.nuevo"))
        data = {
            'nombre': form.nombre.data,
            'mail': form.mail.data,
            'telefono': form.telefono.data or None,
            'rol': form.rol.data
        }
        # Asignar contraseña
        if form.password.data:
            from werkzeug.security import generate_password_hash
            data['password'] = generate_password_hash(form.password.data)
        else:
            flash("La contraseña es obligatoria", "error")
            return redirect(url_for("usuarios.nuevo"))
        try:
            create(data)
            flash("Usuario creado", "success")
            return redirect(url_for("usuarios.index"))
        except Exception as e:
            flash(f"Error al crear usuario: {str(e)}", "error")
    return render_template("usuarios/form.html", form=form, titulo="Nuevo Usuario")

@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar(id):
    usuario = get_by_id(id)
    form = UsuarioForm(obj=usuario)
    if form.validate_on_submit():
        data = {
            'nombre': form.nombre.data,
            'mail': form.mail.data,
            'telefono': form.telefono.data or None,
            'rol': form.rol.data
        }
        # Si se proporcionó nueva contraseña, actualizar
        if form.password.data:
            from werkzeug.security import generate_password_hash
            data['password'] = generate_password_hash(form.password.data)
        try:
            update(id, data)
            flash("Usuario actualizado", "success")
            return redirect(url_for("usuarios.index"))
        except Exception as e:
            flash(f"Error al actualizar usuario: {str(e)}", "error")
    return render_template("usuarios/form.html", form=form, titulo="Editar Usuario")

@bp.route("/<int:id>/eliminar", methods=["POST"])
@admin_required
def eliminar(id):
    if id == current_user.id:
        flash("No puedes eliminar tu propio usuario.", "error")
        return redirect(url_for("usuarios.index"))
    try:
        delete(id)
        flash("Usuario eliminado", "success")
    except Exception as e:
        flash(f"Error al eliminar usuario: {str(e)}", "error")
    return redirect(url_for("usuarios.index"))