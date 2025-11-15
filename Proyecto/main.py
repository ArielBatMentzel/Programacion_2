"""
Este archivo inicializa la API CotizAR usando FastAPI.

Configura los routers para:
- autenticación
- plazos fijos
- bonos
- dólar

La API expone servicios para cotizaciones financieras.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI
from auth.auth_api import router as auth_router
from routers.crear_plazo_fijo import router as plazo_fijo_router
from routers.crear_bono import router as bonos_router
from routers.dolar import router as dolar_router

"""
API CotizAR
-----------

Para iniciar el servidor localmente:
    uvicorn main:cotizar 

http://127.0.0.1:8000/docs
"""

cotizar = FastAPI(title="CotizAR API")

# Routers
cotizar.include_router(auth_router)
cotizar.include_router(plazo_fijo_router)
cotizar.include_router(bonos_router)
cotizar.include_router(dolar_router)


@cotizar.get("/")
async def inicio():
    return {"mensaje": "API CotizAR funcionando correctamente"}
