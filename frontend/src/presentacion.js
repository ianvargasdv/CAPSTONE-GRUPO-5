export function textoBusqueda(valor) {
  return String(valor ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es').trim();
}

export function coincideBusqueda(termino, ...valores) {
  const consulta = textoBusqueda(termino);
  return !consulta || valores.some((valor) => textoBusqueda(valor).includes(consulta));
}

export function fechaLocalISO(fecha = new Date()) {
  return `${fecha.getFullYear()}-${String(fecha.getMonth()+1).padStart(2,'0')}-${String(fecha.getDate()).padStart(2,'0')}`;
}

export function tareaVencida(tarea, hoy = fechaLocalISO()) {
  return tarea.estado !== 'Completada' && /^\d{4}-\d{2}-\d{2}$/.test(tarea.fecha_limite || '') && tarea.fecha_limite < hoy;
}

export function filtrarCatalogo(propiedades, {busqueda='', tipo='Todos', estado='Todos', operacion='Todas'} = {}) {
  return propiedades.filter((p) => coincideBusqueda(busqueda,p.titulo,p.direccion,p.comuna,p.codigo_interno) &&
    (tipo==='Todos' || p.tipo===tipo) && (estado==='Todos' || p.estado===estado) &&
    (operacion==='Todas' || p.tipo_operacion===operacion));
}
