import os
import time
import pandas as pd

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
            PRIMARY KEY (nombre, moneda)
        )
    """)

def reemplazar_tabla_con_csv(csv_path: str, db_path: str, tabla: str = "bonos") -> dict:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)
    esperadas = ["nombre", "moneda", "ultimo", "dia_pct", "mes_pct", "anio_pct"]
    faltantes = [c for c in esperadas if c not in df.columns]
    if faltantes:
        raise ValueError(f"El CSV debe incluir columnas {esperadas}. Faltan: {faltantes}")

    df["ultimo"] = df["ultimo"].map(_to_float)
    for c in ["dia_pct", "mes_pct", "anio_pct"]:
        df[c] = df[c].map(_to_float)

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        with conn:  # transacción atómica
            _crear_tabla_fresca(conn, tabla)  # <- SIEMPRE recrea la tabla con el esquema correcto
            conn.executemany(
                f"""INSERT INTO {tabla}
                    (nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                df[esperadas].itertuples(index=False, name=None)
            )

        return {"db": os.path.abspath(db_path), "tabla": tabla, "filas_insertadas": len(df), "csv": os.path.abspath(csv_path)}
    finally:
        conn.close()


# --- Ejecutar directo ---
if __name__ == "__main__":
    CSV = r"C:\tp_final\Programacion_2\Proyecto\letras_argentinas.csv"
    DB  = r"C:\tp_final\Programacion_2\Proyecto\db\datos_financieros\datos_financieros.db"
    info = reemplazar_tabla_con_csv(CSV, DB, tabla="letras")
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
# import re

# print("Iniciando scraping de letras...")

# # Ruta relativa a la base de datos existente
# db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "datos_financieros", "datos_financieros.db")

# # Configurar Selenium
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# try:
#     driver.get("https://www.cohen.com.ar/Bursatil/Cotizacion/Letras")
#     time.sleep(3)

#     table = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[8]/div[1]/table")
#     rows = table.find_elements(By.TAG_NAME, "tr")

#     data = []
#     for row in rows:
#         cells = row.find_elements(By.TAG_NAME, "td")
#         if not cells:
#             continue
#         fila = [c.text.strip() for c in cells]

#         # Saltar filas vacías o solo con ""
#         if all(v in ["", "null"] for v in fila):
#             continue

#         # Asegurar 15 columnas
#         while len(fila) < 15:
#             fila.append(None)
#         data.append(fila[:15])

# finally:
#     driver.quit()

# # Guardar en la tabla 'letras' de la base existente
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS letras (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     codigo TEXT,
#     tipo TEXT,
#     liquidacion TEXT,
#     fecha TEXT,
#     hora TEXT,
#     moneda TEXT,
#     variacion REAL,
#     ultimo_precio REAL,
#     apertura REAL,
#     cierre_ant REAL,
#     precio_max REAL,
#     precio_min REAL,
#     vn REAL,
#     monto_negociado REAL,
#     op REAL
# )
# """)

# # Convertir valores numéricos
# def limpiar_num(valor):
#     if valor in ["", None]:
#         return None
#     valor = re.sub(r'[^\d,-]', '', valor).replace(".", "").replace(",", ".")
#     try:
#         return float(valor)
#     except:
#         return None

# for fila in data:
#     fila_limpia = [fila[0], fila[1], fila[2], fila[3], fila[4], fila[5]] + [limpiar_num(v) for v in fila[6:]]
#     cursor.execute("""
#         INSERT INTO letras (
#             codigo, tipo, liquidacion, fecha, hora, moneda,
#             variacion, ultimo_precio, apertura, cierre_ant,
#             precio_max, precio_min, vn, monto_negociado, op
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, fila_limpia)

# conn.commit()
# conn.close()
# print(f"✅ Datos guardados en la base existente: {db_path}")
