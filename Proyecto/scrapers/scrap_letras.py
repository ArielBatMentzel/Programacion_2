import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# --- Configuración ---
url = "https://www.cohen.com.ar/Bursatil/Cotizacion/Letras"

# Carpeta data relativa al script
data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)
csv_path = os.path.join(data_dir, "letras.csv")

# Encabezados correctos (15 columnas)
headers = [
    "Código", "Tipo", "Liquidación", "Fecha", "Hora", "Moneda", "Variación",
    "Último Pcio.", "Apertura", "Cierre Ant.", "Pcio. Máx.", "Pcio. Mín.",
    "V.Nominal", "Mto. Negoc.", "OP"
]

print("Iniciando scraping de letras...")

# --- Configurar Selenium WebDriver ---
chrome_options = Options()
chrome_options.add_argument("--headless")  # corre en segundo plano
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(url)
    time.sleep(3)  # esperar a que cargue la tabla

    # Buscar la tabla
    table = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[8]/div[1]/table")
    rows = table.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells:
            continue
        # Las primeras tres celdas vienen combinadas en la página, separarlas
        codigo = cells[0].text.strip()
        tipo = cells[1].text.strip() if len(cells) > 1 else ""
        liquidacion = cells[2].text.strip() if len(cells) > 2 else ""
        resto = [c.text.strip() for c in cells[3:]]
        # Asegurar que la fila tenga 15 columnas
        row_data = [codigo, tipo, liquidacion] + resto
        while len(row_data) < 15:
            row_data.append("")  # rellenar vacíos
        data.append(row_data[:15])

    # Guardar en CSV
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(csv_path, index=False, sep=",", encoding="utf-8-sig")

    print(f"Scraping finalizado. Datos guardados en: {csv_path}")

finally:
    driver.quit()
