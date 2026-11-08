# Roadmap del CRM inmobiliario

Este roadmap ordena el desarrollo por valor operativo. Cada módulo debe poder
probarse y demostrarse por separado antes de pasar al siguiente.

## Estado actual · 8/11/2026

El sprint 6 Seguimiento con IA está activo del 2 al 9/11. Sus cinco actividades
finalizaron el 7/11, con 28 puntos completados:

| Referencia | Funcionalidad | Puntos |
|---|---|---:|
| SCRUM-39 | Preparar notas de llamada con IA | 8 |
| SCRUM-40 | Consultar cartera y filtrar por responsable | 5 |
| SCRUM-43 | Consultar el CRM y preparar tareas con Mobilita | 8 |
| SCRUM-44 | Organizar listados, fichas y vista móvil | 5 |
| SCRUM-45 | Renovar el escenario ficticio de demostración | 2 |

La línea base fue de 13 puntos. SCRUM-43 añadió ocho el 2/11 y SCRUM-44 y
SCRUM-45 añadieron siete el 4/11. Se conservan las fechas del desarrollo previo
de SCRUM-39 y SCRUM-40, registrado el 29/10.

SCRUM-41 está finalizada, con cinco puntos y sin sprint asignado. Bryan aceptó
la revisión asistida de once respuestas originales y dos posteriores al ajuste:
diez originales aprobadas, una rechazada y las dos posteriores aprobadas.
SCRUM-42 conserva el defecto original y su corrección, con dos puntos y sin sprint.
Estas actividades no aumentan los 28 puntos del sprint 6.

El código del avance está publicado en `510e439` y la revisión aceptada en
`7ae691a`. Hasta iniciar el próximo sprint no se modificará el backend.
Quedan preparar la grabación local y registrar el cierre del sprint 6.
Las ampliaciones siguientes se planificarán antes de implementarlas.

Los apartados fechados de octubre conservan el estado de sus entregas. Sus
pendientes son históricos; el estado actual se resume en este apartado.

## Criterio común de terminado

- Backend, interfaz y permisos coherentes.
- Validaciones y mensajes de error comprensibles.
- Pruebas de casos válidos, inválidos y límites.
- Auditoría para toda escritura relevante.
- README y migración actualizados cuando cambie el modelo de datos.

## Módulos

### Presentación y UX · 16/10/2026

**Estado: implementado y verificado en los flujos principales; normalización aplicada.**

- Nombres naturales sin los marcadores heredados, manteniendo el origen ficticio.
- Filtros comerciales y de tareas vencidas, búsqueda sin tildes y limpieza de filtros.
- Formularios con campos obligatorios, detalles opcionales plegables y navegación por teclado.
- Acciones de fila visibles y tablas con desplazamiento interno en móvil.
- Revisión como administrador y ejecutivo en una base temporal, sin cambiar permisos.
- 235 comprobaciones técnicas aprobadas y compilación correcta.
- No implica una revisión exhaustiva de todos los dispositivos o una puesta en producción.

### Calidad y datos de prueba · 16/10/2026

**Estado: código local probado; escenario ficticio aplicado y verificado en la base.**

- Preguntas que contemplan requisitos pendientes en notas o tareas.
- Contexto con fecha de referencia, moneda y estado de propiedades de interés.
- Ocho respuestas reales revisadas contra criterios concretos, con límites registrados.
- Escenario nuevo: 24 clientes y 18 propiedades, sin Demo en nombres/títulos pero
  identificados como ficticios; conserva datos existentes y no duplica al repetir.
- 224 comprobaciones técnicas aprobadas y frontend compilado.
- Resultados en `backend/evidencias/`; no equivale a garantía de ausencia de errores.
- Pendiente registrar las ampliaciones en Jira y actualizar los documentos de entrega.

### Ampliación del asistente · 15/10/2026

**Estado: implementada y verificada con una muestra del proveedor real.**

- Borrador de seguimiento editable y copiable, sin envío automático.
- Preguntas para completar los datos comerciales faltantes, sin modificar el lead.
- Dieciséis pruebas simuladas aprobadas y frontend compilado.
- Credencial rechazada en el primer intento; resuelto tras reemplazarla localmente.
- Cuatro respuestas reales revisadas, con dos perfiles ficticios: borrador y preguntas
  para cada uno. Sin escrituras comerciales ni envío de mensajes. La muestra es
  inicial y no sustituye la revisión humana o una evaluación más amplia.
- Las nuevas historias SCRUM-32 y SCRUM-33 no se incorporan retrospectivamente a los
  cuatro sprints cerrados. No tienen estimación acordada ni sprint asignado.
- WhatsApp queda como propuesta; requiere cuenta, número, credenciales, recepción
  verificada de eventos y validación del flujo antes de poder considerarlo integrado.

### Seguimiento desde una recomendación · 15/10/2026

**Estado: implementado y comprobado en entorno temporal; pendiente de prueba del equipo en el CRM habitual.**

- Usa una recomendación existente sin una nueva generación de IA.
- Consulta tareas pendientes antes de abrir el formulario; no continúa si falla la consulta.
- El usuario revisa, edita y guarda mediante la creación normal de tareas y auditoría.
- No asigna una fecha supuesta ni ejecuta contactos. Cancelar no crea registros.
- Siete pruebas del preparador, 111 comprobaciones existentes y compilación aprobadas.
- Revisión visual con SQLite y recomendación simulada: cancelación sin creación,
  guardado de una tarea editada, vínculo al lead y un registro de creación en Actividad.
- Falta documentarlo en Jira y en los archivos de entrega después de la prueba del equipo.

### M0. Entorno reproducible

**Estado: completado.**

- Dependencias bloqueadas para Python y Node.
- Plantillas `.env` completas y sin secretos.
- Instrucciones verificadas para levantar frontend y backend.

### M1. Integridad de datos

**Estado: completado.**

- Estados y categorías validados en la API.
- Límites de texto, precios, fechas, correo y teléfono.
- Prevención de leads duplicados por correo.
- Errores de validación legibles en el frontend.

### M2. Perfil 360 del lead

**Estado: completado y publicado.**

- Origen comercial y ejecutivo responsable.
- Compra o arriendo, presupuesto y moneda.
- Comunas, tipo de propiedad, dormitorios y requisitos.
- Plazo de decisión y estado del financiamiento.
- Próxima acción visible junto al historial.

### M3. Oportunidades y pipeline

**Estado: completado y publicado.**

- Separar la persona del negocio comercial.
- Relacionar lead, propiedad, ejecutivo y operación.
- Etapas configuradas para contacto, visita, oferta y negociación.
- Negocio ganado o perdido con motivo y fecha de cierre.
- Vista Kanban y vista tabla.

### M4. Agenda de visitas

**Estado: completado y publicado.**

- Visita asociada a lead, propiedad y ejecutivo.
- Fecha, hora, confirmación, resultado y cancelación.
- Registro posterior de objeciones y siguiente acción.
- Agenda diaria y semanal.

### M5. Matching lead–propiedad

**Estado: completado y probado.**

- Coincidencia por presupuesto, comuna, tipo y dormitorios.
- Explicación de por qué una propiedad coincide o no.
- La consulta muestra las coincidencias con el catálogo disponible. Las alertas
  automáticas por nuevas propiedades quedan como una ampliación futura.
- La regla base es determinista; la IA solo resume o explica.

### M6. Catálogo inmobiliario completo

**Estado: implementado y comprobado en el CRM con PostgreSQL de Supabase.**

- Código interno, venta/arriendo, moneda y estado de publicación.
- Superficie, dormitorios, baños, estacionamiento y bodega.
- Gastos comunes, disponibilidad, características y fotografías.
- Datos del propietario/captador con permisos apropiados.

La migración del catálogo se aplicó y comprobó durante las pruebas. El 7/11 se
revisaron el panel de la ficha y los datos ficticios de las 25 propiedades.
Las fotografías se registran por enlace y el captador como texto. El MVP no
almacena archivos de imagen; la asignación de leads corresponde a M7.

### M7. Equipo y asignación de cartera

**Estado: SCRUM-30 y SCRUM-31 implementadas y finalizadas en Jira; validación manual confirmada el 15/10/2026. Historial anterior consolidado y verificado en Supabase.**

Implementado: reasignación de leads por administración e historial paginado con
responsable anterior, nuevo responsable, autor y fecha. La API rechaza usuarios
inactivos, modificaciones sin permisos y cambios desde una ficha desactualizada.
Esto no completa todo M7. Se mantienen pendientes:

- Reasignación coordinada de tareas y oportunidades junto con el lead.
- Extender las vistas de cartera a visitas y oportunidades. El listado de
  clientes cuenta con Mi cartera y filtros administrativos en SCRUM-40; Tareas
  limita al ejecutivo a los leads que tiene asignados.
- Gestión de activación/desactivación de usuarios desde la interfaz.

### M8. Automatizaciones y notificaciones

Propuestas para un sprint posterior; no forman parte del alcance terminado.

- Crear próxima tarea al cambiar de etapa.
- Alertas por tareas vencidas, leads sin contacto y visitas próximas.
- Reglas configurables, sin envíos automáticos irreversibles por defecto.

### M9. Reportería comercial

Propuestas para ampliar los indicadores actuales de Inicio y Negocios.

- Tiempo hasta primer contacto y leads sin próxima acción.
- Conversión entre etapas, tasa de cierre y ciclo promedio.
- Valor del pipeline, comisión estimada y motivos de pérdida.
- Antigüedad del inventario y rendimiento por origen/ejecutivo.

### M10. Comunicaciones

Mobilita ya funciona como asistente dentro del CRM. La mensajería externa y
las capacidades siguientes requieren planificación e integración adicionales.

- Acciones rápidas para llamada, correo y WhatsApp.
- Copiloto que redacta respuestas y plantillas usando solo información registrada.
- Revisión humana obligatoria antes de enviar en la primera versión.
- Registro automático o asistido de la comunicación en el historial.
- Consentimiento, plantillas aprobadas, límites de frecuencia y baja de mensajes.
- Derivación a un ejecutivo ante visita, negociación, reclamo o baja confianza.
- Integrar un canal de atención para clientes, distinto del chat interno Mobilita;
  WhatsApp Business queda como posibilidad posterior.

### M11. Documentos y cierre

Propuestas de gestión documental comercial, distintas de los informes académicos.

- Archivos asociados a oportunidad y propiedad.
- Checklist documental por operación.
- Control de versiones y permisos.
- Integración de firma electrónica como etapa posterior.

### M12. Producción y seguridad

Trabajo futuro para una publicación estable. El MVP actual se demuestra localmente.

- Cookies seguras o estrategia equivalente para sesiones.
- Límite de intentos de acceso y recuperación de contraseña.
- Ampliar las migraciones y copias de seguridad para operación en producción;
  CORS ya se configura mediante `CORS_ORIGINS`.
- Monitoreo, paginación desde el servidor para los listados que todavía reciben
  el conjunto completo y política de retención de auditoría.

## Orden recomendado para las próximas demostraciones

1. M1 Integridad de datos.
2. M2 Perfil 360 del lead.
3. M3 Oportunidades y pipeline.
4. M4 Agenda de visitas.
5. M5 Matching lead–propiedad.
