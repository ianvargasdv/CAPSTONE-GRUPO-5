import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Pantalla de acceso al sistema.
 *
 * No hay opción de registrarse: los accesos los crea quien administra el CRM
 * mediante el script crear_usuario.py del backend.
 *
 * Props:
 * - alIniciarSesion: recibe (email, password) y resuelve con el usuario autenticado
 * - aviso: texto informativo, por ejemplo cuando la sesión se cerró por expirar
 */
function Login({ alIniciarSesion, aviso }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const manejarEnvio = async (e) => {
    e.preventDefault();

    if (!email.trim() || !password) {
      setError('Ingresa tu correo y tu contraseña');
      return;
    }

    try {
      setCargando(true);
      setError(null);
      await alIniciarSesion(email.trim(), password);
    } catch (err) {
      setError(err.message || 'No se pudo iniciar sesión');
      setPassword('');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="login-pantalla">
      <div className="login-caja">
        <div className="login-marca">
          <div className="marca-logo">CRM</div>
          <div className="marca-texto">
            <span className="marca-nombre">Gestión Inmobiliaria</span>
            <span className="marca-sub">Acceso al sistema</span>
          </div>
        </div>

        <form className="form-lead" onSubmit={manejarEnvio}>
          {/* El aviso se oculta en cuanto hay un error propio del intento actual */}
          {aviso && !error && (
            <div className="login-aviso">
              <Icono nombre="reloj" tamano={14} />
              <span>{aviso}</span>
            </div>
          )}

          {error && (
            <div className="alert-error">
              <Icono nombre="alerta" />
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="login-email">Correo</label>
            <input
              id="login-email"
              type="email"
              autoComplete="username"
              placeholder="nombre@empresa.cl"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={cargando}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="login-password">Contraseña</label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={cargando}
            />
          </div>

          <button type="submit" className="btn-primary btn-bloque" disabled={cargando}>
            {cargando ? 'Verificando...' : 'Ingresar'}
          </button>
        </form>

        <p className="login-pie">
          Si no tienes acceso, solicítalo a quien administra el sistema.
        </p>
      </div>
    </div>
  );
}

export default Login;
