# archivo: models/instruments.py

from abc import ABC, abstractmethod

class FixedIncomeInstrument(ABC):
    """
    Clase abstracta para instrumentos financieros de renta fija.
    Define la interfaz que deben implementar todos los instrumentos.
    """

    def __init__(self, nombre: str, moneda: str):
        self.nombre = nombre
        self.moneda = moneda

    @abstractmethod
    def calculate(self) -> float:
        """Calcula el rendimiento o valor del instrumento."""
        pass

    @abstractmethod
    def actualizar(self, valor_dolar: float):
        """Actualiza los valores internos cuando cambia el dólar."""
        pass

# ------------------- Instrumentos concretos -------------------

class PlazoFijo(FixedIncomeInstrument):
    """
    Instrumento de renta fija: Plazo Fijo.
    Atributos:
        - dias: cantidad de días del plazo
    """
    def __init__(self, nombre: str, moneda: str, dias: int):
        super().__init__(nombre, moneda)
        self.dias = dias

    def calculate(self) -> float:
        pass

    def actualizar(self, valor_dolar: float):
        pass

class Letra(FixedIncomeInstrument):
    """
    Instrumento de renta fija: Letra.
    Atributos:
        - precio_actual: precio de la letra
        - dias_al_vencimiento: días restantes hasta el vencimiento
        - emisor: entidad emisora
    """
    def __init__(self, nombre: str, moneda: str, precio_actual: float, dias_al_vencimiento: int, emisor: str):
        super().__init__(nombre, moneda)
        self.precio_actual = precio_actual
        self.dias_al_vencimiento = dias_al_vencimiento
        self.emisor = emisor

    def calculate(self) -> float:
        pass

    def actualizar(self, valor_dolar: float):
        pass

class Bono(FixedIncomeInstrument):
    """
    Instrumento de renta fija: Bono.
    Atributos:
        - cupon: interés periódico
        - valor_nominal: valor nominal del bono
        - frecuencia_pago: frecuencia de pago de cupones
        - emisor: entidad emisora
    """
    def __init__(self, nombre: str, moneda: str, cupon: float, valor_nominal: float, frecuencia_pago: int, emisor: str):
        super().__init__(nombre, moneda)
        self.cupon = cupon
        self.valor_nominal = valor_nominal
        self.frecuencia_pago = frecuencia_pago
        self.emisor = emisor

    def calculate(self) -> float:
        pass

    def actualizar(self, valor_dolar: float):
        pass

class Pase(FixedIncomeInstrument):
    """
    Instrumento de renta fija: Pase.
    Atributos:
        - plazo_dias: duración del pase en días
        - tipo_pase: tipo de pase (por ejemplo, financiero, interbancario)
    """
    def __init__(self, nombre: str, moneda: str, plazo_dias: int, tipo_pase: str):
        super().__init__(nombre, moneda)
        self.plazo_dias = plazo_dias
        self.tipo_pase = tipo_pase

    def calculate(self) -> float:
        pass

    def actualizar(self, valor_dolar: float):
        pass
