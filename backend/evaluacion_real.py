"""Planificación y ejecución explícita de lotes. No importa la API ni la base de datos."""
import copy
import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit

from casos_evaluacion import huella_caso, texto_valido, validar_caso


def fecha_actual():
    return datetime.now(timezone.utc).isoformat()


def decimal_valido(valor, positivo=False):
    if isinstance(valor, bool):
        raise ValueError('Importe inválido.')
    try:
        numero = Decimal(str(valor))
    except InvalidOperation as error:
        raise ValueError('Importe inválido.') from error
    if not numero.is_finite() or numero < 0 or (positivo and numero == 0):
        raise ValueError('El importe debe ser finito y positivo.')
    return numero


def huella(documento):
    return hashlib.sha256(json.dumps(documento, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def configuracion_actual(max_tokens):
    import ia
    if type(max_tokens) is not int or not 1 <= max_tokens <= 16000:
        raise ValueError('El evaluador admite entre 1 y 16000 tokens de salida por llamada.')
    direccion = urlsplit(ia.BASE_URL)
    if not ia.esta_configurada() or direccion.scheme not in ('http', 'https') or not direccion.hostname:
        raise ValueError('Falta una configuración válida del proveedor.')
    if direccion.username or direccion.password or direccion.query or direccion.fragment:
        raise ValueError('La dirección del proveedor no debe incluir credenciales ni parámetros privados.')
    if not texto_valido(ia.MODELO, 200):
        raise ValueError('Modelo inválido.')
    entrada = decimal_valido(ia.PRECIO_ENTRADA_POR_MILLON, positivo=True)
    salida = decimal_valido(ia.PRECIO_SALIDA_POR_MILLON, positivo=True)
    configuracion = {
        'modelo': ia.MODELO, 'proveedor': direccion.hostname,
        'endpoint_sha256': hashlib.sha256(ia.BASE_URL.encode()).hexdigest(),
        'precio_entrada_usd_millon': str(entrada), 'precio_salida_usd_millon': str(salida),
        'max_tokens_salida': max_tokens, 'temperatura': ia.TEMPERATURA,
        'codigo_ia_sha256': hashlib.sha256(Path(ia.__file__).read_bytes()).hexdigest(),
    }
    if ia.API_KEY and ia.API_KEY in json.dumps(configuracion):
        raise ValueError('La configuración pública contiene información privada.')
    return configuracion


def costo(tokens_entrada, tokens_salida, configuracion):
    return (Decimal(tokens_entrada) * decimal_valido(configuracion['precio_entrada_usd_millon'])
        + Decimal(tokens_salida) * decimal_valido(configuracion['precio_salida_usd_millon'])) / Decimal(1000000)


def crear_plan(casos, max_llamadas, presupuesto, max_tokens):
    import ia
    if type(max_llamadas) is not int or not 1 <= max_llamadas <= 100 or not 1 <= len(casos) <= max_llamadas:
        raise ValueError('El número de casos debe respetar el límite de 1 a 100 llamadas.')
    presupuesto = decimal_valido(presupuesto, positivo=True)
    configuracion = configuracion_actual(max_tokens)
    entradas = []
    identificadores = set()
    for caso in casos:
        validar_caso(caso)
        if caso['id'] in identificadores:
            raise ValueError('Caso duplicado.')
        identificadores.add(caso['id'])
        if ia.API_KEY and ia.API_KEY in json.dumps(caso):
            raise ValueError('Un caso contiene información privada de la configuración.')
        mensajes = [{'role': 'system', 'content': ia.INSTRUCCIONES_POR_TIPO[caso['tipo']]},
            {'role': 'user', 'content': caso['ficha']}]
        # Reserva conservadora por bytes y margen de formato. No es un tokenizador
        # del proveedor ni una garantía de facturación; el consumo se verifica después.
        entrada_estimada = len(json.dumps(mensajes, ensure_ascii=False).encode('utf-8')) + 1024
        entradas.append({'caso': copy.deepcopy(caso), 'huella_caso': huella_caso(caso),
            'tokens_entrada_estimados': entrada_estimada,
            'reserva_usd': str(costo(entrada_estimada, max_tokens, configuracion))})
    reserva = sum((decimal_valido(e['reserva_usd']) for e in entradas), Decimal(0))
    if reserva > presupuesto:
        raise ValueError('La reserva estimada supera el presupuesto del lote. Reduce los casos o los límites.')
    return {'version': 1, 'tipo': 'plan_evaluacion_real', 'lote_id': str(uuid.uuid4()),
        'fecha_utc': fecha_actual(), 'datos': 'ficticios', 'configuracion': configuracion,
        'max_llamadas': max_llamadas, 'presupuesto_usd': str(presupuesto),
        'reserva_total_usd': str(reserva), 'entradas': entradas}


def validar_plan(plan):
    if not isinstance(plan, dict) or type(plan.get('version')) is not int or plan['version'] != 1 or plan.get('tipo') != 'plan_evaluacion_real' or plan.get('datos') != 'ficticios':
        raise ValueError('Plan de lote inválido.')
    try:
        uuid.UUID(plan['lote_id'])
        if datetime.fromisoformat(plan['fecha_utc']).tzinfo is None:
            raise ValueError('Fecha sin zona horaria.')
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError('Identificación o fecha del plan inválida.') from error
    presupuesto = decimal_valido(plan.get('presupuesto_usd'), positivo=True)
    configuracion = plan.get('configuracion')
    if not isinstance(configuracion, dict) or not all(texto_valido(configuracion.get(k), 200)
        for k in ('modelo', 'proveedor', 'codigo_ia_sha256', 'endpoint_sha256')):
        raise ValueError('Configuración incompleta.')
    for campo in ('precio_entrada_usd_millon', 'precio_salida_usd_millon'):
        decimal_valido(configuracion.get(campo), positivo=True)
    if type(configuracion.get('max_tokens_salida')) is not int or not 1 <= configuracion['max_tokens_salida'] <= 16000:
        raise ValueError('Límite de salida inválido.')
    entradas = plan.get('entradas')
    limite = plan.get('max_llamadas')
    if type(limite) is not int or not 1 <= limite <= 100 or not isinstance(entradas, list) or not 1 <= len(entradas) <= limite:
        raise ValueError('Cantidad de llamadas inválida.')
    ids = set()
    for entrada in entradas:
        if not isinstance(entrada, dict):
            raise ValueError('Entrada de plan inválida.')
        caso = validar_caso(entrada.get('caso'))
        tokens = entrada.get('tokens_entrada_estimados')
        if caso['id'] in ids or entrada.get('huella_caso') != huella_caso(caso) or type(tokens) is not int or tokens <= 0:
            raise ValueError('Caso duplicado, alterado o sin estimación.')
        ids.add(caso['id'])
        if decimal_valido(entrada.get('reserva_usd')) != costo(tokens, configuracion['max_tokens_salida'], configuracion):
            raise ValueError('Reserva del caso inconsistente.')
    total = sum((decimal_valido(e['reserva_usd']) for e in entradas), Decimal(0))
    if total != decimal_valido(plan.get('reserva_total_usd')) or total > presupuesto:
        raise ValueError('Presupuesto inconsistente.')
    return plan


def _checkpoint(ruta, documento):
    # Sólo reemplaza el archivo que esta ejecución reservó con creación exclusiva.
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=ruta.parent, suffix='.tmp', delete=False) as archivo:
            temporal = Path(archivo.name)
            json.dump(documento, archivo, ensure_ascii=False, indent=2, allow_nan=False)
            archivo.flush(); os.fsync(archivo.fileno())
        os.replace(temporal, ruta)
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()


def totales(documento):
    conocidos = Decimal(0)
    incierto = False
    for r in documento['resultados']:
        if r['estado'] == 'no_ejecutado':
            continue
        valor = (r.get('consumo') or {}).get('costo_estimado_usd')
        if valor is None:
            incierto = True
        else:
            conocidos += decimal_valido(valor)
    return {'costo_conocido_usd': str(conocidos),
        'costo_total_estimado_usd': None if incierto else str(conocidos),
        'consumo_incompleto': incierto}


def ejecutar_real(ruta_plan, confirmacion, salida):
    import ia
    from schemas import PropuestaLlamada
    from pydantic import ValidationError
    plan = validar_plan(json.loads(Path(ruta_plan).read_text(encoding='utf-8')))
    if confirmacion != plan['lote_id']:
        raise ValueError('Confirma explícitamente el identificador del lote que revisaste.')
    actual = crear_plan([e['caso'] for e in plan['entradas']], plan['max_llamadas'], plan['presupuesto_usd'], plan['configuracion']['max_tokens_salida'])
    if actual['configuracion'] != plan['configuracion'] or actual['entradas'] != plan['entradas']:
        raise ValueError('La configuración o el código cambiaron. Prepara y revisa otro plan.')
    ruta = Path(salida)
    if ruta.exists() or not ruta.parent.is_dir():
        raise ValueError('La salida debe ser nueva y su carpeta debe existir.')
    bloqueo = Path(ruta_plan).parent / f'.lote-{plan["lote_id"]}.consumido.json'
    # Un plan no se reintenta ni se reutiliza: otro lote exige otra confirmación.
    with bloqueo.open('x', encoding='utf-8') as archivo:
        json.dump({'lote_id': plan['lote_id'], 'fecha_utc': fecha_actual()}, archivo)
    documento = {'version': 2, 'ejecucion_id': str(uuid.uuid4()), 'fecha_utc': fecha_actual(),
        'modo': 'real', 'datos': 'ficticios', 'configuracion': copy.deepcopy(plan['configuracion']),
        'plan': plan, 'huella_plan': huella(plan), 'confirmacion_lote': confirmacion,
        'llamadas_reales': 0, 'estado_lote': 'en_curso', 'motivo_detencion': None,
        'resultados': [{**copy.deepcopy(e), 'estado': 'no_ejecutado', 'respuesta': None,
            'error': None, 'revision': None, 'fecha_utc': None, 'consumo': None, 'modelo_respuesta': None}
            for e in plan['entradas']]}
    # Si no puede reservarse la evidencia, no se llama al proveedor.
    with ruta.open('x', encoding='utf-8') as archivo:
        json.dump(documento, archivo, ensure_ascii=False, indent=2, allow_nan=False)
    reserva_usada = Decimal(0)

    def limpio(valor, limite):
        texto = str(valor)
        if ia.API_KEY:
            texto = texto.replace(ia.API_KEY, '[clave omitida]')
        return texto[:limite]

    for resultado in documento['resultados']:
        reserva = decimal_valido(resultado['reserva_usd'])
        if documento['llamadas_reales'] >= plan['max_llamadas'] or reserva_usada + reserva > decimal_valido(plan['presupuesto_usd']):
            documento['motivo_detencion'] = 'limite_del_lote'
            break
        resultado['estado'] = 'en_curso'
        resultado['fecha_utc'] = fecha_actual()
        documento['llamadas_reales'] += 1
        reserva_usada += reserva
        _checkpoint(ruta, documento)
        try:
            respuesta = ia.generar_analisis(resultado['caso']['ficha'], resultado['caso']['tipo'],
                max_tokens=plan['configuracion']['max_tokens_salida'])
            texto = respuesta.get('texto')
            if not texto_valido(texto, 4000):
                raise ValueError('Respuesta vacía o inválida.')
            resultado['respuesta'] = limpio(texto, 4000)
            resultado['estado'] = 'respuesta'
            modelo = respuesta.get('modelo')
            resultado['modelo_respuesta'] = limpio(modelo, 200) if texto_valido(modelo, 200) else None
            entrada, salida_tokens = respuesta.get('tokens_entrada'), respuesta.get('tokens_salida')
            completos = all(type(t) is int and t >= 0 for t in (entrada, salida_tokens))
            mismo_modelo = modelo == plan['configuracion']['modelo']
            importe = costo(entrada, salida_tokens, plan['configuracion']) if completos and mismo_modelo else None
            resultado['consumo'] = {'tokens_entrada': entrada if type(entrada) is int and entrada >= 0 else None,
                'tokens_salida': salida_tokens if type(salida_tokens) is int and salida_tokens >= 0 else None,
                'costo_estimado_usd': str(importe) if importe is not None else None}
            if importe is None:
                documento['motivo_detencion'] = 'consumo_incompleto_o_modelo_distinto'
            else:
                reserva_usada += max(Decimal(0), importe - reserva)
                if entrada > resultado['tokens_entrada_estimados'] or salida_tokens > plan['configuracion']['max_tokens_salida']:
                    documento['motivo_detencion'] = 'consumo_supera_estimacion'
            if resultado['caso']['tipo'] == 'registro_llamada':
                try:
                    PropuestaLlamada.model_validate_json(texto)
                except ValidationError:
                    resultado['salida_invalida'] = resultado['respuesta']
                    resultado['respuesta'] = None
                    resultado['estado'] = 'error'
                    resultado['error'] = 'La propuesta de llamada no cumple el formato de la aplicación.'
                    documento['motivo_detencion'] = 'respuesta_invalida'
        except (Exception, KeyboardInterrupt) as error:
            resultado['estado'] = 'error'
            resultado['respuesta'] = None
            resultado['error'] = 'Ejecución interrumpida; consumo sin confirmar.' if isinstance(error, KeyboardInterrupt) else limpio(f'{type(error).__name__}: {error}', 1000)
            documento['motivo_detencion'] = 'error_del_proveedor_o_respuesta'
        _checkpoint(ruta, documento)
        if documento['motivo_detencion']:
            break
    documento['estado_lote'] = 'detenido' if documento['motivo_detencion'] else 'completado'
    _checkpoint(ruta, documento)
    return documento


def validar_contexto_real(documento):
    plan = validar_plan(documento.get('plan'))
    if documento.get('modo') != 'real' or documento.get('datos') != 'ficticios' or documento.get('huella_plan') != huella(plan) or documento.get('confirmacion_lote') != plan['lote_id']:
        raise ValueError('Identidad del lote inconsistente.')
    if documento.get('configuracion') != plan['configuracion'] or documento.get('estado_lote') not in ('en_curso', 'detenido', 'completado'):
        raise ValueError('Estado o configuración del lote inválida.')
    if documento['estado_lote'] == 'detenido' and not texto_valido(documento.get('motivo_detencion'), 200):
        raise ValueError('Falta el motivo de detención.')
    resultados = documento.get('resultados')
    if not isinstance(resultados, list) or len(resultados) != len(plan['entradas']):
        raise ValueError('Faltan resultados del lote.')
    intentadas = 0
    for r, e in zip(resultados, plan['entradas']):
        if not isinstance(r, dict) or any(r.get(k) != e[k] for k in ('caso', 'huella_caso', 'tokens_entrada_estimados', 'reserva_usd')):
            raise ValueError('Los resultados no corresponden al plan.')
        if r.get('estado') != 'no_ejecutado':
            intentadas += 1
            try:
                if datetime.fromisoformat(r['fecha_utc']).tzinfo is None:
                    raise ValueError('Fecha sin zona horaria.')
            except (KeyError, TypeError) as error:
                raise ValueError('Falta la fecha del intento.') from error
        consumo = r.get('consumo')
        if r.get('estado') == 'no_ejecutado' and any(r.get(k) is not None for k in ('fecha_utc', 'consumo', 'modelo_respuesta')):
            raise ValueError('Un caso no ejecutado no puede declarar consumo ni fecha de intento.')
        if r.get('estado') == 'respuesta' and not isinstance(consumo, dict):
            raise ValueError('Falta el estado del consumo de la respuesta.')
        if consumo is not None:
            if not isinstance(consumo, dict):
                raise ValueError('Consumo inválido.')
            tokens = [consumo.get(k) for k in ('tokens_entrada', 'tokens_salida')]
            if any(t is not None and (type(t) is not int or t < 0) for t in tokens):
                raise ValueError('Consumo inválido.')
            importe = consumo.get('costo_estimado_usd')
            if importe is not None and (None in tokens or r.get('modelo_respuesta') != plan['configuracion']['modelo'] or decimal_valido(importe) != costo(*tokens, plan['configuracion'])):
                raise ValueError('Costo inconsistente con el consumo.')
    llamadas = documento.get('llamadas_reales')
    if type(llamadas) is not int or llamadas != intentadas or llamadas > plan['max_llamadas']:
        raise ValueError('Número de intentos inconsistente.')
    if documento['estado_lote'] == 'completado' and (documento.get('motivo_detencion') is not None or any(r['estado'] != 'respuesta' or (r.get('consumo') or {}).get('costo_estimado_usd') is None for r in resultados)):
        raise ValueError('Un lote incompleto no puede figurar como completado.')
    return documento
