from app.models import Producto
from app.extensions import db

def get_all():
    """Obtiene todos los productos ordenados por nombre."""
    return Producto.query.order_by(Producto.nombre).all()

def get_by_id(id):
    """Obtiene un producto por su ID o lanza 404."""
    return Producto.query.get_or_404(id)

def create(data):
    """Crea un nuevo producto con los datos proporcionados."""
    producto = Producto(**data)
    db.session.add(producto)
    db.session.commit()
    return producto

def update(id, data):
    """Actualiza un producto existente."""
    producto = get_by_id(id)
    for key, value in data.items():
        setattr(producto, key, value)
    db.session.commit()
    return producto

def delete(id):
    """Elimina un producto, si no tiene pedidos asociados."""
    producto = get_by_id(id)
    # Verificar si hay pedidos asociados
    if producto.pedido_items:
        raise ValueError("No se puede eliminar porque tiene pedidos asociados")
    db.session.delete(producto)
    db.session.commit()