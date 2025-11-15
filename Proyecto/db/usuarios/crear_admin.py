"""
Script para crear un usuario administrador en Supabase.
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import crear_engine
import bcrypt
from sqlalchemy import text


# Configuración del admin
USERNAME_ADMIN = "admin"
PASSWORD_ADMIN = "admin123"
FULL_NAME_ADMIN = "Administrador"
TIPO_ADMIN = "admin"
EMAIL_ADMIN = "admin@admin.com"
TELEFONO_ADMIN = 0
ROL_ADMIN = "admin"

# Hasheamos la contraseña
password_bytes = PASSWORD_ADMIN.encode("utf-8")
hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

# Creamos el engine de conexión
engine = crear_engine()

# Insertamos o reemplazamos el admin en la tabla usuarios
try:
    with engine.connect() as conn:
        query = text("""
            INSERT INTO usuarios.usuarios (username, hashed_password, full_name, tipo, email, telefono)
            VALUES (:username, :hashed_password, :full_name, :tipo, :email, :telefono)
            ON CONFLICT (username) DO UPDATE 
            SET hashed_password = excluded.hashed_password,
                full_name = excluded.full_name,
                tipo = excluded.tipo,
                email = excluded.email,
                telefono = excluded.telefono
        """)
        conn.execute(query, {
            "username": USERNAME_ADMIN,
            "hashed_password": hashed_password,
            "full_name": FULL_NAME_ADMIN,
            "tipo": TIPO_ADMIN,
            "email": EMAIL_ADMIN,
            "telefono": TELEFONO_ADMIN
        })
        conn.commit()
    print(f"Usuario admin '{USERNAME_ADMIN}' creado o actualizado correctamente.")
except Exception as e:
    print(f"Error al crear admin: {e}")