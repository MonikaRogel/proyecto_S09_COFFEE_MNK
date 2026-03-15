from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Usuario
from ..extensions import db

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@bp.route("/")
def index():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_template("usuarios_list.html", titulo="Usuarios", usuarios=usuarios)

@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        mail = request.form.get("mail", "").strip()
        password = request.form.get("password", "").strip()

        if not nombre or not mail or not password:
            flash("Todos los campos son obligatorios", "error")
            return redirect(url_for("usuarios.nuevo"))

        if Usuario.query.filter_by(mail=mail).first():
            flash("Ya existe un usuario con ese email", "error")
            return redirect(url_for("usuarios.nuevo"))

        usuario = Usuario(nombre=nombre, mail=mail, password=password)
        db.session.add(usuario)
        db.session.commit()
        flash("Usuario creado", "success")
        return redirect(url_for("usuarios.index"))

    return render_template("usuario_form.html", titulo="Nuevo Usuario", usuario=None)

@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == "POST":
        usuario.nombre = request.form.get("nombre", "").strip()
        usuario.mail = request.form.get("mail", "").strip()
        nueva_pass = request.form.get("password", "").strip()
        if nueva_pass:
            usuario.password = nueva_pass
        db.session.commit()
        flash("Usuario actualizado", "success")
        return redirect(url_for("usuarios.index"))

    return render_template("usuario_form.html", titulo="Editar Usuario", usuario=usuario)

@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado", "success")
    return redirect(url_for("usuarios.index"))