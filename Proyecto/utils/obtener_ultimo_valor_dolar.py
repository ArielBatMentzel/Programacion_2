import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "..",
                       "db", "datos_financieros", "datos_financieros.db")


def obtener_dolar_oficial():
    """Helper para obtener el último valor del DÓLAR OFICIAL desde la BD."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT venta 
            FROM dolar 
            WHERE tipo = 'DÓLAR OFICIAL'
            ORDER BY id DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row and row[0] else None
    except Exception as e:
        print(f"⚠️ Error obteniendo dólar oficial: {e}")
        return None
