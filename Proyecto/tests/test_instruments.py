"""
Pruebas unitarias para las clases PlazoFijo y Bono.
Verifica el correcto cálculo de rendimientos, actualizaciones 
de valor del dólar y comparaciones con bandas cambiarias. 
También prueba la conversión de valores y el cálculo de 
rendimientos anuales y mensuales.
Se ejecuta haciendo: 
Desde Programacion_2
pytest Proyecto/tests/test_intruments.py -v 
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import date, timedelta
from unittest.mock import patch
import pytest
from models.instruments import PlazoFijo, Bono, _mes_banda_de_salida

# -------------------- Funciones auxiliares --------------------

def test_mes_banda_de_salida_varios_casos():
    """
    Verifica que _mes_banda_de_salida devuelva el mes final correcto
    según mes_inicio, fecha_inicio y cantidad de días.
    """
    # Caso con mes_inicio
    resultado = _mes_banda_de_salida("2025-11", None, 40)
    assert resultado.startswith("2025-12")

    # Caso con fecha_inicio
    resultado = _mes_banda_de_salida(None, date(2025, 11, 13), 20)
    assert resultado.startswith("2025-12")

    # Caso sin mes ni fecha
    resultado = _mes_banda_de_salida(None, None, 10)
    assert isinstance(resultado, str)

# -------------------- Plazo Fijo --------------------

def test_plazo_fijo_calcular_rendimiento():
    pf = PlazoFijo("Banco Test", tasa_tna=60, dias=30)
    resultado = pf.calcular_rendimiento(10000)

    assert all(k in resultado for k in ["tna", "tea", "monto_final_pesos", "ganancia_pesos"])
    assert resultado["monto_final_pesos"] > 10000
    assert resultado["ganancia_pesos"] > 0


def test_plazo_fijo_actualizar_valor_dolar():
    pf = PlazoFijo("Banco Test", tasa_tna=60)
    pf.actualizar(420)
    assert pf.valor_dolar == 420


def test_plazo_fijo_rendimiento_vs_banda():
    pf = PlazoFijo("Banco Test", tasa_tna=60, dias=30)
    with patch("models.instruments.obtener_banda_cambiaria", return_value=(300, 350)):
        pf.actualizar(valor_dolar=350)
        resultado = pf.rendimiento_vs_banda(10000)

    assert resultado is not None
    assert "monto_final_usd_techo" in resultado
    assert resultado["monto_final_usd_techo"] > 0
    assert "dolar_break_even" in resultado

# -------------------- Bono --------------------

@pytest.mark.parametrize("valor, esperado", [
    ("10%", 10.0),
    ("10,5", 10.5),
    (None, None),
    (123, 123.0),
    ("abc", None)
])


def test_bono_to_float(valor, esperado):
    """
    Verifica la conversión de diferentes valores a float en un bono.
    """
    bono = Bono("Bono Test", "ARS")
    assert bono._to_float(valor) == esperado


def test_bono_estimacion_rend_anual():
    bono = Bono("Bono Test", "ARS", dia_pct=0.1, mes_pct=3, anio_pct=10)
    r_anual = bono._estimacion_rend_anual()
    assert r_anual > 0


def test_bono_calcular_rendimiento_ars():
    bono = Bono("Bono Test", "ARS", dia_pct=0.1, mes_pct=3, anio_pct=10)
    with patch("models.instruments.obtener_dolar_oficial", return_value=350):
        resultado = bono.calcular_rendimiento(10000)

    assert "r_mensual_pct" in resultado
    assert "r_anual_pct" in resultado
    assert resultado["r_mensual_pct"] > 0
    assert resultado["r_anual_pct"] > 0
    assert "usd_invertidos" in resultado


def test_bono_calcular_rendimiento_usd():
    bono = Bono("Bono Test", "USD", dia_pct=0.1, mes_pct=3, anio_pct=10)
    resultado = bono.calcular_rendimiento(10000)
    assert "r_mensual_pct" in resultado
    assert "r_anual_pct" in resultado
    assert "usd_invertidos" not in resultado


def test_bono_rendimiento_vs_banda_normal():
    bono = Bono("Bono Test", "ARS", dia_pct=0.1, mes_pct=3, anio_pct=10)
    with patch("models.instruments.obtener_banda_cambiaria", return_value=(300, 350)), \
         patch("models.instruments.obtener_dolar_oficial", return_value=350):
        resultado = bono.rendimiento_vs_banda(10000)

    assert resultado is not None
    assert "monto_final_usd_techo" in resultado
    assert resultado["monto_final_usd_techo"] > 0


def test_bono_rendimiento_vs_banda_sin_banda():
    bono = Bono("Bono Test", "ARS", dia_pct=0.1, mes_pct=3, anio_pct=10)
    with patch("models.instruments.obtener_banda_cambiaria", return_value=(0, 0)), \
         patch("models.instruments.obtener_dolar_oficial", return_value=350):
        resultado = bono.rendimiento_vs_banda(10000)

    assert resultado is None