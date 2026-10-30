# CRM Inmobiliario - Capstone Grupo 5

Sistema de gestión para ejecutivos inmobiliarios: prospectos (leads), catálogo de
propiedades, historial de contacto, tareas de seguimiento y propiedades de interés
de cada lead.

## Cartera de clientes · avance local del 29/10/2026

En **Leads**, el selector **Cartera** permite alternar entre **Todos los clientes**
y **Mi cartera**. Mi cartera usa el usuario de la sesión y la asignación vigente,
no un nombre escrito en la búsqueda. Administración también puede elegir un
responsable activo o consultar clientes sin asignar.

La búsqueda, estado y nivel de atención se combinan dentro de esa cartera. El
contador muestra los resultados respecto de los clientes de la cartera elegida.
**Actualizar cartera** vuelve a consultar los datos; una cartera vacía conserva
los controles para regresar a Todos. Una reasignación se refleja al recargar.

Esta función organiza el listado, sin cambiar la visibilidad que ya existía en
Todos ni reasignar tareas, visitas u oportunidades. La API valida los filtros y
reserva los de responsable y sin asignar a administración. No requiere migración.
Pruebas sin costo: `python prueba_cartera.py` desde `backend` y
`node --test src/cartera.test.js` desde `frontend`.

## Notas de llamada con IA · avance local del 29/10/2026

En la ficha del cliente, abre **Asistente** y selecciona **Notas de una llamada**.
Introduce notas de una llamada que ya realizaste y solicita
la propuesta. Incluye resumen, requisitos mencionados y próxima acción cuando las
notas la respalden. Revisa y edita el texto y pulsa **Confirmar y registrar llamada**
para guardarlo como una interacción normal. Descartar conserva las notas sin
registrar el contacto. Si falla el guardado, el texto editado permanece disponible.

Preparar consulta al proveedor y guarda el análisis original con su consumo; no
guarda un contacto ni modifica requisitos, tareas o visitas. Las propuestas previas
se consultan en el mismo bloque y no acreditan por sí solas una llamada registrada.
La función usa `analisis_ia` e `interacciones` existentes: no requiere migración.

Comprobación sin costo desde `backend`: `python prueba_llamada.py`. Se validaron
el flujo y los errores con un proveedor simulado y SQLite temporal. La calidad de
las respuestas reales de esta nueva función sigue pendiente de evaluación; no se
reutiliza la autorización de llamadas pagadas de octubre.

## Evaluación del asistente

Desde `backend`, se pueden validar once casos ficticios para las cinco funciones y comprobar el registro
de evaluaciones sin abrir el CRM, conectarse a Supabase ni gastar saldo:

```powershell
.\venv\Scripts\python.exe evaluar_asistente.py validar
.\venv\Scripts\python.exe evaluar_asistente.py ejecutar --salida evaluacion_01.json
.\venv\Scripts\python.exe evaluar_asistente.py resumir evaluacion_01.json
.\venv\Scripts\python.exe prueba_evaluacion.py
.\venv\Scripts\python.exe prueba_evaluacion_real.py
```

El comando `ejecutar` genera únicamente salidas simuladas y no mide la calidad del
modelo. El conjunto conserva los nueve casos anteriores y añade dos de llamada:
requisitos explícitos y notas contradictorias con una orden pegada. La versión 1
del conjunto anterior sigue siendo válida; el conjunto de cinco funciones usa versión 2.
Cada ejecución queda identificada y sus respuestas empiezan pendientes de revisión.
Los criterios de cada caso están en `backend/casos_asistente.json`; su fecha de
referencia es fija para que el sentido de una visita o tarea vencida no cambie
según el día de ejecución. La evidencia real anterior del 16/10 se conserva intacta.

Para registrar una revisión, primero se lee la ficha, la respuesta y los criterios
en el archivo. Luego se indica el identificador del caso, la decisión, el nombre
de quien revisó y una observación concreta. Se guarda otro archivo, no se reemplaza
el original. Revisar una simulación no acredita la calidad del modelo real.

```powershell
# Sustituye el autor y la observación por los de la revisión efectivamente realizada.
.\venv\Scripts\python.exe evaluar_asistente.py revisar evaluacion_01.json --caso resumen_visita_pasada --estado rechazado --autor "Nombre del revisor" --observacion "Observación de la revisión" --salida evaluacion_01_revisada.json
.\venv\Scripts\python.exe evaluar_asistente.py ejecutar --fallo-caso resumen_visita_pasada --salida evaluacion_02.json
.\venv\Scripts\python.exe evaluar_asistente.py comparar evaluacion_01.json evaluacion_02.json --salida comparacion_01_02.json
```

El segundo ejemplo simula un error sin contactar a un proveedor. La comparación
usa el identificador y la huella de cada caso: si cambian su ficha o sus criterios,
lo señala como no comparable. Las huellas detectan diferencias, no autentican al
autor de un archivo. No hay aprobación automática ni un porcentaje de precisión.
Los archivos de salida deben ser nuevos y su carpeta debe existir.

### Lote con el proveedor real

Primero prepara y revisa un plan. Este paso no realiza llamadas ni usa Supabase:

```powershell
.\venv\Scripts\python.exe evaluar_asistente.py planificar-real --max-llamadas 11 --presupuesto-usd 0.10 --max-tokens-salida 900 --salida plan_01.json
```

El plan detalla casos, modelo, precios configurados, límite por respuesta y reserva
estimada. La entrada se estima por sus bytes más un margen de formato: no es un
tokenizador del proveedor ni una garantía de facturación. Requiere precios positivos
y finitos. Si la configuración, el código de IA o las reservas cambian, hay que
preparar otro plan. No se incluyen claves ni una conexión a la base de datos.

Sólo después de autorizar expresamente ese lote y su presupuesto se ejecuta el
comando siguiente, sustituyendo el identificador por el del plan revisado:

```powershell
.\venv\Scripts\python.exe evaluar_asistente.py ejecutar-real --plan plan_01.json --confirmar-lote IDENTIFICADOR_DEL_LOTE --salida evaluacion_real_01.json
.\venv\Scripts\python.exe evaluar_asistente.py resumir evaluacion_real_01.json
```

Cada plan se usa una sola vez desde su carpeta: se crea una marca de consumo que
no debe borrarse para reintentar. Un nuevo lote exige otro plan y otra confirmación.
El archivo de resultados se reserva antes de llamar y se actualiza con puntos de
control. `llamadas_reales` cuenta los intentos iniciados, no cargos confirmados.
Ante un error o interrupción se conserva la evidencia parcial, sin reintentos
automáticos. Si faltan tokens, cambia el modelo respondido o el consumo supera la
estimación, el lote se detiene. Un costo desconocido queda nulo, no como gratis.

Las respuestas válidas quedan pendientes de revisión; el JSON de llamadas también
debe cumplir el esquema de la aplicación. Los comandos `revisar` y `comparar`
admiten estos resultados nuevos sin convertir simulaciones en respuestas reales.
La comparación marca los modos diferentes como no comparables. Las evidencias
históricas del 16/10 no se reescriben ni se importan como una nueva ejecución.

### Resultado inicial · 29/10/2026

Se ejecutó un lote autorizado de once casos, con costo total estimado de
US$0,0013079. Llegaron once respuestas sin errores de transporte. La revisión
técnica asistida no detectó problemas en diez y encontró un hallazgo en el
borrador con una propiedad reservada: atribuye al inmueble la comuna buscada
por el cliente, que no estaba informada para esa propiedad, y deja ambiguo
el efecto del estado sobre su disponibilidad.

SCRUM-42 registra la corrección. Las reglas ahora separan requisitos del cliente
y atributos del inmueble, respetan los estados no disponibles y muestran la
comuna de la propiedad como sin registrar cuando falta. Se reforzaron los criterios
del caso sin cambiar su entrada ni la evidencia original. Pasaron 145 comprobaciones
sin costo tras el ajuste. Un segundo lote autorizado de dos casos respondió según
los criterios en la revisión técnica asistida: no atribuyó al inmueble la comuna
buscada, respetó la reserva y conservó la contradicción de dormitorios pendiente
de aclarar. Este segundo lote costó US$0,0004061 estimados.

Resultados originales: `backend/evidencias/evaluacion_real_20261029.json`.
Observaciones separadas: `backend/evidencias/revision_asistida_20261029.json`.
La revisión asistida no sustituye la humana: las once respuestas originales
permanecen pendientes de esa revisión. La muestra no acredita precisión general.
La regresión y sus observaciones se conservan en
`backend/evidencias/evaluacion_regresion_disponibilidad_20261029.json` y
`backend/evidencias/revision_asistida_regresion_20261029.json`, también sin registrar
una aprobación humana. Entre ambos lotes se hicieron trece llamadas autorizadas
por US$0,0017140 estimados.

## Comprobación del asistente · 16/10/2026

### Presentación y uso del CRM · módulo posterior

Se retiraron los marcadores Demo de los nombres del escenario inicial y de sus
títulos de propiedades. Los datos siguen siendo ficticios: se conserva la marca
interna del cliente y la descripción de origen en las propiedades. El historial y
los análisis guardados no se reescriben para ocultar cómo eran los registros antes.
`backend/normalizar_presentacion.py` permite revisar los conteos; con `--aplicar`
normaliza en una transacción y registra el cambio. Ya se aplicó el 16/10/2026:
29 clientes con cambios de nombre y/o origen y cinco propiedades. Una segunda
ejecución no cambió nada. No requiere una migración de estructura.

Mejoras de interfaz verificadas en un escenario temporal:

- Búsqueda sin tildes por cliente, responsable, comuna o código, según la vista.
- Catálogo filtrable por venta/arriendo y botón para limpiar filtros.
- Tareas con filtro Sólo vencidas, texto de vencimiento y detalles desplegables.
- Acciones de editar/eliminar visibles sin pasar el mouse y moneda/estado en intereses.
- Formularios con campos obligatorios marcados y ficha opcional plegable de propiedades.
- Paneles utilizables con Tab, Shift+Tab y Escape, con retorno del foco al disparador.
- Navegación con nombres accesibles en móvil y desplazamiento interno de tablas.
- Indicador de sesión en vez de afirmar una conexión a Supabase sin comprobarla.

La interfaz se revisó como administrador y ejecutivo; no se añadieron permisos ni
un portal para clientes externos. Pruebas: 221 comprobaciones del backend y 14 del
frontend aprobadas; compilación correcta. No equivale a una auditoría exhaustiva de
accesibilidad, seguridad o todos los dispositivos.

Se amplió el contexto con fecha de referencia, moneda y estado de las propiedades
de interés. Las preguntas consideran también requisitos expresamente pendientes
en notas o tareas, no sólo los campos básicos del perfil. Se reforzaron las
instrucciones para fechas pasadas, contradicciones y texto malicioso en notas.

Se revisaron ocho respuestas reales con fichas ficticias: requisitos adicionales,
perfil completo, contradicciones, visita pasada, no contacto, instrucción maliciosa,
UF con propiedad reservada y tarea vencida existente. En esta muestra se respetaron
los criterios de cada caso; no es una garantía de exactitud futura. Los resultados
y límites están en `backend/evidencias/evaluacion_calidad_20261016.json`.

### Escenario ficticio con nombres naturales

`backend/cargar_escenario_pruebas.py` añade 24 clientes y 18 propiedades con actividad
vinculada. No añade “Demo” a sus nombres o títulos. Los clientes conservan
`es_demo=true` (la interfaz muestra “Datos de prueba”); las propiedades tienen código
`PRUEBA-CRM-*` y descripción que identifica el escenario ficticio. Los correos usan
`example.test`, los teléfonos quedan vacíos y no se incluyen fotografías de inmuebles
reales. Los precios y ubicaciones son inventados, no ofertas ni referencias de mercado.

```powershell
cd backend
.\venv\Scripts\python.exe cargar_escenario_pruebas.py
# Sólo muestra el alcance. Para aplicarlo sobre la base configurada:
.\venv\Scripts\python.exe cargar_escenario_pruebas.py --aplicar
```

La carga del 16/10/2026 ya está aplicada y verificada. Una segunda ejecución añadió
cero registros. Conserva los registros existentes y sus ediciones, y deja una
auditoría identificada como carga ficticia, no como actividad real del equipo.
Se ejecuta en una transacción y revierte si detecta colisiones de sus claves.
No ejecutar dos cargas en paralelo. No necesita una nueva migración.

Pruebas sin costo, desde `backend`: `python prueba_escenario_pruebas.py` y
`python prueba_asistente.py`. No ejecutan generaciones reales.

Incluye un asistente de IA para resumir el historial, recomendar la siguiente
acción, preparar un borrador de seguimiento y sugerir preguntas sobre datos
comerciales faltantes. Los textos requieren revisión humana: el asistente no envía
mensajes ni actualiza la ficha del cliente. También incluye priorización por reglas
y un registro de auditoría.

### Validación de las nuevas funciones de IA · 15/10/2026

El borrador se puede editar y copiar desde la ficha. La edición es temporal; no se
guarda como contacto. Las preguntas se muestran para que el ejecutivo decida cómo
completar el perfil. No se necesita una migración adicional para estos dos tipos.

Las 16 pruebas nuevas usan un proveedor simulado y una base temporal. La primera
validación real falló por una credencial rechazada (`401 invalid_api_key`). Tras
reemplazarla, la consulta del modelo respondió 200 y se obtuvieron las cuatro
respuestas esperadas: borrador y preguntas para dos perfiles ficticios, uno completo
y otro incompleto. Se revisaron los textos contra sus entradas; no se observaron
propiedades, visitas ni preferencias inventadas en esta muestra. El perfil completo
no recibió preguntas adicionales sobre datos que ya tenía.

La muestra no cubre todos los casos ni demuestra ausencia de errores futuros.
Los borradores aún pueden usar expresiones internas del CRM y deben revisarse antes
de compartirlos con un cliente. Estas pruebas no escribieron en Supabase ni enviaron
mensajes. El registro reproducible está en `backend/evidencias/validacion_asistente_20261015.json`.

### Convertir una recomendación en seguimiento

En la ficha del lead, abre **Siguiente acción recomendada** y pulsa **Revisar y
preparar tarea** sobre un análisis existente. Se consultan las tareas actuales y se
abre el formulario con el lead vinculado y el texto de origen en la descripción.
Si otra tarea ya cubre la acción, pulsa **Abrir tarea existente** junto a ese pendiente:
se abre en modo edición con sus datos originales, sin crear otra ni sustituir su
descripción. La propuesta de IA queda desplegable como referencia. Sólo se modifica
la tarea al confirmar **Guardar cambios**. Si se necesita una tarea diferente,
edita la propuesta nueva y confirma **Crear tarea**.
Cancelar no guarda nada. La fecha queda vacía y la prioridad parte de Media, como
en cualquier tarea nueva: no se extraen compromisos ni fechas del texto del modelo.

La creación usa el registro de auditoría habitual. No envía mensajes, no agenda
visitas, no permite cambiar a otro lead desde ese borrador y no prepara tareas para
leads cerrados. La lista de pendientes es una comprobación al abrir, no un bloqueo
de duplicados entre usuarios concurrentes. Preparar una recomendación ya guardada
no consume IA; **Generar de nuevo** sí llama al proveedor.

Pruebas locales del preparador: `node --test src/tareaDesdeIA.test.js` desde
`frontend`. No requiere instalar dependencias adicionales ni migrar la base.

WhatsApp no está integrado. Como siguiente etapa se propone conectar una cuenta y
número de Meta mediante Cloud API, recibir eventos verificados y mantener revisión
humana del envío. Requiere configuración y pruebas propias; no forma parte de lo
validado aquí. Referencia técnica: [ejemplos oficiales de Meta](https://github.com/fbsamples/whatsapp-api-examples).

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
  matching.py        Reglas explicables de coincidencia lead–propiedad
  ia.py              Integración con el modelo de lenguaje
  auditoria.py       Registro de quién hizo qué y comparación de cambios
  crear_usuario.py   Script para dar de alta usuarios
  cambiar_rol.py     Script para cambiar el rol de un usuario
  migrar.py          Aplica cambios de estructura sobre tablas existentes
  cargar_datos_demo.py  Carga un escenario ficticio e idempotente para la presentación
  prueba_auditoria.py  Verifica que ningún endpoint de escritura quede sin auditar
  prueba_validaciones.py  Verifica reglas de entrada y casos límite
  prueba_oportunidades.py  Verifica el avance, cierre y reapertura del pipeline
  prueba_visitas.py  Verifica agenda, cruces de horario, estados y auditoría
  prueba_matching.py  Verifica puntaje, cobertura, orden y datos incompletos
  prueba_catalogo.py  Verifica ficha, fotografías, estados, permisos y auditoría
  prueba_asignaciones.py  Verifica responsables, historial, permisos y conflictos
  consolidar_asignaciones.py  Importa movimientos anteriores sin borrar su origen
  prueba_consolidacion.py  Verifica fechas, datos ausentes e importación sin duplicados
  prueba_asistente.py  Verifica los cuatro tipos, permisos y fallos sin consumir IA

frontend/src/
  App.jsx            Estado general y navegación
  api.js             Llamadas a la API
  index.css          Estilos
  components/        Tablas, formularios, paneles e iconos
```

## Cómo levantar el proyecto

### Publicación con Cloudflare Pages y Render

La interfaz se publica en Cloudflare Pages y la API de Python en Render. Supabase
continúa alojando la base. Con ambos servicios publicados, los visitantes sólo
necesitan navegador e internet; no dependen de este computador.

1. Publica en Git la versión que se vaya a desplegar. En Render, crea un Blueprint
   desde este repositorio utilizando `render.yaml`. El archivo propone el plan
   gratuito y desactiva las publicaciones automáticas por cada commit. Define
   `DATABASE_URL` con la conexión de Supabase y `CORS_ORIGINS` con el dominio final
   de Pages, por ejemplo `https://NOMBRE-DEL-PROYECTO.pages.dev`. La clave de sesión
   se genera en Render. Para habilitar la IA, configura allí su dirección, clave y
   modelo; las claves nunca se copian al frontend. `IA_TEMPERATURA` queda vacía.
   Puedes configurar también los precios y presupuesto indicados en
   `backend/.env.example` para mostrar las estimaciones de consumo.
2. Espera a que la API esté disponible y guarda su URL HTTPS. Si la conexión
   directa de Supabase no es compatible con la red del alojamiento, usa su
   conexión de pooler de sesión. No cambies las tablas ni vuelvas a cargar datos
   para publicar. La aplicación conserva su comportamiento de inicialización
   existente; el script de publicación no ejecuta migraciones ni cargas.
3. En PowerShell, desde la raíz del repositorio, inicia sesión en Cloudflare:

   ```powershell
   npx.cmd --yes wrangler@4 login
   ```

4. Publica la interfaz sustituyendo ambos valores por los reales:

   ```powershell
   .\publicar-web.ps1 -ApiUrl "https://TU-BACKEND.onrender.com" -Proyecto "TU-PROYECTO" -CrearProyecto
   ```

   El nombre del proyecto va en minúsculas, con números o guiones. Si el proyecto
   de Pages ya existe, omite `-CrearProyecto`. El script comprueba `/health` y el
   permiso del dominio antes de compilar. Sólo sube `frontend/dist`; no sube el
   backend, documentos ni archivos `.env`. No usa la IA para comprobar el servicio.
   Al terminar muestra la dirección `https://TU-PROYECTO.pages.dev`.

Para compilar sin publicar ni consultar el backend, añade `-SoloPreparar` y omite
`-CrearProyecto`. Ese modo no confirma que el servidor público esté disponible.
La primera ejecución de Wrangler puede descargar su herramienta desde npm.
Un enlace alojado no garantiza disponibilidad: el plan gratuito de Render puede
suspender el servicio por inactividad y tardar en responder al volver a abrirlo.

Comprobación local sin red: desde `backend`, ejecuta `python prueba_publicacion.py`.
Se conserva la ejecución local con `localhost:3000`; `CORS_ORIGINS` sólo añade
dominios concretos y no sustituye la autenticación por sesión.

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
python migrar.py
uvicorn main:app --reload
```

Queda en `http://localhost:8000`, con la documentación de la API en `/docs`. Al
arrancar crea las tablas que falten. `migrar.py` agrega columnas nuevas a tablas
existentes sin borrar datos y puede ejecutarse más de una vez.

Si existe `historial_asignaciones`, la migración incorpora sus movimientos en
`asignaciones_lead` y conserva la tabla anterior. Mantiene las fechas, nombres
registrados y correo del autor; el nombre del autor se obtiene de la cuenta actual.
El identificador de origen impide importar dos veces el mismo movimiento. No cambia
el responsable actual del lead ni crea eventos nuevos en Actividad. Los movimientos
se consultan por fecha, usando el id para desempatar.

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

### Datos para una demostración

Después de crear al menos un usuario y ejecutar la migración se puede cargar un
escenario coherente con cinco leads, cinco propiedades, cinco oportunidades, cinco
visitas, intereses, contactos y tareas:

```powershell
python cargar_datos_demo.py
```

El script es idempotente: repetirlo no duplica el escenario. Todos los registros
son ficticios, usan correos del dominio reservado `example.test`, teléfonos
imposibles y se distinguen por la marca interna de prueba y la descripción del inmueble. No deben
presentarse como datos de clientes reales.

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
leads          id, nombre, email, telefono, estado, prioridad, ejecutivo_id,
               tipo_operacion, presupuesto_min, presupuesto_max, moneda,
               comunas_interes, tipo_propiedad_buscada, dormitorios_min,
               banos_min, plazo_decision, financiamiento, origen,
               proxima_accion, fecha_proxima_accion, es_demo, fecha_creacion
propiedades    id, titulo, tipo, tipo_operacion, precio, moneda, direccion,
               comuna, dormitorios, banos, estado, fecha_creacion
oportunidades  id, lead_id, propiedad_id, ejecutivo_id, tipo_operacion, etapa,
               valor_estimado, moneda, probabilidad, fecha_cierre_estimada,
               fecha_cierre, motivo_cierre, notas, fechas de creación/actualización
visitas        id, lead_id, propiedad_id, oportunidad_id, ejecutivo_id, fecha_hora,
               duracion_minutos, estado, modalidad, punto_encuentro, resultado,
               motivo_cancelacion, proxima_accion, fechas de creación/actualización
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
- Al borrar un lead o una propiedad, las oportunidades se conservan con el vínculo
  correspondiente en nulo para no perder el historial de ventas y cierres.
- Al borrar un lead, una propiedad, una oportunidad o un ejecutivo, las visitas se
  conservan y el vínculo eliminado queda en nulo para mantener el historial.
- Al borrar un usuario, sus análisis y sus registros de auditoría se conservan con la
  clave foránea en nulo. En auditoría el correo está además guardado como texto, para
  que el registro siga diciendo quién actuó aunque la cuenta ya no exista.
- `intereses` guarda datos propios (`nivel_interes`, `notas`), así que es una
  entidad de asociación y no una simple tabla puente. Tiene una restricción única
  sobre `(lead_id, propiedad_id)` para no asociar dos veces la misma propiedad.

La API valida estados, tipos, prioridades, correos, teléfonos, largos y rangos
numéricos aunque la petición no venga desde el formulario. También impide correos
de lead duplicados sin distinguir mayúsculas y presupuestos cuyo mínimo supere al
máximo.

## Perfil 360 del lead

La ficha reúne datos de contacto y calificación comercial: compra o arriendo,
presupuesto y moneda, comunas, tipo de propiedad, dormitorios, baños, plazo,
financiamiento, origen y próxima acción. Los campos son opcionales porque un lead
puede entrar con información mínima y completarse durante las conversaciones.

Al crear un lead queda asignado automáticamente al usuario que lo registró.
Desde la ficha, administración puede cambiar el responsable por otro usuario
activo (ejecutivo o administrador). El listado y la ficha muestran el responsable
actual; ambos roles pueden consultar el historial de responsables.

Cada cambio conserva responsable anterior, nuevo responsable, autor y fecha en
`asignaciones_lead`, además del registro general de actividad. Guardar el mismo
responsable no genera otro movimiento. Si otra sesión cambió la asignación, la API
devuelve un conflicto y pide actualizar la ficha antes de volver a guardar.
Los leads anteriores no reciben movimientos ni fechas reconstruidas.

Para incorporar la tabla en una base existente, ejecutar `python migrar.py` desde
`backend` antes de utilizar esta versión. La migración no rellena historial antiguo.

## Oportunidades y pipeline

Un lead representa a la persona; una oportunidad representa un negocio concreto.
Puede vincularse a una propiedad y avanza por `Contacto`, `Visita`, `Oferta`,
`Negociación`, `Ganada` o `Perdida`. La interfaz ofrece un tablero Kanban y una
vista tabla, con cambio rápido de etapa.

Cada etapa propone una probabilidad comercial (10%, 30%, 60%, 80%, 100% o 0%). El
ejecutivo puede ajustarla cuando tiene información más precisa. El tablero separa
CLP y UF al sumar el valor abierto y muestra además el pipeline ponderado: valor
multiplicado por probabilidad, que es una proyección y no una venta asegurada.

Al cerrar como perdida el motivo es obligatorio; al ganar o perder se registra la
fecha real. Si el negocio se reabre, se limpian la fecha y el motivo anterior. Las
oportunidades conservan su historial aunque el lead o la propiedad se eliminen, y
todas sus escrituras quedan en auditoría.

## Agenda de visitas

Cada visita relaciona lead, propiedad, oportunidad opcional y ejecutivo. La vista
semanal permite avanzar o retroceder por semanas, filtrar por estado y alternar con
una lista. También muestra cuántas visitas hay hoy, próximas, confirmadas y
realizadas.

El sistema impide que un ejecutivo tenga dos visitas superpuestas; sí permite que
una comience exactamente cuando termina la anterior. Una visita realizada exige
registrar su resultado y una cancelada exige el motivo. Las canceladas y las
inasistencias dejan libre el horario. Todas las creaciones, cambios y eliminaciones
quedan registradas en auditoría.

## Matching lead–propiedad

La ficha del lead ordena las propiedades disponibles según seis criterios: operación,
tipo de inmueble, comuna, presupuesto, dormitorios y baños. El resultado muestra dos
valores distintos: el porcentaje de coincidencia entre lo que sí pudo compararse y
la cobertura, que indica cuántos datos estaban disponibles. Así una coincidencia de
100% con solo un criterio cargado no se presenta como una recomendación completa.

Cada criterio muestra si se cumple y la razón concreta. La comparación de comunas
ignora mayúsculas y tildes, pero el presupuesto solo se compara cuando ambas monedas
son iguales; el sistema no inventa una tasa UF/CLP. Las propiedades reservadas o
vendidas no se recomiendan. Desde el resultado se puede marcar directamente una
propiedad como interés del lead.

El ranking se calcula con reglas en `matching.py`, no con IA. El modelo de lenguaje
recibe los tres mejores resultados ya calculados para poder mencionarlos en un
resumen o recomendación, pero no altera el puntaje.

## Priorización de leads

`GET /api/leads` devuelve cada lead con un puntaje calculado y los motivos que lo
componen, ordenados de mayor a menor. El cálculo está en `prioridad.py` y considera
la antigüedad del último contacto, si nunca se contactó, las propiedades de interés,
la etapa del embudo y la prioridad marcada a mano.

El puntaje no se guarda en la base: se recalcula en cada consulta, porque uno
almacenado quedaría desactualizado en cuanto se registra una interacción. Para no
consultar la base una vez por lead, la actividad se obtiene con consultas agrupadas.

## Asistente con IA

Desde la ficha de un lead se pueden pedir cuatro análisis:

- **Resumen de la situación**: describe en qué punto está el prospecto.
- **Siguiente acción recomendada**: propone qué hacer, revisando las tareas
  pendientes para no proponer algo que ya está agendado.
- **Borrador de seguimiento**: prepara un mensaje editable y copiable, sin enviarlo.
- **Preguntas para completar el perfil**: sugiere aclaraciones a partir de datos
  faltantes o requisitos pendientes. La preparación de notas de llamada se ofrece
  por separado en Historial de contacto, a partir de las notas introducidas.

El backend arma un texto con los datos registrados (perfil de búsqueda, oportunidades,
agenda y resultados de visitas, historial de contacto, propiedades de interés,
prioridad calculada y tareas pendientes), lo envía al modelo
y guarda en `analisis_ia` tanto lo que se envió como lo que respondió. Estas cuatro funciones
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

### Evolución hacia WhatsApp y chatbot

La extensión prevista no es un bot que envía mensajes sin control. El diseño
defendible para un CRM es un copiloto: la IA redacta usando el perfil y el historial,
el ejecutivo revisa y aprueba, el sistema registra el envío y deriva la conversación
a una persona cuando detecta intención de visita, negociación, reclamo o una duda
que no pueda respaldar con datos. Una etapa posterior puede integrar WhatsApp
Business con consentimiento, plantillas aprobadas, límites de envío y trazabilidad.

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
python prueba_datos_demo.py
python prueba_oportunidades.py
python prueba_visitas.py
python prueba_matching.py
python prueba_catalogo.py
python prueba_asignaciones.py
```

El orden de los próximos módulos y su criterio de terminado están en
[`ROADMAP.md`](ROADMAP.md).
El avance verificado y los documentos que deben acompañar cada integración están
en [`SEGUIMIENTO_DESARROLLO.md`](SEGUIMIENTO_DESARROLLO.md).

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
- La reasignación de leads no reasigna sus tareas, visitas ni oportunidades.
  La vista de cartera se limita al listado de clientes; no hay gestión de cuentas
  desde la interfaz. Esas ampliaciones del módulo M7 siguen pendientes.
- No hay cambio de contraseña desde la interfaz.
- El registro de actividad y el historial de responsables están paginados. Los demás
  listados traen todo, porque su tamaño lo acota la operación del negocio.
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

Implementado: leads con perfil comercial 360, oportunidades y pipeline, agenda de
visitas, matching explicable, catálogo ampliado de propiedades, interacciones, tareas, propiedades de interés,
autenticación con roles, priorización de leads, asistente con IA (resumen,
recomendación, borrador y preguntas), preparación revisable de notas de llamada,
cartera por responsable, seguimiento del consumo, registro de actividad y vista de inicio.

El catálogo permite registrar código interno, superficies, estacionamientos, bodega,
gastos comunes en CLP, disponibilidad, descripción y características. Admite hasta
20 fotografías por enlaces HTTP/HTTPS y una principal; no sube archivos ni comprueba
que los enlaces externos sigan disponibles. Si una imagen falla se muestra un aviso.
El captador se registra como texto, sin crear usuarios ni asignaciones de cartera.
Solo administración puede consultar y editar los datos del propietario y captador;
los ejecutivos pueden gestionar el resto de la ficha. Solo las propiedades en estado
Disponible aparecen en el matching. Los cambios quedan auditados.

Antes de usar estos campos sobre una base PostgreSQL existente, ejecutar
`python migrar.py` desde `backend`, con la conexión configurada. Las pruebas del
catálogo usan SQLite temporal: no aplican esa migración sobre Supabase.

Pendiente: equipo, automatizaciones, reportería,
comunicaciones, documentos y las mejoras de producción
detalladas en el roadmap.
