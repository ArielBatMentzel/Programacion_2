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

# GET /dolar/
@router.get("/")
async def mostrar_dolar_oficial_hoy():
    loop = asyncio.get_running_loop()
    try:
        valor = await loop.run_in_executor(None, obtener_ultimo_valor_dolar)
        return {"Dólar hoy": valor}
    except Exception as e:
        return {"error": str(e)}

# GET /dolar/cotizaciones
@router.get("/cotizaciones")
async def mostrar_cotizaciones():
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

# GET /dolar/exportar
@router.get("/exportar")
async def exportar_csv():

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
