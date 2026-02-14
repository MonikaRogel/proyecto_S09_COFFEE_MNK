from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bienvenido a COFFEE_MNK – Sistema de Ventas para Cafetería"

@app.route("/producto/<nombre>")
def producto(nombre):
    return f"Producto: {nombre} – disponible para venta."

@app.route("/pedido/<cliente>")
def pedido(cliente):
    return f"Cliente {cliente}: tu pedido está en preparación en COFFEE_MNK."

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    app.run(debug=True)
