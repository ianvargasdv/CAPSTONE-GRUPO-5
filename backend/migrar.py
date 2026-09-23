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
