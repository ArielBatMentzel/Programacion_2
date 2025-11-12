# archivo: utils/helpers.py

"""
Funciones auxiliares del proyecto.

Incluye utilidades para:
- Cálculos financieros
- Formateo de datos
- Validaciones
"""

from typing import List, Dict


def formatear_moneda(valor: float, moneda: str = "ARS") -> str:
    """
    Devuelve el valor formateado como moneda.

    Args:
        valor (float): valor numérico a formatear
        moneda (str): código de moneda, por defecto 'ARS'

    Returns:
        str: cadena formateada, e.g., 'ARS 1,000.50'
    """
    return f"{moneda} {valor:,.2f}"


def promedio(valores: List[float]) -> float:
    """
    Calcula el promedio de una lista de números.

    Args:
        valores (List[float]): lista de valores numéricos

    Returns:
        float: promedio de la lista, 0.0 si la lista está vacía
    """
    if not valores:
        return 0.0
    return sum(valores) / len(valores)


def filtrar_por_emisor(instrumentos: List[Dict], emisor: str) -> List[Dict]:
    """
    Filtra una lista de instrumentos financieros por emisor.

    Args:
        instrumentos (List[Dict]): lista de instrumentos
        emisor (str): nombre del emisor a filtrar

    Returns:
        List[Dict]: instrumentos que coinciden con el emisor
    """
    return [
        i for i in instrumentos
        if i.get("emisor") == emisor
    ]


def calcular_rendimiento_simple(
        valor_inicial: float, valor_final: float) -> float:
    """
    Calcula el rendimiento simple como porcentaje.

    Args:
        valor_inicial (float): valor inicial del instrumento
        valor_final (float): valor final del instrumento

    Returns:
        float: rendimiento en porcentaje, 0.0 si valor_inicial es 0
    """
    if valor_inicial == 0:
        return 0.0
    return ((valor_final - valor_inicial) / valor_inicial) * 100
