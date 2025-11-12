# archivo: Proyecto/models/instruments.py

from abc import ABC, abstractmethod
from datetime import date, timedelta
from utils.obtener_banda_cambiaria import obtener_banda_cambiaria


def _mes_banda_de_salida(
    mes_inicio: str | None, fecha_inicio: date | None, dias: int
) -> str:
    """Calcula el mes final sumando `dias` al mes o fecha inicial.

    Args:
        mes_inicio: mes inicial en formato 'YYYY-MM' (opcional)
        fecha_inicio: fecha de inicio (opcional)
        dias: cantidad de días a sumar

    Returns:
        Mes final en formato 'YYYY-MM'.
    """
    if mes_inicio:
        y, m = mes_inicio.split("-")
        start = date(int(y), int(m), 1)
    else:
        start = fecha_inicio or date.today()
    fin = start + timedelta(days=dias)
    return f"{fin.year:04d}-{fin.month:02d}"


# -------------------- Clase base --------------------


class FixedIncomeInstrument(ABC):
    """Clase base abstracta para instrumentos financieros de renta fija."""

    def __init__(self, nombre: str, moneda: str):
        """Inicializa un instrumento financiero.

        Args:
            nombre: nombre del instrumento
            moneda: moneda en la que se expresa (ARS, USD, etc.)
        """
        self.nombre = nombre
        self.moneda = moneda
        self.valor_dolar = None

    @abstractmethod
    def calcular_rendimiento(
        self, monto_inicial: float, tipo_cambio_actual: float
    ):
        """Calcula el rendimiento del instrumento.

        Args:
            monto_inicial: monto invertido
            tipo_cambio_actual: valor actual del dólar (si aplica)
        """
        pass

    def actualizar(self, valor_dolar: float):
        """Actualiza el valor de referencia del dólar.

        Args:
            valor_dolar: valor actual del dólar
        """
        self.valor_dolar = valor_dolar

    @abstractmethod
    def rendimiento_vs_banda(self, monto_inicial: float, mes: str = None):
        """Calcula métricas comparando con la banda cambiaria.

        Args:
            monto_inicial: monto invertido
            mes: mes de referencia (YYYY-MM)

        Returns:
            Diccionario con métricas comparativas.
        """
        pass


# -------------------- Plazo Fijo --------------------


class PlazoFijo(FixedIncomeInstrument):
    """Representa un Plazo Fijo."""

    def __init__(self, nombre: str, moneda: str, dias: int, tasa_tna: float):
        """Inicializa un Plazo Fijo.

        Args:
            nombre: nombre del plazo fijo
            moneda: moneda (ARS, USD)
            dias: duración en días
            tasa_tna: tasa nominal anual (%)
        """
        super().__init__(nombre, moneda)
        self.dias = dias
        self.tasa_tna = tasa_tna

    def calcular_rendimiento(
        self, monto_inicial: float, tipo_cambio_actual: float = None
    ):
        """Calcula rendimiento en pesos del Plazo Fijo.

        Args:
            monto_inicial: monto invertido
            tipo_cambio_actual: ignorado para Plazo Fijo

        Returns:
            Dict con TNA, TEA, monto final y ganancia en pesos.
        """
        n = 365 / self.dias
        tasa_efectiva_anual = (1 + self.tasa_tna / (100 * n)) ** n - 1
        rendimiento_periodo = (1 + tasa_efectiva_anual) ** (self.dias/365) - 1
        monto_final = monto_inicial * (1 + rendimiento_periodo)
        ganancia_pesos = monto_final - monto_inicial
        return {
            "tna": self.tasa_tna,
            "tea": round(tasa_efectiva_anual * 100, 2),
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
        }

    def rendimiento_vs_banda(self, monto_inicial: float, mes: str = None):
        """Calcula métricas vs techo de la banda cambiaria.

        Args:
            monto_inicial: monto invertido
            mes: mes de referencia (YYYY-MM)

        Returns:
            Dict con monto final en USD techo y dólar equilibrio.
        """
        _, techo = obtener_banda_cambiaria(mes)
        if not techo or techo <= 0:
            return None

        rend = self.calcular_rendimiento(monto_inicial)
        monto_final_pesos = rend["monto_final_pesos"]
        factor_ars = monto_final_pesos / monto_inicial
        dolar_break_even = factor_ars * techo
        monto_final_usd_techo = monto_final_pesos / techo

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2),
            "dolar_equilibrio": round(dolar_break_even, 2),
        }
