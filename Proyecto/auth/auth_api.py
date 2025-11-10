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
def registrar_usuario(datos: UsuarioCrear):                                #Modelo UsuarioCrear que contiene nombre, contraseña y nombre completo. 
    """Crea un nuevo usuario en la base de datos."""
    
    usuario_existente = db_usuarios.buscar_usuario_por_nombre(datos.nombre_usuario)
    if usuario_existente:
        raise HTTPException(
            status_code=400, detail= "El nombre de usuario ya existe."
        )

    contraseña_segura = crear_hash_contraseña(datos.contraseña)             #Hasheamos la contraseña para guardarla segura en la base de datos
    db_usuarios.crear_usuario(datos.nombre_usuario, contraseña_segura, datos.nombre_completo)

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
    token = crear_token_acceso({"sub": usuario["username"]})

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