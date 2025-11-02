import os
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

print("Inicio del scraping de bandas cambiarias...")

# Configurar Chrome headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# Rutas
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(carpeta_script, "..", "db", "datos_financieros.db")  # apunta a la DB existente

# Iniciar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.bcra.gob.ar/PublicacionesEstadisticas/bandas-cambiarias-piso-techo.asp")

# Esperar que la tabla esté presente
tabla = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, "//table"))
)
filas = tabla.find_elements(By.TAG_NAME, "tr")

datos = []
for fila in filas[1:]:
    celdas = fila.find_elements(By.TAG_NAME, "td")
    if len(celdas) >= 3:
        fecha = celdas[0].text.strip()
        banda_inferior = float(celdas[1].text.strip().replace(".", "").replace(",", ".").replace("$", ""))
        banda_superior = float(celdas[2].text.strip().replace(".", "").replace(",", ".").replace("$", ""))
        datos.append((fecha, banda_inferior, banda_superior))

driver.quit()
print(f"✅ Datos extraídos: {len(datos)} filas")

# Guardar en la base de datos existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bandas_cambiarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    banda_inferior REAL,
    banda_superior REAL
)
""")

for fila in datos:
    cursor.execute("""
    INSERT INTO bandas_cambiarias (fecha, banda_inferior, banda_superior)
    VALUES (?, ?, ?)
    """, fila)

conn.commit()
conn.close()
print(f"✅ Datos guardados en la base existente: {db_path}")
