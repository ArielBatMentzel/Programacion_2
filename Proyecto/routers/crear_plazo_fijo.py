from models.instruments import PlazoFijo
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import crear_engine
from sqlalchemy import text
from fastapi import FastAPI, HTTPException

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")






# Instancia principal de FastAPI
cotizar = FastAPI(title="CotizAR API")

engine = crear_engine()

class PlazoFijoInput(BaseModel):
    usuario_id: str
    banco: str
    monto_inicial: float


@cotizar.get("/dashboard", response_class=HTMLResponse)
async def mostrar_dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )





@cotizar.get("/instrumentos/plazos-fijos/bancos")
def obtener_bancos():
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT banco, tasa_pct FROM datos_financieros.plazos_fijos")
            )
            bancos = [dict(row) for row in result.fetchall()]
        return bancos
    except Exception as e:
        # loguealo si querés; por ahora devolvemos 500
        raise HTTPException(status_code=500, detail=f"Error obteniendo bancos: {e}")



@cotizar.post("/instrumentos/plazos-fijos/crear")
def crear_plazo_fijo(data: PlazoFijoInput):
    # 1) Obtener la tasa del banco desde la tabla de datos_financieros
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT tasa_pct
                    FROM datos_financieros.plazos_fijos
                    WHERE banco = :b
                """),
                {"b": data.banco}
            ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"No existe el banco '{data.banco}'")
        tasa_tna = row["tasa_pct"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando tasa: {e}")

    # 2) Crear objeto PlazoFijo con la tasa y (opcional) días
    dias = data.dias if data.dias and data.dias > 0 else 30
    pf = PlazoFijo(banco=data.banco, tasa_tna=tasa_tna, dias=dias)

    # 3) Calcular rendimiento usando tu método real
    try:
        resultado = pf.calcular_rendimiento(data.monto_inicial)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando rendimiento: {e}")

    # 4) Guardar el registro en instrumentos_usuarios.plazos_fijos_usuarios
    try:
        with engine.begin() as conn:  # begin() hace commit/rollback automáticamente
            conn.execute(
                text("""
                    INSERT INTO instrumentos_usuarios.plazos_fijos_usuarios
                    (usuario_id, nombre, banco, tasa_pct, monto_inicial,
                     monto_final_pesos, ganancia_pesos, fecha_calculo)
                    VALUES (:usuario_id, :nombre, :banco, :tasa_pct, :monto,
                            :monto_final, :ganancia, NOW())
                """),
                {
                    "usuario_id": data.usuario_id,
                    "nombre": f"Plazo Fijo {data.banco} {dias}d",
                    "banco": data.banco,
                    "tasa_pct": tasa_tna,
                    "monto": data.monto_inicial,
                    "monto_final": resultado["monto_final_pesos"],
                    "ganancia": resultado["ganancia_pesos"]
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando en la DB: {e}")

    # 5) Devolver el resultado completo del cálculo (útil para el frontend)
    return {
        "tna": resultado.get("tna"),
        "tea": resultado.get("tea"),
        "monto_final_pesos": resultado.get("monto_final_pesos"),
        "ganancia_pesos": resultado.get("ganancia_pesos"),
        "banco": data.banco,
        "monto_inicial": data.monto_inicial,
        "dias": dias
    }


























# @cotizar.post("/instrumentos/plazos-fijos/crear")
# def crear_plazo_fijo(data: PlazoFijoInput):

#     usuario_id = data.usuario_id

#     # 1) Obtener tasa desde Supabase
#     result = conn.execute(
#         text("""
#             SELECT tasa_pct 
#             FROM datos_financieros.plazos_fijos 
#             WHERE banco = :b
#         """), {"b": data.banco}
#     ).fetchone()

#     if not result:
#         raise HTTPException(404, "Banco no encontrado")

#     tasa_tna = result.tasa_pct

#     # 2) Crear objeto real
#     pf = PlazoFijo(banco=data.banco, tasa_tna=tasa_tna)

#     # 3) Calcular
#     resultado = pf.calcular_rendimiento(data.monto_inicial)

#     # 4) Guardar
#     conn.execute(
#         text("""
#             INSERT INTO instrumentos_usuarios.plazos_fijos_usuarios
#             (usuario_id, banco, tasa_pct, monto_inicial, monto_final, ganancia)
#             VALUES (:u, :b, :t, :m, :f, :g)
#         """),
#         {
#             "u": usuario_id,
#             "b": data.banco,
#             "t": tasa_tna,
#             "m": data.monto_inicial,
#             "f": resultado["monto_final_pesos"],
#             "g": resultado["ganancia_pesos"]
#         }
#     )
#     conn.commit()

#     return resultado
