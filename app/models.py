from .extensions import db

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)      # longitud 100
    nombre = db.Column(db.String(200), nullable=False)                 # longitud 200
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(500), default='')                        # URL puede ser larga
    descripcion = db.Column(db.Text, default='')                       # Texto largo sin límite fijo

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)                 # longitud 200
    cedula = db.Column(db.String(20), unique=True)                     # cédula máxima 20
    email = db.Column(db.String(120), unique=True)                     # email hasta 120
    telefono = db.Column(db.String(20))                                # teléfono hasta 20

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha = db.Column(db.String(30), nullable=False)                   # fecha en formato string
    estado = db.Column(db.String(50), nullable=False)                  # estado
    notas = db.Column(db.Text, default='')
    total = db.Column(db.Float, nullable=False)

    cliente = db.relationship('Cliente', backref='pedidos')

class PedidoItem(db.Model):
    __tablename__ = 'pedido_items'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    pedido = db.relationship('Pedido', backref='items')
    producto = db.relationship('Producto')

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)                 # longitud 200
    mail = db.Column(db.String(120), unique=True, nullable=False)      # email hasta 120
    password = db.Column(db.String(200), nullable=False)               # contraseña (hasheada)