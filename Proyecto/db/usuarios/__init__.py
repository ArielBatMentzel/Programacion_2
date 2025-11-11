import sqlite3
from pathlib import Path

RUTA_DB = Path(__file__).resolve().parent.parent / "usuarios" / "usuarios.db"

with sqlite3.connect(RUTA_DB) as conn:
    cursor = conn.cursor()

    # Crear tablas si no existen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            hashed_password TEXT,
            full_name TEXT,
            tipo TEXT,
            email TEXT UNIQUE,
            telefono INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            token TEXT PRIMARY KEY,
            usuario_id INTEGER,
            fecha_inicio TEXT,
            fecha_expiracion TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()