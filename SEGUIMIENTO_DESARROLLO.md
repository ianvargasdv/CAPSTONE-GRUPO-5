# Seguimiento del desarrollo

Actualizado: 23/10/2026. Este archivo es un control de trabajo, no un acta de reunión.

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
