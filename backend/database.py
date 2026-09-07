import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Cargar variables de entorno del archivo .env de la carpeta backend
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
load_dotenv()

# Obtener URL de la base de datos PostgreSQL/Supabase desde el entorno
DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("Error: La variable DATABASE_URL no está definida en el archivo .env")

# Motor de conexión a PostgreSQL (Supabase)
engine = create_engine(DATABASE_URL)

# Creador de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para la definición de modelos ORM
Base = declarative_base()


# Generador de sesión para inyección de dependencias en endpoints de FastAPI
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
