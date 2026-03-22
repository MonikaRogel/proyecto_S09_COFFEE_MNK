from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Producto(db.Model):
    __tablename__ = 'productos'
    id          = db.Column(db.Integer, primary_key=True)
    slug        = db.Column(db.String(100), unique=True, nullable=False)
    nombre      = db.Column(db.String(200), nullable=False)
    precio      = db.Column(db.Float, nullable=False)
    stock       = db.Column(db.Integer, nullable=False)
    img         = db.Column(db.String(500), default='')
    descripcion = db.Column(db.Text, default='')


class Cliente(db.Model):
    __tablename__ = 'clientes'
    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(200), nullable=False)
    cedula   = db.Column(db.String(20),  unique=True)
    email    = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(20))


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id         = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha      = db.Column(db.String(30),  nullable=False)
    estado     = db.Column(db.String(50),  nullable=False)
    notas      = db.Column(db.Text, default='')
    total      = db.Column(db.Float, nullable=False)

    cliente = db.relationship('Cliente', backref='pedidos')


class PedidoItem(db.Model):
    __tablename__ = 'pedido_items'
    id              = db.Column(db.Integer, primary_key=True)
    pedido_id       = db.Column(db.Integer, db.ForeignKey('pedidos.id'),   nullable=False)
    producto_id     = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad        = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float,   nullable=False)
    subtotal        = db.Column(db.Float,   nullable=False)

    pedido   = db.relationship('Pedido',   backref='items')
    producto = db.relationship('Producto')


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id       = db.Column(db.Integer,     primary_key=True)
    nombre   = db.Column(db.String(200), nullable=False)
    mail     = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol      = db.Column(db.String(20),  nullable=False, default='cliente')

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    @property
    def es_admin(self):
        return self.rol == 'admin'