# main.py
from fastapi import FastAPI
from pydantic import BaseModel

# NOTA: Para iniciar el servidor se usa: `Uvicorn main:app --reload` y se cierra con `control + c`
app = FastAPI(title="Ejemplo CotizAR - Mini API") # Crea una app web que escucha peticiones HTTP
# Esto no arranca el servidor

@app.get("/") # Significa: cuando alguien hace una solicitud HTTP `GET` a la URL `/`, ejecuta la función que esta abajo.
async def hello_world():
    return {"hello": "world"}