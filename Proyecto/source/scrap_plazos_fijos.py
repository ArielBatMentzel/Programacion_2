# scrap_plazos_fijos.py
"""
Scraping de plazos fijos desde comparatasas.ar y almacenamiento en SQLite.

Reglas:
- La tabla 'plazos_fijos' se elimina si existía.
- Se crean las columnas banco, plazo y tasa_pct.
- Se insertan todos los datos extraídos de la web.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import os
import time

print("Inicio del scraping de plazos fijos...")

# Ruta de la base de datos existente
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(
    carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db"
)
# Asegura existencia de la carpeta
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Configuración del driver Chrome headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.get("https://comparatasas.ar/plazos-fijos")
time.sleep(5)  # Esperar carga dinámica del sitio

# Localizar contenedor principal de plazos fijos
try:
    contenedor = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/main/div[2]/div/div[2]"
    )
    plazos = contenedor.find_elements(By.TAG_NAME, "a")
except Exception:
    print("❌ No se encontró el contenedor de plazos fijos")
    driver.quit()
    exit()

# Extraer datos: banco, plazo y tasa
data = []
for p in plazos:
    try:
        banco = p.find_element(
            By.CSS_SELECTOR, "div.flex-col div.font-medium"
        ).text.strip()
        plazo = p.find_element(
            By.CSS_SELECTOR, "div.flex-wrap span.font-medium"
        ).text.strip()
        tasa = p.find_element(
            By.CSS_SELECTOR, "div.text-primary-600"
        ).text.strip()
        # Normalizar tasa: eliminar % y reemplazar coma por punto
        tasa = tasa.replace("%", "").replace(",", ".")
        try:
            tasa = float(tasa)
        except Exception:
            tasa = None
        data.append([banco, plazo, tasa])
    except Exception:
        continue

driver.quit()
print(f"✅ Datos extraídos: {len(data)} filas")

# Guardar en SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Eliminar tabla anterior si existía
cursor.execute("DROP TABLE IF EXISTS plazos_fijos")

# Crear tabla desde cero
cursor.execute("""
CREATE TABLE plazos_fijos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    banco TEXT,
    plazo TEXT,
    tasa_pct REAL
)
""")

# Insertar todos los registros de una vez
cursor.executemany("""
INSERT INTO plazos_fijos (banco, plazo, tasa_pct)
VALUES (?, ?, ?)
""", data)

conn.commit()
conn.close()
print(f"✅ Tabla reemplazada y datos guardados en: {db_path}")
print("Fin del scraping de plazos fijos.")
