# auth_service.py

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from db.usuarios.users_db import DataBaseUsuario, RUTA_DB
from models.user import UsuarioPublico


# ======================
# CONFIGURACIÓN GENERAL
# ======================

CLAVE_SECRETA = "perro_chancho_unsam_2025_!9xM4"
ALGORITMO = "HS256"
MINUTOS_EXPIRACION_TOKEN = 60

# Configuración del sistema de hash
contexto_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 indica que el token se obtendrá desde /auth/iniciar_sesion
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/iniciar_sesion")


# ======================
# FUNCIONES DE SEGURIDAD
# ======================

def crear_hash_contraseña(contraseña: str) -> str:
    """
    Genera un hash seguro de la contraseña ingresada.
    
    Args:
        contraseña (str): Contraseña en texto plano.
    
    Returns:
        str: Hash seguro de la contraseña.
    """
    return contexto_hash.hash(contraseña)


def verificar_contraseña(
    contraseña_plana: str, contraseña_hasheada: str
) -> bool:
    """
    Compara una contraseña ingresada con su versión hasheada.
    
    Args:
        contraseña_plana (str): Contraseña en texto plano.
        contraseña_hasheada (str): Hash de la contraseña.
    
    Returns:
        bool: True si coinciden, False si no.
    """
    return contexto_hash.verify(contraseña_plana, contraseña_hasheada)


# ======================
# FUNCIONES PARA TOKENS JWT
# ======================

def crear_token_acceso(datos: dict, duracion: timedelta | None = None) -> str:
    """
    Crea un token JWT firmado con fecha de expiración.
    
    Args:
        datos (dict): Información a codificar en el token.
        duracion (timedelta | None): Duración opcional del token.
    
    Returns:
        str: Token JWT codificado.
    """
    datos_a_codificar = datos.copy()
    expiracion = datetime.now(timezone.utc) + (
        duracion or timedelta(minutes=MINUTOS_EXPIRACION_TOKEN)
    )
    datos_a_codificar.update({"exp": expiracion})
    token_codificado = jwt.encode(
        datos_a_codificar, CLAVE_SECRETA, algorithm=ALGORITMO
    )
    return token_codificado


async def obtener_usuario_actual(
    token: str = Depends(esquema_oauth2)
) -> UsuarioPublico:
    """
    Valida el JWT recibido y devuelve el usuario autenticado.
    
    Args:
        token (str): Token JWT del usuario.
    
    Returns:
        UsuarioPublico: Datos públicos del usuario autenticado.
    
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe.
    """
    error_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        carga_util = jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
        nombre_usuario: str = carga_util.get("sub")

        if nombre_usuario is None:
            raise error_credenciales

    except JWTError:
        raise error_credenciales

    db_usuarios = DataBaseUsuario(RUTA_DB)
    usuario = db_usuarios.buscar_usuario_por_nombre(nombre_usuario)

    if not usuario:
        raise error_credenciales

    return UsuarioPublico(
        nombre_usuario=usuario["username"],
        nombre_completo=usuario["full_name"],
        tipo=usuario["tipo"],
    )
