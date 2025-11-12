
# utils/ obtener_banda_cambiaria.py

import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "db",
    "datos_financieros",
    "datos_financieros.db"
)


def obtener_banda_cambiaria(mes: str = None):
    """
    Devuelve la banda inferior y superior para un mes.
    Si no se pasa mes, toma el último disponible.

    Args:
        mes: formato 'yyyy-mm' (ej: '2025-11') o None para el último mes.

    Returns:
        tuple: (banda_inferior, banda_superior)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if mes:
        # Buscar por mes exacto
        cursor.execute(
            """
            SELECT banda_inferior, banda_superior
            FROM bandas_cambiarias
            WHERE fecha = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (mes,)
        )
    else:
        # Última disponible
        cursor.execute(
            """
            SELECT banda_inferior, banda_superior
            FROM bandas_cambiarias
            ORDER BY id DESC
            LIMIT 1
            """
        )

    row = cursor.fetchone()
    conn.close()

    if row:
        return float(row[0]), float(row[1])
    return None, None
