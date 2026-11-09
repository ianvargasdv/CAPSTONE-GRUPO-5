# CRM Inmobiliario - Capstone Grupo 5

Sistema de gestión para ejecutivos inmobiliarios: prospectos (leads), catálogo de
propiedades, historial de contacto, tareas de seguimiento y propiedades de interés
de cada lead.

## Estado al 8/11/2026

El sprint 6 se cerró el 8/11, con sus cinco actividades finalizadas y 28 puntos
completados. El término planificado se conserva en el 9/11. SCRUM-41 está finalizada,
con cinco puntos y sin sprint asignado. El código del avance está en el commit `510e439` y
la revisión aceptada de las respuestas de IA en `7ae691a`.

La última comprobación, realizada el 7/11, aprobó 136 pruebas del backend, 53 del
frontend y la compilación. Las pruebas automáticas usan datos temporales y un
proveedor simulado. Las respuestas reales y sus revisiones se guardan por separado
en `backend/evidencias/`.

Hasta iniciar el próximo sprint no se modificará el backend. Quedan la grabación
local y el mantenimiento de las evidencias. Los apartados
fechados conservan las comprobaciones realizadas en cada etapa.

## Lectura de los listados

### Renovación del escenario académico

Desde backend, `python renovar_escenario.py` muestra el alcance; `--aplicar` guarda
los cambios. Usa la fecha local de Santiago y sólo selecciona leads con `es_demo`
y correo del dominio reservado `example.test`. Renueva tareas, próximas acciones,
visitas y cierres de sus negocios; disponibilidad de propiedades `PRUEBA-CRM-*` y
fechas de interacciones identificadas por los textos originales del cargador.
Conserva fotos, usuarios, fechas de ingreso, notas manuales, análisis y consumo de IA
y auditoría histórica. Las actividades siguen siendo simuladas, no gestiones reales.

Antes de guardar crea un respaldo de los campos afectados en `.codex-temp/respaldos/`
(ignorado por Git). Una marca de auditoría impide repetir la renovación el mismo día.
No se ejecuta automáticamente: las tareas podrán volver a vencer con el tiempo.
Las respuestas históricas de IA conservan su fecha y no se regeneran ni se cobran.

### Navegación del catálogo

El catálogo muestra miniaturas de 108 × 80 px: fotografía principal o primera URL
HTTP/HTTPS válida. Pulsar una miniatura abre la imagen a mayor tamaño en otra pestaña.
La ficha conserva su galería. Hay estados Sin foto y Foto no disponible, carga diferida
y ausencia de envío del referente al servidor de imágenes.

El catálogo académico recibió enlaces referenciales de Pexels el 4/11. No son fotos
reales de esos inmuebles; se eligieron por tipo y algunas se reutilizan. Se identifican
mediante el fragmento `#referencial` de la URL y el texto alternativo accesible.
El listado muestra las fotografías sin un rótulo adicional.
La selección y licencia están en `backend/recursos/fotos_catalogo.json`; cada número
corresponde a `https://www.pexels.com/photo/NUMERO/`. Licencia:
https://www.pexels.com/license/ . La base conserva URLs en los campos existentes
`fotografias` y `foto_principal`, sin archivos binarios ni migración nueva. Los enlaces
dependen del proveedor externo; pueden sustituirse por fotografías reales desde Editar.

Para revisar propiedades sin fotos: `python fotos_catalogo.py` desde backend.
`python fotos_catalogo.py --aplicar` verifica los enlaces y completa sólo propiedades
de los tipos incluidos que no tengan galería ni fotografía principal; no reemplaza
fotos existentes. Guarda la actualización y su auditoría en una sola transacción.
Esta carga administrativa registra autor nulo, sin atribuirla a la sesión de una persona.
No se ejecuta automáticamente al iniciar el CRM.

Leads, Propiedades, Tareas, Negocios (vista Tabla) y Visitas (vista Lista) muestran
10 registros por página, con selector de 10, 25 o 50 y controles Anterior/Siguiente.
La búsqueda y los filtros se aplican antes de paginar y reinician la página. La
paginación es local sobre los datos ya recibidos; no reduce la carga de la API.
Actividad solicita páginas de 10 registros al servidor, conservando sus filtros.

En Leads, correo y perfil de búsqueda se despliegan en Datos de contacto y búsqueda.
Negocios comienza en Abiertos; Cerrados y Todos los negocios permiten consultar el
resto sin borrarlo. Los indicadores superiores corresponden al conjunto completo,
no al filtro visible. Las tarjetas muestran lead, propiedad, monto y probabilidad;
Detalles y acciones contiene la fecha, el cambio de etapa, edición y eliminación.
Cada etapa muestra cinco tarjetas inicialmente y permite ver las restantes. El
tablero desplaza sus columnas dentro del panel, con botones para recorrerlas y
la alternativa Tabla. Visitas conserva la agenda semanal y su vista Lista.

En pantallas de hasta 640 px, Menú abre la navegación con nombres completos y las
opciones correspondientes al rol. Negocios utiliza tarjetas verticales paginadas,
con filtros de estado y etapa, búsqueda y acciones desplegables. El resumen muestra
abiertos y concretados; Ver montos despliega los valores por moneda. El botón de
Mobilita se reduce a un icono. La ficha del inmueble abre en un panel lateral con
datos agrupados, dos columnas cuando caben y galería ampliable.

## Ampliación local de Mobilita · posterior al cierre del sprint 6

Esta ampliación fue solicitada después del cierre; no forma parte de los 28 puntos
cerrados ni está publicada. Antes de usarla en la base existente, ejecutar
`backend/venv/Scripts/python.exe backend/migrar.py` desde la raíz y reiniciar la API.
La migración agrega `leads.archivado` y `solicitudes_archivo`, con un índice que evita
solicitudes pendientes repetidas. Bryan informó que las 56 instrucciones se ejecutaron
sin error. La conversación guiada no requiere otra migración; requiere reiniciar la API.

Mobilita puede preparar hasta cinco acciones para un mismo lead: registrar un contacto,
actualizar su estado o perfil comercial, crear o actualizar tareas, asociar una propiedad,
agendar o reprogramar una visita. El servidor resuelve nombres y títulos; si no hay una
coincidencia única solicita una aclaración. Las fechas relativas se interpretan con
la fecha de Santiago enviada al modelo y se muestran como fechas concretas al revisar.
Las visitas exigen hora y zona horaria; se comprueba el cruce de agenda al confirmar.

El chat muestra el conjunto antes de guardar. Se confirma todo en una transacción;
si una acción falla, ninguna se conserva. El navegador no puede sustituir las operaciones
al confirmar. Se revisa de nuevo la cartera y, en actualizaciones, que los datos no hayan
cambiado. Una confirmación repetida no vuelve a aplicar el plan. Cada acción queda auditada.
No hay cambios masivos, envío de mensajes, edición de usuarios, roles, responsables o configuración.

Para pedir borrar un lead, el ejecutivo indica un motivo y confirma una solicitud de
archivo. La sección **Solicitudes** muestra las propias; administración ve el buzón
completo y un aviso de pendientes al entrar (actualizado cada minuto). Sólo administración
puede aprobar o rechazar, indicando su motivo. Aprobar archiva y cierra el lead sin borrar
su historial; sale del listado activo y ya no admite acciones del chat. No cancela
ni elimina automáticamente tareas, negocios o visitas existentes. El borrado definitivo
por la API normal queda reservado a administración, fuera del chat.

La regresión automática usa SQLite temporal y respuestas simuladas. La evaluación
histórica de PostgreSQL que aparece abajo corresponde al flujo anterior de creación
de tareas: no valida por sí sola las nuevas acciones, la migración o el buzón.
La conversación se comprobó además con ocho llamadas reales autorizadas, todas con datos
ficticios y una base temporal. El estimado acumulado fue US$0,00460. La primera tanda
detectó un formato de perfil no admitido; se conservan los dos resultados rechazados y
las dos respuestas posteriores a la corrección en `backend/evidencias/conversacion_mobilita_*20261108.json`.
No se han actualizado Drive ni Jira por esta ampliación.

### Conversación guiada

Mobilita conserva hasta cinco solicitudes y prepara un bloque por vez, con un máximo
de cinco acciones por bloque. Si hay homónimos muestra opciones de la cartera; elegir
no consulta otra vez al proveedor. Las operaciones de ese cliente se confirman juntas.
El resto sigue pendiente. La agenda distingue guardado y descartado; reintentar un paso
no confirma el siguiente. Puedes corregir el bloque actual, omitirlo o descartar lo que
queda sin deshacer lo ya guardado. Las aclaraciones mantienen los datos conocidos.

Puede crear una ficha con nombre y correo, sin propiedad asociada y asignada a quien
confirma. Si falta un dato obligatorio lo pide; no completa requisitos comerciales por
su cuenta. Corregir un nombre conserva el ID, correo e historial de la misma persona.
El chat distingue esa corrección de haber registrado información en otro cliente: no
traslada historiales. Los datos y permisos se validan de nuevo antes de escribir.

La memoria del diálogo y los recibos de cada confirmación quedan en el JSON de
`propuestas_tarea_chat`. No se crea un manual por tarea ni se da acceso SQL al modelo.
El proveedor recibe las solicitudes del usuario y el bloque pendiente, no las listas
completas del CRM; las opciones de clientes se resuelven y muestran desde el servidor.
Las propuestas mantienen su vigencia de 30 minutos. Para probar sin costo:
`python -m unittest prueba_conversacion_mobilita` desde backend y
`node --test src/mobilitaAcciones.test.js` desde frontend.

## Mobilita: asistente del CRM

La concurrencia se comprobó el 4/11 directamente en PostgreSQL de Supabase,
sin Docker. `python verificar_concurrencia_postgres.py --ejecutar` crea un esquema
aleatorio `qa_mobilita_*`, traduce las cinco tablas de prueba hacia ese esquema y
ejecuta dos transacciones desde conexiones independientes. Luego retira únicamente
las tablas y el esquema creados por esa ejecución. Requiere permisos de crear
esquemas; no usa ni limpia las tablas del CRM y no llama al proveedor de IA.
Sin `--ejecutar` no conecta ni modifica datos. No ejecutar Python con optimización
(`-O`), porque las comprobaciones usan assert.

Pasaron cuatro casos: rechazo de resumen general a ejecutivo; propuesta sin guardado
automático; misma propuesta confirmada simultáneamente con una sola tarea y una sola
auditoría de creación; dos propuestas del mismo seguimiento con un guardado y un
rechazo 409. El lead conservó su estado. Evidencia:
`backend/evidencias/mobilita_postgres_20261104_135257.json`.
Es una prueba acotada de integración, no una prueba de carga ni garantía de seguridad
completa. Las evaluaciones anteriores con SQLite conservan sus límites originales.

Las propiedades consultadas se presentan en tarjetas: tres visibles al inicio,
resto desplegable hasta el límite de diez de la consulta y acceso al catálogo completo.
El precio usa separación de miles y conserva CLP/UF; la operación se muestra sólo
si está registrada. Los identificadores internos no se muestran en las tarjetas.
Las respuestas largas se posicionan al comienzo para mantener visible el resumen.

El chat comparte la tipografía Inter y los colores de texto, botones, fondos y bordes
del CRM. El acento azul se limita al personaje y a la actividad del asistente.

La cabecera reúne **Nuevo chat**, ampliar/reducir y minimizar.
El acceso flotante se oculta al abrir el panel y vuelve al minimizarlo o pulsar Escape,
conservando el borrador. El panel ocupa el espacio inferior que deja libre el botón.
Las consultas sugeridas rellenan el mensaje sin enviarlo. **Enter** envía y
**Mayús + Enter** añade una línea.
Si hay texto o una tarea propuesta sin guardar, Nuevo chat pide elegir entre conservar
ese trabajo o descartarlo expresamente. El consumo se consulta desde el panel de
administración; no se muestran costos ni detalles técnicos en el chat. Los resultados
de consultas muestran su fecha. La vista móvil mantiene
la entrada fija y el desplazamiento dentro de la conversación.

Los desplegables del frontend mantienen su funcionamiento nativo y de teclado,
con etiquetas subrayadas y sin triángulos decorativos. En la lista de leads,
la acción de abrir el cliente aparece como **Ver ficha**.

Mientras el proveedor responde, se muestra la solicitud enviada y un indicador de
espera con puntos, actividad en cabecera y avatar. Al terminar o fallar, se retira.
Las entradas de mensajes, sugerencias y propuestas tienen transiciones breves.
No se simula una respuesta por partes ni un porcentaje de avance. Por decisión del
proyecto, las animaciones de Mobilita permanecen activadas, incluso con movimiento
reducido del sistema; no hay selector. Las demás pantallas conservan su comportamiento.
El acceso tiene un personaje animado y un saludo estático, sin consultar al modelo:
«¡Hola! Soy Mobilita. Te ayudo a revisar tu cartera, consultar pendientes y preparar
tareas». Abrir el chat o cerrar el saludo lo oculta durante esa sesión del navegador.

Mobilita responde preguntas sobre las funciones existentes del CRM: leads,
propiedades, negocios, visitas, seguimiento y uso de la IA. Recibe contexto funcional
interno y datos del proyecto enviados por el servidor: es un MVP académico en desarrollo,
Mobilita es el asistente integrado y el modelo se toma de la configuración vigente.
Ese contexto no es un manual publicado; no se envían claves ni credenciales al modelo.
Para datos vigentes puede solicitar las consultas
cerradas descritas a continuación; no dispone de consulta libre de fichas ni datos
reservados. Para otras preguntas orienta a la pantalla correspondiente.

### Consultas de datos reales

Ejemplos: «¿Cuántos leads tengo asignados?», «¿Qué tareas vencidas tiene mi cartera?»
y «¿Qué propiedades están disponibles?». El modelo propone una de cinco herramientas:
`cartera_resumen`, `tareas_pendientes`, `tareas_vencidas`, `propiedades_disponibles`
y `ejecutivos_disponibles`.
`backend/consultas_mobilita.py`, función `ejecutar_consulta()`, comprueba el alcance
y ejecuta consultas predeterminadas con SQLAlchemy. No acepta SQL, tablas, URLs ni
un usuario elegido por el modelo.

Si se rechaza la confirmación de una tarea en Mobilita, el aviso aparece junto al
botón de confirmar, recibe el foco y queda visible dentro del chat. La propuesta
y sus campos se conservan para corregirlos o descartarlos. Un aviso fuera de la
zona visible no debe confundirse con un guardado exitoso.
Los duplicados se identifican por el código de error del backend, sin comparar el
texto del mensaje. Se muestran en ámbar con «Esta tarea ya existe» y «Ver tarea
existente». Antes de abrirla se vuelve a consultar el listado autorizado. La
propuesta se conserva y el botón Confirmar reaparece si se cambia el título o lead.

La cartera propia se obtiene de la sesión. El alcance general requiere administración;
una palabra clave o un rol escrito en el chat no cambian los permisos. Las tareas de
una cartera son las asociadas a sus leads: la tabla de tareas no tiene un responsable
propio. Vencidas excluye hoy, tareas completadas y ausencia de fecha; usa America/Santiago.
La misma restricción se aplica en la API de Tareas: los ejecutivos sólo listan,
crean, editan, completan o eliminan tareas vinculadas a sus leads asignados.
Administración conserva el acceso general, incluidas las tareas sin lead. El
formulario de tareas ofrece al ejecutivo sólo su cartera y exige asociar un lead.
Mobilita filtra sus coincidencias por esa misma cartera y vuelve a comprobarla
al confirmar o reintentar. Reasignar el lead cambia los permisos sobre sus tareas;
no se cambia la sesión ni se crea un responsable adicional en la tabla de tareas.
Los listados devuelven como máximo diez filas y el total. Propiedades disponibles
consulta el catálogo compartido, sin seleccionar propietario ni captador.

Administración también puede preguntar «¿Qué ejecutivos hay?». La consulta
`ejecutivos_disponibles` devuelve hasta diez ejecutivos activos ordenados por nombre,
su cantidad de leads asignados y el total de ejecutivos. Incluye ejecutivos sin
cartera con cero y cuenta todos sus leads, incluidos los cerrados. El identificador
permanece en los datos de la respuesta, sin mostrarse en el texto. Excluye administradores e inactivos y no selecciona
correos ni hashes de contraseña. El backend rechaza la consulta para ejecutivos
con cualquiera de los alcances. No modifica roles ni reasigna leads.

Los resultados se redactan en el backend, se muestran con fecha de consulta y se
conservan en el registro del turno. No se envían al proveedor de IA, tampoco al
continuar el historial. Son resultados del momento de consulta; una respuesta antigua
no se actualiza sola. El chat no incorpora borrados, ni siquiera para administradores.

Esta conexión utiliza funciones internas de la API existente: **no es un servidor MCP**.
La restricción se aplica en la capa del backend; no se ha creado un usuario PostgreSQL
independiente con permisos de sólo lectura. Para conectarlo a otro CRM haría falta
un adaptador y autorización por usuario en ese sistema. MCP es una opción futura para
exponer estas herramientas; no se afirma integración externa ya comprobada.

Pruebas del 4/11: 99 del backend, 44 del frontend y compilación aprobadas. Otro lote
autorizado de cuatro llamadas reales comprobó cartera propia, vencidas, propiedades
y resumen general para admin, con datos ficticios y SQLite temporal: US$0,0008322
estimados. Evidencia: `backend/evidencias/mobilita_consultas_real_20261104_4b7f8aab.json`.
No acredita todos los posibles enunciados ni concurrencia en PostgreSQL. No requiere
otra migración ni modificó Supabase durante la prueba.

Las preguntas ajenas al CRM reciben un rechazo breve. El límite de tema se indica
al modelo y la API sustituye las respuestas clasificadas como ajenas por un texto
fijo. No se afirma que un LLM clasifique correctamente todas las entradas posibles.
El modelo no recibe acceso a internet, SQL ni herramientas para acciones arbitrarias.

La conversación puede retomar hasta seis turnos previos propios, recuperados desde
el servidor con el usuario autenticado. No se acepta un historial enviado por el
navegador. Si un turno vence a los 30 minutos, inicia una **Nueva conversación**.
Una respuesta informativa o aclaración permite seguir escribiendo y no puede
confirmarse como tarea. El historial visible se limita a los últimos 20 mensajes.

Para preparar una tarea, pulsa **Mobilita**, abajo a la derecha, y escribe el nombre del lead y el trabajo
que necesitas registrar. Se abre una ventana de chat disponible desde los listados
del CRM. Puedes minimizarla sin perder el borrador o la propuesta al navegar.
El modelo interpreta la solicitud y
el backend busca las coincidencias. Si hay varios leads, elige la ficha correcta.
Revisa el título y la descripción, elige prioridad y fecha cuando corresponda y
pulsa **Confirmar y crear tarea**. La nueva tarea aparece en la lista.

Escape minimiza el chat y devuelve el foco al botón. La ventana se adapta a móvil.
Se oculta al abrir una ficha,
un formulario lateral o una confirmación para no superponer controles; al cerrar
ese panel recupera la conversación de la sesión actual.

Preparar registra la solicitud y el consumo de IA, sin crear una tarea.
Descartar no modifica el seguimiento. Sólo el autor puede confirmar la propuesta,
que vence a los 30 minutos. Una confirmación repetida devuelve la misma tarea,
incluso si se perdió la respuesta del primer guardado. Una tarea eliminada no se
recrea al reintentar. Crear una tarea por ese formulario no cambia el estado del lead ni envía mensajes. Las acciones compuestas se revisan en su propio resumen de cambios.
Se muestran las tareas pendientes del cliente. Desde el chat no se puede crear
otra pendiente con el mismo título, aunque cambie la descripción; se normalizan
espacios, mayúsculas y tildes. Si es una acción distinta, hay que usar un título
específico. No se afirma detectar equivalencias semánticas entre títulos distintos.

Se incorpora `propuestas_tarea_chat`, relacionada con `usuarios` y, tras confirmar,
con `tareas`. Conserva solicitud, salida original, datos confirmados y consumo.
El modelo no recibe credenciales ni acceso directo a la base de datos. El panel
administrativo suma estas propuestas a los análisis existentes, incluidas las
respuestas inválidas cuyo consumo fue informado.

La migración de `propuestas_tarea_chat` se aplicó y su presencia en Supabase quedó
verificada durante las comprobaciones de noviembre. En otra base existente,
ejecutar `python migrar.py` desde `backend` antes de usar esta versión.
El arranque de la API crea tablas ausentes, pero no agrega columnas a las existentes.

Pruebas sin costo: `python -m unittest prueba_chat_tareas` desde `backend` y
`node --test src/chatTareas.test.js` desde `frontend`. Las pruebas usan un LLM
simulado y SQLite; no acreditan calidad del modelo real ni concurrencia real en
PostgreSQL. Las once situaciones del evaluador anterior no incluyen aún el chat.

El 4/11 se comprobaron cuatro solicitudes con el proveedor real y datos ficticios:
creación confirmada, homónimos, cliente ausente y acción de borrado no admitida.
La revisión técnica fue satisfactoria en esa muestra, con US$0,0003863 estimados.
Las respuestas y comprobaciones están en
`backend/evidencias/chat_tareas_real_20261104_fc515416.json`. La base usada para esas
acciones fue SQLite temporal. Se verificó en modo de sólo lectura que la tabla
migrada existe en Supabase; falta comprobar el recorrido en el CRM habitual.

Después de ampliar el chat el 4/11 se ejecutó otro lote autorizado de cuatro llamadas:
consulta de uso del CRM, clima, intento de ignorar las reglas y aclaración de cliente
para una tarea. Las cuatro comprobaciones de la muestra fueron satisfactorias,
con US$0,000760 estimados. Evidencia:
`backend/evidencias/mobilita_general_real_20261104_52dcc123.json`.
Las acciones se comprobaron en SQLite temporal; no se crearon tareas en Supabase.
La ampliación reutiliza el JSON de propuestas y no requiere otra migración.

## Cartera de clientes

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

## Notas de llamada con IA

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

Comprobación sin costo desde `backend`: `python prueba_llamada.py`. El flujo y los
errores se comprueban con un proveedor simulado y SQLite temporal. Los casos reales
de notas de llamada forman parte de la muestra revisada en SCRUM-41. El 7/11 se
comprobaron también el descarte y el guardado del texto editado en el CRM habitual.
Una nueva ejecución con el proveedor requiere una autorización de gasto nueva.

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
La regresión y sus observaciones se conservan en
`backend/evidencias/evaluacion_regresion_disponibilidad_20261029.json` y
`backend/evidencias/revision_asistida_regresion_20261029.json`. Entre ambos lotes se hicieron trece llamadas autorizadas
por US$0,0017140 estimados.

### Revisión aceptada · 7/11/2026

Bryan aceptó el balance de la revisión asistida: diez respuestas originales
aprobadas y una rechazada; las dos respuestas posteriores a la corrección quedaron
aprobadas. Se conserva el fallo original y sólo se repitieron esos dos casos.
La aceptación no fue una evaluación independiente ni demuestra precisión general.

Las decisiones, observaciones, autor y fecha están en
`backend/evidencias/evaluacion_real_revisada_20261107.json` y
`backend/evidencias/evaluacion_regresion_revisada_20261107.json`. El balance y la
aceptación se conservan en `revision_muestra_20261107.md` y
`aceptacion_revision_asistida_20261107.json`, dentro de la misma carpeta.
Los originales permanecen intactos. SCRUM-41 está finalizada y fuera del sprint 6.

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

### Ejecución local y demostración

La interfaz y el backend se ejecutan localmente. La base de datos continúa
alojada en Supabase y las funciones de IA consultan al proveedor configurado.
Por tanto, la demostración local requiere conexión a esos servicios.

Para la presentación se grabará el recorrido desde el entorno local con datos
ficticios. No se deben mostrar archivos de configuración ni claves durante la grabación.

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

Este esquema describe el código local. `archivado` y `solicitudes_archivo`
requieren la migración de la ampliación de Mobilita. Su ejecución fue informada
por Bryan (56/56 instrucciones); no corresponde a una inspección nueva de Supabase.

```
usuarios       id, nombre, email (único), password_hash, rol, activo, fecha_creacion
leads          id, nombre, email, telefono, estado, prioridad, ejecutivo_id,
               tipo_operacion, presupuesto_min, presupuesto_max, moneda,
               comunas_interes, tipo_propiedad_buscada, dormitorios_min,
               banos_min, plazo_decision, financiamiento, origen,
               proxima_accion, fecha_proxima_accion, es_demo, archivado, fecha_creacion
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
propuestas_tarea_chat
               id, usuario_id, solicitud, salida_original, propuesta, estado,
               tarea_id, confirmacion, modelo, tokens_entrada, tokens_salida,
               costo_estimado_usd, fecha_creacion
solicitudes_archivo
               id, lead_id, lead_nombre, autor_id, autor_nombre, motivo, estado,
               resolucion, resuelto_por_id, resuelto_por_nombre,
               fecha_creacion, fecha_resolucion
auditoria      id, usuario_id, usuario_email, accion, entidad, entidad_id,
               descripcion, detalle, fecha_creacion
```

Sobre las relaciones:

- Archivar no borra relaciones. La solicitud conserva nombre y autor, su motivo y
  la decisión administrativa. Sólo puede existir una solicitud pendiente por lead.
- Las acciones compuestas conservan su plan en `propuestas_tarea_chat`; se confirman
  en conjunto y cada registro modificado se audita. El vínculo `tarea_id` corresponde
  al flujo de creación de una sola tarea.

- Las propuestas de tareas pertenecen a un usuario. Tras confirmar, se vinculan
  con la tarea creada. Al eliminar esa tarea se conserva la propuesta y su vínculo
  queda nulo; confirmar de nuevo no la vuelve a crear.

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

**Mobilita · histórico registrado** separa el consumo del chat: solicitudes,
costos estimados guardados, tokens y primera/última fecha de registro. Incluye
propuestas canceladas y respuestas inválidas conservadas en propuestas_tarea_chat.
Los costos desconocidos se cuentan aparte; el gasto queda sin informar cuando no
hay ningún costo registrado. Cambiar precios no recalcula las cifras anteriores.
Confirmar una propuesta varias veces no duplica el gasto.

El histórico no distingue claves anteriores ni recupera usos externos, registros
eliminados o pruebas realizadas en otras bases. No requiere migración adicional.
El presupuesto configurado no es el saldo ni el límite real de OpenAI. Por solicitud
del usuario se retiraron del panel el párrafo explicativo y el enlace al consumo
oficial. No hay sincronización administrativa con OpenAI. Esa integración requiere
una credencial administrativa separada y definir
el proyecto o identificador de clave que debe consultarse; no se usa la clave de
generación para atribuir cargos oficiales.

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
- Los orígenes permitidos del navegador incluyen `localhost:3000` y
  `127.0.0.1:3000`. Las direcciones adicionales se configuran en `CORS_ORIGINS`;
  no se admiten comodines ni URLs con rutas o credenciales.
- La reasignación de leads no reasigna sus tareas, visitas ni oportunidades.
  Mi cartera organiza el listado de clientes y Tareas restringe el acceso del
  ejecutivo a los leads que tiene asignados. Quedan por extender las vistas de
  cartera de visitas y oportunidades y la gestión de cuentas desde la interfaz.
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
cartera por responsable, Mobilita para consultas y tareas con confirmación,
seguimiento del consumo, registro de actividad y vista de inicio.

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

Posibles ampliaciones: gestión de cuentas desde la interfaz, vistas de cartera
para visitas y oportunidades, automatizaciones, reportería, comunicaciones y
documentos comerciales. Se describen en el roadmap como propuestas para planificar,
no como compromisos del sprint actual.
