from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

db = SQLAlchemy()

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.es_admin:
            flash('Acceso denegado. Necesitas privilegios de administrador.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function