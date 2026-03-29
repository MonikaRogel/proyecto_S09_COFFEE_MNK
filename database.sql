-- Tabla productos
CREATE TABLE IF NOT EXISTS productos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    slug VARCHAR(100) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    precio FLOAT NOT NULL,
    stock INT NOT NULL,
    img VARCHAR(500) DEFAULT '',
    descripcion TEXT DEFAULT ''
);

-- Tabla clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(200) NOT NULL,
    cedula VARCHAR(20) UNIQUE,
    email VARCHAR(120) UNIQUE,
    telefono VARCHAR(20)
);

-- Tabla pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT NOT NULL,
    fecha VARCHAR(30) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    notas TEXT DEFAULT '',
    total FLOAT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
);

-- Tabla pedido_items
CREATE TABLE IF NOT EXISTS pedido_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario FLOAT NOT NULL,
    subtotal FLOAT NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
);

-- Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(200) NOT NULL,
    mail VARCHAR(120) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    password VARCHAR(200) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'cliente'
);