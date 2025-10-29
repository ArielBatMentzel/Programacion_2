from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time

print("Inicio del scraping de bonos Rava...")

# Configurar Chrome en modo headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# Carpeta destino
carpeta_script = os.path.dirname(os.path.abspath(__file__))
carpeta_data = os.path.join(carpeta_script, "data")
os.makedirs(carpeta_data, exist_ok=True)
ruta_csv = os.path.join(carpeta_data, "bonos.csv")

# Iniciar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.rava.com/cotizaciones/bonos")
time.sleep(5)  # Esperar a que cargue la tabla

# Localizar la tabla
tabla = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div/div[2]/table")
filas = tabla.find_elements(By.TAG_NAME, "tr")

# Extraer datos
datos = []
for fila in filas:
    if fila.get_attribute("id") == "titulos":
        continue  # saltar fila de encabezados
    celdas = fila.find_elements(By.TAG_NAME, "td")
    if celdas:
        datos.append([c.get_attribute("textContent").strip() for c in celdas])

# Definir columnas (según estructura de Rava)
columnas = ["Especie","Último","% Día","% Mes","% Año",
            "Anterior","Apertura","Mínimo","Máximo",
            "Hora","Vol. Nominal","Vol. Efectivo"]

# Crear DataFrame y guardar CSV
df = pd.DataFrame(datos, columns=columnas)
df.to_csv(ruta_csv, index=False)

print(f"✅ Archivo guardado en: {ruta_csv}")
driver.quit()
print("Fin del scraping de bonos Rava.")
