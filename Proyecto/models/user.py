# archivo: models/user.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ================================================================
# MODELOS SIMPLES (ENTIDADES INTERNAS)
# ================================================================


class User:
    """Representa un usuario del sistema.

    Atributos:
        email (str): correo electrónico del usuario.
        nombre (str): nombre del usuario.
        tipo (str): 'admin' o 'normal'.
    """

    def __init__(self, email: str, nombre: str, tipo: str = "normal"):
        self.email = email
        self.nombre = nombre
        self.tipo = tipo

    def solicitar_datos(self):
        """Método para que el usuario solicite datos desde la API o DB."""
        pass

    def consultar_instrumentos(self):
        """Permite al usuario consultar instrumentos financieros."""
        pass


class Session:
    """Representa una sesión activa de un usuario.

    Atributos:
        token (str): identificador único de la sesión.
        usuario_id (int): id del usuario.
        fecha_inicio (datetime): inicio de sesión.
        fecha_expiracion (datetime): expiración de la sesión.
    """

    def __init__(
        self,
        token: str,
        usuario_id: int,
        fecha_inicio: datetime,
        fecha_expiracion: datetime,
    ):
        self.token = token
        self.usuario_id = usuario_id
        self.fecha_inicio = fecha_inicio
        self.fecha_expiracion = fecha_expiracion


# ================================================================
# MODELOS Pydantic (VALIDACIÓN / API)
# ================================================================


class UsuarioCrear(BaseModel):
    """Modelo para registrar un nuevo usuario a través de la API.

    Valida y estandariza los datos recibidos.
    """

    nombre_usuario: str = Field(..., min_length=3, max_length=20)
    contraseña: str = Field(..., min_length=6)
    nombre_completo: Optional[str] = None
    tipo: Optional[str] = Field(default="normal")
    email: Optional[EmailStr] = None
    telefono: Optional[int] = None


class UsuarioPublico(BaseModel):
    """Modelo para exponer datos públicos de un usuario."""

    nombre_usuario: str
    nombre_completo: Optional[str] = None
    tipo: str  # 'admin' o 'normal'


class Token(BaseModel):
    """Representa un token JWT devuelto al iniciar sesión."""

    access_token: str
    token_type: str = "bearer"
