from flask import Flask
from .config import Config
from .db import init_db
from .seed import seed_if_empty

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # IMPORTANTE: cargar Config (SECRET_KEY, etc.)
    app.config.from_object(Config)

    with app.app_context():
        init_db()
        seed_if_empty()

    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .routes.productos import bp as productos_bp
    app.register_blueprint(productos_bp, url_prefix="/productos")

    from .routes.pedidos import bp as pedidos_bp
    app.register_blueprint(pedidos_bp, url_prefix="/pedidos")

    # En templates usa "blueprints", no current_app
    @app.context_processor
    def inject_blueprints():
        return {"blueprints": app.blueprints}

    return app