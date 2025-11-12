"""
Función para cargar datos de un CSV en la base de datos 'datos_financieros.db'.

Al ejecutar la función:
- Se eliminan las filas existentes de la tabla indicada.
- Se insertan los datos nuevos desde el CSV.
"""

import os
import sqlite3
import pandas as pd


def _to_float(val):
    """Convierte valores tipo string o None a float, manejando % y comas."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).replace("%", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return None


def _crear_tabla_fresca(conn, tabla: str):
    """Elimina la tabla si existe y la recrea con el esquema correcto."""
    conn.execute(f"DROP TABLE IF EXISTS {tabla};")
    conn.execute(
        f"""
        CREATE TABLE {tabla} (
            nombre   TEXT NOT NULL,
            moneda   TEXT NOT NULL,
            ultimo   REAL,
            dia_pct  REAL,
            mes_pct  REAL,
            anio_pct REAL,
            fecha_vencimiento TEXT,
            PRIMARY KEY (nombre, moneda)
        )
        """
    )


def reemplazar_tabla_con_csv(
    csv_path: str, db_path: str, tabla: str = "bonos"
) -> dict:

    """Carga los datos del CSV a la tabla indicada en la base de datos."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)

    esperadas = [
        "nombre",
        "moneda",
        "ultimo",
        "dia_pct",
        "mes_pct",
        "anio_pct",
        "fecha_vencimiento",
    ]

    faltantes = [c for c in esperadas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"El CSV debe incluir columnas {esperadas}. "
            f"Faltan: {faltantes}"
        )

    df["ultimo"] = df["ultimo"].map(_to_float)
    for c in ["dia_pct", "mes_pct", "anio_pct"]:
        df[c] = df[c].map(_to_float)

    df["fecha_vencimiento"] = pd.to_datetime(
        df["fecha_vencimiento"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        with conn:  # transacción atómica
            _crear_tabla_fresca(conn, tabla)
            sql_insert = (
                f"INSERT INTO {tabla} "
                "(nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct, "
                "fecha_vencimiento) VALUES (?, ?, ?, ?, ?, ?, ?)"
            )
            conn.executemany(
                sql_insert, df[esperadas].itertuples(index=False, name=None)
            )

        return {
            "db": os.path.abspath(db_path),
            "tabla": tabla,
            "filas_insertadas": len(df),
            "csv": os.path.abspath(csv_path),
        }
    finally:
        conn.close()


# --- Ejecutar directo ---
if __name__ == "__main__":
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    DB = os.path.join(
        carpeta_script,
        "..",
        "db",
        "datos_financieros",
        "datos_financieros.db",
    )
    CSV = os.path.join(
        carpeta_script,
        "..",
        "datasets",
        "bonos_argentinos_vencimiento.csv",
    )
    info = reemplazar_tabla_con_csv(CSV, DB, tabla="bonos")
    print("✅ OK:", info)
