# crear_admin.py

from utils.conexion_db import crear_engine
import bcrypt
from sqlalchemy import text
"""
Script seguro para crear un usuario administrador en Supabase.

Uso:
    python crear_admin.py
"""

# Configuración del admin
USERNAME_ADMIN = "admin"
PASSWORD_ADMIN = "admin123"
FULL_NAME_ADMIN = "Administrador"
TIPO_ADMIN = "admin"
EMAIL_ADMIN = "admin@admin.com"
TELEFONO_ADMIN = 0
ROL_ADMIN = "admin"

# Hashear la contraseña
password_bytes = PASSWORD_ADMIN.encode("utf-8")
hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

# Crear engine de conexión
engine = crear_engine()


# Insertar o reemplazar admin en la tabla usuarios
try:
    with engine.connect() as conn:
        query = text("""
            INSERT INTO usuarios.usuarios (username, hashed_password, full_name, tipo, email, telefono, rol)
            VALUES (:username, :hashed_password, :full_name, :tipo, :email, :telefono, :rol)
            ON CONFLICT (username) DO UPDATE 
            SET hashed_password = excluded.hashed_password,
                full_name = excluded.full_name,
                tipo = excluded.tipo,
                email = excluded.email,
                telefono = excluded.telefono,
                rol = excluded.rol
        """)
        conn.execute(query, {
            "username": USERNAME_ADMIN,
            "hashed_password": hashed_password,
            "full_name": FULL_NAME_ADMIN,
            "tipo": TIPO_ADMIN,
            "email": EMAIL_ADMIN,
            "telefono": TELEFONO_ADMIN,
            "rol": ROL_ADMIN
        })
        conn.commit()
    print(f"Usuario admin '{USERNAME_ADMIN}' creado o actualizado correctamente.")
except Exception as e:
    print(f"Error al crear admin: {e}")