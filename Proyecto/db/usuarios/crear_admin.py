# crear_admin.py

import sqlite3
from pathlib import Path
import bcrypt

# Ir dos niveles arriba desde este archivo hasta la raíz del proyecto
RUTA_DB = Path(__file__).resolve().parent.parent / "usuarios" / "usuarios.db"
# admin123
password = "admin123".encode("utf-8")
hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

# Asegurar que el directorio exista
RUTA_DB.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(RUTA_DB) as conn:
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO usuarios (username, hashed_password, full_name, tipo, email, telefono, rol)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("admin", hashed, "Administrador", "admin", "admin@admin.com", 0, "admin"))
    conn.commit()
