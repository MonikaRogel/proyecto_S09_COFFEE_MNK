from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "coffee_mnk_secret_key"  # Necesario para usar flash messages (demo académica)

# Catálogo simulado (precio + stock + imagen + descripción)
MENU = {
    "capuccino": {
        "nombre": "Capuccino",
        "precio": 2.75,
        "stock": 18,
        "img": "https://images.unsplash.com/photo-1481391319762-47dff72954d9?auto=format&fit=crop&w=1200&q=70",
        "desc": "Café espresso con espuma de leche, balanceado y cremoso."
    },
    "mocaccino": {
        "nombre": "Mocaccino",
        "precio": 3.25,
        "stock": 12,
        "img": "https://images.unsplash.com/photo-1511920170033-f8396924c348?auto=format&fit=crop&w=1200&q=70",
        "desc": "Mezcla de café, chocolate y leche, ideal para un sabor dulce."
    },
    "latte": {
        "nombre": "Latte",
        "precio": 3.00,
        "stock": 20,
        "img": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=70",
        "desc": "Café con leche vaporizada, suave y perfecto para cualquier hora."
    },
    "espresso": {
        "nombre": "Espresso",
        "precio": 2.00,
        "stock": 25,
        "img": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=1200&q=70",
        "desc": "Clásico espresso intenso, corto y aromático."
    },
}

# Pedidos simulados (persisten mientras el servicio esté activo)
ORDERS = []  # Cada pedido: dict con id, cliente, items, total, fecha, estado, notas

# Manejo de favicon
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

# Página principal
@app.route("/")
def home():
    destacados = ["capuccino", "mocaccino", "latte"]
    return render_template("index.html", titulo="Inicio", destacados=destacados, menu=MENU)

# Página "Acerca de"
@app.route("/about")
def about():
    return render_template("about.html", titulo="Acerca de")

# Página de menú (productos)
@app.route("/menu")
def menu():
    return render_template("menu.html", titulo="Menú", menu=MENU)

# Inventario simulado
@app.route("/inventario")
def inventario():
    total_skus = len(MENU)
    total_stock = sum(p["stock"] for p in MENU.values())
    return render_template(
        "inventario.html",
        titulo="Inventario",
        menu=MENU,
        total_skus=total_skus,
        total_stock=total_stock
    )

# Detalle de producto
@app.route("/producto/<slug>")
def producto(slug: str):
    slug = slug.lower().strip()
    if slug not in MENU:
        flash("El producto solicitado no existe.", "error")
        return redirect(url_for("menu"))

    return render_template(
        "producto.html",
        titulo=f"Producto - {MENU[slug]['nombre']}",
        slug=slug,
        producto=MENU[slug]
    )

# Formulario: crear nuevo pedido (GET muestra formulario, POST procesa)
@app.route("/pedido/nuevo", methods=["GET", "POST"])
def pedido_nuevo():
    # Prefill opcional: /pedido/nuevo?producto=latte
    pre_producto = request.args.get("producto", "").lower().strip()

    if request.method == "GET":
        return render_template(
            "pedido_nuevo.html",
            titulo="Nuevo pedido",
            menu=MENU,
            pre_producto=pre_producto
        )

    # POST: procesar pedido
    cliente = request.form.get("cliente", "").strip()
    producto_slug = request.form.get("producto", "").lower().strip()
    cantidad_raw = request.form.get("cantidad", "1").strip()
    notas = request.form.get("notas", "").strip()

    # Validaciones básicas
    if not cliente:
        flash("Debes ingresar el nombre del cliente.", "error")
        return redirect(url_for("pedido_nuevo", producto=pre_producto or producto_slug))

    if producto_slug not in MENU:
        flash("Debes seleccionar un producto válido.", "error")
        return redirect(url_for("pedido_nuevo"))

    try:
        cantidad = int(cantidad_raw)
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        flash("La cantidad debe ser un número entero positivo.", "error")
        return redirect(url_for("pedido_nuevo", producto=producto_slug))

    # Validar stock
    if MENU[producto_slug]["stock"] < cantidad:
        flash(
            f"Stock insuficiente para {MENU[producto_slug]['nombre']}. "
            f"Disponible: {MENU[producto_slug]['stock']}.",
            "error"
        )
        return redirect(url_for("pedido_nuevo", producto=producto_slug))

    # Descontar stock (simulación)
    MENU[producto_slug]["stock"] -= cantidad

    # Calcular total
    precio = MENU[producto_slug]["precio"]
    subtotal = round(precio * cantidad, 2)

    pedido_id = len(ORDERS) + 1
    pedido = {
        "id": pedido_id,
        "cliente": cliente.title(),
        "estado": "En preparación",
        "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "notas": notas,
        "items": [
            {
                "slug": producto_slug,
                "nombre": MENU[producto_slug]["nombre"],
                "precio": precio,
                "cantidad": cantidad,
                "subtotal": subtotal,
            }
        ],
        "total": subtotal,
    }
    ORDERS.append(pedido)

    flash(f"Pedido #{pedido_id} registrado correctamente.", "success")
    return redirect(url_for("pedido_detalle", pedido_id=pedido_id))

# Detalle de pedido por id
@app.route("/pedido/<int:pedido_id>")
def pedido_detalle(pedido_id: int):
    pedido = next((p for p in ORDERS if p["id"] == pedido_id), None)
    if not pedido:
        flash("No se encontró el pedido solicitado.", "error")
        return redirect(url_for("home"))

    return render_template("pedido_detalle.html", titulo=f"Pedido #{pedido_id}", pedido=pedido)

if __name__ == "__main__":
    app.run(debug=True)