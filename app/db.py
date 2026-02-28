import sqlite3
from pathlib import Path
import os  # ← IMPORTANTE: agregar esta línea

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "instance" / "coffee_mnk.db"

def connect():
    # Crear el directorio instance si no existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def _col_exists(conn, table: str, col: str) -> bool:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(c["name"] == col for c in cols)

def init_db():
    with connect() as conn:
        # Productos
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

        # Clientes (con cedula)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT,
            email TEXT UNIQUE,
            telefono TEXT
        );
        """)
        # Migración: agregar cedula si no existe (para BD antiguas)
        if not _col_exists(conn, "clientes", "cedula"):
            conn.execute("ALTER TABLE clientes ADD COLUMN cedula TEXT;")

        # Pedidos
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

        # Pedido items
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
        conn.commit()