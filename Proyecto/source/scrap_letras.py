import os
import sqlite3
import pandas as pd

"""
Función para cargar datos de CSV en la base de datos 'datos_financieros.db'.
- Reemplaza completamente la tabla indicada.
- Normaliza valores numéricos y fechas.
"""


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


def _crear_tabla_fresca(conn, tabla: str):
    """
    Elimina la tabla existente (si hay) y la crea con el esquema correcto.
    - columnas:
    nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct, fecha_vencimiento
    - clave primaria: (nombre, moneda)
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
    Reemplaza completamente una tabla
      en la base de datos con los datos del CSV.
    
    Args:
        csv_path (str): ruta al archivo CSV con los datos
        db_path (str): ruta a la base de datos SQLite
        tabla (str): nombre de la tabla a reemplazar (por defecto "letras")
    
    Returns:
        dict:
          información del reemplazo incluyendo path DB,
            tabla, filas insertadas y CSV
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")

    # Leer CSV como strings
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

    # Conectar a la base de datos y reemplazar tabla
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        with conn:
            # Crear tabla nueva
            _crear_tabla_fresca(conn, tabla)
            # Insertar todos los registros
            conn.executemany(
                f"""INSERT INTO {tabla} (
                    nombre, moneda, ultimo, dia_pct, mes_pct,
                    anio_pct, fecha_vencimiento
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
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
    # Rutas relativas
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    DB = os.path.join(
        carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db"
        )
    CSV = os.path.join(
        carpeta_script, "..", "datasets", "letras_argentinas_vencimiento.csv"
        )
    
    # Ejecutar reemplazo de tabla
    info = reemplazar_tabla_con_csv(CSV, DB, tabla="letras")
    print("✅ OK:", info)


"""
A partir de acá,
 no se usan las siguientes funciones porque los datos que scrappeamos
requieren de conocimiento financiero
 muy avanzado para poder realizar los distintos 
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
# db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
#  "db", "datos_financieros", "datos_financieros.db")

# # Configurar Selenium
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# driver = webdriver.Chrome(service=Service
# (ChromeDriverManager().install()), options=chrome_options)

# try:
#     driver.get("https://www.cohen.com.ar/Bursatil/Cotizacion/Letras")
#     time.sleep(3)

#     table = driver.find_element(By.XPATH, "/
# html/body/div[1]/div[2]/div/div[8]/div[1]/table")
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
#     fila_limpia = [fila[0], fila[1], fila[2], fila[3], fila[4], fila[5]] 
# + [limpiar_num(v) for v in fila[6:]]
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