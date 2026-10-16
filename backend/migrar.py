"""
Aplica cambios de estructura sobre tablas que ya existen.

Hace falta porque models.Base.metadata.create_all() solo crea las tablas que
faltan: no agrega columnas nuevas a una tabla que ya está creada. Cuando se suma
una columna a un modelo existente, el código la espera y la base no la tiene.

No se usa una herramienta de migraciones como Alembic porque para el alcance del
proyecto son unos pocos cambios puntuales, y este script es más fácil de leer y de
explicar. Si los cambios de estructura se vuelven frecuentes, conviene reemplazarlo.

Cada instrucción usa IF NOT EXISTS, así que el script se puede correr las veces que
sea necesario sin romper nada ni perder datos.

Uso:
    python migrar.py
"""

import sys

from sqlalchemy import text

import database
from consolidar_asignaciones import consolidar_historial

# Cada entrada es (descripción, instrucción SQL). Se agregan al final, nunca se
# modifican las anteriores: así el script sirve también para una base recién creada.
CAMBIOS = [
    (
        "analisis_ia: tokens de entrada informados por el proveedor",
        "ALTER TABLE analisis_ia ADD COLUMN IF NOT EXISTS tokens_entrada INTEGER",
    ),
    (
        "analisis_ia: tokens de salida informados por el proveedor",
        "ALTER TABLE analisis_ia ADD COLUMN IF NOT EXISTS tokens_salida INTEGER",
    ),
    (
        "analisis_ia: costo estimado en dólares al momento de generarlo",
        "ALTER TABLE analisis_ia ADD COLUMN IF NOT EXISTS costo_estimado_usd DOUBLE PRECISION",
    ),
    (
        "usuarios: rol de acceso (admin o ejecutivo)",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'ejecutivo'",
    ),
    ("leads: tipo de operación", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS tipo_operacion VARCHAR(20)"),
    ("leads: presupuesto mínimo", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS presupuesto_min INTEGER"),
    ("leads: presupuesto máximo", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS presupuesto_max INTEGER"),
    ("leads: moneda del presupuesto", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS moneda VARCHAR(10)"),
    ("leads: comunas de interés", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS comunas_interes VARCHAR(300)"),
    ("leads: tipo de propiedad buscada", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS tipo_propiedad_buscada VARCHAR(50)"),
    ("leads: dormitorios mínimos", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS dormitorios_min INTEGER"),
    ("leads: baños mínimos", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS banos_min INTEGER"),
    ("leads: plazo de decisión", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS plazo_decision VARCHAR(30)"),
    ("leads: financiamiento", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS financiamiento VARCHAR(40)"),
    ("leads: origen", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS origen VARCHAR(40)"),
    ("leads: próxima acción", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS proxima_accion VARCHAR(250)"),
    ("leads: fecha de próxima acción", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS fecha_proxima_accion DATE"),
    ("leads: marcador de datos demo", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS es_demo BOOLEAN NOT NULL DEFAULT FALSE"),
    ("leads: ejecutivo responsable", "ALTER TABLE leads ADD COLUMN IF NOT EXISTS ejecutivo_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL"),
    (
        "oportunidades: tabla del pipeline comercial",
        """CREATE TABLE IF NOT EXISTS oportunidades (
            id SERIAL PRIMARY KEY,
            lead_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
            propiedad_id INTEGER REFERENCES propiedades(id) ON DELETE SET NULL,
            ejecutivo_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            tipo_operacion VARCHAR(20) NOT NULL,
            etapa VARCHAR(30) NOT NULL DEFAULT 'Contacto',
            valor_estimado INTEGER,
            moneda VARCHAR(10),
            probabilidad INTEGER NOT NULL DEFAULT 10,
            fecha_cierre_estimada DATE,
            fecha_cierre DATE,
            motivo_cierre VARCHAR(250),
            notas TEXT,
            fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )""",
    ),
    ("oportunidades: índice por lead", "CREATE INDEX IF NOT EXISTS ix_oportunidades_lead_id ON oportunidades (lead_id)"),
    ("oportunidades: índice por etapa", "CREATE INDEX IF NOT EXISTS ix_oportunidades_etapa ON oportunidades (etapa)"),
    (
        "visitas: agenda comercial",
        """CREATE TABLE IF NOT EXISTS visitas (
            id SERIAL PRIMARY KEY,
            lead_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
            propiedad_id INTEGER REFERENCES propiedades(id) ON DELETE SET NULL,
            oportunidad_id INTEGER REFERENCES oportunidades(id) ON DELETE SET NULL,
            ejecutivo_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            fecha_hora TIMESTAMPTZ NOT NULL,
            duracion_minutos INTEGER NOT NULL DEFAULT 60,
            estado VARCHAR(30) NOT NULL DEFAULT 'Programada',
            modalidad VARCHAR(20) NOT NULL DEFAULT 'Presencial',
            punto_encuentro VARCHAR(250),
            resultado TEXT,
            motivo_cancelacion VARCHAR(250),
            proxima_accion VARCHAR(250),
            fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )""",
    ),
    ("visitas: índice por fecha", "CREATE INDEX IF NOT EXISTS ix_visitas_fecha_hora ON visitas (fecha_hora)"),
    ("visitas: índice por ejecutivo", "CREATE INDEX IF NOT EXISTS ix_visitas_ejecutivo_id ON visitas (ejecutivo_id)"),
    ("visitas: índice por lead", "CREATE INDEX IF NOT EXISTS ix_visitas_lead_id ON visitas (lead_id)"),
    ("propiedades: tipo de operación", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS tipo_operacion VARCHAR(20)"),
    ("propiedades: moneda", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS moneda VARCHAR(10)"),
    ("propiedades: comuna", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS comuna VARCHAR(100)"),
    ("propiedades: dormitorios", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS dormitorios INTEGER"),
    ("propiedades: baños", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS banos INTEGER"),
    ("propiedades: código", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS codigo_interno VARCHAR(100)"),
    ("propiedades: superficie útil", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS superficie_util DOUBLE PRECISION"),
    ("propiedades: superficie total", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS superficie_total DOUBLE PRECISION"),
    ("propiedades: estacionamientos", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS estacionamientos INTEGER"),
    ("propiedades: bodega", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS bodega BOOLEAN"),
    ("propiedades: gastos comunes", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS gastos_comunes BIGINT"),
    ("propiedades: disponibilidad", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS fecha_disponibilidad DATE"),
    ("propiedades: descripción", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS descripcion TEXT"),
    ("propiedades: características", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS caracteristicas TEXT"),
    ("propiedades: fotografías", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS fotografias JSON NOT NULL DEFAULT '[]'"),
    ("propiedades: fotografía principal", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS foto_principal VARCHAR(2048)"),
    ("propiedades: propietario", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS propietario_nombre VARCHAR(100)"),
    ("propiedades: correo propietario", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS propietario_email VARCHAR(150)"),
    ("propiedades: teléfono propietario", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS propietario_telefono VARCHAR(20)"),
    ("propiedades: captador", "ALTER TABLE propiedades ADD COLUMN IF NOT EXISTS captador VARCHAR(100)"),
    (
        "asignaciones_lead: historial de responsables",
        """CREATE TABLE IF NOT EXISTS asignaciones_lead (
            id SERIAL PRIMARY KEY,
            lead_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
            lead_nombre VARCHAR(100) NOT NULL,
            anterior_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            anterior_nombre VARCHAR(100),
            nuevo_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            nuevo_nombre VARCHAR(100) NOT NULL,
            autor_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            autor_nombre VARCHAR(100) NOT NULL,
            fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""",
    ),
    ("asignaciones_lead: índice por lead", "CREATE INDEX IF NOT EXISTS ix_asignaciones_lead_lead_id ON asignaciones_lead (lead_id)"),
    ("asignaciones_lead: correo del autor en registros anteriores", "ALTER TABLE asignaciones_lead ADD COLUMN IF NOT EXISTS autor_email VARCHAR(150)"),
    ("asignaciones_lead: identificador del movimiento anterior", "ALTER TABLE asignaciones_lead ADD COLUMN IF NOT EXISTS historial_origen_id INTEGER"),
    ("asignaciones_lead: evitar importar dos veces el mismo movimiento", "CREATE UNIQUE INDEX IF NOT EXISTS ux_asignaciones_historial_origen ON asignaciones_lead (historial_origen_id)"),
]


def main() -> int:
    print("Aplicando cambios de estructura")
    print("-" * 60)

    aplicados = 0
    try:
        with database.engine.begin() as conexion:
            for descripcion, instruccion in CAMBIOS:
                conexion.execute(text(instruccion))
                print(f"  ok   {descripcion}")
                aplicados += 1
            importados = consolidar_historial(conexion)
    except Exception as error:
        # No mostrar parámetros SQL ni cadenas de conexión con datos privados.
        print(f"  FALLO: {type(error).__name__}. No se confirmó ningún cambio de esta ejecución.")
        return 1

    print("-" * 60)
    print(f"{aplicados} de {len(CAMBIOS)} instrucciones ejecutadas sin error.")
    print(f"Movimientos anteriores incorporados: {importados}. La tabla original se conserva.")
    print("El script es idempotente: volver a correrlo no genera cambios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
