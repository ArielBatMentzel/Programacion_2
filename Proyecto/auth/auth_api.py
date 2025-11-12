# api/auth_api.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth_service import (crear_hash_contraseña, verificar_contraseña, crear_token_acceso, obtener_usuario_actual)
from models.user import UsuarioCrear, UsuarioPublico, Token
from db.usuarios.users_db import DataBaseUsuario
from db.usuarios.users_db import RUTA_DB

router = APIRouter(prefix="/auth", tags=["Autenticación"])
db_usuarios = DataBaseUsuario(str(RUTA_DB))


# ================================
# REGISTRO DE NUEVOS USUARIOS
# ================================


@router.post("/registrar", status_code=201)
def registrar_usuario(datos: UsuarioCrear):
    """Crea un nuevo usuario en la base de datos."""
    
    # Verificar si ya existe
    usuario_existente = db_usuarios.buscar_usuario_por_nombre(datos.nombre_usuario)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")

    # Hashear contraseña
    contraseña_segura = crear_hash_contraseña(datos.contraseña)

    # Crear usuario
    db_usuarios.crear_usuario(
        nombre_usuario=datos.nombre_usuario,
        contraseña_hash=contraseña_segura,
        nombre_completo=datos.nombre_completo or "",
        tipo="normal",   # forzado a usuario normal
        email=datos.email,
        telefono=datos.telefono
    )

    return {"mensaje": "Usuario registrado correctamente"}



# ================================
# LOGIN Y GENERACIÓN DE TOKEN
# ================================


@router.post("/iniciar_sesion")
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Recibe: OAuth2PasswordRequestForm que espera los campos username y password.
    Función: Verifica credenciales, genera un token JWT y guarda la sesión.
    """

    from datetime import datetime, timedelta
    from models.user import Session  # Importá tu modelo de sesión

    usuario = db_usuarios.buscar_usuario_por_nombre(form_data.username)

    if not usuario or not verificar_contraseña(form_data.password, usuario["hashed_password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Crear token JWT
    #token = crear_token_acceso({"sub": usuario["username"]})

    token = crear_token_acceso({
    "sub": usuario["username"],
    "tipo": usuario["tipo"]
    })


    # Obtener ID del usuario (necesario para guardar sesión)
    usuario_id = db_usuarios.obtener_id_usuario(usuario["username"])
    if not usuario_id:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Crear y guardar sesión
    sesion = Session(
        token=token,
        usuario_id=usuario_id,
        fecha_inicio=str(datetime.now()),
        fecha_expiracion=str(datetime.now() + timedelta(hours=2))
    )
    db_usuarios.guardar_sesion(sesion)

    return {"access_token": token, "token_type": "bearer"}


# ================================
# RUTA PROTEGIDA (PERFIL)
# ================================


@router.get("/yo", response_model=UsuarioPublico)
async def obtener_perfil(usuario_actual: UsuarioPublico = Depends(obtener_usuario_actual)):
    
    """Devuelve los datos del usuario autenticado."""
    
    return usuario_actual

# ================================
# CERRAR SESIÓN
# ================================

@router.post("/cerrar_sesion", summary="Cerrar sesión del usuario actual")
def cerrar_sesion(usuario_actual: UsuarioPublico = Depends(obtener_usuario_actual)):

    """
    **Descripción:**  
    Finaliza la sesión activa del usuario autenticado eliminando su token de acceso.  
    Esto invalida el token actual, impidiendo su uso en futuras solicitudes protegidas.

    **Requiere:**  
    - Autenticación mediante token Bearer válido.  

    **Proceso:**  
    1. Se identifica al usuario autenticado a partir del token.  
    2. Se busca y elimina su sesión almacenada en la base de datos.  

    **Respuestas:**  
    - `200 OK`: Sesión cerrada correctamente.  
    - `400 Bad Request`: No existía una sesión activa para el usuario.  
    - `401 Unauthorized`: Token ausente o inválido.
    """
    exito = db_usuarios.eliminar_sesion_por_usuario(usuario_actual.nombre_usuario)
    if not exito:
        raise HTTPException(status_code=400, detail="No había sesión activa para este usuario.")
    return {"mensaje": "Sesión cerrada correctamente."}


# ================================
# USUARIO ACTUAL (PROTEGIDO)
# ================================

@router.get(
    "/usuario_actual",
    response_model=UsuarioPublico,
    summary="Obtener información del usuario autenticado"
)
def obtener_usuario(usuario_actual: UsuarioPublico = Depends(obtener_usuario_actual)):
    """
    **Descripción:**  
    Devuelve los datos públicos del usuario autenticado, obtenidos a partir del token de acceso actual.  

    **Requiere:**  
    - Autenticación mediante token Bearer válido.  

    **Retorna:**  
    - Nombre de usuario.  
    - Nombre completo (si está disponible).  

    **Respuestas:**  
    - `200 OK`: Devuelve los datos del usuario autenticado.  
    - `401 Unauthorized`: Token ausente, inválido o expirado.
    """
    return usuario_actual

############### BORAR USUARIO
@router.delete("/borrar_usuario/{username}", summary="Eliminar usuario (solo admin)")
def borrar_usuario(
    username: str,
    usuario_actual: UsuarioPublico = Depends(obtener_usuario_actual)
):
    """Elimina un usuario de la base de datos (solo accesible para administradores)."""

    if usuario_actual.tipo != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden borrar usuarios."
        )

    usuario_objetivo = db_usuarios.buscar_usuario_por_nombre(username)
    if not usuario_objetivo:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    usuario_id = db_usuarios.obtener_id_usuario(username)

    if username == usuario_actual.nombre_usuario:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario.")

    exito = db_usuarios.eliminar(usuario_id)
    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el usuario.")

    return {"mensaje": f"Usuario '{username}' eliminado correctamente."}