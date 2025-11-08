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
        if not techo or techo <= 0:
            return None

        rend = self.calcular_rendimiento(monto_inicial, techo)

        monto_final_pesos = rend["monto_final_pesos"]

        factor_ars = monto_final_pesos / monto_inicial     # Factor de crecimiento en pesos

        dolar_break_even = factor_ars * techo     # Dólar break-even = techo * factor_ars

        monto_final_usd_techo = monto_final_pesos / techo

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2),
            "dolar_equilibrio": round(dolar_break_even, 2)
            }

# -------------------- Bono -------------------    
    
class Bono(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str, ultimo=None,
                 dia_pct=None, mes_pct=None, anio_pct=None):
        super().__init__(nombre, moneda)
        self.ultimo = self._to_float(ultimo)
        self.dia_pct = self._to_float(dia_pct)    
        self.mes_pct = self._to_float(mes_pct)    
        self.anio_pct = self._to_float(anio_pct)   

     # Helpers robustos para convertir a float

    def _to_float(self, value): 
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.replace('%', '').replace(',', '.').strip()
            try:
                return float(value)
            except ValueError:
                return None
        return None
    def _estimacion_rend_anual(self):
        posibles = []
        if self.anio_pct is not None:
            posibles.append(self.anio_pct / 100)
        if self.mes_pct is not None:
            posibles.append((1 + self.mes_pct / 100) ** 12 - 1)
        if self.dia_pct is not None:
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
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd else None
        }
    
    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None):
        _, techo = obtener_banda_cambiaria(fecha)
        if not techo or techo <= 0:
            return None

        rend = self.calcular_rendimiento(monto_inicial, techo)

        monto_final_pesos = rend.get("monto_final_pesos", monto_inicial + rend["ganancia_pesos"])


        factor_ars = monto_final_pesos / monto_inicial
        dolar_break_even = factor_ars * techo


        monto_final_usd_techo = monto_final_pesos / techo

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2),
            "dolar_equilibrio": round(dolar_break_even, 2)
            }

# -------------------- Letra --------------------
    

class Letra(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str, precio_actual: float,
                 dias_al_vencimiento: int, valor_nominal: float = 100.0):
        super().__init__(nombre, moneda)
        if precio_actual is None or precio_actual <= 0:
            raise ValueError("precio_actual debe ser > 0")
        if dias_al_vencimiento is None or dias_al_vencimiento <= 0:
            raise ValueError("dias_al_vencimiento debe ser > 0")
        self.precio_actual = float(precio_actual)
        self.dias_al_vencimiento = int(dias_al_vencimiento)
        self.valor_nominal = float(valor_nominal)

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float, dias: int = None):
        
        dias_base = self.dias_al_vencimiento #dias base de la letra
        dias= dias_base if dias is None else int(dias) #dias para informar un rendiemiento del periodo
        r_vencimiento = (self.valor_nominal / self.precio_actual) - 1 #rendimiento al vencimiento
        r_anual = (1 + r_vencimiento) ** (365 / dias_base) - 1 #tea usando dias al vencimiento
        r_periodo = (1 + r_anual) ** (dias / 365) - 1 #rendimiento para #dias informados (si difieren de dias al vencimiento)

        monto_final = monto_inicial * (self.valor_nominal / self.precio_actual)
        ganancia_pesos = monto_final - monto_inicial
        ganancia_usd = None
        monto_final_usd = None
        if tipo_cambio_actual and tipo_cambio_actual > 0:
            ganancia_usd = ganancia_pesos / tipo_cambio_actual
            monto_final_usd = monto_final / tipo_cambio_actual

        return {
            "dias_considerados": dias,
            "rend_anual_pct": round(r_anual * 100, 2),
            "r_periodo_dias_pct": round(r_periodo * 100, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd else None,
            "monto_final_pesos": round(monto_final, 2),
            "monto_final_usd": round(monto_final_usd, 2) if monto_final_usd else None
        }
    
    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None):
        _, techo = obtener_banda_cambiaria(fecha)
        if not techo or techo <= 0:
            return None

        rend = self.calcular_rendimiento(monto_inicial, techo)

        monto_final_pesos = rend.get("monto_final_pesos", monto_inicial + rend["ganancia_pesos"])

        factor_ars = monto_final_pesos / monto_inicial

        dolar_break_even = factor_ars * techo

        monto_final_usd_techo = monto_final_pesos / techo

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2),
            "dolar_equilibrio": round(dolar_break_even, 2)
        }

    # -------------------- billetera virtual --------------------


class Billeteravirtual(FixedIncomeInstrument):
  
    #Podés pasar TNA (%) o TEA (%) — si viene TNA, convertimos a TEA asumiendo capitalización diaria.

    def __init__(self, nombre: str, moneda: str, tna: float = None, tea: float = None, dias_default: int = 30):
        super().__init__(nombre, moneda)
        if tna is None and tea is None:
            raise ValueError("Debes indicar tna o tea para la billetera.")
        self.tna = float(tna) if tna is not None else None      # % nominal anual
        self.tea = float(tea) if tea is not None else None      # % efectiva anual
        self.dias_default = int(dias_default)

    def _tea(self) -> float:
        """Devuelve TEA (en proporción, no %) a partir de TEA directa o TNA con capitalización diaria."""
        if self.tea is not None:
            return self.tea / 100.0
        # si solo viene TNA, aproximamos TEA con comp. diaria
        tna_prop = self.tna / 100.0
        return (1 + tna_prop / 365.0) ** 365.0 - 1.0

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float, dias: int = None):
        dias = self.dias_default if dias is None else int(dias)
        tea_prop = self._tea()
        r_periodo = (1 + tea_prop) ** (dias / 365.0) - 1.0

        monto_final = monto_inicial * (1 + r_periodo)
        ganancia_pesos = monto_final - monto_inicial

        ganancia_usd = None
        monto_final_usd = None
        if tipo_cambio_actual and tipo_cambio_actual > 0:
            ganancia_usd = ganancia_pesos / tipo_cambio_actual
            monto_final_usd = monto_final / tipo_cambio_actual

        return {
            "tna": round(self.tna, 2) if self.tna is not None else None,
            "tea": round(tea_prop * 100, 2),
            "r_periodo_dias_pct": round(r_periodo * 100, 2),
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd is not None else None,
            "monto_final_usd": round(monto_final_usd, 2) if monto_final_usd is not None else None,
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None, dias: int = None):
        _, techo = obtener_banda_cambiaria(fecha)
        if not techo or techo <= 0:
            return None

        rend = self.calcular_rendimiento(monto_inicial, techo, dias=dias)
        monto_final_pesos = rend.get("monto_final_pesos", monto_inicial + rend["ganancia_pesos"])
        factor_ars = monto_final_pesos / monto_inicial
        dolar_break_even = factor_ars * techo
        monto_final_usd_techo = monto_final_pesos / techo

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2),
            "dolar_break_even": round(dolar_break_even, 2)
        }
    


class BilleteraMP(FixedIncomeInstrument):
    # Billetera virtual (Mercado Pago).
    # Podés pasar TNA (%) o TEA (%) — si viene TNA, convertimos a TEA asumiendo capitalización diaria.
    def __init__(self, nombre: str, moneda: str, tna: float = None, tea: float = None, dias_default: int = 30):
        super().__init__(nombre, moneda)
        if tna is None and tea is None:
            raise ValueError("Debes indicar tna o tea para la billetera.")
        self.tna = float(tna) if tna is not None else None
        self.tea = float(tea) if tea is not None else None
        self.dias_default = int(dias_default)

    def _tea(self) -> float:
        # Devuelve TEA (en proporción)
        if self.tea is not None:
            return self.tea / 100.0
        tna_prop = self.tna / 100.0
        return (1 + tna_prop / 365.0) ** 365.0 - 1.0

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float, dias: int = None):
        dias = self.dias_default if dias is None else int(dias)
        tea_prop = self._tea()
        r_periodo = (1 + tea_prop) ** (dias / 365.0) - 1.0

        monto_final = monto_inicial * (1 + r_periodo)
        ganancia_pesos = monto_final - monto_inicial

        ganancia_usd = None
        monto_final_usd = None
        if tipo_cambio_actual and tipo_cambio_actual > 0:
            ganancia_usd = ganancia_pesos / tipo_cambio_actual
            monto_final_usd = monto_final / tipo_cambio_actual

        return {
            "tna": round(self.tna, 2) if self.tna is not None else None,
            "tea": round(tea_prop * 100, 2),
            "r_anual_pct": round(tea_prop * 100, 2),         # alias para uniformidad con otros instrumentos
            "r_periodo_dias_pct": round(r_periodo * 100, 2),
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd is not None else None,
            "monto_final_usd": round(monto_final_usd, 2) if monto_final_usd is not None else None,
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None, dias: int = None):
        _, techo = obtener_banda_cambiaria(fecha)
        if not techo or techo <= 0:
            return None

        rend = self.calcular_rendimiento(monto_inicial, techo, dias=dias)
        monto_final_pesos = rend.get("monto_final_pesos", monto_inicial + rend["ganancia_pesos"])
        factor_ars = monto_final_pesos / monto_inicial
        dolar_break_even = factor_ars * techo
        monto_final_usd_techo = monto_final_pesos / techo

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2),
            "dolar_equilibrio": round(dolar_break_even, 2)   # unificado con otros instrumentos
        }

    