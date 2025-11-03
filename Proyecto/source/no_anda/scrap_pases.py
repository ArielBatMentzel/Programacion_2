from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import os
import time

print("Iniciando scraping de pases...")

# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Carpeta del script y base de datos existente
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(carpeta_script, "db", "datos_financieros.db")

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

    try:
        tabla = driver.find_element(By.TAG_NAME, "table")
        filas = tabla.find_elements(By.TAG_NAME, "tr")[1:]  # Ignorar encabezado
    except:
        print(f"No se encontró tabla en la página {page+1}")
        continue

    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        datos_fila = [celda.text.strip() for celda in celdas]
        if datos_fila:
            # Convertir números con comas a float
            for i in range(1, len(datos_fila)):
                valor = datos_fila[i].replace(".", "").replace(",", ".")
                try:
                    datos_fila[i] = float(valor)
                except:
                    pass
            all_data.append(datos_fila)

driver.quit()
print("✅ Datos extraídos de pases.")

# Guardar en la DB existente
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS pases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    tipo TEXT,
    emisor TEXT,
    fecha TEXT,
    vencimiento TEXT,
    moneda TEXT,
    cupón REAL,
    precio REAL,
    cantidad REAL
)
""")

for fila in all_data:
    # Rellenar con None si faltan columnas
    while len(fila) < 9:
        fila.append(None)
    cursor.execute("""
    INSERT INTO pases (
        codigo, tipo, emisor, fecha, vencimiento, moneda, cupón, precio, cantidad
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fila[:9])

conn.commit()
conn.close()
print(f"✅ Datos guardados en la base existente: {db_path}")
