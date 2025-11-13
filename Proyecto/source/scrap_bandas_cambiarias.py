"""
Carga los datos de bandas cambiarias desde CSV a la 
base de datos de Supabase.
Elimina las filas existentes y carga las nuevas.
"""

import pandas as pd
from sqlalchemy import text
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import crear_engine

# Solo carga el .env si existe (útil localmente, el Render lo ignora)
# Porque setea sus propias variables de entorno (setea el mismo el DB_URL)
engine = crear_engine()


def _to_float(val):
    """
    Convierte strings con ',' y espacios a float.
    None o NaN se devuelven como None.

    :param val: valor a convertir (str, float, None)
    :return: float o None
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return None


def reemplazar_tabla_bandas_con_csv(
    csv_path: str,
    tabla: str = "datos_financieros.bandas_cambiarias"
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
    esperadas = ["fecha", "banda_inferior", "banda_superior", "ancho"]
    faltantes = [c for c in esperadas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"El CSV debe incluir columnas {esperadas}. Faltan: {faltantes}"
            )

    # Normalizar columnas numéricas a float
    df["banda_inferior"] = df["banda_inferior"].map(_to_float)
    df["banda_superior"] = df["banda_superior"].map(_to_float)
    df["ancho"] = df["ancho"].map(_to_float)
    
    # Conectar a Supabase y reemplazar tabla
    with engine.begin() as conn:
        # Verificar si existe la tabla
        tabla_existe = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = '{esquema_db}' 
                AND table_name = '{tabla_db}'
            )
        """)).scalar()

        filas_borradas = 0
        if tabla_existe:
            # Borrar filas y obtener cantidad borrada
            filas_borradas = conn.execute(
                text(f"DELETE FROM {esquema_db}.{tabla_db}")
            ).rowcount

            # Reiniciar secuencia solo si hubo filas borradas
            if filas_borradas > 0:
                conn.execute(
                    text(f"ALTER SEQUENCE {esquema_db}.{tabla_db}_id_seq RESTART WITH 1")
                )
        else:
            # agregar columna id incremental
            df.insert(0, "id", range(1, len(df) + 1))

        # Insertar datos del CSV (crea tabla si no existía)
        df.to_sql(
            tabla_db,
            conn,
            schema=esquema_db,
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
        carpeta_script, "..", "datasets", "bandas_nov2025_dic2028.csv"
        )

    try:
        info = reemplazar_tabla_bandas_con_csv(CSV)
        print("✅ Tabla 'bandas_cambiarias' reemplazada correctamente en Supabase:")
        for k, v in info.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()