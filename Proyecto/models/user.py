# archivo: models/user.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ================================================================
# PRIMEROS MODELOS SIMPLES
# ================================================================

class User:
    """
    Representa un usuario del sistema.
    Atributos:
        - tipo: 'admin' o 'normal'
        - email: correo electrónico del usuario
        - nombre: nombre del usuario
        - otros atributos opcionales según necesidad.
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
    """
    Representa una sesión activa de un usuario.
    Atributos:
        - token: identificador único de la sesión
        - usuario_id: id del usuario (entero)
        - fecha_inicio: datetime de inicio de sesión
        - fecha_expiracion: datetime de expiración de la sesión
    """

    def __init__(self, token: str, usuario_id: int, fecha_inicio: datetime, fecha_expiracion: datetime):
        self.token = token
        self.usuario_id = usuario_id
        self.fecha_inicio = fecha_inicio
        self.fecha_expiracion = fecha_expiracion

# ================================================================
# MODELOS Pydantic (USADOS EN LA API / VALIDACIÓN DE DATOS)
# ================================================================

# Función de Pydantic Model: Nos permite definir la estructura de datos que se usarán en la FastApi. 
# Entonces validará los datos que lleguen y estandarizará lo que devuelve la API. 

class UsuarioCrear(BaseModel):
    """ Modelo para registrar un nuevo usuario. """
    
    nombre_usuario: str = Field(..., min_length=3, max_length=20)
    contraseña: str = Field(..., min_length=6)
    nombre_completo: Optional[str] = None


class UsuarioPublico(BaseModel):
    """ Modelo para mostrar datos públicos del usuario. """
    
    nombre_usuario: str
    nombre_completo: Optional[str] = None


class Token(BaseModel):
    """ Token JWT devuelto al iniciar sesión. """
    
    access_token: str
    token_type: str = "bearer"