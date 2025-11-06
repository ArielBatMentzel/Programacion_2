# archivo: Proyecto/utils/scrap_runner.py
import asyncio
import subprocess
from typing import List
import time
import os

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

MAX_CONCURRENCY = 3

async def run_scraper(nombre: str):
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
    
    proc = await asyncio.create_subprocess_exec(
        "python", path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await proc.communicate()
    
    if stdout:
        print(stdout.decode().strip())
    if stderr:
        print(stderr.decode().strip())
    
    elapsed = time.time() - start
    if proc.returncode == 0:
        print(f"✅ {archivo} finalizó correctamente en {elapsed:.2f} s.")
    else:
        print(f"❌ {archivo} falló con código {proc.returncode} en {elapsed:.2f} s.")


async def _scrap_limited(names: List[str]):
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def sem_task(name):
        async with semaphore:
            await run_scraper(name)
    
    await asyncio.gather(*(sem_task(name) for name in names))


def scrap(nombres: List[str]):
    """Ejemplo: scrap(["bono","plazo_fijo"])"""
    asyncio.run(_scrap_limited(nombres))