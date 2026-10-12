# Bella Pasta — Restaurante italiano

Aplicación web de administración con clientes, mesas, categorías, platos, reservas, pedidos y detalles de pedidos. Frontend HTML/CSS/JavaScript, API FastAPI y base de datos SQLite en local / PostgreSQL (Supabase) en Vercel.

## Ejecutar localmente

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Visita http://127.0.0.1:8000 y la API en `/docs`. Sin `DATABASE_URL` usa `restaurante.db` (SQLite).

## Publicar en Vercel con Supabase

1. Crea un proyecto en [Supabase](https://supabase.com). En **Connect**, copia el enlace PostgreSQL del **Session pooler** (puerto 5432) o el de conexión compatible con IPv4 que indique tu panel.
2. En **Vercel → bella-pasta → Settings → Environment Variables**, crea una variable llamada `DATABASE_URL` y pega la URL PostgreSQL completa como valor. No la subas a GitHub ni la compartas en capturas. La contraseña puede necesitar codificar caracteres especiales de URL.
3. Actualiza GitHub con los nuevos `main.py`, `database.py`, `requirements.txt`, `static/index.html` y `static/styles.css` (y demás archivos de este proyecto). Vercel debería generar un nuevo despliegue. Si agregaste la variable después, haz **Redeploy**.
4. Prueba crear un cliente, editarlo, refrescar la página, abrirla en otra ventana y verificar que el cambio persista. Luego prueba eliminar.

La API crea tablas y carga categorías, mesas y platos de ejemplo cuando la base está vacía. Datos previos de `restaurante.db` **no se migran** automáticamente a Supabase.

## Archivos

- `main.py`: rutas y reglas del negocio.
- `database.py`: esquema SQL, conectividad y datos de ejemplo.
- `static/index.html`, `styles.css`, `app.js`, `carbonara.jpg`: interfaz.
- `docs/diagrama_entidad_relacion.mmd`: diagrama ER.
- `requirements.txt`, `vercel.json`, `.gitignore`: configuración.

## API

Para clientes, mesas, categorias, platos, reservas, pedidos y detalles_pedido:
GET `/api/{tabla}`, GET `/api/{tabla}/{id}`, POST `/api/{tabla}`, PUT `/api/{tabla}/{id}`, DELETE `/api/{tabla}/{id}`. Adicionalmente GET `/api/resumen` y GET `/api/pedidos/{id}/total`.

**Seguridad:** esta aplicación es una práctica educativa sin autenticación. No ingreses datos reales de clientes hasta añadir controles de acceso.
