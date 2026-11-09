import React, { useEffect, useRef, useState } from 'react';
import Icono from './Iconos';
import AvatarMobilita from './AvatarMobilita';
import PlanMobilita from './PlanMobilita';
import AgendaMobilita from './AgendaMobilita';
import { confirmarAccionesMobilita, elegirClienteMobilita, descartarPasoMobilita, ajustarPasoMobilita } from '../api';
import { prepararTareaChat, confirmarTareaChat, cancelarTareaChat } from '../api';
import { prepararRevisionChat, confirmacionChat, precioPropiedadChat, duplicadoConfirmacion } from '../chatTareas';

function ResultadoPropiedades({ consulta, alVerCatalogo }) {
  const propiedades = consulta.propiedades;
  const tarjeta = propiedad => <li key={propiedad.id} className="mobilita-inmueble">
    <span className="mobilita-inmueble-nombre">{propiedad.titulo}</span>
    <span className="mobilita-inmueble-meta">{[propiedad.comuna || 'Comuna sin registrar', propiedad.operacion === 'Compra' ? 'Venta' : propiedad.operacion].filter(Boolean).join(' · ')}</span>
    <span className="mobilita-inmueble-precio">{precioPropiedadChat(propiedad.precio, propiedad.moneda)}</span>
  </li>;
  return <div className="mobilita-inmuebles">
    <p>{consulta.mensaje}</p>
    <ul aria-label="Propiedades disponibles">{propiedades.slice(0, 3).map(tarjeta)}</ul>
    {propiedades.length > 3 && <details className="mobilita-mas-propiedades">
      <summary><span className="resumen-abrir">Ver {propiedades.length - 3} más de esta consulta</span><span className="resumen-cerrar">Mostrar menos propiedades</span></summary>
      <ul aria-label="Más propiedades disponibles">{propiedades.slice(3).map(tarjeta)}</ul>
    </details>}
    {consulta.total > propiedades.length && <p className="mobilita-inmuebles-aviso">Esta consulta incluye {propiedades.length} de {consulta.total}. El resto está en el catálogo.</p>}
    {alVerCatalogo && propiedades.length > 0 && <button type="button" className="btn-secondary" onClick={alVerCatalogo}>Ver catálogo completo</button>}
  </div>;
}

export default function Mobilita({ iaConfigurada, tareas = [], alGuardar, alCambios, alGenerar, alVerPropiedades, alVerTarea, oculto = false }) {
  const [abierto, setAbierto] = useState(false);
  const [ampliado, setAmpliado] = useState(false);
  const [reinicioPendiente, setReinicioPendiente] = useState(false);
  const [saludoVisible, setSaludoVisible] = useState(() => {
    try {
      return sessionStorage.getItem('mobilita_saludo_cerrado') !== '1';
    } catch { return true; }
  });
  const [mensaje, setMensaje] = useState('');
  const [propuesta, setPropuesta] = useState(null);
  const [revision, setRevision] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [ultimoTurno, setUltimoTurno] = useState(null);
  const [conversacion, setConversacion] = useState(null);
  const [error, setError] = useState('');
  const [duplicada, setDuplicada] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const [solicitudEnCurso, setSolicitudEnCurso] = useState(null);
  const enCurso = useRef(false);
  const siguienteMensaje = useRef(0);
  const editor = useRef(null);
  const entrada = useRef(null);
  const lanzador = useRef(null);
  const cuerpo = useRef(null);
  const ultimaRespuesta = useRef(null);
  const avisoError = useRef(null);

  const agregarMensajes = (...mensajes) => {
    const nuevos = mensajes.map(item => ({ ...item, id: ++siguienteMensaje.current }));
    setHistorial(prev => [...prev, ...nuevos].slice(-20));
  };
  const cerrar = () => {
    setAbierto(false);
    requestAnimationFrame(() => lanzador.current?.focus());
  };
  const cerrarSaludo = () => {
    setSaludoVisible(false);
    try { sessionStorage.setItem('mobilita_saludo_cerrado', '1'); } catch { /* Se conserva el estado mientras la aplicación esté abierta. */ }
  };
  const abrir = () => {
    cerrarSaludo();
    setAbierto(true);
  };

  useEffect(() => {
    if (abierto && !oculto && !ocupado && !reinicioPendiente) {
      const destino = propuesta ? editor.current : entrada.current;
      destino?.focus();
    }
  }, [abierto, oculto, propuesta, ocupado, reinicioPendiente]);

  useEffect(() => {
    if (entrada.current) {
      entrada.current.style.height = 'auto';
      entrada.current.style.height = `${Math.min(entrada.current.scrollHeight, 128)}px`;
    }
  }, [mensaje, propuesta, abierto, ampliado]);

  useEffect(() => {
    if (!error || !abierto || oculto) return;
    const frame = requestAnimationFrame(() => {
      avisoError.current?.scrollIntoView({ block: 'nearest' });
      avisoError.current?.focus({ preventScroll: true });
    });
    return () => cancelAnimationFrame(frame);
  }, [error, abierto, oculto]);

  useEffect(() => {
    if (!abierto || !cuerpo.current) return;
    // En respuestas largas se muestra el comienzo, no el final que oculta el resumen.
    if (!solicitudEnCurso && ultimaRespuesta.current?.offsetHeight > cuerpo.current.clientHeight / 2) {
      cuerpo.current.scrollTop += ultimaRespuesta.current.getBoundingClientRect().top - cuerpo.current.getBoundingClientRect().top - 12;
    } else {
      cuerpo.current.scrollTop = historial.length || solicitudEnCurso ? cuerpo.current.scrollHeight : 0;
    }
  }, [historial, abierto, solicitudEnCurso, ocupado]);

  const ejecutar = async (accion) => {
    if (enCurso.current) return;
    enCurso.current = true; setOcupado(true); setError(''); setDuplicada(null);
    try { await accion(); }
    catch (e) {
      setError(e.message || 'No se pudo completar la acción. Tus datos se conservan.');
      setDuplicada(duplicadoConfirmacion(e, revision));
    }
    finally { enCurso.current = false; setOcupado(false); }
  };

  const recibir = resultado => {
    const borrador = resultado.acciones || resultado.agenda?.length ? null : prepararRevisionChat(resultado);
    const revisable = resultado.estado === 'pendiente' && (resultado.acciones?.length || resultado.clientes.length > 0);
    setPropuesta(revisable ? resultado : null); setRevision(revisable ? borrador : null);
    setConversacion(resultado); setUltimoTurno(resultado.id); setMensaje('');
    return revisable;
  };

  const preparar = (e) => {
    e.preventDefault();
    if (!mensaje.trim() || propuesta || reinicioPendiente) return;
    ejecutar(async () => {
      const solicitud = mensaje.trim();
      setSolicitudEnCurso(solicitud);
      try {
        const resultado = await prepararTareaChat(solicitud, ultimoTurno);
        const revisable = recibir(resultado);
        agregarMensajes({ autor: 'usuario', texto: solicitud }, { autor: 'mobilita', texto: resultado.mensaje,
          consulta: resultado.consulta });
        alGenerar?.();
        requestAnimationFrame(() => (revisable ? editor.current : entrada.current)?.focus());
      } finally {
        setSolicitudEnCurso(null);
      }
    });
  };

  const confirmar = (e) => {
    e.preventDefault();
    ejecutar(async () => {
      const tarea = await confirmarTareaChat(propuesta.id, confirmacionChat(propuesta, revision));
      setPropuesta(null); setRevision(null); setMensaje('');
      agregarMensajes({ autor: 'mobilita', texto: `Tarea guardada: ${tarea.titulo}. Puedes revisarla en Tareas.` });
      alGuardar(tarea);
    });
  };

  const confirmarPlan = () => ejecutar(async () => {
    const resultado = await confirmarAccionesMobilita(propuesta.id, propuesta.paso);
    if (resultado.siguiente) recibir(resultado.siguiente);
    else { setPropuesta(null); setRevision(null); setMensaje(''); }
    agregarMensajes({ autor: 'mobilita', texto: resultado.mensaje });
    if (resultado.siguiente?.estado === 'aclarar') agregarMensajes({ autor: 'mobilita', texto: resultado.siguiente.mensaje });
    alCambios?.();
  });

  const cancelar = () => ejecutar(async () => {
    if (propuesta.agenda?.length) {
      const siguiente = await descartarPasoMobilita(propuesta.id, propuesta.paso);
      recibir(siguiente);
      agregarMensajes({ autor: 'mobilita', texto: siguiente.mensaje });
      return;
    }
    await cancelarTareaChat(propuesta.id);
    setPropuesta(null); setRevision(null);
    agregarMensajes({ autor: 'mobilita', texto: 'Propuesta descartada. No se guardaron cambios. Puedes corregir tu solicitud.' });
    requestAnimationFrame(() => entrada.current?.focus());
  });

  const reiniciar = () => ejecutar(async () => {
    if (conversacion?.agenda?.some(b => b.estado === 'pendiente')) await descartarPasoMobilita(conversacion.id, conversacion.paso, true);
    else if (propuesta) await cancelarTareaChat(propuesta.id);
    setPropuesta(null); setRevision(null); setHistorial([]); setUltimoTurno(null);
    setMensaje(''); setReinicioPendiente(false);
    setConversacion(null);
  });

  const elegirCliente = id => ejecutar(async () => {
    const resultado = await elegirClienteMobilita(conversacion.id, conversacion.paso, id);
    recibir(resultado);
    agregarMensajes({ autor: 'mobilita', texto: resultado.mensaje });
  });
  const ajustarSolicitud = () => ejecutar(async () => {
    const resultado = await ajustarPasoMobilita(conversacion.id, conversacion.paso);
    recibir(resultado);
    agregarMensajes({ autor: 'mobilita', texto: resultado.mensaje });
    requestAnimationFrame(() => entrada.current?.focus());
  });
  const descartarPendiente = (todos = false) => ejecutar(async () => {
    const resultado = await descartarPasoMobilita(conversacion.id, conversacion.paso, todos);
    recibir(resultado);
    agregarMensajes({ autor: 'mobilita', texto: resultado.mensaje });
  });

  const sugerir = (texto) => {
    setMensaje(texto);
    entrada.current?.focus();
  };

  const pendientes = tareas.filter(t => t.lead_id === Number(revision?.lead_id) && t.estado !== 'Completada');
  const puedeRevisar = propuesta?.estado === 'pendiente' && propuesta.clientes.length > 0;
  const cambiar = (campo, valor) => {
    setRevision(prev => ({ ...prev, [campo]: valor }));
    if (duplicada && ['titulo', 'lead_id'].includes(campo)) { setDuplicada(null); setError(''); }
  };
  const verExistente = () => ejecutar(async () => {
    await alVerTarea(duplicada.id, duplicada.leadId);
    cerrar();
  });
  const clienteSeleccionado = propuesta?.clientes.find(c => c.id === Number(revision?.lead_id));

  return (
    <div className="mobilita" hidden={oculto}>
      {!abierto && saludoVisible && <aside className="mobilita-saludo-flotante" aria-label="Presentación de Mobilita">
        <button type="button" className="mobilita-saludo-cerrar" aria-label="Cerrar saludo de Mobilita" onClick={cerrarSaludo}>
          <Icono nombre="cerrar" tamano={14} />
        </button>
        <div className="mobilita-saludo-identidad"><AvatarMobilita tamano="pequeno" /><strong>¡Hola! Soy Mobilita.</strong></div>
        <p>Te ayudo a revisar tu cartera, consultar pendientes y preparar tareas.</p>
        <button type="button" className="mobilita-saludo-abrir" onClick={abrir}>¿Lo revisamos?</button>
      </aside>}
      <button ref={lanzador} hidden={abierto} className={`mobilita-lanzador${ocupado ? ' trabajando' : ''}`} type="button" aria-expanded={abierto}
        aria-controls="mobilita-ventana" aria-label="Abrir Mobilita" onClick={abrir}>
        <AvatarMobilita className="mobilita-personaje" pensando={ocupado} saludando={saludoVisible && !abierto} />
        <span className="mobilita-lanzador-texto"><strong>Mobilita</strong><small>{ocupado ? 'Preparando respuesta…' : 'Tu asistente del CRM'}</small></span>
        {ocupado && <span className="mobilita-actividad" aria-hidden="true" />}
      </button>
      <section id="mobilita-ventana" hidden={!abierto} className={`mobilita-ventana${ampliado ? ' ampliada' : ''}`} role="dialog"
        aria-labelledby="mobilita-titulo" aria-describedby="mobilita-descripcion"
        onKeyDown={e => { if (e.key === 'Escape') { e.stopPropagation(); cerrar(); } }}>
        <header className={`mobilita-encabezado${ocupado ? ' trabajando' : ''}`}>
          <div className="mobilita-identidad"><AvatarMobilita pensando={ocupado} />
            <div><h2 id="mobilita-titulo">Mobilita</h2><p>Asistente del CRM</p></div>
          </div>
          <div className="mobilita-acciones">
          <button type="button" className="mobilita-nuevo" aria-label="Nuevo chat" title="Empezar un nuevo chat"
            disabled={ocupado}
            onClick={() => propuesta || mensaje.trim() || conversacion?.agenda?.some(b => b.estado === 'pendiente') ? setReinicioPendiente(true) : reiniciar()}>
            <Icono nombre="editar" tamano={16} /><span>Nuevo chat</span>
          </button>
          <button type="button" className="mobilita-control mobilita-ampliar" aria-label={ampliado ? 'Reducir chat' : 'Ampliar chat'}
            title={ampliado ? 'Reducir chat' : 'Ampliar chat'} onClick={() => setAmpliado(prev => !prev)}>
            <Icono nombre={ampliado ? 'reducir' : 'ampliar'} tamano={16} />
          </button>
          <button type="button" className="mobilita-control mobilita-minimizar" aria-label="Minimizar chat" title="Minimizar chat (Escape)" onClick={cerrar}>
            <Icono nombre="minimizar" tamano={16} /><span>Minimizar</span>
          </button>
          </div>
        </header>
        <p id="mobilita-descripcion" className="mobilita-alcance">Consultas y acciones del CRM con tu confirmación</p>
        {reinicioPendiente && <div className="mobilita-reinicio" role="group" aria-label="Confirmar nuevo chat">
          <strong>¿Empezar otro chat?</strong>
          <p>Se descartarán el texto y la propuesta pendientes.</p>
          <div><button type="button" className="btn-secondary" disabled={ocupado} onClick={() => setReinicioPendiente(false)}>Seguir aquí</button>
            <button type="button" className="btn-primary" disabled={ocupado} onClick={reiniciar}>Empezar nuevo chat</button></div>
        </div>}
        <div ref={cuerpo} className="chat-tareas-contenido mobilita-cuerpo">
        {!historial.length && !solicitudEnCurso && <div className="mobilita-inicio">
          <AvatarMobilita tamano="grande" saludando />
          <h3>¿Qué necesitas revisar?</h3>
          <p>Consulta tu cartera o cuéntame qué hiciste con un cliente. Revisarás los cambios antes de guardarlos.</p>
          <div className="mobilita-sugerencias" aria-label="Consultas sugeridas">
            {[['usuarios', 'Mi cartera', '¿Cuántos leads tengo asignados en mi cartera?'],
              ['reloj', 'Tareas vencidas', '¿Qué tareas vencidas tiene mi cartera?'],
              ['edificio', 'Propiedades disponibles', '¿Qué propiedades están disponibles?']].map(([icono, texto, consulta]) =>
                <button key={texto} type="button" disabled={ocupado || reinicioPendiente || !iaConfigurada} onClick={() => sugerir(consulta)}>
                  <Icono nombre={icono} tamano={17} /><span>{texto}</span>
                </button>)}
          </div>
          <small>Estas son algunas sugerencias. También puedes escribir tu propia consulta sobre el CRM.</small>
        </div>}
        <div className="mobilita-conversacion" role="log" aria-label="Conversación con Mobilita" aria-live="polite" aria-relevant="additions">
          {historial.map(item => <div key={item.id} ref={item.autor === 'mobilita' && item.id === historial[historial.length - 1]?.id ? ultimaRespuesta : undefined}
            className={`mobilita-mensaje ${item.autor === 'usuario' ? 'usuario' : 'asistente'}`}>
            <div className="mobilita-mensaje-identidad">{item.autor !== 'usuario' && <AvatarMobilita tamano="mini" />}<strong>{item.autor === 'usuario' ? 'Tú' : 'Mobilita'}</strong></div>
            {item.consulta?.permitida && item.consulta.herramienta === 'propiedades_disponibles' && Array.isArray(item.consulta.propiedades)
              ? <ResultadoPropiedades consulta={item.consulta} alVerCatalogo={alVerPropiedades ? () => { cerrar(); alVerPropiedades(); } : null} />
              : <p>{item.texto}</p>}
            {item.consulta && <div className={`mobilita-fuente${item.consulta.permitida ? '' : ' denegada'}`}>
              <Icono nombre={item.consulta.permitida ? 'baseDatos' : 'alerta'} tamano={13} />
              <span>{item.consulta.permitida ? 'Datos del CRM' : 'Sin permiso para esta consulta'} · {new Date(item.consulta.fecha_consulta).toLocaleString('es-CL')}</span></div>}
          </div>)}
          {solicitudEnCurso && <div className="mobilita-mensaje usuario"><strong>Tú</strong><p>{solicitudEnCurso}</p></div>}
        </div>
        {ocupado && (solicitudEnCurso || propuesta) && <div className="mobilita-escribiendo" role="status">
          <AvatarMobilita tamano="pequeno" pensando />
          <div><strong>Mobilita</strong><div className="mobilita-espera">
            <span className="mobilita-puntos" aria-hidden="true"><i /><i /><i /></span>
            <span>{propuesta ? 'Procesando la propuesta…' : 'Preparando respuesta…'}</span>
          </div></div>
        </div>}
        {!iaConfigurada && <p role="status">El servicio de IA no está disponible. Puedes crear la tarea con el formulario habitual.</p>}
        {error && !propuesta && <p ref={avisoError} tabIndex={-1} className="alert-error" role="alert">{error}</p>}
        <AgendaMobilita conversacion={conversacion} ocupado={ocupado || reinicioPendiente}
          alElegir={elegirCliente} alDescartar={() => descartarPendiente()} alDescartarTodos={() => descartarPendiente(true)} />
        {propuesta?.acciones && <PlanMobilita key={`${propuesta.id}-${propuesta.paso || ''}`} propuesta={propuesta}
          pendientes={tareas.filter(t => t.lead_id === propuesta.clientes[0]?.id && t.estado !== 'Completada')}
          ocupado={ocupado || reinicioPendiente} error={error} alConfirmar={confirmarPlan} alDescartar={cancelar}
          alAjustar={ajustarSolicitud} />}
        {propuesta && !propuesta.acciones && <div className="mobilita-propuesta">
          <div className="mobilita-propuesta-titulo"><Icono nombre="tareas" tamano={18} /><div><strong>Propuesta de tarea</strong><p>Aún no está guardada. Revisa los datos.</p></div></div>
          {puedeRevisar && <form onSubmit={confirmar}>
            <fieldset disabled={ocupado || reinicioPendiente} className="chat-tareas-campos">
              <legend className="mobilita-solo-lector">Revisa la tarea antes de confirmar</legend>
              <label htmlFor="chat-tarea-lead">Lead *</label>
              <select id="chat-tarea-lead" className="form-select" required value={revision.lead_id}
                onChange={e => cambiar('lead_id', e.target.value)}>
                <option value="">Selecciona al lead correcto</option>
                {propuesta.clientes.map(c => <option key={c.id} value={c.id} disabled={c.estado === 'Cerrado'}>
                  {c.nombre} · Ficha #{c.id}{c.estado === 'Cerrado' ? ' · Cerrado' : ''}
                </option>)}
              </select>
              {pendientes.length > 0 && <div className="chat-tareas-pendientes">
                <strong>Revisa las tareas pendientes para evitar duplicar el seguimiento:</strong>
                <ul>{pendientes.map(t => <li key={t.id}>{t.titulo} · {t.estado}</li>)}</ul>
              </div>}
              <label htmlFor="chat-tarea-titulo">Título *</label>
              <input ref={editor} id="chat-tarea-titulo" className="form-input" required maxLength={200}
                value={revision.titulo} onChange={e => cambiar('titulo', e.target.value)} />
              <label htmlFor="chat-tarea-descripcion">Descripción</label>
              <textarea id="chat-tarea-descripcion" className="form-textarea" rows={3} maxLength={5000}
                value={revision.descripcion} onChange={e => cambiar('descripcion', e.target.value)} />
              <div className="chat-tareas-fila">
                <label>Prioridad<select className="form-select" value={revision.prioridad} onChange={e => cambiar('prioridad', e.target.value)}>
                  <option>Alta</option><option>Media</option><option>Baja</option>
                </select></label>
                <label>Fecha límite (opcional)<input type="date" className="form-input" value={revision.fecha_limite}
                  onChange={e => cambiar('fecha_limite', e.target.value)} /></label>
              </div>
              <p className="resumen-anteriores">Se guardará como Pendiente. Esta propuesta vence a los 30 minutos.</p>
              {error && <div ref={avisoError} id="mobilita-error-confirmacion" tabIndex={-1} className={`alert-error mobilita-aviso-confirmacion${duplicada ? ' duplicada' : ''}`} role="alert">
                <Icono nombre="alerta" tamano={20} />
                <div><strong>{duplicada ? 'Esta tarea ya existe' : 'No se pudo confirmar'}</strong>
                  <p>{duplicada ? `Revisa la tarea pendiente de ${clienteSeleccionado?.nombre || 'este lead'}.` : error}</p>
                  {duplicada && alVerTarea && <button type="button" className="btn-secondary" onClick={verExistente}>Ver tarea existente</button>}
                </div>
              </div>}
              {!duplicada && <button type="submit" className="btn-primary" aria-describedby={error ? 'mobilita-error-confirmacion' : undefined} disabled={!revision.lead_id}>{ocupado ? 'Guardando…' : 'Confirmar y crear tarea'}</button>}
            </fieldset>
          </form>}
          <button className="btn-secondary" type="button" disabled={ocupado || reinicioPendiente} onClick={cancelar}>
            {puedeRevisar ? 'Descartar propuesta' : 'Corregir solicitud'}
          </button>
        </div>}
        </div>
        {!propuesta && <form className="mobilita-compositor" onSubmit={preparar}>
          <label htmlFor="chat-tareas-mensaje" className="mobilita-solo-lector">Mensaje para Mobilita</label>
          <div className="mobilita-entrada">
            <textarea ref={entrada} id="chat-tareas-mensaje" className="form-textarea" rows={2} minLength={2} maxLength={3000}
              placeholder="Pregunta sobre tu CRM…"
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
                  e.preventDefault();
                  if (!ocupado && !reinicioPendiente && iaConfigurada && mensaje.trim().length >= 2) e.currentTarget.form.requestSubmit();
                }
              }}
              value={mensaje} onChange={e => setMensaje(e.target.value)} disabled={ocupado || reinicioPendiente} required />
            <button className="mobilita-enviar" type="submit" disabled={ocupado || reinicioPendiente || !iaConfigurada || mensaje.trim().length < 2}
              aria-label={ocupado ? 'Preparando propuesta' : 'Enviar solicitud a Mobilita'}>
              {ocupado ? <span className="mobilita-spinner" aria-hidden="true" /> : <Icono nombre="enviar" tamano={19} />}
            </button>
          </div>
          <div className="mobilita-pie-entrada"><small>Revisa las propuestas antes de guardarlas.</small><small>Mayús + Enter: nueva línea</small></div>
        </form>}
      </section>
    </div>
  );
}
