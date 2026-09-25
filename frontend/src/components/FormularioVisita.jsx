import React, { useEffect, useMemo, useState } from 'react';

const ESTADOS = ['Programada', 'Confirmada', 'Realizada', 'Cancelada', 'No asistió'];

function aInputLocal(iso) {
  if (!iso) return '';
  const fecha = new Date(iso);
  const local = new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

const VACIO = {
  lead_id: '', propiedad_id: '', oportunidad_id: '', fecha_hora: '',
  duracion_minutos: 60, estado: 'Programada', modalidad: 'Presencial',
  punto_encuentro: '', resultado: '', motivo_cancelacion: '', proxima_accion: '',
};

function FormularioVisita({ alGuardar, visitaEditar, leads, propiedades, oportunidades, alCancelar }) {
  const [datos, setDatos] = useState(VACIO);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!visitaEditar) {
      setDatos(VACIO);
    } else {
      const editables = Object.fromEntries(
        Object.keys(VACIO).map((campo) => [campo, visitaEditar[campo] ?? VACIO[campo]])
      );
      editables.fecha_hora = aInputLocal(visitaEditar.fecha_hora);
      setDatos(editables);
    }
    setError(null);
  }, [visitaEditar]);

  const oportunidadesCompatibles = useMemo(() => oportunidades.filter((o) => (
    o.lead_id === Number(datos.lead_id)
    && (!o.propiedad_id || !datos.propiedad_id || o.propiedad_id === Number(datos.propiedad_id))
  )), [oportunidades, datos.lead_id, datos.propiedad_id]);

  const cambiar = (campo) => (evento) => setDatos((actuales) => ({
    ...actuales, [campo]: evento.target.value,
  }));

  const cambiarLead = (evento) => {
    const leadId = evento.target.value;
    setDatos((actuales) => ({
      ...actuales,
      lead_id: leadId,
      oportunidad_id: oportunidades.some((o) => (
        o.id === Number(actuales.oportunidad_id)
        && o.lead_id === Number(leadId)
        && (!o.propiedad_id || !actuales.propiedad_id
          || o.propiedad_id === Number(actuales.propiedad_id))
      )) ? actuales.oportunidad_id : '',
    }));
  };

  const cambiarPropiedad = (evento) => {
    const propiedadId = evento.target.value;
    const propiedad = propiedades.find((item) => item.id === Number(propiedadId));
    setDatos((actuales) => ({
      ...actuales,
      propiedad_id: propiedadId,
      punto_encuentro: actuales.punto_encuentro || propiedad?.direccion || '',
      oportunidad_id: oportunidades.some((o) => (
        o.id === Number(actuales.oportunidad_id)
        && o.lead_id === Number(actuales.lead_id)
        && (!o.propiedad_id || !propiedadId || o.propiedad_id === Number(propiedadId))
      ))
        ? actuales.oportunidad_id : '',
    }));
  };

  const manejarEnvio = async (evento) => {
    evento.preventDefault();
    if (!datos.lead_id || !datos.propiedad_id || !datos.fecha_hora) {
      setError('Lead, propiedad y fecha son obligatorios');
      return;
    }
    if (datos.estado === 'Realizada' && !datos.resultado.trim()) {
      setError('Registra el resultado de la visita');
      return;
    }
    if (datos.estado === 'Cancelada' && !datos.motivo_cancelacion.trim()) {
      setError('Indica el motivo de cancelación');
      return;
    }

    const payload = {
      ...datos,
      lead_id: Number(datos.lead_id),
      propiedad_id: Number(datos.propiedad_id),
      oportunidad_id: datos.oportunidad_id ? Number(datos.oportunidad_id) : null,
      fecha_hora: new Date(datos.fecha_hora).toISOString(),
      duracion_minutos: Number(datos.duracion_minutos),
      punto_encuentro: datos.punto_encuentro.trim() || null,
      resultado: datos.resultado.trim() || null,
      motivo_cancelacion: datos.motivo_cancelacion.trim() || null,
      proxima_accion: datos.proxima_accion.trim() || null,
    };

    try {
      setCargando(true);
      setError(null);
      await alGuardar(payload);
    } catch (err) {
      setError(err.message || 'No se pudo guardar la visita');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      {error && <div className="alert-error">{error}</div>}
      <p className="form-seccion-titulo">Participantes</p>
      <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="visita-lead">Lead</label>
          <select id="visita-lead" value={datos.lead_id} onChange={cambiarLead} disabled={cargando || Boolean(visitaEditar)}>
            <option value="">Selecciona un lead</option>
            {leads.map((lead) => <option key={lead.id} value={lead.id}>{lead.nombre}</option>)}
          </select>
        </div>
        <div className="form-group form-group-full">
          <label htmlFor="visita-propiedad">Propiedad</label>
          <select id="visita-propiedad" value={datos.propiedad_id} onChange={cambiarPropiedad} disabled={cargando}>
            <option value="">Selecciona una propiedad</option>
            {propiedades.map((propiedad) => <option key={propiedad.id} value={propiedad.id}>{propiedad.titulo}</option>)}
          </select>
        </div>
        <div className="form-group form-group-full">
          <label htmlFor="visita-oportunidad">Oportunidad relacionada</label>
          <select id="visita-oportunidad" value={datos.oportunidad_id || ''} onChange={cambiar('oportunidad_id')} disabled={cargando}>
            <option value="">Sin oportunidad asociada</option>
            {oportunidadesCompatibles.map((o) => <option key={o.id} value={o.id}>{o.tipo_operacion} · {o.etapa} · #{o.id}</option>)}
          </select>
        </div>
      </div>

      <p className="form-seccion-titulo">Horario</p>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="visita-fecha">Fecha y hora</label>
          <input id="visita-fecha" type="datetime-local" value={datos.fecha_hora} onChange={cambiar('fecha_hora')} disabled={cargando} />
        </div>
        <div className="form-group">
          <label htmlFor="visita-duracion">Duración</label>
          <select id="visita-duracion" value={datos.duracion_minutos} onChange={cambiar('duracion_minutos')} disabled={cargando}>
            {[30, 45, 60, 90, 120].map((minutos) => <option key={minutos} value={minutos}>{minutos} minutos</option>)}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="visita-estado">Estado</label>
          <select id="visita-estado" value={datos.estado} onChange={cambiar('estado')} disabled={cargando}>
            {ESTADOS.map((estado) => <option key={estado}>{estado}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="visita-modalidad">Modalidad</label>
          <select id="visita-modalidad" value={datos.modalidad} onChange={cambiar('modalidad')} disabled={cargando}><option>Presencial</option><option>Virtual</option></select>
        </div>
        <div className="form-group form-group-full">
          <label htmlFor="visita-punto">Punto de encuentro o enlace</label>
          <input id="visita-punto" value={datos.punto_encuentro || ''} onChange={cambiar('punto_encuentro')} disabled={cargando} placeholder="Dirección, conserjería o enlace de videollamada" />
        </div>
      </div>

      {datos.estado === 'Realizada' && <div className="form-group"><label htmlFor="visita-resultado">Resultado de la visita</label><textarea id="visita-resultado" className="form-textarea" rows="3" value={datos.resultado || ''} onChange={cambiar('resultado')} disabled={cargando} placeholder="Interés, objeciones y acuerdos" /></div>}
      {datos.estado === 'Cancelada' && <div className="form-group"><label htmlFor="visita-cancelacion">Motivo de cancelación</label><input id="visita-cancelacion" value={datos.motivo_cancelacion || ''} onChange={cambiar('motivo_cancelacion')} disabled={cargando} /></div>}
      <div className="form-group"><label htmlFor="visita-proxima">Próxima acción</label><input id="visita-proxima" value={datos.proxima_accion || ''} onChange={cambiar('proxima_accion')} disabled={cargando} placeholder="Enviar documentos, preparar oferta, reagendar..." /></div>

      <div className="form-actions">
        <button type="button" className="btn-secondary" onClick={alCancelar} disabled={cargando}>Cancelar</button>
        <button type="submit" className="btn-primary" disabled={cargando}>{cargando ? 'Guardando...' : visitaEditar ? 'Guardar cambios' : 'Agendar visita'}</button>
      </div>
    </form>
  );
}

export default FormularioVisita;
