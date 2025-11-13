# archivo: models/user.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ================================================================
# PRIMEROS MODELOS SIMPLES
# ================================================================

class User:
    """
    Representa un usuario del sistema.

    Atributos:
        email (str): correo electrónico del usuario.
        nombre (str): nombre del usuario.
        tipo (str): tipo de usuario ('admin' o 'normal').
    """

    def __init__(self, email: str, nombre: str, tipo: str = "normal"):
        """
        Inicializa un usuario.

        :param email: correo electrónico del usuario
        :param nombre: nombre del usuario
        :param tipo: tipo de usuario, por defecto 'normal'
        """
        self.email = email
        self.nombre = nombre
        self.tipo = tipo

    def solicitar_datos(self):
        """
        Método para que el usuario solicite datos desde la API o DB.

        :return: None (implementación pendiente)
        """
        pass

    def consultar_instrumentos(self):
        """
        Permite al usuario consultar instrumentos financieros.

        :return: None (implementación pendiente)
        """
        pass


class Session:
    """
    Representa una sesión activa de un usuario.

    Atributos:
        token (str): identificador único de la sesión
        usuario_id (int): id del usuario
        fecha_inicio (datetime): inicio de sesión
        fecha_expiracion (datetime): expiración de la sesión
    """

    def __init__(self, token: str, usuario_id: int, fecha_inicio: datetime,
                 fecha_expiracion: datetime):
        """
        Inicializa una sesión de usuario.

        :param token: identificador único de la sesión
        :param usuario_id: id del usuario asociado
        :param fecha_inicio: datetime de inicio de sesión
        :param fecha_expiracion: datetime de expiración de la sesión
        """
        self.token = token
        self.usuario_id = usuario_id
        self.fecha_inicio = fecha_inicio
        self.fecha_expiracion = fecha_expiracion


# ================================================================
# MODELOS Pydantic (USADOS EN LA API / VALIDACIÓN DE DATOS)
# ================================================================

class UsuarioCrear(BaseModel):
    """
    Modelo Pydantic para registrar un nuevo usuario.

    Atributos:
        nombre_usuario (str): nombre de usuario, mínimo 3 caracteres
        contraseña (str): contraseña, mínimo 6 caracteres
        nombre_completo (Optional[str]): nombre completo del usuario
        tipo (Optional[str]): tipo de usuario, por defecto 'normal'
        email (Optional[EmailStr]): correo electrónico válido
        telefono (Optional[int]): número de teléfono
    """
    nombre_usuario: str = Field(..., min_length=3, max_length=20)
    contraseña: str = Field(..., min_length=6)
    nombre_completo: Optional[str] = None
    tipo: Optional[str] = Field(default="normal")
    email: Optional[EmailStr] = None
    telefono: Optional[int] = None


class UsuarioPublico(BaseModel):
    """
    Modelo Pydantic para mostrar datos públicos del usuario.

    Atributos:
        nombre_usuario (str): nombre de usuario
        nombre_completo (Optional[str]): nombre completo
        tipo (str): tipo de usuario ('admin' o 'normal')
    """
    nombre_usuario: str
    nombre_completo: Optional[str] = None
    tipo: str


class Token(BaseModel):
    """
    Token JWT devuelto al iniciar sesión.

    Atributos:
        access_token (str): token de acceso
        token_type (str): tipo de token, por defecto 'bearer'
    """
    access_token: str
    token_type: str = "bearer"