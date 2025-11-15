from sqlalchemy import text
from typing import List, Dict, Any
from utils.conexion_db import engine 


def obtener_bonos_desde_bd(moneda: str = None) -> List[Dict[str, Any]]:
    """
    Consulta bonos desde la base de datos, opcionalmente filtrando por moneda.

    Args:
        moneda (str, optional): 'ARS' o 'USD'. Si None, devuelve todos.

    Returns:
        List[Dict[str, Any]]: Lista de bonos.
    """
    query = "SELECT * FROM datos_financieros.bonos"
    params = {}
    if moneda in ("ARS", "USD"):
        query += " WHERE moneda = :moneda"
        params["moneda"] = moneda

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]


def obtener_tipo_cambio() -> Dict[str, float]:
    """
    Devuelve un diccionario con los tipos de cambio actuales desde la tabla de dólares.

    Returns:
        Dict[str, float]: {tipo: venta}.
    """
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM datos_financieros.dolar"))
        return {row._mapping["tipo"]: float(row._mapping["venta"]) for row in result}