# main.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from jose import jwt, JWTError
from passlib.context import CryptContext

from fastapi import HTTPException
from pydantic import BaseModel
import os
from auth.auth_api import router as auth_router
from utils.obtener_ultimo_valor_dolar import obtener_ultimo_valor_dolar
from pathlib import Path
import sqlite3
import pandas as pd
from fastapi.responses import StreamingResponse
from io import StringIO
import asyncio

"""
NOTA: Para iniciar el servidor se usa: `uvicorn main:cotizar --reload` 
y se cierra con `Control + C`.
Asegurarse de haber iniciado el entorno y haber hecho: cd Proyecto


Endpoints principales:

USAR ESTE
http://127.0.0.1:8000/docs → documentación interactiva



http://127.0.0.1:8000/ → mensaje de inicio
http://127.0.0.1:8000/dolar → dólar
http://127.0.0.1:8000/cotizaciones → tabla de base de datos
http://127.0.0.1:8000/exportar → descarga CSV
"""

# 🔹 Creamos una sola instancia de FastAPI
cotizar = FastAPI(title="CotizAR API")

# 🔹 Registrar router de autenticación
cotizar.include_router(auth_router)

# 🔹 Ruta al archivo de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "datos_financieros", "datos_financieros.db")
#######################################################################################################################################
# 🔹 Endpoint principal
@cotizar.get(
    "/", 
    summary="Inicio de la API", 
    description="Mensaje de bienvenida para verificar que la API está funcionando correctamente."
)
async def inicio():
    return {"mensaje": "API CotizAR funcionando correctamente"}

#######################################################################################################################################
@cotizar.get("/dolar")
async def mostrar_dolar_hoy():
    loop = asyncio.get_running_loop()
    try:
        valor = await loop.run_in_executor(None, obtener_ultimo_valor_dolar)
        return {"Dólar hoy": valor}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}


#######################################################################################################################################
# 🔹 Función para obtener los datos de la base de datos
def obtener_datos():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row  # Permite devolver resultados como diccionarios
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM dolar")  # Cambiar por el nombre de tu tabla
    datos = cursor.fetchall()
    conexion.close()
    return [dict(fila) for fila in datos]

# 🔹 Endpoint para mostrar los datos de la base
@cotizar.get(
    "/cotizaciones",
    summary="Mostrar cotizaciones",
    description="Devuelve todas las cotizaciones de la tabla 'dolar' de la base de datos en formato JSON."
)
async def mostrar_cotizaciones():
    loop = asyncio.get_running_loop()
    try:
        data = await loop.run_in_executor(None, obtener_datos)
        return {"cotizaciones": data}
    except Exception as e:
        return {"error": str(e)}

#######################################################################################################################################
# 🔹 Endpoint para exportar la tabla como CSV
@cotizar.get(
    "/exportar_dolar",
    summary="Exportar cotizaciones de dolar a CSV",
    description="Exporta todas las cotizaciones de la base de datos en un archivo CSV descargable."
)
async def exportar_csv():
    loop = asyncio.get_running_loop()

    def exportar():
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM dolar", conn)
        conn.close()
        stream = StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        return stream

    stream = await loop.run_in_executor(None, exportar)
    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cotizaciones.csv"}
    )
