from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time

print("Inicio del scraping de bandas cambiarias...")

# Configurar Chrome en modo headless (sin ventana)
options = Options()
options.add_argument("--headless=new")  # modo invisible moderno
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# Carpeta destino
carpeta_script = os.path.dirname(os.path.abspath(__file__))
carpeta_data = os.path.join(carpeta_script, "data")
os.makedirs(carpeta_data, exist_ok=True)
ruta_csv = os.path.join(carpeta_data, "bandas.csv")

# Iniciar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.bcra.gob.ar/PublicacionesEstadisticas/bandas-cambiarias-piso-techo.asp")
time.sleep(5)

# Extraer tabla
tabla = driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div/div/table")
filas = tabla.find_elements(By.TAG_NAME, "tr")

data = []
for fila in filas:
    celdas = fila.find_elements(By.TAG_NAME, "td")
    if celdas:
        data.append([c.text.strip() for c in celdas])

df = pd.DataFrame(data, columns=["Fecha", "Banda Inferior", "Banda Superior"])
df.to_csv(ruta_csv, index=False)

print(f"✅ Archivo guardado en: {ruta_csv}")

driver.quit()
print("Fin del scraping de bandas cambiarias.")
