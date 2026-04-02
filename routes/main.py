from flask import Blueprint, render_template
from models import Producto

bp = Blueprint("main", __name__)

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
def home():
    menu = _fetch_menu_dict()
    destacados = ["capuccino", "mocaccino", "latte"]
    return render_template("index.html", titulo="Inicio", menu=menu, destacados=destacados)

@bp.route("/about")
def about():
    return render_template("about.html", titulo="Acerca de")