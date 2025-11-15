"""
Este script lee un archivo CSV con datos de letras
y reemplaza la tabla correspondiente en Supabase, eliminando 
los datos existentes e insertando los nuevos. 
Realiza la conversión de valores numéricos.
"""

import pandas as pd
from sqlalchemy import text
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import engine


def _to_float(val):
    """
    Convierte un string a float.
    - Reemplaza ',' por '.'
    - Elimina '%'
    - Espacios son ignorados
    - None o NaN -> None
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).replace("%", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return None


def reemplazar_tabla_letras_con_csv(
    csv_path: str,
    tabla: str = "datos_financieros.letras"
) -> dict:
    """
    Reemplaza la tabla de letras en Supabase 
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
    esperadas = ["nombre", "moneda", "ultimo", "dia_pct", "mes_pct",
                 "anio_pct", "fecha_vencimiento"]
    faltan = [c for c in esperadas if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en el CSV: {faltan}")

    # Normalizar valores numéricos
    df["ultimo"] = df["ultimo"].map(_to_float)
    for c in ["dia_pct", "mes_pct", "anio_pct"]:
        df[c] = df[c].map(_to_float)

    # Asegurar orden de columnas
    df = df[esperadas]
    
    # Conectar a Supabase y reemplazar tabla
    with engine.begin() as conn:
        # Eliminar registros solo si la tabla existe
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
        # Insertar los nuevos datos
        df.to_sql(
            tabla_db,              # Nombre de la tabla
            conn,
            schema=esquema_db,     # Esquema
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
    Script ejecutable que reemplaza la tabla 'letras'
      en la base de datos usando un CSV local. 
    Muestra información del resultado en consola.
    """
    # Directorio del script actual y la ruta del CSV
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    CSV = os.path.join(
        carpeta_script, "..", "datasets", "letras_argentinas_vencimiento.csv"
        )

    try:
        info = reemplazar_tabla_letras_con_csv(CSV)
        print("✅ Tabla 'letras' reemplazada correctamente en Supabase:")
        for k, v in info.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()