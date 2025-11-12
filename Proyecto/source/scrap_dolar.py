from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import sqlite3
import os
import re
import shutil

print("Iniciando scraping de dólar...")

# Rutas
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(carpeta_script, "..", "db",
                       "datos_financieros", "datos_financieros.db")

# Configurar Selenium headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Abrir navegador (se autorepara si ChromeDriver falla)
try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
except WebDriverException as e:
    print("⚠️ Error con ChromeDriver, limpiando caché y reintentando...")
    shutil.rmtree(os.path.expanduser("~/.wdm"), ignore_errors=True)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

# Abrir página
driver.get("https://dolarhoy.com/")
wait = WebDriverWait(driver, 10)

# Extraer los datos
bloques = wait.until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "div.tile.is-child, div.tile.is-child.only-mobile")
    )
)
data = []


def limpiar_numero(valor):
    """
    Convierte un string a float, ignorando símbolos y manteniendo decimales.
    Ejemplo: "$350,25" -> 350.25
    Retorna None si no es convertible.
    """
    valor = re.sub(r"[^\d.,-]", "", valor).replace(",", ".")
    try:
        return float(valor)
    except Exception:
        return None


for b in bloques:
    try:
        tipo = b.find_element(
            By.CSS_SELECTOR, ".titleText"
            ).text.strip().upper()
        compra = b.find_element(By.CSS_SELECTOR, ".compra .val").text.strip()
        venta = b.find_element(By.CSS_SELECTOR, ".venta .val").text.strip()
        variacion = b.find_element(
            By.CSS_SELECTOR, ".var-porcentaje div"
            ).text.strip()

        data.append([tipo, limpiar_numero(compra), limpiar_numero(venta),
                     limpiar_numero(variacion)])
    except Exception:
        continue

driver.quit()
print("Datos extraídos de la web.")

# Guardar en la base existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Eliminamos la tabla anterior si existe 
cursor.execute("DROP TABLE IF EXISTS dolar")
# Creamos la tabla desde cero 
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
# Insertamos todos los registros de una vez con executemany()
cursor.executemany(
    """INSERT INTO dolar (tipo, compra, venta, variacion)
       VALUES (?, ?, ?, ?)""",
    data
)

conn.commit()
conn.close()

print(f"✅ Tabla reemplazada y datos guardados en: {db_path}")
print("Fin del scraping de dólar.")