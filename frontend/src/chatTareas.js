export function duplicadoConfirmacion(error, revision) {
  if (error?.status !== 409 || error.codigo !== 'tarea_duplicada' ||
      !Number.isInteger(error.tareaId) || error.tareaId <= 0 ||
      !Number.isInteger(error.leadId) || error.leadId <= 0 ||
      error.leadId !== Number(revision?.lead_id)) return null;
  return { id: error.tareaId, leadId: error.leadId };
}

export function precioPropiedadChat(precio, moneda) {
  if (typeof precio !== 'number' || !Number.isFinite(precio) || precio < 0) return 'Precio sin registrar';
  const valor = precio.toLocaleString('es-CL', { useGrouping: true, maximumFractionDigits: moneda === 'CLP' ? 0 : 2 });
  return ['CLP', 'UF'].includes(moneda) ? `${valor} ${moneda}` : `${valor} · moneda sin registrar`;
}

export function prepararRevisionChat(respuesta) {
  if (!respuesta || !Number.isInteger(respuesta.id) || respuesta.id <= 0 ||
      !Array.isArray(respuesta.clientes) ||
      !['pendiente', 'aclarar', 'respuesta'].includes(respuesta.estado) ||
      respuesta.clientes.some(c => !Number.isInteger(c.id) || c.id <= 0 || typeof c.nombre !== 'string') ||
      typeof respuesta.titulo !== 'string' || typeof respuesta.descripcion !== 'string' ||
      typeof respuesta.mensaje !== 'string' || !respuesta.mensaje.trim()) {
    throw new Error('El servidor devolvió una propuesta inválida. No se creó una tarea.');
  }
  const unico = respuesta.clientes.length === 1 ? respuesta.clientes[0] : null;
  return {
    lead_id: unico && unico.estado !== 'Cerrado' ? String(unico.id) : '',
    titulo: respuesta.titulo, descripcion: respuesta.descripcion,
    prioridad: 'Media', fecha_limite: '',
  };
}

export function confirmacionChat(propuesta, revision) {
  const leadId = Number(revision.lead_id);
  if (propuesta?.estado !== 'pendiente' || !propuesta.clientes.some(c => c.id === leadId && c.estado !== 'Cerrado')) {
    throw new Error('Selecciona al lead correcto antes de confirmar.');
  }
  const titulo = revision.titulo.trim();
  const descripcion = revision.descripcion.trim();
  if (!titulo || titulo.length > 200 || descripcion.length > 5000 || !['Alta', 'Media', 'Baja'].includes(revision.prioridad)) {
    throw new Error('Revisa el título, la descripción y la prioridad.');
  }
  return { lead_id: leadId, titulo, descripcion: descripcion || null,
    prioridad: revision.prioridad, fecha_limite: revision.fecha_limite || null };
}
