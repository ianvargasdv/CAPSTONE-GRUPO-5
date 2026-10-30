import { coincideBusqueda } from './presentacion.js';

export function parametrosCartera(seleccion, usuario) {
  if (!Number.isSafeInteger(usuario?.id) || usuario.id <= 0) throw new Error('La sesión no permite identificar tu cartera.');
  if (seleccion === 'todos') return {};
  // La identidad se resuelve en el servidor: no se envía un id elegido por el cliente.
  if (seleccion === 'mia') return { cartera: 'mia' };
  if (usuario.rol !== 'admin') throw new Error('Sólo administración puede seleccionar otro responsable.');
  if (seleccion === 'sin_asignar') return { sin_asignar: true };
  if (typeof seleccion === 'string' && /^responsable:[1-9]\d*$/.test(seleccion)) {
    const id = Number(seleccion.slice('responsable:'.length));
    if (Number.isSafeInteger(id)) return { ejecutivo_id: id };
  }
  throw new Error('Selecciona una cartera válida.');
}

export function filtrarClientes(leads, busqueda = '', estado = 'Todos', categoria = 'Todas') {
  return leads.filter((lead) =>
    coincideBusqueda(busqueda, lead.nombre, lead.email, lead.telefono, lead.comunas_interes, lead.ejecutivo_nombre)
    && (estado === 'Todos' || lead.estado === estado)
    && (categoria === 'Todas' || lead.categoria === categoria));
}
