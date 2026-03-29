from app.models import Usuario
from app.extensions import db

def get_all():
    return Usuario.query.order_by(Usuario.nombre).all()

def get_by_id(id):
    return Usuario.query.get_or_404(id)

def create(data):
    usuario = Usuario(**data)
    if 'password' in data and data['password']:
        usuario.set_password(data['password'])
    db.session.add(usuario)
    db.session.commit()
    return usuario

def update(id, data):
    usuario = get_by_id(id)
    for key, value in data.items():
        if key == 'password' and value:
            usuario.set_password(value)
        else:
            setattr(usuario, key, value)
    db.session.commit()
    return usuario

def delete(id):
    usuario = get_by_id(id)
    # No se puede eliminar el propio usuario actual
    db.session.delete(usuario)
    db.session.commit()