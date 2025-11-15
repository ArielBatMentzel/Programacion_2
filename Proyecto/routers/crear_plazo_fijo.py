"""
Rutas para obtener información y calcular plazos fijos, incluyendo 
tasas, rendimientos y comparación con el dólar actual.
También permite crear registros de plazos fijos para los usuarios.
"""

from models.instruments import PlazoFijo
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import engine
from utils.obtener_ultimo_valor_dolar import obtener_dolar_oficial
from sqlalchemy import text
from fastapi import APIRouter, HTTPException

# Inicialización de Variables
router = APIRouter(prefix="/plazo fijo", tags=["Plazos Fijos"])

# Modelo para trabajar con los datos
class PlazoFijoInput(BaseModel):
    usuario_username: str
    banco: str
    monto_inicial: float
    dias: int | None = None


# -------------------------------
# Endpoints (métodos que manejan solicitudes HTTP)
# -------------------------------


@router.get("/instrumentos/plazos-fijos/bancos")
def obtener_bancos():
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT banco, tasa_pct FROM datos_financieros.plazos_fijos")
            )
            bancos = [dict(row._mapping) for row in result]
        return bancos
    except Exception as e:
        # loguealo si querés; por ahora devolvemos 500
        raise HTTPException(status_code=500, detail=f"Error obteniendo bancos: {e}")


@router.post("/instrumentos/plazos-fijos/crear")
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
        tasa_tna = row[0]
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
    
    dolar_actual = obtener_dolar_oficial()
    if dolar_actual:
        dolar_equilibrio = round(
            (resultado["monto_final_pesos"] * dolar_actual) / data.monto_inicial,
            2
        )
        
    # 4) Guardar el registro en instrumentos_usuarios.plazos_fijos_usuarios
    try:
        with engine.begin() as conn:  # begin() hace commit/rollback automáticamente
            conn.execute(
                text("""
                    INSERT INTO instrumentos_usuarios.plazos_fijos_usuarios
                    (usuario_username, banco, monto_inicial, tasa_pct,
                    monto_final_pesos, dolar_actual, dolar_equilibrio, fecha_calculo)
                    VALUES (:usuario_username, :banco, :monto_inicial, :tasa_pct, :monto_final_pesos,
                            :dolar_actual, :dolar_equilibrio, NOW())
                """),
                {
                    "usuario_username": data.usuario_username,
                    "banco": data.banco,
                    "monto_inicial": data.monto_inicial,
                    "tasa_pct": tasa_tna,
                    "monto_final_pesos": resultado["monto_final_pesos"],
                    "dolar_actual": dolar_actual,
                    "dolar_equilibrio": dolar_equilibrio
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando en la DB: {e}")

    # 5) Devolver el resultado completo del cálculo (útil para el frontend)
    return {
        "banco": data.banco,
        "tna": resultado.get("tna"),
        "tea": resultado.get("tea"),
        "dias": dias,
        "monto_inicial": data.monto_inicial,
        "monto_final_pesos": resultado.get("monto_final_pesos"),
        "ganancia_pesos": resultado.get("ganancia_pesos"),
        "dólar equilibrio": dolar_equilibrio
    }