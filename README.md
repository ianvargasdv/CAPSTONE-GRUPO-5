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
  seguridad.py       Contraseñas, tokens, roles y autorización
  prioridad.py       Reglas de priorización de leads
  ia.py              Integración con el modelo de lenguaje
  crear_usuario.py   Script para dar de alta usuarios
  cambiar_rol.py     Script para cambiar el rol de un usuario
  migrar.py          Aplica cambios de estructura sobre tablas existentes

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

Opcionalmente se puede configurar el proveedor de IA que genera los resúmenes. Si se
deja vacío el sistema funciona igual, solo no ofrece generarlos:

```
IA_BASE_URL=http://localhost:11434/v1
IA_API_KEY=local
IA_MODELO=llama3
```

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

Pide nombre, correo, rol y contraseña. Sin al menos un usuario no se puede entrar.

Hay dos roles. El **ejecutivo** trabaja la cartera: leads, propiedades, tareas y el
asistente. El **admin** además ve el panel de consumo del agente de IA. No existe un
rol para clientes porque los clientes no acceden al CRM: se comunican con la
inmobiliaria y sus datos los registra el ejecutivo.

Para cambiar el rol de un usuario que ya existe:

```powershell
python cambiar_rol.py
```

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

## Asistente con IA

Desde la ficha de un lead se pueden pedir dos análisis:

- **Resumen de la situación**: describe en qué punto está el prospecto.
- **Siguiente acción recomendada**: propone qué hacer, revisando las tareas
  pendientes para no proponer algo que ya está agendado.

El backend arma un texto con los datos registrados (historial de contacto,
propiedades de interés, prioridad calculada y tareas pendientes), lo envía al modelo
y guarda en `analisis_ia` tanto lo que se envió como lo que respondió. Los dos tipos
parten de la misma ficha y se diferencian solo en las instrucciones.

Cada generación ocurre al presionar el botón. No hay procesos automáticos ni
llamadas al abrir la ficha, porque cada llamada al proveedor tiene costo.

### Consumo y costo

De cada llamada se guardan los tokens que informa el proveedor y el costo estimado
calculado con los precios de `IA_PRECIO_ENTRADA_USD_MILLON` e
`IA_PRECIO_SALIDA_USD_MILLON`. El costo se calcula al momento de generar el análisis
y se almacena, para que cambiar de modelo o de precio después no altere el histórico.

Es una estimación para tener referencia mientras se usa el sistema. El valor que
manda es el del panel de facturación del proveedor.

Si el proveedor no informa el consumo, los tokens y el costo quedan en nulo. No se
guarda cero, porque un cero se leería como que la llamada fue gratis.

El rol admin tiene una sección que muestra el gasto acumulado, el desglose por tipo
de análisis, por modelo y por día, y cuánto queda del presupuesto declarado en
`IA_PRESUPUESTO_USD`. También muestra la configuración vigente del proceso, porque
la configuración se lee al arrancar: si se cambia el `.env` hay que reiniciar el
servidor para que tome efecto.

Se guarda la entrada además de la salida para poder verificar de dónde salió cada
resumen. La ficha permite desplegar esa información, y el texto siempre aparece
identificado como generado automáticamente con su fecha y el modelo que lo produjo.

La integración usa el formato de chat completions compatible con OpenAI, así que
sirve tanto un servicio alojado como un modelo local. Cambiar de proveedor es cambiar
`IA_BASE_URL` e `IA_MODELO` en el `.env`.

La llamada al proveedor se hace desde el backend. Si se hiciera desde el navegador la
clave viajaría al cliente y cualquiera podría leerla.

## Limitaciones conocidas

- El token se guarda en `localStorage`, que es accesible desde JavaScript y por lo
  tanto vulnerable a XSS. Lo más robusto serían cookies `httpOnly`, que complican
  CORS y el desarrollo local.
- No hay límite de intentos de login. Solo frena el costo de bcrypt.
- `/docs` es accesible sin autenticación. En producción habría que deshabilitarlo.
- `create_all()` crea las tablas que faltan pero no agrega columnas a tablas que ya
  existen. Para eso está `migrar.py`, que aplica los cambios de estructura con
  `IF NOT EXISTS` y se puede correr las veces que sea necesario. Hay que ejecutarlo
  después de traer cambios que agreguen columnas a una tabla existente.
- CORS está limitado a `localhost:3000`. Al desplegar hay que agregar el dominio en
  `backend/main.py`.
- No hay asignación de leads por ejecutivo: todos ven la misma cartera.
- No hay cambio de contraseña desde la interfaz ni paginación en los listados.
- Los roles se asignan por terminal, no desde la aplicación. Es deliberado: un
  endpoint para cambiar roles sería una vía para que alguien se diera permisos.

## Problemas (evitables pero probables)

**`tenant or user not found` al arrancar el backend.** El proyecto de Supabase está
pausado por inactividad. Hay que reactivarlo desde el panel y esperar un par de
minutos.

**`La variable SECRET_KEY no está definida`.** Falta completar `SECRET_KEY` en
`backend/.env`.

**No se puede entrar y no hay usuarios.** Correr `python crear_usuario.py`.

**La aplicación tarda unos dos segundos en responder.** Uvicorn escucha solo en IPv4
y en Windows `localhost` se resuelve primero a IPv6. Se corrige creando
`frontend/.env` con `VITE_API_URL=http://127.0.0.1:8000`.

## Alcance del proyecto actual (MVP) 

Implementado: leads, propiedades, interacciones, tareas, propiedades de interés,
autenticación con roles, priorización de leads, asistente con IA (resumen y
recomendación), seguimiento del consumo del agente y vista de inicio.

Pendiente: documentos y auditoría.
