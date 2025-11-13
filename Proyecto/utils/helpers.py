# archivo: utils/helpers.py

"""
Funciones auxiliares del proyecto.
Incluye utilidades para cálculos financieros, formateo de datos y validaciones.
"""

from typing import List, Dict


def formatear_moneda(valor: float, moneda: str = "ARS") -> str:
    """
    Devuelve el valor formateado como moneda.

    Args:
        valor (float): Valor numérico a formatear.
        moneda (str, opcional): Símbolo de la moneda. Por defecto "ARS".

    Returns:
        str: Valor formateado con separadores de miles y dos decimales.
    
    Ejemplo:
        1000.5 -> 'ARS 1,000.50'
    """
    return f"{moneda} {valor:,.2f}"


def promedio(valores: List[float]) -> float:
    """
    Calcula el promedio de una lista de números.

    Args:
        valores (List[float]): Lista de números.

    Returns:
        float: Promedio de los valores o 0.0 si la lista está vacía.
    """
    if not valores:
        return 0.0
    return sum(valores) / len(valores)


def filtrar_por_emisor(instrumentos: List[Dict], emisor: str) -> List[Dict]:
    """
    Filtra una lista de instrumentos financieros por emisor.

    Args:
        instrumentos (List[Dict]): 
        Lista de diccionarios con información de instrumentos.
        emisor (str): Nombre del emisor a filtrar.

    Returns:
        List[Dict]: Lista filtrada con instrumentos del emisor especificado.
    """
    return [i for i in instrumentos if i.get("emisor") == emisor]


def calcular_rendimiento_simple(
        valor_inicial: float, valor_final: float
        ) -> float:
    """
    Calcula el rendimiento simple como porcentaje.

    Args:
        valor_inicial (float): Valor inicial de la inversión.
        valor_final (float): Valor final de la inversión.

    Returns:
        float: Rendimiento en porcentaje. Retorna 0 si valor_inicial es 0.
    """
    if valor_inicial == 0:
        return 0.0
    return ((valor_final - valor_inicial) / valor_inicial) * 100