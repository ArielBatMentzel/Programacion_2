import os
import sqlite3
from .scrapper import scrap

# Ruta segura a la DB desde utils
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "db",
    "datos_financieros",
    "datos_financieros.db"
)


def obtener_ultimo_valor_dolar(tipo: str = "DÓLAR BLUE") -> float:
    """
    Devuelve el último valor de venta del dólar según el tipo.
    Actualiza primero los datos mediante scraping.

    Args:
        tipo (str): Tipo de dólar (ej: 'DÓLAR BLUE', 'DÓLAR OFICIAL').

    Returns:
        float: Valor de venta.

    Raises:
        ValueError: Si no se encuentra el tipo en la base de datos.
    """
    scrap(["dolar"])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT venta 
        FROM dolar 
        WHERE tipo = ? 
        ORDER BY id DESC 
        LIMIT 1
        """,
        (tipo,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return float(row[0])
    raise ValueError(
        f"No se encontró el valor del dólar para el tipo '{tipo}'."
        )


def obtener_dolar_oficial() -> float | None:
    """
    Helper para obtener el último valor del DÓLAR OFICIAL desde la BD.
    Maneja errores y devuelve None si falla.

    Returns:
        float | None: Valor del dólar oficial o None si hay error.
    """
    scrap(["dolar"])
    try:
        return obtener_ultimo_valor_dolar("DÓLAR OFICIAL")
    except Exception as e:
        print(f"⚠️ Error obteniendo dólar oficial: {e}")
        return None
