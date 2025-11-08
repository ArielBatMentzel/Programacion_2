import sqlite3
import os
from Proyecto.utils.scrapper import scrap

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "datos_financieros", "datos_financieros.db")


def obtener_ultimo_valor_dolar(tipo="DÓLAR BLUE"):
    """
    Devuelve el último valor de venta del dólar para el tipo indicado.
    """
    # Scrappeamos el último valor del dólar
    scrap(["dolar"])
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT venta 
        FROM dolar 
        WHERE tipo = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (tipo,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return float(row[0])
    else:
        raise ValueError(f"No se encontró el valor del dólar para el tipo '{tipo}'.")