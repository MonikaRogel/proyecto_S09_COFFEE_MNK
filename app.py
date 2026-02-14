from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Ruta principal (muestra propósito + enlaces para evidenciar rutas dinámicas)
@app.route("/")
def home():
    return """
    <h1>Bienvenido a COFFEE_MNK – Sistema de Ventas para Cafetería</h1>
    <p>Este sistema incluye rutas dinámicas para consultar productos y pedidos.</p>

    <h3>Rutas de prueba (haz clic):</h3>
    <ul>
        <li><a href="/producto/Latte">/producto/Latte</a></li>
        <li><a href="/pedido/Ana">/pedido/Ana</a></li>
    </ul>
    """

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
