"""
Script de terminal para dar de alta usuarios del CRM.

Se usa un script en lugar de un endpoint de registro porque el sistema es de uso
interno: los accesos los crea quien administra el sistema, no se auto-registra
cualquiera que encuentre la URL. Dejar un endpoint de registro abierto sería el
agujero más grande que podríamos dejar.

La contraseña se pide con getpass, que no la muestra en pantalla ni la deja en el
historial de comandos.

Uso:
    python crear_usuario.py
"""

import getpass
import sys

import database
import models
import seguridad

MIN_CARACTERES_PASSWORD = 8


def pedir_texto(etiqueta: str) -> str:
    """Pide un valor por consola y no acepta que quede vacío."""
    while True:
        valor = input(f"{etiqueta}: ").strip()
        if valor:
            return valor
        print("  No puede quedar vacío.")


def pedir_password() -> str:
    """
    Pide la contraseña dos veces y valida su largo.
    bcrypt solo considera los primeros 72 bytes, por eso se rechaza más que eso
    en lugar de recortarla en silencio.
    """
    while True:
        password = getpass.getpass("Contraseña: ")

        if len(password) < MIN_CARACTERES_PASSWORD:
            print(f"  Debe tener al menos {MIN_CARACTERES_PASSWORD} caracteres.")
            continue

        if len(password.encode("utf-8")) > seguridad.LIMITE_BYTES_PASSWORD:
            print(f"  No puede superar los {seguridad.LIMITE_BYTES_PASSWORD} bytes.")
            continue

        if password != getpass.getpass("Repetir contraseña: "):
            print("  Las contraseñas no coinciden.")
            continue

        return password


def pedir_rol() -> str:
    """
    Pide el rol del usuario. El valor por omisión es el de menos permisos.
    """
    print("\nRoles disponibles:")
    print("  1) ejecutivo  trabaja la cartera: leads, propiedades, tareas y asistente")
    print("  2) admin      además supervisa el sistema y el gasto del agente de IA")

    while True:
        opcion = input("Rol [1]: ").strip() or "1"
        if opcion in ("1", "ejecutivo"):
            return seguridad.ROL_EJECUTIVO
        if opcion in ("2", "admin"):
            return seguridad.ROL_ADMIN
        print("  Escribe 1 o 2.")


def main() -> int:
    # Asegura que la tabla de usuarios exista antes de insertar
    models.Base.metadata.create_all(bind=database.engine)

    print("Alta de usuario del CRM")
    print("-" * 40)

    nombre = pedir_texto("Nombre completo")
    email = pedir_texto("Correo").lower()

    db = database.SessionLocal()
    try:
        existente = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        if existente:
            print(f"\nYa existe un usuario con el correo {email}.")
            return 1

        rol = pedir_rol()
        password = pedir_password()

        usuario = models.Usuario(
            nombre=nombre,
            email=email,
            password_hash=seguridad.hashear_password(password),
            rol=rol,
            activo=True,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        print(f"\nUsuario creado. id={usuario.id}  correo={usuario.email}  rol={usuario.rol}")
        print("Ya puedes iniciar sesión en el CRM con estas credenciales.")
        return 0

    except Exception as error:
        db.rollback()
        print(f"\nNo se pudo crear el usuario: {error}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
