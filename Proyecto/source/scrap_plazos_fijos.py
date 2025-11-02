from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import os
import time

print("Inicio del scraping de plazos fijos...")

# Ruta de la base existente
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(carpeta_script, "..", "db", "datos_financieros.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Asegura que exista la carpeta

# Inicializar driver headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://comparatasas.ar/plazos-fijos")
time.sleep(5)  # Esperar carga dinámica

# Contenedor principal
try:
    contenedor = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[2]/div/div[2]")
    plazos = contenedor.find_elements(By.TAG_NAME, "a")
except:
    print("❌ No se encontró el contenedor de plazos fijos")
    driver.quit()
    exit()

data = []
for p in plazos:
    try:
        banco = p.find_element(By.CSS_SELECTOR, "div.flex-col div.font-medium").text.strip()
        plazo = p.find_element(By.CSS_SELECTOR, "div.flex-wrap span.font-medium").text.strip()
        tasa = p.find_element(By.CSS_SELECTOR, "div.text-primary-600").text.strip()
        # Quitar "%" y reemplazar coma por punto
        tasa = tasa.replace("%", "").replace(",", ".")
        try:
            tasa = float(tasa)
        except:
            tasa = None
        data.append([banco, plazo, tasa])
    except:
        continue

driver.quit()
print(f"✅ Datos extraídos: {len(data)} filas")

# Guardar en la base existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS plazos_fijos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    banco TEXT,
    plazo TEXT,
    tasa_pct REAL
)
""")

for fila in data:
    cursor.execute("""
    INSERT INTO plazos_fijos (banco, plazo, tasa_pct)
    VALUES (?, ?, ?)
    """, fila)

conn.commit()
conn.close()
print(f"✅ Datos guardados en la base existente: {db_path}")
print("Fin del scraping de plazos fijos.")
