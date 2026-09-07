import React, { useEffect, useState } from 'react';
import { obtenerLeads, crearLead, obtenerPropiedades, crearPropiedad } from './api';
import FormularioLead from './components/FormularioLead';
import TablaLeads from './components/TablaLeads';
import FormularioPropiedad from './components/FormularioPropiedad';
import TablaPropiedades from './components/TablaPropiedades';

function App() {
  const [pestañaActiva, setPestañaActiva] = useState('leads');

  // Estado de Leads
  const [leads, setLeads] = useState([]);
  const [cargandoLeads, setCargandoLeads] = useState(true);
  const [errorLeads, setErrorLeads] = useState(null);

  // Estado de Propiedades
  const [propiedades, setPropiedades] = useState([]);
  const [cargandoPropiedades, setCargandoPropiedades] = useState(true);
  const [errorPropiedades, setErrorPropiedades] = useState(null);

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

  const manejarGuardarLead = async (nuevoLead) => {
    const leadGuardado = await crearLead(nuevoLead);
    setLeads((prev) => [...prev, leadGuardado]);
  };

  const manejarGuardarPropiedad = async (nuevaPropiedad) => {
    const propiedadGuardada = await crearPropiedad(nuevaPropiedad);
    setPropiedades((prev) => [...prev, propiedadGuardada]);
  };

  return (
    <>
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo">CRM</div>
          <div>
            <h1 className="brand-title">Gestión Inmobiliaria</h1>
            <span className="header-subtitle">Proyecto Capstone</span>
          </div>
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
      </header>

      <main className="main-content">
        {pestañaActiva === 'leads' ? (
          <>
            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Nuevo Lead</h2>
                <span className="badge">Gestión de Leads</span>
              </div>
              <FormularioLead alGuardar={manejarGuardarLead} />
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Leads Registrados ({leads.length})</h2>
              </div>
              <TablaLeads leads={leads} cargando={cargandoLeads} error={errorLeads} />
            </div>
          </>
        ) : (
          <>
            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Nueva Propiedad</h2>
                <span className="badge">Catálogo Inmobiliario</span>
              </div>
              <FormularioPropiedad alGuardar={manejarGuardarPropiedad} />
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Propiedades Registradas ({propiedades.length})</h2>
              </div>
              <TablaPropiedades
                propiedades={propiedades}
                cargando={cargandoPropiedades}
                error={errorPropiedades}
              />
            </div>
          </>
        )}
      </main>
    </>
  );
}

export default App;
