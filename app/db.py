import sqlite3
from pathlib import Path

DB_PATH = Path("instance") / "coffee_mnk.db"

def ensure_instance():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def connect():
    ensure_instance()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Crea todas las tablas si no existen."""
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL CHECK(precio > 0),
            stock INTEGER NOT NULL CHECK(stock >= 0),
            img TEXT DEFAULT '',
            descripcion TEXT DEFAULT ''
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE,
            telefono TEXT
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL,
            notas TEXT DEFAULT '',
            total REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS pedido_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL CHECK(cantidad > 0),
            precio_unitario REAL NOT NULL CHECK(precio_unitario > 0),
            subtotal REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
            FOREIGN KEY(producto_id) REFERENCES productos(id) ON DELETE RESTRICT
        );
        """)