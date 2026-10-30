"""Evaluación local: simulación predeterminada y lotes reales con confirmación explícita."""
import argparse
import copy
import hashlib
import json
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from casos_evaluacion import CASOS_PREDETERMINADOS, cargar_casos, huella_caso, texto_valido, validar_caso


def ahora():
    return datetime.now(timezone.utc).isoformat()


def guardar_nuevo(ruta, documento):
    """El modo exclusivo evita reemplazar evidencias, incluso por accidente."""
    contenido = json.dumps(documento, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        archivo.write(contenido)


def ejecutar(casos, fallos=()):
    identificadores = {caso['id'] for caso in casos}
    if set(fallos) - identificadores:
        raise ValueError('El caso seleccionado para simular un fallo no existe.')
    resultados = []
    for caso in casos:
        resultado = {
            'caso': copy.deepcopy(caso),
            'huella_caso': huella_caso(caso),
            'estado': 'error' if caso['id'] in fallos else 'respuesta',
            'respuesta': None if caso['id'] in fallos else
                '[SIMULACIÓN] Salida ficticia para comprobar el registro y su revisión. No es una respuesta del modelo.',
            'error': 'Fallo de proveedor simulado; no se realizó una llamada.' if caso['id'] in fallos else None,
            'revision': None,
        }
        resultados.append(resultado)
    return {
        'version': 1,
        'ejecucion_id': str(uuid.uuid4()),
        'fecha_utc': ahora(),
        'modo': 'simulado',
        'datos': 'ficticios',
        'configuracion': {
            'modelo': 'sin-modelo-simulacion',
            'proveedor': 'ninguno',
            'codigo_ia_sha256': hashlib.sha256(Path(__file__).with_name('ia.py').read_bytes()).hexdigest(),
        },
        'llamadas_reales': 0,
        'resultados': resultados,
    }


def _fecha_valida(valor):
    if not texto_valido(valor, 40):
        return False
    try:
        return datetime.fromisoformat(valor).tzinfo is not None
    except ValueError:
        return False


def validar_ejecucion(documento):
    if not isinstance(documento, dict) or type(documento.get('version')) is not int or documento['version'] not in (1, 2):
        raise ValueError('Versión de ejecución inválida.')
    if documento['version'] == 2:
        from evaluacion_real import validar_contexto_real
        validar_contexto_real(documento)
    else:
        if documento.get('modo') != 'simulado' or documento.get('datos') != 'ficticios':
            raise ValueError('Una ejecución histórica de versión 1 debe ser simulada y ficticia.')
        if type(documento.get('llamadas_reales')) is not int or documento['llamadas_reales'] != 0:
            raise ValueError('Una simulación no puede declarar llamadas reales.')
    if not _fecha_valida(documento.get('fecha_utc')):
        raise ValueError('Fecha de ejecución inválida.')
    try:
        uuid.UUID(documento['ejecucion_id'])
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise ValueError('Identificador de ejecución inválido.') from error
    configuracion = documento.get('configuracion')
    if not isinstance(configuracion, dict) or not all(
        texto_valido(configuracion.get(campo), 200)
        for campo in ('modelo', 'proveedor', 'codigo_ia_sha256')
    ):
        raise ValueError('Falta la configuración no secreta de la ejecución.')
    resultados = documento.get('resultados')
    if not isinstance(resultados, list) or not resultados:
        raise ValueError('La ejecución no contiene resultados.')
    ids = set()
    for resultado in resultados:
        if not isinstance(resultado, dict) or not isinstance(resultado.get('caso'), dict):
            raise ValueError('Resultado inválido.')
        caso = resultado['caso']
        validar_caso(caso)
        try:
            huella = huella_caso(caso)
            identificador = caso['id']
        except (KeyError, TypeError) as error:
            raise ValueError('Caso incompleto en los resultados.') from error
        if not isinstance(identificador, str) or identificador in ids or resultado.get('huella_caso') != huella:
            raise ValueError('Caso duplicado o huella del caso inconsistente.')
        ids.add(identificador)
        estado = resultado.get('estado')
        if estado == 'respuesta':
            if not texto_valido(resultado.get('respuesta'), 4000) or resultado.get('error') is not None:
                raise ValueError('La respuesta debe contener texto y no tener un error asociado.')
        elif estado == 'error':
            if resultado.get('respuesta') is not None or not texto_valido(resultado.get('error'), 1000):
                raise ValueError('Un error no puede contener una respuesta válida.')
        elif documento['version'] == 2 and estado in ('no_ejecutado', 'en_curso'):
            if resultado.get('respuesta') is not None or resultado.get('error') is not None or resultado.get('revision') is not None:
                raise ValueError('Un caso sin respuesta no puede tener revisión ni resultado inventado.')
        else:
            raise ValueError('Estado de resultado inválido.')
        revision = resultado.get('revision')
        if revision is not None:
            if estado != 'respuesta' or not isinstance(revision, dict):
                raise ValueError('No se puede aprobar o rechazar una ejecución fallida.')
            if revision.get('estado') not in ('aprobado', 'rechazado'):
                raise ValueError('Estado de revisión inválido.')
            if not texto_valido(revision.get('autor'), 150) or not texto_valido(revision.get('observacion'), 2000):
                raise ValueError('La revisión debe tener autor y observación.')
            if not _fecha_valida(revision.get('fecha_utc')):
                raise ValueError('Fecha de revisión inválida.')
    return documento


def leer_ejecucion(ruta):
    return validar_ejecucion(json.loads(Path(ruta).read_text(encoding='utf-8')))


def revisar(documento, caso_id, estado, autor, observacion):
    validar_ejecucion(documento)
    copia = copy.deepcopy(documento)
    resultado = next((r for r in copia['resultados'] if r['caso']['id'] == caso_id), None)
    if resultado is None:
        raise ValueError('El caso no pertenece a esta ejecución.')
    if resultado['revision'] is not None:
        raise ValueError('El caso ya tiene una revisión. Se conserva el registro original.')
    resultado['revision'] = {'estado': estado, 'autor': autor, 'observacion': observacion, 'fecha_utc': ahora()}
    validar_ejecucion(copia)
    return copia


def resumen(documento):
    validar_ejecucion(documento)
    conteo = Counter()
    for resultado in documento['resultados']:
        if resultado['estado'] == 'error':
            conteo['errores'] += 1
        elif resultado['estado'] in ('no_ejecutado', 'en_curso'):
            conteo[resultado['estado']] += 1
        elif resultado['revision'] is None:
            conteo['pendientes'] += 1
        else:
            conteo[resultado['revision']['estado']] += 1
    real = documento['modo'] == 'real'
    informe = {
        'ejecucion_id': documento['ejecucion_id'],
        'modo': documento['modo'],
        'total': len(documento['resultados']),
        'aprobados_simulados': 0 if real else conteo['aprobado'],
        'rechazados_simulados': 0 if real else conteo['rechazado'],
        'aprobados_reales': conteo['aprobado'] if real else 0,
        'rechazados_reales': conteo['rechazado'] if real else 0,
        'errores': conteo['errores'],
        'pendientes': conteo['pendientes'],
        'no_ejecutados': conteo['no_ejecutado'], 'en_curso': conteo['en_curso'],
        'respuestas_reales_evaluadas': conteo['aprobado'] + conteo['rechazado'] if real else 0,
        'alcance': 'Revisión de una muestra de respuestas reales; no acredita precisión general.' if real else 'Comprueba el registro y la revisión. No mide la calidad del modelo real.',
    }
    if real:
        from evaluacion_real import totales
        informe.update(totales(documento))
        informe.update(estado_lote=documento['estado_lote'], motivo_detencion=documento['motivo_detencion'], llamadas_reales=documento['llamadas_reales'])
    return informe


def comparar(anterior, actual):
    validar_ejecucion(anterior)
    validar_ejecucion(actual)
    previos = {r['caso']['id']: r for r in anterior['resultados']}
    actuales = {r['caso']['id']: r for r in actual['resultados']}
    filas = []
    for identificador in sorted(previos.keys() | actuales.keys()):
        antes, despues = previos.get(identificador), actuales.get(identificador)
        mismo_modo = anterior['modo'] == actual['modo']
        comparable = mismo_modo and antes is not None and despues is not None and antes['huella_caso'] == despues['huella_caso']
        filas.append({
            'caso': identificador,
            'comparable': comparable,
            'motivo': 'misma ficha y criterios' if comparable else 'modos distintos' if not mismo_modo else 'caso nuevo, eliminado o modificado',
            'estado_anterior': antes['estado'] if antes else None,
            'estado_actual': despues['estado'] if despues else None,
            'revision_anterior': antes['revision']['estado'] if antes and antes['revision'] else None,
            'revision_actual': despues['revision']['estado'] if despues and despues['revision'] else None,
        })
    return {
        'anterior': anterior['ejecucion_id'], 'actual': actual['ejecucion_id'], 'modo': anterior['modo'] if anterior['modo'] == actual['modo'] else 'mixto',
        'codigo_ia_igual': anterior['configuracion']['codigo_ia_sha256'] == actual['configuracion']['codigo_ia_sha256'],
        'casos': filas,
        'alcance': 'No se equipara una simulación con una respuesta real ni se infiere precisión general.',
    }


def main(argumentos=None):
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest='comando', required=True)
    validar = comandos.add_parser('validar', help='Validar casos sin llamar al proveedor.')
    validar.add_argument('--casos', type=Path, default=CASOS_PREDETERMINADOS)
    ejecutar_cli = comandos.add_parser('ejecutar', help='Ejecutar una simulación sin red ni base de datos.')
    ejecutar_cli.add_argument('--casos', type=Path, default=CASOS_PREDETERMINADOS)
    ejecutar_cli.add_argument('--salida', type=Path, required=True)
    ejecutar_cli.add_argument('--fallo-caso', action='append', default=[], help='Simular un error en este caso.')
    plan_cli = comandos.add_parser('planificar-real', help='Preparar un lote y su estimación sin llamar al proveedor.')
    plan_cli.add_argument('--casos', type=Path, default=CASOS_PREDETERMINADOS)
    plan_cli.add_argument('--caso', action='append', default=[], help='Seleccionar explícitamente un caso; sin este argumento incluye el conjunto completo.')
    plan_cli.add_argument('--max-llamadas', type=int, required=True)
    plan_cli.add_argument('--presupuesto-usd', required=True)
    plan_cli.add_argument('--max-tokens-salida', type=int)
    plan_cli.add_argument('--salida', type=Path, required=True)
    real_cli = comandos.add_parser('ejecutar-real', help='Ejecutar un plan nuevo sólo después de autorizar ese lote y su gasto estimado.')
    real_cli.add_argument('--plan', type=Path, required=True)
    real_cli.add_argument('--confirmar-lote', required=True)
    real_cli.add_argument('--salida', type=Path, required=True)
    revisar_cli = comandos.add_parser('revisar', help='Crear un archivo nuevo con una revisión humana explícita.')
    revisar_cli.add_argument('archivo', type=Path)
    revisar_cli.add_argument('--caso', required=True)
    revisar_cli.add_argument('--estado', required=True, choices=('aprobado', 'rechazado'))
    revisar_cli.add_argument('--autor', required=True)
    revisar_cli.add_argument('--observacion', required=True)
    revisar_cli.add_argument('--salida', type=Path, required=True)
    resumir_cli = comandos.add_parser('resumir')
    resumir_cli.add_argument('archivo', type=Path)
    comparar_cli = comandos.add_parser('comparar')
    comparar_cli.add_argument('anterior', type=Path)
    comparar_cli.add_argument('actual', type=Path)
    comparar_cli.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args(argumentos)
    try:
        if args.comando == 'validar':
            salida = {'casos_validos': len(cargar_casos(args.casos)), 'llamadas_reales': 0}
        elif args.comando == 'ejecutar':
            documento = ejecutar(cargar_casos(args.casos), args.fallo_caso)
            guardar_nuevo(args.salida, documento)
            salida = resumen(documento)
        elif args.comando == 'planificar-real':
            from evaluacion_real import crear_plan
            import ia
            casos = cargar_casos(args.casos)
            if args.caso:
                if len(set(args.caso)) != len(args.caso) or set(args.caso) - {c['id'] for c in casos}:
                    raise ValueError('Selección de casos inválida.')
                casos = [c for c in casos if c['id'] in args.caso]
            plan = crear_plan(casos, args.max_llamadas, args.presupuesto_usd,
                ia.MAX_TOKENS if args.max_tokens_salida is None else args.max_tokens_salida)
            guardar_nuevo(args.salida, plan)
            salida = {'lote_id': plan['lote_id'], 'casos': [e['caso']['id'] for e in plan['entradas']],
                'modelo': plan['configuracion']['modelo'], 'llamadas_reales': 0,
                'reserva_estimada_usd': plan['reserva_total_usd'], 'presupuesto_usd': plan['presupuesto_usd'],
                'aviso': 'Plan sin ejecutar. La estimación no es una garantía de facturación. Requiere autorización nueva para este lote.'}
        elif args.comando == 'ejecutar-real':
            from evaluacion_real import ejecutar_real
            documento = ejecutar_real(args.plan, args.confirmar_lote, args.salida)
            salida = resumen(documento)
        elif args.comando == 'revisar':
            documento = revisar(leer_ejecucion(args.archivo), args.caso, args.estado, args.autor, args.observacion)
            guardar_nuevo(args.salida, documento)
            salida = resumen(documento)
        elif args.comando == 'resumir':
            salida = resumen(leer_ejecucion(args.archivo))
        else:
            salida = comparar(leer_ejecucion(args.anterior), leer_ejecucion(args.actual))
            guardar_nuevo(args.salida, salida)
        print(json.dumps(salida, ensure_ascii=False, indent=2))
        return 2 if args.comando == 'ejecutar-real' and documento['estado_lote'] != 'completado' else 0
    except (ValueError, OSError, KeyError, TypeError):
        # No imprimir contenido de archivos ni mensajes externos en un error del CLI.
        print('No se pudo completar: revisa los datos, las rutas y que la salida no exista.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
