from abc import ABC, abstractmethod
from typing import Any, List, Optional


class AbstractDatabase(ABC):
    """
    Clase base abstracta para todas las bases de datos del proyecto.
    Define la interfaz que deben implementar todas las DB concretas
    (instrumentos, usuarios, etc.)
    """

    @abstractmethod
    def guardar(self, objeto: Any):
        """
        Guarda un objeto en la base de datos.
        Si ya existe, lo actualiza.
        :param objeto: instancia de cualquier entidad que se deba persistir
        """
        pass

    @abstractmethod
    def eliminar(self, id: Any) -> bool:
        """
        Elimina un objeto de la base de datos por su identificador.
        :param id: identificador del objeto
        :return: True si se eliminó, False si no se encontró
        """
        pass

    @abstractmethod
    def consultar(self, filtro: Optional[str] = None) -> List[Any]:
        """
        Devuelve los objetos almacenados en la base de datos.
        :param filtro: criterio de filtrado opcional
        :return: lista de objetos
        """
        pass