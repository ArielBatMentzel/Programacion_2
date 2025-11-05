# archivo: models/instruments.py

# NOTAS:
"""
Plazo Fijo: Calculamos la TEA (Tasa Efectiva Anual), la diferencia con la TNA (Tasa Nominal Anual), es que
la TEA incluye la capitalación (mensual en este caso), es decir, los intereses por renovar el plazo fijo cada mes.
Fórmula: TEA = (1+i_p)^n  - 1
Siendo: 
    * i_p: Tasa periódica es la tasa de interés correspondiente a un período
    de capitalización (x ej, a 30 días). Entonces: i_p = TNA(en decimales)/n
    * n: Cantidad de períodos en un año. A 30 días, son 12 períodos aprox (en realidad, hay que hacer n=365/30)

En la tabla de Plazo Fijo, el atributo tasa_pct equivale al porcentaje de la TNA

------

Bonos: 


------

Letras: 

------

Pases: 

------



"""



from abc import ABC, abstractmethod

class FixedIncomeInstrument(ABC):
    """
    Clase abstracta para instrumentos financieros de renta fija.
    Define la interfaz que deben implementar todos los instrumentos.
    Atributos:
        - nombre: la especificación del instrumento de renta fija
        - moneda: moneda en la que se trabaja
    """

    def __init__(self, nombre: str, moneda: str):
        self.nombre = nombre
        self.moneda = moneda

    @abstractmethod
    def calcular_rendimiento(self) -> float:
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
    def __init__(self, nombre: str, moneda: str, dias: int, tasa_tna: float):
        super().__init__(nombre, moneda)
        self.dias = dias
        self.tasa_tna = tasa_tna

    def calcular_rendimiento(self, monto_inicial:float, tipo_cambio_actual: float) -> float:
        # Convertimos la TNA a TEA con la fórmula de antes
        n = 365 / self.dias
        tasa_efectiva_anual = (1 + self.tasa_tna/(100*n))**n - 1
        
        # Rendimiento proporcional al plazo elegido (interés generado respecto al monto invertido en cada período/renovación)
        rendimiento_periodo = (1 + tasa_efectiva_anual)**(self.dias / 365) - 1
        
        monto_final = monto_inicial * (1 + rendimiento_periodo)
        ganancia_pesos = monto_final - monto_inicial
        ganancia_usd = ganancia_pesos / tipo_cambio_actual

        return {
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 2),
            "tasa_efectiva_anual": round(tasa_efectiva_anual * 100, 2)
        }

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

    def calcular_rendimiento(self) -> float:
        pass

    def actualizar(self, valor_dolar: float):
        pass

# class Bono(FixedIncomeInstrument):
#     """
#     Instrumento de renta fija: Bono.
#     Atributos:
#         - cupon: interés periódico
#         - valor_nominal: valor nominal del bono
#         - frecuencia_pago: frecuencia de pago de cupones
#         - emisor: entidad emisora
#     """
#     def __init__(self, nombre: str, moneda: str, cupon: float, valor_nominal: float, frecuencia_pago: int, emisor: str):
#         super().__init__(nombre, moneda)
#         self.cupon = cupon
#         self.valor_nominal = valor_nominal
#         self.frecuencia_pago = frecuencia_pago
#         self.emisor = emisor

#     def calcular_rendimiento(self) -> float:
#         pass

#     def actualizar(self, valor_dolar: float):
#         pass

class Bono(FixedIncomeInstrument):
    def __init__(self, nombre: str, moneda: str,
                 ultimo: float = None,
                 dia_pct: float = None,
                 mes_pct: float = None,
                 anio_pct: float = None,
                 cupon: float = None,           # % anual (ej 5.0 -> 5%)
                 valor_nominal: float = None,   # valor nominal del bono
                 frecuencia_pago: int = 1,
                 emisor: str = None):
        super().__init__(nombre, moneda)
        self.ultimo = ultimo
        self.dia_pct = dia_pct
        self.mes_pct = mes_pct
        self.anio_pct = anio_pct
        self.cupon = cupon
        self.valor_nominal = valor_nominal
        self.frecuencia_pago = frecuencia_pago
        self.emisor = emisor

    def _estimate_annual_return(self):
        estimates = []

        # Estrategia A: año_pct directo (si existe)
        if self.anio_pct is not None:
            try:
                estimates.append(self.anio_pct / 100.0)
            except Exception:
                pass

        # Estrategia B: annualizar mes_pct
        if self.mes_pct is not None:
            try:
                r_m = self.mes_pct / 100.0
                estimates.append((1 + r_m) ** 12 - 1)
            except Exception:
                pass

        # Estrategia C: annualizar dia_pct
        if self.dia_pct is not None:
            try:
                r_d = self.dia_pct / 100.0
                estimates.append((1 + r_d) ** 365 - 1)
            except Exception:
                pass

        # Estrategia D: rendimiento por cupón (current yield). No existe cupon en estos datos scrappeadosasi que esta no se hace nunca
        if self.cupon is not None and self.valor_nominal is not None and self.ultimo:
            try:
                cupon_valor_anual = self.valor_nominal * (self.cupon / 100.0)
                current_yield = cupon_valor_anual / float(self.ultimo)
                estimates.append(current_yield)
            except Exception:
                pass

        if not estimates:
            # fallback conservador: 0
            return 0.0

        # Recomiendo promedio simple (podés aplicar ponderaciones si querés)
        return sum(estimates) / len(estimates)

    def calculate(self, monto_inicial: float, dias: int, tipo_cambio_actual: float) -> dict:
        """
        Calcula rendimiento esperado para un horizonte 'dias' usando estimación anual.
        Devuelve diccionario con monto final, ganancias, ganancia en usd y dolar_equilibrio.
        """
        r_anual = self._estimate_annual_return()  # ej 0.22
        # rendimiento en el periodo pedido
        r_periodo = (1 + r_anual) ** (dias / 365.0) - 1

        monto_final = monto_inicial * (1 + r_periodo)
        ganancia_pesos = monto_final - monto_inicial
        ganancia_usd = ganancia_pesos / tipo_cambio_actual if tipo_cambio_actual else None

        dolar_equilibrio = tipo_cambio_actual * (1 + r_periodo) if tipo_cambio_actual else None

        return {
            "r_anual_estimada": round(r_anual * 100, 4),
            "r_periodo_pct": round(r_periodo * 100, 6),
            "monto_final_pesos": round(monto_final, 2),
            "ganancia_pesos": round(ganancia_pesos, 2),
            "ganancia_usd": round(ganancia_usd, 6) if ganancia_usd is not None else None,
            "dolar_equilibrio": round(dolar_equilibrio, 6) if dolar_equilibrio is not None else None,
            "metodos_usados": {
                "anio_pct": self.anio_pct,
                "mes_pct": self.mes_pct,
                "dia_pct": self.dia_pct,
                "cupon": self.cupon,
                "valor_nominal": self.valor_nominal
            }
        }


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

    def calcular_rendimiento(self) -> float:
        pass

    def actualizar(self, valor_dolar: float):
        pass
