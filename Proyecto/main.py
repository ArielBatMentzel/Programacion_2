# main.py
from fastapi import FastAPI
import os
from auth.auth_api import router as auth_router
from utils.obtener_ultimo_valor_dolar import obtener_ultimo_valor_dolar
import sqlite3
import pandas as pd
from fastapi.responses import StreamingResponse
from io import StringIO
import asyncio

"""
API CotizAR

Proporciona endpoints para cotizaciones financieras y exportación a CSV.

Instrucciones:
1. Iniciar servidor: `uvicorn main:cotizar --reload`
2. Cerrar con Ctrl+C
3. Ejecutar desde carpeta Proyecto y entorno activo.

Endpoints:
- / → mensaje de inicio
- /dolar → valor actual del dólar
- /cotizaciones → cotizaciones en JSON
- /exportar_dolar → descarga CSV
- /docs → documentación interactiva
"""

cotizar = FastAPI(title="CotizAR API")
cotizar.include_router(auth_router)

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "db",
    "datos_financieros",
    "datos_financieros.db"
)


#######################################################################
@cotizar.get(
    "/",
    summary="Inicio de la API",
    description="Verifica que la API esté funcionando correctamente."
)
async def inicio():
    """Retorna un mensaje indicando que la API está operativa."""
    return {"mensaje": "API CotizAR funcionando correctamente"}


#######################################################################
@cotizar.get("/dolar")
async def mostrar_dolar_hoy():
    """
    Obtiene el último valor del dólar 'DÓLAR BLUE'.

    Returns:
        dict: {"Dólar hoy": valor} o {"error": mensaje}.
    """
    loop = asyncio.get_running_loop()
    try:
        valor = await loop.run_in_executor(
            None, obtener_ultimo_valor_dolar
        )
        return {"Dólar hoy": valor}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}


#######################################################################
def obtener_datos():
    """
    Recupera todos los registros de la tabla 'dolar' como diccionarios.

    Returns:
        List[dict]: Lista de filas de la tabla.
    """
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM dolar")
    datos = cursor.fetchall()
    conexion.close()
    return [dict(fila) for fila in datos]


#######################################################################
@cotizar.get(
    "/cotizaciones",
    summary="Mostrar cotizaciones",
    description="Devuelve todas las cotizaciones de la tabla 'dolar' en JSON."
)
async def mostrar_cotizaciones():
    """Retorna todas las cotizaciones en formato JSON."""
    loop = asyncio.get_running_loop()
    try:
        data = await loop.run_in_executor(None, obtener_datos)
        return {"cotizaciones": data}
    except Exception as e:
        return {"error": str(e)}


#######################################################################
@cotizar.get(
    "/exportar_dolar",
    summary="Exportar cotizaciones a CSV",
    description="Exporta cotizaciones a un archivo CSV descargable."
)
async def exportar_csv():
    """
    Consulta la tabla 'dolar' y devuelve un CSV en StreamingResponse.

    Returns:
        StreamingResponse: CSV con todas las cotizaciones.
    """
    loop = asyncio.get_running_loop()

    def exportar():
        """Genera el CSV en memoria desde la DB."""
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
            "Content-Disposition":
            "attachment; filename=cotizaciones.csv"
        }
    )
