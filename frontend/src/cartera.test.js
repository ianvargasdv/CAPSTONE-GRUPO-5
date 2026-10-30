import test from 'node:test';
import assert from 'node:assert/strict';
import { filtrarClientes, parametrosCartera } from './cartera.js';

const ejecutivo = { id: 2, rol: 'ejecutivo' };
const admin = { id: 1, rol: 'admin' };

test('mi cartera no envía un identificador de usuario manipulable', () => {
  assert.deepEqual(parametrosCartera('mia', ejecutivo), { cartera: 'mia' });
  assert.deepEqual(parametrosCartera('mia', admin), { cartera: 'mia' });
  assert.deepEqual(parametrosCartera('todos', ejecutivo), {});
});

test('sólo administración puede preparar filtros de responsable y sin asignar', () => {
  assert.deepEqual(parametrosCartera('responsable:3', admin), { ejecutivo_id: 3 });
  assert.deepEqual(parametrosCartera('sin_asignar', admin), { sin_asignar: true });
  assert.throws(() => parametrosCartera('responsable:3', ejecutivo));
  assert.throws(() => parametrosCartera('sin_asignar', ejecutivo));
});

test('rechaza sesiones y selecciones inválidas', () => {
  for (const usuario of [null, {}, { id: -1 }, { id: '2' }]) assert.throws(() => parametrosCartera('mia', usuario));
  for (const opcion of ['', null, 'otro', 'responsable:0', 'responsable:-1', 'responsable:abc', 'responsable:1.5', 'responsable:9007199254740992']) {
    assert.throws(() => parametrosCartera(opcion, admin));
  }
});

const clientes = [
  { id: 1, nombre: 'Nicolás', comunas_interes: 'Peñalolén', ejecutivo_nombre: 'Ejecutivo Norte', estado: 'Nuevo', categoria: 'Alta' },
  { id: 2, nombre: 'Ana', comunas_interes: 'Ñuñoa', ejecutivo_nombre: 'Ejecutivo Norte', estado: 'Contactado', categoria: 'Normal' },
  { id: 3, nombre: 'Sol', comunas_interes: 'Macul', ejecutivo_nombre: null, estado: 'Nuevo', categoria: 'Baja' },
];

test('combina búsqueda sin tildes, estado y atención dentro de la cartera recibida', () => {
  assert.deepEqual(filtrarClientes(clientes, 'penalolen', 'Nuevo', 'Alta').map(c => c.id), [1]);
  assert.deepEqual(filtrarClientes(clientes, 'norte', 'Contactado', 'Normal').map(c => c.id), [2]);
  assert.deepEqual(filtrarClientes(clientes, 'nicolas', 'Contactado'), []);
});

test('cartera vacía y filtros sin resultados no inventan ni recuperan clientes externos', () => {
  assert.deepEqual(filtrarClientes([], ''), []);
  assert.deepEqual(filtrarClientes(clientes.slice(0, 1), 'Ana'), []);
  assert.equal(filtrarClientes(clientes, '').length, 3);
});

test('consultar no altera los clientes ni su orden de prioridad', () => {
  const antes = structuredClone(clientes);
  assert.deepEqual(filtrarClientes(clientes).map(c => c.id), [1, 2, 3]);
  assert.deepEqual(clientes, antes);
});
