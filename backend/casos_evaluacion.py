"""Validación de casos ficticios; no importa la API, la base ni el proveedor."""
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

TIPOS = ('resumen', 'recomendacion', 'mensaje', 'preguntas')
CASOS_PREDETERMINADOS = Path(__file__).with_name('casos_asistente.json')


def texto_valido(valor, limite):
    return isinstance(valor, str) and bool(valor.strip()) and len(valor) <= limite


def cargar_casos(ruta=CASOS_PREDETERMINADOS):
    documento = json.loads(Path(ruta).read_text(encoding='utf-8'))
    if not isinstance(documento, dict) or type(documento.get('version')) is not int or documento['version'] != 1:
        raise ValueError('La versión del conjunto de casos debe ser 1.')
    if documento.get('datos') != 'ficticios':
        raise ValueError('El conjunto debe declarar datos ficticios.')
    casos = documento.get('casos')
    if not isinstance(casos, list) or not 8 <= len(casos) <= 100:
        raise ValueError('El conjunto debe contener entre 8 y 100 casos.')
    identificadores = set()
    for caso in casos:
        if not isinstance(caso, dict):
            raise ValueError('Cada caso debe ser un objeto.')
        identificador = caso.get('id')
        if not isinstance(identificador, str) or not re.fullmatch(r'[a-z][a-z0-9_]{2,79}', identificador):
            raise ValueError('Identificador de caso inválido.')
        if identificador in identificadores:
            raise ValueError('Hay identificadores de caso duplicados.')
        identificadores.add(identificador)
        if caso.get('tipo') not in TIPOS:
            raise ValueError('Tipo de análisis desconocido.')
        if not texto_valido(caso.get('fecha_referencia'), 40):
            raise ValueError('Falta la fecha de referencia del caso.')
        try:
            fecha = datetime.fromisoformat(caso['fecha_referencia'])
        except ValueError as error:
            raise ValueError('Fecha de referencia inválida.') from error
        if fecha.tzinfo is None:
            raise ValueError('La fecha debe incluir zona horaria.')
        if not texto_valido(caso.get('ficha'), 20000):
            raise ValueError('La ficha debe contener entre 1 y 20000 caracteres.')
        for campo in ('esperado', 'no_debe_afirmar'):
            criterios = caso.get(campo)
            if not isinstance(criterios, list) or not 1 <= len(criterios) <= 20:
                raise ValueError('Faltan criterios de revisión.')
            if not all(texto_valido(criterio, 1000) for criterio in criterios):
                raise ValueError('Criterio de revisión vacío o demasiado extenso.')
    cantidades = Counter(caso['tipo'] for caso in casos)
    if any(cantidades[tipo] < 2 for tipo in TIPOS):
        raise ValueError('Debe haber al menos dos casos por función del asistente.')
    return casos


def huella_caso(caso):
    """Permite reconocer cambios de ficha o criterios entre dos ejecuciones."""
    campos = {campo: caso[campo] for campo in ('id', 'tipo', 'fecha_referencia', 'ficha', 'esperado', 'no_debe_afirmar')}
    canonico = json.dumps(campos, ensure_ascii=False, sort_keys=True).encode('utf-8')
    return hashlib.sha256(canonico).hexdigest()
