from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import sqlite3
import os
import time
import shutil

print("Inicio del scraping de plazos fijos...")

# Carpeta del script y ruta a la base de datos existente
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(
    carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db"
)
os.makedirs(os.path.dirname(db_path), exist_ok=True)
# Crea carpeta si no existe

# Configuración del navegador Chrome en modo headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecuta sin abrir ventana
options.add_argument("--no-sandbox")  # Evita problemas de permisos
options.add_argument("--disable-dev-shm-usage")
# Evita errores de memoria compartida

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

driver.get("https://comparatasas.ar/plazos-fijos")
time.sleep(5)  # Espera a que cargue la página dinámicamente

# Localizar el contenedor principal de los plazos fijos
try:
    contenedor = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/main/div[2]/div/div[2]"
    )
    plazos = contenedor.find_elements(By.TAG_NAME, "a")
    # Cada plazo está en un enlace
except Exception:
    print("❌ No se encontró el contenedor de plazos fijos")
    driver.quit()
    exit()

data = []

# Extraer información de cada plazo fijo
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

        # Limpiar porcentaje y convertir a float
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


# Conectamos la base de datos existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Eliminamos la tabla anterior si existe
cursor.execute("DROP TABLE IF EXISTS plazos_fijos")
# Creamos la tabla desde cero con el esquema correcto
cursor.execute(
    """
CREATE TABLE plazos_fijos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    banco TEXT,
    plazo TEXT,
    tasa_pct REAL
)
"""
)

# Insertamos todos los registros de una vez
cursor.executemany(
    """
    INSERT INTO plazos_fijos (banco, plazo, tasa_pct)
    VALUES (?, ?, ?)""",
    data,
)

conn.commit()
conn.close()

print(f"✅ Tabla reemplazada y datos guardados en: {db_path}")
print("Fin del scraping de plazos fijos.")