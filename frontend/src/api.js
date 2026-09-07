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
