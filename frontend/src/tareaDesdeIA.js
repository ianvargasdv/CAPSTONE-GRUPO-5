/** Prepara datos locales; nunca guarda ni interpreta el texto como una orden. */
export function prepararTareaDesdeIA(lead, analisis) {
  if (!Number.isInteger(lead?.id) || lead.id <= 0 || lead.estado === 'Cerrado') {
    throw new Error('Abre un lead activo para preparar el seguimiento.');
  }
  if (analisis?.tipo !== 'recomendacion' || analisis.lead_id !== lead.id ||
      !Number.isInteger(analisis.id) || analisis.id <= 0 ||
      typeof analisis.salida !== 'string' || !analisis.salida.trim() || analisis.salida.length > 4000) {
    throw new Error('No hay una recomendación válida para este lead.');
  }
  return {
    titulo: `Seguimiento de ${lead.nombre || 'lead'}`.slice(0, 200),
    descripcion: `Propuesta basada en la recomendación IA #${analisis.id}. Revisar antes de guardar.\n\n${analisis.salida.trim()}`,
    lead_id: lead.id,
    estado: 'Pendiente',
    prioridad: 'Media',
    fecha_limite: null,
  };
}

export function pendientesDelLead(tareas, leadId) {
  return tareas.filter((t) => t.lead_id === leadId && t.estado !== 'Completada');
}

export function seleccionarTareaPendiente(tareas, leadId, tareaId) {
  const tarea = pendientesDelLead(tareas, leadId).find((t) => t.id === tareaId);
  if (!tarea) throw new Error('La tarea ya no está disponible entre los pendientes de este lead.');
  // Abrir la tarea no debe reemplazar sus detalles con la propuesta del modelo.
  return { ...tarea };
}
