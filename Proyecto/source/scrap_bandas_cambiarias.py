import os
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import platform
import stat

print("Inicio del scraping de bandas cambiarias...")

# Configurar Chrome headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# Rutas
carpeta_script = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(carpeta_script, "..", "db", "datos_financieros", "datos_financieros.db")

# Iniciar navegador
# Diagnostic: obtener e imprimir la ruta del chromedriver que webdriver_manager descarga/usa
driver_path = ChromeDriverManager().install()
print(f"ChromeDriverManager returned: {driver_path}")
if not os.path.exists(driver_path):
    raise FileNotFoundError(f"Chromedriver not found at: {driver_path}")
# On Windows the binary should be an .exe and be executable
if platform.system() == "Windows":
    if not driver_path.lower().endswith('.exe'):
        print("Advertencia: el archivo del driver no termina en .exe — puede no ser un binario Windows válido.")
else:
    # For non-windows platforms check executable bit
    try:
        mode = os.stat(driver_path).st_mode
        if not (mode & stat.S_IXUSR):
            print("Advertencia: el driver no tiene el bit ejecutable set. Intentando continuar de todas formas.")
    except Exception as e:
        print(f"No se pudo comprobar permisos de ejecución: {e}")

driver = webdriver.Chrome(service=Service(driver_path), options=options)
driver.get("https://www.bcra.gob.ar/PublicacionesEstadisticas/bandas-cambiarias-piso-techo.asp")

# Esperar que la tabla esté presente
tabla = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, "//table"))
)
filas = tabla.find_elements(By.TAG_NAME, "tr")

# Extraer datos
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

# Guardar en la base de datos existente (reemplazando la tabla)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Eliminar tabla anterior si existe
cursor.execute("DROP TABLE IF EXISTS bandas_cambiarias")

# Crear tabla nueva
cursor.execute("""
CREATE TABLE bandas_cambiarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    banda_inferior REAL,
    banda_superior REAL
)
""")

# Insertar nuevos datos
cursor.executemany("""
INSERT INTO bandas_cambiarias (fecha, banda_inferior, banda_superior)
VALUES (?, ?, ?)
""", datos)

conn.commit()
conn.close()
print(f"✅ Tabla reemplazada y datos guardados en: {db_path}")
