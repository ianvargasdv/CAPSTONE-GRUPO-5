"""Pruebas del evaluador local, sin red, modelos ni conexiones al CRM."""
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import casos_evaluacion as casos
import evaluar_asistente as evaluar


class EvaluacionTest(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix='crm_evaluacion_')
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name)
        self.casos = casos.cargar_casos()
        self.documento = {'version': 1, 'datos': 'ficticios', 'casos': copy.deepcopy(self.casos)}

    def cargar(self, documento):
        archivo = self.ruta / 'entrada.json'
        archivo.write_text(json.dumps(documento, ensure_ascii=False), encoding='utf-8')
        return casos.cargar_casos(archivo)

    def cli(self, *argumentos):
        with redirect_stdout(io.StringIO()) as salida, redirect_stderr(io.StringIO()) as errores:
            codigo = evaluar.main(list(argumentos))
        return codigo, salida.getvalue(), errores.getvalue()

    def test_conjunto_cubre_cuatro_funciones_y_no_muta(self):
        self.assertEqual(len(self.casos), 9)
        for tipo in casos.TIPOS:
            self.assertGreaterEqual(sum(c['tipo'] == tipo for c in self.casos), 2)
        antes = copy.deepcopy(self.documento)
        self.cargar(self.documento)
        self.assertEqual(self.documento, antes)

    def test_rechaza_version_y_datos_no_ficticios(self):
        for campo, valor in [('version', True), ('version', 2), ('datos', 'reales')]:
            with self.subTest(campo=campo, valor=valor):
                documento = copy.deepcopy(self.documento)
                documento[campo] = valor
                with self.assertRaises(ValueError):
                    self.cargar(documento)

    def test_rechaza_duplicados_tipos_y_campos_invalidos(self):
        cambios = [('id', self.casos[1]['id']), ('id', '../archivo'), ('tipo', 'enviar'),
                   ('ficha', ''), ('ficha', 'a' * 20001), ('fecha_referencia', 'ayer'),
                   ('fecha_referencia', '2026-10-20'), ('esperado', []),
                   ('no_debe_afirmar', ['']), ('esperado', [None])]
        for campo, valor in cambios:
            with self.subTest(campo=campo):
                documento = copy.deepcopy(self.documento)
                documento['casos'][0][campo] = valor
                with self.assertRaises(ValueError):
                    self.cargar(documento)

    def test_rechaza_conjunto_corto_o_funcion_sin_dos_casos(self):
        documento = copy.deepcopy(self.documento)
        documento['casos'] = documento['casos'][:7]
        with self.assertRaises(ValueError):
            self.cargar(documento)
        documento = copy.deepcopy(self.documento)
        documento['casos'][0]['tipo'] = 'mensaje'
        with self.assertRaises(ValueError):
            self.cargar(documento)

    def test_limites_de_ficha_y_criterios(self):
        documento = copy.deepcopy(self.documento)
        documento['casos'][0]['ficha'] = 'a' * 20000
        documento['casos'][0]['esperado'] = ['b' * 1000] * 20
        self.assertEqual(len(self.cargar(documento)), 9)
        documento['casos'][0]['esperado'].append('criterio extra')
        with self.assertRaises(ValueError):
            self.cargar(documento)

    def test_huella_estable_y_sensible_a_criterios(self):
        caso = self.casos[0]
        self.assertEqual(casos.huella_caso(caso), casos.huella_caso(dict(reversed(list(caso.items())))))
        cambio = copy.deepcopy(caso)
        cambio['esperado'].append('Criterio nuevo.')
        self.assertNotEqual(casos.huella_caso(caso), casos.huella_caso(cambio))

    def test_generar_no_usa_red_y_deja_todo_pendiente(self):
        with patch('urllib.request.urlopen', side_effect=AssertionError('No usar red')):
            documento = evaluar.ejecutar(self.casos)
        informe = evaluar.resumen(documento)
        self.assertEqual(informe['pendientes'], 9)
        self.assertEqual(informe['aprobados_simulados'], 0)
        self.assertEqual(informe['respuestas_reales_evaluadas'], 0)
        self.assertEqual(documento['llamadas_reales'], 0)
        self.assertTrue(all('[SIMULACIÓN]' in r['respuesta'] for r in documento['resultados']))

    def test_fallo_simulado_no_se_cuenta_como_respuesta_aprobada(self):
        documento = evaluar.ejecutar(self.casos, [self.casos[0]['id']])
        informe = evaluar.resumen(documento)
        self.assertEqual(informe['errores'], 1)
        self.assertEqual(informe['pendientes'], 8)
        with self.assertRaises(ValueError):
            evaluar.revisar(documento, self.casos[0]['id'], 'aprobado', 'Revisor de prueba', 'No corresponde.')

    def test_rechaza_fallo_de_caso_inexistente(self):
        with self.assertRaises(ValueError):
            evaluar.ejecutar(self.casos, ['no_existe'])

    def test_revision_nueva_conserva_entrada_y_no_acredita_modelo_real(self):
        original = evaluar.ejecutar(self.casos)
        revisada = evaluar.revisar(original, self.casos[0]['id'], 'aprobado', 'Revisor ficticio', 'Prueba del registro, no del modelo.')
        self.assertIsNone(original['resultados'][0]['revision'])
        self.assertEqual(evaluar.resumen(revisada)['aprobados_simulados'], 1)
        self.assertEqual(evaluar.resumen(revisada)['respuestas_reales_evaluadas'], 0)
        self.assertEqual(revisada['ejecucion_id'], original['ejecucion_id'])

    def test_revision_exige_autor_observacion_y_caso_valido(self):
        documento = evaluar.ejecutar(self.casos)
        for identificador, estado, autor, observacion in [
            ('inexistente', 'aprobado', 'Revisor', 'Comentario'),
            (self.casos[0]['id'], 'aprobado', '', 'Comentario'),
            (self.casos[0]['id'], 'aprobado', 'Revisor', ''),
            (self.casos[0]['id'], 'pendiente', 'Revisor', 'Comentario'),
        ]:
            with self.subTest(estado=estado, autor=autor):
                with self.assertRaises(ValueError):
                    evaluar.revisar(documento, identificador, estado, autor, observacion)

    def test_no_reemplaza_revision_previa(self):
        documento = evaluar.revisar(evaluar.ejecutar(self.casos), self.casos[0]['id'], 'rechazado', 'Revisor ficticio', 'Prueba de rechazo.')
        with self.assertRaises(ValueError):
            evaluar.revisar(documento, self.casos[0]['id'], 'aprobado', 'Otro revisor', 'Cambiar.')

    def test_protege_evidencias_existentes_y_no_escribe_nan(self):
        destino = self.ruta / 'ejecucion.json'
        evaluar.guardar_nuevo(destino, evaluar.ejecutar(self.casos))
        antes = destino.read_bytes()
        with self.assertRaises(FileExistsError):
            evaluar.guardar_nuevo(destino, {})
        self.assertEqual(destino.read_bytes(), antes)
        invalido = self.ruta / 'invalido.json'
        with self.assertRaises(ValueError):
            evaluar.guardar_nuevo(invalido, {'costo': float('nan')})
        self.assertFalse(invalido.exists())

    def test_rechaza_resultados_manipulados(self):
        documento = evaluar.ejecutar(self.casos)
        for campo, valor in [('respuesta', ''), ('estado', 'aprobado'), ('huella_caso', 'incorrecta'), ('revision', {'estado': 'aprobado'})]:
            copia = copy.deepcopy(documento)
            copia['resultados'][0][campo] = valor
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                evaluar.validar_ejecucion(copia)
        documento['resultados'][0]['caso']['ficha'] += ' Cambió.'
        with self.assertRaises(ValueError):
            evaluar.validar_ejecucion(documento)

    def test_rechaza_resultados_duplicados_y_modo_real(self):
        documento = evaluar.ejecutar(self.casos)
        documento['resultados'].append(copy.deepcopy(documento['resultados'][0]))
        with self.assertRaises(ValueError):
            evaluar.validar_ejecucion(documento)
        documento = evaluar.ejecutar(self.casos)
        documento['modo'] = 'real'
        with self.assertRaises(ValueError):
            evaluar.validar_ejecucion(documento)

    def test_comparar_detecta_casos_nuevos_eliminados_y_modificados(self):
        anterior = evaluar.ejecutar(self.casos)
        actual = evaluar.ejecutar(self.casos)
        actual['resultados'][0]['caso']['esperado'].append('Otro criterio.')
        actual['resultados'][0]['huella_caso'] = casos.huella_caso(actual['resultados'][0]['caso'])
        actual['resultados'].pop(1)
        nuevo = copy.deepcopy(actual['resultados'][2])
        nuevo['caso']['id'] = 'caso_nuevo'
        nuevo['huella_caso'] = casos.huella_caso(nuevo['caso'])
        actual['resultados'].append(nuevo)
        filas = {f['caso']: f for f in evaluar.comparar(anterior, actual)['casos']}
        self.assertFalse(filas[self.casos[0]['id']]['comparable'])
        self.assertFalse(filas[self.casos[1]['id']]['comparable'])
        self.assertFalse(filas['caso_nuevo']['comparable'])
        self.assertTrue(filas[self.casos[-1]['id']]['comparable'])

    def test_cli_validar_ejecutar_resumir_revisar_y_comparar(self):
        salida = self.ruta / 'primera.json'
        self.assertEqual(self.cli('validar')[0], 0)
        codigo, texto, _ = self.cli('ejecutar', '--salida', str(salida))
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(texto)['pendientes'], 9)
        self.assertEqual(self.cli('resumir', str(salida))[0], 0)
        revisada = self.ruta / 'revisada.json'
        self.assertEqual(self.cli('revisar', str(salida), '--caso', self.casos[0]['id'], '--estado', 'rechazado', '--autor', 'Revisor ficticio', '--observacion', 'Sólo prueba del flujo.', '--salida', str(revisada))[0], 0)
        comparacion = self.ruta / 'comparacion.json'
        self.assertEqual(self.cli('comparar', str(salida), str(revisada), '--salida', str(comparacion))[0], 0)
        self.assertTrue(comparacion.exists())

    def test_cli_no_reemplaza_entrada_y_no_expone_contenido_invalido(self):
        archivo = self.ruta / 'registro.json'
        evaluar.guardar_nuevo(archivo, evaluar.ejecutar(self.casos))
        antes = archivo.read_bytes()
        self.assertEqual(self.cli('revisar', str(archivo), '--caso', self.casos[0]['id'], '--estado', 'aprobado', '--autor', 'Revisor ficticio', '--observacion', 'Prueba.', '--salida', str(archivo))[0], 1)
        self.assertEqual(archivo.read_bytes(), antes)
        archivo.write_text('contenido privado inválido', encoding='utf-8')
        codigo, _, errores = self.cli('resumir', str(archivo))
        self.assertEqual(codigo, 1)
        self.assertNotIn('contenido privado', errores)


if __name__ == '__main__':
    unittest.main(verbosity=2)
