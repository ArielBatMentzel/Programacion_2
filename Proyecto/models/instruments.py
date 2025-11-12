# archivo: Proyecto/models/instruments.py

from abc import ABC, abstractmethod
import sqlite3
import os
from utils.obtener_banda_cambiaria import obtener_banda_cambiaria
from utils.obtener_ultimo_valor_dolar import obtener_dolar_oficial
from datetime import date, datetime, timedelta



def _mes_banda_de_salida(mes_inicio: str | None, fecha_inicio: date | None, dias: int) -> str:
    """Devuelve 'YYYY-MM' del mes final (inicio + dias)."""
    if mes_inicio:
        y, m = mes_inicio.split("-")
        start = date(int(y), int(m), 1)
    else:
        start = fecha_inicio or date.today()
    fin = start + timedelta(days=int(dias))
    return f"{fin.year:04d}-{fin.month:02d}"


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
            v = value.replace("%", "").replace(",", ".").strip()
            try:
                return float(v)
            except ValueError:
                return None
        return None

    def _estimacion_rend_anual(self) -> float:
        """
        Estima una TEA a partir de lo disponible:
        - anio_pct tal cual (ej.: 17% -> 0.17)
        - mes_pct anualizado: (1 + m)^12 - 1
        - dia_pct anualizado: (1 + d)^365 - 1
        Promedia lo que haya.
        """
        posibles = []
        if self.anio_pct is not None:
            posibles.append(self.anio_pct / 100.0)
        if self.mes_pct is not None:
            posibles.append((1.0 + self.mes_pct / 100.0) ** 12 - 1.0)
        if self.dia_pct is not None:
            posibles.append((1.0 + self.dia_pct / 100.0) ** 365 - 1.0)
        return sum(posibles) / len(posibles) if posibles else 0.0

    def calcular_rendimiento(self, monto_inicial: float, tipo_cambio_actual: float = None, dias: int = 30):
        """
        Devuelve para la sección 'Rendimiento':
        - r_mensual_pct: usando 30 días
        - r_anual_pct: TEA estimada
        - usd_invertidos (solo si el bono es ARS y hay TC): monto_inicial / tipo_cambio
        NO devuelve montos finales ni días.
        """
        r_anual = self._estimacion_rend_anual()
        r_mensual = (1.0 + r_anual) ** (30.0 / 365.0) - 1.0

        resultado = {
            "r_mensual_pct": round(r_mensual * 100.0, 2),
            "r_anual_pct": round(r_anual * 100.0, 2),
        }

        # Si el bono es en ARS, exponer cuántos USD se invirtieron
        if self.moneda == "ARS":
            tc = tipo_cambio_actual or getattr(self, "valor_dolar", None)
            if not tc:
                try:
                    tc = obtener_dolar_oficial()
                except Exception:
                    tc = None
            if tc:
                resultado["usd_invertidos"] = round(monto_inicial / float(tc), 2)

        return resultado

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(
        self,
        monto_inicial: float,
        mes: str | None = None,
        dias: int = 30,
        fecha_inicio: date | None = None
    ):
        """
        Comparación contra banda cambiaria:
        - Convierte a ARS si el bono está en USD (usa self.valor_dolar o el oficial)
        - Aplica TEA estimada por 'dias'
        - Usa el techo del mes de salida (inicio + dias)
        """
        dias = int(dias) if dias and dias > 0 else 30

        # 1) Factor ARS para 'dias' a partir de la TEA estimada
        r_anual = self._estimacion_rend_anual()
        factor_ars = (1.0 + r_anual) ** (dias / 365.0)

        # 2) Pasar a ARS si el bono está en USD
        dolar_oficial = getattr(self, "valor_dolar", None) or obtener_dolar_oficial()
        if self.moneda == "USD" and dolar_oficial:
            monto_inicial_ars = monto_inicial * float(dolar_oficial)
        else:
            monto_inicial_ars = monto_inicial

        monto_final_pesos = monto_inicial_ars * factor_ars

        # 3) Banda del MES FINAL (inicio + dias)
        mes_salida = _mes_banda_de_salida(mes_inicio=mes, fecha_inicio=fecha_inicio, dias=dias)
        piso, techo = obtener_banda_cambiaria(mes_salida)
        if not techo or techo <= 0:
            # fallback al último disponible
            piso, techo = obtener_banda_cambiaria(None)
            if not techo or techo <= 0:
                return None

        # 4) Métricas vs banda
        return {
            "monto_final_pesos": round(monto_final_pesos, 2),
            "factor_ars": round(factor_ars, 6),
            "monto_final_usd_techo": round(monto_final_pesos / techo, 2),
            "dolar_equilibrio": round(factor_ars * techo, 2),
            "dias_considerados": dias,
            "mes_banda_usado": mes_salida,
        }

# -------------------- Letra --------------------


# -------------------- Letra --------------------
from datetime import date, datetime

class Letra(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str, ultimo=None, dia_pct=None, mes_pct=None, anio_pct=None, fecha_vencimiento: str | None = None):
        super().__init__(nombre, moneda)
        self.ultimo = self._to_float(ultimo)
        self.dia_pct = self._to_float(dia_pct)
        self.mes_pct = self._to_float(mes_pct)
        self.anio_pct = self._to_float(anio_pct)
        self.fecha_vencimiento = fecha_vencimiento

    # ---- helpers ----
    def _to_float(self, v):
        if v is None: return None
        if isinstance(v, (int, float)): return float(v)
        if isinstance(v, str):
            v2 = v.replace("%", "").replace(",", ".").strip()
            try: return float(v2)
            except ValueError: return None
        return None

    def _tea_estimada(self) -> float:
        """Promedia la info disponible: anio_pct, (1+mes)^12-1, (1+dia)^365-1."""
        comps = []
        if self.anio_pct is not None:
            comps.append(self.anio_pct / 100.0)
        if self.mes_pct is not None:
            comps.append((1.0 + self.mes_pct / 100.0) ** 12 - 1.0)
        if self.dia_pct is not None:
            comps.append((1.0 + self.dia_pct / 100.0) ** 365 - 1.0)
        return sum(comps) / len(comps) if comps else 0.0

    def _dias_hasta_venc(self, fecha_inicio: date | None = None) -> int:
        fi = fecha_inicio or date.today()
        if not self.fecha_vencimiento:
            return 0
        fv = datetime.strptime(self.fecha_vencimiento, "%Y-%m-%d").date()
        return max((fv - fi).days, 0)

    # ---- API pública (solo HTM) ----
    def calcular_rendimiento(self,monto_inicial: float,tipo_cambio_actual: float | None = None,fecha_inicio: date | None = None):
        """
        SOLO hold-to-maturity:
        - r_mensual_pct (30 días)
        - r_anual_pct (TEA estimada)
        - usd_invertidos (si es ARS y hay TC)
        """
        r_anual = self._tea_estimada()
        r_mensual = (1.0 + r_anual) ** (30.0 / 365.0) - 1.0

        out = {
            "r_mensual_pct": round(r_mensual * 100.0, 2),
            "r_anual_pct": round(r_anual * 100.0, 2),
        }

        if self.moneda == "ARS":
            tc = tipo_cambio_actual or getattr(self, "valor_dolar", None) or obtener_dolar_oficial()
            if tc:
                out["usd_invertidos"] = round(monto_inicial / float(tc), 2)

        return out

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(self,monto_inicial: float,fecha_inicio: date | None = None):
        """
        SOLO hold-to-maturity:
        - Usa días hasta vencimiento
        - Banda del mes del vencimiento
        Devuelve:
        - monto_final_pesos
        - monto_final_usd_techo
        - dolar_equilibrio
        - fecha_vencimiento
        """
        # 1) Días hasta vencimiento y factor ARS
        dias = self._dias_hasta_venc(fecha_inicio)
        r_anual = self._tea_estimada()
        factor_ars = (1.0 + r_anual) ** (dias / 365.0)

        # 2) Convertir a ARS si está en USD
        dolar = getattr(self, "valor_dolar", None) or obtener_dolar_oficial()
        monto_inicial_ars = monto_inicial * (float(dolar) if self.moneda == "USD" and dolar else 1.0)
        monto_final_pesos = monto_inicial_ars * factor_ars

        # 3) Banda del mes del vencimiento
        if not self.fecha_vencimiento:
            return None
        fv = datetime.strptime(self.fecha_vencimiento, "%Y-%m-%d").date()
        mes_banda = fv.strftime("%Y-%m")
        piso, techo = obtener_banda_cambiaria(mes_banda)
        if not techo or techo <= 0:
            piso, techo = obtener_banda_cambiaria(None)
            if not techo or techo <= 0:
                return None

        return {
            "monto_final_pesos": round(monto_final_pesos, 2),
            "monto_final_usd_techo": round(monto_final_pesos / techo, 2),
            "dolar_equilibrio": round(factor_ars * techo, 2),
            "fecha_vencimiento": self.fecha_vencimiento,
        }