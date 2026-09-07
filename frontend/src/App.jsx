import React, { useEffect, useState } from 'react';
import { obtenerLeads, crearLead } from './api';
import FormularioLead from './components/FormularioLead';
import TablaLeads from './components/TablaLeads';

function App() {
  const [leads, setLeads] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const cargarLeads = async () => {
    try {
      setCargando(true);
      setError(null);
      const datos = await obtenerLeads();
      setLeads(datos);
    } catch (err) {
      setError('No se pudo conectar con el servidor backend. Verifica que FastAPI esté ejecutándose.');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarLeads();
  }, []);

  const manejarGuardarLead = async (nuevoLead) => {
    const leadGuardado = await crearLead(nuevoLead);
    setLeads((leadsPrevios) => [...leadsPrevios, leadGuardado]);
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
      </header>

      <main className="main-content">
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Nuevo Lead</h2>
            <span className="badge">Módulo Leads</span>
          </div>
          <FormularioLead alGuardar={manejarGuardarLead} />
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Leads Registrados ({leads.length})</h2>
          </div>
          <TablaLeads leads={leads} cargando={cargando} error={error} />
        </div>
      </main>
    </>
  );
}

export default App;
