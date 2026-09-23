# CRM Inmobiliario - Capstone Grupo 5

Sistema de gestión para ejecutivos inmobiliarios: prospectos (leads), catálogo de
propiedades, historial de contacto, tareas de seguimiento y propiedades de interés
de cada lead.

El proyecto contempla incorporar más adelante un agente de IA que priorice leads,
resuma el historial de un cliente y recomiende la siguiente acción. Esa parte
todavía no está implementada.

## Stack

- Backend: Python 3.14, FastAPI, SQLAlchemy, Uvicorn
- Frontend: React 18 con Vite 5, Node 24
- Base de datos: PostgreSQL en Supabase
- Autenticación: bcrypt para las contraseñas y PyJWT para los tokens

Sin librerías de UI externas: los estilos están en un solo archivo CSS y los iconos
son SVG definidos en `frontend/src/components/Iconos.jsx`.

## Estructura

```
backend/
  main.py            Endpoints de la API
  models.py          Modelos ORM (tablas)
  schemas.py         Esquemas de entrada y salida
  database.py        Conexión a PostgreSQL
  seguridad.py       Contraseñas, tokens y autenticación
  prioridad.py       Reglas de priorización de leads
  crear_usuario.py   Script para dar de alta usuarios

frontend/src/
  App.jsx            Estado general y navegación
  api.js             Llamadas a la API
  index.css          Estilos
  components/        Tablas, formularios, paneles e iconos
```

## Cómo levantar el proyecto

Hacen falta dos terminales, una para el backend y otra para el frontend.

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crear `backend/.env` a partir de `backend/.env.example` y completar dos valores:

```
DATABASE_URL=postgresql://...
SECRET_KEY=...
```

`DATABASE_URL` es la cadena de conexión del proyecto, que se obtiene desde el panel
de Supabase. `SECRET_KEY` es la clave con la que se firman los tokens y se genera
con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Cada persona genera su propia clave. El archivo `.env` está en el `.gitignore` y no
se sube al repositorio.

Levantar el servidor:

```powershell
uvicorn main:app --reload
```

Queda en `http://localhost:8000`, con la documentación de la API en `/docs`. Al
arrancar crea las tablas que falten.

### Crear un usuario

No hay registro desde la interfaz porque el sistema es de uso interno. Con el
entorno virtual activado:

```powershell
python crear_usuario.py
```

Pide nombre, correo y contraseña. Sin al menos un usuario no se puede entrar.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Queda en `http://localhost:3000` y apunta al backend en `localhost:8000`. Para
cambiar la dirección, crear `frontend/.env` con `VITE_API_URL=http://127.0.0.1:8000`.

## Modelo de datos

```
usuarios       id, nombre, email (único), password_hash, activo, fecha_creacion
leads          id, nombre, email, telefono, estado, prioridad, fecha_creacion
propiedades    id, titulo, tipo, precio, direccion, estado, fecha_creacion
interacciones  id, lead_id, tipo, notas, fecha_creacion
tareas         id, titulo, descripcion, estado, prioridad, fecha_limite, lead_id
intereses      id, lead_id, propiedad_id, nivel_interes, notas, fecha_creacion
```

Sobre las relaciones:

- Al borrar un lead se borran sus interacciones y sus intereses, porque no tienen
  sentido sin él.
- Al borrar un lead sus tareas se conservan y quedan sin vínculo, porque el trabajo
  pendiente puede seguir siendo válido.
- `intereses` guarda datos propios (`nivel_interes`, `notas`), así que es una
  entidad de asociación y no una simple tabla puente. Tiene una restricción única
  sobre `(lead_id, propiedad_id)` para no asociar dos veces la misma propiedad.

Los campos de texto como `estado`, `tipo` o `prioridad` los limita el formulario,
no la base ni la API.

## Priorización de leads

`GET /api/leads` devuelve cada lead con un puntaje calculado y los motivos que lo
componen, ordenados de mayor a menor. El cálculo está en `prioridad.py` y considera
la antigüedad del último contacto, si nunca se contactó, las propiedades de interés,
la etapa del embudo y la prioridad marcada a mano.

El puntaje no se guarda en la base: se recalcula en cada consulta, porque uno
almacenado quedaría desactualizado en cuanto se registra una interacción. Para no
consultar la base una vez por lead, la actividad se obtiene con consultas agrupadas.

## Limitaciones conocidas

- El token se guarda en `localStorage`, que es accesible desde JavaScript y por lo
  tanto vulnerable a XSS. Lo más robusto serían cookies `httpOnly`, que complican
  CORS y el desarrollo local.
- No hay límite de intentos de login. Solo frena el costo de bcrypt.
- `/docs` es accesible sin autenticación. En producción habría que deshabilitarlo.
- `create_all()` crea las tablas que faltan pero no agrega columnas a tablas que ya
  existen. Al modificar un modelo existente hay que aplicar el cambio a mano en
  Supabase.
- CORS está limitado a `localhost:3000`. Al desplegar hay que agregar el dominio en
  `backend/main.py`.
- No hay roles, ni asignación de leads por ejecutivo, ni cambio de contraseña desde
  la interfaz, ni paginación en los listados.

## Problemas frecuentes

**`tenant or user not found` al arrancar el backend.** El proyecto de Supabase está
pausado por inactividad. Hay que reactivarlo desde el panel y esperar un par de
minutos.

**`La variable SECRET_KEY no está definida`.** Falta completar `SECRET_KEY` en
`backend/.env`.

**No se puede entrar y no hay usuarios.** Correr `python crear_usuario.py`.

**La aplicación tarda unos dos segundos en responder.** Uvicorn escucha solo en IPv4
y en Windows `localhost` se resuelve primero a IPv6. Se corrige creando
`frontend/.env` con `VITE_API_URL=http://127.0.0.1:8000`.

## Estado del proyecto

Implementado: leads, propiedades, interacciones, tareas, propiedades de interés,
autenticación, priorización de leads y vista de inicio.

Pendiente: agente de IA, documentos y auditoría.
