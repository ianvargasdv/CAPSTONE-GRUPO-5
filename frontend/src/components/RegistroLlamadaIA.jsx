import React, { useRef, useState } from 'react';
import { textoDeAnalisisLlamada, validarRespuestaLlamada } from '../notasLlamada';

function RegistroLlamadaIA({ cliente, alPreparar, alGuardar, iaConfigurada, analisis = [], integrado = false }) {
  const [notas, setNotas] = useState('');
  const [preparacion, setPreparacion] = useState(null);
  const [texto, setTexto] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  // El ref cubre dos eventos antes de que React alcance a desactivar el botón.
  const enCurso = useRef(false);
  const editor = useRef(null);
  const anteriores = analisis.filter((a) => a.tipo === 'registro_llamada');

  const preparar = async () => {
    if (enCurso.current || !notas.trim() || notas.trim().length > 5000) return;
    enCurso.current = true;
    setOcupado(true); setError(''); setAviso('');
    try {
      const respuesta = await alPreparar(notas.trim());
      const nuevoTexto = validarRespuestaLlamada(respuesta, cliente.id);
      setTexto(nuevoTexto); setPreparacion(respuesta);
      requestAnimationFrame(() => editor.current?.focus());
    } catch (err) {
      setError(err.message || 'No se pudieron preparar las notas. Puedes volver a intentarlo.');
    } finally {
      enCurso.current = false; setOcupado(false);
    }
  };

  const guardar = async (e) => {
    e.preventDefault();
    if (enCurso.current || !preparacion || !texto.trim() || texto.trim().length > 5000) return;
    enCurso.current = true;
    setOcupado(true); setError('');
    try {
      await alGuardar({ tipo: 'Llamada', notas: texto.trim() });
      setPreparacion(null); setNotas(''); setTexto('');
      setAviso('Llamada registrada. La ficha y las tareas no se modificaron.');
    } catch (err) {
      setError(err.message || 'No se pudo registrar la llamada. El texto se conserva.');
    } finally {
      enCurso.current = false; setOcupado(false);
    }
  };

  const formulario = (
      <form className="form-lead" onSubmit={guardar} aria-label={`Registro asistido de llamada de ${cliente.nombre}`}>
        <p className="resumen-anteriores"><strong>Cliente: {cliente.nombre}</strong><br />
          Usa notas de una llamada que ya realizaste. Revisa el texto antes de registrarlo.</p>
        {error && <div className="alert-error" role="alert">{error}</div>}
        {aviso && <p role="status">{aviso}</p>}
        <div className="form-group">
          <label htmlFor="notas-llamada-ia">Tus notas de la llamada *</label>
          <textarea id="notas-llamada-ia" className="form-textarea" rows={4} maxLength={5000}
            value={notas} onChange={(e) => { setNotas(e.target.value); setAviso(''); }}
            disabled={ocupado || Boolean(preparacion)} placeholder="Qué conversaron, qué pidió el cliente y qué quedó pendiente" />
        </div>
        {!preparacion ? (
          <>
            <p className="resumen-anteriores">Preparar consulta al proveedor de IA y registra el análisis y su consumo. Todavía no registra una llamada.</p>
            <button type="button" className="btn-secondary" onClick={preparar}
              disabled={ocupado || !iaConfigurada || !notas.trim()}>
              {ocupado ? 'Preparando propuesta…' : 'Preparar propuesta'}
            </button>
            {!iaConfigurada && <p className="resumen-anteriores">El servicio de IA no está configurado. Puedes usar el registro manual.</p>}
          </>
        ) : (
          <div className="bloque-resumen">
            <p className="resumen-origen">Propuesta generada con IA · Análisis #{preparacion.analisis.id}</p>
            <p className="resumen-anteriores">
              {preparacion.analisis.modelo}
              {preparacion.analisis.costo_estimado_usd != null && ` · ${preparacion.analisis.costo_estimado_usd.toLocaleString('es-CL', { style: 'currency', currency: 'USD', minimumFractionDigits: 6 })} estimados`}
            </p>
            <div className="form-group">
              <label htmlFor="texto-llamada-confirmado">Texto que se guardará *</label>
              <textarea ref={editor} id="texto-llamada-confirmado" className="form-textarea" rows={9}
                value={texto} maxLength={5000} disabled={ocupado} onChange={(e) => setTexto(e.target.value)} required />
            </div>
            <p className="resumen-anteriores">Confirmar registra una llamada con este texto. Los requisitos y la próxima acción no se guardan en otros campos.</p>
            <div className="form-actions">
              <button type="button" className="btn-secondary" disabled={ocupado}
                onClick={() => { setPreparacion(null); setTexto(''); setError(''); setAviso('Propuesta descartada. Tus notas se conservan y no se registró una llamada.'); }}>
                Descartar propuesta
              </button>
              <button type="submit" className="btn-primary" disabled={ocupado || !texto.trim()}>
                {ocupado ? 'Guardando…' : 'Confirmar y registrar llamada'}
              </button>
            </div>
          </div>
        )}
        {anteriores.length > 0 && (
          <details className="resumen-detalle">
            <summary>Ver análisis de llamadas guardados ({anteriores.length})</summary>
            {anteriores.map((a) => (
              <details key={a.id}>
                <summary>Análisis #{a.id} · {new Date(a.fecha_creacion).toLocaleString('es-CL')}</summary>
                <p className="resumen-anteriores">Este análisis no acredita que se haya registrado una llamada.</p>
                <p className="resumen-texto" style={{ whiteSpace: 'pre-wrap' }}>{textoDeAnalisisLlamada(a.salida)}</p>
                <details><summary>Salida original de IA</summary><pre className="resumen-entrada">{a.salida}</pre></details>
                <details><summary>Notas enviadas al modelo</summary><pre className="resumen-entrada">{a.entrada}</pre></details>
              </details>
            ))}
          </details>
        )}
      </form>
  );

  return integrado ? (
    <section className="registro-llamada-ia integrado" aria-label="Notas de una llamada">
      <h3 className="asistente-titulo">Notas de una llamada</h3>
      {formulario}
    </section>
  ) : (
    <details className="registro-llamada-ia">
      <summary>Preparar notas de llamada con IA</summary>
      {formulario}
    </details>
  );
}

export default RegistroLlamadaIA;
