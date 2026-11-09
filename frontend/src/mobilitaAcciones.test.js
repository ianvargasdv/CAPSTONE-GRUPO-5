import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

let servidor, Plan, Buzon, Agenda;
before(async () => {
  servidor = await createServer({ server: { middlewareMode: true }, appType: 'custom' });
  Plan = (await servidor.ssrLoadModule('/src/components/PlanMobilita.jsx')).default;
  Buzon = (await servidor.ssrLoadModule('/src/components/BuzonSolicitudes.jsx')).default;
  Agenda = (await servidor.ssrLoadModule('/src/components/AgendaMobilita.jsx')).default;
});
after(async () => { await servidor?.close(); });

const render = (Componente, props) => renderToStaticMarkup(React.createElement(Componente, props));
const propuesta = {
  cliente_acciones: 'Cliente de prueba', acciones: [
    { tipo: 'actualizar_lead', etiqueta: 'Actualizar datos del lead', datos: { estado: 'Contactado' }, antes: { estado: 'Nuevo' } },
    { tipo: 'crear_tarea', etiqueta: 'Crear tarea', datos: { titulo: 'Volver a llamar', fecha_limite: '2026-11-10' } },
  ],
};
const solicitudes = [{ id: 1, cliente: 'Cliente de prueba', autor: 'Ejecutivo', motivo: 'No desea continuar.', estado: 'Pendiente', fecha: '2026-11-08T12:00:00Z' }];

test('muestra el cliente, cada cambio y fecha concreta antes de confirmar', () => {
  const html = render(Plan, { propuesta, pendientes: [{ id: 1, titulo: 'Confirmar requisitos' }] });
  for (const texto of ['Cliente de prueba', 'Actual: Nuevo', 'Contactado', 'Volver a llamar', '2026-11-10', 'Confirmar cambios', 'Descartar propuesta']) {
    assert.ok(html.includes(texto), texto);
  }
  assert.ok(html.includes('Todavía no se ha guardado nada'));
  assert.ok(html.includes('Confirmar requisitos'));
  assert.ok(html.includes('pide actualizar la tarea existente'));
});

test('el texto recibido se presenta como texto, sin ejecutar HTML', () => {
  const html = render(Plan, { propuesta: { ...propuesta, cliente_acciones: '<script>error()</script>' } });
  assert.ok(!html.includes('<script>'));
  assert.ok(html.includes('&lt;script&gt;'));
});

test('durante el guardado se bloquean confirmar y descartar', () => {
  const html = render(Plan, { propuesta, ocupado: true });
  assert.equal((html.match(/disabled=""/g) || []).length, 2);
});

test('un error de confirmación es visible y puede recibir foco', () => {
  const html = render(Plan, { propuesta, error: 'La tarea cambió. Prepara otra propuesta.' });
  assert.ok(html.includes('role="alert"'));
  assert.ok(html.includes('tabindex="-1"'));
  assert.ok(html.includes('La tarea cambió'));
});

test('sólo administración ve las opciones de decidir una solicitud', () => {
  const ejecutivo = render(Buzon, { solicitudes, admin: false });
  const admin = render(Buzon, { solicitudes, admin: true });
  assert.ok(ejecutivo.includes('Mis solicitudes'));
  assert.ok(!ejecutivo.includes('Revisar archivo'));
  assert.ok(!ejecutivo.includes('>Rechazar<'));
  assert.ok(admin.includes('Revisar archivo'));
  assert.ok(admin.includes('>Rechazar<'));
});

test('el buzón vacío y los errores se distinguen', () => {
  assert.ok(render(Buzon, { solicitudes: [], admin: true }).includes('No hay solicitudes'));
  const error = render(Buzon, { solicitudes: [], error: 'No se pudo cargar el buzón', admin: true });
  assert.ok(error.includes('role="alert"'));
  assert.ok(!error.includes('No hay solicitudes'));
});

test('la agenda distingue guardado, pendiente y descartado sin ofrecer repetir lo terminado', () => {
  const html = render(Agenda, { conversacion: { estado: 'pendiente', agenda: [
    { numero: 1, cliente: 'Uno', estado: 'guardado', acciones: ['Registrar contacto'] },
    { numero: 2, cliente: 'Dos', estado: 'pendiente', acciones: ['Crear tarea'] },
    { numero: 3, cliente: 'Tres', estado: 'descartado', acciones: [] },
  ] } });
  for (const texto of ['Solicitud 2 de 3', 'Guardado', 'Pendiente', 'Descartado']) assert.ok(html.includes(texto));
  assert.ok(!html.includes('Omitir esta solicitud'));
});

test('la selección muestra nombres y un dato para distinguir homónimos', () => {
  const html = render(Agenda, { conversacion: { estado: 'aclarar', agenda: [{ numero: 1, cliente: 'Valentina', estado: 'pendiente', acciones: [] }],
    opciones_cliente: [{ id: 1, nombre: 'Valentina Pérez', correo: 'una@example.test', estado: 'Nuevo' },
      { id: 2, nombre: 'Valentina Soto', correo: 'otra@example.test', estado: 'Contactado' }] }, ocupado: true });
  assert.ok(html.includes('Valentina Pérez')); assert.ok(html.includes('Valentina Soto'));
  assert.ok(html.includes('una@example.test'));
  assert.ok(html.includes('Elegir el cliente correcto'));
  assert.ok(html.includes('disabled=""'));
});

test('corregir una propuesta es una opción separada de confirmar y descartar', () => {
  const html = render(Plan, { propuesta, alAjustar() {} });
  assert.ok(html.includes('Corregir esta solicitud'));
  assert.ok(html.includes('Confirmar cambios'));
  assert.ok(html.includes('Descartar propuesta'));
});

test('al terminar la agenda no ofrece descartar solicitudes guardadas', () => {
  const html = render(Agenda, { conversacion: { estado: 'confirmada', agenda: [{ numero: 1, cliente: 'Uno', estado: 'guardado', acciones: [] }] } });
  assert.ok(html.includes('Solicitudes terminadas'));
  assert.ok(!html.includes('<button'));
});
