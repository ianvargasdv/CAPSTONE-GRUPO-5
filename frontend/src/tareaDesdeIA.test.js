import test from 'node:test';
import assert from 'node:assert/strict';
import { prepararTareaDesdeIA, pendientesDelLead, seleccionarTareaPendiente, firmaPendientes, validarNuevaTareaIA } from './tareaDesdeIA.js';

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

const pendiente = {id:10,lead_id:5,titulo:'Completar requisitos',descripcion:'Confirmar estacionamientos y terreno.',estado:'Pendiente',prioridad:'Media',fecha_limite:'2026-10-16'};
const propuesta = prepararTareaDesdeIA(lead, recomendacion);

test('con pendientes bloquea crear desde IA sin decidir expresamente otra acción', () => {
  for (const decision of [undefined, {}, {crearDistinta:true}, {confirmarDistinta:true}]) {
    assert.throws(() => validarNuevaTareaIA(propuesta,[pendiente],propuesta,decision));
  }
});

test('rechaza reutilizar el borrador o copiar el título o descripción del pendiente', () => {
  const decision = {crearDistinta:true,confirmarDistinta:true};
  for (const cambio of [{}, {titulo:'Título distinto',descripcion:''},
    {titulo:'  COMPLETAR  REQUISITOS ',descripcion:'Detalle diferente'},
    {titulo:'Acción diferente',descripcion:'  Confirmar estacionamientos y terreno. '}]) {
    assert.throws(() => validarNuevaTareaIA(propuesta,[pendiente],{...propuesta,...cambio},decision));
  }
});

test('permite una acción distinta revisada sin tocar la tarea existente', () => {
  const antes = JSON.stringify(pendiente);
  validarNuevaTareaIA(propuesta,[pendiente],{...propuesta,titulo:'Enviar ficha de la propiedad',descripcion:'Enviar los antecedentes solicitados por el cliente.'},{crearDistinta:true,confirmarDistinta:true});
  assert.equal(JSON.stringify(pendiente),antes);
});

test('sin pendientes no exige una decisión extra y excluye completadas y otros clientes', () => {
  validarNuevaTareaIA(propuesta,[],propuesta);
  validarNuevaTareaIA(propuesta,[{...pendiente,estado:'Completada'},{...pendiente,lead_id:6}],propuesta);
  assert.throws(() => validarNuevaTareaIA(propuesta,[],{...propuesta,lead_id:6}));
  validarNuevaTareaIA(null,[pendiente],{titulo:'Tarea manual'});
});

test('la firma detecta cambios sin depender del orden ni de las tareas de otros clientes', () => {
  const otra = {...pendiente,id:11,titulo:'Otra tarea'};
  assert.equal(firmaPendientes([pendiente,otra],5),firmaPendientes([otra,pendiente],5));
  assert.equal(firmaPendientes([pendiente],5),firmaPendientes([pendiente,{...otra,lead_id:6}],5));
  for (const cambio of [{estado:'Completada'},{fecha_limite:'2026-10-19'},{descripcion:'Nuevo detalle'},{titulo:'Título corregido'}]) {
    assert.notEqual(firmaPendientes([pendiente],5),firmaPendientes([{...pendiente,...cambio}],5));
  }
});
