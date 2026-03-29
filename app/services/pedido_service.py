from app.models import Pedido
from app.extensions import db

def get_all(estado=None):
    if estado:
        return Pedido.query.filter_by(estado=estado).order_by(Pedido.id.desc()).all()
    return Pedido.query.order_by(Pedido.id.desc()).all()

def get_by_id(id):
    return Pedido.query.get_or_404(id)

def update_estado(pedido_id, nuevo_estado):
    pedido = get_by_id(pedido_id)
    pedido.estado = nuevo_estado
    db.session.commit()
    return pedido