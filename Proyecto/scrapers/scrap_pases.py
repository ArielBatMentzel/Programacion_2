from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time

# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecutar en segundo plano
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Carpeta de guardado
carpeta_script = os.path.dirname(os.path.abspath(__file__))
carpeta_data = os.path.join(carpeta_script, "data")
os.makedirs(carpeta_data, exist_ok=True)
archivo_csv = os.path.join(carpeta_data, "pases.csv")

# Paginación
MAX_PAGES = 26
ROWS_PER_PAGE = 20

# Lista para acumular datos
all_data = []

for page in range(MAX_PAGES):
    ini = page * ROWS_PER_PAGE
    url = f"https://www.screenermatic.com/bondsdescriptive.php?ini={ini}&hojassel={ROWS_PER_PAGE}"
    driver.get(url)
    time.sleep(2)  # Espera que cargue la tabla

    # Buscar tabla y filas
    try:
        tabla = driver.find_element(By.TAG_NAME, "table")
        filas = tabla.find_elements(By.TAG_NAME, "tr")[1:]  # Ignorar encabezado
    except:
        print(f"No se encontró tabla en la página {page+1}")
        continue

    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        datos_fila = [celda.text.strip() for celda in celdas]
        if datos_fila:  # Evita filas vacías
            all_data.append(datos_fila)

driver.quit()

# Guardar en CSV
if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv(archivo_csv, index=False, encoding="utf-8-sig")
    print(f"Datos guardados en {archivo_csv}")
else:
    print("No se extrajeron datos.")
