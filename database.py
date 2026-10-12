"""SQLite: esquema relacional y datos iniciales del restaurante."""
import os
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv('DATABASE_PATH', str(BASE / 'restaurante.db')))
SCHEMA = '''
CREATE TABLE IF NOT EXISTS clientes (
 id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, telefono TEXT NOT NULL,
 correo TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS mesas (
 id INTEGER PRIMARY KEY AUTOINCREMENT, numero INTEGER NOT NULL UNIQUE CHECK(numero>0),
 capacidad INTEGER NOT NULL CHECK(capacidad>0), estado TEXT NOT NULL DEFAULT 'Disponible'
 CHECK(estado IN ('Disponible','Ocupada','Reservada'))
);
CREATE TABLE IF NOT EXISTS categorias (
 id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE, descripcion TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS platos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, descripcion TEXT NOT NULL DEFAULT '',
 precio REAL NOT NULL CHECK(precio>=0), categoria_id INTEGER NOT NULL,
 disponible INTEGER NOT NULL DEFAULT 1 CHECK(disponible IN (0,1)),
 FOREIGN KEY(categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS reservas (
 id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, mesa_id INTEGER NOT NULL,
 fecha TEXT NOT NULL, hora TEXT NOT NULL, personas INTEGER NOT NULL CHECK(personas>0),
 estado TEXT NOT NULL DEFAULT 'Confirmada' CHECK(estado IN ('Confirmada','Pendiente','Cancelada','Completada')),
 FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
 FOREIGN KEY(mesa_id) REFERENCES mesas(id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS pedidos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, mesa_id INTEGER,
 fecha TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'Pendiente'
 CHECK(estado IN ('Pendiente','Preparando','Servido','Pagado','Cancelado')),
 FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
 FOREIGN KEY(mesa_id) REFERENCES mesas(id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS detalles_pedido (
 id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL, plato_id INTEGER NOT NULL,
 cantidad INTEGER NOT NULL CHECK(cantidad>0), precio_unitario REAL NOT NULL CHECK(precio_unitario>=0),
 FOREIGN KEY(pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
 FOREIGN KEY(plato_id) REFERENCES platos(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_reservas_fecha ON reservas(fecha,hora);
CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha);
'''

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def initialize_database():
    with get_connection() as c:
        c.executescript(SCHEMA)
        if c.execute('SELECT COUNT(*) FROM categorias').fetchone()[0] == 0:
            c.executemany('INSERT INTO categorias(nombre,descripcion) VALUES (?,?)', [
                ('Pastas clásicas','Recetas tradicionales italianas'),('Pastas especiales','Especialidades de la casa'),
                ('Bebidas','Para acompañar cada plato'),('Postres italianos','Dulces típicos de Italia')])
        if c.execute('SELECT COUNT(*) FROM mesas').fetchone()[0] == 0:
            c.executemany('INSERT INTO mesas(numero,capacidad,estado) VALUES (?,?,?)',
                          [(1,2,'Disponible'),(2,4,'Disponible'),(3,4,'Reservada'),(4,6,'Disponible'),(5,2,'Ocupada'),(6,8,'Disponible')])
        if c.execute('SELECT COUNT(*) FROM platos').fetchone()[0] == 0:
            c.executemany('INSERT INTO platos(nombre,descripcion,precio,categoria_id,disponible) VALUES (?,?,?,?,?)',[
                ('Spaghetti alla Carbonara','Pasta con huevo, parmesano y panceta',5600,1,1),
                ('Fettuccine Alfredo','Salsa cremosa con parmesano',5400,1,1),
                ('Lasagna alla Bolognese','Capas de pasta, carne y bechamel',6200,2,1),
                ('Ravioli Ricotta e Spinaci','Ravioles de ricotta y espinaca',6500,2,1),
                ('Penne all Arrabbiata','Tomate, ajo y un toque picante',4900,1,1),
                ('Limonata italiana','Limonada con hierbas frescas',1900,3,1),
                ('Espresso','Café espresso italiano',1500,3,1),
                ('Tiramisú','Postre con café y mascarpone',3200,4,1),
                ('Panna cotta','Crema italiana con frutos rojos',2900,4,1)])
