# archivo: Proyecto/utils/scrap_runner.py
import subprocess
import time
import os
from typing import List

# Base de scrapers
SCRAPERS_DIR = os.path.join(os.path.dirname(__file__), "..", "source")

# Map "nombre fácil" -> archivo dentro de source/
SCRAPERS_MAP = {
    "dolar": "scrap_dolar.py",
    "plazo_fijo": "scrap_plazos_fijos.py",
    "bono": "scrap_bono.py",
    "letras": "scrap_letras.py",
    "bandas": "scrap_bandas_cambiarias.py"
}

def run_scraper_blocking(nombre: str):
    archivo = SCRAPERS_MAP.get(nombre)
    if not archivo:
        print(f"❌ No se encontró scraper para '{nombre}'")
        return

    path = os.path.join(SCRAPERS_DIR, archivo)
    if not os.path.exists(path):
        print(f"❌ No se encontró el archivo del scraper '{archivo}'")
        return

    print(f"▶ Ejecutando {archivo} ...")
    start = time.time()
    
    try:
        result = subprocess.run(
            ["python", path],  # o sys.executable para usar el mismo intérprete
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
        print(f"✅ {archivo} finalizó correctamente en {time.time()-start:.2f} s.")
    except subprocess.CalledProcessError as e:
        print(f"❌ {archivo} falló con código {e.returncode} en {time.time()-start:.2f} s.")
        if e.stdout:
            print(e.stdout.strip())
        if e.stderr:
            print(e.stderr.strip())

def scrap(nombres: List[str]):
    """
    Ejecuta los scrapers de manera síncrona.
    
    Posibles:
    "dolar"
    "plazo_fijo"
    "bono"
    "letras"
    "bandas"
    
    Ejemplo: scrap(["bono","plazo_fijo"])
    """
    for name in nombres:
        run_scraper_blocking(name)
