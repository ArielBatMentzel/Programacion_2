# archivo: utils/helpers.py

"""
Funciones auxiliares del proyecto.
Incluye utilidades para cálculos financieros, formateo de datos y validaciones.
"""

from typing import List, Dict

def formatear_moneda(valor: float, moneda: str = "ARS") -> str:
    """
    Devuelve el valor formateado como moneda.
    Ejemplo: 1000.5 → 'ARS 1,000.50'
    """
    return f"{moneda} {valor:,.2f}"

def promedio(valores: List[float]) -> float:
    """
    Calcula el promedio de una lista de números.
    """
    if not valores:
        return 0.0
    return sum(valores) / len(valores)

def filtrar_por_emisor(instrumentos: List[Dict], emisor: str) -> List[Dict]:
    """
    Filtra una lista de instrumentos financieros por emisor.
    """
    return [i for i in instrumentos if i.get("emisor") == emisor]

def calcular_rendimiento_simple(valor_inicial: float, valor_final: float) -> float:
    """
    Calcula el rendimiento simple como porcentaje.
    """
    if valor_inicial == 0:
        return 0.0
    return ((valor_final - valor_inicial) / valor_inicial) * 100
