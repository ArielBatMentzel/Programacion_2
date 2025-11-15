from abc import ABC, abstractmethod
from datetime import date, timedelta
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.obtener_banda_cambiaria import obtener_banda_cambiaria
from utils.obtener_ultimo_valor_dolar import obtener_dolar_oficial


def _mes_banda_de_salida(
    mes_inicio: str | None,
    fecha_inicio: date | None,
    dias: int
) -> str:
    """
    Devuelve el mes final ('YYYY-MM') sumando días a la fecha de inicio.

    Args:
        mes_inicio (str | None): Mes inicial en formato 'YYYY-MM', opcional.
        fecha_inicio (date | None): Fecha de inicio si mes_inicio no está.
        dias (int): Días a sumar desde la fecha inicial.

    Returns:
        str: Mes final en formato 'YYYY-MM'.
    """
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
    Clase abstracta para instrumentos de renta fija.

    Atributos:
        nombre (str): Nombre del instrumento.
        moneda (str): Moneda del instrumento.
        valor_dolar (float | None): Último valor conocido del dólar.
    """

    def __init__(self, nombre: str, moneda: str):
        self.nombre = nombre
        self.moneda = moneda
        self.valor_dolar = None

    @abstractmethod
    def calcular_rendimiento(
        self, monto_inicial: float, tipo_cambio_actual: float
            ):
        """
        Calcula el rendimiento del instrumento.

        Args:
            monto_inicial (float): Monto invertido.
            tipo_cambio_actual (float):
            Tipo de cambio para conversiones si aplica.

        Returns:
            dict: Métricas de rendimiento específicas.
        """
        pass

    def actualizar(self, valor_dolar: float):
        """
        Actualiza el valor del dólar observado.

        Args:
            valor_dolar (float): Valor del dólar a actualizar.
        """
        self.valor_dolar = valor_dolar

    @abstractmethod
    def rendimiento_vs_banda(self, monto_inicial: float, mes: str = None):
        """
        Calcula el rendimiento considerando la banda cambiaria.

        Args:
            monto_inicial (float): Monto invertido.
            mes (str, opcional): Mes de referencia para la banda.

        Returns:
            dict | None:
              Métricas vs banda cambiaria o None si no se puede calcular.
        """
        pass


# -------------------- Plazo Fijo --------------------

class PlazoFijo(FixedIncomeInstrument):
    """Instrumento Plazo Fijo."""

    def __init__(self, banco: str, tasa_tna: float, dias: int = 30):
        """
        Inicializa un Plazo Fijo.

        Args:
            nombre (str): Nombre del instrumento.
            moneda (str): Moneda ('ARS' normalmente).
            dias (int): Plazo en días.
            tasa_tna (float): Tasa nominal anual en porcentaje.
        """
        super().__init__(nombre=banco, moneda="ARS")
        self.dias = dias
        self.tasa_tna = tasa_tna

    def calcular_rendimiento(
            self, monto_inicial: float, tipo_cambio_actual: float = None
            ):
        """
        Calcula el rendimiento del plazo fijo.

        Args:
            monto_inicial (float): Monto invertido.
            tipo_cambio_actual (float, opcional): Ignorado, PF siempre ARS.

        Returns:
            dict: {'tna', 'tea', 'monto_final_pesos', 'ganancia_pesos'}.
        """
        n = 365 / self.dias
        tasa_efectiva_anual = (1 + self.tasa_tna / (100 * n)) ** n - 1
        rendimiento_periodo = (
            (1 + tasa_efectiva_anual) ** (self.dias / 365) - 1
        )
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
        """
        Calcula métricas frente a la banda cambiaria.

        Devuelve un dict con:
        - monto_final_usd_techo: cuánto USD equivaldrían los pesos finales si el tipo llega al techo
        - dolar_break_even: factor_ars * techo (métrica relativa frente al techo)
        - dolar_equilibrio: EL dólar real de equilibrio (precio máximo del USD para no perder en USD)

        Si falta información útil (techo o dólar actual) algunos campos serán None.
        """
        # Obtener banda (piso, techo)
        piso, techo = obtener_banda_cambiaria(mes)
        if not techo or techo <= 0:
            # No hay banda válida
            techo = None

        # Cálculo del rendimiento del plazo fijo
        rend = self.calcular_rendimiento(monto_inicial)
        monto_final_pesos = float(rend["monto_final_pesos"])

        # Evitar división por cero
        if monto_inicial == 0:
            return None

        # Métrica relacionada con la banda
        factor_ars = monto_final_pesos / monto_inicial
        dolar_break_even = None
        monto_final_usd_techo = None
        if techo:
            dolar_break_even = factor_ars * float(techo)
            monto_final_usd_techo = monto_final_pesos / float(techo)

        # Necesitamos el dolar actual; preferimos usar self.valor_dolar si está,
        # si no, intentamos obtenerlo desde el helper obtener_dolar_oficial()
        dolar_actual = getattr(self, "valor_dolar", None)
        if not dolar_actual:
            try:
                from utils.obtener_ultimo_valor_dolar import obtener_dolar_oficial
                dolar_actual = obtener_dolar_oficial()
            except Exception:
                dolar_actual = None

        dolar_equilibrio = None
        if dolar_actual and monto_inicial:
            # fórmula: (monto_final_pesos * dolar_actual) / monto_inicial
            try:
                dolar_equilibrio = round((monto_final_pesos * float(dolar_actual)) / float(monto_inicial), 2)
            except Exception:
                dolar_equilibrio = None

        return {
            "monto_final_usd_techo": round(monto_final_usd_techo, 2) if monto_final_usd_techo is not None else None,
            "dolar_break_even": round(dolar_break_even, 2) if dolar_break_even is not None else None,
            "dolar_equilibrio": dolar_equilibrio
        }

    @classmethod
    def from_supabase_row(cls, row: dict):
        """
        Genera un objeto PlazoFijo a partir de una fila de datos
        en formato diccionario (como lo que devuelve la base de datos).
        """
        
        # Al usar el decorador classmethod, 
        # cls representa la misma clase "PlazoFijo" 
        instancia = cls(
            banco=row["banco"],
            tasa_tna=float(row["tasa_pct"]),   # 👈 A float sí o sí
            dias=30
        )

        # Convertir todo lo que venga como Decimal → float
        instancia.monto_inicial = float(row["monto_inicial"])
        instancia.dolar_equilibrio = (
            float(row["dolar_equilibrio"]) if row.get("dolar_equilibrio") else None
        )
        instancia.valor_dolar = (
            float(row["dolar_actual"]) if row.get("dolar_actual") else None
        )

        return instancia


# -------------------- Bono --------------------

class Bono(FixedIncomeInstrument):
    """Instrumento Bono."""

    def __init__(self, nombre: str, moneda: str, ultimo=None, dia_pct=None,
                 mes_pct=None, anio_pct=None):
        """
        Inicializa un Bono.

        Args:
            nombre (str): Nombre del bono.
            moneda (str): Moneda ('ARS' o 'USD').
            ultimo (float | str | None): Último precio/cotización.
            dia_pct, mes_pct, anio_pct (float | str | None):
            Rendimientos diarios, mensuales, anuales.
        """
        super().__init__(nombre, moneda)
        self.ultimo = self._to_float(ultimo)
        self.dia_pct = self._to_float(dia_pct)
        self.mes_pct = self._to_float(mes_pct)
        self.anio_pct = self._to_float(anio_pct)

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
        Estima TEA promedio del bono según datos disponibles.

        Returns:
            float: Rendimiento anual estimado.
        """
        posibles = []
        if self.anio_pct is not None:
            posibles.append(self.anio_pct / 100.0)
        if self.mes_pct is not None:
            posibles.append((1.0 + self.mes_pct / 100.0) ** 12 - 1.0)
        if self.dia_pct is not None:
            posibles.append((1.0 + self.dia_pct / 100.0) ** 365 - 1.0)
        return sum(posibles) / len(posibles) if posibles else 0.0

    def calcular_rendimiento(self, monto_inicial: float,
                             tipo_cambio_actual: float = None, dias: int = 30):
        """
        Calcula métricas de rendimiento del bono.

        Args:
            monto_inicial (float): Monto invertido.
            tipo_cambio_actual (float, opcional): Tipo de cambio para ARS/USD.
            dias (int, opcional): Para cálculo mensual (default=30).

        Returns:
            dict: {'r_mensual_pct', 'r_anual_pct', 'usd_invertidos' si aplica}.
        """
        r_anual = self._estimacion_rend_anual()
        r_mensual = (1.0 + r_anual) ** (30.0 / 365.0) - 1.0

        resultado = {
            "r_mensual_pct": round(r_mensual * 100.0, 2),
            "r_anual_pct": round(r_anual * 100.0, 2),
        }

        if self.moneda == "ARS":
            tc = tipo_cambio_actual or getattr(self, "valor_dolar", None)
            if not tc:
                try:
                    tc = obtener_dolar_oficial()
                except Exception:
                    tc = None
            if tc:
                resultado["usd_invertidos"] = round(
                    monto_inicial / float(tc), 2)

        return resultado

    def actualizar(self, valor_dolar: float):
        self.valor_dolar = valor_dolar

    def rendimiento_vs_banda(
            self, monto_inicial: float, mes: str | None = None,
            dias: int = 30, fecha_inicio: date | None = None
            ):
        """
        Calcula métricas del bono vs banda cambiaria.

        Args:
            monto_inicial (float): Monto invertido.
            mes (str, opcional): Mes de referencia inicial.
            dias (int, opcional): Cantidad de días a considerar.
            fecha_inicio (date | None, opcional): Fecha inicial
              para conteo de días.

        Returns:
            dict | None: Métricas vs banda o None si no se puede calcular.
        """
        dias = int(dias) if dias and dias > 0 else 30
        r_anual = self._estimacion_rend_anual()
        factor_ars = (1.0 + r_anual) ** (dias / 365.0)

        dolar_oficial = (
            getattr(self, "valor_dolar", None) or obtener_dolar_oficial()
        )

        if self.moneda == "USD" and dolar_oficial:
            monto_inicial_ars = monto_inicial * float(dolar_oficial)
        else:
            monto_inicial_ars = monto_inicial

        monto_final_pesos = monto_inicial_ars * factor_ars

        mes_salida = _mes_banda_de_salida(
            mes_inicio=mes,
            fecha_inicio=fecha_inicio,
            dias=dias
        )
        piso, techo = obtener_banda_cambiaria(mes_salida)
        if not techo or techo <= 0:
            piso, techo = obtener_banda_cambiaria(None)
            if not techo or techo <= 0:
                return None

        return {
            "monto_final_pesos": round(monto_final_pesos, 2),
            "factor_ars": round(factor_ars, 6),
            "monto_final_usd_techo": round(monto_final_pesos / techo, 2),
            "dolar_equilibrio": round(factor_ars * techo, 2),
            "dias_considerados": dias,
            "mes_banda_usado": mes_salida,
        }
