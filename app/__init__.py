from flask import Flask
from .config import Config
from .db import init_db
from .seed import seed_if_empty

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    app.config.from_object(Config)  # ✅ SECRET_KEY y demás

    with app.app_context():
        init_db()
        seed_if_empty()

    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .routes.productos import bp as productos_bp
    app.register_blueprint(productos_bp, url_prefix="/productos")

    from .routes.pedidos import bp as pedidos_bp
    app.register_blueprint(pedidos_bp, url_prefix="/pedidos")

    from .routes.clientes import bp as clientes_bp
    app.register_blueprint(clientes_bp, url_prefix="/clientes")

    @app.context_processor
    def inject_blueprints():
        return {"blueprints": app.blueprints}

    return app