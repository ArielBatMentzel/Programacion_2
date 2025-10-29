import os
import importlib
import concurrent.futures

def run_scraper(module_name: str):
    """Ejecuta un módulo scrap_*.py que tenga main()."""
    try:
        modulo = importlib.import_module(module_name)
        if hasattr(modulo, "main"):
            print(f"▶ Ejecutando {module_name} ...")
            modulo.main()
            print(f"✅ Finalizado: {module_name}")
        else:
            print(f"⚠ {module_name} no tiene función main().")
    except Exception as e:
        print(f"❌ Error en {module_name}: {e}")

def run_scrapers(*targets):
    """
    Ejecuta uno o varios scrapers:
      - Sin argumentos → ejecuta todos los archivos scrap_*.py
      - Con nombres → ejecuta los indicados (sin 'scrap_' ni '.py')
        Ejemplo: run_scrapers("dolar", "bono")
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    archivos = [f[:-3] for f in os.listdir(base_path) if f.startswith("scrap_") and f.endswith(".py")]

    if not targets:
        seleccionados = archivos
    else:
        seleccionados = [f"scrap_{t}" for t in targets if f"scrap_{t}.py" in os.listdir(base_path)]

    if not seleccionados:
        print("⚠ No se encontraron módulos para ejecutar.")
        return

    # Ejecutar en paralelo
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_scraper, seleccionados)

if __name__ == "__main__":
    # Ejemplo: todos
    run_scrapers()
    # Ejemplo: solo algunos
    # run_scrapers("dolar", "bono")
