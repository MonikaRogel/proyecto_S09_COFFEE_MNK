from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ..extensions import db, admin_required
from ..forms.producto_form import ProductoForm
from ..services.producto_service import get_all, get_by_id, create, update, delete
from ..models import Producto, PedidoItem

bp = Blueprint("productos", __name__)

def _fetch_menu_dict():
    productos = Producto.query.order_by(Producto.id.desc()).all()
    menu = {}
    for p in productos:
        menu[p.slug] = {
            "id": p.id,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
            "img": p.img or "",
            "desc": p.descripcion or "",
        }
    return menu

# ---------- Rutas públicas ----------
@bp.route("/")
def index():
    menu = _fetch_menu_dict()
    return render_template("productos/menu.html", titulo="Menú", menu=menu)

@bp.route("/<slug>")
def detalle(slug: str):
    slug = slug.lower().strip()
    producto = Producto.query.filter_by(slug=slug).first()
    if not producto:
        flash("El producto solicitado no existe.", "error")
        return redirect(url_for("productos.index"))
    prod_dict = {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "stock": producto.stock,
        "img": producto.img or "",
        "desc": producto.descripcion or "",
    }
    return render_template(
        "productos/detalle.html",
        titulo=f"Producto - {producto.nombre}",
        slug=slug,
        producto=prod_dict,
    )

# ---------- Rutas administrativas ----------
@bp.route("/inventario")
@admin_required
def inventario():
    menu = _fetch_menu_dict()
    total_skus = len(menu)
    total_stock = sum(p["stock"] for p in menu.values())
    return render_template(
        "productos/inventario.html",
        titulo="Inventario",
        menu=menu,
        total_skus=total_skus,
        total_stock=total_stock,
    )

@bp.route("/admin")
@admin_required
def admin():
    productos = get_all()
    return render_template("productos/admin.html", titulo="Administrar Productos", productos=productos)

@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    form = ProductoForm()
    if form.validate_on_submit():
        data = {
            'slug': form.slug.data,
            'nombre': form.nombre.data,
            'precio': form.precio.data,
            'stock': form.stock.data,
            'img': form.img.data,
            'descripcion': form.descripcion.data
        }
        create(data)
        flash("Producto creado", "success")
        return redirect(url_for("productos.admin"))
    return render_template("productos/form.html", form=form, titulo="Nuevo Producto")

@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar(id):
    producto = get_by_id(id)
    form = ProductoForm(obj=producto)
    if form.validate_on_submit():
        data = {
            'slug': form.slug.data,
            'nombre': form.nombre.data,
            'precio': form.precio.data,
            'stock': form.stock.data,
            'img': form.img.data,
            'descripcion': form.descripcion.data
        }
        update(id, data)
        flash("Producto actualizado", "success")
        return redirect(url_for("productos.admin"))
    return render_template("productos/form.html", form=form, titulo="Editar Producto")

@bp.route("/<int:id>/eliminar", methods=["POST"])
@admin_required
def eliminar(id):
    try:
        delete(id)
        flash("Producto eliminado", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("productos.admin"))