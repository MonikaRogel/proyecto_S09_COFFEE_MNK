from models import Producto
from extensions import db

def get_all():
    return Producto.query.order_by(Producto.nombre).all()

def get_by_id(id):
    return Producto.query.get_or_404(id)

def create(data):
    producto = Producto(**data)
    db.session.add(producto)
    db.session.commit()
    return producto

def update(id, data):
    producto = get_by_id(id)
    for key, value in data.items():
        setattr(producto, key, value)
    db.session.commit()
    return producto

def delete(id):
    producto = get_by_id(id)
    if producto.pedido_items:
        raise ValueError("No se puede eliminar porque tiene pedidos asociados")
    db.session.delete(producto)
    db.session.commit()