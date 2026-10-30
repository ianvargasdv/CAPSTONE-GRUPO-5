"""Comprueba el modo real con transporte simulado; todos sus archivos son temporales."""
import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

import casos_evaluacion
import evaluar_asistente as evaluar
import evaluacion_real as real
import ia


class EvaluacionRealTest(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix='crm_evaluacion_real_test_')
        self.addCleanup(temporal.cleanup)
        self.carpeta = Path(temporal.name)
        self.ruta_plan = self.carpeta / 'plan.json'
        self.salida = self.carpeta / 'resultado.json'
        self.casos = casos_evaluacion.cargar_casos()
        for nombre, valor in {'BASE_URL': 'https://proveedor.example.test/v1', 'API_KEY': 'clave-ficticia-de-prueba-sin-valor',
                'MODELO': 'modelo-ficticio', 'PRECIO_ENTRADA_POR_MILLON': 0.1, 'PRECIO_SALIDA_POR_MILLON': 0.4,
                'MAX_TOKENS': 600, 'TEMPERATURA': 0.2}.items():
            parche = patch.object(ia, nombre, valor); parche.start(); self.addCleanup(parche.stop)
        red = patch('urllib.request.urlopen', side_effect=AssertionError('Las pruebas no permiten salir a la red'))
        self.red = red.start(); self.addCleanup(red.stop)
        generador = patch.object(ia, 'generar_analisis', return_value={
            'texto': 'Respuesta ficticia del doble de prueba.', 'modelo': 'modelo-ficticio',
            'tokens_entrada': 100, 'tokens_salida': 40, 'costo_estimado_usd': 0.000026})
        self.generador = generador.start(); self.addCleanup(generador.stop)

    def plan(self, casos=None):
        plan = real.crear_plan(self.casos[:2] if casos is None else casos, 11, '0.10', 600)
        evaluar.guardar_nuevo(self.ruta_plan, plan)
        return plan

    def ejecutar(self, plan=None):
        plan = self.plan() if plan is None else plan
        return real.ejecutar_real(self.ruta_plan, plan['lote_id'], self.salida)

    def cli(self, *argumentos):
        with redirect_stdout(io.StringIO()) as salida, redirect_stderr(io.StringIO()) as errores:
            codigo = evaluar.main(list(argumentos))
        return codigo, salida.getvalue(), errores.getvalue()

    def test_plan_no_llama_ni_expone_clave_y_cubre_cinco_funciones(self):
        plan = real.crear_plan(self.casos, 11, '0.10', 600)
        self.assertEqual(len(plan['entradas']), 11)
        self.assertEqual({e['caso']['tipo'] for e in plan['entradas']}, set(casos_evaluacion.TIPOS_ACTUALES))
        self.assertNotIn(ia.API_KEY, json.dumps(plan))
        self.assertGreater(real.decimal_valido(plan['reserva_total_usd']), 0)
        self.generador.assert_not_called(); self.red.assert_not_called()
        self.assertNotIn('database', sys.modules)
        self.assertNotIn('main', sys.modules)

    def test_limites_y_presupuestos_invalidos_no_llaman(self):
        for limite in [False, 0, -1, 1, 101]:
            with self.assertRaises(ValueError): real.crear_plan(self.casos[:2], limite, '0.1', 600)
        for importe in [False, 0, -1, 'NaN', 'Infinity', 'texto', '0.000000001']:
            with self.assertRaises(ValueError): real.crear_plan(self.casos, 11, importe, 600)
        for tokens in [False, 0, -1, 16001, '600']:
            with self.assertRaises(ValueError): real.crear_plan(self.casos, 11, '0.1', tokens)
        self.generador.assert_not_called()

    def test_precios_ausentes_o_invalidos_no_permiten_plan(self):
        for precio in [0, -1, float('nan'), float('inf')]:
            with patch.object(ia, 'PRECIO_ENTRADA_POR_MILLON', precio), self.assertRaises(ValueError):
                real.crear_plan(self.casos, 11, '0.1', 600)
        with patch.object(ia, 'MODELO', ''), self.assertRaises(ValueError):
            real.crear_plan(self.casos, 11, '0.1', 600)
        self.generador.assert_not_called()

    def test_no_guarda_urls_con_credenciales_y_detecta_clave_en_casos(self):
        for url in ['https://usuario:secreto@proveedor.example.test/v1', 'https://proveedor.example.test/v1?api_key=privado']:
            with patch.object(ia, 'BASE_URL', url), self.assertRaises(ValueError): real.crear_plan(self.casos, 11, '0.1', 600)
        casos = copy.deepcopy(self.casos)
        casos[0]['ficha'] += ia.API_KEY
        with self.assertRaises(ValueError): real.crear_plan(casos, 11, '0.1', 600)

    def test_sin_confirmacion_del_lote_no_escribe_ni_llama(self):
        self.plan()
        for confirmacion in ['', 'otro-lote', None]:
            with self.assertRaises(ValueError): real.ejecutar_real(self.ruta_plan, confirmacion, self.salida)
        self.assertFalse(self.salida.exists()); self.generador.assert_not_called()

    def test_cambio_de_modelo_precio_o_codigo_exige_nuevo_plan(self):
        plan = self.plan()
        for campo, valor in [('MODELO', 'otro-modelo'), ('PRECIO_SALIDA_POR_MILLON', 0.9)]:
            with patch.object(ia, campo, valor), self.assertRaises(ValueError):
                self.ejecutar(plan)
        modificado = copy.deepcopy(plan)
        modificado['configuracion']['codigo_ia_sha256'] = 'codigo-distinto'
        self.ruta_plan.write_text(json.dumps(modificado), encoding='utf-8')
        with self.assertRaises(ValueError): self.ejecutar(plan)
        self.generador.assert_not_called()

    def test_no_sobrescribe_salida_existente_antes_de_consumir(self):
        plan = self.plan()
        self.salida.write_text('archivo anterior', encoding='utf-8')
        with self.assertRaises(ValueError): self.ejecutar(plan)
        self.assertEqual(self.salida.read_text(), 'archivo anterior')
        self.generador.assert_not_called()

    def test_un_lote_no_puede_reutilizarse(self):
        plan = self.plan(); self.ejecutar(plan)
        llamadas = self.generador.call_count
        with self.assertRaises(FileExistsError):
            real.ejecutar_real(self.ruta_plan, plan['lote_id'], self.carpeta / 'otro.json')
        self.assertEqual(self.generador.call_count, llamadas)

    def test_evidencia_guardada_sigue_legible_tras_cambiar_configuracion_activa(self):
        original = self.ejecutar()
        with patch.object(ia, 'MODELO', 'modelo-nuevo'):
            leida = evaluar.leer_ejecucion(self.salida)
        self.assertEqual(leida, original)
        self.assertEqual(leida['configuracion']['modelo'], 'modelo-ficticio')

    def test_lote_registra_respuestas_consumo_y_revision_pendiente(self):
        documento = self.ejecutar()
        evaluar.validar_ejecucion(documento)
        self.assertEqual(documento['estado_lote'], 'completado')
        self.assertEqual(documento['llamadas_reales'], 2)
        self.assertEqual(self.generador.call_count, 2)
        self.assertEqual(self.generador.call_args.kwargs['max_tokens'], 600)
        for r in documento['resultados']:
            self.assertIsNone(r['revision'])
            self.assertEqual(r['consumo']['tokens_entrada'], 100)
            self.assertEqual(real.decimal_valido(r['consumo']['costo_estimado_usd']), real.Decimal('0.000026'))
        informe = evaluar.resumen(documento)
        self.assertEqual(informe['pendientes'], 2)
        self.assertEqual(informe['respuestas_reales_evaluadas'], 0)

    def test_checkpoint_existe_antes_de_cada_intento(self):
        respuesta = copy.deepcopy(self.generador.return_value)
        def comprobar(*args, **kwargs):
            guardado = json.loads(self.salida.read_text(encoding='utf-8'))
            self.assertEqual(guardado['llamadas_reales'], self.generador.call_count)
            self.assertEqual(guardado['resultados'][self.generador.call_count - 1]['estado'], 'en_curso')
            return respuesta
        self.generador.side_effect = comprobar
        self.ejecutar()

    def test_fallo_de_checkpoint_impide_primera_llamada(self):
        plan = self.plan()
        with patch.object(real, '_checkpoint', side_effect=OSError('Fallo de disco')), self.assertRaises(OSError):
            self.ejecutar(plan)
        self.generador.assert_not_called()

    def test_fallo_del_proveedor_detiene_sin_reintentos_ni_costo_cero(self):
        self.generador.side_effect = ia.IAFallo('Error simulado ' + ia.API_KEY)
        documento = self.ejecutar()
        evaluar.validar_ejecucion(documento)
        self.assertEqual(self.generador.call_count, 1)
        self.assertEqual(documento['estado_lote'], 'detenido')
        self.assertEqual(documento['resultados'][1]['estado'], 'no_ejecutado')
        self.assertNotIn(ia.API_KEY, self.salida.read_text(encoding='utf-8'))
        self.assertIsNone(evaluar.resumen(documento)['costo_total_estimado_usd'])

    def test_timeout_e_interrupcion_conservan_evidencia_parcial(self):
        for i, error in enumerate([TimeoutError('Espera agotada'), KeyboardInterrupt()]):
            with self.subTest(error=type(error).__name__):
                self.ruta_plan = self.carpeta / f'plan-{i}.json'; self.salida = self.carpeta / f'resultado-{i}.json'
                self.generador.side_effect = error
                documento = self.ejecutar()
                self.assertEqual(documento['estado_lote'], 'detenido')
                self.assertEqual(documento['llamadas_reales'], 1)
                evaluar.validar_ejecucion(documento)

    def test_consumo_ausente_o_invalido_detiene_sin_inventar_costo(self):
        for i, valor in enumerate([None, True, -1, '100']):
            self.ruta_plan = self.carpeta / f'plan-{i}.json'; self.salida = self.carpeta / f'resultado-{i}.json'
            self.generador.return_value['tokens_entrada'] = valor
            documento = self.ejecutar()
            self.assertEqual(documento['llamadas_reales'], 1)
            self.assertIsNone(documento['resultados'][0]['consumo']['costo_estimado_usd'])
            self.assertIsNone(evaluar.resumen(documento)['costo_total_estimado_usd'])

    def test_modelo_distinto_detiene_hasta_comprobar_sus_precios(self):
        self.generador.return_value['modelo'] = 'otro-modelo'
        documento = self.ejecutar()
        self.assertEqual(documento['estado_lote'], 'detenido')
        self.assertEqual(documento['llamadas_reales'], 1)
        self.assertTrue(evaluar.resumen(documento)['consumo_incompleto'])

    def test_consumo_superior_a_reserva_detiene_el_lote(self):
        plan = self.plan()
        self.generador.return_value['tokens_entrada'] = plan['entradas'][0]['tokens_entrada_estimados'] + 1
        documento = self.ejecutar(plan)
        self.assertEqual(documento['motivo_detencion'], 'consumo_supera_estimacion')
        self.assertEqual(self.generador.call_count, 1)

    def test_propuesta_de_llamada_invalida_es_error_y_no_aprobacion(self):
        plan = self.plan(self.casos[-2:])
        documento = self.ejecutar(plan)
        self.assertEqual(documento['resultados'][0]['estado'], 'error')
        self.assertIn('salida_invalida', documento['resultados'][0])
        self.assertEqual(evaluar.resumen(documento)['errores'], 1)
        self.assertEqual(evaluar.resumen(documento)['pendientes'], 0)
        with self.assertRaises(ValueError): evaluar.revisar(documento, self.casos[-2]['id'], 'aprobado', 'Revisor ficticio', 'No corresponde')

    def test_propuesta_valida_y_error_de_respuesta_vacia_se_distinguen(self):
        plan = self.plan(self.casos[-2:])
        self.generador.return_value['texto'] = json.dumps({'resumen': 'Falta aclarar dormitorios.', 'requisitos': [], 'proxima_accion': None})
        documento = self.ejecutar(plan)
        self.assertEqual(evaluar.resumen(documento)['pendientes'], 2)
        self.ruta_plan = self.carpeta / 'plan-vacio.json'; self.salida = self.carpeta / 'vacio.json'
        self.generador.return_value['texto'] = ''
        self.assertEqual(self.ejecutar()['estado_lote'], 'detenido')

    def test_revision_real_conserva_original_y_se_separa_de_simulacion(self):
        documento = self.ejecutar()
        revisado = evaluar.revisar(documento, self.casos[0]['id'], 'rechazado', 'Revisor ficticio de la prueba', 'Observación de prueba del registro, no una evaluación real.')
        self.assertIsNone(documento['resultados'][0]['revision'])
        self.assertEqual(evaluar.resumen(revisado)['rechazados_reales'], 1)
        self.assertEqual(evaluar.resumen(revisado)['aprobados_simulados'], 0)
        simulacion = evaluar.ejecutar(self.casos)
        comparacion = evaluar.comparar(simulacion, revisado)
        self.assertEqual(comparacion['modo'], 'mixto')
        self.assertTrue(all(not f['comparable'] for f in comparacion['casos']))

    def test_rechaza_evidencia_manipulada_y_plan_con_reservas_falsas(self):
        documento = self.ejecutar()
        for campo, valor in [('llamadas_reales', True), ('llamadas_reales', 0), ('huella_plan', 'otra'), ('modo', 'simulado')]:
            cambio = copy.deepcopy(documento); cambio[campo] = valor
            with self.assertRaises(ValueError): evaluar.validar_ejecucion(cambio)
        cambio = copy.deepcopy(documento); cambio['resultados'][0]['consumo']['costo_estimado_usd'] = '0'
        with self.assertRaises(ValueError): evaluar.validar_ejecucion(cambio)
        plan = copy.deepcopy(documento['plan']); plan['entradas'][0]['reserva_usd'] = '0'
        with self.assertRaises(ValueError): real.validar_plan(plan)

    def test_clave_no_aparece_en_respuesta_guardada_ni_en_resumen(self):
        self.generador.return_value['texto'] = 'Respuesta simulada que incluye accidentalmente ' + ia.API_KEY
        documento = self.ejecutar()
        self.assertNotIn(ia.API_KEY, self.salida.read_text(encoding='utf-8'))
        self.assertNotIn(ia.API_KEY, json.dumps(evaluar.resumen(documento)))

    def test_cli_planifica_sin_gasto_y_exige_confirmacion_nueva(self):
        codigo, texto, _ = self.cli('planificar-real', '--max-llamadas', '2', '--presupuesto-usd', '0.1',
            '--caso', self.casos[0]['id'], '--caso', self.casos[1]['id'], '--salida', str(self.ruta_plan))
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(texto)['llamadas_reales'], 0)
        self.generador.assert_not_called()
        codigo, _, _ = self.cli('ejecutar-real', '--plan', str(self.ruta_plan), '--confirmar-lote', 'otro', '--salida', str(self.salida))
        self.assertEqual(codigo, 1); self.generador.assert_not_called()
        plan = json.loads(self.ruta_plan.read_text(encoding='utf-8'))
        codigo, texto, _ = self.cli('ejecutar-real', '--plan', str(self.ruta_plan), '--confirmar-lote', plan['lote_id'], '--salida', str(self.salida))
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(texto)['pendientes'], 2)

    def test_cli_fallo_devuelve_estado_detenido_sin_exponer_credenciales(self):
        plan = self.plan()
        self.generador.side_effect = ia.IAFallo('Fallo simulado con ' + ia.API_KEY)
        codigo, texto, errores = self.cli('ejecutar-real', '--plan', str(self.ruta_plan), '--confirmar-lote', plan['lote_id'], '--salida', str(self.salida))
        self.assertEqual(codigo, 2)
        self.assertNotIn(ia.API_KEY, texto + errores)
        self.assertEqual(json.loads(texto)['estado_lote'], 'detenido')


if __name__ == '__main__':
    unittest.main(verbosity=2)
