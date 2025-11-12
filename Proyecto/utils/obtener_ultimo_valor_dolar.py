# obtener_ultimo_valor_dolar.py

import os
import sqlite3
from .scrapper import scrap

# Ruta segura a la base de datos de datos_financieros
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "db",
    "datos_financieros",
    "datos_financieros.db"
)


def obtener_ultimo_valor_dolar(tipo: str = "DÓLAR BLUE") -> float:
    """
    Obtiene el último valor de venta del dólar según el tipo especificado.

    Esta función primero ejecuta el scraper para actualizar los datos
    de la tabla `dolar` y luego consulta la base de datos SQLite
    para devolver el último valor registrado.

    Args:
        tipo (str): Tipo de dólar a consultar. Ejemplos:
                    "DÓLAR BLUE", "DÓLAR OFICIAL", etc.
                    Por defecto: "DÓLAR BLUE".

    Returns:
        float: Último valor de venta del dólar correspondiente al tipo.

    Raises:
        ValueError: Si no se encuentra un registro para el tipo solicitado.
    """
    # Actualiza la información del dólar ejecutando el scraper
    scrap(["dolar"])

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Consulta SQL para obtener el último valor
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
    else:
        raise ValueError(
            f"No se encontró el valor del dólar "
            f"para el tipo '{tipo}'."
        )
