from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def crear_engine() -> Engine:
    load_dotenv()
    try:
        DB_URL = os.getenv("DB_URL")
        if not DB_URL:
            raise ValueError("No se encontró la variable DB_URL en el entorno.")

        # 👇 Forzamos IPv4 si Supabase responde por IPv6
        if "supabase.co" in DB_URL and "options=" not in DB_URL:
            DB_URL += "?sslmode=require&options=-c%20inet_client_addr=127.0.0.1"

        engine = create_engine(DB_URL)

    except Exception as e:
        raise RuntimeError(f"Error al configurar la conexión a la base de datos: {e}")
    
    return engine