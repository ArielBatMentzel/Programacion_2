# archivo: factory/fixed_income_factory.py

from abc import ABC, abstractmethod
from models.instruments import FixedIncomeInstrument, Bono, Letra, PlazoFijo
#Pase
from typing import Optional

class FinancialInstrumentFactory(ABC):
    """
    Clase abstracta para la creación de instrumentos financieros.
    Define la interfaz que deben implementar las fábricas concretas.
    """

    @abstractmethod
    def crear_instrumento(self, tipo: str, nombre: str, moneda: str, **kwargs) -> Optional[FixedIncomeInstrument]:
        """
        Crea un instrumento financiero según el tipo especificado.
        #:param tipo: tipo de instrumento ("bono", "letra", "plazo_fijo", "pase")
        :param nombre: nombre del instrumento
        :param moneda: moneda del instrumento
        :param kwargs: otros parámetros específicos del instrumento
        :return: instancia de FixedIncomeInstrument o None si el tipo no es válido
        """
        pass

class FixedIncomeInstrumentFactory(FinancialInstrumentFactory):
    """
    Fábrica concreta que implementa la creación de instrumentos de renta fija.
    """

    def crear_instrumento(self, tipo: str, nombre: str, moneda: str, **kwargs) -> Optional[FixedIncomeInstrument]:
        """
        Crea un instrumento concreto según el tipo.
        """
        tipo = tipo.lower()
        if tipo == "bono":
            return Bono(nombre=nombre, moneda=moneda, **kwargs)
        elif tipo == "letra":
            return Letra(nombre=nombre, moneda=moneda, **kwargs)
        elif tipo == "plazo_fijo":
            return PlazoFijo(nombre=nombre, moneda=moneda, **kwargs)
        # elif tipo == "pase":
        #     return Pase(nombre=nombre, moneda=moneda, **kwargs)
        else:
            return None