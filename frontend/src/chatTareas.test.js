import test from 'node:test';
import assert from 'node:assert/strict';
import { prepararRevisionChat, confirmacionChat, precioPropiedadChat, duplicadoConfirmacion } from './chatTareas.js';

test('duplicado sólo enlaza la tarea y el lead identificados por el rechazo del servidor', () => {
  const e = {status:409, codigo:'tarea_duplicada', tareaId:12, leadId:7};
  assert.deepEqual(duplicadoConfirmacion(e, {lead_id:'7'}), {id:12, leadId:7});
  for (const cambio of [{status:500}, {codigo:'propuesta_vencida'}, {leadId:8}, {tareaId:-1}, {tareaId:'12'}, {leadId:null}]) {
    assert.equal(duplicadoConfirmacion({...e, ...cambio}, {lead_id:'7'}), null);
  }
  assert.equal(duplicadoConfirmacion(new Error('Sin conexión'), {lead_id:'7'}), null);
});

test('precios del chat usan separación de miles y conservan CLP o UF', () => {
  assert.equal(precioPropiedadChat(169000000, 'CLP'), '169.000.000 CLP');
  assert.equal(precioPropiedadChat(3980, 'UF'), '3.980 UF');
  assert.equal(precioPropiedadChat(3980.5, 'UF'), '3.980,5 UF');
  assert.equal(precioPropiedadChat(0, 'CLP'), '0 CLP');
});
test('precio o moneda ausentes no se inventan', () => {
  for (const valor of [null, undefined, '100', NaN, Infinity, -1]) assert.equal(precioPropiedadChat(valor, 'CLP'), 'Precio sin registrar');
  assert.equal(precioPropiedadChat(100, null), '100 · moneda sin registrar');
});

const propuesta = { id: 2, estado: 'pendiente', mensaje: 'Revisa antes de confirmar.', clientes: [{ id: 7, nombre: 'Cliente ficticio', estado: 'Nuevo' }], titulo: 'Llamar', descripcion: '' };

test('prepara al único cliente sin inventar fecha ni prioridad alta', () => {
  assert.deepEqual(prepararRevisionChat(propuesta), { lead_id: '7', titulo: 'Llamar', descripcion: '', prioridad: 'Media', fecha_limite: '' });
});
test('homónimos requieren selección y un cliente cerrado no se preselecciona', () => {
  assert.equal(prepararRevisionChat({ ...propuesta, clientes: [...propuesta.clientes, { id: 8, nombre: 'Cliente ficticio' }] }).lead_id, '');
  assert.equal(prepararRevisionChat({ ...propuesta, clientes: [{ ...propuesta.clientes[0], estado: 'Cerrado' }] }).lead_id, '');
});
test('una aclaración no prepara una escritura', () => {
  const p = { ...propuesta, estado: 'aclarar', clientes: [] };
  assert.throws(() => confirmacionChat(p, prepararRevisionChat(p)));
});
test('una respuesta del CRM permite continuar pero no confirmar una tarea', () => {
  const p = { ...propuesta, estado: 'respuesta', clientes: [], titulo: '', descripcion: '', mensaje: 'Abre la ficha del lead.' };
  assert.equal(prepararRevisionChat(p).lead_id, '');
  assert.throws(() => confirmacionChat(p, prepararRevisionChat(p)));
});
test('rechaza respuestas mal formadas', () => {
  for (const valor of [null, {}, { ...propuesta, id: -1 }, { ...propuesta, clientes: [{}] }, { ...propuesta, titulo: null }, { ...propuesta, mensaje: ' ' }]) {
    assert.throws(() => prepararRevisionChat(valor));
  }
});
test('confirmación conserva el cliente permitido y sólo envía campos admitidos', () => {
  const r = prepararRevisionChat(propuesta);
  const datos = confirmacionChat(propuesta, { ...r, titulo: ' Contactado: quiere la propiedad ', estado: 'Contactado', sql: 'x' });
  assert.equal(datos.titulo, 'Contactado: quiere la propiedad');
  assert.deepEqual(Object.keys(datos).sort(), ['descripcion', 'fecha_limite', 'lead_id', 'prioridad', 'titulo']);
  assert.equal(datos.lead_id, 7);
});
test('no confirma sin cliente ni con una ficha ajena', () => {
  for (const lead_id of ['', '90']) assert.throws(() => confirmacionChat(propuesta, { ...prepararRevisionChat(propuesta), lead_id }));
});
test('valida título, descripción y prioridad antes de enviar', () => {
  for (const cambio of [{ titulo: ' ' }, { titulo: 'x'.repeat(201) }, { descripcion: 'x'.repeat(5001) }, { prioridad: 'Urgente' }]) {
    assert.throws(() => confirmacionChat(propuesta, { ...prepararRevisionChat(propuesta), ...cambio }));
  }
});
test('preparar y confirmar no mutan la propuesta original', () => {
  const antes = structuredClone(propuesta);
  confirmacionChat(propuesta, prepararRevisionChat(propuesta));
  assert.deepEqual(propuesta, antes);
});
