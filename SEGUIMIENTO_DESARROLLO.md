# Seguimiento del desarrollo

Actualizado: 8/11/2026. Control de avances y comprobaciones del proyecto.

## Revisión documental · 8/11/2026

Se actualizaron README y Roadmap con las finalizaciones del 7/11 y los commits
510e439 y 7ae691a. Se corrigieron referencias a migración y evaluación pendientes,
se distinguieron las propuestas futuras y se aclaró la secuencia de aceptación
de SCRUM-41. La revisión de Drive del 7/11 confirmó los ajustes de estados y
resúmenes; el cambio de colores del User Story Mapping queda a cargo del compañero.

El sprint 6 sigue activo hasta su término previsto del 9/11. El backend se mantiene
sin cambios hasta el próximo sprint. Esta revisión sólo modifica documentación
y se versiona junto con README, Roadmap y el balance de respuestas.

## Restricción de cambios y revisión documental · 7/11/2026

Bryan indicó que no se pueden realizar más cambios en el backend hasta iniciar
el próximo sprint. Durante este intervalo se mantiene el código del backend,
sin nuevas funciones, migraciones ni renovaciones de datos. Corresponde mantener
las evidencias y documentos, preparar la grabación local cuando Bryan lo decida
y registrar el cierre del sprint 6. El siguiente sprint aún no está planificado.

La revisión de Jira confirmó las cinco actividades del sprint 6 Finalizadas,
con 28 puntos y el sprint activo hasta su término previsto del 9/11. SCRUM-41
también está Finalizado, con cinco puntos y sin sprint asignado. Las épicas
SCRUM-18 y SCRUM-38 se finalizaron al comprobar que todos sus hijos están
Finalizados. Esta actualización no cierra el sprint ni declara terminado todo
el proyecto. La revisión inicial encontró textos y resúmenes desactualizados en
Drive. Se corrigieron y su guardado se comprobó posteriormente, salvo el cambio
de colores del User Story Mapping que realizará el compañero.

## Finalización de actividades y revisión de respuestas · 7/11/2026

El código del avance quedó en main y GitHub mediante el commit 510e439. En la
comprobación final aprobaron 136 pruebas del backend, 53 del frontend y la
compilación. El evaluador se ejecutó en proceso separado. No hubo llamadas pagadas.
SCRUM-39, 40, 43, 44 y 45 quedaron Finalizadas en Jira, conservando 28 puntos.
El sprint 6 permanece activo; su término previsto es el 9/11.

Se revisaron también las once respuestas reales originales y las dos posteriores
a SCRUM-42. Bryan aceptó el balance mostrado: diez originales aprobadas y una
rechazada; las dos respuestas repetidas quedaron aprobadas. La aceptación se basa
en revisión asistida, no en una evaluación humana independiente. Se preservaron
los originales y se comprobaron sus huellas. Las copias revisadas conservan
decisión, observación, autor y fecha por caso en backend/evidencias/.

SCRUM-41 quedó Finalizado con cinco puntos, sin sprint asignado. No suma puntos
al sprint 6. No se generaron nuevas respuestas ni se modificó Supabase. Las nuevas
evidencias se versionan junto con esta actualización documental. Los registros
anteriores conservan el estado que tenían en cada fecha.

## Historial de comprobaciones

Los apartados siguientes conservan el estado al realizar cada prueba. Las
finalizaciones y publicaciones posteriores figuran en el resumen anterior;
un pendiente histórico no significa que siga abierto.

### Ajuste móvil de Negocios y navegación · 7/11/2026

Bryan confirmó la revisión del ajuste móvil en su sesión. Se registró en SCRUM-44
como confirmación informada, sin una captura nueva del recorrido.

La revisión de Bryan a 390 px mostró poco espacio por la barra lateral, los cuatro
indicadores apilados y el tablero horizontal. Se incorporó Menú con el Drawer
existente a 640 px o menos, conservando las opciones según el rol. Negocios muestra
dos contadores, montos desplegables y una lista vertical con búsqueda, filtros por
estado y etapa, paginación y las mismas acciones. Mobilita usa un botón compacto.
La ficha del inmueble aprovecha dos columnas a 390 px y una a 360 px o menos.

Pasaron 53 pruebas existentes y la compilación. En navegador, con los componentes
reales y datos ficticios aislados, se comprobaron anchos de 320 y 390 px sin
desbordamiento de página; búsqueda vacía, filtros de etapa y estado, cambio de
etapa, apertura del formulario, paginación 10/25, montos, menú por rol, ficha del
inmueble y apertura/minimización de Mobilita. A 1366 px se comprobó el regreso al
tablero y Tabla, y el cierre del menú al ampliar. No se usaron Supabase ni la IA.
La comprobación con datos aislados y la confirmación del usuario se registran
por separado.

Los archivos auxiliares del frontend y el servidor temporal de prueba se retiraron.
La captura de referencia está en .codex-temp/movil-qa-20261107/Negocios_390.png,
ignorada por Git. Cambio de presentación de SCRUM-44, que continúa En revisión.
Código local, pendiente de commit y push.

## Reprogramación de pendientes ficticios · 7/11/2026

Bryan confirmó con capturas que la ficha de Valentina muestra la visita Programada
para el 9/11 a las 13:00, el próximo seguimiento del 11/11 y las dos llamadas
conservadas. Se añadió esta comprobación visual a SCRUM-45.

Bryan autorizó reprogramar tareas y visitas vencidas del escenario. Se seleccionaron
sólo registros de leads con es_demo y correo example.test. Se guardó el respaldo
.codex-temp/respaldos/fechas_antes_20261107_113742_187813.json y se actualizaron ocho
tareas al 9–13/11, seis visitas al 9/11 y ocho fechas de próxima acción vinculadas
por título y fecha a esas tareas. Se comprobaron cruces de agenda por ejecutivo.
Cada cambio se auditó dentro de la misma transacción.

La lectura posterior confirmó las fechas, cero tareas pendientes vencidas y cero
visitas pendientes anteriores al inicio del 7/11 en el escenario seleccionado.
Las visitas actualizadas pasaron el esquema del backend. El corte diario no prueba
que todas las horas del propio 7/11 sigan siendo futuras. No se modificaron títulos,
estados ni llamadas. Se registró en SCRUM-45, que sigue En revisión. Sin llamadas de IA.

## Ficha del inmueble y datos del departamento 803A · 7/11/2026

Bryan confirmó la paginación de Negocios en Todos y Tabla: Siguiente cambia
los registros con 10 por página y elegir 25 muestra los 23 negocios en una página.
Se registró en SCRUM-44. La presentación en pantalla estrecha sigue pendiente.

En Negocios, la captura de Bryan muestra 19 abiertos de 23. Después confirmó
cuatro cerrados, 23 al seleccionar Todos y registros visibles en Tabla. Se
registró el resultado en SCRUM-44, manteniendo En revisión. Queda comprobar
la paginación de Tabla y el tablero en una pantalla estrecha.

Bryan comprobó en Actividad la apertura del detalle en una ventana centrada,
su cierre y el paso a la segunda página de registros. Se registró el recorrido
en SCRUM-44, que sigue En revisión. La captura no verifica textos de gran longitud
ni la presentación móvil.

Se registraron en Jira la corrección del panel en SCRUM-44 y la carga adicional
de datos ficticios en SCRUM-45, con sus comprobaciones y pendientes. Se verificó
la descripción guardada y ambas actividades continúan En revisión.

Después, Bryan solicitó completar todas las fichas existentes. Se rellenaron 102
campos vacíos en las 25 propiedades, incluidos los datos administrativos. Se
conservaron los valores existentes. Cada actualización quedó registrada en
Actividad como carga de datos ficticios. Los correos generados usan example.test.
La lectura posterior confirmó las 25 fichas válidas según el esquema de respuesta
y ningún vacío en los 18 campos comerciales, técnicos y administrativos revisados.

La ficha del catálogo abre un panel lateral con información comercial, datos técnicos,
descripción, características y galería. Las fotografías de la galería se pueden ampliar.
Pasaron 53 pruebas del frontend y la compilación. La comprobación visual quedó pendiente
por un bloqueo del control del navegador.

Por solicitud de Bryan se completaron 15 campos de la propiedad 1 con datos ficticios
de demostración. Se configuró arriendo por 620.000 CLP, dos dormitorios, dos baños,
55 m² útiles, 60 m² totales, estacionamiento, bodega y gastos comunes de 85.000 CLP.
Se verificó la lectura posterior en Supabase y la validación del esquema de respuesta.
La procedencia ficticia y los valores anteriores quedaron registrados en Actividad,
dentro de la misma transacción. Estos datos no proceden de un aviso inmobiliario real.

## Validación del filtro de cartera · 6/11/2026

El 7/11 Bryan confirmó con su cuenta ejecutiva que buscar Valentina muestra su
ficha, un término sin coincidencias devuelve cero resultados y limpiar recupera
la ficha. Se registró en SCRUM-40, manteniendo En revisión.

- SCRUM-40. Validación manual del 6/11/2026. Con la sesión de ejecutivo, Mi cartera mostró únicamente el lead asignado (1 de 1). Con la sesión de administrador, filtrar por ese mismo ejecutivo mostró el mismo lead (1 de 1). Ambas vistas mostraron dos tareas asociadas.

## Validación de notas de llamada · 6/11/2026

El 7/11 Bryan preparó otra propuesta, reemplazó su texto y confirmó la llamada.
La captura posterior muestra dos contactos, la llamada anterior conservada y una
nueva llamada del 7/11 a las 11:34 con el texto editado exacto. Se registró en
SCRUM-39. Con este recorrido queda comprobado manualmente el guardado del texto
revisado. La historia permanece En revisión hasta la aceptación final del sprint.

El 7/11 Bryan preparó y descartó una propuesta con datos ficticios, tras autorizar
una generación. Las capturas anterior y posterior conservan un contacto y la misma
llamada del 6/11. Se registró en SCRUM-39. No se verificó el costo con estas capturas.
El guardado del texto editado se comprobó después, como se registra arriba.

Bryan probó las notas con IA en un lead de prueba. Seguimiento mostró una sola
llamada, con los tres dormitorios, dos estacionamientos y la acción acordada de
revisar propiedades compatibles. Se registró el resultado en SCRUM-39.

## Validación del flujo de duplicados · 6/11/2026

En su sesión de ejecutivo, Bryan intentó confirmar una tarea pendiente con el
mismo título. Mobilita mostró «Esta tarea ya existe» y abrió la tarea correcta
desde «Ver tarea existente». La captura confirma el título y el estado Pendiente.
Una consulta de sólo lectura en Supabase confirmó dos tareas visibles para su
cuenta y una sola coincidencia con el título probado. Se registró el caso en
SCRUM-43, que continúa En revisión.

## Aviso visible al rechazar una confirmación en Mobilita · 5/11/2026

El flujo final de duplicados usa ámbar, «Esta tarea ya existe», el nombre del lead
y «Ver tarea existente». El backend responde 409 con código tarea_duplicada y los
identificadores de tarea y lead ya autorizados; el frontend no deduce el tipo de
error a partir de su texto. App vuelve a cargar las tareas permitidas antes de abrir
el formulario de edición. Si cambió el acceso o no existe la tarea, muestra el error.
No hay guardado automático al abrir. Confirmar queda oculto durante el duplicado y
reaparece al cambiar el título o el lead; los demás campos se conservan.

Pasaron 68 pruebas del backend (chat y permisos), 53 del frontend y compilación.
Se probó en navegador con API simulada el aviso visible, el botón y la apertura de
la tarea ficticia indicada por el rechazo. La integración de la apertura en la
sesión habitual queda pendiente de comprobación por Bryan. Sin Supabase ni IA real
en esta prueba. Auxiliares del frontend retirados y servidores de prueba detenidos.

Bryan detectó que pulsar Confirmar en una propuesta duplicada no mostraba un aviso
en la parte visible del chat. El error se renderizaba antes de toda la propuesta,
fuera de la zona visible al estar junto al botón. Se movió el aviso al formulario,
antes de Confirmar, con role alert, foco y desplazamiento dentro del chat.
Los errores sin propuesta conservan su ubicación general y reciben el mismo foco.

Por petición posterior de Bryan se acortó el rechazo de duplicados a «Esta tarea ya
existe para este lead. Revisa la tarea pendiente.». El aviso junto al botón añade
un icono, título «No se pudo confirmar», separación y borde visible con foco. Se
comprobó otra vez en navegador con 409 simulado que el texto completo queda visible
y enfocado. Pasaron la regresión de duplicados y la compilación tras este ajuste.

En navegador se comprobó con un cliente ficticio y una API local simulada que
responde 409: aviso completo visible, foco en el mensaje, un solo aviso tras dos
intentos y título y descripción conservados. No se usaron Supabase ni el proveedor.
Se retiraron los dos archivos temporales del frontend y se detuvieron los servidores
de prueba. El auxiliar restante está en .codex-temp, ignorado por Git.

Pasaron las 58 pruebas del chat, incluida una regresión de 409 con detalle y propuesta
pendiente conservada al reintentar, 52 pruebas del frontend y compilación. No se
modificó la regla de duplicados. Falta el reintento de Bryan en su sesión habitual.
Se registra en SCRUM-43 como corrección de presentación del rechazo, sin cerrar
la historia. Cambios locales, sin commit, push ni llamadas pagadas.

## Tareas limitadas a la cartera del ejecutivo · 4/11/2026

Durante la aceptación funcional, la cuenta ejecutiva veía 27 tareas aunque tenía
un solo lead. listar_tareas() devolvía el listado general, mientras las consultas
de Mobilita sí filtraban la cartera. Se corrigieron listado, creación, edición,
finalización y eliminación en main.py y tareas_servicio.py. Administración conserva
el acceso general y las tareas sin lead; el ejecutivo debe asociar un lead propio.
Las operaciones no autorizadas se rechazan antes de modificar o auditar una tarea.

Mobilita filtra candidatos por la cartera y vuelve a comprobar la asignación al
confirmar, también en reintentos de una propuesta ya confirmada. Los bloqueos del
lead y de la tarea conservan la comprobación durante la escritura. El formulario
sólo ofrece leads propios al ejecutivo. No cambia el acceso de los demás módulos.
La prueba de concurrencia aislada se adaptó para asignar su lead ficticio al usuario;
esa comprobación PostgreSQL no se repitió en esta sesión.

Pasaron 102 pruebas del backend (10 nuevas de permisos), 52 del frontend, compilación
y las 62 verificaciones de auditoría. Todo con SQLite temporal y proveedor simulado.
Después se repitieron las diez regresiones tras el ajuste de bloqueos. Una lectura
de Supabase con la nueva función confirmó dos tareas visibles para la cuenta
ejecutiva, un lead asignado y las 27 tareas generales conservadas. No se modificaron
datos comerciales, no hubo llamadas pagadas ni migraciones. Falta la comprobación
visual del usuario tras recargar. Cambio local, sin commit ni push. Se registra
como corrección del alcance de permisos de SCRUM-43, manteniendo En revisión.

## Consulta administrativa de ejecutivos en Mobilita · 4/11/2026

Tras la prueba manual, el texto del directorio se ajustó para mostrar el nombre
y el número de leads asignados, en lugar del identificador «Usuario». El identificador
permanece sólo en los datos estructurados. Se conservan ejecutivos con cero leads;
el conteo incluye todos los estados y cambia con la asignación vigente. Se añadieron
dos regresiones para contar leads sin multiplicarlos por sus tareas, conservar ceros
y comprobar la reasignación. Esta ampliación no modifica usuarios ni asignaciones.

Bryan pidió consultar los ejecutivos desde el chat como administrador. Se añadió
ejecutivos_disponibles en consultas_mobilita.py, con comprobación del rol de sesión
antes de consultar usuarios, tanto para alcance mia como general. Selecciona sólo
id y nombre de ejecutivos activos, excluye administradores e inactivos y devuelve
hasta diez ordenados por nombre e identificador, además del total. No reasigna leads,
modifica roles ni muestra correos, hashes o credenciales. No requiere migración.

Se actualizaron el contexto funcional y las instrucciones del modelo. Pasaron las
55 pruebas del chat, incluidos cinco casos nuevos y la ampliación del rechazo de
SQL. Cubren permisos aunque el LLM proponga la herramienta, suplantación en el mensaje,
lista vacía, límite, homónimos y exclusión de resultados del historial enviado al
proveedor. SQLite temporal y modelo simulado; no hubo llamadas pagadas ni cambios
en los datos comerciales de Supabase. Falta probar la selección de la herramienta
con el modelo real desde la cuenta administradora. Se añadió el alcance y los
resultados a SCRUM-43, manteniendo En revisión y 8 puntos. Cambios locales, sin commit
ni push. La actualización de la evidencia de criterios en Drive queda pendiente
cuando se confirme el flujo; no se editaron los informes 2.4 y 2.6.

## Registro de las últimas mejoras en Jira · 4/11/2026

Después de actualizar la Daily se registraron los cambios en Jira. SCRUM-43 conserva
8 puntos y En revisión; se añadieron los resultados de PostgreSQL de Supabase y los
ajustes de contexto del asistente. Se actualizó la épica SCRUM-38 manteniendo la
planificación original y distinguiendo el alcance añadido durante el sprint.

Se crearon y comprobaron:
- SCRUM-44, Historia: Organizar los listados y facilitar la revisión del catálogo,
  5 puntos. Incluye paginación, tablero y fotografías.
- SCRUM-45, Tarea: Renovar el escenario de demostración con seguimientos vigentes,
  2 puntos. Incluye respaldo, renovación y comprobaciones.

Ambas asignadas a Bryan, informador Bryan, épica SCRUM-38, sprint 6, inicio 4/11
y vencimiento 6/11. Se pasaron a En revisión, no a Finalizado. Los 5 y 2 puntos
son estimaciones de seguimiento registradas después de implementar el trabajo;
no se presentan como estimaciones iniciales ni como horas. No se alteraron fechas
de creación ni sprints cerrados.

Verificación actual: 38 historias y tareas, 32 Finalizado, 6 En revisión, 207 puntos.
Sprint 6 activo del 2 al 9/11: SCRUM-39 (8), SCRUM-40 (5), SCRUM-43 (8), SCRUM-44 (5)
y SCRUM-45 (2), total 28 puntos, todos En revisión. Se conserva la línea base de 13;
SCRUM-43 añadió 8 el 2/11 y SCRUM-44/45 añadieron 7 el 4/11.

Pendiente trasladar estas referencias al Product Backlog, Sprint Backlog, Planning,
Scrumboard y Burndown; renovar las exportaciones de historias y épicas. La Daily del
4/11 puede referir SCRUM-43, SCRUM-44 y SCRUM-45. No se editaron archivos de Drive,
informes 2.4/2.6, ni se hizo commit, push o cierre del sprint.

## Verificación en PostgreSQL de Supabase · 4/11/2026

Por indicación de Bryan se utilizó PostgreSQL en Supabase sin Docker. Se verificó
permiso para un esquema aislado y aislamiento READ COMMITTED. El comprobador creó
un esquema qa_mobilita con identificador aleatorio y cinco tablas aisladas, sin
importar main ni ejecutar migraciones del CRM. SQLAlchemy tradujo todas las tablas
del ejercicio a ese esquema. Se usaron usuarios y leads ficticios, sin LLM.

Pasaron cuatro casos: ejecutivo sin acceso a resumen general; preparar propuesta
sin guardar una tarea; dos confirmaciones simultáneas de la misma propuesta con un
único registro y una única auditoría de creación; dos propuestas distintas del mismo
seguimiento con resultados 200 y 409, sin duplicar. Se sincronizaron dos conexiones
PostgreSQL independientes antes de adquirir el bloqueo. El estado del lead no cambió.
El esquema y sus tablas se retiraron al terminar y se comprobó su ausencia.

Evidencia: backend/evidencias/mobilita_postgres_20261104_135257.json.
Comprobador: backend/verificar_concurrencia_postgres.py, ejecución explícita con
--ejecutar; no ejecutarlo con -O. No se tocaron tablas comerciales del CRM, no hubo
consumo de IA, Docker, commit ni push. La prueba no acredita carga masiva ni todas
las variantes de entrada. SCRUM-43 conserva la revisión funcional pendiente; no se
cambió su estado en Jira.

Esta comprobación resuelve el pendiente de concurrencia señalado más abajo en la
verificación parcial. Docker no es un requisito ni un impedimento del proyecto.
En la Daily del 4/11 se puede añadir la comprobación PostgreSQL y reemplazar ese
pendiente por la actualización de Jira y evidencias. Si se registró Docker como
impedimento, aclarar que se resolvió usando Supabase; no inventar que se inició Docker.

## Verificación final parcial de Mobilita · 4/11/2026

Se repitieron las 77 pruebas del chat y del asistente con SQLite temporal y modelo
simulado; todas pasaron. Cubren restricciones de ejecutivo, confirmación explícita,
reintento sin duplicación, propuestas ajenas y separación entre datos e instrucciones.
No son una nueva evaluación del modelo real. La concurrencia en PostgreSQL sigue
pendiente: Docker está instalado, pero su motor local no está en ejecución. No se
intentó esa prueba sobre la base compartida ni se modificó Supabase durante esta
verificación. No se marcaron historias finalizadas ni se hizo commit o push.

## Renovación del escenario académico · 4/11/2026

Bryan solicitó renovar los datos envejecidos y diversificar las tareas para la
demostración. La auditoría inicial encontró 26 tareas pendientes vencidas y numerosos
títulos repetidos. Se preparó renovar_escenario.py, con vista previa, respaldo previo,
una transacción y bloqueo de reejecución durante el mismo día. No borra registros.

Se aplicó en Supabase a los 29 leads identificados con flag de prueba y correo
example.test: 26 tareas, 11 visitas, 23 negocios, fechas de disponibilidad de 18
propiedades del cargador y fechas de 23 contactos reconocidos como simulados.
Las fechas de ingreso originales se conservaron para mantener coherencia con la
auditoría y los análisis previos. No se cambiaron notas de contactos manuales,
usuarios, fotografías, historial de asignaciones, auditoría previa ni consumo de IA.

Verificación posterior por consultas de sólo lectura: 26 títulos distintos;
13 tareas Pendiente, 9 En Progreso y 4 Completada; cero pendientes vencidas y tres
para hoy. Fechas entre 3 y 13 de noviembre (el 3 corresponde a tareas completadas).
Nueve visitas futuras y ninguna Programada/Confirmada en pasado. Se conservaron
las 25 fotos principales. Una segunda ejecución respondió ya_aplicado sin cambios.
Pasaron ocho pruebas de renovación y cargador con SQLite temporal; cubren conservación
de registros no ficticios, respaldo, variedad, fechas, visitas y repetición segura.

Respaldo local ignorado por Git: .codex-temp/respaldos/escenario_antes_20261104_072612_786438.json.
No contiene claves ni usuarios; conserva los campos comerciales afectados para recuperar
la versión anterior. No se hicieron llamadas pagadas ni se generaron nuevas respuestas
de IA. Los análisis antiguos siguen siendo históricos; no se presentan como actualizados.
No hay cambios de esquema ni necesidad de renovar el modelo relacional.

Pendiente de gestión: incorporar la preparación de datos al alcance de demostración
del sprint 6 y a la Daily del 4/11, con evidencia de las cifras anteriores. No registrar
como desarrollo de funciones nuevas ni cambiar sprints ya cerrados. No se modificaron
Jira, Drive ni los informes 2.4/2.6. Código local, sin commit ni push.

## Fotografías del catálogo · 4/11/2026

Por solicitud de Bryan se añadieron miniaturas de 108 × 80 px al catálogo, con acceso
a la imagen de mayor tamaño, galería existente y respaldo para imagen ausente o rota.
Se consultó el catálogo real en modo de lectura: las 25 propiedades no tenían fotos.
Después de verificar 14 imágenes de Pexels se guardaron enlaces en las 25 propiedades,
seleccionando según Casa o Departamento y reutilizando algunas. No se afirma que
correspondan a sus direcciones, distribución o equipamiento reales. Se etiquetan
como imágenes de muestra mediante la marca `#referencial` en los enlaces guardados
y el texto alternativo. Por solicitud posterior de Bryan se retiraron los rótulos
visibles de las miniaturas y la galería. La licencia permite
uso en aplicaciones: https://www.pexels.com/license/ .

La carga modificó Supabase: fotografias, foto_principal y un registro de auditoría
por propiedad, sin cambiar el modelo ni agregar columnas. Los enlaces de las dos
columnas suman 5664 bytes; esta cifra no incluye auditoría ni sobrecarga de PostgreSQL.
La auditoría identifica una carga referencial sin atribuir usuario humano. La utilidad
fotos_catalogo.py no reemplaza fotos existentes y, por defecto, sólo informa candidatas.
Una consulta posterior confirmó 25 principales guardadas y cero propiedades pendientes.

Pasaron 52 pruebas del frontend, dos pruebas de carga con SQLite temporal y compilación.
Se verificó en navegador la carga de diez miniaturas iniciales, estados sin imagen y
enlace roto y ausencia de desbordamiento de página a 390 px. Los casos negativos se
añadieron sólo al entorno visual temporal, sin insertarlos en Supabase. Se eliminaron
esos auxiliares y se detuvo el servidor de revisión. Sin commit, push ni llamadas de IA.

Añadir este alcance al seguimiento de organización del catálogo del 4/11: Daily,
actividad de Jira pendiente de registro y evidencias del sprint 6. No marcar una
aceptación del usuario ni inventar estimaciones acordadas. La estructura de la base
permanece igual, por lo que no requiere rehacer el diagrama relacional.

## Organización de listados · 4/11/2026

Bryan solicitó reducir la saturación de Leads, Negocios, Visitas, Propiedades,
Tareas y Actividad y resolver el recorte del tablero. Se incorporaron páginas de
10 registros (selector 10/25/50) en los listados; Actividad usa 10 por petición.
Leads despliega sus datos secundarios. Negocios separa abiertos/cerrados/todos,
limita inicialmente a cinco tarjetas por etapa y agrupa detalles y acciones.
Se acotó el ancho del tablero y se añadieron botones para recorrer sus columnas.
No se cambiaron permisos, registros, estructura de Supabase ni funciones del backend.

Referencias consultadas: soporte de Inmovilla, Búsquedas y filtros
(https://inmovilla.freshdesk.com/support/solutions/folders/103000130135), y HubSpot,
Customize the board view for objects with pipelines
(https://knowledge.hubspot.com/object-settings/select-properties-to-show-on-records-in-board-view).
Se adaptaron patrones de filtrado y reducción de información visible; no se copiaron
plantillas ni se afirma una evaluación con ejecutivos reales.

Verificación: 49 pruebas del frontend y compilación aprobadas. En navegador se
usaron 23 registros ficticios para revisar paginación de Leads, Tareas, Propiedades,
Visitas en Lista y Negocios en Tabla; reinicio al buscar un lead, apertura de datos
secundarios, expansión de tarjetas y acceso a sus acciones. A 390 px se comprobó
que la página no desborda horizontalmente y que los botones desplazan el tablero.
Actividad se revisó en código, sin una comprobación visual nueva de su API real.
La paginación local no sustituye paginación de servidor para grandes volúmenes.

Seguimiento pendiente (sin modificar los informes 2.4 y 2.6 entregados):
- Jira: registrar esta mejora de interfaz como alcance añadido el 4/11 al sprint 6
  (2–9/11), separada de SCRUM-43. Propuesta de estimación: 5 puntos Fibonacci,
  por las seis vistas, navegación y revisión adaptable; pendiente de acuerdo del
  equipo, no representa horas ni una estimación original del sprint. Estado de
  revisión hasta comprobar el CRM habitual; no marcar aceptación por el usuario.
- Daily: Bryan, 4/11, reorganización de listados y pruebas. Siguiente: validación
  habitual y actualización de evidencias; no inventar un bloqueo actual.
- Impedimentos: registrar el recorte del tablero como incidencia corregida si
  corresponde a ese registro, sin inventar fechas anteriores ni indisponibilidad.
- Product Backlog, Sprint Backlog, Planning y Scrumboard: añadir el alcance y su
  identificador cuando exista; conservar la incorporación del 4/11.
- Burndown: registrar el aumento de alcance cuando se acuerde la estimación; no
  alterar los puntos iniciales ni inventar cierres diarios. Review, retrospectiva
  y Release: incorporar resultados y aprendizajes después de la aceptación.
- Gantt y mapas: revisar sólo si cambian hitos o recorrido; la organización visual
  no requiere un nuevo modelo de datos. Renovar exportaciones de Jira si se añade
  la actividad. Drive no se auditó ni se modificó durante este ajuste.

Cambios locales, sin commit, push, despliegue ni llamadas pagadas. Se eliminaron
los archivos auxiliares utilizados para la revisión visual.

## Contexto del proyecto y del asistente · 4/11/2026

Se corrigió la falta de información que llevaba a Mobilita a confundir el CRM con
el asistente y a desconocer que el proyecto es un MVP. El servidor ahora aporta
la etapa del proyecto, el alcance del asistente y el nombre del modelo configurado,
sin enviar claves ni direcciones del proveedor. Las instrucciones aclaran que el
contexto funcional es interno, no un manual publicado, y que los datos del servidor
prevalecen sobre respuestas anteriores incorrectas.
Se ajustó también el tono: se indica «Uso el modelo» al identificar el modelo y
se evitan referencias femeninas al asistente.

Pasaron 77 pruebas del chat y del asistente con SQLite temporal y proveedor simulado.
Incluyen configuración cambiante o ausente, exclusión de credenciales y rechazo de
metadatos aportados desde el navegador. Esto verifica el contexto y los controles;
queda comprobar la redacción con el proveedor real. Sin llamadas pagadas ni cambios
de estructura en Supabase. Cambios locales, sin commit ni push.

## Limpieza de controles del frontend · 4/11/2026

Se retiraron Detalles de la última respuesta y los costos de la ventana de Mobilita,
conservando el registro de consumo y el panel administrativo. El pie mantiene la
revisión de propuestas y Mayús+Enter. Se eliminaron las flechas decorativas del chat
y el icono de abrir ficha de leads se reemplazó por texto. Los desplegables usan
texto subrayado sin marcadores de triángulo; propiedades cambia a Mostrar menos
al desplegar el resto.

Pasaron 46 pruebas del frontend y la compilación. Se comprobó en navegador la
ausencia de detalles de consumo, la apertura/cierre con Enter sin marcador y
el acceso Ver ficha. QA con SQLite temporal y proveedor simulado; sin llamadas
pagadas, cambios en Supabase, commit ni push.

## Presentación de propiedades en Mobilita · 4/11/2026

La consulta de propiedades devuelve datos estructurados y el chat presenta tres
tarjetas iniciales, sin identificadores visibles y con precios formateados en CLP/UF.
El resto de las primeras diez se despliega; Ver catálogo completo abre Propiedades.
La operación Compra se presenta como Venta, igual que en el catálogo existente.
Las respuestas largas dejan visible el comienzo en vez de saltar al final.

Pasaron 74 pruebas del backend, 46 del frontend y compilación. Se comprobó con
18 propiedades ficticias: tres tarjetas iniciales, despliegue de las diez, formato
móvil sin desbordamiento y navegación al catálogo con los 18 registros. Sólo SQLite
temporal y proveedor simulado; sin migración, llamadas pagadas, commit ni push.

## Histórico de consumo de Mobilita · 4/11/2026

Se añadió al panel administrativo el histórico del chat: costo estimado acumulado,
solicitudes, tokens y período conservado. Incluye propuestas canceladas y respuestas
inválidas con consumo informado; separa costos y tokens desconocidos. No recalcula
costos antiguos ni duplica el gasto al repetir una confirmación.

Se diferenció el presupuesto configurado del saldo o límite real de OpenAI. Se añadió
un enlace al panel oficial. La sincronización de facturación requiere credencial
administrativa y alcance de proyecto/clave; no está implementada ni se afirma que
el total local incluya llamadas externas o registros eliminados.

Pasaron 73 pruebas del backend, incluida la protección exclusiva para admin, y la
compilación del frontend. Se revisó en navegador un histórico ficticio con costos
parciales, Actualizar y el diseño a 390 px. Sólo SQLite temporal; sin llamadas
pagadas, cambios en Supabase, migración adicional, commit ni push.

## Interfaz de Mobilita · 4/11/2026

El acceso flotante se oculta mientras el panel está abierto y reaparece al minimizar
con el control de cabecera o Escape. Se verificó en navegador la conservación del
borrador, el retorno del foco al botón y los márgenes del panel a 390 px.

Se unificaron los colores y la tipografía con el CRM: botones casi negros, superficies
blancas, bordes neutros y textos con los estilos compartidos. El azul quedó en el
personaje y los indicadores de actividad. Se aumentó la legibilidad del saludo,
respuestas y textos secundarios, con revisión del acceso y panel en escritorio y
del ancho y tipografía a 390 px. No cambia las funciones del asistente.

Posteriormente, Bryan solicitó dejar las animaciones siempre activas y retirar el
selector. Se reemplazó el acceso anterior por un personaje animado con saludo estático
que invita a revisar cartera, pendientes y tareas. Abrir el chat o cerrar el saludo
lo oculta durante esa sesión. Se comprobó la persistencia de ese cierre tras recargar,
la ausencia de ajustes, las animaciones activas con movimiento reducido del navegador
y los márgenes del chat a 390 px. Pasaron 44 pruebas del frontend y compilación.
El saludo no consulta al proveedor de IA.

Al informar que no se veían las animaciones, se identificaron dos reglas de movimiento
reducido: una global reducía su duración a 0,01 ms y otra las desactivaba en el chat.
Se incorporó una preferencia local: Sistema, Activadas o Reducidas. Activadas excluye
únicamente el chat de esas restricciones. Se comprobó en navegador con movimiento
reducido activo que los puntos recuperan su duración de 1,15 s y se desplazan, que
los otros modos detienen el movimiento y que la elección persiste al recargar.

Se añadieron animaciones de apertura y entrada de mensajes, sugerencias y propuesta.
La espera incluye puntos, actividad en cabecera, avatar y botón de envío. La solicitud
se muestra de inmediato sin duplicarse al recibir la respuesta. El indicador depende
de la petición real; no simula escritura progresiva ni porcentajes. Se respeta la
preferencia de movimiento reducido.

Se reorganizó el chat tomando como referencia los patrones documentados de Breeze
Assistant e Intercom Copilot: acciones de conversación en cabecera, sugerencias de
consulta, entrada fija, detalles de consumo separados y tarjeta de tarea pendiente
de confirmación. Nuevo chat protege texto y propuestas sin guardar; se puede ampliar
la ventana para leer listados. No cambia permisos ni herramientas del backend.

Se comprobó en navegador con SQLite temporal y proveedor simulado: sugerencias sin
envío automático, Enter para enviar, Mayús + Enter para salto de línea, conservación
y descarte explícito de una propuesta, confirmación de una tarea y ajuste móvil a
390 px. Se corrigió un desbordamiento horizontal detectado en esa revisión. Sin
llamadas pagadas, cambios en Supabase, commit ni push por este ajuste de interfaz.

## Consultas restringidas de Mobilita · 4/11/2026

Se amplió SCRUM-43 con cuatro herramientas: resumen de cartera, tareas sin completar,
tareas vencidas y propiedades disponibles. La sesión determina la cartera propia y
el resumen general requiere rol admin comprobado por el backend. Los listados se
limitan a diez registros, con total y fecha de consulta. Las propiedades sólo exponen
columnas comerciales. Las tareas corresponden a los leads de la cartera, porque no
tienen un responsable propio en el modelo actual.

El LLM elige una herramienta permitida; no recibe los resultados de la base ni puede
proponer SQL o identidades para la consulta. Los resultados tampoco se envían como
historial al proveedor. Se conserva el guardado de tareas con confirmación y no se
incorporan borrados, tampoco mediante palabras clave de administración.

Pasaron 99 pruebas del backend, 44 del frontend y la compilación. Se probaron alcance
propio y general, cambio de responsable, tareas sin lead, límites, fechas, datos
reservados, herramientas desconocidas y consultas manipuladas.

Se autorizaron cuatro llamadas reales con datos ficticios y hasta US$0,05 estimados.
Cartera propia, vencidas, propiedades y resumen general admin dieron los resultados
esperados en SQLite temporal: US$0,0008322 estimados. Evidencia:
backend/evidencias/mobilita_consultas_real_20261104_4b7f8aab.json.

No requiere migración adicional. No se modificó Supabase en estas pruebas. No se
implementó un servidor MCP ni una cuenta PostgreSQL de sólo lectura: se usa una
capa de funciones restringidas sobre la API existente. Conectarlo a otro CRM requiere
adaptador y autorización en ese CRM. SCRUM-43 sigue En revisión; falta la prueba
funcional en el CRM habitual y concurrencia en PostgreSQL. Sin commit ni push.

## Conversación sobre el CRM con Mobilita · 4/11/2026

Por solicitud de Bryan se amplió SCRUM-43: Mobilita explica funciones existentes
del CRM y permite continuar después de una respuesta o aclaración. Se incorporó
una guía del producto; las consultas generales no reciben fichas completas ni
datos reservados de la base. Los temas ajenos se rechazan brevemente cuando el
modelo los clasifica fuera de alcance. La API usa un texto fijo para ese rechazo.
Sólo se mantiene la escritura de tareas, con revisión y confirmación.

El servidor recupera hasta seis turnos propios y comprueba su autor y vigencia.
No admite un historial proporcionado por el navegador. El contexto usa el JSON
de propuestas_tarea_chat: no requiere otra migración.

Pasaron 91 pruebas del backend, 44 del frontend y la compilación. Se comprobaron
en navegador la consulta, el rechazo breve, la continuación de la conversación,
la preparación y confirmación de una tarea y el inicio de una conversación nueva,
con proveedor simulado y SQLite temporal.

Se autorizaron otras cuatro llamadas con datos ficticios y US$0,05 estimados como
máximo. La consulta del CRM, el clima, un intento de saltarse los límites y la
aclaración de una tarea dieron los resultados esperados: US$0,000760 estimados.
Evidencia: backend/evidencias/mobilita_general_real_20261104_52dcc123.json.
Es una muestra pequeña; no acredita rechazo perfecto de todas las entradas ni
concurrencia en PostgreSQL. No se modificó Supabase durante estas comprobaciones.
SCRUM-43 conserva En revisión. Sin commit, push ni despliegue.

## Comprobación real del asistente de tareas · 4/11/2026

La interfaz pasó a una ventana flotante llamada Mobilita, disponible desde los
listados del CRM. Conserva el borrador y la propuesta al minimizar y navegar,
permite cerrar con Escape y adapta el tamaño a móvil. Se comprobó el guardado
desde el chat, la conservación al abrir y cerrar un formulario y la ausencia de
desbordamiento a 390 px, con SQLite y proveedor simulado. No se generaron nuevas
respuestas pagadas por este cambio de interfaz.

Bryan compartió la salida de migrar.py con 53 instrucciones aprobadas. Después se
comprobó directamente, en modo de sólo lectura, la presencia de propuestas_tarea_chat
en Supabase y que aún no contenía propuestas.

Se autorizó un lote de hasta cuatro llamadas y US$0,05 estimados con datos ficticios.
Se ejecutaron cuatro con el proveedor real por US$0,0003863 estimados. Las respuestas
se probaron a través de la API en memoria con SQLite temporal: tarea para el cliente
correcto y confirmación repetida sin duplicar, dos homónimos y cancelación, solicitud
sin cliente y rechazo de una orden de borrado. Las cuatro comprobaciones técnicas
fueron satisfactorias; se leyeron también las respuestas originales.

La evidencia está en backend/evidencias/chat_tareas_real_20261104_fc515416.json.
Este lote no agregó registros en Supabase. Quedan la prueba funcional del usuario
en su CRM habitual y la comprobación de concurrencia en PostgreSQL. No se acredita
precisión general del modelo a partir de cuatro casos. SCRUM-43 sigue En revisión.
Sin commit, push ni despliegue.

## Asistente para crear tareas · 2/11/2026

Se incorporó SCRUM-43 al sprint 6, bajo Seguimiento comercial asistido y asignada
a Bryan: 8 puntos, inicio el 2/11 y objetivo de entrega el viernes 6/11. El sprint
se inició en Jira y conserva su período del 2 al 9 de noviembre. El alcance nuevo
se distingue del trabajo adelantado de SCRUM-39 y SCRUM-40.

Desde Tareas se interpreta una solicitud escrita, se resuelve el nombre del lead
y se prepara una tarea revisable. Los homónimos requieren selección. Confirmar
registra la tarea; cancelar no modifica el seguimiento. Se comprueban autor,
vigencia, campos y duplicados. Repetir la confirmación devuelve la misma tarea.
El título «Contactado» no modifica el estado del lead.

Se preparó la tabla propuestas_tarea_chat y su migración, sin aplicarlas a Supabase.
El consumo se integra al panel administrativo y los eventos se auditan. Las pruebas
y el navegador usaron SQLite temporal y un proveedor simulado: se comprobó la
selección entre dos leads del mismo nombre y el guardado del texto revisado.
La exclusión mutua entre peticiones simultáneas en PostgreSQL no se probó.
Pasaron 82 pruebas de chat y funciones relacionadas, 72 regresiones adicionales,
43 pruebas de frontend, 62 verificaciones de auditoría y la compilación. Los
evaluadores que comprueban aislamiento se ejecutaron en procesos separados.
SCRUM-43 quedó En revisión; no se registra aceptación funcional del equipo.
Queda validar las respuestas del proveedor real y el entorno compartido; no se
reutiliza una autorización anterior de llamadas pagadas.

También se retiró la configuración del alojamiento usado para la demostración.
La presentación se preparará con ejecución y grabación locales; Supabase y el
proveedor de IA siguen siendo servicios externos. Los cambios de código siguen
locales, sin commit ni push. Los informes 2.4 y 2.6 no se modificaron.

## Revisión de la ficha del cliente · 30/10/2026

La ficha se organizó en Resumen, Asistente, Seguimiento y Propiedades. El selector
del asistente reúne las cinco funciones; modelo, consumo y contexto se consultan
en detalles desplegables. Se conservaron notas y borradores al cambiar de sección.
Se revisaron escritorio, móvil y navegación por teclado.

La comprobación del navegador usó una base temporal y proveedor simulado: preparar
no creó contactos, confirmar guardó una llamada con el texto editado y reabrir la
ficha conservó ese registro. Un fallo simulado mantuvo las notas sin crear contactos.
Pasaron 35 pruebas de frontend, 13 de llamadas y 10 de cartera, y la compilación.
No hubo llamadas pagadas, cambios en Supabase ni modificación de estados en Jira.
La reorganización sigue local, sin commit ni push. SCRUM-39, 40 y 41 siguen en
revisión; el sprint 6 continúa futuro, previsto del 2 al 9 de noviembre.

## Integración del avance · 29/10/2026

El commit f22957c reúne las notas de llamada con confirmación y los filtros de
cartera, junto con sus pruebas. Antes de integrar la evaluación y sus evidencias
se repitieron 93 pruebas del backend, 12 del frontend y la compilación; todas
pasaron. Esta comprobación no hizo nuevas llamadas pagadas.

El avance corresponde al 29/10, antes del período previsto del sprint 6
(2 al 9 de noviembre). SCRUM-39 y SCRUM-40 siguen en revisión; SCRUM-41 continúa
en revisión fuera de ese sprint y SCRUM-42 está finalizado. Queda actualizar
los registros compartidos de seguimiento y revisar las respuestas con el equipo.
Los informes 2.4 y 2.6 ya entregados no se modifican como parte de este avance.
Las entradas anteriores conservan el estado que tenían cuando se registraron.

## Regresión real del borrador y las notas · 29/10/2026

Bryan autorizó dos llamadas adicionales con presupuesto estimado de US$0,01.
El lote 77784ccf-6ba7-4c85-a8c0-e225eb9509b8 terminó con dos respuestas, sin errores
de transporte, y US$0,0004061 estimados. El borrador respetó la reserva como estado
no disponible y no atribuyó al inmueble la comuna buscada. El JSON de llamada
conservó la contradicción de dormitorios e ignoró la orden pegada.

La revisión técnica asistida fue satisfactoria para estos dos casos. La evidencia
original y las observaciones se guardaron por separado en backend/evidencias,
conservando los resultados anteriores. Los criterios reforzados del borrador hacen
que su huella difiera de la primera versión; no se presenta como una comparación
automática entre casos idénticos. El caso de llamada conserva su huella.

SCRUM-42 queda cerrado técnicamente por la regresión comprobada. SCRUM-41 continúa
en revisión: las respuestas se mantienen pendientes de revisión humana, sin atribuir
una aprobación al equipo. Entre ambos lotes se hicieron trece llamadas autorizadas
por US$0,0017140 estimados. No se hizo una tercera ejecución ni se modificó Supabase.
Los cambios siguen locales, sin commit, push, migración o despliegue.

## Lote real y corrección de fidelidad de datos · 29/10/2026

Bryan autorizó hasta once llamadas con datos ficticios y presupuesto estimado de
US$0,10. Se ejecutaron los once casos con gpt-6-luna, sin errores de transporte,
por US$0,0013079 estimados según el consumo y los precios configurados. No se
consultó ni modificó Supabase. Las respuestas originales se conservaron junto
con su plan, configuración y consumo.

La revisión técnica asistida encontró diez respuestas satisfactorias en esta muestra
y una que requiere corrección. En mensaje_moneda_y_reserva, el borrador atribuye
La Reina a la propiedad aunque la comuna sólo aparece en la búsqueda del cliente.
También deja ambiguo si el estado Reservada afecta a la disponibilidad. La revisión
se guardó aparte: no representa aprobación de Bryan, Amaro o el docente ni se
registró como una revisión humana de las once respuestas.

Se creó SCRUM-42 como tarea de defecto, con dos puntos propuestos, bajo SCRUM-38
y fuera del alcance del sprint 6. Se corrigieron las instrucciones comunes y el
contexto de propiedades: no transferir datos del perfil al inmueble, respetar los
estados no disponibles y declarar sin registrar una comuna ausente. El criterio
del caso se reforzó; la entrada y la evidencia del lote original permanecen intactas.
La comparación reconocerá que sus criterios cambiaron, sin presentar las dos
versiones como un caso idéntico.

Tras la corrección pasaron 145 comprobaciones: 19 del evaluador, 24 del modo real
con transporte simulado, 27 del asistente, 13 de llamadas y 62 de auditoría.
Se preparó, sin ejecutarlo, un plan de dos casos con reserva estimada de
US$0,0017189 y presupuesto propuesto de US$0,01. Las once llamadas anteriores ya
se usaron; la repetición requiere una autorización nueva. SCRUM-41 y SCRUM-42
continúan en revisión. Sin commit, push, despliegue ni cambios de estructura.

## Preparación de la evaluación real · 29/10/2026

SCRUM-41 comenzó el 29/10 por solicitud de continuar. Permanece en el backlog,
sin añadirla al alcance de 13 puntos del sprint 6 futuro. Se amplió el conjunto
a once casos: los nueve anteriores y dos de notas de llamada. Cada caso conserva
fecha de referencia, datos ficticios, resultado esperado y afirmaciones que debe evitar.

La herramienta mantiene la simulación como opción predeterminada. Ahora permite
preparar un plan con modelo, precios, límite por respuesta, máximo de llamadas y
reserva estimada. Ejecutarlo exige confirmar el identificador de ese lote; el plan
se marca para impedir su reutilización accidental desde la misma carpeta. No usa
la API del CRM ni conecta a Supabase. La ejecución reserva un archivo nuevo antes
de llamar y guarda el avance. Los fallos, consumo desconocido o cambio de modelo
detienen el lote sin reintentos. El presupuesto es estimado, no una garantía de cobro.

Pasaron 143 comprobaciones: 19 del evaluador, 23 del modo real con transporte
simulado, 26 del asistente, 13 de llamadas y 62 de auditoría. La red estuvo simulada
en las pruebas del modo real. Los archivos de esos dobles de prueba fueron temporales;
no se entregan como respuestas del modelo real. La ejecución simulada completa de
once casos quedó con once respuestas pendientes de revisión y cero respuestas
reales evaluadas. La evidencia histórica del 16/10 no se modificó.

Se preparó un plan sin ejecutarlo: once casos, máximo de once intentos y 900 tokens
de salida por solicitud. Con los precios configurados, la reserva estimada es
US$0,0085752 y el presupuesto propuesto es US$0,10. No se consume la autorización
de llamadas anteriores. Falta autorización nueva para ejecutar y después revisar
las respuestas; SCRUM-41 no está finalizada. Sin commit, push, despliegue o migración.

En la comprobación anterior del CRM habitual se consultaron, en modo de sólo lectura,
el análisis #24 y su interacción #30: una llamada nueva guardada junto al WhatsApp
anterior del cliente ficticio, con auditoría separada. Es evidencia manual del flujo
de SCRUM-39, no una ejecución del lote de evaluación de SCRUM-41.

## Mi cartera y filtro por responsable · 29/10/2026

SCRUM-40 se adelantó al 29/10 por solicitud de continuar el desarrollo. Permanece
asociada al sprint 6 futuro (2–9/11): este trabajo previo se registra en octubre,
sin atribuirlo a jornadas de noviembre ni iniciar el sprint retrospectivamente.

El listado ofrece Todos y Mi cartera. Administración dispone además de responsables
activos y Sin asignar. La identidad de Mi cartera se resuelve con la sesión en la
API; los filtros administrativos se autorizan allí. Todos mantiene la visibilidad
existente. La búsqueda, estado y atención se combinan dentro de la cartera y el
contador corresponde a ese conjunto. Actualizar y reintentar conservan los filtros.

Se ejecutaron 190 comprobaciones: 10 pruebas nuevas de API de carteras, 35 del
frontend y 145 regresiones de asignaciones (13), asistente (24), llamadas (13),
auditoría (62) y validaciones (33). Todas aprobadas; frontend compilado.

La revisión visual se realizó con SQLite temporal, cuatro cuentas y cinco clientes
ficticios. Se comprobaron filtros combinados, clientes sin asignar, fallo y reintento,
cambios rápidos de cartera, dos ejecutivos con resultados diferentes y una cuenta
sin clientes que puede volver a Todos. Una reasignación realizada en esa base temporal
retiró el cliente de la cartera anterior y lo mostró en la nueva. Los ejecutivos
no vieron opciones administrativas. No se usó el proveedor de IA ni Supabase.

La estructura de datos se conserva. Pendiente revisar la función en el CRM habitual
antes de finalizar la historia. Los cambios están locales, sin commit, push o
despliegue. Actualizar los registros compartidos con este trabajo previo al sprint;
no modificar los informes 2.4 y 2.6 entregados ni inventar una Daily de Amaro.

## Preparación del sprint 6 y notas de llamada · 29/10/2026

Se creó la épica SCRUM-38 y las historias SCRUM-39, 40 y 41, con Bryan como
responsable e informador. Tras elegir Bryan el período 2–9/11, se programó el
Sprint 6 Seguimiento con IA con SCRUM-39 y 40 (13 puntos propuestos). El sprint
continúa futuro; SCRUM-41 queda en el backlog. El trabajo de SCRUM-39 del 29/10
es previo al sprint, no avance realizado durante noviembre.

La preparación de llamadas usa únicamente las notas introducidas y la identificación
del cliente. La API valida la propuesta estructurada y registra análisis, autor,
modelo y consumo. El ejecutivo puede editarla y confirmar una interacción de tipo
Llamada. Preparar o descartar no crea contactos ni modifica el perfil, tareas,
oportunidades o visitas. Las propuestas originales se conservan por separado del
texto finalmente confirmado. No hay llamada telefónica, transcripción ni envío.

Se comprobaron 13 pruebas nuevas del backend, 29 del frontend y 145 regresiones
del asistente, evaluador, duplicados de tareas, auditoría y validaciones. En el
navegador, usando el CRM integrado con SQLite temporal y un proveedor simulado,
se revisaron fallo con conservación de notas, descarte sin contacto, edición,
guardado único, reapertura con persistencia y separación entre dos clientes.

No se usó el proveedor real ni se modificó Supabase. No se necesita migración de
estructura. La calidad del texto del modelo real y la revisión en el CRM habitual
siguen pendientes. Esto no equivale a una aprobación del equipo o del docente.

Pendiente de registrar en los archivos compartidos: planificación y backlog del
sprint 6, incorporación de SCRUM-38 a 41 al Product Backlog y evidencias de épicas e
historias, y el avance del 29/10 en la Daily. No registrar una nueva Daily de Amaro
ni un impedimento de negocio por los permisos del entorno de pruebas. El burndown
del sprint 6 no debe inventar avances diarios ni confundir el trabajo previo con
el realizado desde el 2/11. Los informes 2.4 y 2.6 entregados no se modifican.

Los cambios de este bloque están locales, sin commit, push ni despliegue.

## Revisión del seguimiento y preparación de entrega · 23/10/2026

Bryan compartió dos capturas del CRM: primero se ofrece abrir el seguimiento
pendiente de Diego Alvarado y después se abre esa tarea conservando título,
descripción, prioridad, estado, cliente y fecha. Las capturas comprueban la
apertura, no un guardado nuevo ni todos los casos de validación.

Al preparar una tarea desde IA se consultan los pendientes actuales. Si existen,
crear otra exige indicar una acción distinta y revisar su contenido. Antes de
guardar se comprueba si los pendientes cambiaron. La API rechaza otra tarea
activa del mismo cliente con título y descripción iguales tras normalizar
espacios, mayúsculas y tildes. No detecta equivalencia semántica ni garantiza
exclusión entre solicitudes simultáneas en PostgreSQL.

Se repitieron 168 pruebas y verificaciones: 18 del evaluador, 24 del asistente,
8 de duplicados, 23 del frontend, 62 de auditoría y 33 de validaciones.
La compilación del frontend terminó correctamente. Los scripts de auditoría y
validaciones se ejecutaron en procesos separados porque inicializan sus propios
datos. Las pruebas usaron SQLite temporal y respuestas simuladas, sin modificar
Supabase ni consumir saldo de IA. La herramienta de evaluación continúa siendo
simulada: estos resultados no son una nueva evaluación del modelo real.

Se prepara la integración en Git con autorización de Bryan, excluyendo el informe
2.6 local y los documentos ajenos al desarrollo. Los estados de Jira no se han
vuelto a consultar ni modificado en esta revisión. El commit y su subida no
equivalen a despliegue, cierre del sprint o aceptación de todas sus historias.
Pendiente: actualizar las evidencias compartidas del sprint 5 con el resultado
real de la integración y revisar los criterios de cierre antes de finalizarlo.

## Identificación del cliente al gestionar tareas · 21/10/2026

Bryan detectó dificultad para distinguir tareas con el mismo título en distintos
clientes al probar el seguimiento desde IA. La diferencia de fechas 17/10–19/10
no es un error confirmado: aclaró que había seleccionado otro cliente durante
la comprobación. No se modificaron las fechas almacenadas para hacerlas coincidir.

Se creó SCRUM-37 como tarea de mejora de usabilidad bajo SCRUM-18, asignada al
Sprint 5, con Bryan como informador y responsable. Inicio 21/10, vencimiento
23/10 y estimación inicial de dos puntos. Se añadió después del inicio: la
referencia original del sprint se conserva en 11 puntos y el alcance pasa a 13.
Ese aumento debe verse en el burndown como cambio de alcance, no como trabajo
planificado desde el 19/10. No se añadió un impedimento: se registró una mejora
detectada durante las pruebas de SCRUM-36.

Cambios locales de presentación:

- FormularioTarea muestra al cliente antes de las instrucciones y mantiene el
  encabezado visible al desplazarse. El nombre sigue al cliente seleccionado.
- Los pendientes de una propuesta identifican al cliente y usan DD-MM-AAAA.
- TablaTareas muestra al cliente en la primera columna y diferencia las acciones
  accesibles de tareas con títulos iguales. No se reescriben títulos almacenados.
- Si no hay cliente o no está disponible se indica expresamente. Un cliente no
  disponible no aparece como Ninguno en el selector de edición.

Verificación: 18 pruebas del frontend aprobadas (cuatro nuevas, con entradas
válidas, ausencia de cliente, cambio de selección y formato de fecha) y compilación
correcta. En un entorno visual aislado se usaron dos clientes ficticios con
tareas homónimas, fechas 17/10 y 19/10 y descripciones distintas. Se comprobó
identificación, apertura de la tarea existente con conservación de datos,
cancelación sin llamadas de guardado, selección de otro cliente y guardado único
en memoria. También se comprobaron las etiquetas Sin cliente asociado y Cliente
no disponible. El entorno no carga App.jsx ni tiene API: esa prueba no acredita
persistencia en Supabase ni sustituye todo el recorrido integrado pendiente en
SCRUM-36. Las capturas están en outputs/sprint5-20261021, fuera del repo interior.

SCRUM-37 pasa a En revisión; no se declara finalizada por la prueba aislada.
README y los informes entregados no requieren cambios para esta mejora visual.
La estructura y los datos de Supabase no se tocaron. Sin commit, push o despliegue.

Texto para añadir a la Daily: Durante las pruebas confundimos tareas con el
mismo título de distintos clientes. Mejoramos la identificación del cliente en
el listado, el formulario y los pendientes propuestos por IA. Pasaron las pruebas
del frontend y la compilación; verificamos el recorrido en un entorno aislado.
Falta la revisión en el CRM integrado. No se confirmó un fallo de fechas.

Pendiente en los archivos compartidos: añadir SCRUM-37 al Product Backlog, anotar
la incorporación posterior al inicio en la planificación y sumar dos puntos de
alcance al burndown, conservando la referencia inicial de 11. El Scrumboard de
Jira ya refleja la actividad. Las hojas de Drive no se han editado en este cambio;
no corresponde rehacer el 2.6 entregado, el modelo relacional ni las retrospectivas.

## Inicio del Sprint 5 y primera implementación · 20 y 21/10/2026

Con la indicación de Bryan de continuar se activó el Sprint 5 en Jira el
20/10/2026 a las 23:55 de Chile (21/10 a las 02:55 UTC). Jira registra ese inicio
efectivo; el fin se mantiene el 26/10 a las 00:00 de Chile. El período 19–26/10
corresponde a la previsión anterior, no a trabajo acreditado desde el lunes.
El alcance seleccionado contiene SCRUM-34, 35 y 36, con una referencia inicial
de 11 puntos. No se atribuye una reunión ni una estimación de equipo no realizada.
La épica SCRUM-18 está En curso y sus historias anteriores continúan finalizadas.

Se prepararon nueve casos ficticios reutilizables en casos_asistente.json: dos
resúmenes, dos recomendaciones, dos mensajes y tres casos de preguntas. Tienen
fecha de referencia fija, ficha, criterios esperados y afirmaciones que deben
evitarse. casos_evaluacion.py valida el conjunto y genera huellas para detectar
cambios en la ficha o en los criterios. No importa el proveedor ni la base de datos.

evaluar_asistente.py permite validar, ejecutar simulaciones, registrar revisiones
en archivos nuevos, resumir sus estados y comparar ejecuciones por caso. No
sobrescribe archivos existentes ni aprueba por defecto. Todas las salidas son
simuladas y se identifican como tales. Este primer módulo todavía no ejecuta el
modelo real ni importa respuestas reales. No acredita una mejora de la calidad
de sus respuestas. README.md incluye los comandos y sus límites.

Verificación realizada:

- prueba_evaluacion.py: 18 pruebas aprobadas, incluyendo datos inválidos, límites,
  duplicados, revisiones, archivos existentes, casos modificados y error simulado.
- prueba_asistente.py: 24 pruebas aprobadas, tres nuevas para esperas agotadas,
  conexión fallida, límites/cuota del proveedor y ocultación de claves en errores.
- Frontend: 14 pruebas aprobadas de tareaDesdeIA y presentación; compilación de
  producción aprobada. No se modificó la interfaz.
- Se ejecutó el comando de simulación dos veces: primera con nueve respuestas
  pendientes y segunda con ocho pendientes y un error simulado. Se generó su
  comparación. No se registró una aprobación humana ni se reemplazó la evidencia
  del 16/10. Archivos en outputs/sprint5-20261021, fuera del repositorio interior.

El intento inicial de pruebas de API se interrumpió por bloqueo del entorno
restringido. La repetición autorizada, con SQLite temporal y proveedor simulado,
terminó correctamente. La primera compilación devolvió EPERM; la repetición
autorizada terminó correctamente. No se consideran defectos confirmados del CRM.
No hubo llamadas pagadas ni conexión a Supabase, migración o despliegue.

Estado de entrega local: SCRUM-34 y SCRUM-35 pasan a En revisión; SCRUM-36 continúa
En curso. Falta revisar el conjunto y la herramienta con Bryan y comprobar en
pantalla, en un entorno temporal, la preparación/cancelación/confirmación de
tareas. Las pruebas de funciones puras y de API no sustituyen esa comprobación
completa de interfaz. No se ha completado el sprint y no se consumen puntos como
finalizados en el burndown. No se hizo commit ni push; se conservaron las
modificaciones ajenas, incluido el informe 2.6 local.

### Texto para el registro de trabajo del 21/10

Preparamos nueve casos reutilizables para las cuatro funciones del asistente y
una herramienta local para registrar y comparar evaluaciones simuladas. Pasaron
las pruebas del evaluador, del asistente y del frontend, junto con la compilación.
Falta revisar los casos y comprobar en pantalla el flujo de tareas antes del cierre.
No utilizamos saldo de IA ni modificamos la base de Supabase. No se confirmó un
impedimento nuevo. Es un registro de trabajo, no un acta de una reunión con Amaro.

Pendiente en los documentos compartidos: reflejar el inicio efectivo del sprint,
las tres actividades seleccionadas y sus estados en Planning, Product Backlog y
Scrumboard; incorporar este avance a la Daily. Para el burndown, conservar el
inicio efectivo con 11 puntos y no inventar días de avance desde el 19/10. No se
actualizaron Drive, Review, retrospectivas, Release ni el informe 2.6 entregado.

## Alcance preparado del Sprint 5 · 20/10/2026

Tras la indicación de continuar de Bryan, se revisaron ia.py, prueba_asistente.py,
tareaDesdeIA.js, sus pruebas y la evaluación conservada del 16/10. Las funciones
del asistente y varios controles ya existen; el nuevo alcance no los presenta
como pendientes de implementación. No se encontraron actividades abiertas ni
duplicados de evaluación/calidad en la consulta de Jira de este corte.

Se crearon y asignaron al Sprint 5, en estado Por hacer:

| Actividad | Tipo | Puntos propuestos | Inicio previsto | Vencimiento |
| --- | --- | --- | --- | --- |
| SCRUM-34 · Preparar casos reutilizables para evaluar el asistente | Historia | 3 | 20/10/2026 | 22/10/2026 |
| SCRUM-35 · Ejecutar y revisar evaluaciones repetibles del asistente | Historia | 5 | 22/10/2026 | 24/10/2026 |
| SCRUM-36 · Verificar errores del asistente y confirmación de tareas | Tarea | 3 | 24/10/2026 | 26/10/2026 |

Bryan es informador y responsable de las tres actividades. No se asignó trabajo
a Amaro ni se registró una opinión suya. Cada actividad contiene criterios de
aceptación o cierre, prioridad y límites. SCRUM-35 depende del conjunto de casos
de SCRUM-34. Los 11 puntos son una propuesta inicial, no capacidad confirmada ni
un acuerdo de Planning Poker. Antes de iniciar se debe revisar si el alcance cabe
en el tiempo disponible. La planificación del sprint sigue siendo 19–26/10, pero
las actividades nuevas no se fechan como iniciadas el 19.

La épica SCRUM-18 pasó a Por hacer porque ahora contiene trabajo nuevo. Sus
historias anteriores siguen finalizadas. El Sprint 5 sigue en estado future;
no se inició ni se modificaron los cuatro sprints cerrados. No se implementó ni
probó código nuevo en esta preparación y no se realizaron llamadas pagadas.

Pendiente documental inmediato: incorporar estas tres filas al Product Backlog
priorizado, registrar el objetivo y alcance propuesto en Planificación de los
sprints y reflejarlas en Scrumboard. La Daily puede registrar esta preparación
real, no una reunión de equipo. No hay un impedimento nuevo confirmado que añadir.
El burndown todavía no debe presentar consumo de puntos; la referencia propuesta
es 11 puntos, sujeta a revisión antes del inicio. No se redactan Review,
retrospectiva ni Release como si este trabajo estuviera completado.

## Fechas de historias y control del Sprint 5 · 20/10/2026

Por solicitud de Bryan se completaron y verificaron mediante el conector las
fechas de SCRUM-30 a SCRUM-33. SCRUM-30 y SCRUM-31 tienen inicio 05/10/2026 y
vencimiento 12/10/2026, correspondientes a la planificación del Sprint 4. Su
finalización real permanece el 15/10. SCRUM-32 y SCRUM-33 tienen inicio 15/10 y
vencimiento 16/10, regularizados según el intervalo histórico documentado, no
como compromiso previo. Su cierre real permanece el 16/10 y siguen sin sprint.
Se añadió esta aclaración a cada historia. No se alteraron puntos ni estados.

Para el Sprint 5, registrar antes de desarrollar: objetivo, historias o tareas
según la naturaleza del trabajo, épica correspondiente, criterios comprobables,
prioridad, estimación propuesta y responsable. El informador debe corresponder a
quien solicita la actividad; no se atribuirán solicitudes, pruebas u opiniones a
Amaro sin respaldo. Las fechas de las actividades deben encajar en el período
seleccionado, distinguiendo planificación e inicio efectivo. El sprint aún no se
ha iniciado ni tiene actividades seleccionadas.

Mantener al día la planificación, Product Backlog priorizado y Scrumboard; el
Sprint Backlog se controla en Jira sin exigir otro archivo, según la decisión
previa de Bryan de omitir ese documento. Registrar avances reales en Daily,
bloqueos reales en impedimentos y cambios del trabajo pendiente para el burndown.
Guardar pruebas y evidencias del código. Review, retrospectivas y Release se
actualizarán cuando ocurran sus revisiones o resultados, sin inventar reuniones.
Revisar impactos en Gantt, historias, mapas, modelo de datos y documentación
técnica sólo cuando cambie el alcance o funcionamiento que describen. El informe
2.6 entregado no se reescribe para presentar trabajo futuro como parte de aquella
entrega. No se hizo commit, push ni cambio de código en esta regularización.

## Período solicitado para el Sprint 5 · 20/10/2026

Bryan indicó el período planificado del lunes 19 al lunes 26 de octubre de 2026.
La configuración se realiza el 20/10; no acredita un inicio efectivo ni trabajo
realizado el día 19. El sprint se mantendrá sin iniciar hasta seleccionar y estimar
el alcance pendiente.

El conector disponible permite consultar el tablero, pero no ofrece la operación
de creación/edición de sprints. Se utilizó la interfaz de Jira. La creación produjo
el contenedor vacío con id 40 y los datos automáticos «Sprint 4 Equipo y asignación
2», período 12–19/10, estado future. Se intentó cambiarlo a «Sprint 5 Evaluación y
calidad del asistente», período 19–26/10 y objetivo de evaluación repetible.

Jira mostró «Algo ha ido mal. Actualiza la página y vuelve a intentarlo». La consulta
posterior mediante el conector y la recarga del navegador confirmaron que las
ediciones no persistieron. Un segundo intento reducido de nombre y objetivo también
falló. No se crearon otros contenedores, no se añadieron actividades ni se inició
el sprint.

Después se guardó correctamente el mismo contenedor 40 con el nombre «Sprint 5
Calidad del asistente», período 19–26/10/2026 y objetivo «Evaluar el asistente con
casos repetibles y verificar errores y seguimiento con tareas». La consulta del
conector y la recarga del tablero confirmaron la configuración. Sigue en estado
future, sin iniciar y con cero actividades. Queda seleccionar y estimar el trabajo
antes de iniciarlo. No se ha confirmado la causa del rechazo inicial. Los sprints
anteriores no se modificaron.

## Retoma del desarrollo y preparación del Sprint 5 · 20/10/2026

El informe 2.6 ya fue entregado según lo comunicado por Bryan. Se conserva como
registro de esa entrega y no se modifica para incorporar trabajo posterior.
Los apartados fechados más abajo conservan los resultados y pendientes de sus
respectivos cortes; no representan todos el estado actual.

Se consultó Jira mediante el conector: 27 historias y cuatro épicas finalizadas.
Las 27 historias tienen épica. Los sprints 1 a 4 están cerrados; no hay sprint
activo ni Sprint 5 en el listado del tablero. SCRUM-32 y SCRUM-33 están finalizadas
sin sprint y se mantienen fuera de los sprints históricos.

La rama local es main y el código parte de deefe06. Tras consultar GitHub y
descargar únicamente sus referencias, origin/main apunta a faff5b9. Hay nueve
commits remotos posteriores que, comparados con deefe06, cambian sólo los informes
2.4 y 2.6 y la presentación de Fase 2. No contienen cambios de código. Se conserva
la modificación local del 2.6 y los archivos sin seguimiento del usuario. No se
hizo pull ni se sustituyeron documentos.

Se ejecutó prueba_asistente.py: 21 pruebas aprobadas. El script usa SQLite temporal
y un proveedor simulado. Esta ejecución verifica el flujo y sus controles, no la
calidad de respuestas nuevas de un modelo real. No se realizaron llamadas pagadas
ni escrituras en Supabase. El primer intento bajo el entorno restringido no terminó
y se interrumpió; la ejecución posterior autorizada finalizó correctamente.

### Propuesta para el siguiente sprint

Objetivo propuesto: hacer repetible la evaluación del asistente y comprobar sus
controles ante errores antes de ampliar las automatizaciones. No es todavía una
planificación acordada ni un sprint iniciado.

Trabajo candidato, por priorizar y estimar antes de seleccionarlo:

- Preparar casos ficticios reutilizables para las cuatro funciones, con criterios
  de revisión por caso y separación entre resultados simulados y respuestas reales.
- Preparar un registro de evaluación que permita repetir casos y comparar sus
  respuestas sin modificar los datos del CRM. Una revisión pendiente no se contará
  como aprobada. La ejecución con proveedor real requerirá autorización de gasto.
- Revisar la cobertura de errores del proveedor y del flujo de tareas. Añadir
  pruebas de límites o regresión sólo para comportamientos comprobables; los
  defectos que aparezcan se registrarán con su reproducción y criterio de cierre.

Para iniciar: definir alcance seleccionado, responsables y estimación; registrar
el Sprint Planning y fijar fechas reales en Jira. No se fijan horas disponibles,
opiniones del compañero ni una fecha de inicio retroactiva. WhatsApp no se incluye
en esta propuesta. No se trasladan historias terminadas para llenar el sprint.

### Seguimiento documental del nuevo trabajo

- Planificación de sprints: añadir el Sprint 5 sin reescribir los sprints 1 a 4.
- Product Backlog: registrar el trabajo nuevo y su prioridad antes de desarrollarlo.
- Sprint Backlog y Scrumboard: reflejar sólo el alcance seleccionado y sus estados.
- Registro de trabajo o Daily: anotar avances reales con fecha; no afirmar que hubo
  una reunión si sólo se realizó trabajo individual.
- Impedimentos: registrar sólo bloqueos reales, con su estado efectivo.
- Burndown del Sprint 5: obtener la referencia inicial y los cambios desde su inicio,
  conservando aparte los burndowns reconstruidos de los sprints anteriores.
- Evidencias: conservar casos, resultados y comprobaciones durante el desarrollo.
- Review, retrospectiva y Release: actualizar cuando existan una revisión, resultados
  o una nueva versión que registrar; no redactarlos como hechos antes de realizarlos.

No se modificaron Jira ni Drive durante esta retoma. No hubo cambios funcionales,
commit, push ni despliegue.

## Módulo de presentación y UX · 16/10/2026

Antes de iniciar este módulo se creó y subió `3a0d95a`, con las mejoras anteriores
de IA, tareas revisables, ocho casos de calidad y carga de datos ficticios. Los
documentos no relacionados que estaban sin seguimiento se conservaron sin añadirlos
al commit. Este módulo se mantiene separado del anterior.

Se aplicó la normalización de 29 leads (cinco nombres con sufijo y/o origen del
escenario) y cinco títulos de propiedades. Se retiraron los marcadores visibles de
los nombres y se cambió el origen heredado a Escenario de prueba. Los datos no pasan
a ser clientes u ofertas reales: conservan la marca interna o descripción ficticia.
Se verificó que identificadores, relaciones, demás campos y auditorías anteriores
quedaron intactos. La segunda ejecución produjo cero cambios. No se reescriben
textos históricos ni análisis de IA ya guardados. Registro agregado:
`backend/evidencias/normalizacion_presentacion_20261016.json`.

Se adaptó el cargador inicial para no volver a crear propiedades con el prefijo
anterior ni sobrescribir las ediciones del usuario. La API admite el origen nuevo y
conserva la compatibilidad con el valor histórico. Se corrigió además el máximo de
150 caracteres del título de propiedades para que coincida con su columna real.

UX implementada: búsqueda sin tildes; búsqueda por responsable en leads y por código
en propiedades; filtro venta/arriendo y limpieza de filtros; filtro Sólo vencidas;
etiqueta textual de vencimiento; detalle de tareas plegable; acciones de fila siempre
visibles; moneda y estado en los intereses. Se marcaron campos obligatorios y se
plegaron los campos opcionales de la ficha ampliada de propiedades. Se cambió el
indicador estático Supabase conectado por Sesión iniciada, que no pretende verificar
el estado de la base.

Paneles: foco visible, recorrido Tab/Shift+Tab limitado al formulario, cierre con
Escape y retorno del foco a Nueva propiedad comprobado en navegador. En ancho 430px
la página mantuvo 430px de ancho y la tabla se desplazó dentro de su contenedor;
los botones de navegación mantienen nombres accesibles aunque se oculten los textos.
Se corrigió durante la revisión el retorno del foco y la estrechez de las columnas.

Verificación: 221 comprobaciones del backend (incluidas siete del nuevo módulo),
14 del frontend y compilación aprobadas. En escenario temporal se combinaron nunoa
y Arriendo (dos resultados), se limpiaron filtros y se vieron siete tareas vencidas.
Se recorrieron Inicio, Pipeline, Agenda y Leads sin alertas visibles en ese escenario.
Como ejecutivo no aparecieron Actividad, Consumo de IA ni campos privados del
propietario. No hubo generaciones de IA ni escritura de pruebas visuales en Supabase.
No es una auditoría completa de todos los dispositivos o de accesibilidad.

Pendiente para documentación: registrar este módulo y los anteriores en Jira,
actualizar historias y Product Backlog, Daily/impedimentos, informes 2.4/2.6, Release
y evidencias. Mantener los sprints cerrados y sus burndowns como registros históricos.
La definición inicial y el estado ficticio de los datos no se deben presentar como
validaciones externas, clientes reales o ventas reales.

## Calidad del asistente y escenario ficticio · 16/10/2026

Se añadió fecha de referencia UTC al contexto y moneda/estado al describir
propiedades de interés. Se corrigió la instrucción de preguntas: debe tener en
cuenta requisitos pendientes en notas y tareas aunque los campos básicos estén
completos. Se reforzó el manejo de contradicciones, visitas pasadas y redacción
de borradores para el cliente. No se afirma que las instrucciones garanticen
eliminar errores o inyecciones de texto.

Con autorización para ocho llamadas y un máximo estimado de US$0,10 se obtuvieron
ocho respuestas del proveedor con fichas artificiales. Se revisaron requisitos de
terreno/estacionamientos, perfil sin pendientes, búsqueda contradictoria, visita
programada pasada, cliente cerrado sin permiso de contacto, orden maliciosa en
notas, propiedad reservada en UF y tarea pendiente vencida. En esta muestra se
respetaron los criterios. Se observó que el resumen también señaló una visita
anterior al ingreso del lead, sin inventar que se había realizado. La muestra es
una ejecución por caso, no una evaluación estadística ni garantía de cero errores.
Costo según configuración: US$0,00154; facturación del proveedor no verificada.
No se enviaron datos reales del CRM ni se guardaron esos análisis en Supabase.
Registro completo: `backend/evidencias/evaluacion_calidad_20261016.json`.

Se aplicó el escenario ficticio con 24 clientes, 18 propiedades, 24 intereses,
18 interacciones, 22 tareas, 18 oportunidades y 6 visitas nuevos. Los nombres no
contienen Demo; se conserva la marca interna de prueba y la descripción ficticia
de propiedades. No hay teléfonos de personas reales ni fotos ajenas. Se compararon
huellas de los registros previos y quedaron intactos; la segunda ejecución agregó
cero registros en todas las categorías. Totales verificados: 30 leads, 25 propiedades,
26 tareas, 30 intereses, 25 interacciones, 23 oportunidades y 11 visitas. La carga
dejó auditoría sin atribuir contactos ficticios a una persona del equipo.
Comprobación agregada: `backend/evidencias/escenario_pruebas_20261016.json`.

Pruebas sin proveedor: asistente 21, validaciones 33, escenario anterior 17,
escenario nuevo 5, catálogo 8, auditoría 62, asignaciones 13, consolidación 12,
oportunidades 15, visitas 15 y matching 13: 214 comprobaciones aprobadas. El frontend
aprobó sus 10 pruebas del flujo de tareas y compiló: 224 comprobaciones técnicas en
total. Los tests de instrucciones verifican el código, no la calidad del modelo;
las ocho respuestas reales se revisaron por separado.

Pendiente para la fase de documentación: actualizar Jira, Daily, impedimentos,
Product Backlog e historias, informes 2.4/2.6, Release y evidencias de prueba con
estas ampliaciones y resultados. Las capturas y actividades del escenario ficticio
no se deben presentar como clientes, contactos o ventas reales. No modificar los
burndowns ni las actas de sprints ya cerrados para incluir este desarrollo posterior.
No se creó un sprint nuevo ni se inventaron puntos, reuniones u opiniones de Amaro.
Estos cambios siguen locales: no hay commit, push ni despliegue en este avance.

## Seguimiento a partir de una recomendación · 15/10/2026

Mejora posterior: se añadió Abrir tarea existente junto a cada pendiente mostrado.
El usuario observó que la recomendación de su lead pedía avanzar una tarea ya creada.
El botón abre esa tarea en modo edición sin crear otra, conserva sus datos y mantiene
la propuesta de IA separada como referencia. Guardar utiliza la actualización normal.
No se afirma que el sistema detecte automáticamente similitud entre tareas.

Verificación de esta mejora: 10 pruebas del preparador aprobadas (incluyen tres
nuevas sobre selección y conservación de tareas existentes) y compilación correcta.
En SQLite temporal se abrió el pendiente original, se editó su descripción y se
guardó: siguió existiendo una tarea y Actividad registró Modificación de Tarea #1,
no Creación. No se llamó al proveedor ni se modificaron registros en Supabase.

Se implementó el paso desde una recomendación guardada a un formulario de tarea.
La propuesta se mantiene como texto editable, con referencia al análisis de origen;
no se interpreta como una orden ejecutable. El formulario consulta y muestra las
tareas pendientes antes de que el usuario confirme. Si falla la consulta, no abre
un formulario con una lista engañosamente vacía. El lead queda vinculado y no se
puede cambiar desde ese borrador. No prepara tareas para leads cerrados.

Cancelar no guarda; Crear tarea usa el endpoint y la auditoría existentes. El
formulario bloquea envíos simultáneos mientras guarda. No hay nueva tabla, migración,
dependencia, envío de mensajes o llamada adicional a IA en este paso. La prioridad
inicial es la habitual Media y la fecha queda vacía para que decida el ejecutivo.
La consulta de pendientes no garantiza evitar duplicados entre distintos usuarios.

Verificación local: 7 pruebas del preparador (casos válidos, otro lead, tipo inválido,
texto vacío, lead cerrado, límites y conservación de los datos); 16 pruebas del
asistente, 62 de auditoría y 33 de validaciones aprobadas. Frontend compilado.
Prueba visual con base SQLite temporal, cuenta ficticia y recomendación simulada:
había una tarea inicial; cancelar mantuvo una; confirmar creó una segunda tarea con
el título editado, lead correcto y descripción de origen; Actividad mostró un único
registro de creación. No se utilizó Supabase ni se hicieron llamadas pagadas.

Pendiente: prueba del equipo en el CRM habitual. No se creó todavía una historia
nueva ni se modificaron los sprints cerrados; el usuario pidió registrar en Jira
y actualizar los archivos después de terminar este avance.

### Archivos que deben recoger las ampliaciones

- Jira: registrar la tarea asistida y sus criterios; añadir las comprobaciones que
  el usuario compartió para borrador y preguntas. Mantener responsables reales.
- Product Backlog e historias de usuario: incorporar la tarea asistida y actualizar
  el estado de las dos funciones anteriores sin inventar puntos ni sprint.
- Daily: registrar desarrollo y pruebas efectivamente realizados por Bryan, sin
  atribuir reuniones ni trabajo no confirmado a Amaro.
- Impedimentos: cerrar el rechazo de la clave por la validación real; no anotar los
  cortes del servidor temporal como si fueran un fallo de la aplicación productiva.
- Informes 2.4 y 2.6: actualizar funcionalidades, pruebas, resultados y límites;
  distinguir muestra real de IA y pruebas técnicas simuladas.
- Release y evidencias del sistema: añadir el flujo confirmado y sus capturas reales
  cuando el equipo lo pruebe. Las capturas de SQLite son pruebas simuladas.
- User Story Map e Impact Mapping: revisar si necesitan ampliar la parte de
  seguimiento y apoyo al ejecutivo; no cambiar sus objetivos sin necesidad.
- Scrumboard y Sprint Planning: actualizar sólo al planificar trabajo nuevo. No
  incorporar retrospectivamente las ampliaciones a sprints cerrados.
- Burndowns y revisiones de sprints cerrados: conservar el registro histórico.
- Gantt: revisar sólo si cambia el calendario; no alterar duraciones sin acuerdo.
- Retrospectivas: agregar aprendizajes cuando se revisen; no inventar opiniones ni
  una reunión. La definición original del proyecto permanece como antecedente.

## Validación real del asistente · 15/10/2026, 23:32 (Chile)

El usuario reemplazó la clave local. Se consultó la disponibilidad del modelo con
resultado HTTP 200 y se hicieron cuatro generaciones autorizadas con datos ficticios,
sin escribir en Supabase ni enviar mensajes. Se conservan los resultados completos
en `backend/evidencias/validacion_asistente_20261015.json`.

Revisión de la muestra:

- Perfil incompleto, borrador: pidió aclarar la búsqueda, sin ofrecer propiedades.
- Perfil incompleto, preguntas: tres preguntas sobre datos comerciales ausentes.
- Perfil completo, borrador: mantuvo comuna, tipo de propiedad, presupuesto,
  dormitorios, baños y plazo registrados; no confirmó una visita ni una oferta.
- Perfil completo, preguntas: reconoció que los datos básicos estaban completos,
  sin fabricar preguntas adicionales.

El bloqueo de credenciales queda resuelto para esta ejecución. El costo calculado
con los precios configurados fue US$0,0005874; no es un comprobante de facturación.
No se probaron en esta muestra clientes cerrados, notas maliciosas o contradicciones
entre campos y contactos. Tampoco se evaluó WhatsApp. Los borradores contienen algunas
expresiones internas del CRM: el ejecutivo debe revisarlos antes de compartirlos.

Esta actualización supera el bloqueo descrito en el registro anterior sin borrar
el antecedente. Los informes Word y el Excel aún necesitan incorporar este avance.

## Ampliación del asistente · 15/10/2026

Se incorporaron dos opciones a la ficha: preparar un borrador de seguimiento y
sugerir preguntas sobre información comercial faltante. Se mantienen el resumen y
la recomendación. El borrador se edita de forma temporal y se copia; no hay envío
de mensajes, registro de contacto ni actualización automática del perfil.

Las 16 pruebas nuevas verificaron los cuatro tipos, autenticación, entradas
inválidas, persistencia del análisis, consumo simulado y manejo de errores. Se
ejecutan sin Supabase ni llamadas externas. Las pruebas existentes se ejecutaron en
procesos separados porque algunos scripts crean sus propios datos al importarse;
ejecutarlos todos en el mismo proceso mezclaba las bases temporales.

Resultado de la ejecución aislada: asistente (16), asignaciones (13), catálogo (8),
auditoría (62), validaciones (33), matching (13), consolidación (12), oportunidades
(15) y visitas (15): 187 comprobaciones aprobadas. También compiló el frontend.
Se revisó en el navegador un prospecto ficticio con proveedor simulado: selección
de funciones, edición temporal conservada al alternar opciones y copia del mensaje.
Esta revisión visual no es evidencia de una respuesta real del modelo.

Se intentaron cuatro generaciones reales con perfiles ficticios; las cuatro
fallaron. Una consulta posterior del modelo, sin generar texto, devolvió HTTP 401
con código `invalid_api_key`. No se evaluó la calidad de respuestas ni se hicieron
más generaciones. El consumo facturado no se confirmó en el panel del proveedor.

Impedimento abierto: credencial del proveedor rechazada. Próximo paso: sustituirla
localmente por una clave válida y comprobar las dos funciones con datos ficticios,
con autorización para el gasto. Nunca se debe pegar la clave en documentos o Jira.

SCRUM-32 y SCRUM-33 registran este trabajo fuera de los cuatro sprints cerrados.
No se inventaron puntos, reuniones, aceptación del compañero ni fechas de sprint.
WhatsApp sólo se plantea como siguiente integración, no está conectado.

Los informes 2.4 y 2.6 y el Excel entregados en el avance anterior reflejan ese
corte anterior: todavía no incluyen esta ampliación ni su bloqueo de credenciales.
No se reemplazaron archivos en Drive ni documentos que el usuario dejó para subir.

## Actualización del historial anterior · 15/10/2026

Se confirmó directamente en Supabase que había tres movimientos en
`historial_asignaciones` y uno en `asignaciones_lead`. Se aplicaron 51 instrucciones
de migración y se incorporaron los tres movimientos anteriores al historial actual.
Se verificó igualdad de fechas, responsables, nombres registrados y correo del autor.
La tabla original, los responsables actuales y el movimiento nuevo quedaron intactos.
Una segunda consolidación incorporó cero registros. No se eliminaron tablas ni filas.

El historial ahora se ordena por fecha e id, no sólo por id: una importación antigua
no debe aparecer por encima de una reasignación más reciente. El nombre del autor de
la importación se resuelve con la cuenta actual y su correo anterior se conserva por
separado. No se registran movimientos inventados para leads sin antecedentes.

Validación: 12 pruebas de consolidación, 13 de asignaciones y 8 de catálogo
aprobadas. También aprobaron auditoría (62), validaciones (33), datos demo (17),
oportunidades (15), visitas (15), matching (13) y compilación del frontend.
La prueba de auditoría utilizaba la fecha local para consultar registros UTC;
se fijó una fecha de muestra para que no dependa del huso horario de la ejecución.
No se cambió la interpretación UTC del filtro de la aplicación.

Jira consultado: 25 historias finalizadas y cuatro sprints cerrados. Las cuatro
épicas siguen Por hacer. Esta corrección complementa SCRUM-31, sin modificar fechas
ni reabrir sprints cerrados. Pendiente de producto: evaluación sistemática de la IA;
no se realizaron llamadas pagadas ni se inventaron resultados de calidad.

Los apartados siguientes conservan el registro previo a esta actualización; sus
pendientes de commit y cierre de Jira ya fueron atendidos en el avance anterior.

## Avance en curso: responsables de leads

La consulta de Jira de esta sesión mantiene SCRUM-30 y SCRUM-31 en «Por hacer».
El Sprint 4 figura como futuro, aunque sus fechas previstas ya pasaron. No se
modificaron estados, fechas ni sprints. Antes de iniciarlo o cerrarlo hay que
resolver esa diferencia con el equipo, sin cambiar el historial para hacerlo coincidir.

| Historia | Cambio local | Comprobación | Pendiente para terminar |
| --- | --- | --- | --- |
| SCRUM-30 · Asignación de leads | Administración puede cambiar el responsable por otro usuario activo; listado y ficha muestran el responsable actual. | Pruebas de API aprobadas; Bryan confirmó la comprobación manual el 15/10/2026. | Guardar cambios en Git cuando se autorice y actualizar el estado de Jira con el resultado real. |
| SCRUM-31 · Historial de asignaciones | Registra responsable anterior, nuevo, autor y fecha; consulta paginada desde la ficha. | Pruebas de API aprobadas; historial y Actividad compartidos en el chat, y permisos de ejecutivo confirmados el 15/10/2026. | Incorporar las evidencias a la documentación de entrega y actualizar Jira cuando se autorice. |

Se permite asignar a administradores porque ya pueden crear y trabajar leads.
Los ejecutivos consultan, pero no reasignan. No se añadieron filtros de cartera,
gestión de cuentas ni reasignación automática de tareas, visitas u oportunidades.
Los movimientos antiguos no se reconstruyen ni reciben fechas inventadas.

### Verificación local realizada

Se utilizaron datos ficticios y SQLite, sin modificar Supabase ni llamar al proveedor de IA.

| Prueba | Resultado |
| --- | --- |
| `prueba_asignaciones.py` | 12 pruebas aprobadas |
| `prueba_catalogo.py` | 8 pruebas aprobadas |
| `prueba_auditoria.py` | 62 verificaciones aprobadas |
| `prueba_validaciones.py` | 33 verificaciones aprobadas |
| `prueba_datos_demo.py` | 17 verificaciones aprobadas |
| `prueba_oportunidades.py` | 15 verificaciones aprobadas |
| `prueba_visitas.py` | 15 verificaciones aprobadas |
| `prueba_matching.py` | 13 verificaciones aprobadas |
| Frontend | Compilación de producción aprobada |

La comprobación de ficha desactualizada no es una prueba de concurrencia real en
PostgreSQL. El bloqueo entre peticiones simultáneas todavía no se ha probado allí.

También se comprobó en navegador, con una base temporal, que administración puede
reasignar un lead y consultar el movimiento con autor y fecha. El listado y la ficha
mostraron al nuevo responsable. Los permisos del ejecutivo se verificaron por API
y posteriormente Bryan confirmó su comprobación manual. Evidencia local de administración:
`../outputs/qa-asignaciones/asignacion-administracion.png`.

### Validación manual comunicada por Bryan · 15/10/2026

- Compartió la salida de `migrar.py`: 48 de 48 instrucciones sin error, incluidas
  la tabla `asignaciones_lead` y su índice. No se inspeccionó directamente la
  conexión remota en esta comprobación; se conserva el resultado comunicado.
- Confirmó la reapertura de la ficha con el nuevo responsable y compartió el
  historial con responsable anterior, nuevo, autor y fecha.
- Compartió el registro de Actividad del mismo cambio de responsable.
- Confirmó con una cuenta de ejecutivo que puede consultar el historial de
  responsables, sin selector ni botón para reasignar, y sin acceso a Actividad.

La validación funcional manual prevista está completada según lo comunicado en el
chat. Pendiente: guardar los cambios en Git con autorización, conservar capturas
para la entrega y actualizar Jira y documentos con su fecha real. No se atribuye
esta validación a Amaro ni se registra como una reunión de Review.

## Control de documentos

El inventario toma como base la revisión previa del Drive y el historial de este
chat. No significa que los archivos del Drive se hayan editado en esta sesión.
Se conservan los registros de fechas anteriores; los avances nuevos se registran
con su fecha real, sin atribuir pruebas u opiniones a Bryan o Amaro sin confirmación.

| Documento | Situación y próxima actualización |
| --- | --- |
| Análisis del caso | Existente. Revisar solo si cambia el problema o alcance. |
| Squad y responsabilidades | Existente. Actualizar si cambia el reparto real. |
| Mapa mental | Existente. Sin cambio por esta implementación. |
| Mapa de actores | Existente. Mantiene administrador y ejecutivo. |
| Visión del proyecto + cuatro pilares | Existente. No añadir automatizaciones fuera del alcance acordado. |
| Épicas | Existen en Jira; pendiente conservar la evidencia en la carpeta compartida según el último inventario. |
| Historias con criterios y estimación | Existen en Jira; pendiente conservar la evidencia completa en la carpeta. El backlog resumido no sustituye los criterios. |
| Impact Mapping | Existente. Revisar si cambian los resultados o comportamientos esperados. |
| Product Backlog priorizado | Existente. Actualizar estados y fecha tras la validación; no dar por hechas SCRUM-30/31 solo por tener código local. |
| User Story Mapping | Existente. Corregir estados antiguos del catálogo y el rótulo MVP entre recorridos; revisar si se incorporan las dos historias nuevas. |
| Retrospectiva del proyecto | Existente. Añadir aprendizajes cuando haya resultados nuevos; no convertirla en cierre definitivo. |
| Sprint Planning | Existente para 1–4. Mantener la distinción entre reconstrucción histórica y planificación actual. |
| Sprint Backlog | Existe en el libro consolidado según la última revisión. Actualizar el trabajo real del Sprint 4 sin confundir tareas con estado de historia. |
| Scrumboard | Existente para 1–4. Actualizar captura o exportación cuando cambien los estados. |
| Burndown | Existente para 1–3, con límites de reconstrucción. No inventar valores diarios ni un burndown del Sprint 4 no iniciado. |
| Daily Meeting | Existente. Registrar hechos reales; esta sesión de desarrollo no acredita que se celebró una Daily. |
| Registro de impedimentos | Existente. Resolver la contradicción entre «Por confirmar» y fecha de cierre en el registro de auditoría, según comprobación real. |
| Release | Existente. Corregir la referencia a código que quedó sin identificar. Preparar otra versión cuando se integre este avance, no antes. |
| Review | Existente para 1–3. Preparar la revisión del Sprint 4 con una demostración real y comentarios confirmados. |
| Retrospective de sprints | Existente para 1–3. La siguiente depende de la revisión real del trabajo. |

También habrá que actualizar el modelo relacional con `asignaciones_lead` después
de aplicar y comprobar la migración. Revisar el avance del informe 2.4 y la Gantt
contra las fechas reales; no modificar los informes de Fase 1 para aparentar que
el desarrollo nuevo ya existía. Las evidencias de Fase 2 deben reflejar el entorno
que realmente se probó: local o compartido.

## Regla de cierre

Código local, pruebas locales, base compartida y estado de Jira se registran por
separado. Un commit o un push tampoco equivalen a un despliegue ni a aceptación
del equipo. En esta sesión no se hizo commit, push, despliegue ni cambios en Jira.
