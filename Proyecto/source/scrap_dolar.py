from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from sqlalchemy import text
import re
import shutil
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import crear_engine


print("Iniciando scraping de dólar...")

# CONFIG DB (Supabase via SQLAlchemy)
engine = crear_engine()

# CONFIGURAR SELENIUM 
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Detectar entorno y asignar driver
if os.getenv("RENDER"):
    # Entorno Render
    chromium_path = "/usr/bin/chromium"
    chromedriver_path = "/usr/bin/chromedriver"

    if not os.path.exists(chromium_path) or not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"En Render no se encontró Chromium o ChromeDriver en {chromium_path} / {chromedriver_path}")

    options.binary_location = chromium_path
    service = Service(chromedriver_path)
    print("Usando Chromium y ChromeDriver del sistema (Render)")
else:
    # Entorno local
    service = Service()  # Selenium busca automáticamente el driver en el PATH
    print("Usando Chrome local (PATH)")

#Crear driver con manejo de errores
try:
    driver = webdriver.Chrome(service=service, options=options)
except WebDriverException:
    # Solo en local, intentar webdriver_manager
    if not os.getenv("RENDER"):
        print("Error con ChromeDriver del sistema, intentando con ChromeDriverManager...")
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print("ChromeDriverManager instalado correctamente")
        except WebDriverException:
            print("Error con ChromeDriverManager, limpiando caché y reintentando...")
            shutil.rmtree(os.path.expanduser("~/.wdm"), ignore_errors=True)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print("ChromeDriverManager reinstalado correctamente")
    else:
        raise  # En Render, propagamos el error si falla
    
# Abrir página
driver.get("https://dolarhoy.com/")
wait = WebDriverWait(driver, 7)

# Extraer los datos
bloques = wait.until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "div.tile.is-child, div.tile.is-child.only-mobile")
    )
)

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

data = []
for b in bloques:
    try:
        tipo = b.find_element(
            By.CSS_SELECTOR, ".titleText"
            ).text.strip().upper()
        compra = b.find_element(
            By.CSS_SELECTOR, ".compra .val"
            ).text.strip()
        venta = b.find_element(
            By.CSS_SELECTOR, ".venta .val"
            ).text.strip()
        variacion = b.find_element(
            By.CSS_SELECTOR, ".var-porcentaje div"
            ).text.strip()

        data.append((tipo, limpiar_numero(compra), limpiar_numero(venta), limpiar_numero(variacion)))
    except Exception:
        continue

driver.quit()
print("Datos extraídos de la web.")

# Guardamos en Supabase
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS datos_financieros.dolar"))
    conn.execute(text("""
        CREATE TABLE datos_financieros.dolar (
            id SERIAL PRIMARY KEY,
            tipo TEXT,
            compra DOUBLE PRECISION,
            venta DOUBLE PRECISION,
            variacion DOUBLE PRECISION
        )
    """))
    conn.execute(
        text("INSERT INTO datos_financieros.dolar (tipo, compra, venta, variacion) VALUES (:tipo, :compra, :venta, :variacion)"),
        [{"tipo": t, "compra": c, "venta": v, "variacion": var} for (t, c, v, var) in data]
    )

print("✅ Tabla 'dolar' reemplazada y datos guardados en Supabase.")