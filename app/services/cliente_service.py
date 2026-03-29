from app.models import Cliente
from app.extensions import db

def get_all():
    return Cliente.query.order_by(Cliente.nombre).all()

def get_by_id(id):
    return Cliente.query.get_or_404(id)

def create(data):
    cliente = Cliente(**data)
    db.session.add(cliente)
    db.session.commit()
    return cliente

def update(id, data):
    cliente = get_by_id(id)
    for key, value in data.items():
        setattr(cliente, key, value)
    db.session.commit()
    return cliente

def delete(id):
    cliente = get_by_id(id)
    if cliente.pedidos:
        raise ValueError("No se puede eliminar porque tiene pedidos asociados")
    db.session.delete(cliente)
    db.session.commit()