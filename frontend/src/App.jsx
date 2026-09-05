import React from 'react';

function App() {
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
            <h2 className="card-title">Estado del Sistema</h2>
            <span className="badge">Estado Inicial</span>
          </div>

          <p className="card-description">
            Estructura base iniciada con éxito. Listo para incorporar componentes y lógica requerida.
          </p>

          <div className="status-grid">
            <div className="status-card">
              <span className="status-label">Sistema Frontend</span>
              <div className="status-indicator">
                <span className="dot"></span>
                Activo
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

export default App;
