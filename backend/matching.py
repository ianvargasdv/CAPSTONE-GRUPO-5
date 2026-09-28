"""Matching determinista entre el perfil de un lead y el catálogo disponible."""

import unicodedata


PESOS = {
    "operacion": 20,
    "tipo": 20,
    "comuna": 20,
    "presupuesto": 25,
    "dormitorios": 10,
    "banos": 5,
}


def _normalizar(texto) -> str:
    if not texto:
        return ""
    base = unicodedata.normalize("NFKD", str(texto).strip().lower())
    return "".join(caracter for caracter in base if not unicodedata.combining(caracter))


def _criterio(nombre, coincide, detalle, peso):
    return {"nombre": nombre, "coincide": coincide, "detalle": detalle, "peso": peso}


def calcular_matching(lead, propiedad) -> dict:
    """
    Compara solo datos presentes en ambos registros.

    ``puntaje`` mide coincidencia entre los criterios evaluables y ``cobertura``
    indica qué porcentaje de los datos necesarios pudo compararse. Separarlos evita
    mostrar un 100% engañoso cuando solo existe un criterio cargado.
    """
    criterios = []
    faltantes = []

    if lead.tipo_operacion and propiedad.tipo_operacion:
        coincide = lead.tipo_operacion == propiedad.tipo_operacion
        criterios.append(_criterio(
            "Operación", coincide,
            f"Busca {lead.tipo_operacion.lower()} y la propiedad es para {propiedad.tipo_operacion.lower()}",
            PESOS["operacion"],
        ))
    else:
        faltantes.append("operación del lead o de la propiedad")

    if lead.tipo_propiedad_buscada and propiedad.tipo:
        coincide = lead.tipo_propiedad_buscada == propiedad.tipo
        criterios.append(_criterio(
            "Tipo de propiedad", coincide,
            f"Busca {lead.tipo_propiedad_buscada.lower()} y el inmueble es {propiedad.tipo.lower()}",
            PESOS["tipo"],
        ))
    else:
        faltantes.append("tipo de propiedad buscada")

    comunas = {
        _normalizar(comuna) for comuna in (lead.comunas_interes or "").split(",") if comuna.strip()
    }
    if comunas and propiedad.comuna:
        coincide = _normalizar(propiedad.comuna) in comunas
        criterios.append(_criterio(
            "Comuna", coincide,
            f"{propiedad.comuna} {'está' if coincide else 'no está'} entre las comunas declaradas",
            PESOS["comuna"],
        ))
    else:
        faltantes.append("comunas de interés o comuna de la propiedad")

    tiene_presupuesto = lead.presupuesto_min is not None or lead.presupuesto_max is not None
    if tiene_presupuesto and lead.moneda and propiedad.moneda:
        if lead.moneda != propiedad.moneda:
            coincide = False
            detalle = f"No se compara el precio: lead en {lead.moneda} y propiedad en {propiedad.moneda}"
        else:
            minimo_ok = lead.presupuesto_min is None or propiedad.precio >= lead.presupuesto_min
            maximo_ok = lead.presupuesto_max is None or propiedad.precio <= lead.presupuesto_max
            coincide = minimo_ok and maximo_ok
            detalle = (
                f"Precio {propiedad.precio:,} {propiedad.moneda} "
                f"{'dentro' if coincide else 'fuera'} del rango declarado"
            ).replace(",", ".")
        criterios.append(_criterio("Presupuesto", coincide, detalle, PESOS["presupuesto"]))
    else:
        faltantes.append("presupuesto o moneda comparable")

    if lead.dormitorios_min is not None and propiedad.dormitorios is not None:
        coincide = propiedad.dormitorios >= lead.dormitorios_min
        criterios.append(_criterio(
            "Dormitorios", coincide,
            f"Tiene {propiedad.dormitorios}; requiere al menos {lead.dormitorios_min}",
            PESOS["dormitorios"],
        ))
    else:
        faltantes.append("dormitorios requeridos o disponibles")

    if lead.banos_min is not None and propiedad.banos is not None:
        coincide = propiedad.banos >= lead.banos_min
        criterios.append(_criterio(
            "Baños", coincide,
            f"Tiene {propiedad.banos}; requiere al menos {lead.banos_min}",
            PESOS["banos"],
        ))
    else:
        faltantes.append("baños requeridos o disponibles")

    evaluado = sum(criterio["peso"] for criterio in criterios)
    obtenido = sum(criterio["peso"] for criterio in criterios if criterio["coincide"])
    puntaje = round(obtenido / evaluado * 100) if evaluado else None

    if puntaje is None:
        categoria = "Sin datos"
    elif puntaje >= 80:
        categoria = "Excelente"
    elif puntaje >= 60:
        categoria = "Buena"
    else:
        categoria = "Parcial"

    return {
        "propiedad": propiedad,
        "puntaje": puntaje,
        "cobertura": evaluado,
        "categoria": categoria,
        "criterios": criterios,
        "datos_faltantes": faltantes,
    }


def ordenar_matches(lead, propiedades):
    resultados = [calcular_matching(lead, propiedad) for propiedad in propiedades]
    return sorted(
        resultados,
        key=lambda item: (
            item["puntaje"] is not None,
            item["puntaje"] if item["puntaje"] is not None else -1,
            item["cobertura"],
        ),
        reverse=True,
    )
