from utils.scrap_runner import scrap
'''

Scrapeamos a la database usando este metodo directamente

    "dolar": "scrap_dolar.py",
    "plazo_fijo": "scrap_plazos_fijos.py",
    "bono": "scrap_bono.py",
    "letras": "scrap_letras.py",
    "bandas": "scrap_bandas_cambiarias.py"
'''
scrap(["dolar", "bono", 'plazo_fijo', 'letras', 'bandas'])