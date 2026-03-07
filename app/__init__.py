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

    # Crear el directorio 'instance' si no existe
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Configurar SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'coffee_mnk.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Importar modelos explícitamente para que SQLAlchemy los conozca
        from . import models  # Esto ejecuta models.py y registra las tablas
        print("Modelos importados. Creando tablas...")
        db.create_all()
        print("Tablas creadas (o ya existían).")

        # Verificación opcional: contar productos
        try:
            from .models import Producto
            num_productos = Producto.query.count()
            print(f"📦 Productos en DB: {num_productos}")
        except Exception as e:
            print(f"Error al consultar productos: {e}")

    # Registrar blueprints
    from .routes.main import bp as main_bp
    from .routes.productos import bp as productos_bp
    from .routes.clientes import bp as clientes_bp
    from .routes.pedidos import bp as pedidos_bp
    from .routes.datos import bp as datos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    app.register_blueprint(datos_bp)

    return app