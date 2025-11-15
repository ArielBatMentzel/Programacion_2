"""
Script para crear la base "datos_financieros" localmente.
"""

import sqlite3
import os
from pathlib import Path


RUTA_DB = Path(__file__).resolve().parent.parent / "datos_financieros" / "datos_financieros.db"

# Crear carpeta si no existe
os.makedirs(os.path.dirname(RUTA_DB), exist_ok=True)

conn = sqlite3.connect(RUTA_DB) # Crear la base vacía
conn.close()

print("Base de datos creada vacía:", RUTA_DB)