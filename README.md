# CRM Inmobiliario — Capstone Grupo 5

Sistema de gestión para ejecutivos inmobiliarios. Permite administrar prospectos
(leads), el catálogo de propiedades, el historial de contacto con cada cliente,
las tareas de seguimiento y las propiedades que le interesan a cada lead.

El objetivo del proyecto es incorporar más adelante un agente de IA que asista al
ejecutivo priorizando leads, resumiendo el historial de un cliente y recomendando
la siguiente acción. Esa parte todavía no está implementada.

## Stack

**Backend**

| Componente | Versión probada |
|---|---|
| Python | 3.14.6 |
| FastAPI | 0.141.1 |
| SQLAlchemy | 2.0.52 |
| Pydantic | 2.13.5 |
| Uvicorn | 0.52.4 |
| bcrypt | 5.0.0 |
| PyJWT | 2.14.0 |

**Frontend**

| Componente | Versión probada |
|---|---|
| Node | 24.20.0 |
| React | 18.2 |
| Vite | 5.2 |

**Base de datos:** PostgreSQL alojado en Supabase.

No se usan librerías de UI externas: los estilos son propios y los iconos son SVG
escritos a mano en `frontend/src/components/Iconos.jsx`.

## Estructura

```
backend/
  main.py            Endpoints de la API
  models.py          Modelos ORM (tablas)
  schemas.py         Esquemas de entrada y salida (Pydantic)
  database.py        Conexión a PostgreSQL y sesiones
  seguridad.py       Hash de contraseñas, tokens JWT y autenticación
  crear_usuario.py   Script para dar de alta usuarios
  requirements.txt

frontend/
  src/
    App.jsx          Estado global, navegación y paneles
    api.js           Capa de comunicación con la API
    index.css        Sistema de diseño completo
    components/      Tablas, formularios, sidebar, paneles e iconos
```

## Puesta en marcha

Se necesitan dos terminales: una para el backend y otra para el frontend.

### 1. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crear el archivo `backend/.env` copiando `backend/.env.example` y completando dos
valores obligatorios:

```
DATABASE_URL=postgresql://...        # cadena de conexión de Supabase
SECRET_KEY=...                       # clave con la que se firman los tokens
```

La `DATABASE_URL` se obtiene del botón **Connect** en el panel de Supabase.

La `SECRET_KEY` se genera con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Cada persona debe generar su propia clave. No se comparte y no se sube al
repositorio: `.env` está en el `.gitignore`.

Levantar el servidor:

```powershell
uvicorn main:app --reload
```

Al arrancar crea automáticamente las tablas que falten. La API queda en
`http://localhost:8000` y la documentación interactiva en
`http://localhost:8000/docs`.

### 2. Crear el primer usuario

No hay registro desde la interfaz: el sistema es de uso interno y los accesos se
crean por terminal. Con el entorno virtual activado:

```powershell
python crear_usuario.py
```

Pide nombre, correo y contraseña. La contraseña no se muestra al escribirla y se
guarda hasheada con bcrypt, nunca en texto plano.

Sin al menos un usuario no se puede entrar al sistema.

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Queda en `http://localhost:3000`.

Por defecto apunta a `http://localhost:8000`. Para cambiarlo, crear
`frontend/.env` con:

```
VITE_API_URL=http://127.0.0.1:8000
```

## Modelo de datos

```
usuarios
  id, nombre, email (único), password_hash, activo, fecha_creacion

leads
  id, nombre, email, telefono, estado, prioridad, fecha_creacion

propiedades
  id, titulo, tipo, precio, direccion, estado, fecha_creacion

interacciones
  id, lead_id → leads (ON DELETE CASCADE)
  tipo, notas, fecha_creacion

tareas
  id, titulo, descripcion, estado, prioridad, fecha_limite
  lead_id → leads (ON DELETE SET NULL)
  fecha_creacion

intereses
  id, lead_id → leads (ON DELETE CASCADE)
  propiedad_id → propiedades (ON DELETE CASCADE)
  nivel_interes, notas, fecha_creacion
  UNIQUE (lead_id, propiedad_id)
```

Decisiones sobre las claves foráneas:

- Al borrar un lead se borran sus interacciones y sus intereses, porque no tienen
  sentido sin él.
- Al borrar un lead sus tareas **se conservan** y quedan sin vínculo, porque el
  trabajo pendiente puede seguir siendo válido.
- `intereses` no es una tabla puente simple: guarda información propia
  (`nivel_interes`, `notas`), así que es una entidad de asociación.
- La restricción `UNIQUE` evita asociar dos veces la misma propiedad a un lead.

### Valores válidos

| Campo | Valores |
|---|---|
| `leads.estado` | Nuevo, Contactado, Calificado, Cerrado |
| `leads.prioridad` | Alta, Media, Baja |
| `propiedades.tipo` | Departamento, Casa, Terreno, Oficina |
| `propiedades.estado` | Disponible, Reservada, Vendida |
| `interacciones.tipo` | Llamada, Email, Visita, WhatsApp |
| `tareas.estado` | Pendiente, En Progreso, Completada |
| `tareas.prioridad` | Alta, Media, Baja |
| `intereses.nivel_interes` | Alto, Medio, Bajo |

## API

Rutas públicas:

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| POST | `/api/auth/login` | Devuelve el token de sesión |

Todo el resto exige la cabecera `Authorization: Bearer <token>` y responde `401`
sin ella.

| Método | Ruta |
|---|---|
| GET | `/api/auth/yo` |
| GET, POST | `/api/leads` |
| PUT, DELETE | `/api/leads/{id}` |
| GET, POST | `/api/propiedades` |
| PUT, DELETE | `/api/propiedades/{id}` |
| GET, POST | `/api/leads/{id}/interacciones` |
| GET, POST | `/api/tareas` |
| PUT, DELETE | `/api/tareas/{id}` |
| GET, POST | `/api/leads/{id}/intereses` |
| DELETE | `/api/intereses/{id}` |

La protección no se declara endpoint por endpoint: todos cuelgan de un router que
la declara una sola vez, de modo que cualquier endpoint nuevo que se agregue a ese
router queda protegido por omisión.

Los `PUT` son parciales: solo modifican los campos que se envían en el cuerpo.

Para probar la API desde `/docs`, hacer primero login, copiar el `access_token` y
pegarlo en el botón **Authorize**.

## Autenticación

- Las contraseñas se guardan hasheadas con bcrypt, con salt distinto por usuario.
- El token es un JWT firmado con `SECRET_KEY`, válido por 8 horas
  (configurable con `TOKEN_EXPIRA_MINUTOS`).
- El login devuelve el mismo error para correo inexistente, usuario inactivo y
  contraseña incorrecta, y tarda lo mismo en los tres casos, para no revelar qué
  correos están registrados.
- El estado `activo` del usuario se revisa en cada petición: dar de baja a alguien
  invalida sus tokens al instante.
- El frontend guarda el token en `localStorage` y valida la sesión contra el
  backend al cargar la página.

## Limitaciones conocidas

Están listadas a propósito: son decisiones tomadas para este alcance, no
descuidos.

- **El token se guarda en `localStorage`**, que es accesible desde JavaScript y
  por lo tanto expuesto a XSS. La alternativa robusta son cookies `httpOnly`, que
  complican CORS y el desarrollo local.
- **Sin límite de intentos de login.** Solo frena el costo de bcrypt (~220 ms por
  intento). Un límite real necesita middleware con registro de intentos.
- **`/docs` es accesible sin autenticación.** Útil en desarrollo; en producción
  habría que deshabilitarlo.
- **Sin roles.** Todos los usuarios tienen los mismos permisos y ven los mismos
  leads. No hay asignación de leads por ejecutivo.
- **Sin cambio de contraseña** desde la interfaz.
- **Sin paginación.** Los listados traen todos los registros.
- **Sin migraciones.** `create_all()` crea las tablas que faltan, pero **no agrega
  columnas a tablas que ya existen**. Al modificar un modelo existente hay que
  aplicar el cambio a mano en Supabase o incorporar una herramienta de
  migraciones.
- **CORS** está limitado a `localhost:3000` y `127.0.0.1:3000`. Al desplegar hay
  que agregar el dominio de producción en `backend/main.py`.

## Problemas frecuentes

**`tenant or user not found` al arrancar el backend.** El proyecto de Supabase
está pausado. Los proyectos del plan gratuito se pausan tras varios días sin
actividad; hay que reactivarlo desde el panel y esperar uno o dos minutos.

**`La variable SECRET_KEY no está definida`.** Falta completar `SECRET_KEY` en
`backend/.env`. Ver la sección de puesta en marcha.

**No se puede iniciar sesión y no hay usuarios.** Correr `python crear_usuario.py`.

**La aplicación responde con unos dos segundos de retardo.** Uvicorn escucha solo
en IPv4 y en Windows `localhost` se resuelve primero a IPv6, lo que agrega una
espera antes de reintentar. Se corrige creando `frontend/.env` con
`VITE_API_URL=http://127.0.0.1:8000`.

## Estado del proyecto

Implementado: gestión de leads, propiedades, interacciones, tareas y propiedades
de interés, con autenticación y vista de inicio con la operación del día.

Pendiente: priorización automática de leads, agente de IA (resumen del historial y
recomendación de próxima acción), documentos y auditoría.
