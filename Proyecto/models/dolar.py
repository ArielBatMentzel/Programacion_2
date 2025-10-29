# archivo: models/dolar.py

from typing import List
from models.instruments import FixedIncomeInstrument

class Dolar:
    """
    Representa el valor del dólar y notifica automáticamente a los instrumentos
    financieros suscritos cuando cambia su valor.
    Implementa el patrón Observer.
    """

    def __init__(self, valor_inicial: float):
        """
        Inicializa el valor del dólar y la lista de observadores.
        :param valor_inicial: valor inicial del dólar
        """
        self.valor_actual = valor_inicial
        self.observadores: List[FixedIncomeInstrument] = []

    def suscribir(self, instrumento: FixedIncomeInstrument):
        """
        Suscribe un instrumento a las notificaciones de cambios del dólar.
        :param instrumento: instancia de FixedIncomeInstrument
        """
        if instrumento not in self.observadores:
            self.observadores.append(instrumento)

    def desuscribir(self, instrumento: FixedIncomeInstrument):
        """
        Quita un instrumento de las notificaciones.
        :param instrumento: instancia de FixedIncomeInstrument
        """
        if instrumento in self.observadores:
            self.observadores.remove(instrumento)

    def actualizar_valor(self, nuevo_valor: float):
        """
        Actualiza el valor del dólar y notifica a todos los instrumentos suscritos.
        :param nuevo_valor: nuevo valor del dólar
        """
        self.valor_actual = nuevo_valor
        self._notificar_observadores()

    def _notificar_observadores(self):
        """
        Llama al método de actualización de cada instrumento suscrito.
        """
        for instrumento in self.observadores:
            instrumento.actualizar(self.valor_actual)
