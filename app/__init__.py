from flask import Flask
from flask_login import LoginManager
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

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'   # ruta a la que redirigir si no está autenticado
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'

    @login_manager.user_loader
    def load_user(user_id):
        from .models import Usuario
        return Usuario.query.get(int(user_id))

    with app.app_context():
        from . import models
        db.create_all()
        print("Tablas creadas (o ya existían).")
        from .seed import seed_if_empty
        seed_if_empty()

    # Registrar blueprints
    from .routes.main import bp as main_bp
    from .routes.productos import bp as productos_bp
    from .routes.clientes import bp as clientes_bp
    from .routes.pedidos import bp as pedidos_bp
    from .routes.datos import bp as datos_bp
    from .routes.usuarios import bp as usuarios_bp
    from .routes.auth import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    app.register_blueprint(datos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(auth_bp)

    return app