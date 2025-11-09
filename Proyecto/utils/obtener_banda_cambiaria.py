
#utils/ obtener_banda_cambiaria.py
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "datos_financieros","datos_financieros.db")

def obtener_banda_cambiaria(fecha: str = None):
    """
    Devuelve la banda inferior y superior para una fecha.
    Si no se pasa fecha, toma la última disponible.
    Fecha en formato 'dd/mm/yyyy'.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if fecha:
        cursor.execute("""
            SELECT banda_inferior, banda_superior
            FROM bandas_cambiarias
            WHERE fecha = ?
            ORDER BY id DESC
            LIMIT 1
        """, (fecha,))
    else:
        cursor.execute("""
            SELECT banda_inferior, banda_superior
            FROM bandas_cambiarias
            ORDER BY id DESC
            LIMIT 1
        """)
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None