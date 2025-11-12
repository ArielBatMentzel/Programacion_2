from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import os
import re

print("Iniciando scraping de dólar...")

# Rutas
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db")  # usa la db existente

# Configurar Selenium headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Abrir navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://dolarhoy.com/")
wait = WebDriverWait(driver, 10)

# Bloques de cotización
bloques = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "div.tile.is-child, div.tile.is-child.only-mobile")
))

data = []
for b in bloques:
    try:
        tipo = b.find_element(By.CSS_SELECTOR, ".titleText").text.strip().upper()
        compra = b.find_element(By.CSS_SELECTOR, ".compra .val").text.strip()
        venta = b.find_element(By.CSS_SELECTOR, ".venta .val").text.strip()
        variacion = b.find_element(By.CSS_SELECTOR, ".var-porcentaje div").text.strip()

        # Limpiar número y mantener todos los decimales
        def limpiar_numero(valor):
            valor = re.sub(r"[^\d.,-]", "", valor).replace(",", ".")
            try:
                return float(valor)
            except:
                return None

        data.append([tipo, limpiar_numero(compra), limpiar_numero(venta), limpiar_numero(variacion)])
    except:
        continue

driver.quit()
print("Datos extraídos de la web.")

# Guardar en la base existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 🟢 CAMBIO 1: eliminar la tabla anterior si existe
cursor.execute("DROP TABLE IF EXISTS dolar")

# 🟢 CAMBIO 2: crear la tabla desde cero (sin IF NOT EXISTS)
cursor.execute("""
CREATE TABLE dolar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    compra REAL,
    venta REAL,
    variacion REAL
)
""")

# 🟢 CAMBIO 3: insertar todos los registros de una vez con executemany()
cursor.executemany("""
INSERT INTO dolar (tipo, compra, venta, variacion)
VALUES (?, ?, ?, ?)
""", data)

conn.commit()
conn.close()
print(f"Tabla reemplazada y datos guardados en: {db_path}")
print("Fin del scraping de dólar.")
