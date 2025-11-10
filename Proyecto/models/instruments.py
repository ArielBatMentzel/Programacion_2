# archivo: Proyecto/models/instruments.py

from abc import ABC, abstractmethod
import sqlite3
import os
from utils.obtener_banda_cambiaria import obtener_banda_cambiaria
from utils.obtener_ultimo_valor_dolar import obtener_dolar_oficial


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

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    @abstractmethod
    def rendimiento_vs_banda(self, monto_inicial: float, mes: str = None):
        """Calcula el rendimiento considerando el techo de la banda cambiaria."""
        pass

# -------------------- Plazo Fijo --------------------


class PlazoFijo(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str, dias: int, tasa_tna: float):
        super().__init__(nombre, moneda)
        self.dias = dias
        self.tasa_tna = tasa_tna

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float = None):
        n = 365 / self.dias
        tasa_efectiva_anual = (1 + self.tasa_tna / (100 * n)) ** n - 1
        rendimiento_periodo = (
            1 + tasa_efectiva_anual) ** (self.dias / 365) - 1
        monto_final = monto_inicial * (1 + rendimiento_periodo)
        ganancia_pesos = monto_final - monto_inicial
        return {
            "tna": self.tasa_tna,
            "tea": round(tasa_efectiva_anual * 100, 2),
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, mes: str = None):
        _, techo = obtener_banda_cambiaria(mes)
        if not techo or techo <= 0:
            return None

    # El rendimiento del PF se calcula directo en ARS
        # debe devolver "monto_final" en ARS
        rend = self.calcular_rendimiento(monto_inicial)
        monto_final_pesos = rend["monto_final_pesos"]

    # Factor de crecimiento en ARS (mismo denominador que el cálculo)
        factor_ars = monto_final_pesos / monto_inicial

    # Banda se usa solo para proyectar a USD techo
        dolar_break_even = factor_ars * techo
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

        monto_inicial_ars = monto_inicial
        if self.moneda == "USD":
            if tipo_cambio_actual is None:
                tipo_cambio_actual = self.valor_dolar  # 🔥 Intenta caché primero
                if tipo_cambio_actual is None:
                    tipo_cambio_actual = obtener_dolar_oficial()
                    self.valor_dolar = tipo_cambio_actual  # 🔥 Guarda en caché
            if tipo_cambio_actual:
                monto_inicial_ars = monto_inicial * tipo_cambio_actual

        r_anual = self._estimacion_rend_anual()
        r_periodo = (1 + r_anual) ** (30 / 365) - 1
        monto_final = monto_inicial_ars * (1 + r_periodo)
        ganancia_pesos = monto_final - monto_inicial_ars
        ganancia_usd = ganancia_pesos / tipo_cambio_actual if tipo_cambio_actual else None
        return {
            "r_anual_pct": round(r_anual * 100, 2),
            "r_mensual_pct": round(r_periodo * 100, 2),
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2)
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, mes: str = None):
        piso, techo = obtener_banda_cambiaria(mes)
        if not techo or techo <= 0:
            return None

        dolar_oficial = self.valor_dolar or obtener_dolar_oficial()
    # 1) calculo con monto ORIGINAL + TC oficial (la función convierte una sola vez)
        rend = self.calcular_rendimiento(
            monto_inicial, tipo_cambio_actual=dolar_oficial)
        monto_final_pesos = rend["monto_final_pesos"]

    # 2) factor en ARS (mismo TC en numerador y denominador)
        monto_inicial_ars = monto_inicial * \
            (dolar_oficial if self.moneda == "USD" and dolar_oficial else 1.0)
        factor_ars = monto_final_pesos / monto_inicial_ars

    # 3) banda SOLO para el break-even en USD
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

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float = None, dias: int = None):
        # 🔥 Convertir USD→ARS si aplica (con caché)
        monto_inicial_ars = monto_inicial
        if self.moneda == "USD":
            if tipo_cambio_actual is None:
                tipo_cambio_actual = self.valor_dolar  # Intenta caché
                if tipo_cambio_actual is None:
                    tipo_cambio_actual = obtener_dolar_oficial()
                    self.valor_dolar = tipo_cambio_actual  # Guarda en caché
            if tipo_cambio_actual:
                monto_inicial_ars = monto_inicial * tipo_cambio_actual

        dias_base = self.dias_al_vencimiento
        dias = dias_base if dias is None else int(dias)
        r_vencimiento = (self.valor_nominal / self.precio_actual) - 1
        r_anual = (1 + r_vencimiento) ** (365 / dias_base) - 1
        r_periodo = (1 + r_anual) ** (dias / 365) - 1

        monto_final = monto_inicial_ars * \
            (self.valor_nominal / self.precio_actual)
        ganancia_pesos = monto_final - monto_inicial_ars

        return {
            "dias_considerados": dias,
            "rend_anual_pct": round(r_anual * 100, 2),
            "r_periodo_dias_pct": round(r_periodo * 100, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "monto_final_pesos": round(monto_final, 2),
        }

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self, monto_inicial: float, mes: str = None):
        piso, techo = obtener_banda_cambiaria(mes)
        if not techo or techo <= 0:
            return None

        dolar_oficial = self.valor_dolar or obtener_dolar_oficial()
        rend = self.calcular_rendimiento(
            monto_inicial, tipo_cambio_actual=dolar_oficial)
        monto_final_pesos = rend["monto_final_pesos"]

        monto_inicial_ars = monto_inicial * \
            (dolar_oficial if self.moneda == "USD" and dolar_oficial else 1.0)
        factor_ars = monto_final_pesos / monto_inicial_ars

        dolar_break_even = factor_ars * techo
        monto_final_usd_techo = monto_final_pesos / techo

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2),
            "dolar_equilibrio": round(dolar_break_even, 2)
        }

    # -------------------- billetera virtual --------------------


# class Billeteravirtual(FixedIncomeInstrument):

#     #Podés pasar TNA (%) o TEA (%) — si viene TNA, convertimos a TEA asumiendo capitalización diaria.

#     def __init__(self, nombre: str, moneda: str, tna: float = None, tea: float = None, dias_default: int = 30):
#         super().__init__(nombre, moneda)
#         if tna is None and tea is None:
#             raise ValueError("Debes indicar tna o tea para la billetera.")
#         self.tna = float(tna) if tna is not None else None      # % nominal anual
#         self.tea = float(tea) if tea is not None else None      # % efectiva anual
#         self.dias_default = int(dias_default)

#     def _tea(self) -> float:
#         """Devuelve TEA (en proporción, no %) a partir de TEA directa o TNA con capitalización diaria."""
#         if self.tea is not None:
#             return self.tea / 100.0
#         # si solo viene TNA, aproximamos TEA con comp. diaria
#         tna_prop = self.tna / 100.0
#         return (1 + tna_prop / 365.0) ** 365.0 - 1.0

#     def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float, dias: int = None):
#         dias = self.dias_default if dias is None else int(dias)
#         tea_prop = self._tea()
#         r_periodo = (1 + tea_prop) ** (dias / 365.0) - 1.0

#         monto_final = monto_inicial * (1 + r_periodo)
#         ganancia_pesos = monto_final - monto_inicial

#         ganancia_usd = None
#         monto_final_usd = None
#         if tipo_cambio_actual and tipo_cambio_actual > 0:
#             ganancia_usd = ganancia_pesos / tipo_cambio_actual
#             monto_final_usd = monto_final / tipo_cambio_actual

#         return {
#             "tna": round(self.tna, 2) if self.tna is not None else None,
#             "tea": round(tea_prop * 100, 2),
#             "r_periodo_dias_pct": round(r_periodo * 100, 2),
#             "monto_final_pesos": round(monto_final, 2),
#             "ganancia_pesos": round(ganancia_pesos, 2),
#             "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd is not None else None,
#             "monto_final_usd": round(monto_final_usd, 2) if monto_final_usd is not None else None,
#         }

#     def actualizar(self, valor_dolar: float):
#         self.valor_dolar = valor_dolar

#     def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None, dias: int = None):
#         _, techo = obtener_banda_cambiaria(fecha)
#         if not techo or techo <= 0:
#             return None

#         rend = self.calcular_rendimiento(monto_inicial, techo, dias=dias)
#         monto_final_pesos = rend.get("monto_final_pesos", monto_inicial + rend["ganancia_pesos"])
#         factor_ars = monto_final_pesos / monto_inicial
#         dolar_break_even = factor_ars * techo
#         monto_final_usd_techo = monto_final_pesos / techo

#         return {
#             "monto_final_usd_techo": round(monto_final_usd_techo, 2),
#             "dolar_break_even": round(dolar_break_even, 2)
#         }


# class BilleteraMP(FixedIncomeInstrument):
#     # Billetera virtual (Mercado Pago).
#     # Podés pasar TNA (%) o TEA (%) — si viene TNA, convertimos a TEA asumiendo capitalización diaria.
#     def __init__(self, nombre: str, moneda: str, tna: float = None, tea: float = None, dias_default: int = 30):
#         super().__init__(nombre, moneda)
#         if tna is None and tea is None:
#             raise ValueError("Debes indicar tna o tea para la billetera.")
#         self.tna = float(tna) if tna is not None else None
#         self.tea = float(tea) if tea is not None else None
#         self.dias_default = int(dias_default)

#     def _tea(self) -> float:
#         # Devuelve TEA (en proporción)
#         if self.tea is not None:
#             return self.tea / 100.0
#         tna_prop = self.tna / 100.0
#         return (1 + tna_prop / 365.0) ** 365.0 - 1.0

#     def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float, dias: int = None):
#         dias = self.dias_default if dias is None else int(dias)
#         tea_prop = self._tea()
#         r_periodo = (1 + tea_prop) ** (dias / 365.0) - 1.0

#         monto_final = monto_inicial * (1 + r_periodo)
#         ganancia_pesos = monto_final - monto_inicial

#         ganancia_usd = None
#         monto_final_usd = None
#         if tipo_cambio_actual and tipo_cambio_actual > 0:
#             ganancia_usd = ganancia_pesos / tipo_cambio_actual
#             monto_final_usd = monto_final / tipo_cambio_actual

#         return {
#             "tna": round(self.tna, 2) if self.tna is not None else None,
#             "tea": round(tea_prop * 100, 2),
#             "r_anual_pct": round(tea_prop * 100, 2),         # alias para uniformidad con otros instrumentos
#             "r_periodo_dias_pct": round(r_periodo * 100, 2),
#             "monto_final_pesos": round(monto_final, 2),
#             "ganancia_pesos": round(ganancia_pesos, 2),
#             "ganancia_usd": round(ganancia_usd, 2) if ganancia_usd is not None else None,
#             "monto_final_usd": round(monto_final_usd, 2) if monto_final_usd is not None else None,
#         }

#     def actualizar(self, valor_dolar: float):
#         self.valor_dolar = valor_dolar

#     def rendimiento_vs_banda(self, monto_inicial: float, fecha: str = None, dias: int = None):
#         _, techo = obtener_banda_cambiaria(fecha)
#         if not techo or techo <= 0:
#             return None

#         rend = self.calcular_rendimiento(monto_inicial, techo, dias=dias)
#         monto_final_pesos = rend.get("monto_final_pesos", monto_inicial + rend["ganancia_pesos"])
#         factor_ars = monto_final_pesos / monto_inicial
#         dolar_break_even = factor_ars * techo
#         monto_final_usd_techo = monto_final_pesos / techo

#         return {
#             "monto_final_usd_techo": round(monto_final_usd_techo, 2),
#             "dolar_equilibrio": round(dolar_break_even, 2)   # unificado con otros instrumentos
#         }
