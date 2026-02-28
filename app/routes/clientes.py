from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..db import connect
import sqlite3

bp = Blueprint("clientes", __name__)


def _get_cliente(cliente_id: int):
    with connect() as conn:
        return conn.execute(
            "SELECT id, nombre, cedula, email, telefono FROM clientes WHERE id=?",
            (cliente_id,),
        ).fetchone()


def _email_ya_existe(email: str, exclude_id: int | None = None) -> bool:
    if not email:
        return False
    with connect() as conn:
        if exclude_id is None:
            row = conn.execute("SELECT 1 FROM clientes WHERE email=? LIMIT 1", (email,)).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM clientes WHERE email=? AND id<>? LIMIT 1",
                (email, exclude_id),
            ).fetchone()
    return row is not None


def _cedula_ya_existe(cedula: str, exclude_id: int | None = None) -> bool:
    if not cedula:
        return False
    with connect() as conn:
        if exclude_id is None:
            row = conn.execute("SELECT 1 FROM clientes WHERE cedula=? LIMIT 1", (cedula,)).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM clientes WHERE cedula=? AND id<>? LIMIT 1",
                (cedula, exclude_id),
            ).fetchone()
    return row is not None


@bp.route("/")
def index():
    q = (request.args.get("q") or "").strip()

    with connect() as conn:
        if q:
            like = f"%{q}%"
            clientes = conn.execute(
                """
                SELECT c.id, c.nombre, c.cedula, c.email, c.telefono,
                       COUNT(p.id) AS pedidos_count
                FROM clientes c
                LEFT JOIN pedidos p ON p.cliente_id = c.id
                WHERE c.nombre LIKE ?
                   OR IFNULL(c.cedula,'') LIKE ?
                   OR IFNULL(c.email,'') LIKE ?
                   OR IFNULL(c.telefono,'') LIKE ?
                GROUP BY c.id
                ORDER BY c.nombre
                """,
                (like, like, like, like),
            ).fetchall()
        else:
            clientes = conn.execute(
                """
                SELECT c.id, c.nombre, c.cedula, c.email, c.telefono,
                       COUNT(p.id) AS pedidos_count
                FROM clientes c
                LEFT JOIN pedidos p ON p.cliente_id = c.id
                GROUP BY c.id
                ORDER BY c.nombre
                """
            ).fetchall()

    return render_template("clientes_list.html", titulo="Clientes", clientes=clientes, q=q)


@bp.route("/nuevo", methods=["GET", "POST"])
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

    # ✅ Validación de unicidad a nivel app (sin migración pesada)
    if cedula and _cedula_ya_existe(cedula):
        flash("La cédula ya está registrada para otro cliente.", "error")
        return redirect(url_for("clientes.nuevo"))

    # ✅ Validación de email duplicado (pre-check) + IntegrityError por seguridad
    if email and _email_ya_existe(email):
        flash("Ese email ya está registrado para otro cliente.", "error")
        return redirect(url_for("clientes.nuevo"))

    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO clientes (nombre, cedula, email, telefono) VALUES (?, ?, ?, ?)",
                (nombre, cedula, email, telefono),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        # Por si se nos escapa por carrera / datos viejos
        flash("No se pudo crear el cliente (email duplicado).", "error")
        return redirect(url_for("clientes.nuevo"))

    flash("Cliente creado.", "success")
    return redirect(url_for("clientes.index"))


@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
def editar(cliente_id: int):
    cliente = _get_cliente(cliente_id)
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

    # ✅ Unicidad de cédula a nivel app
    if cedula and _cedula_ya_existe(cedula, exclude_id=cliente_id):
        flash("La cédula ya está registrada para otro cliente.", "error")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))

    # ✅ Email duplicado sin except genérico
    if email and _email_ya_existe(email, exclude_id=cliente_id):
        flash("Ese email ya está registrado para otro cliente.", "error")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))

    try:
        with connect() as conn:
            conn.execute(
                "UPDATE clientes SET nombre=?, cedula=?, email=?, telefono=? WHERE id=?",
                (nombre, cedula, email, telefono, cliente_id),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        flash("No se pudo actualizar (email duplicado).", "error")
        return redirect(url_for("clientes.editar", cliente_id=cliente_id))

    flash("Cliente actualizado.", "success")
    return redirect(url_for("clientes.index"))


@bp.route("/<int:cliente_id>/eliminar", methods=["POST"])
def eliminar(cliente_id: int):
    # ✅ Validación “no borrar si tiene pedidos”
    with connect() as conn:
        pedidos_count = conn.execute(
            "SELECT COUNT(1) AS n FROM pedidos WHERE cliente_id=?",
            (cliente_id,),
        ).fetchone()["n"]

        if pedidos_count > 0:
            flash("No se pudo eliminar: el cliente tiene pedidos asociados.", "error")
            return redirect(url_for("clientes.index"))

        conn.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
        conn.commit()

    flash("Cliente eliminado.", "success")
    return redirect(url_for("clientes.index"))