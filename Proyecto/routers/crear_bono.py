# routers/bonos.py
from fastapi import APIRouter, Query
from datetime import date
from typing import List, Dict
from sqlalchemy import text
from models.instruments import Bono
from utils.obtener_bonos import obtener_bonos_desde_bd, obtener_tipo_cambio
from utils.obtener_banda_cambiaria import obtener_banda_cambiaria
from utils.conexion_db import engine  # usar el engine directamente

router = APIRouter(prefix="/bonos", tags=["Bonos"])

@router.get("/calcular", summary="Calcular rendimiento de bonos")
async def calcular_bonos(
    monto: float = Query(10000, description="Monto a invertir"),
    moneda_inversion: str = Query("ARS", description="Moneda de la inversión: 'ARS' o 'USD'"),
    usuario_username: str = Query(..., description="Usuario que realiza la inversión")
):
    bonos_data: List[Dict] = obtener_bonos_desde_bd()
    tipos_cambio = obtener_tipo_cambio()
    dolar_oficial = tipos_cambio.get("DÓLAR OFICIAL", None)

    resultados = []

    for data in bonos_data:
        bono = Bono(
            nombre=data.get("nombre"),
            moneda=data.get("moneda"),
            ultimo=data.get("ultimo") or 0,
            dia_pct=data.get("dia_pct") or 0,
            mes_pct=data.get("mes_pct") or 0,
            anio_pct=data.get("anio_pct") or 0,
        )

        fecha_venc = data.get("fecha_vencimiento")
        fecha_venc_dt = None
        if fecha_venc:
            try:
                fecha_venc_dt = date.fromisoformat(fecha_venc)
            except ValueError:
                fecha_venc_dt = None

        # Convertir monto según moneda de inversión
        monto_convertido = monto
        if bono.moneda == "ARS" and moneda_inversion.upper() == "USD" and dolar_oficial:
            monto_convertido = monto * dolar_oficial
        elif bono.moneda == "USD" and moneda_inversion.upper() == "ARS" and dolar_oficial:
            monto_convertido = monto / dolar_oficial

        # Actualizar valor de dólar del bono si aplica
        if bono.moneda == "ARS" and dolar_oficial:
            bono.actualizar(dolar_oficial)

        # Calcular rendimiento
        rendimiento = bono.calcular_rendimiento(
            monto_convertido,
            tipo_cambio_actual=dolar_oficial
        ) or {}

        # Calcular métricas vs banda cambiaria
        vs_banda = bono.rendimiento_vs_banda(
            monto_convertido,
            fecha_inicio=fecha_venc_dt,
            dias=30
        ) or {}

        # Insertar en DB
        with engine.begin() as conn:
            insert_stmt = text("""
                INSERT INTO instrumentos_usuarios.bonos_usuarios (
                    usuario_username, bono, moneda_bono, monto_inicial, moneda_inversion,
                    monto_convertido, r_mensual_pct, r_anual_pct,
                    monto_final_pesos, factor_ars, vs_banda_techo_usd,
                    dolar_actual, dolar_equilibrio,
                    dias_considerados, mes_banda_usado
                ) VALUES (
                    :usuario_username, :bono, :moneda_bono, :monto_inicial, :moneda_inversion,
                    :monto_convertido, :r_mensual_pct, :r_anual_pct,
                    :monto_final_pesos, :factor_ars, :vs_banda_techo_usd,
                    :dolar_actual, :dolar_equilibrio,
                    :dias_considerados, :mes_banda_usado
                )
            """)
            conn.execute(insert_stmt, {
                "usuario_username": usuario_username,
                "bono": bono.nombre,
                "moneda_bono": bono.moneda,
                "monto_inicial": monto,
                "moneda_inversion": moneda_inversion.upper(),
                "monto_convertido": round(monto_convertido, 6),
                "r_mensual_pct": round(rendimiento.get("mensual_pct", 0), 2),
                "r_anual_pct": round(rendimiento.get("anual_pct", 0), 2),
                "monto_final_pesos": round(vs_banda.get("monto_final_pesos", 0), 2),
                "factor_ars": round(vs_banda.get("factor_ars", 0), 6),
                "vs_banda_techo_usd": round(vs_banda.get("vs_techo_usd", 0), 6),
                "dolar_actual": round(dolar_oficial or 0, 2),
                "dolar_equilibrio": round(vs_banda.get("dolar_equilibrio", 0), 2),
                "dias_considerados": vs_banda.get("dias", 30),
                "mes_banda_usado": vs_banda.get("mes", "")
            })

        resultados.append({
            "bono": bono.nombre,
            "moneda": bono.moneda,
            "monto_inicial": monto,
            "moneda_inversion": moneda_inversion.upper(),
            "monto_convertido": round(monto_convertido, 2),
            "rendimiento": rendimiento,
            "vs_banda": vs_banda
        })

    return resultados













# # routers/bonos.py
# from fastapi import APIRouter, Query
# from datetime import date
# from typing import List, Dict
# from models.instruments import Bono
# from utils.obtener_bonos import obtener_bonos_desde_bd, obtener_tipo_cambio
# from utils.obtener_banda_cambiaria import obtener_banda_cambiaria

# router = APIRouter(prefix="/bonos", tags=["Bonos"])

# @router.get("/calcular", summary="Calcular rendimiento de bonos")
# async def calcular_bonos(
#     monto: float = Query(10000, description="Monto a invertir"),
#     moneda_inversion: str = Query("ARS", description="Moneda de la inversión: 'ARS' o 'USD'")
# ):
#     """
#     Calcula rendimientos de bonos considerando la moneda de inversión.
#     Convierte valores automáticamente usando el dólar oficial.
#     Selecciona la banda cambiaria correcta según la fecha de vencimiento del bono.
#     """
#     bonos_data: List[Dict] = obtener_bonos_desde_bd()
#     tipos_cambio = obtener_tipo_cambio()
#     dolar_oficial = tipos_cambio.get("DÓLAR OFICIAL", None)

#     resultados = []

#     for data in bonos_data:
#         bono = Bono(
#             nombre=data.get("nombre"),
#             moneda=data.get("moneda"),
#             ultimo=data.get("ultimo"),
#             dia_pct=data.get("dia_pct"),
#             mes_pct=data.get("mes_pct"),
#             anio_pct=data.get("anio_pct"),
#         )

#         fecha_venc = data.get("fecha_vencimiento")
#         fecha_venc_dt = date.fromisoformat(fecha_venc) if fecha_venc else None

#         # Convertir monto según moneda de inversión
#         monto_convertido = monto
#         if bono.moneda == "ARS" and moneda_inversion.upper() == "USD" and dolar_oficial:
#             monto_convertido = monto * dolar_oficial
#         elif bono.moneda == "USD" and moneda_inversion.upper() == "ARS" and dolar_oficial:
#             monto_convertido = monto / dolar_oficial

#         # Actualizar valor de dólar del bono si aplica
#         if bono.moneda == "ARS" and dolar_oficial:
#             bono.actualizar(dolar_oficial)

#         # Calcular rendimiento
#         rendimiento = bono.calcular_rendimiento(
#             monto_convertido,
#             tipo_cambio_actual=dolar_oficial
#         )

#         # Calcular métricas vs banda cambiaria usando la fecha de vencimiento
#         vs_banda = bono.rendimiento_vs_banda(
#             monto_convertido,
#             fecha_inicio=fecha_venc_dt,
#             dias=30
#         )

#         resultados.append({
#             "bono": bono.nombre,
#             "moneda": bono.moneda,
#             "monto_inicial": monto,
#             "moneda_inversion": moneda_inversion.upper(),
#             "monto_convertido": round(monto_convertido, 2),
#             "rendimiento": rendimiento,
#             "vs_banda": vs_banda
#         })

#     return resultados



