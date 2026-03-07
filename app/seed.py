from .extensions import db
from .models import Producto, Cliente

PRODUCTOS_INICIALES = [
    {
        "slug": "capuccino",
        "nombre": "Capuccino",
        "precio": 2.75,
        "stock": 18,
        "img": "https://images.unsplash.com/photo-1481391319762-47dff72954d9?auto=format&fit=crop&w=1200&q=70",
        "descripcion": "Café espresso con espuma de leche, balanceado y cremoso."
    },
    {
        "slug": "mocaccino",
        "nombre": "Mocaccino",
        "precio": 3.25,
        "stock": 12,
        "img": "https://images.unsplash.com/photo-1511920170033-f8396924c348?auto=format&fit=crop&w=1200&q=70",
        "descripcion": "Mezcla de café, chocolate y leche, ideal para un sabor dulce."
    },
    {
        "slug": "latte",
        "nombre": "Latte",
        "precio": 3.00,
        "stock": 20,
        "img": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=70",
        "descripcion": "Café con leche vaporizada, suave y perfecto para cualquier hora."
    },
    {
        "slug": "espresso",
        "nombre": "Espresso",
        "precio": 2.00,
        "stock": 25,
        "img": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=1200&q=70",
        "descripcion": "Clásico espresso intenso, corto y aromático."
    }
]

CLIENTES_INICIALES = [
    {
        "nombre": "Monika",
        "cedula": "12345678",
        "email": "monika@email.com",
        "telefono": "0999999999"
    },
    {
        "nombre": "Ana",
        "cedula": "87654321",
        "email": "ana@email.com",
        "telefono": "0988888888"
    }
]

def seed_if_empty():
    """Inserta datos iniciales solo si las tablas están vacías."""
    # Productos
    if Producto.query.count() == 0:
        for data in PRODUCTOS_INICIALES:
            producto = Producto(**data)
            db.session.add(producto)
        db.session.commit()
        print("Productos iniciales insertados.")

    # Clientes
    if Cliente.query.count() == 0:
        for data in CLIENTES_INICIALES:
            cliente = Cliente(**data)
            db.session.add(cliente)
        db.session.commit()
        print("Clientes iniciales insertados.")