# archivo: auth/auth_service.py

from typing import Optional
from models.user import User, Session
from Proyecto.db.usuarios.users_db import DataBaseUsuario
import hashlib
import secrets
from datetime import datetime, timedelta

class AuthService:
    """
    AuthService se encarga de:
    - Gestionar usuarios y sesiones
    - Autenticación y autorización
    - Recuperación de contraseñas
    """

    def __init__(self, db: DataBaseUsuario):
        """
        Inicializa el servicio con acceso a la base de usuarios.
        :param db: instancia de DataBaseUsuario
        """
        self.db = db
        self.sesiones_activas = {}  # dict[token: Session]

    def login(self, email: str, contrasena: str) -> Optional[str]:
        """
        Verifica credenciales y crea una sesión.
        :param email: correo del usuario
        :param contrasena: contraseña en texto plano
        :return: token de sesión si es válido, None si falla
        """
        pass

    def logout(self, token: str):
        """
        Termina la sesión activa asociada al token.
        """
        pass

    def crear_usuario(self, email: str, contrasena: str, tipo: str = "normal") -> User:
        """
        Crea un nuevo usuario y lo guarda en la base.
        :param email: correo del usuario
        :param contrasena: contraseña en texto plano
        :param tipo: "admin" o "normal"
        :return: instancia de User creada
        """
        pass

    def recuperar_contrasena(self, email: str) -> bool:
        """
        Inicia el flujo de recuperación de contraseña para el usuario.
        :param email: correo del usuario
        :return: True si existe usuario y se envió correo, False si no existe
        """
        pass

    def verificar_token(self, token: str) -> Optional[User]:
        """
        Verifica si un token es válido y devuelve el usuario asociado.
        :param token: string de sesión
        :return: User si es válido, None si no
        """
        pass

    def _generar_token(self, longitud: int = 32) -> str:
        """
        Genera un token seguro para sesiones.
        """
        return secrets.token_hex(longitud)

    def _hashear_contrasena(self, contrasena: str) -> str:
        """
        Devuelve la contraseña hasheada usando SHA-256.
        """
        return hashlib.sha256(contrasena.encode()).hexdigest()
