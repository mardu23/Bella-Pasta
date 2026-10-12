"""API FastAPI para Restaurante Sabor Tico. CRUD y panel en tiempo real."""
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from database import get_connection, initialize_database

class Cliente(BaseModel):
    nombre: str = Field(min_length=1,max_length=90)
    telefono: str = Field(min_length=1,max_length=25)
    correo: str = Field(default='',max_length=120)
class Mesa(BaseModel):
    numero: int = Field(gt=0)
    capacidad: int = Field(gt=0)
    estado: Literal['Disponible','Ocupada','Reservada'] = 'Disponible'
class Categoria(BaseModel):
    nombre: str = Field(min_length=1,max_length=80)
    descripcion: str = ''
class Plato(BaseModel):
    nombre: str = Field(min_length=1,max_length=90)
    descripcion: str = ''
    precio: float = Field(ge=0)
    categoria_id: int = Field(gt=0)
    disponible: int = Field(default=1,ge=0,le=1)
class Reserva(BaseModel):
    cliente_id: int = Field(gt=0)
    mesa_id: int = Field(gt=0)
    fecha: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    hora: str = Field(pattern=r'^\d{2}:\d{2}$')
    personas: int = Field(gt=0)
    estado: Literal['Confirmada','Pendiente','Cancelada','Completada'] = 'Confirmada'
class Pedido(BaseModel):
    cliente_id: int = Field(gt=0)
    mesa_id: int | None = None
    fecha: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    estado: Literal['Pendiente','Preparando','Servido','Pagado','Cancelado'] = 'Pendiente'
class DetallePedido(BaseModel):
    pedido_id: int = Field(gt=0)
    plato_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)
    precio_unitario: float = Field(ge=0)

MODELOS = {'clientes':Cliente,'mesas':Mesa,'categorias':Categoria,'platos':Plato,
           'reservas':Reserva,'pedidos':Pedido,'detalles_pedido':DetallePedido}
ROOT = Path(__file__).parent
@asynccontextmanager
async def lifespan(app):
    initialize_database()
    yield
app = FastAPI(title='Restaurante Sabor Tico - API',version='1.0',lifespan=lifespan)
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')

@app.get('/',include_in_schema=False)
def home():return FileResponse(ROOT/'static'/'index.html')

@app.get('/api/resumen')
def resumen():
    with get_connection() as c:
        counts={t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in MODELOS}
        ventas=c.execute("""SELECT COALESCE(SUM(d.cantidad*d.precio_unitario),0)
                FROM detalles_pedido d JOIN pedidos p ON p.id=d.pedido_id WHERE p.estado='Pagado'""").fetchone()[0]
        ocupadas=c.execute("SELECT COUNT(*) FROM mesas WHERE estado='Ocupada'").fetchone()[0]
    return {**counts,'ventas':round(ventas,2),'mesas_ocupadas':ocupadas}

def validar_tabla(tabla):
    if tabla not in MODELOS:raise HTTPException(404,'Módulo no encontrado')

def error_integridad(ex):
    raise HTTPException(409,'No se pudo guardar: registro duplicado, dato inválido o relación con otro registro.') from ex

@app.get('/api/{tabla}')
def listar(tabla:str):
    validar_tabla(tabla)
    with get_connection() as c:
        return [dict(r) for r in c.execute(f'SELECT * FROM {tabla} ORDER BY id DESC')]

@app.get('/api/{tabla}/{id}')
def obtener(tabla:str,id:int):
    validar_tabla(tabla)
    with get_connection() as c:r=c.execute(f'SELECT * FROM {tabla} WHERE id=?',(id,)).fetchone()
    if r is None:raise HTTPException(404,'Registro no encontrado')
    return dict(r)

def validar_negocio(tabla, datos, c, id=None):
    if tabla=='reservas':
        mesa=c.execute('SELECT capacidad FROM mesas WHERE id=?',(datos['mesa_id'],)).fetchone()
        if mesa and datos['personas']>mesa['capacidad']:
            raise HTTPException(400,'La cantidad de personas supera la capacidad de la mesa.')
        if datos['estado'] in ('Pendiente','Confirmada'):
            choque=c.execute("""SELECT id FROM reservas WHERE mesa_id=? AND fecha=? AND hora=?
                 AND estado IN ('Pendiente','Confirmada') AND id!=?""",
                 (datos['mesa_id'],datos['fecha'],datos['hora'],id or -1)).fetchone()
            if choque:raise HTTPException(409,'Esta mesa ya tiene una reserva para ese día y hora.')

@app.post('/api/{tabla}',status_code=201)
def crear(tabla:str,datos:dict):
    validar_tabla(tabla)
    payload=MODELOS[tabla].model_validate(datos).model_dump()
    cols=list(payload)
    try:
        with get_connection() as c:
            validar_negocio(tabla,payload,c)
            cursor=c.execute(f"INSERT INTO {tabla} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",tuple(payload.values()))
            nuevo=c.execute(f'SELECT * FROM {tabla} WHERE id=?',(cursor.lastrowid,)).fetchone()
            return dict(nuevo)
    except sqlite3.IntegrityError as ex:error_integridad(ex)

@app.put('/api/{tabla}/{id}')
def editar(tabla:str,id:int,datos:dict):
    validar_tabla(tabla)
    payload=MODELOS[tabla].model_validate(datos).model_dump()
    try:
        with get_connection() as c:
            validar_negocio(tabla,payload,c,id)
            cursor=c.execute(f"UPDATE {tabla} SET {','.join(k+'=?' for k in payload)} WHERE id=?",(*payload.values(),id))
            if not cursor.rowcount:raise HTTPException(404,'Registro no encontrado')
            return dict(c.execute(f'SELECT * FROM {tabla} WHERE id=?',(id,)).fetchone())
    except sqlite3.IntegrityError as ex:error_integridad(ex)

@app.delete('/api/{tabla}/{id}',status_code=204)
def eliminar(tabla:str,id:int):
    validar_tabla(tabla)
    try:
        with get_connection() as c:
            cursor=c.execute(f'DELETE FROM {tabla} WHERE id=?',(id,))
            if not cursor.rowcount:raise HTTPException(404,'Registro no encontrado')
    except sqlite3.IntegrityError as ex:error_integridad(ex)

@app.get('/api/pedidos/{id}/total')
def total_pedido(id:int):
    with get_connection() as c:
        if not c.execute('SELECT id FROM pedidos WHERE id=?',(id,)).fetchone():
            raise HTTPException(404,'Pedido no encontrado')
        total=c.execute('SELECT COALESCE(SUM(cantidad*precio_unitario),0) FROM detalles_pedido WHERE pedido_id=?',(id,)).fetchone()[0]
    return {'pedido_id':id,'total':round(total,2)}
