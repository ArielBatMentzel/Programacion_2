from typing import List
from models.user import User
from models.instruments import FixedIncomeInstrument
from models.dolar import Dolar


class Alerta:
    """
    Representa una alerta que un usuario puede configurar.
    Evalúa condiciones sobre instrumentos financieros y el dólar,
    y notifica al usuario cuando se cumplen.
    """

    def __init__(self, usuario: User, condicion: str):
        """
        Inicializa la alerta.
        :param usuario: instancia de User que creó la alerta
        :param condicion: expresión o regla que define cuándo se dispara
        """
        self.usuario = usuario
        self.condicion = condicion

    def evaluar(
        self,
        dolar: Dolar,
        instrumentos: List[FixedIncomeInstrument]
    ) -> bool:
        """
        Evalúa si la condición de la alerta se cumple.
        :param dolar: objeto Dolar con valor actual
        :param instrumentos: lista de instrumentos a evaluar
        :return: True si la condición se cumple, False en caso contrario
        """
        pass

    def notificar(self):
        """
        Notifica al usuario que la condición de la alerta se cumplió.
        Podría ser un mensaje en pantalla, correo, o registro de log.
        """
        pass