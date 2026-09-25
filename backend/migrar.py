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
]


def main() -> int:
    print("Aplicando cambios de estructura")
    print("-" * 60)

    aplicados = 0
    with database.engine.begin() as conexion:
        for descripcion, instruccion in CAMBIOS:
            try:
                conexion.execute(text(instruccion))
                print(f"  ok   {descripcion}")
                aplicados += 1
            except Exception as error:
                print(f"  FALLO {descripcion}")
                print(f"        {error}")
                return 1

    print("-" * 60)
    print(f"{aplicados} de {len(CAMBIOS)} instrucciones ejecutadas sin error.")
    print("El script es idempotente: volver a correrlo no genera cambios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
