import os
import sqlite3
import pandas as pd

"""
Funcionalidad:
Cargar datos de un CSV a la base de datos SQLite 'datos_financieros.db'.

Reglas:
- La tabla especificada se elimina si existía y se crea desde cero.
- Se insertan los nuevos datos del CSV.
- Los valores numéricos se normalizan a float.
- La columna 'fecha_vencimiento' se mantiene en formato YYYY-MM-DD.
"""


def _to_float(val):
    """
    Convierte un valor a float de manera segura.

    - Elimina '%' y reemplaza ',' por '.'.
    - Si el valor es None o NaN devuelve None.
    - Si no se puede convertir a float, devuelve None.

    Args:
        val: valor a convertir

    Returns:
        float o None
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).replace("%", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return None


def _crear_tabla_fresca(conn, tabla: str):
    """
    Elimina la tabla si existe y crea una nueva con el esquema correcto.

    Esquema:
        - nombre (TEXT, NOT NULL)
        - moneda (TEXT, NOT NULL)
        - ultimo (REAL)
        - dia_pct, mes_pct, anio_pct (REAL)
        - fecha_vencimiento (TEXT)
        - PRIMARY KEY(nombre, moneda)

    Args:
        conn: conexión SQLite activa
        tabla: nombre de la tabla
    """
    conn.execute(f"DROP TABLE IF EXISTS {tabla};")
    conn.execute(f"""
        CREATE TABLE {tabla} (
            nombre             TEXT NOT NULL,
            moneda             TEXT NOT NULL,
            ultimo             REAL,
            dia_pct            REAL,
            mes_pct            REAL,
            anio_pct           REAL,
            fecha_vencimiento  TEXT,
            PRIMARY KEY (nombre, moneda)
        )
    """)


def reemplazar_tabla_con_csv(csv_path: str,
                             db_path: str,
                             tabla: str = "letras") -> dict:
    """
    Reemplaza la tabla en la base de datos usando los datos de un CSV.

    Pasos:
    1. Leer CSV como string.
    2. Validar columnas esperadas.
    3. Normalizar columnas numéricas a float.
    4. Reordenar columnas según el esquema.
    5. Crear o reemplazar la tabla en la DB.
    6. Insertar todos los datos del CSV en la tabla.

    Args:
        csv_path: ruta del archivo CSV
        db_path: ruta de la base de datos SQLite
        tabla: nombre de la tabla a reemplazar (por defecto 'letras')

    Returns:
        dict información de la operación:
        ruta DB, tabla, filas insertadas, ruta CSV
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")

    # Leer CSV
    df = pd.read_csv(csv_path, dtype=str)

    # Columnas esperadas
    esperadas = [
        "nombre", "moneda", "ultimo",
        "dia_pct", "mes_pct", "anio_pct",
        "fecha_vencimiento"
    ]
    faltan = [c for c in esperadas if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en el CSV: {faltan}")

    # Normalizar columnas numéricas
    df["ultimo"] = df["ultimo"].map(_to_float)
    for c in ["dia_pct", "mes_pct", "anio_pct"]:
        df[c] = df[c].map(_to_float)

    # Asegurar orden de columnas
    df = df[esperadas]

    # Crear carpeta de la DB si no existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        # Optimización de escritura
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        with conn:
            _crear_tabla_fresca(conn, tabla)
            conn.executemany(
                f"""INSERT INTO {tabla}
                    (nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct,
                     fecha_vencimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                df.itertuples(index=False, name=None)
            )

        return {
            "db": os.path.abspath(db_path),
            "tabla": tabla,
            "filas_insertadas": len(df),
            "csv": os.path.abspath(csv_path),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    DB = os.path.join(
        carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db"
    )
    CSV = os.path.join(
        carpeta_script, "..", "datasets", "letras_argentinas_vencimiento.csv"
    )
    info = reemplazar_tabla_con_csv(CSV, DB, tabla="letras")
    print("✅ OK:", info)
