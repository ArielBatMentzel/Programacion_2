import sqlite3
import os
import time










"""
A partir de acá, no se usan las siguientes funciones porque los datos que scrappeamos
requieren de conocimiento financiero muy avanzado para poder realizar los distintos 
calculos de las fórmulas para computar el rendimiento.
"""

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import sqlite3
# import os
# import time

# print("Inicio del scraping de bonos...")

# # Configurar Chrome en modo headless
# options = Options()
# options.add_argument("--headless=new")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--disable-gpu")

# # Carpeta del proyecto y base de datos
# carpeta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# db_path = os.path.join(carpeta_proyecto, "db","datos_financieros", "datos_financieros.db")
# os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Crear carpeta si no existe

# # Iniciar navegador
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver.get("https://www.rava.com/cotizaciones/bonos")
# time.sleep(5)  # Esperar a que cargue la tabla

# # Localizar la tabla
# tabla = driver.find_element(By.XPATH, "//table")
# filas = tabla.find_elements(By.TAG_NAME, "tr")

# datos = []
# for fila in filas:
#     celdas = fila.find_elements(By.TAG_NAME, "td")
#     if celdas:
#         fila_datos = []
#         for i, c in enumerate(celdas):
#             valor = c.get_attribute("textContent").strip()
#             # Convertir a float los valores numéricos, excepto la primera columna y "-" vacío
#             if i != 0 and valor not in ["-", ""]:
#                 valor = valor.replace(".", "").replace(",", ".")
#                 try:
#                     valor = float(valor)
#                 except ValueError:
#                     pass
#             fila_datos.append(valor)
#         datos.append(fila_datos)

# driver.quit()
# print("✅ Datos extraídos de Rava.")

# # Guardar en la base de datos
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()

# # Crear tabla si no existe
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS bonos (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     especie TEXT,
#     ultimo REAL,
#     'Dia_pct' REAL,
#     'Mes_pct' REAL,
#     'Año_pct' REAL,
#     anterior REAL,
#     apertura REAL,
#     minimo REAL,
#     maximo REAL,
#     hora TEXT,
#     vol_nominal REAL,
#     vol_efectivo REAL
# )
# """)

# for fila in datos:
#     # Completar la fila con None si faltan columnas
#     while len(fila) < 12:
#         fila.append(None)
#     cursor.execute("""
#     INSERT INTO bonos (
#         especie, ultimo, 'Dia_pct', 'Mes_pct', 'Año_pct',
#         anterior, apertura, minimo, maximo,
#         hora, vol_nominal, vol_efectivo
#     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, fila)

# conn.commit()
# conn.close()
# print(f"✅ Datos guardados en la base: {db_path}")
# print("Fin del scraping de bonos.")
