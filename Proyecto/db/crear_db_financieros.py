import sqlite3
import os

db_path = "Proyecto/db/datos_financieros.db"

# Crear carpeta si no existe
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Crear la base vacía
conn = sqlite3.connect(db_path)
conn.close()

print("✅ Base de datos creada vacía:", db_path)
