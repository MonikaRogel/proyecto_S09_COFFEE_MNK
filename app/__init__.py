from flask import Flask
from .config import Config
from .db import init_db
from .seed import seed_if_empty
import os

def create_app():
    # Obtener la ruta absoluta de la raíz del proyecto (un nivel arriba de app/)
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(__name__,
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    app.config.from_object(Config)

    with app.app_context():
        init_db()
        seed_if_empty()

    from .routes.main import bp as main_bp
    from .routes.productos import bp as productos_bp
    from .routes.clientes import bp as clientes_bp
    from .routes.pedidos import bp as pedidos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')

    return app