"""
Cambia el rol de un usuario que ya existe.

Existe como script aparte porque cambiar permisos no debería ser algo que se haga
desde la interfaz: es una operación de administración del sistema, poco frecuente, y
dejarla fuera de la API significa que no hay un endpoint que alguien pueda usar para
darse permisos a sí mismo.

Uso:
    python cambiar_rol.py
"""

import sys

import database
import models
import seguridad


def main() -> int:
    db = database.SessionLocal()
    try:
        usuarios = db.query(models.Usuario).order_by(models.Usuario.id).all()
        if not usuarios:
            print("No hay usuarios registrados. Crea uno con: python crear_usuario.py")
            return 1

        print("Usuarios registrados")
        print("-" * 60)
        for u in usuarios:
            estado = "activo" if u.activo else "dado de baja"
            print(f"  id={u.id:<4} {u.email:<32} {u.rol:<10} {estado}")
        print("-" * 60)

        entrada = input("\nid del usuario a modificar: ").strip()
        if not entrada.isdigit():
            print("Eso no es un id.")
            return 1

        usuario = db.query(models.Usuario).filter(models.Usuario.id == int(entrada)).first()
        if usuario is None:
            print("No existe un usuario con ese id.")
            return 1

        print(f"\n{usuario.email} tiene el rol '{usuario.rol}'.")
        print("  1) ejecutivo")
        print("  2) admin")
        opcion = input("Nuevo rol: ").strip()

        if opcion in ("1", "ejecutivo"):
            nuevo = seguridad.ROL_EJECUTIVO
        elif opcion in ("2", "admin"):
            nuevo = seguridad.ROL_ADMIN
        else:
            print("Opción inválida. No se cambió nada.")
            return 1

        if nuevo == usuario.rol:
            print(f"Ya tenía el rol '{nuevo}'. No se cambió nada.")
            return 0

        # Evita quedarse sin ningún administrador en el sistema
        if usuario.rol == seguridad.ROL_ADMIN and nuevo != seguridad.ROL_ADMIN:
            otros_admin = (
                db.query(models.Usuario)
                .filter(
                    models.Usuario.rol == seguridad.ROL_ADMIN,
                    models.Usuario.id != usuario.id,
                    models.Usuario.activo.is_(True),
                )
                .count()
            )
            if otros_admin == 0:
                print("\nEs el único administrador activo. Si le quitas el rol, nadie")
                print("podría acceder a la supervisión del sistema. No se cambió nada.")
                return 1

        anterior = usuario.rol
        usuario.rol = nuevo
        db.commit()
        print(f"\n{usuario.email}: '{anterior}' -> '{nuevo}'")
        print("Hay que cerrar sesión y volver a entrar para que el cambio se refleje.")
        return 0

    except Exception as error:
        db.rollback()
        print(f"\nNo se pudo cambiar el rol: {error}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
