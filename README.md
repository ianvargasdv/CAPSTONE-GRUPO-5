# CRM Inmobiliario - Capstone Grupo 5

Sistema de gestión para ejecutivos inmobiliarios: prospectos (leads), catálogo de
propiedades, historial de contacto, tareas de seguimiento y propiedades de interés
de cada lead.

Incluye un agente de IA que resume el historial de un lead y recomienda la siguiente
acción, priorización automática de la cartera y un registro de auditoría de todo lo
que se modifica.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy, Uvicorn
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
  auditoria.py       Registro de quién hizo qué y comparación de cambios
  crear_usuario.py   Script para dar de alta usuarios
  cambiar_rol.py     Script para cambiar el rol de un usuario
  migrar.py          Aplica cambios de estructura sobre tablas existentes
  prueba_auditoria.py  Verifica que ningún endpoint de escritura quede sin auditar

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
pip install -r requirements.lock.txt
Copy-Item .env.example .env
```

`requirements.lock.txt` contiene las versiones exactas que se probaron en el
proyecto; `requirements.txt` enumera las dependencias directas para cuando sea
necesario actualizarlas. El último comando crea `backend/.env` desde la plantilla.
Completar al menos dos valores:

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

Cada persona genera su propia `SECRET_KEY`; no hace falta que sea igual entre
integrantes. El archivo `.env` está en el `.gitignore` y no se sube al repositorio.
La configuración no secreta se mantiene sincronizada modificando `.env.example`,
nunca copiando el `.env` real al repositorio.

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
asistente. El **admin** además ve el consumo del agente de IA y el registro de
actividad. No existe un rol para clientes porque los clientes no acceden al CRM: se
comunican con la inmobiliaria y sus datos los registra el ejecutivo.

Para cambiar el rol de un usuario que ya existe:

```powershell
python cambiar_rol.py
```

### Frontend

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

`npm ci` instala exactamente las versiones registradas en `package-lock.json`. El
frontend queda en `http://localhost:3000` y apunta al backend en `localhost:8000`.
Para cambiar la dirección, editar `frontend/.env` y usar, por ejemplo,
`VITE_API_URL=http://127.0.0.1:8000`.

## Modelo de datos

```
usuarios       id, nombre, email (único), password_hash, rol, activo, fecha_creacion
leads          id, nombre, email, telefono, estado, prioridad, fecha_creacion
propiedades    id, titulo, tipo, precio, direccion, estado, fecha_creacion
interacciones  id, lead_id, tipo, notas, fecha_creacion
tareas         id, titulo, descripcion, estado, prioridad, fecha_limite, lead_id
intereses      id, lead_id, propiedad_id, nivel_interes, notas, fecha_creacion
analisis_ia    id, lead_id, usuario_id, tipo, entrada, salida, modelo,
               tokens_entrada, tokens_salida, costo_estimado_usd, fecha_creacion
auditoria      id, usuario_id, usuario_email, accion, entidad, entidad_id,
               descripcion, detalle, fecha_creacion
```

Sobre las relaciones:

- Al borrar un lead se borran sus interacciones, sus intereses y sus análisis, porque
  no tienen sentido sin él.
- Al borrar un lead sus tareas se conservan y quedan sin vínculo, porque el trabajo
  pendiente puede seguir siendo válido.
- Al borrar un usuario, sus análisis y sus registros de auditoría se conservan con la
  clave foránea en nulo. En auditoría el correo está además guardado como texto, para
  que el registro siga diciendo quién actuó aunque la cuenta ya no exista.
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

## Registro de actividad

Cada vez que alguien crea, modifica o elimina un registro, o genera un análisis con
IA, queda una entrada en la tabla `auditoria` con quién lo hizo, cuándo, sobre qué y
qué cambió. En una inmobiliaria donde varios ejecutivos trabajan la misma cartera es
la única forma de responder por qué un lead cambió de estado o quién sacó una
propiedad del catálogo.

En las modificaciones se compara el registro antes y después, y se guarda solo lo que
cambió de verdad: `estado: Nuevo -> Contactado; prioridad: Media -> Alta`. Se compara
el resultado y no lo que venía en la petición, porque enviar un campo con el mismo
valor que ya tenía no es un cambio.

El registro se escribe en la misma transacción que la operación que describe. O se
guardan las dos cosas o no se guarda ninguna: no puede quedar una acción sin rastro
ni un rastro de algo que falló.

El listado está en la sección **Actividad** y lo ve solo el rol admin. Tiene filtros
por usuario, tipo de registro, tipo de acción y rango de fechas, búsqueda por texto y
paginación. Un ejecutivo no puede consultarlo: el backend responde 403.

La auditoría se registra llamando explícitamente a `auditoria.registrar()` en cada
endpoint, en lugar de detectarla sola con un listener de SQLAlchemy. El automático
producía registros falsos, porque había endpoints que modificaban objetos en memoria
solo para poder serializarlos y el listener lo interpretaba como un cambio real. Un
registro con entradas falsas no sirve, porque su único valor es que se pueda confiar
en él. La contrapartida es que se puede olvidar en un endpoint nuevo, y eso lo cubre
`prueba_auditoria.py`:

```powershell
cd backend
python prueba_auditoria.py
```

Recorre los endpoints de escritura y comprueba que todos dejen rastro, además de los
filtros, la paginación y el acceso por rol. Corre sobre una base SQLite temporal que
crea y borra sola, así que no toca los datos reales, y reemplaza el proveedor de IA
por uno falso para no gastar crédito. Al agregar un endpoint de escritura hay que
sumarlo a esa prueba.

Las reglas de entrada tienen una prueba separada que cubre formatos, valores
permitidos, límites y correos duplicados:

```powershell
cd backend
python prueba_validaciones.py
```

El orden de los próximos módulos y su criterio de terminado están en
[`ROADMAP.md`](ROADMAP.md).

No hay forma de borrar ni editar entradas del registro desde la API. Es a propósito:
un historial que se puede alterar no sirve como historial.

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
- No hay cambio de contraseña desde la interfaz.
- Solo el registro de actividad está paginado. Los demás listados traen todo, porque
  su tamaño lo acota la operación del negocio; el de actividad crece con cada acción.
- Los filtros de fecha del registro de actividad toman días completos en UTC, que es
  la zona en que se guardan las fechas. Con horario chileno el corte puede caer unas
  horas antes de la medianoche local.
- El registro de actividad no tiene purga: crece indefinidamente. Con el volumen de un
  MVP no es un problema, pero en producción habría que archivar lo antiguo.
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
recomendación), seguimiento del consumo del agente, registro de actividad y vista de
inicio.

Pendiente: documentos.
