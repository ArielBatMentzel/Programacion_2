"""
Carga los datos de bonos desde CSV a la 
base de datos de Supabase.
Elimina las filas existentes y carga las nuevas.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("⚠️ No se encontró la variable DB_URL en el entorno.")
engine = create_engine(DB_URL)


def _to_float(val):
    """
    Convierte valores a float.
    
    Args:
        val: str, int, float o None. Puede tener comas, espacios o '%'.
    
    Returns:
        float o None si no se puede convertir.
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).replace("%", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return None


def reemplazar_tabla_bonos_con_csv(
    csv_path: str,
    tabla: str = "datos_financieros.bonos"
) -> dict:
    """
    Reemplaza la tabla de bandas cambiarias en Supabase 
    con los datos del CSV.
    - Elimina todas las filas existentes
    - Inserta los datos del CSV

    CSV esperado:
    fecha,banda_inferior,banda_superior,ancho

    :param csv_path: ruta del CSV
    :param tabla: ruta de la tabla en el Supabase a reemplazar
    :return: dict con información de la operación
    """
    esquema_db = tabla.split(".")[0]
    tabla_db = tabla.split(".")[-1]
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")

    # Leer CSV
    df = pd.read_csv(csv_path, dtype=str)

    # Columnas esperadas
    esperadas = [
        "nombre", "moneda", "ultimo",
        "dia_pct", "mes_pct", "anio_pct", "fecha_vencimiento"
        ]
    faltantes = [c for c in esperadas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"El CSV debe incluir columnas {esperadas}. Faltan: {faltantes}"
            )

    # Normalizar numéricas
    df["ultimo"] = df["ultimo"].map(_to_float)
    for c in ["dia_pct", "mes_pct", "anio_pct"]:
        df[c] = df[c].map(_to_float)

    # Formatear fecha
    df["fecha_vencimiento"] = pd.to_datetime(
        df["fecha_vencimiento"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    # Conectar a Supabase y reemplazar tabla
    with engine.begin() as conn:
        conn.execute(text(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = '{esquema_db}'
                    AND table_name = '{tabla_db}'
                ) THEN
                    EXECUTE 'DELETE FROM {esquema_db}.{tabla_db}';
                END IF;
            END
            $$;
        """))
        df.to_sql(
            tabla_db, # Tabla del Supabase
            conn, 
            schema=esquema_db, # Esquema del Supabase
            if_exists="append", 
            index=False
        )
    
    return {
        "tabla": tabla,
        "filas_insertadas": len(df),
        "csv": os.path.abspath(csv_path)
    }
    


# --- Ejecutar directo ---
if __name__ == "__main__":
    """
    Script ejecutable que reemplaza la tabla 'bandas_cambiarias'
      en la base de datos usando un CSV local. 
    Muestra información del resultado en consola.
    """
    # Directorio del script actual y la ruta del CSV
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    CSV = os.path.join(
        carpeta_script, "..", "datasets", "bonos_argentinos_vencimiento.csv"
        )

    try:
        info = reemplazar_tabla_bonos_con_csv(CSV)
        print("✅ Tabla 'bonos' reemplazada correctamente en Supabase:")
        for k, v in info.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()