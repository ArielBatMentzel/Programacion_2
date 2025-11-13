# api/auth_api.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth_service import (
    crear_hash_contraseña,
    verificar_contraseña,
    crear_token_acceso,
    obtener_usuario_actual
)
from models.user import UsuarioCrear, UsuarioPublico
from db.usuarios.users_db import DataBaseUsuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])
db_usuarios = DataBaseUsuario()


# -------------------------------
# REGISTRO DE NUEVOS USUARIOS
# -------------------------------

@router.post("/registrar", status_code=201, summary="Registrar usuario")
def registrar_usuario(datos: UsuarioCrear):
    """
    Crea un usuario nuevo en la base de datos.

    Verifica duplicados y hashea la contraseña.
    """
    usuario_existente = db_usuarios.buscar_usuario_por_nombre(
        datos.nombre_usuario
    )
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya existe."
        )

    contraseña_segura = crear_hash_contraseña(datos.contraseña)

    db_usuarios.crear_usuario(
        nombre_usuario=datos.nombre_usuario,
        contraseña_hash=contraseña_segura,
        nombre_completo=datos.nombre_completo or "",
        tipo="normal",
        email=datos.email,
        telefono=datos.telefono
    )

    return {"mensaje": "Usuario registrado correctamente"}


# -------------------------------
# LOGIN Y GENERACIÓN DE TOKEN
# -------------------------------

@router.post("/iniciar_sesion", summary="Iniciar sesión")
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Verifica credenciales, genera token JWT y guarda la sesión.
    """
    from datetime import datetime, timedelta
    from models.user import Session

    usuario = db_usuarios.buscar_usuario_por_nombre(form_data.username)

    if not usuario or not verificar_contraseña(
        form_data.password,
        usuario["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    token = crear_token_acceso({
        "sub": usuario["username"],
        "tipo": usuario["tipo"]
    })

    usuario_id = db_usuarios.obtener_id_usuario(usuario["username"])
    if not usuario_id:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    sesion = Session(
        token=token,
        usuario_id=usuario_id,
        fecha_inicio=str(datetime.now()),
        fecha_expiracion=str(datetime.now() + timedelta(hours=2))
    )
    db_usuarios.guardar_sesion(sesion)

    return {"access_token": token, "token_type": "bearer"}


# -------------------------------
# USUARIO ACTUAL (PROTEGIDO)
# -------------------------------

@router.get(
    "/usuario_actual",
    response_model=UsuarioPublico,
    summary="Perfil usuario autenticado"
)
def obtener_usuario(usuario_actual: UsuarioPublico = Depends(
    obtener_usuario_actual
)):
    """Devuelve los datos públicos del usuario autenticado."""
    return usuario_actual


# -------------------------------
# CERRAR SESIÓN
# -------------------------------

@router.post("/cerrar_sesion", summary="Cerrar sesión usuario")
def cerrar_sesion(usuario_actual: UsuarioPublico = Depends(
    obtener_usuario_actual
)):
    """Finaliza la sesión activa del usuario autenticado."""
    exito = db_usuarios.eliminar_sesion_por_usuario(
        usuario_actual.nombre_usuario
    )
    if not exito:
        raise HTTPException(
            status_code=400,
            detail="No había sesión activa para este usuario."
        )
    return {"mensaje": "Sesión cerrada correctamente."}


# -------------------------------
# BORRAR USUARIO (solo admin)
# -------------------------------

@router.delete("/borrar_usuario/{username}", summary="Eliminar usuario")
def borrar_usuario(
    username: str,
    usuario_actual: UsuarioPublico = Depends(obtener_usuario_actual)
):
    """Elimina un usuario (solo administradores)."""
    if usuario_actual.tipo != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden borrar usuarios."
        )

    usuario_objetivo = db_usuarios.buscar_usuario_por_nombre(username)
    if not usuario_objetivo:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )

    usuario_id = db_usuarios.obtener_id_usuario(username)
    if username == usuario_actual.nombre_usuario:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminar tu propio usuario."
        )

    exito = db_usuarios.eliminar(usuario_id)
    if not exito:
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el usuario."
        )

    return {"mensaje": f"Usuario '{username}' eliminado correctamente."}