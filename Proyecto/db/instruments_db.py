# archivo: db/instruments_db.py

from typing import List, Optional
from models.instruments import FixedIncomeInstrument
from db.abstract_db import AbstractDatabase

class DBInstruments(AbstractDatabase):
    """
    DBInstruments maneja la persistencia de instrumentos financieros.
    Hereda de AbstractDatabase y cumple la interfaz común de las bases de datos.
    """

    def __init__(self, conexion: str):
        """
        Inicializa la base de datos de instrumentos.
        :param conexion: string de conexión o path a archivo/base de datos
        """
        self.conexion = conexion
        self.tabla_instrumentos: List[FixedIncomeInstrument] = []

    def guardar(self, instrumento: FixedIncomeInstrument):
        """
        Guarda un instrumento en la base interna.
        Si ya existe, lo actualiza.
        """
        pass

    def eliminar(self, id: int) -> bool:
        """
        Elimina un instrumento de la base por su ID.
        :param id: identificador del instrumento
        :return: True si se eliminó, False si no se encontró
        """
        pass

    def consultar(self, filtro: Optional[str] = None) -> List[FixedIncomeInstrument]:
        """
        Devuelve los instrumentos almacenados, opcionalmente filtrados por tipo, nombre, vencimiento, etc.
        :param filtro: criterio de filtrado
        :return: lista de FixedIncomeInstrument
        """
        pass

    def actualizar(self, instrumento: FixedIncomeInstrument):
        """
        Actualiza un instrumento existente en la base de datos.
        :param instrumento: instancia de FixedIncomeInstrument con datos actualizados
        """
        pass
