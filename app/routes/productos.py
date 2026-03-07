from flask import Blueprint, render_template, redirect, url_for, flash
from ..models import Producto

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

@bp.route("/")
def index():
    menu = _fetch_menu_dict()
    return render_template("menu.html", titulo="Menú", menu=menu)

@bp.route("/inventario")
def inventario():
    menu = _fetch_menu_dict()
    total_skus = len(menu)
    total_stock = sum(p["stock"] for p in menu.values())
    return render_template(
        "inventario.html",
        titulo="Inventario",
        menu=menu,
        total_skus=total_skus,
        total_stock=total_stock,
    )

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
        "producto.html",
        titulo=f"Producto - {producto.nombre}",
        slug=slug,
        producto=prod_dict,
    )