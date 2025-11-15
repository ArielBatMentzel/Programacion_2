from utils.conexion_db import engine
from sqlalchemy import text


def obtener_plazos_fijos_por_usuario(usuario_username: str):
    """
    Devuelve todos los plazos fijos del usuario desde Supabase.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        id,
                        usuario_username,
                        banco,
                        monto_inicial,
                        tasa_pct,
                        monto_final_pesos,
                        dolar_actual,
                        dolar_equilibrio,
                        fecha_calculo
                    FROM instrumentos_usuarios.plazos_fijos_usuarios
                    WHERE usuario_username = :usuario_username
                    ORDER BY fecha_calculo DESC
                """),
                {"usuario_username": usuario_username}
            )

            rows = result.fetchall()
            return [dict(r._mapping) for r in rows]

    except Exception as e:
        print(f"[ERROR obtener_plazos_fijos_por_usuario] {e}")
        return []