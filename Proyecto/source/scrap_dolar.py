from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from sqlalchemy import create_engine, text
import os
import re
import shutil
from dotenv import load_dotenv

print("Iniciando scraping de dólar...")

# CONFIG DB (Supabase via SQLAlchemy)
load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("⚠️ No se encontró la variable DB_URL en el entorno.")
engine = create_engine(DB_URL)

# CONFIGURAR SELENIUM 

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Intentamos primero con el driver del sistema (Render)
try:
    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
    print("Usando ChromeDriver del sistema (/usr/bin/chromedriver)")

# Si falla, usamos webdriver_manager (para entorno local)
except WebDriverException:
    print("Error con ChromeDriver del sistema, intentando con webdriver_manager...")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("ChromeDriverManager instalado correctamente")
    except WebDriverException as e:
        print("Error con ChromeDriverManager, limpiando caché y reintentando...")
        shutil.rmtree(os.path.expanduser("~/.wdm"), ignore_errors=True)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("ChromeDriverManager reinstalado correctamente")



driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)

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