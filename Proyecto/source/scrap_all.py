import os
import subprocess
import sys

# Carpeta actual donde están los scrapers y este script
source_dir = os.path.dirname(__file__)

# Listar todos los archivos .py excepto este mismo
scrapers = [f for f in os.listdir(source_dir) 
            if f.endswith(".py") and f != os.path.basename(__file__)]

def run_scraper(scraper):
    path = os.path.join(source_dir, scraper)
    print(f"▶ Ejecutando {scraper} ...")
    
    # Ejecutar scraper, silenciando solo stdout (prints) pero mostrando errores
    result = subprocess.run(
        [sys.executable, path], # El sys.executable permite utilizar el python actualmente en uso (y no obliga a usar el global)
        stdout=subprocess.DEVNULL,  # prints silenciados
        stderr=None,                # errores se muestran en consola
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {scraper} finalizó correctamente.")
    else:
        print(f"❌ {scraper} falló.")

# Ejecutar todos los scrapers en orden
for scraper in scrapers:
    run_scraper(scraper)
