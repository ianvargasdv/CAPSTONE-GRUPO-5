import React, { useEffect, useState } from 'react';
import { asignarLead, obtenerAsignaciones, obtenerEjecutivos, obtenerLeads } from '../api';

export default function AsignacionLead({ lead, esAdmin, alActualizar }) {
  const [ejecutivos, setEjecutivos] = useState([]);
  const [seleccion, setSeleccion] = useState(String(lead.ejecutivo_id ?? ''));
  const [historial, setHistorial] = useState({ items: [], total: 0 });
  const [pagina, setPagina] = useState(1);
  const [version, setVersion] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState('');
  const [errorHistorial, setErrorHistorial] = useState('');
  const [aviso, setAviso] = useState('');

  useEffect(() => setSeleccion(String(lead.ejecutivo_id ?? '')), [lead.ejecutivo_id]);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setErrorHistorial('');
    obtenerAsignaciones(lead.id, pagina)
      .then((datos) => { if (vigente) setHistorial(datos); })
      .catch((e) => { if (vigente) setErrorHistorial(e.message); })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [lead.id, pagina, version]);

  useEffect(() => {
    if (!esAdmin) return undefined;
    let vigente = true;
    obtenerEjecutivos()
      .then((datos) => { if (vigente) setEjecutivos(datos); })
      .catch((e) => { if (vigente) setError(e.message); });
    return () => { vigente = false; };
  }, [esAdmin, lead.id, version]);

  async function guardar(e) {
    e.preventDefault();
    setGuardando(true); setError(''); setAviso('');
    try {
      const actualizado = await asignarLead(lead.id, Number(seleccion), lead.ejecutivo_id);
      alActualizar(actualizado);
      setPagina(1); setVersion((v) => v + 1);
      setAviso('Responsable actualizado. El cambio quedó registrado.');
    } catch (e) { setError(e.message); }
    finally { setGuardando(false); }
  }

  async function refrescar() {
    setGuardando(true); setError(''); setAviso('');
    try {
      const actual = (await obtenerLeads()).find((item) => item.id === lead.id);
      if (!actual) throw new Error('El lead ya no existe. Cierra esta ficha y actualiza el listado.');
      alActualizar(actual);
      setPagina(1); setVersion((v) => v + 1);
    } catch (e) { setError(e.message); }
    finally { setGuardando(false); }
  }

  return (
    <section className="ficha-seccion">
      <div className="ficha-seccion-encabezado">
        <span className="ficha-seccion-titulo">Responsable del lead</span>
        <button type="button" className="btn-secondary" disabled={guardando} onClick={refrescar}>Actualizar</button>
      </div>
      <p>{lead.ejecutivo_nombre || 'Sin asignar'}</p>
      {esAdmin && (
        <form onSubmit={guardar} className="asignacion-formulario">
          <label htmlFor={`responsable-${lead.id}`}>Nuevo responsable *</label>
          <select id={`responsable-${lead.id}`} className="filter-select" required value={seleccion}
            disabled={guardando || ejecutivos.length === 0} onChange={(e) => { setSeleccion(e.target.value); setAviso(''); }}>
            <option value="">Seleccionar usuario activo</option>
            {lead.ejecutivo_id && !ejecutivos.some((u) => u.id === lead.ejecutivo_id) && (
              <option value={lead.ejecutivo_id} disabled>{lead.ejecutivo_nombre || 'Responsable no disponible'}</option>
            )}
            {ejecutivos.map((u) => <option key={u.id} value={u.id}>{u.nombre}{u.rol === 'admin' ? ' (administración)' : ''}</option>)}
          </select>
          <button className="btn-primary" type="submit"
            disabled={guardando || !seleccion || Number(seleccion) === lead.ejecutivo_id || !ejecutivos.some((u) => u.id === Number(seleccion))}>
            {guardando ? 'Guardando…' : 'Guardar responsable'}
          </button>
        </form>
      )}
      {error && <div className="alert-error" role="alert">{error}</div>}
      {aviso && <p role="status">{aviso}</p>}
      <details className="asignaciones-detalle">
        <summary>Historial de responsables ({historial.total})</summary>
        {cargando ? <p>Cargando historial…</p> : errorHistorial ? (
          <p role="alert">{errorHistorial} Usa Actualizar para volver a consultar.</p>
        ) : historial.items.length === 0 ? (
          <p>No hay movimientos registrados. En leads anteriores, el responsable actual puede existir sin un historial de asignación.</p>
        ) : (
          <>
            <div className="asignaciones-lista">
              {historial.items.map((movimiento) => (
                <div key={movimiento.id} className="asignacion-movimiento">
                  <strong>{movimiento.anterior_nombre || 'Sin asignar'} → {movimiento.nuevo_nombre}</strong>
                  <span className="celda-secundaria">
                    {new Date(movimiento.fecha_creacion).toLocaleString('es-CL')} · Registrado por {movimiento.autor_nombre}
                  </span>
                </div>
              ))}
            </div>
            <div className="asignacion-paginacion">
              <button type="button" className="btn-secondary" disabled={cargando || guardando || pagina === 1} onClick={() => setPagina((p) => p - 1)}>Anterior</button>
              <span>Página {pagina} de {Math.max(1, Math.ceil(historial.total / 10))}</span>
              <button type="button" className="btn-secondary" disabled={cargando || guardando || pagina * 10 >= historial.total} onClick={() => setPagina((p) => p + 1)}>Siguiente</button>
            </div>
          </>
        )}
      </details>
    </section>
  );
}
