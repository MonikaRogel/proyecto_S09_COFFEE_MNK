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

    from flask import Blueprint, render_template, redirect, url_for, flash, request
    from ..models import Producto
    from ..extensions import db

    bp = Blueprint("productos", __name__)

# ... (código existente: index, inventario, detalle)

@bp.route("/admin")
def admin():
    """Lista administrativa de productos con opciones de editar/eliminar"""
    productos = Producto.query.order_by(Producto.nombre).all()
    return render_template("productos_admin.html", titulo="Administrar Productos", productos=productos)

@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        slug = request.form.get("slug", "").strip().lower()
        nombre = request.form.get("nombre", "").strip()
        precio = float(request.form.get("precio", 0))
        stock = int(request.form.get("stock", 0))
        img = request.form.get("img", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not slug or not nombre or precio <= 0:
            flash("Datos inválidos", "error")
            return redirect(url_for("productos.nuevo"))

        if Producto.query.filter_by(slug=slug).first():
            flash("Ya existe un producto con ese slug", "error")
            return redirect(url_for("productos.nuevo"))

        producto = Producto(
            slug=slug,
            nombre=nombre,
            precio=precio,
            stock=stock,
            img=img,
            descripcion=descripcion
        )
        db.session.add(producto)
        db.session.commit()
        flash("Producto creado", "success")
        return redirect(url_for("productos.admin"))

    return render_template("producto_form.html", titulo="Nuevo Producto", producto=None)

@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    producto = Producto.query.get_or_404(id)
    if request.method == "POST":
        producto.slug = request.form.get("slug", "").strip().lower()
        producto.nombre = request.form.get("nombre", "").strip()
        producto.precio = float(request.form.get("precio", 0))
        producto.stock = int(request.form.get("stock", 0))
        producto.img = request.form.get("img", "").strip()
        producto.descripcion = request.form.get("descripcion", "").strip()

        db.session.commit()
        flash("Producto actualizado", "success")
        return redirect(url_for("productos.admin"))

    return render_template("producto_form.html", titulo="Editar Producto", producto=producto)

@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    # Verificar si tiene pedidos asociados (opcional, para no eliminar si está en uso)
    from ..models import PedidoItem
    if PedidoItem.query.filter_by(producto_id=id).first():
        flash("No se puede eliminar porque tiene pedidos asociados", "error")
        return redirect(url_for("productos.admin"))

    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado", "success")
    return redirect(url_for("productos.admin"))