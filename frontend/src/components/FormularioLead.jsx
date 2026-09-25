import React, { useEffect, useState } from 'react';

const VACIO = {
  nombre: '', email: '', telefono: '', estado: 'Nuevo', prioridad: 'Media',
  tipo_operacion: '', presupuesto_min: '', presupuesto_max: '', moneda: '',
  comunas_interes: '', tipo_propiedad_buscada: '', dormitorios_min: '', banos_min: '',
  plazo_decision: '', financiamiento: '', origen: '',
  proxima_accion: '', fecha_proxima_accion: '',
};

const camposNumericos = ['presupuesto_min', 'presupuesto_max', 'dormitorios_min', 'banos_min'];

function FormularioLead({ alGuardar, leadEditar, alCancelar }) {
  const [datos, setDatos] = useState(VACIO);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const modoEdicion = Boolean(leadEditar);

  useEffect(() => {
    const editables = leadEditar
      ? Object.fromEntries(Object.keys(VACIO).map((campo) => [campo, leadEditar[campo] ?? VACIO[campo]]))
      : VACIO;
    setDatos({ ...VACIO, ...editables });
    setError(null);
  }, [leadEditar]);

  const cambiar = (campo) => (evento) => {
    setDatos((actuales) => ({ ...actuales, [campo]: evento.target.value }));
  };

  const manejarEnvio = async (evento) => {
    evento.preventDefault();
    if (!datos.nombre.trim() || !datos.email.trim()) {
      setError('El nombre y el correo son obligatorios');
      return;
    }

    const minimo = datos.presupuesto_min === '' ? null : Number(datos.presupuesto_min);
    const maximo = datos.presupuesto_max === '' ? null : Number(datos.presupuesto_max);
    if (minimo !== null && maximo !== null && minimo > maximo) {
      setError('El presupuesto mínimo no puede superar el máximo');
      return;
    }

    const payload = { ...datos, nombre: datos.nombre.trim(), email: datos.email.trim() };
    ['telefono', 'tipo_operacion', 'moneda', 'comunas_interes', 'tipo_propiedad_buscada',
      'plazo_decision', 'financiamiento', 'origen', 'proxima_accion',
      'fecha_proxima_accion'].forEach((campo) => {
      payload[campo] = typeof payload[campo] === 'string' ? payload[campo].trim() || null : payload[campo];
    });
    camposNumericos.forEach((campo) => {
      payload[campo] = payload[campo] === '' || payload[campo] === null ? null : Number(payload[campo]);
    });

    try {
      setCargando(true);
      setError(null);
      await alGuardar(payload);
    } catch (err) {
      setError(err.message || 'No se pudo guardar el lead');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      {error && <div className="alert-error">{error}</div>}

      <p className="form-seccion-titulo">Datos de contacto</p>
      <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="nombre">Nombre completo</label>
          <input id="nombre" value={datos.nombre} onChange={cambiar('nombre')} disabled={cargando} autoFocus placeholder="Camila Soto" />
        </div>
        <div className="form-group">
          <label htmlFor="email">Correo</label>
          <input id="email" type="email" value={datos.email} onChange={cambiar('email')} disabled={cargando} placeholder="camila@ejemplo.cl" />
        </div>
        <div className="form-group">
          <label htmlFor="telefono">Teléfono</label>
          <input id="telefono" value={datos.telefono || ''} onChange={cambiar('telefono')} disabled={cargando} placeholder="+56 9 1234 5678" />
        </div>
        <div className="form-group">
          <label htmlFor="estado">Estado</label>
          <select id="estado" value={datos.estado} onChange={cambiar('estado')} disabled={cargando}>
            {['Nuevo', 'Contactado', 'Calificado', 'Cerrado'].map((valor) => <option key={valor}>{valor}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="prioridad">Prioridad comercial</label>
          <select id="prioridad" value={datos.prioridad} onChange={cambiar('prioridad')} disabled={cargando}>
            {['Alta', 'Media', 'Baja'].map((valor) => <option key={valor}>{valor}</option>)}
          </select>
        </div>
      </div>

      <p className="form-seccion-titulo">Perfil de búsqueda</p>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="tipo_operacion">Operación</label>
          <select id="tipo_operacion" value={datos.tipo_operacion || ''} onChange={cambiar('tipo_operacion')} disabled={cargando}>
            <option value="">Sin definir</option><option>Compra</option><option>Arriendo</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="tipo_propiedad_buscada">Tipo de propiedad</label>
          <select id="tipo_propiedad_buscada" value={datos.tipo_propiedad_buscada || ''} onChange={cambiar('tipo_propiedad_buscada')} disabled={cargando}>
            <option value="">Sin definir</option>
            {['Departamento', 'Casa', 'Terreno', 'Oficina'].map((valor) => <option key={valor}>{valor}</option>)}
          </select>
        </div>
        <div className="form-group form-group-full">
          <label htmlFor="comunas_interes">Comunas de interés</label>
          <input id="comunas_interes" value={datos.comunas_interes || ''} onChange={cambiar('comunas_interes')} disabled={cargando} placeholder="Ñuñoa, Macul, Providencia" />
        </div>
        <div className="form-group">
          <label htmlFor="presupuesto_min">Presupuesto mínimo</label>
          <input id="presupuesto_min" type="number" min="0" value={datos.presupuesto_min ?? ''} onChange={cambiar('presupuesto_min')} disabled={cargando} />
        </div>
        <div className="form-group">
          <label htmlFor="presupuesto_max">Presupuesto máximo</label>
          <input id="presupuesto_max" type="number" min="0" value={datos.presupuesto_max ?? ''} onChange={cambiar('presupuesto_max')} disabled={cargando} />
        </div>
        <div className="form-group">
          <label htmlFor="moneda">Moneda</label>
          <select id="moneda" value={datos.moneda || ''} onChange={cambiar('moneda')} disabled={cargando}><option value="">Sin definir</option><option>UF</option><option>CLP</option></select>
        </div>
        <div className="form-group form-inline-dos">
          <div><label htmlFor="dormitorios_min">Dormitorios mín.</label><input id="dormitorios_min" type="number" min="0" max="20" value={datos.dormitorios_min ?? ''} onChange={cambiar('dormitorios_min')} disabled={cargando} /></div>
          <div><label htmlFor="banos_min">Baños mín.</label><input id="banos_min" type="number" min="0" max="20" value={datos.banos_min ?? ''} onChange={cambiar('banos_min')} disabled={cargando} /></div>
        </div>
        <div className="form-group">
          <label htmlFor="plazo_decision">Plazo de decisión</label>
          <select id="plazo_decision" value={datos.plazo_decision || ''} onChange={cambiar('plazo_decision')} disabled={cargando}>
            <option value="">Sin definir</option>{['Inmediato', '0-3 meses', '3-6 meses', '6-12 meses'].map((valor) => <option key={valor}>{valor}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="financiamiento">Financiamiento</label>
          <select id="financiamiento" value={datos.financiamiento || ''} onChange={cambiar('financiamiento')} disabled={cargando}>
            <option value="">Sin definir</option>{['Crédito preaprobado', 'En evaluación', 'Recursos propios'].map((valor) => <option key={valor}>{valor}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="origen">Origen</label>
          <select id="origen" value={datos.origen || ''} onChange={cambiar('origen')} disabled={cargando}>
            <option value="">Sin definir</option>
            {['Referido', 'Portal inmobiliario', 'Redes sociales', 'Sitio web', 'Llamada', 'Otro', 'Demo capstone'].map((valor) => <option key={valor}>{valor}</option>)}
          </select>
        </div>
      </div>

      <p className="form-seccion-titulo">Seguimiento</p>
      <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="proxima_accion">Próxima acción</label>
          <input id="proxima_accion" value={datos.proxima_accion || ''} onChange={cambiar('proxima_accion')} disabled={cargando} placeholder="Enviar alternativas y confirmar visita" />
        </div>
        <div className="form-group">
          <label htmlFor="fecha_proxima_accion">Fecha comprometida</label>
          <input id="fecha_proxima_accion" type="date" value={datos.fecha_proxima_accion || ''} onChange={cambiar('fecha_proxima_accion')} disabled={cargando} />
        </div>
      </div>

      <div className="form-actions">
        {alCancelar && <button type="button" className="btn-secondary" onClick={alCancelar} disabled={cargando}>Cancelar</button>}
        <button type="submit" className="btn-primary" disabled={cargando}>{cargando ? 'Guardando...' : modoEdicion ? 'Guardar cambios' : 'Crear lead'}</button>
      </div>
    </form>
  );
}

export default FormularioLead;
