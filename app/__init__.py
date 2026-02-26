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

    app.config.from_object(Config)

    # Inicializar DB + seed
    with app.app_context():
        init_db()
        seed_if_empty()

    # Registrar blueprints
    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_blueprints():
        return {"blueprints": app.blueprints}

    return app