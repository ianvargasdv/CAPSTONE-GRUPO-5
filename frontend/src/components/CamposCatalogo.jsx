import React from 'react';

export const CAMPOS_NUMERICOS_CATALOGO = ['superficie_util', 'superficie_total', 'estacionamientos', 'gastos_comunes'];
export const CAMPOS_PRIVADOS_CATALOGO = ['propietario_nombre', 'propietario_email', 'propietario_telefono', 'captador'];

const campos = [
  ['codigo_interno', 'Código interno', 'text'],
  ['superficie_util', 'Superficie útil (m²)', 'number'],
  ['superficie_total', 'Superficie total (m²)', 'number'],
  ['estacionamientos', 'Estacionamientos', 'number'],
  ['gastos_comunes', 'Gastos comunes (CLP)', 'number'],
  ['fecha_disponibilidad', 'Fecha de disponibilidad', 'date'],
];
const privados = [
  ['propietario_nombre', 'Nombre del propietario', 'text'],
  ['propietario_email', 'Correo del propietario', 'email'],
  ['propietario_telefono', 'Teléfono del propietario', 'tel'],
  ['captador', 'Captador responsable', 'text'],
];

export default function CamposCatalogo({ datos, alCambiar, esAdmin, deshabilitado }) {
  const fotos = (datos.fotografiasTexto || '').split('\n').map(url => url.trim()).filter(Boolean);
  return <>
    {campos.map(([nombre, etiqueta, tipo]) => <div className="form-group" key={nombre}>
      <label htmlFor={`catalogo_${nombre}`}>{etiqueta}</label>
      <input id={`catalogo_${nombre}`} type={tipo} min={tipo === 'number' ? 0 : undefined}
        step={nombre.startsWith('superficie') ? 'any' : undefined}
        maxLength={tipo === 'text' ? 100 : undefined}
        value={datos[nombre] ?? ''} disabled={deshabilitado}
        onChange={e => alCambiar(nombre, e.target.value)} />
    </div>)}
    <div className="form-group">
      <label htmlFor="catalogo_bodega">Bodega</label>
      <select id="catalogo_bodega" value={datos.bodega ?? ''} disabled={deshabilitado} onChange={e => alCambiar('bodega', e.target.value)}>
        <option value="">Sin registrar</option><option value="si">Sí</option><option value="no">No</option>
      </select>
    </div>
    {['descripcion', 'caracteristicas'].map(nombre => <div className="form-group form-group-full" key={nombre}>
      <label htmlFor={`catalogo_${nombre}`}>{nombre === 'descripcion' ? 'Descripción comercial' : 'Características (orientación, terraza, equipamiento)'}</label>
      <textarea id={`catalogo_${nombre}`} maxLength={5000} value={datos[nombre] ?? ''} disabled={deshabilitado} onChange={e => alCambiar(nombre, e.target.value)} />
    </div>)}
    <div className="form-group form-group-full">
      <label htmlFor="catalogo_fotografias">Fotografías: un enlace HTTP o HTTPS por línea (máximo 20)</label>
      <textarea id="catalogo_fotografias" value={datos.fotografiasTexto || ''} disabled={deshabilitado}
        onChange={e => {
          alCambiar('fotografiasTexto', e.target.value);
          if (!e.target.value.split('\n').map(url => url.trim()).includes(datos.foto_principal)) alCambiar('foto_principal', '');
        }} />
    </div>
    <div className="form-group form-group-full">
      <label htmlFor="catalogo_principal">Fotografía principal</label>
      <select id="catalogo_principal" value={datos.foto_principal || ''} disabled={deshabilitado} onChange={e => alCambiar('foto_principal', e.target.value)}>
        <option value="">Usar la primera fotografía</option>
        {[...new Set(fotos)].map(url => <option key={url} value={url}>{url}</option>)}
      </select>
    </div>
    {esAdmin && privados.map(([nombre, etiqueta, tipo]) => <div className="form-group" key={nombre}>
      <label htmlFor={`catalogo_${nombre}`}>{etiqueta} (administración)</label>
      <input id={`catalogo_${nombre}`} type={tipo} maxLength={nombre === 'propietario_email' ? 150 : nombre === 'propietario_telefono' ? 20 : 100}
        value={datos[nombre] ?? ''} disabled={deshabilitado} onChange={e => alCambiar(nombre, e.target.value)} />
    </div>)}
  </>;
}
