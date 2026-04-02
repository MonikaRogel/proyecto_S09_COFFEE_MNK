from models import Usuario
from extensions import db

def get_all():
    return Usuario.query.order_by(Usuario.nombre).all()

def get_by_id(id):
    return Usuario.query.get_or_404(id)

def create(data):
    usuario = Usuario(**data)
    db.session.add(usuario)
    db.session.commit()
    return usuario

def update(id, data):
    usuario = get_by_id(id)
    for key, value in data.items():
        setattr(usuario, key, value)
    db.session.commit()
    return usuario

def delete(id):
    usuario = get_by_id(id)
    db.session.delete(usuario)
    db.session.commit()