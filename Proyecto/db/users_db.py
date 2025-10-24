# archivo: db/users_db.py

from typing import Optional, List
from models.user import User, Session
from db.abstract_db import AbstractDatabase

class DataBaseUsuario(AbstractDatabase):
    """
    DataBaseUsuario maneja la persistencia de usuarios y sesiones.
    Hereda de AbstractDatabase y cumple la interfaz común de las bases de datos.
    """

    def __init__(self, conexion: str):
        """
        Inicializa la base de datos de usuarios.
        :param conexion: string de conexión o path a archivo/base de datos
        """
        self.conexion = conexion
        self.usuarios: List[User] = []
        self.sesiones: List[Session] = []

    def guardar(self, objeto: User):
        """
        Guarda un usuario en la base interna.
        Si ya existe, lo actualiza.
        :param objeto: instancia de User
        """
        pass

    def eliminar(self, id: str) -> bool:
        """
        Elimina un usuario o sesión de la base por su identificador.
        :param id: identificador del usuario o token de sesión
        :return: True si se eliminó, False si no se encontró
        """
        pass

    def consultar(self, filtro: Optional[str] = None) -> List[User]:
        """
        Devuelve los usuarios almacenados, opcionalmente filtrados.
        :param filtro: criterio de filtrado, por ejemplo email o tipo de usuario
        :return: lista de User
        """
        pass

    def actualizar(self, objeto: User):
        """
        Actualiza un usuario existente en la base de datos.
        :param objeto: instancia de User con datos actualizados
        """
        pass

    # Métodos específicos para sesiones
    def guardar_sesion(self, session: Session):
        """Guarda una sesión activa en la base interna"""
        pass

    def consultar_sesion(self, token: str) -> Optional[Session]:
        """Devuelve la sesión correspondiente al token dado"""
        pass

    def eliminar_sesion(self, token: str) -> bool:
        """Elimina una sesión activa por su token"""
        pass
