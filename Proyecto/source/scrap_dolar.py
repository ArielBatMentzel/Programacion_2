# scrap_dolar.py
"""
Scraping dólar desde 'dolarhoy.com' y almacenamiento en SQLite.

- Descarga valores de compra, venta y variación de los tipos de dólar.
- Reemplaza la tabla 'dolar' en la base de datos 'datos_financieros.db'.
"""

import os
import re
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

print("Iniciando scraping de dólar...")

# Rutas
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(
    carpeta_script,
    "..",
    "db",
    "datos_financieros",
    "datos_financieros.db",
)

# Configuración de Selenium headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Abrir navegador
driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager().install()
    ),
    options=options
)
driver.get("https://dolarhoy.com/")
wait = WebDriverWait(driver, 10)

# Bloques de cotización
bloques = wait.until(
    EC.presence_of_all_elements_located(
        (
            By.CSS_SELECTOR,
            "div.tile.is-child, div.tile.is-child.only-mobile"
        )
    )
)


# Función para limpiar los números (mantener decimales)
def limpiar_numero(valor: str) -> float | None:
    valor = re.sub(r"[^\d.,-]", "", valor).replace(",", ".")
    try:
        return float(valor)
    except Exception:
        return None


# Extraer datos
data = []
for b in bloques:
    try:
        tipo = (
            b.find_element(By.CSS_SELECTOR, ".titleText")
            .text.strip()
            .upper()
        )
        compra = (
            b.find_element(By.CSS_SELECTOR, ".compra .val")
            .text.strip()
        )
        venta = (
            b.find_element(By.CSS_SELECTOR, ".venta .val")
            .text.strip()
        )
        variacion = (
            b.find_element(By.CSS_SELECTOR, ".var-porcentaje div")
            .text.strip()
        )
        data.append([
            tipo,
            limpiar_numero(compra),
            limpiar_numero(venta),
            limpiar_numero(variacion),
        ])
    except Exception:
        continue

driver.quit()
print(f"✅ Datos extraídos: {len(data)} registros.")

# Guardar en la base existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Eliminar tabla anterior
cursor.execute("DROP TABLE IF EXISTS dolar")

# Crear tabla nueva
cursor.execute(
    """
CREATE TABLE dolar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    compra REAL,
    venta REAL,
    variacion REAL
)
"""
)

# Insertar todos los registros
cursor.executemany(
    """
INSERT INTO dolar (tipo, compra, venta, variacion)
VALUES (?, ?, ?, ?)
""",
    data
)

conn.commit()
conn.close()
print(f"✅ Tabla reemplazada y datos guardados en: {db_path}")
print("Fin del scraping de dólar.")
