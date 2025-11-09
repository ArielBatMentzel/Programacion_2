import os
import sqlite3
from .scrapper import scrap

# Ruta segura a la DB desde utils
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "datos_financieros", "datos_financieros.db")

def obtener_ultimo_valor_dolar(tipo="DÓLAR BLUE"):
    # Scrappeamos el último valor
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
