import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import re

print("Iniciando scraping de letras...")

# Ruta relativa a la base de datos existente
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "datos_financieros", "datos_financieros.db")

# Configurar Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    driver.get("https://www.cohen.com.ar/Bursatil/Cotizacion/Letras")
    time.sleep(3)

    table = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[8]/div[1]/table")
    rows = table.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells:
            continue
        fila = [c.text.strip() for c in cells]

        # Saltar filas vacías o solo con ""
        if all(v in ["", "null"] for v in fila):
            continue

        # Asegurar 15 columnas
        while len(fila) < 15:
            fila.append(None)
        data.append(fila[:15])

finally:
    driver.quit()

# Guardar en la tabla 'letras' de la base existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS letras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    tipo TEXT,
    liquidacion TEXT,
    fecha TEXT,
    hora TEXT,
    moneda TEXT,
    variacion REAL,
    ultimo_precio REAL,
    apertura REAL,
    cierre_ant REAL,
    precio_max REAL,
    precio_min REAL,
    vn REAL,
    monto_negociado REAL,
    op REAL
)
""")

# Convertir valores numéricos
def limpiar_num(valor):
    if valor in ["", None]:
        return None
    valor = re.sub(r'[^\d,-]', '', valor).replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except:
        return None

for fila in data:
    fila_limpia = [fila[0], fila[1], fila[2], fila[3], fila[4], fila[5]] + [limpiar_num(v) for v in fila[6:]]
    cursor.execute("""
        INSERT INTO letras (
            codigo, tipo, liquidacion, fecha, hora, moneda,
            variacion, ultimo_precio, apertura, cierre_ant,
            precio_max, precio_min, vn, monto_negociado, op
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fila_limpia)

conn.commit()
conn.close()
print(f"✅ Datos guardados en la base existente: {db_path}")
