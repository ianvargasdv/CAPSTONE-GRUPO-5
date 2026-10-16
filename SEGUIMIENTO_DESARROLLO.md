# Seguimiento del desarrollo

Actualizado: 15/10/2026. Este archivo es un control de trabajo, no un acta de reunión.

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
