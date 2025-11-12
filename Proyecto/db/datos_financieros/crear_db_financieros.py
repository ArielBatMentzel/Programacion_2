# ================================
# crear_db_financieros.py
# ================================

import sqlite3
import os

DB_PATH = "Proyecto/db/datos_financieros/datos_financieros.db"

# Crear carpeta si no existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Crear la base de datos vacía
conn = sqlite3.connect(DB_PATH)
conn.close()

print("✅ Base de datos creada vacía:", DB_PATH)
