# Roadmap del CRM inmobiliario

Este roadmap ordena el desarrollo por valor operativo. Cada módulo debe poder
probarse y demostrarse por separado antes de pasar al siguiente.

## Criterio común de terminado

- Backend, interfaz y permisos coherentes.
- Validaciones y mensajes de error comprensibles.
- Pruebas de casos válidos, inválidos y límites.
- Auditoría para toda escritura relevante.
- README y migración actualizados cuando cambie el modelo de datos.

## Módulos

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

**Estado: implementado y migrado; pendiente de prueba visual del usuario y commit.**

- Origen comercial y ejecutivo responsable.
- Compra o arriendo, presupuesto y moneda.
- Comunas, tipo de propiedad, dormitorios y requisitos.
- Plazo de decisión y estado del financiamiento.
- Próxima acción visible junto al historial.

### M3. Oportunidades y pipeline

- Separar la persona del negocio comercial.
- Relacionar lead, propiedad, ejecutivo y operación.
- Etapas configuradas para contacto, visita, oferta y negociación.
- Negocio ganado o perdido con motivo y fecha de cierre.
- Vista Kanban y vista tabla.

### M4. Agenda de visitas

- Visita asociada a lead, propiedad y ejecutivo.
- Fecha, hora, confirmación, resultado y cancelación.
- Registro posterior de objeciones y siguiente acción.
- Agenda diaria y semanal.

### M5. Matching lead–propiedad

- Coincidencia por presupuesto, comuna, tipo y dormitorios.
- Explicación de por qué una propiedad coincide o no.
- Alertas cuando ingresa una propiedad compatible.
- La regla base es determinista; la IA solo resume o explica.

### M6. Catálogo inmobiliario completo

- Código interno, venta/arriendo, moneda y estado de publicación.
- Superficie, dormitorios, baños, estacionamiento y bodega.
- Gastos comunes, disponibilidad, características y fotografías.
- Datos del propietario/captador con permisos apropiados.

### M7. Equipo y asignación de cartera

- Leads, tareas y oportunidades asignados a un ejecutivo.
- Vista personal y vista de equipo para administradores.
- Reasignación auditada y usuarios activables/desactivables.

### M8. Automatizaciones y notificaciones

- Crear próxima tarea al cambiar de etapa.
- Alertas por tareas vencidas, leads sin contacto y visitas próximas.
- Reglas configurables, sin envíos automáticos irreversibles por defecto.

### M9. Reportería comercial

- Tiempo hasta primer contacto y leads sin próxima acción.
- Conversión entre etapas, tasa de cierre y ciclo promedio.
- Valor del pipeline, comisión estimada y motivos de pérdida.
- Antigüedad del inventario y rendimiento por origen/ejecutivo.

### M10. Comunicaciones

- Acciones rápidas para llamada, correo y WhatsApp.
- Copiloto que redacta respuestas y plantillas usando solo información registrada.
- Revisión humana obligatoria antes de enviar en la primera versión.
- Registro automático o asistido de la comunicación en el historial.
- Consentimiento, plantillas aprobadas, límites de frecuencia y baja de mensajes.
- Derivación a un ejecutivo ante visita, negociación, reclamo o baja confianza.
- Chatbot web como canal inicial; WhatsApp Business como integración posterior.

### M11. Documentos y cierre

- Archivos asociados a oportunidad y propiedad.
- Checklist documental por operación.
- Control de versiones y permisos.
- Integración de firma electrónica como etapa posterior.

### M12. Producción y seguridad

- Cookies seguras o estrategia equivalente para sesiones.
- Límite de intentos de acceso y recuperación de contraseña.
- CORS configurable, migraciones versionadas y copias de seguridad.
- Monitoreo, paginación general y política de retención de auditoría.

## Orden recomendado para las próximas demostraciones

1. M1 Integridad de datos.
2. M2 Perfil 360 del lead.
3. M3 Oportunidades y pipeline.
4. M4 Agenda de visitas.
5. M5 Matching lead–propiedad.
