from .db import connect

PRODUCTOS_INICIALES = [
    ("capuccino","Capuccino",2.75,18,
     "https://images.unsplash.com/photo-1481391319762-47dff72954d9?auto=format&fit=crop&w=1200&q=70",
     "Café espresso con espuma de leche, balanceado y cremoso."),
    ("mocaccino","Mocaccino",3.25,12,
     "https://images.unsplash.com/photo-1511920170033-f8396924c348?auto=format&fit=crop&w=1200&q=70",
     "Mezcla de café, chocolate y leche, ideal para un sabor dulce."),
    ("latte","Latte",3.00,20,
     "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=70",
     "Café con leche vaporizada, suave y perfecto para cualquier hora."),
    ("espresso","Espresso",2.00,25,
     "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=1200&q=70",
     "Clásico espresso intenso, corto y aromático."),
]

CLIENTES_INICIALES = [
    ("Monika", "monika@email.com", "0999999999"),
    ("Ana", "ana@email.com", "0988888888"),
]

def seed_if_empty():
    """Inserta datos iniciales solo si las tablas están vacías."""
    with connect() as conn:
        # Productos
        c = conn.execute("SELECT COUNT(*) as c FROM productos").fetchone()["c"]
        if c == 0:
            conn.executemany("""
                INSERT INTO productos (slug, nombre, precio, stock, img, descripcion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, PRODUCTOS_INICIALES)

        # Clientes
        c = conn.execute("SELECT COUNT(*) as c FROM clientes").fetchone()["c"]
        if c == 0:
            conn.executemany("""
                INSERT INTO clientes (nombre, email, telefono)
                VALUES (?, ?, ?)
            """, CLIENTES_INICIALES)

        conn.commit()