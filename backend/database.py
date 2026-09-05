import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Obtener URL de la base de datos desde el entorno.
# Si no está configurada, usa SQLite local por defecto para facilitar pruebas rápidas.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./capstone.db")

# Si la base de datos es SQLite se requiere el argumento check_same_thread
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Creador de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para la definición de modelos
Base = declarative_base()


# Generador de sesión para inyección de dependencias en endpoints de FastAPI
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
