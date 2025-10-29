from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import os

print("Iniciando scraping de dólarhoy.com...")

# Configurar rutas
carpeta_script = os.path.dirname(os.path.abspath(__file__))
carpeta_data = os.path.join(carpeta_script, "data")
os.makedirs(carpeta_data, exist_ok=True)
ruta_csv = os.path.join(carpeta_data, "dolares.csv")

# Opciones headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Iniciar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://dolarhoy.com/")

wait = WebDriverWait(driver, 10)

# Bloques de cotizaciones
bloques = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "div.tile.is-child, div.tile.is-child.only-mobile")
))

data = []
for b in bloques:
    try:
        tipo = b.find_element(By.CSS_SELECTOR, ".titleText").text.strip().upper()
        compra = b.find_element(By.CSS_SELECTOR, ".compra .val").text.strip()
        venta = b.find_element(By.CSS_SELECTOR, ".venta .val").text.strip()
        variacion = b.find_element(By.CSS_SELECTOR, ".var-porcentaje div").text.strip()

        # Función para limpiar números
        def limpiar_numero(valor):
            valor = re.sub(r'[^\d.,-]', '', valor).replace(',', '.')
            try:
                return float(valor)
            except:
                return None

        data.append([tipo, limpiar_numero(compra), limpiar_numero(venta), limpiar_numero(variacion)])
    except:
        continue

driver.quit()

# Guardar DataFrame
df = pd.DataFrame(data, columns=["Tipo", "Compra", "Venta", "Variacion"])
df = df.dropna(how="all")
df.to_csv(ruta_csv, index=False)

print(f"✅ Scraping finalizado. Datos guardados en: {ruta_csv}")
