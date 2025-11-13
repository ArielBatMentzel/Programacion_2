from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from db.usuarios.users_db import DataBaseUsuario
from models.user import UsuarioPublico

# ======================
# CONFIGURACIÓN GENERAL
# ======================

CLAVE_SECRETA = "perro_chancho_unsam_2025_!9xM4"
# La Clave Secreta NO debe compartirse ni subirse a Github
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
    """Genera un hash seguro de la contraseña ingresada."""
    return contexto_hash.hash(contraseña)


def verificar_contraseña(contraseña_plana: str,
                         contraseña_hasheada: str) -> bool:
    """
    Compara una contraseña ingresada con su versión hasheada.
    Devuelve True si coinciden, False si no.
    """
    return contexto_hash.verify(contraseña_plana, contraseña_hasheada)


# ======================
# FUNCIONES PARA TOKENS JWT
# ======================


def crear_token_acceso(datos: dict, duracion: timedelta | None = None):
    """Crea un token JWT firmado con una fecha de expiración."""
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
    """Valida el JWT recibido y devuelve el usuario autenticado."""
    error_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificar el token con la clave y el algoritmo
        carga_util = jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
        nombre_usuario: str = carga_util.get("sub")
        if nombre_usuario is None:
            raise error_credenciales
    except JWTError:
        raise error_credenciales

    db_usuarios = DataBaseUsuario()
    usuario = db_usuarios.buscar_usuario_por_nombre(nombre_usuario)
    if not usuario:
        raise error_credenciales

    return UsuarioPublico(
        nombre_usuario=usuario["username"],
        nombre_completo=usuario["full_name"],
        tipo=usuario["tipo"]
    )