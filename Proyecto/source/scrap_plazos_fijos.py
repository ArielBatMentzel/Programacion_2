from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from sqlalchemy import text
import os
import time
import shutil
from utils.conexion_db import crear_engine

print("Inicio del scraping de plazos fijos...")

engine = crear_engine()

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecuta sin abrir ventana
options.add_argument("--no-sandbox")  # Evita problemas de permisos
options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
except WebDriverException:
    print("⚠️ Error con ChromeDriver, limpiando caché y reintentando...")
    shutil.rmtree(os.path.expanduser("~/.wdm"), ignore_errors=True)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

driver.get("https://comparatasas.ar/plazos-fijos")
time.sleep(5)  # Espera a que cargue la página dinámicamente

# Localizar el contenedor principal de los plazos fijos
try:
    contenedor = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[2]/div/div[2]")
    plazos = contenedor.find_elements(By.TAG_NAME, "a")
except Exception:
    print("❌ No se encontró el contenedor de plazos fijos.")
    driver.quit()
    exit()

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

        tasa = tasa.replace("%", "").replace(",", ".")
        try:
            tasa = float(tasa)
        except Exception:
            tasa = None

        data.append((banco, plazo, tasa))
    except Exception:
        continue

driver.quit()
print(f"✅ Datos extraídos: {len(data)} filas")

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS datos_financieros.plazos_fijos"))
    conn.execute(text("""
        CREATE TABLE datos_financieros.plazos_fijos (
            id SERIAL PRIMARY KEY,
            banco TEXT,
            plazo TEXT,
            tasa_pct DOUBLE PRECISION
        )
    """))
    conn.execute(
        text("""
            INSERT INTO datos_financieros.plazos_fijos (banco, plazo, tasa_pct)
            VALUES (:banco, :plazo, :tasa_pct)
        """),
        [{"banco": b, "plazo": p, "tasa_pct": t} for (b, p, t) in data]
    )

print("✅ Tabla 'plazos_fijos' reemplazada y datos guardados en Supabase.")
print("Fin del scraping de plazos fijos.")