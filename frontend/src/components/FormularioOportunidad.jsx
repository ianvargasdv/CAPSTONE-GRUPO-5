import React, { useEffect, useState } from 'react';

const ETAPAS = ['Contacto', 'Visita', 'Oferta', 'Negociación', 'Ganada', 'Perdida'];
const PROBABILIDAD = { Contacto: 10, Visita: 30, Oferta: 60, Negociación: 80, Ganada: 100, Perdida: 0 };

const VACIO = {
  lead_id: '', propiedad_id: '', tipo_operacion: '', etapa: 'Contacto',
  valor_estimado: '', moneda: '', probabilidad: 10, fecha_cierre_estimada: '',
  motivo_cierre: '', notas: '',
};

function FormularioOportunidad({ alGuardar, oportunidadEditar, leads, propiedades, alCancelar }) {
  const [datos, setDatos] = useState(VACIO);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!oportunidadEditar) {
      setDatos(VACIO);
    } else {
      setDatos(Object.fromEntries(
        Object.keys(VACIO).map((campo) => [campo, oportunidadEditar[campo] ?? VACIO[campo]])
      ));
    }
    setError(null);
  }, [oportunidadEditar]);

  const cambiar = (campo) => (evento) => {
    const valor = evento.target.value;
    setDatos((actuales) => ({ ...actuales, [campo]: valor }));
  };

  const cambiarLead = (evento) => {
    const leadId = evento.target.value;
    const lead = leads.find((item) => item.id === Number(leadId));
    setDatos((actuales) => ({
      ...actuales,
      lead_id: leadId,
      tipo_operacion: lead?.tipo_operacion || actuales.tipo_operacion,
    }));
  };

  const cambiarEtapa = (evento) => {
    const etapa = evento.target.value;
    setDatos((actuales) => ({
      ...actuales,
      etapa,
      probabilidad: PROBABILIDAD[etapa],
      motivo_cierre: etapa === 'Perdida' ? actuales.motivo_cierre : '',
    }));
  };

  const manejarEnvio = async (evento) => {
    evento.preventDefault();
    if (!datos.lead_id || !datos.tipo_operacion) {
      setError('El lead y el tipo de operación son obligatorios');
      return;
    }
    if (datos.valor_estimado && !datos.moneda) {
      setError('Selecciona la moneda del valor estimado');
      return;
    }
    if (datos.etapa === 'Perdida' && !datos.motivo_cierre.trim()) {
      setError('Indica por qué se perdió la oportunidad');
      return;
    }

    const payload = {
      ...datos,
      lead_id: Number(datos.lead_id),
      propiedad_id: datos.propiedad_id ? Number(datos.propiedad_id) : null,
      valor_estimado: datos.valor_estimado ? Number(datos.valor_estimado) : null,
      probabilidad: Number(datos.probabilidad),
      moneda: datos.moneda || null,
      fecha_cierre_estimada: datos.fecha_cierre_estimada || null,
      motivo_cierre: datos.motivo_cierre.trim() || null,
      notas: datos.notas.trim() || null,
    };

    try {
      setCargando(true);
      setError(null);
      await alGuardar(payload);
    } catch (err) {
      setError(err.message || 'No se pudo guardar la oportunidad');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      {error && <div className="alert-error">{error}</div>}

      <p className="form-seccion-titulo">Negocio</p>
      <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="oportunidad-lead">Lead</label>
          <select id="oportunidad-lead" value={datos.lead_id} onChange={cambiarLead} disabled={cargando || Boolean(oportunidadEditar)}>
            <option value="">Selecciona un lead</option>
            {leads.map((lead) => <option key={lead.id} value={lead.id}>{lead.nombre}</option>)}
          </select>
          {oportunidadEditar && <span className="form-ayuda">El lead no se cambia después de crear el negocio.</span>}
        </div>
        <div className="form-group form-group-full">
          <label htmlFor="oportunidad-propiedad">Propiedad asociada</label>
          <select id="oportunidad-propiedad" value={datos.propiedad_id || ''} onChange={cambiar('propiedad_id')} disabled={cargando}>
            <option value="">Aún sin propiedad definida</option>
            {propiedades.map((propiedad) => <option key={propiedad.id} value={propiedad.id}>{propiedad.titulo}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="oportunidad-tipo">Operación</label>
          <select id="oportunidad-tipo" value={datos.tipo_operacion} onChange={cambiar('tipo_operacion')} disabled={cargando}>
            <option value="">Selecciona</option><option>Compra</option><option>Arriendo</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="oportunidad-etapa">Etapa</label>
          <select id="oportunidad-etapa" value={datos.etapa} onChange={cambiarEtapa} disabled={cargando}>
            {ETAPAS.map((etapa) => <option key={etapa}>{etapa}</option>)}
          </select>
        </div>
      </div>

      <p className="form-seccion-titulo">Valor y proyección</p>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="oportunidad-valor">Valor estimado</label>
          <input id="oportunidad-valor" type="number" min="1" value={datos.valor_estimado ?? ''} onChange={cambiar('valor_estimado')} disabled={cargando} />
        </div>
        <div className="form-group">
          <label htmlFor="oportunidad-moneda">Moneda</label>
          <select id="oportunidad-moneda" value={datos.moneda || ''} onChange={cambiar('moneda')} disabled={cargando}>
            <option value="">Sin definir</option><option>UF</option><option>CLP</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="oportunidad-probabilidad">Probabilidad (%)</label>
          <input id="oportunidad-probabilidad" type="number" min="0" max="100" value={datos.probabilidad} onChange={cambiar('probabilidad')} disabled={cargando} />
        </div>
        <div className="form-group">
          <label htmlFor="oportunidad-fecha">Cierre estimado</label>
          <input id="oportunidad-fecha" type="date" value={datos.fecha_cierre_estimada || ''} onChange={cambiar('fecha_cierre_estimada')} disabled={cargando} />
        </div>
      </div>

      {datos.etapa === 'Perdida' && (
        <div className="form-group">
          <label htmlFor="oportunidad-motivo">Motivo de pérdida</label>
          <input id="oportunidad-motivo" value={datos.motivo_cierre || ''} onChange={cambiar('motivo_cierre')} disabled={cargando} placeholder="Precio, financiamiento, eligió otra propiedad..." />
        </div>
      )}

      <div className="form-group">
        <label htmlFor="oportunidad-notas">Notas comerciales</label>
        <textarea id="oportunidad-notas" className="form-textarea" rows="4" value={datos.notas || ''} onChange={cambiar('notas')} disabled={cargando} placeholder="Condiciones, objeciones o acuerdos relevantes" />
      </div>

      <div className="form-actions">
        <button type="button" className="btn-secondary" onClick={alCancelar} disabled={cargando}>Cancelar</button>
        <button type="submit" className="btn-primary" disabled={cargando}>{cargando ? 'Guardando...' : oportunidadEditar ? 'Guardar cambios' : 'Crear oportunidad'}</button>
      </div>
    </form>
  );
}

export default FormularioOportunidad;
