import React, { useEffect, useState } from 'react';
import {
  obtenerLeads,
  crearLead,
  actualizarLead,
  eliminarLead,
  obtenerPropiedades,
  crearPropiedad,
  actualizarPropiedad,
  eliminarPropiedad,
} from './api';
import FormularioLead from './components/FormularioLead';
import TablaLeads from './components/TablaLeads';
import FormularioPropiedad from './components/FormularioPropiedad';
import TablaPropiedades from './components/TablaPropiedades';

function App() {
  const [pestañaActiva, setPestañaActiva] = useState('leads');

  // Estado del toast — mensaje temporal que desaparece solo
  const [toast, setToast] = useState(null);

  /**
   * Muestra un mensaje de notificación breve en pantalla.
   * Se oculta automáticamente después de 3 segundos.
   */
  const mostrarToast = (mensaje) => {
    setToast(mensaje);
    setTimeout(() => setToast(null), 3000);
  };

  // --- Estado de Leads ---
  const [leads, setLeads] = useState([]);
  const [cargandoLeads, setCargandoLeads] = useState(true);
  const [errorLeads, setErrorLeads] = useState(null);
  // leadEditar contiene el objeto lead que está siendo editado, o null si es modo creación
  const [leadEditar, setLeadEditar] = useState(null);

  // --- Estado de Propiedades ---
  const [propiedades, setPropiedades] = useState([]);
  const [cargandoPropiedades, setCargandoPropiedades] = useState(true);
  const [errorPropiedades, setErrorPropiedades] = useState(null);
  // propiedadEditar contiene el objeto propiedad que está siendo editado, o null si es modo creación
  const [propiedadEditar, setPropiedadEditar] = useState(null);

  const cargarLeads = async () => {
    try {
      setCargandoLeads(true);
      setErrorLeads(null);
      const datos = await obtenerLeads();
      setLeads(datos);
    } catch (err) {
      setErrorLeads('No se pudo conectar con el backend para cargar los leads.');
    } finally {
      setCargandoLeads(false);
    }
  };

  const cargarPropiedades = async () => {
    try {
      setCargandoPropiedades(true);
      setErrorPropiedades(null);
      const datos = await obtenerPropiedades();
      setPropiedades(datos);
    } catch (err) {
      setErrorPropiedades('No se pudo conectar con el backend para cargar las propiedades.');
    } finally {
      setCargandoPropiedades(false);
    }
  };

  useEffect(() => {
    cargarLeads();
    cargarPropiedades();
  }, []);

  // --- Handlers de Leads ---

  const manejarGuardarLead = async (datosLead) => {
    if (leadEditar) {
      // Modo edición: actualiza el lead existente
      const leadActualizado = await actualizarLead(leadEditar.id, datosLead);
      setLeads((prev) =>
        prev.map((l) => (l.id === leadActualizado.id ? leadActualizado : l))
      );
      setLeadEditar(null);
      mostrarToast('Lead actualizado con éxito ✓');
    } else {
      // Modo creación: agrega el nuevo lead a la lista
      const leadGuardado = await crearLead(datosLead);
      setLeads((prev) => [...prev, leadGuardado]);
      mostrarToast('Lead registrado con éxito en Supabase ✓');
    }
  };

  const manejarEditarLead = (lead) => {
    setLeadEditar(lead);
    // Desplaza la vista hacia arriba para mostrar el formulario
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const manejarEliminarLead = async (id) => {
    await eliminarLead(id);
    setLeads((prev) => prev.filter((l) => l.id !== id));
    mostrarToast('Lead eliminado ✓');
  };

  const manejarCancelarEdicionLead = () => {
    setLeadEditar(null);
  };

  // --- Handlers de Propiedades ---

  const manejarGuardarPropiedad = async (datosPropiedad) => {
    if (propiedadEditar) {
      // Modo edición: actualiza la propiedad existente
      const propiedadActualizada = await actualizarPropiedad(propiedadEditar.id, datosPropiedad);
      setPropiedades((prev) =>
        prev.map((p) => (p.id === propiedadActualizada.id ? propiedadActualizada : p))
      );
      setPropiedadEditar(null);
      mostrarToast('Propiedad actualizada con éxito ✓');
    } else {
      // Modo creación: agrega la nueva propiedad a la lista
      const propiedadGuardada = await crearPropiedad(datosPropiedad);
      setPropiedades((prev) => [...prev, propiedadGuardada]);
      mostrarToast('Propiedad registrada con éxito en Supabase ✓');
    }
  };

  const manejarEditarPropiedad = (propiedad) => {
    setPropiedadEditar(propiedad);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const manejarEliminarPropiedad = async (id) => {
    await eliminarPropiedad(id);
    setPropiedades((prev) => prev.filter((p) => p.id !== id));
    mostrarToast('Propiedad eliminada ✓');
  };

  const manejarCancelarEdicionPropiedad = () => {
    setPropiedadEditar(null);
  };

  return (
    <>
      {/* Toast de notificación — aparece en la esquina inferior derecha */}
      {toast && (
        <div className="toast-notification">
          {toast}
        </div>
      )}

      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo">CRM</div>
          <div>
            <h1 className="brand-title">Gestión Inmobiliaria</h1>
            <span className="header-subtitle">Proyecto Capstone</span>
          </div>
        </div>

        <div className="header-right">
          {/* Indicador de conexión a la base de datos */}
          <div className="db-indicator">
            <span className="dot"></span>
            <span>Base de Datos: Supabase</span>
          </div>

          <nav className="nav-tabs">
            <button
              className={`tab-btn ${pestañaActiva === 'leads' ? 'active' : ''}`}
              onClick={() => setPestañaActiva('leads')}
            >
              Leads ({leads.length})
            </button>
            <button
              className={`tab-btn ${pestañaActiva === 'propiedades' ? 'active' : ''}`}
              onClick={() => setPestañaActiva('propiedades')}
            >
              Propiedades ({propiedades.length})
            </button>
          </nav>
        </div>
      </header>

      <main className="main-content">
        {pestañaActiva === 'leads' ? (
          <>
            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">
                  {leadEditar ? `Editando Lead #${leadEditar.id}` : 'Nuevo Lead'}
                </h2>
                <span className="badge">Gestión de Leads</span>
              </div>
              <FormularioLead
                alGuardar={manejarGuardarLead}
                leadEditar={leadEditar}
                alCancelar={manejarCancelarEdicionLead}
              />
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Leads Registrados ({leads.length})</h2>
              </div>
              <TablaLeads
                leads={leads}
                cargando={cargandoLeads}
                error={errorLeads}
                alEditar={manejarEditarLead}
                alEliminar={manejarEliminarLead}
              />
            </div>
          </>
        ) : (
          <>
            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">
                  {propiedadEditar ? `Editando Propiedad #${propiedadEditar.id}` : 'Nueva Propiedad'}
                </h2>
                <span className="badge">Catálogo Inmobiliario</span>
              </div>
              <FormularioPropiedad
                alGuardar={manejarGuardarPropiedad}
                propiedadEditar={propiedadEditar}
                alCancelar={manejarCancelarEdicionPropiedad}
              />
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Propiedades Registradas ({propiedades.length})</h2>
              </div>
              <TablaPropiedades
                propiedades={propiedades}
                cargando={cargandoPropiedades}
                error={errorPropiedades}
                alEditar={manejarEditarPropiedad}
                alEliminar={manejarEliminarPropiedad}
              />
            </div>
          </>
        )}
      </main>
    </>
  );
}

export default App;
