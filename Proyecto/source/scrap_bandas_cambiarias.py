"""
Carga los datos de bandas cambiarias desde CSV a la base de datos.
Elimina las filas existentes y carga las nuevas.
"""

import os
import sqlite3
import pandas as pd


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


def _crear_tabla_fresca(conn, tabla: str):
    """
    Elimina y recrea la tabla con el esquema correcto.

    :param conn: conexión sqlite3
    :param tabla: nombre de la tabla
    """
    conn.execute(f"DROP TABLE IF EXISTS {tabla};")
    conn.execute(f"""
        CREATE TABLE {tabla} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            banda_inferior REAL,
            banda_superior REAL,
            ancho REAL
        )
    """)


def reemplazar_tabla_bandas_con_csv(
    csv_path: str,
    db_path: str,
    tabla: str = "bandas_cambiarias"
) -> dict:
    """
    Reemplaza toda la tabla de bandas cambiarias con los datos del CSV.
    - Elimina todas las filas existentes
    - Inserta los datos del CSV
    - Transacción atómica

    CSV esperado:
    fecha,banda_inferior,banda_superior,ancho

    :param csv_path: ruta del CSV
    :param db_path: ruta de la base de datos SQLite
    :param tabla: nombre de la tabla a reemplazar
    :return: dict con información de la operación
    """
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

    # Crear directorio de la BD si no existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Conectar y guardar
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        with conn:  # transacción atómica
            _crear_tabla_fresca(conn, tabla)
            conn.executemany(
                f"""INSERT INTO {tabla}
                    (fecha, banda_inferior, banda_superior, ancho)
                    VALUES (?, ?, ?, ?)""",
                df[esperadas].itertuples(index=False, name=None)
            )

        return {
            "db": os.path.abspath(db_path),
            "tabla": tabla,
            "filas_insertadas": len(df),
            "csv": os.path.abspath(csv_path)
        }
    finally:
        conn.close()


# --- Ejecutar directo ---
if __name__ == "__main__":
    """
    Script ejecutable que reemplaza la tabla 'bandas_cambiarias'
      en la base de datos
    usando un CSV local. Muestra información del resultado en consola.
    """
    # Directorio del script actual
    carpeta_script = os.path.dirname(os.path.abspath(__file__))

    # Rutas de la base de datos y del CSV
    DB = os.path.join(
        carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db"
        )
    CSV = os.path.join(
        carpeta_script, "..", "datasets", "bandas_nov2025_dic2028.csv"
        )

    try:
        # Reemplazar tabla con los datos del CSV
        info = reemplazar_tabla_bandas_con_csv(
            CSV, DB, tabla="bandas_cambiarias"
            )

        # Mostrar información del reemplazo
        print("✅ Tabla 'bandas_cambiarias' reemplazada correctamente:")
        for k, v in info.items():
            print(f"  {k}: {v}")

    except Exception as e:
        # Mostrar error completo en consola
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


"""
A partir de acá, no se usan las siguientes funciones
porque los datos que scrappeamos
requieren de conocimiento financiero muy avanzado
para poder realizar los distintos
calculos de las fórmulas para computar el rendimiento.
"""


# import os
# import sqlite3
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# print("Inicio del scraping de bandas cambiarias...")

# # Configurar Chrome headless
# options = Options()
# options.add_argument("--headless=new")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--disable-gpu")

# # Rutas
# carpeta_script = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(carpeta_script, "..", "db",
# "datos_financieros", "datos_financieros.db")

# # Iniciar navegador
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
#  options=options)
# driver.get("https://www.bcra.gob.ar/PublicacionesEstadisticas/bandas-cambiarias-piso-techo.asp")

# # Esperar que la tabla esté presente
# tabla = WebDriverWait(driver, 15).until(
#     EC.presence_of_element_located((By.XPATH, "//table"))
# )
# filas = tabla.find_elements(By.TAG_NAME, "tr")

# # Extraer datos
# datos = []
# for fila in filas[1:]:
#     celdas = fila.find_elements(By.TAG_NAME, "td")
#     if len(celdas) >= 3:
#         fecha = celdas[0].text.strip()
#         banda_inferior = float(celdas[1].text.strip().replace(".", "").
# replace(",", ".").replace("$", ""))
#         banda_superior = float(celdas[2].text.strip().replace(".", "").
# replace(",", ".").replace("$", ""))
#         datos.append((fecha, banda_inferior, banda_superior))

# driver.quit()
# print(f"✅ Datos extraídos: {len(datos)} filas")

# # Guardar en la base de datos existente (reemplazando la tabla)
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()

# # Eliminar tabla anterior si existe
# cursor.execute("DROP TABLE IF EXISTS bandas_cambiarias")

# # Crear tabla nueva
# cursor.execute("""
# CREATE TABLE bandas_cambiarias (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     fecha TEXT,
#     banda_inferior REAL,
#     banda_superior REAL
# )
# """)

# # Insertar nuevos datos
# cursor.executemany("""
# INSERT INTO bandas_cambiarias (fecha, banda_inferior, banda_superior)
# VALUES (?, ?, ?)
# """, datos)

# conn.commit()
# conn.close()
# print(f"✅ Tabla reemplazada y datos guardados en: {db_path}")
