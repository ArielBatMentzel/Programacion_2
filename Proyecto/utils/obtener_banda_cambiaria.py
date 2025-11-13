# utils/obtener_banda_cambiaria.py
from sqlalchemy import text, create_engine
from utils.conexion_db import crear_engine

engine = crear_engine()


def obtener_banda_cambiaria(mes: str = None):
    """
    Devuelve la banda inferior y superior para un mes desde Supabase.
    Si no se pasa mes, toma el último disponible.

    Args:
        mes (str, optional): Mes en formato 'yyyy-mm' (ej: '2025-11').
                             None para obtener el último mes.

    Returns:
        tuple[float, float] | tuple[None, None]:
        (banda_inferior, banda_superior)
    """
    with engine.connect() as conn:
        if mes:
            result = conn.execute(
                text("""
                    SELECT banda_inferior, banda_superior
                    FROM datos_financieros.bandas_cambiarias
                    WHERE fecha = :mes
                    ORDER BY id DESC
                    LIMIT 1
                """),
                {"mes": mes}
            )
        else:
            result = conn.execute(
                text("""
                    SELECT banda_inferior, banda_superior
                    FROM datos_financieros.bandas_cambiarias
                    ORDER BY id DESC
                    LIMIT 1
                """)
            )

        row = result.fetchone()

    if row:
        return float(row[0]), float(row[1])
    return None, None