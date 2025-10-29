from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time

print("Inicio del scraping de plazos fijos...")

# Carpeta del script y data
carpeta_script = os.path.dirname(os.path.abspath(__file__))
ruta_data = os.path.join(carpeta_script, "data")
os.makedirs(ruta_data, exist_ok=True)
ruta_csv = os.path.join(ruta_data, "plazos_fijos.csv")

# Inicializar driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://comparatasas.ar/plazos-fijos")
time.sleep(5)  # esperar carga dinámica

# Contenedor principal
contenedor = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[2]/div/div[2]")
plazos = contenedor.find_elements(By.TAG_NAME, "a")

data = []
for p in plazos:
    try:
        banco = p.find_element(By.CSS_SELECTOR, "div.flex-col div.font-medium").text.strip()
        plazo = p.find_element(By.CSS_SELECTOR, "div.flex-wrap span.font-medium").text.strip()
        tasa = p.find_element(By.CSS_SELECTOR, "div.text-primary-600").text.strip()
        data.append([banco, plazo, tasa])
    except Exception as e:
        # ignorar elementos que no coinciden
        continue

driver.quit()

# Guardar CSV
df = pd.DataFrame(data, columns=["Banco", "Plazo", "Tasa"])
df.to_csv(ruta_csv, index=False)
print(f"Scraping finalizado. Datos guardados en: {ruta_csv}")
