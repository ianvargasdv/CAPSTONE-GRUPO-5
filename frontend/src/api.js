const API_URL = 'http://localhost:8000/api';

/**
 * Obtiene el listado completo de leads desde el backend.
 */
export async function obtenerLeads() {
  const respuesta = await fetch(`${API_URL}/leads`);
  if (!respuesta.ok) {
    throw new Error('No se pudo cargar la lista de leads');
  }
  return await respuesta.json();
}

/**
 * Envíos los datos de un nuevo lead para registrarlo en el backend.
 */
export async function crearLead(datosLead) {
  const respuesta = await fetch(`${API_URL}/leads`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datosLead),
  });

  if (!respuesta.ok) {
    throw new Error('No se pudo guardar el lead');
  }
  return await respuesta.json();
}

/**
 * Obtiene el catálogo completo de propiedades desde el backend.
 */
export async function obtenerPropiedades() {
  const respuesta = await fetch(`${API_URL}/propiedades`);
  if (!respuesta.ok) {
    throw new Error('No se pudo cargar el catálogo de propiedades');
  }
  return await respuesta.json();
}

/**
 * Envía los datos de una nueva propiedad para registrarla en el backend.
 */
export async function crearPropiedad(datosPropiedad) {
  const respuesta = await fetch(`${API_URL}/propiedades`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datosPropiedad),
  });

  if (!respuesta.ok) {
    throw new Error('No se pudo guardar la propiedad');
  }
  return await respuesta.json();
}

/**
 * Actualiza los campos de un lead existente.
 * Recibe el ID del lead y un objeto con los campos a modificar.
 */
export async function actualizarLead(id, datosLead) {
  const respuesta = await fetch(`${API_URL}/leads/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datosLead),
  });

  if (!respuesta.ok) {
    throw new Error('No se pudo actualizar el lead');
  }
  return await respuesta.json();
}

/**
 * Elimina un lead por su ID.
 */
export async function eliminarLead(id) {
  const respuesta = await fetch(`${API_URL}/leads/${id}`, {
    method: 'DELETE',
  });

  if (!respuesta.ok) {
    throw new Error('No se pudo eliminar el lead');
  }
}

/**
 * Actualiza los campos de una propiedad existente.
 * Recibe el ID de la propiedad y un objeto con los campos a modificar.
 */
export async function actualizarPropiedad(id, datosPropiedad) {
  const respuesta = await fetch(`${API_URL}/propiedades/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datosPropiedad),
  });

  if (!respuesta.ok) {
    throw new Error('No se pudo actualizar la propiedad');
  }
  return await respuesta.json();
}

/**
 * Elimina una propiedad por su ID.
 */
export async function eliminarPropiedad(id) {
  const respuesta = await fetch(`${API_URL}/propiedades/${id}`, {
    method: 'DELETE',
  });

  if (!respuesta.ok) {
    throw new Error('No se pudo eliminar la propiedad');
  }
}

