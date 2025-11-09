# auth/auth_api.py
"""
Módulo de autenticación de la API CotizAR.

Este archivo define un router de FastAPI para endpoints relacionados
con autenticación de usuarios (login, registro, verificación, etc.).
Actualmente se incluye un ejemplo mínimo para probar la integración.
"""

from fastapi import APIRouter, HTTPException

# Crear un router independiente para la autenticación
router = APIRouter(
    prefix="/auth",           # Prefijo común para todos los endpoints de este router
    tags=["Autenticación"]    # Categoría para la documentación automática de FastAPI
)

# Ejemplo de endpoint de prueba
@router.get("/ping")
async def ping():
    """
    Endpoint de prueba para verificar que el router funciona.
    
    GET /auth/ping
    Retorna un mensaje simple.
    """
    return {"mensaje": "pong"}

# Ejemplo de endpoint de login (simulación)
@router.post("/login")
async def login(usuario: str, clave: str):
    """
    Endpoint de login simulado.
    
    Parámetros:
    - usuario: nombre de usuario
    - clave: contraseña
    
    Retorna un mensaje de éxito si las credenciales son "admin"/"1234", 
    de lo contrario lanza un error 401.
    """
    if usuario == "admin" and clave == "1234":
        return {"mensaje": "Login exitoso"}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

# Ejemplo de endpoint de registro (simulación)
@router.post("/registro")
async def registro(usuario: str, clave: str):
    """
    Endpoint de registro simulado.
    
    Actualmente no guarda datos, solo devuelve un mensaje de confirmación.
    """
    return {"mensaje": f"Usuario '{usuario}' registrado correctamente"}
