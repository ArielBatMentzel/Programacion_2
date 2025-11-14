from sqlalchemy import text
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.scrap_runner import scrap
from utils.conexion_db import engine


def obtener_ultimo_valor_dolar(tipo: str = "DÓLAR BLUE") -> float:
    """
    Devuelve el último valor de venta del dólar según el tipo,
    consultando directamente en la base de datos de Supabase.

    Args:
        tipo (str): Tipo de dólar (ej: 'DÓLAR BLUE', 'DÓLAR OFICIAL').

    Returns:
        float: Valor de venta.

    Raises:
        ValueError: Si no se encuentra el tipo en la base de datos.
    """
    # Ejecutar scraping antes (actualiza la tabla si corresponde)
    # scrap(["dolar"])

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT venta
                FROM datos_financieros.dolar
                WHERE tipo = :tipo
                ORDER BY id DESC
                LIMIT 1
            """),
            {"tipo": tipo}
        )
        row = result.fetchone()

    if row:
        return float(row[0])

    raise ValueError(f"No se encontró el valor del dólar para el tipo '{tipo}'.")

def obtener_dolar_oficial() -> float | None:
    """
    Helper para obtener el último valor del dólar oficial desde la BD.
    Maneja errores y devuelve None si falla.

    Returns:
        float | None: Valor del dólar oficial o None si hay error.
    """
    try:
        return obtener_ultimo_valor_dolar("DÓLAR OFICIAL")
    except Exception as e:
        print(f"Error obteniendo dólar oficial: {e}")
        return None
