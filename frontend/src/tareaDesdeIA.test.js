import test from 'node:test';
import assert from 'node:assert/strict';
import { prepararTareaDesdeIA, pendientesDelLead, seleccionarTareaPendiente } from './tareaDesdeIA.js';

const lead = { id: 5, nombre: 'Cliente ficticio', estado: 'Contactado' };
const recomendacion = { id: 9, lead_id: 5, tipo: 'recomendacion', salida: 'Revisar los requisitos pendientes.' };

test('prepara una tarea revisable sin inventar fecha o prioridad alta', () => {
  const r = prepararTareaDesdeIA(lead, recomendacion);
  assert.equal(r.lead_id, 5);
  assert.equal(r.fecha_limite, null);
  assert.equal(r.estado, 'Pendiente');
  assert.equal(r.prioridad, 'Media');
  assert.ok(r.descripcion.includes(recomendacion.salida));
  assert.ok(r.descripcion.includes('#9'));
  assert.equal(r.id, undefined);
});

test('no cambia el lead ni el análisis de origen', () => {
  const antes = JSON.stringify([lead, recomendacion]);
  prepararTareaDesdeIA(lead, recomendacion);
  assert.equal(JSON.stringify([lead, recomendacion]), antes);
});

test('rechaza otro lead, otro tipo o una recomendación sin texto', () => {
  for (const cambio of [{lead_id:6}, {tipo:'mensaje'}, {salida:''}, {salida:'   '}, {salida:null}, {salida:{}}, {id:0}]) {
    assert.throws(() => prepararTareaDesdeIA(lead, {...recomendacion, ...cambio}));
  }
});

test('rechaza un lead cerrado o un identificador inválido', () => {
  for (const cambio of [{estado:'Cerrado'}, {id:0}, {id:'5'}, {id:null}]) {
    assert.throws(() => prepararTareaDesdeIA({...lead, ...cambio}, recomendacion));
  }
  assert.throws(() => prepararTareaDesdeIA(null, recomendacion));
});

test('respeta límites sin recortar la recomendación', () => {
  const r = prepararTareaDesdeIA({...lead, nombre:'x'.repeat(300)}, {...recomendacion, salida:'x'.repeat(4000)});
  assert.equal(r.titulo.length, 200);
  assert.ok(r.descripcion.length <= 5000);
  assert.ok(r.descripcion.endsWith('x'.repeat(4000)));
  assert.throws(() => prepararTareaDesdeIA(lead, {...recomendacion, salida:'x'.repeat(4001)}));
});

test('no interpreta HTML ni órdenes del modelo', () => {
  const texto = '<script>enviarMensaje()</script>';
  assert.ok(prepararTareaDesdeIA(lead, {...recomendacion, salida:texto}).descripcion.endsWith(texto));
});

test('muestra sólo las tareas abiertas del mismo lead, sin mutarlas', () => {
  const tareas = [{id:1,lead_id:5,estado:'Pendiente'}, {id:2,lead_id:5,estado:'En Progreso'},
    {id:3,lead_id:5,estado:'Completada'}, {id:4,lead_id:6,estado:'Pendiente'}];
  assert.deepEqual(pendientesDelLead(tareas,5).map(t=>t.id),[1,2]);
  assert.equal(tareas.length,4);
  assert.deepEqual(pendientesDelLead([],5),[]);
});

test('abrir una tarea existente conserva id, descripción, prioridad y fecha', () => {
  const tarea = {id:10, lead_id:5, titulo:'Completar requisitos', descripcion:'Detalle original',
    estado:'Pendiente', prioridad:'Alta', fecha_limite:'2026-09-28'};
  const copia = seleccionarTareaPendiente([tarea],5,10);
  assert.deepEqual(copia,tarea);
  assert.notEqual(copia,tarea);
  copia.descripcion = 'Edición todavía local';
  assert.equal(tarea.descripcion,'Detalle original');
});

test('no abre tareas de otro lead, completadas o que no están en la lista', () => {
  const tareas = [{id:1,lead_id:6,estado:'Pendiente'}, {id:2,lead_id:5,estado:'Completada'}];
  for (const id of [1,2,3,null]) assert.throws(() => seleccionarTareaPendiente(tareas,5,id));
});

test('permite abrir una tarea que ya está en progreso', () => {
  const tarea = {id:4,lead_id:5,estado:'En Progreso'};
  assert.equal(seleccionarTareaPendiente([tarea],5,4).id,4);
});
