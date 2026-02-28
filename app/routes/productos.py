from flask import Blueprint, render_template, redirect, url_for, flash
from ..db import connect

bp = Blueprint("productos", __name__)

def _fetch_menu_dict():
    """Devuelve un dict {slug: producto_dict} para reutilizar tus templates actuales."""
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, slug, nombre, precio, stock, img, descripcion
            FROM productos
            ORDER BY id DESC
        """).fetchall()

    menu = {}
    for r in rows:
        menu[r["slug"]] = {
            "id": r["id"],
            "nombre": r["nombre"],
            "precio": r["precio"],
            "stock": r["stock"],
            "img": r["img"] or "",
            "desc": r["descripcion"] or "",
        }
    return menu


@bp.route("/")
def index():
    # Menú de productos
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
    slug = (slug or "").lower().strip()
    menu = _fetch_menu_dict()

    if slug not in menu:
        flash("El producto solicitado no existe.", "error")
        return redirect(url_for("productos.index"))

    return render_template(
        "producto.html",
        titulo=f"Producto - {menu[slug]['nombre']}",
        slug=slug,
        producto=menu[slug],
    )