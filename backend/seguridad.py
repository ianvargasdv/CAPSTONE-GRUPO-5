"""
Funciones de seguridad del sistema: hasheo de contraseñas, emisión y validación
de tokens JWT, y la dependencia que identifica al usuario de cada petición.

Existe como módulo aparte para que main.py siga siendo solo endpoints y para que
toda la lógica sensible quede en un único lugar auditable.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import database
import models

# Se cargan las variables de entorno aquí también para que el módulo funcione
# sin depender del orden en que se importe
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "Error: la variable SECRET_KEY no está definida en el archivo .env. "
        "Genera una con: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
    )

ALGORITMO = "HS256"
TOKEN_EXPIRA_MINUTOS = int(os.getenv("TOKEN_EXPIRA_MINUTOS", "480"))

# bcrypt solo considera los primeros 72 bytes de la contraseña. En lugar de
# truncar en silencio, se rechazan las contraseñas más largas.
LIMITE_BYTES_PASSWORD = 72

# Hash señuelo usado cuando el email no existe. Permite gastar el mismo tiempo
# de cómputo que una verificación real y así no revelar, por la duración de la
# respuesta, si un correo está registrado o no.
_HASH_SENUELO = bcrypt.hashpw(b"valor-senuelo-sin-uso-real", bcrypt.gensalt())


def hashear_password(password: str) -> str:
    """
    Convierte una contraseña en su hash bcrypt.
    bcrypt genera y guarda un salt distinto en cada hash, así que dos usuarios
    con la misma contraseña quedan con hashes diferentes.
    """
    bytes_password = password.encode("utf-8")
    if len(bytes_password) > LIMITE_BYTES_PASSWORD:
        raise ValueError(
            f"La contraseña no puede superar los {LIMITE_BYTES_PASSWORD} bytes"
        )
    return bcrypt.hashpw(bytes_password, bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, hash_guardado: str) -> bool:
    """
    Compara una contraseña con un hash almacenado.
    Devuelve False ante cualquier entrada inválida en lugar de lanzar una
    excepción, para que un dato mal formado no se convierta en un error 500.
    """
    try:
        bytes_password = password.encode("utf-8")
        if len(bytes_password) > LIMITE_BYTES_PASSWORD:
            return False
        return bcrypt.checkpw(bytes_password, hash_guardado.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def gastar_tiempo_de_verificacion(password: str) -> None:
    """
    Ejecuta una comparación contra el hash señuelo. Se llama cuando el email no
    existe para que el login tarde lo mismo que con un email válido.
    """
    verificar_password(password, _HASH_SENUELO.decode("utf-8"))


def crear_token(usuario_id: int) -> str:
    """
    Emite un token JWT firmado que identifica al usuario.
    El campo sub guarda el id y exp define hasta cuándo es válido.
    """
    ahora = datetime.now(timezone.utc)
    contenido = {
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=TOKEN_EXPIRA_MINUTOS),
    }
    return jwt.encode(contenido, SECRET_KEY, algorithm=ALGORITMO)


# auto_error=False para poder construir el 401 con la cabecera WWW-Authenticate
esquema_bearer = HTTPBearer(
    auto_error=False,
    description="Token JWT obtenido en /api/auth/login",
)


def _no_autorizado() -> HTTPException:
    """
    Construye siempre el mismo 401, sin distinguir si faltó el token, si estaba
    mal formado o si expiró. Dar detalles ayudaría a un atacante.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer),
    db: Session = Depends(database.obtener_db),
) -> models.Usuario:
    """
    Dependencia que protege los endpoints.

    Recibe el token de la cabecera Authorization, lo valida y devuelve el usuario
    correspondiente. Si algo falla, corta la petición con un 401 y el endpoint
    nunca llega a ejecutarse.
    """
    if credenciales is None:
        raise _no_autorizado()

    try:
        contenido = jwt.decode(
            credenciales.credentials, SECRET_KEY, algorithms=[ALGORITMO]
        )
        usuario_id = int(contenido["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        # Cubre firma inválida, token expirado, sub ausente o no numérico
        raise _no_autorizado()

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

    # Un token puede seguir siendo válido criptográficamente aunque el usuario
    # haya sido dado de baja, por eso se revisa el estado en cada petición
    if not usuario or not usuario.activo:
        raise _no_autorizado()

    return usuario
