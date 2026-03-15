from flask import Flask
from .config import Config
from .extensions import db
import os

def create_app():
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__,
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    app.config.from_object(Config)

    # Crear el directorio 'instance' (ya no es necesario para MySQL, pero no molesta)
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Configurar SQLAlchemy: la URI ya viene de Config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Importar modelos y crear tablas
        from . import models
        db.create_all()
        print("Tablas creadas (o ya existían).")

        # Ejecutar seed si la base está vacía
        from .seed import seed_if_empty
        seed_if_empty()

    # Registrar blueprints
    from .routes.main import bp as main_bp
    from .routes.productos import bp as productos_bp
    from .routes.clientes import bp as clientes_bp
    from .routes.pedidos import bp as pedidos_bp
    from .routes.datos import bp as datos_bp
    from .routes.usuarios import bp as usuarios_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    app.register_blueprint(datos_bp)
    app.register_blueprint(usuarios_bp)

    return app