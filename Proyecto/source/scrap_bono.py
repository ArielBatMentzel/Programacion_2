"""
Crear una función que cargue los datos del CSV a la base de datos de 'datos_financieros.db'
Asegurarse que cuando se ejecute la función, al menos en datos_financieros, elimine las filas 
que ya estan y cargue las nuevas.
"""
import os
import sqlite3
import pandas as pd

def _to_float(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).replace("%", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return None


def _crear_tabla_fresca(conn, tabla: str):
    # si existe con otro esquema, la volamos y la recreamos con el correcto
    conn.execute(f"DROP TABLE IF EXISTS {tabla};")
    conn.execute(f"""
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
    """)


def reemplazar_tabla_con_csv(csv_path: str, db_path: str, tabla: str = "bonos") -> dict:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)
    esperadas = ["nombre", "moneda", "ultimo",
                 "dia_pct", "mes_pct", "anio_pct", "fecha_vencimiento"]
    faltantes = [c for c in esperadas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"El CSV debe incluir columnas {esperadas}. Faltan: {faltantes}")

    df["ultimo"] = df["ultimo"].map(_to_float)
    for c in ["dia_pct", "mes_pct", "anio_pct"]:
        df[c] = df[c].map(_to_float)

    df["fecha_vencimiento"] = pd.to_datetime(
        df["fecha_vencimiento"], errors="coerce").dt.strftime("%Y-%m-%d")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        with conn:  # transacción atómica
            # <- SIEMPRE recrea la tabla con el esquema correcto
            _crear_tabla_fresca(conn, tabla)
            conn.executemany(
                f"""INSERT INTO {tabla}
                    (nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct, fecha_vencimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                df[esperadas].itertuples(index=False, name=None)
            )

        return {"db": os.path.abspath(db_path), "tabla": tabla, "filas_insertadas": len(df), "csv": os.path.abspath(csv_path)}
    finally:
        conn.close()


# --- Ejecutar directo ---
if __name__ == "__main__":
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    DB = os.path.join(carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db")  # usa la db existente
    CSV = os.path.join(carpeta_script, "..", "datasets", "bonos_argentinos_vencimiento.csv")  
    info = reemplazar_tabla_con_csv(CSV, DB, tabla="bonos")
    print("✅ OK:", info)


"""
A partir de acá, no se usan las siguientes funciones porque los datos que scrappeamos
requieren de conocimiento financiero muy avanzado para poder realizar los distintos 
calculos de las fórmulas para computar el rendimiento.
"""

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import sqlite3
# import os
# import time

# print("Inicio del scraping de bonos...")

# # Configurar Chrome en modo headless
# options = Options()
# options.add_argument("--headless=new")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--disable-gpu")

# # Carpeta del proyecto y base de datos
# carpeta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# db_path = os.path.join(carpeta_proyecto, "db","datos_financieros", "datos_financieros.db")
# os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Crear carpeta si no existe

# # Iniciar navegador
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver.get("https://www.rava.com/cotizaciones/bonos")
# time.sleep(5)  # Esperar a que cargue la tabla

# # Localizar la tabla
# tabla = driver.find_element(By.XPATH, "//table")
# filas = tabla.find_elements(By.TAG_NAME, "tr")

# datos = []
# for fila in filas:
#     celdas = fila.find_elements(By.TAG_NAME, "td")
#     if celdas:
#         fila_datos = []
#         for i, c in enumerate(celdas):
#             valor = c.get_attribute("textContent").strip()
#             # Convertir a float los valores numéricos, excepto la primera columna y "-" vacío
#             if i != 0 and valor not in ["-", ""]:
#                 valor = valor.replace(".", "").replace(",", ".")
#                 try:
#                     valor = float(valor)
#                 except ValueError:
#                     pass
#             fila_datos.append(valor)
#         datos.append(fila_datos)

# driver.quit()
# print("✅ Datos extraídos de Rava.")

# # Guardar en la base de datos
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()

# # Crear tabla si no existe
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS bonos (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     especie TEXT,
#     ultimo REAL,
#     'Dia_pct' REAL,
#     'Mes_pct' REAL,
#     'Año_pct' REAL,
#     anterior REAL,
#     apertura REAL,
#     minimo REAL,
#     maximo REAL,
#     hora TEXT,
#     vol_nominal REAL,
#     vol_efectivo REAL
# )
# """)

# for fila in datos:
#     # Completar la fila con None si faltan columnas
#     while len(fila) < 12:
#         fila.append(None)
#     cursor.execute("""
#     INSERT INTO bonos (
#         especie, ultimo, 'Dia_pct', 'Mes_pct', 'Año_pct',
#         anterior, apertura, minimo, maximo,
#         hora, vol_nominal, vol_efectivo
#     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, fila)

# conn.commit()
# conn.close()
# print(f"✅ Datos guardados en la base: {db_path}")
# print("Fin del scraping de bonos.")