from flask import Flask
from .config import Config
from .db import init_db
from .seed import seed_if_empty

def create_app():
    # Por ahora apuntamos a templates/static de la raíz (NO movemos nada aún)
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    # init + seed (robusto en Render)
    with app.app_context():
        init_db()
        seed_if_empty()

    return app