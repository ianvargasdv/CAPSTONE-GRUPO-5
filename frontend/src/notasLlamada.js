/** Valida la propuesta recibida antes de ofrecer un texto para guardar. */
export function textoDePropuesta(propuesta) {
  const texto = (valor, maximo) => typeof valor === 'string' && valor.trim().length > 0 && valor.length <= maximo;
  if (!propuesta || !texto(propuesta.resumen, 1600)
    || !Array.isArray(propuesta.requisitos) || propuesta.requisitos.length > 8
    || !propuesta.requisitos.every((r) => texto(r, 600))
    || !(propuesta.proxima_accion === null || texto(propuesta.proxima_accion, 600))) {
    throw new Error('La propuesta no tiene el formato esperado. Conserva las notas y vuelve a intentarlo.');
  }
  const partes = [propuesta.resumen.trim()];
  if (propuesta.requisitos.length) partes.push(`Requisitos mencionados:\n${propuesta.requisitos.map((r) => `- ${r.trim()}`).join('\n')}`);
  if (propuesta.proxima_accion) partes.push(`Próxima acción propuesta:\n${propuesta.proxima_accion.trim()}`);
  const resultado = partes.join('\n\n');
  if (resultado.length > 5000) throw new Error('La propuesta es demasiado larga para el historial. Registra las notas manualmente.');
  return resultado;
}

export function validarRespuestaLlamada(respuesta, clienteId) {
  if (!respuesta?.analisis?.id || respuesta.analisis.lead_id !== clienteId
    || respuesta.analisis.tipo !== 'registro_llamada') {
    throw new Error('La propuesta no corresponde a este cliente. No se guardó ningún contacto.');
  }
  return textoDePropuesta(respuesta.propuesta);
}

export function textoDeAnalisisLlamada(salida) {
  try {
    return textoDePropuesta(JSON.parse(salida));
  } catch {
    return 'No se pudo interpretar la propuesta guardada. Revisa la salida original.';
  }
}
