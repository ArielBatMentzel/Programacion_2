# main.py
from fastapi import FastAPI
from auth.auth_api import router as auth_router
from utils.obtener_ultimo_valor_dolar import obtener_ultimo_valor_dolar
from fastapi.responses import StreamingResponse
from io import StringIO
import os
import sqlite3
import pandas as pd
import asyncio

"""
API CotizAR
-----------

Para iniciar el servidor:
    uvicorn main:cotizar --reload

Endpoints principales:
    /           → mensaje de inicio
    /dolar      → último valor del dólar
    /cotizaciones → tabla completa de la base de datos
    /exportar_dolar → descarga CSV
    /docs      → documentación interactiva
"""

# Instancia principal de FastAPI
cotizar = FastAPI(title="CotizAR API")

# Registrar router de autenticación
cotizar.include_router(auth_router)

# Ruta al archivo de base de datos
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "db",
    "datos_financieros",
    "datos_financieros.db",
)


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
async def mostrar_dolar_hoy():
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dolar")
    datos = cursor.fetchall()
    conn.close()
    return [dict(fila) for fila in datos]


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
# Endpoint para exportar la tabla como CSV
@cotizar.get(
    "/exportar_dolar",
    summary="Exportar cotizaciones de dolar a CSV",
    description="Exporta todas las cotizaciones de "
    "la base de datos en un archivo CSV descargable.",
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
        headers={
            "Content-Disposition": "attachment; filename=cotizaciones.csv"
            },
    )
