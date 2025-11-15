"""
Rutas para obtener información sobre el valor del dólar, incluyendo:
- Dólar oficial actual.
- Cotizaciones históricas almacenadas en la base de datos.
- Exportación de cotizaciones históricas a un archivo CSV.
"""

from fastapi import APIRouter
from utils.obtener_ultimo_valor_dolar import obtener_ultimo_valor_dolar
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from utils.conexion_db import engine
import pandas as pd
import asyncio
from io import StringIO

router = APIRouter(prefix="/dolar", tags=["Dólar"])


# -------------------------------
# Endpoints 
# -------------------------------


@router.get("/")
async def mostrar_dolar_oficial_hoy():
    """
    Obtiene el valor del dólar oficial actual.
    """
    
    loop = asyncio.get_running_loop()
    try:
        valor = await loop.run_in_executor(None, obtener_ultimo_valor_dolar)
        return {"Dólar hoy": valor}
    except Exception as e:
        return {"error": str(e)}


@router.get("/cotizaciones")
async def mostrar_cotizaciones():
    """
    Obtiene todas las cotizaciones actuales de distintos 
    tipos de dólares almacenados en la base de datos y 
    los devuelve como diccionarios.
    """
    
    loop = asyncio.get_running_loop()
    def obtener_datos():
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM datos_financieros.dolar"))
                return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener datos del dolar: {e}")

    try:
        data = await loop.run_in_executor(None, obtener_datos)
        return {"cotizaciones": data}
    except Exception as e:
        return {"error": str(e)}


@router.get("/exportar")
async def exportar_csv():
    """
    Exporta las cotizaciones de distintos actuales de 
    distintos tipos de dólares desde la base de datos a
    un archivo CSV y lo devuelv para ser descargado.
    """

    loop = asyncio.get_running_loop()
    def exportar():
        try:
            with engine.connect() as conn:
                df = pd.read_sql("SELECT * FROM datos_financieros.dolar", conn)
            stream = StringIO()
            df.to_csv(stream, index=False)
            stream.seek(0)
            return stream
        except SQLAlchemyError as e:
            raise Exception(f"Error al exportar dolar como CSV: {e}")

    stream = await loop.run_in_executor(None, exportar)
    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cotizaciones.csv"},
    )
