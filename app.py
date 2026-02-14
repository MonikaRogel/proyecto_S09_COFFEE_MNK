from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Ruta principal
@app.route("/")
def home():
    return "Bienvenido a COFFEE_MNK – Sistema de Ventas para Cafetería"

# Ruta dinámica para productos
@app.route("/producto/<nombre>")
def producto(nombre):
    return f"Producto: {nombre.capitalize()} – disponible para venta en COFFEE_MNK."

# Ruta dinámica para pedidos
@app.route("/pedido/<cliente>")
def pedido(cliente):
    return f"Hola {cliente.capitalize()}, tu pedido está en preparación en COFFEE_MNK."

# Ruta para favicon
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    app.run(debug=True)
