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
from prueba import obtener_ultimo_valor_dolar
from pathlib import Path
import sqlite3
import pandas as pd
from fastapi.responses import StreamingResponse
from io import StringIO


cotizar = FastAPI(title="CotizAR API - Autenticación")

# Registrar router de autenticación
cotizar.include_router(auth_router)

@cotizar.get("/")
def inicio():
    return {"mensaje": "API CotizAR funcionando correctamente"}



"""    
Poner los endpoints en los archivos correctos 
(hay que armar esa carpeta API y crear los archivos para cada endpoint ahí adentro)
Seguir mas o menos como estan en el docs de API CotizAR
"""

"""


# NOTA: Para iniciar el servidor se usa: `Uvicorn main:app --reload` y se cierra con `control + c`
cotizar = FastAPI(title="Ejemplo CotizAR - Mini API") # Crea una app web que escucha peticiones HTTP
# Esto no arranca el servidor

@cotizar.get("/") # Significa: cuando alguien hace una solicitud HTTP `GET` a la URL `/`, ejecuta la función que esta abajo.
async def hello_world():
    return {"hello": "world"}






# Endpoint, obtener precio del dólar actual
# Agregar que cuando 
@cotizar.get("/dolar") 
async def mostrar_dolar_hoy():
    valor = obtener_ultimo_valor_dolar()
    return  {
        "Dólar hoy": valor
    }
    


cotizar = FastAPI(title="Ejemplo API con Base de Datos")

# Ruta al archivo de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "datos_financieros", "datos_financieros.db")


# 🔹 Función para obtener los datos de la base de datos
def obtener_datos():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row  # Permite devolver resultados como diccionarios
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM dolar")  # Cambiá por el nombre de tu tabla
    datos = cursor.fetchall()

    conexion.close()

    # Convertir cada fila en un diccionario
    return [dict(fila) for fila in datos]


# 🔹 Endpoint para mostrar los datos
@cotizar.get("/cotizaciones")
async def mostrar_cotizaciones():
    try:
        data = obtener_datos()
        return {"cotizaciones": data}
    except Exception as e:
        return {"error": str(e)}









cotizar = FastAPI()
# Endpoint para guardar como CSV la tabla
@cotizar.get("/exportar")
def exportar_csv():
    # Conectamos a la base
    conn = sqlite3.connect(DB_PATH)
    
    # Elegí la tabla que quieras exportar
    df = pd.read_sql_query("SELECT * FROM dolar", conn)
    conn.close()
    
    # Convertimos el DataFrame a CSV en memoria
    stream = StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)
    
    # Enviamos como archivo descargable
    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usuarios.csv"}
    )



"""