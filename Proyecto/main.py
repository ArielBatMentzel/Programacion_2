# main.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI
from auth.auth_api import router as auth_router
from routers.crear_plazo_fijo import router as plazo_fijo_router
from routers.crear_bono import router as bonos_router
from utils.obtener_ultimo_valor_dolar import obtener_ultimo_valor_dolar
from fastapi.responses import StreamingResponse
from io import StringIO
import pandas as pd
import asyncio

"""
API CotizAR
-----------

Para iniciar el servidor:
    uvicorn main:cotizar --reload

http://127.0.0.1:8000/docs

Endpoints principales:
    /           → mensaje de inicio
    /dolar      → último valor del dólar
    /cotizaciones → tabla completa de la base de datos
    /exportar_dolar → descarga CSV
    /docs      → documentación interactiva
"""

# Instancia principal de FastAPI
cotizar = FastAPI(title="CotizAR API")

cotizar.include_router(auth_router) # Registrar router de autenticación
cotizar.include_router(plazo_fijo_router) # Registrar router de Plazos Fijos
cotizar.include_router(bonos_router) # Registrar router de bonos

#######################################################################
# Endpoint raíz
@cotizar.get(
    "/",
    summary="Inicio de la API",
    description="Mensaje de bienvenida para verificar que"
    " la API está funcionando correctamente.",
)
async def inicio():
    return {"mensaje": "API CotizAR funcionando correctamente"}


#######################################################################
# Endpoint para obtener el último valor del dólar
@cotizar.get("/dolar")
async def mostrar_dolar_oficial_hoy():
    loop = asyncio.get_running_loop()
    try:
        valor = await loop.run_in_executor(None, obtener_ultimo_valor_dolar)
        return {"Dólar hoy": valor}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}


#######################################################################
# Función auxiliar para obtener datos de la base
def obtener_datos():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM datos_financieros.dolar"))
            return [dict(row._mapping) for row in result]
    except SQLAlchemyError as e:
        raise Exception(f"Error al obtener datos del dolar: {e}")

# Endpoint para mostrar todas las cotizaciones
@cotizar.get(
    "/cotizaciones",
    summary="Mostrar cotizaciones",
    description="Devuelve todas las cotizaciones"
    " de la tabla 'dolar' en formato JSON.",
)
async def mostrar_cotizaciones():
    loop = asyncio.get_running_loop()
    try:
        data = await loop.run_in_executor(None, obtener_datos)
        return {"cotizaciones": data}
    except Exception as e:
        return {"error": str(e)}


#######################################################################
# Endpoint para exportar la tabla del dolar como CSV
@cotizar.get(
    "/exportar_dolar",
    summary="Exportar cotizaciones de dolar a CSV",
    description="Exporta todas las cotizaciones de "
    "la base de datos en un archivo CSV descargable.",
)
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
        headers={
            "Content-Disposition": "attachment; filename=cotizaciones.csv"
        },
    )
