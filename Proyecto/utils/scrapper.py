# archivo: Proyecto/utils/scrap_runner.py
import os
import sys
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

# Carpeta donde están los scrapers
SCRAPERS_DIR = os.path.join(os.path.dirname(__file__), "..", "source")

# Map "nombre fácil" -> archivo dentro de source/
SCRAPERS_MAP = {
    "dolar": "scrap_dolar.py",
    "plazo_fijo": "scrap_plazos_fijos.py",
    "bono": "scrap_bono.py",
    "letras": "scrap_letras.py",
    "bandas": "scrap_bandas_cambiarias.py",
}

MAX_CONCURRENCY = 3  # Máximo de scrapers ejecutándose a la vez


def run_scraper_blocking(nombre: str):
    """
    Ejecuta un scraper de forma bloqueante y muestra logs por consola.
    """
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
            [sys.executable, path],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())

        elapsed = time.time() - start
        if result.returncode == 0:
            print(f"✅ {archivo} finalizó correctamente en {elapsed:.2f} s.")
        else:
            print(
                f"❌ {archivo} falló con código {result.returncode} "
                f"en {elapsed:.2f} s."
            )
    except Exception as e:
        print(f"❌ Error ejecutando {archivo}: {e}")


def scrap(nombres: List[str]):
    """
    Llama a múltiples scrapers de forma concurrente con límite de threads.

    Args:
        nombres (List[str]): Lista de nombres de scrapers a ejecutar.
            Posibles valores:
              "dolar", "plazo_fijo", "bono", "letras", "bandas".

    Ejemplo:
        scrap(["bono", "plazo_fijo"])
    """
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        futures = [
            executor.submit(run_scraper_blocking, name) for name in nombres
            ]
        for _ in as_completed(futures):
            pass