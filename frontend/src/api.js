/**
 * Capa de comunicación con la API.
 *
 * Todas las peticiones pasan por pedir(), que se encarga de adjuntar el token de
 * sesión y de reaccionar igual ante un 401. Centralizarlo evita que a alguna
 * llamada se le olvide la autenticación.
 */

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const BASE = `${API_URL}/api`;
const CLAVE_TOKEN = 'crm_token';

// Callback que App registra para saber cuándo la sesión dejó de ser válida
let alExpirarSesion = null;

/** Permite a la aplicación reaccionar cuando el backend rechaza el token. */
export function registrarCierreDeSesion(callback) {
  alExpirarSesion = callback;
}

export function obtenerToken() {
  return localStorage.getItem(CLAVE_TOKEN);
}

export function guardarToken(token) {
  localStorage.setItem(CLAVE_TOKEN, token);
}

export function borrarToken() {
  localStorage.removeItem(CLAVE_TOKEN);
}

/**
 * Ejecuta una petición contra la API.
 *
 * @param ruta        camino relativo a /api, por ejemplo "/leads"
 * @param metodo      verbo HTTP
 * @param cuerpo      objeto que se envía como JSON (opcional)
 * @param mensajeError texto a mostrar si el backend no da un detalle propio
 * @param requiereToken false solo para el login, que se llama sin sesión
 */
async function pedir(ruta, { metodo = 'GET', cuerpo, mensajeError = 'Error de comunicación con el servidor', requiereToken = true } = {}) {
  const cabeceras = {};
  if (cuerpo !== undefined) {
    cabeceras['Content-Type'] = 'application/json';
  }

  const token = obtenerToken();
  if (requiereToken && token) {
    cabeceras.Authorization = `Bearer ${token}`;
  }

  let respuesta;
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      method: metodo,
      headers: cabeceras,
      body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined,
    });
  } catch {
    // fetch solo lanza si no hubo respuesta: servidor caído, sin red o CORS.
    // Sin esto el usuario vería el "Failed to fetch" del navegador.
    throw new Error('No se pudo conectar con el servidor. Verifica que el backend esté corriendo.');
  }

  // Token ausente, inválido o expirado: se cierra la sesión en el frontend
  if (respuesta.status === 401 && requiereToken) {
    borrarToken();
    if (alExpirarSesion) alExpirarSesion();
    throw new Error('Tu sesión expiró. Vuelve a iniciar sesión.');
  }

  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => null);
    // FastAPI devuelve detail como texto en los errores propios, pero como
    // arreglo en los de validación, por eso solo se usa si es texto
    const detalle = typeof datos?.detail === 'string' ? datos.detail : null;
    throw new Error(detalle ?? mensajeError);
  }

  // Las respuestas 204 (borrados) no traen cuerpo
  if (respuesta.status === 204) return null;

  return respuesta.json();
}

/* ══════════════════ Sesión ══════════════════ */

/**
 * Valida credenciales contra el backend y guarda el token devuelto.
 * Retorna los datos del usuario autenticado.
 */
export async function iniciarSesion(email, password) {
  const datos = await pedir('/auth/login', {
    metodo: 'POST',
    cuerpo: { email, password },
    mensajeError: 'No se pudo iniciar sesión',
    requiereToken: false,
  });

  guardarToken(datos.access_token);
  return datos.usuario;
}

/** Devuelve el usuario dueño del token guardado. Falla si ya no es válido. */
export function obtenerPerfil() {
  return pedir('/auth/yo', { mensajeError: 'No se pudo validar la sesión' });
}

/* ══════════════════ Leads ══════════════════ */

export function obtenerLeads() {
  return pedir('/leads', { mensajeError: 'No se pudo cargar la lista de leads' });
}

export function crearLead(datos) {
  return pedir('/leads', {
    metodo: 'POST',
    cuerpo: datos,
    mensajeError: 'No se pudo guardar el lead',
  });
}

export function actualizarLead(id, datos) {
  return pedir(`/leads/${id}`, {
    metodo: 'PUT',
    cuerpo: datos,
    mensajeError: 'No se pudo actualizar el lead',
  });
}

export function eliminarLead(id) {
  return pedir(`/leads/${id}`, {
    metodo: 'DELETE',
    mensajeError: 'No se pudo eliminar el lead',
  });
}

/* ══════════════════ Propiedades ══════════════════ */

export function obtenerPropiedades() {
  return pedir('/propiedades', { mensajeError: 'No se pudo cargar el catálogo de propiedades' });
}

export function crearPropiedad(datos) {
  return pedir('/propiedades', {
    metodo: 'POST',
    cuerpo: datos,
    mensajeError: 'No se pudo guardar la propiedad',
  });
}

export function actualizarPropiedad(id, datos) {
  return pedir(`/propiedades/${id}`, {
    metodo: 'PUT',
    cuerpo: datos,
    mensajeError: 'No se pudo actualizar la propiedad',
  });
}

export function eliminarPropiedad(id) {
  return pedir(`/propiedades/${id}`, {
    metodo: 'DELETE',
    mensajeError: 'No se pudo eliminar la propiedad',
  });
}

/* ══════════════════ Interacciones ══════════════════ */

export function obtenerInteracciones(leadId) {
  return pedir(`/leads/${leadId}/interacciones`, {
    mensajeError: 'No se pudo cargar el historial de interacciones',
  });
}

export function crearInteraccion(leadId, datos) {
  return pedir(`/leads/${leadId}/interacciones`, {
    metodo: 'POST',
    cuerpo: datos,
    mensajeError: 'No se pudo registrar la interacción',
  });
}

/* ══════════════════ Tareas ══════════════════ */

export function obtenerTareas() {
  return pedir('/tareas', { mensajeError: 'No se pudo cargar la lista de tareas' });
}

export function crearTarea(datos) {
  return pedir('/tareas', {
    metodo: 'POST',
    cuerpo: datos,
    mensajeError: 'No se pudo guardar la tarea',
  });
}

export function actualizarTarea(id, datos) {
  return pedir(`/tareas/${id}`, {
    metodo: 'PUT',
    cuerpo: datos,
    mensajeError: 'No se pudo actualizar la tarea',
  });
}

export function eliminarTarea(id) {
  return pedir(`/tareas/${id}`, {
    metodo: 'DELETE',
    mensajeError: 'No se pudo eliminar la tarea',
  });
}

/* ══════════════════ Propiedades de interés ══════════════════ */

export function obtenerIntereses(leadId) {
  return pedir(`/leads/${leadId}/intereses`, {
    mensajeError: 'No se pudieron cargar las propiedades de interés',
  });
}

export function crearInteres(leadId, datos) {
  return pedir(`/leads/${leadId}/intereses`, {
    metodo: 'POST',
    cuerpo: datos,
    mensajeError: 'No se pudo registrar el interés',
  });
}

export function eliminarInteres(id) {
  return pedir(`/intereses/${id}`, {
    metodo: 'DELETE',
    mensajeError: 'No se pudo quitar el interés',
  });
}

/* ══════════════════ Análisis con IA ══════════════════ */

/** Indica si hay proveedor de IA configurado en el backend. */
export function obtenerEstadoIA() {
  return pedir('/ia/estado', { mensajeError: 'No se pudo consultar el estado del servicio de IA' });
}

/** Devuelve los análisis ya generados para un lead, del más reciente al más antiguo. */
export function obtenerAnalisis(leadId) {
  return pedir(`/leads/${leadId}/analisis`, {
    mensajeError: 'No se pudieron cargar los análisis del lead',
  });
}

/**
 * Pide al backend que genere un análisis del lead con el modelo de lenguaje.
 *
 * El tipo puede ser "resumen", que describe la situación del prospecto, o
 * "recomendacion", que propone la siguiente acción.
 *
 * Puede tardar varios segundos: el backend espera la respuesta del proveedor.
 */
export function generarAnalisis(leadId, tipo = 'resumen') {
  return pedir(`/leads/${leadId}/analisis?tipo=${tipo}`, {
    metodo: 'POST',
    mensajeError: 'No se pudo generar el análisis',
  });
}

/**
 * Consumo acumulado del agente de IA. Solo responde a usuarios con rol admin:
 * a un ejecutivo el backend le devuelve 403.
 */
export function obtenerConsumoIA() {
  return pedir('/ia/consumo', { mensajeError: 'No se pudo cargar el consumo del agente' });
}

/* ══════════════════ Auditoría ══════════════════ */

/**
 * Arma la cadena de consulta descartando los filtros vacíos.
 *
 * Hace falta porque un filtro en blanco enviado como parámetro no es lo mismo que
 * no enviarlo: el backend valida los valores de entidad y acción, y un texto vacío
 * lo haría responder 400.
 */
function comoConsulta(filtros) {
  const parametros = new URLSearchParams();

  Object.entries(filtros).forEach(([clave, valor]) => {
    if (valor !== '' && valor !== null && valor !== undefined) {
      parametros.set(clave, valor);
    }
  });

  return parametros.toString();
}

/**
 * Registro de auditoría paginado. Solo responde a usuarios con rol admin:
 * a un ejecutivo el backend le devuelve 403.
 *
 * Filtros aceptados: pagina, por_pagina, usuario_email, entidad, accion,
 * desde y hasta (YYYY-MM-DD) y busqueda.
 */
export function obtenerAuditoria(filtros = {}) {
  return pedir(`/auditoria?${comoConsulta(filtros)}`, {
    mensajeError: 'No se pudo cargar el registro de actividad',
  });
}

/** Valores que ofrecen los selectores de filtro: entidades, acciones y usuarios. */
export function obtenerFiltrosAuditoria() {
  return pedir('/auditoria/filtros', {
    mensajeError: 'No se pudieron cargar los filtros del registro',
  });
}
