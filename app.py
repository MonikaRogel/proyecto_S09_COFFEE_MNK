from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Manejo de favicon para evitar error 404 del navegador
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

# Ruta principal: ahora renderiza una plantilla
@app.route("/")
def home():
    return render_template("index.html", titulo="Inicio")

# Página "Acerca de"
@app.route("/about")
def about():
    return render_template("about.html", titulo="Acerca de")

# Ruta dinámica: producto
@app.route("/producto/<nombre>")
def producto(nombre):
    return render_template(
        "producto.html",
        titulo="Producto",
        nombre=nombre.capitalize()
    )

# Ruta dinámica: pedido
@app.route("/pedido/<cliente>")
def pedido(cliente):
    return render_template(
        "pedido.html",
        titulo="Pedido",
        cliente=cliente.capitalize()
    )

if __name__ == "__main__":
    app.run(debug=True)