# Bella Pasta — Sistema web de restaurante

## Análisis del proyecto

**Nombre:** Bella Pasta · Restaurante italiano.

**Problema:** Una administración de restaurante que mantiene reservas, pedidos, clientes y el menú en cuadernos o archivos distintos puede perder información, registrar mesas dos veces y dificultar el seguimiento de órdenes.

**Objetivo general:** Desarrollar una aplicación web para administrar información del restaurante mediante una interfaz conectada a una API de Python FastAPI y a una base de datos relacional SQLite.

**Funcionalidades:** CRUD completo de clientes, mesas, categorías, platos, reservas, pedidos y detalle de pedidos; controles básicos de capacidad y duplicación de reservas; cálculo del valor de ventas pagadas; panel con estadísticas provenientes de SQLite; documentación API automática.

**Usuarios:** Personal administrativo, encargados de reservas, caja y atención de mesas.

## Tecnologías

- Backend: Python 3.10 o superior, FastAPI y Pydantic.
- Datos: SQLite con claves primarias, foráneas, restricciones e índices.
- Frontend: HTML, CSS y JavaScript con `fetch`.
- GitHub: repositorio de control de versiones (debe publicarse desde tu cuenta).
- Vercel: despliegue web (requiere vincular el repositorio).

## Instalación y ejecución local

Abre una terminal dentro de la carpeta del proyecto:

```bash
python -m venv venv
```

Activa el entorno:

**Windows:** `venv\Scripts\activate`

**macOS / Linux:** `source venv/bin/activate`

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Inicia la aplicación:

```bash
uvicorn main:app --reload
```

- Web: http://127.0.0.1:8000
- Documentación Swagger: http://127.0.0.1:8000/docs
- API: http://127.0.0.1:8000/api/clientes

La base SQLite `restaurante.db` ya contiene el esquema y ejemplos de mesas, categorías y platos. Si se elimina, se crea nuevamente en el primer arranque.

## Estructura

```text
Restaurante_Sabor_Tico/
├── main.py                  # FastAPI: endpoints, CRUD, validación
├── database.py              # Conexión y esquema SQLite
├── restaurante.db           # SQLite con ejemplos iniciales
├── static/
│   ├── index.html           # Interfaz del restaurante
│   ├── styles.css           # Diseño adaptable
│   └── app.js               # Comunicación real con API
├── docs/
│   └── diagrama_entidad_relacion.mmd
├── requirements.txt
├── .gitignore
├── vercel.json
└── README.md
```

## Modelo de base de datos

- `clientes`: PK `id`, nombre, teléfono, correo.
- `mesas`: PK `id`, número único, capacidad, estado.
- `categorias`: PK `id`, nombre único, descripción.
- `platos`: PK `id`; FK `categoria_id` → `categorias.id`.
- `reservas`: PK `id`; FK `cliente_id` → `clientes.id`; FK `mesa_id` → `mesas.id`.
- `pedidos`: PK `id`; FK `cliente_id` → `clientes.id`; FK opcional `mesa_id` → `mesas.id`.
- `detalles_pedido`: PK `id`; FK `pedido_id` → `pedidos.id` (eliminación en cascada); FK `plato_id` → `platos.id`.

El diagrama ER editable está en `docs/diagrama_entidad_relacion.mmd`, visible con Mermaid.

## Rutas

Para cada tabla (`clientes`, `mesas`, `categorias`, `platos`, `reservas`, `pedidos`, `detalles_pedido`):

- `GET /api/{tabla}` — listar.
- `GET /api/{tabla}/{id}` — consultar uno.
- `POST /api/{tabla}` — crear.
- `PUT /api/{tabla}/{id}` — modificar.
- `DELETE /api/{tabla}/{id}` — eliminar.

Extras: `GET /api/resumen` y `GET /api/pedidos/{id}/total`.

## Publicar en GitHub

Crea un repositorio nuevo, por ejemplo `restaurante-sabor-tico`. En la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Proyecto restaurante con FastAPI y SQLite"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/restaurante-sabor-tico.git
git push -u origin main
```

Sustituye `TU_USUARIO` y entrega el enlace real de tu repositorio.

## Publicar en Vercel — advertencia importante

El archivo `vercel.json` configura el punto de entrada de FastAPI. Importa el repositorio en Vercel y realiza un despliegue de prueba. **Precaución: SQLite es un archivo local, y el sistema de archivos de las funciones serverless de Vercel no es persistente.** En Vercel el archivo incluido en el despliegue puede permitir lecturas, pero las escrituras no persistirán y podrían fallar. Por tanto, **esta versión ofrece CRUD SQLite persistente en ejecución local, pero no garantiza CRUD funcional en Vercel**. Para cumplir la exigencia de CRUD persistente en una URL de producción hace falta un almacenamiento SQLite persistente externo o una plataforma con disco persistente y una estrategia compatible. No declares como completado el despliegue hasta probar crear/editar/eliminar y verificar su persistencia.

## Prueba rápida

Entra a la web, crea un cliente, crea una reserva para una mesa con capacidad suficiente, edítala y elimínala. Reinicia el servidor y verifica que los datos que no eliminaste siguen ahí. Prueba el resto de módulos, incluida la vinculación de categorías con platos y los detalles con pedidos.
