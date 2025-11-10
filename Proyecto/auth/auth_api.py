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
    Función: Verifica credenciales y devuelve un token JWT."""

    usuario = db_usuarios.buscar_usuario_por_nombre(form_data.username)            # Buscamos el usuario en la base de datos

    if not usuario or not verificar_contraseña(form_data.password, usuario["hashed_password"]): # Si no coinciden las credenciales tira error. 
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = crear_token_acceso({"sub": usuario["username"]})            # Creamos el token JWT con el nombre de usuario como sujeto
    return {"access_token": token, "token_type": "bearer"}



# ================================
# RUTA PROTEGIDA (PERFIL)
# ================================


@router.get("/yo", response_model=UsuarioPublico)
async def obtener_perfil(usuario_actual: UsuarioPublico = Depends(obtener_usuario_actual)):
    
    """Devuelve los datos del usuario autenticado."""
    
    return usuario_actual