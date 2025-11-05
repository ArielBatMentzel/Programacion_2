# archivo: Proyecto/models/instruments.py

from abc import ABC, abstractmethod
from utils.obtener_banda_cambiaria import obtener_banda_cambiaria

# -------------------- Clase base --------------------

class FixedIncomeInstrument(ABC):
    """
    Clase abstracta para instrumentos financieros de renta fija.
    Define la interfaz que deben implementar todos los instrumentos.
    """

    def __init__(self, nombre: str, moneda: str):
        self.nombre = nombre
        self.moneda = moneda
        self.valor_dolar = None  # último valor conocido

    @abstractmethod
    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float):
        pass

    @abstractmethod
    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar
        pass

    @abstractmethod
    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None):
        """Calcula el rendimiento considerando el techo de la banda cambiaria."""
        pass

# -------------------- Plazo Fijo --------------------

class PlazoFijo(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str, dias: int, tasa_tna: float):
        super().__init__(nombre, moneda)
        self.dias = dias
        self.tasa_tna = tasa_tna

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float):
        n = 365 / self.dias
        tasa_efectiva_anual = (1 + self.tasa_tna / (100 * n)) ** n - 1
        rendimiento_periodo = (1 + tasa_efectiva_anual) ** (self.dias / 365) - 1
        monto_final = monto_inicial * (1 + rendimiento_periodo)
        ganancia_pesos = monto_final - monto_inicial
        ganancia_usd = ganancia_pesos / tipo_cambio_actual if tipo_cambio_actual else None
        return {
            "tna": self.tasa_tna,
            "tea": round(tasa_efectiva_anual * 100, 2),
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd else None
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None):
        _, techo = obtener_banda_cambiaria(fecha)
        if not techo:
            return None
        rend = self.calcular_rendimiento(monto_inicial, techo)
        dolar_equilibrio = rend["monto_final_pesos"] / monto_inicial
        return {
            "monto_final_usd_techo": round(rend["ganancia_usd"] + monto_inicial / techo, 2),
            "dolar_equilibrio": round(dolar_equilibrio, 2)
        }

# -------------------- Bono --------------------

class Bono(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str, ultimo=None,
                 dia_pct=None, mes_pct=None, anio_pct=None):
        super().__init__(nombre, moneda)
        self.ultimo = ultimo
        self.dia_pct = dia_pct
        self.mes_pct = mes_pct
        self.anio_pct = anio_pct

    def _estimacion_rend_anual(self):
        posibles = []
        if self.anio_pct:
            posibles.append(self.anio_pct / 100)
        if self.mes_pct:
            posibles.append((1 + self.mes_pct / 100) ** 12 - 1)
        if self.dia_pct:
            posibles.append((1 + self.dia_pct / 100) ** 365 - 1)
        return sum(posibles) / len(posibles) if posibles else 0.0

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float):
        r_anual = self._estimacion_rend_anual()
        r_periodo = (1 + r_anual) ** (30 / 365) - 1
        monto_final = monto_inicial * (1 + r_periodo)
        ganancia_pesos = monto_final - monto_inicial
        ganancia_usd = ganancia_pesos / tipo_cambio_actual if tipo_cambio_actual else None
        return {
            "r_anual_pct": round(r_anual * 100, 2),
            "r_mensual_pct": round(r_periodo * 100, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd else None
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None):
        _, techo = obtener_banda_cambiaria(fecha)
        if not techo:
            return None
        rend = self.calcular_rendimiento(monto_inicial, techo)
        dolar_equilibrio = (rend["ganancia_pesos"] + monto_inicial) / monto_inicial
        return {
            "monto_final_usd_techo": round(rend["ganancia_usd"] + monto_inicial / techo, 2),
            "dolar_equilibrio": round(dolar_equilibrio, 2)
        }

# -------------------- Letra --------------------

class Letra(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str, precio_actual: float,
                 dias_al_vencimiento: int, valor_nominal: float = 100.0):
        super().__init__(nombre, moneda)
        self.precio_actual = precio_actual
        self.dias_al_vencimiento = dias_al_vencimiento
        self.valor_nominal = valor_nominal

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float):
        r_periodo = (self.valor_nominal / self.precio_actual) - 1
        r_anual = (1 + r_periodo) ** (365 / self.dias_al_vencimiento) - 1
        ganancia_pesos = monto_inicial * r_periodo
        ganancia_usd = ganancia_pesos / tipo_cambio_actual if tipo_cambio_actual else None
        return {
            "rend_anual_pct": round(r_anual * 100, 2),
            "rend_periodo_pct": round(r_periodo * 100, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd else None
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None):
        _, techo = obtener_banda_cambiaria(fecha)
        if not techo:
            return None
        rend = self.calcular_rendimiento(monto_inicial, techo)
        dolar_equilibrio = (rend["ganancia_pesos"] + monto_inicial) / monto_inicial
        return {
            "monto_final_usd_techo": round(rend["ganancia_usd"] + monto_inicial / techo, 2),
            "dolar_equilibrio": round(dolar_equilibrio, 2)
        }

#pase