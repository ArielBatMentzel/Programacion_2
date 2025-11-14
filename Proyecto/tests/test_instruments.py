# archivo: tests/test_instruments.py

import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.instruments import PlazoFijo, Bono#, Pase, Letra,
from models.dolar import Dolar

@pytest.fixture
def dolar():
    """
    Fixture que crea un objeto Dolar para simular cambios de valor.
    """
    return Dolar(valor_inicial=100)

def test_calculate_plazofijo():
    """
    Verifica que el método calculate de PlazoFijo retorne un número (placeholder por ahora).
    """
    pf = PlazoFijo(nombre="PF1", moneda="ARS", dias=30)
    resultado = pf.calculate()
    # Por ahora solo comprobamos que sea un número (la lógica de cálculo se implementará después)
    assert isinstance(resultado, (int, float))

def test_actualizar_plazofijo(dolar):
    """
    Verifica que actualizar() de PlazoFijo se pueda llamar con un valor de dólar.
    """
    pf = PlazoFijo(nombre="PF1", moneda="ARS", dias=30)
    pf.actualizar(dolar.valor_actual)
    # No esperamos retorno, solo que no lance error

def test_calculate_letra():
    """
    Verifica que calculate() de Letra retorne un número.
    """
    letra = Letra(nombre="Letra1", moneda="ARS", precio_actual=100.0, dias_al_vencimiento=60, emisor="Gobierno")
    resultado = letra.calculate()
    assert isinstance(resultado, (int, float))

def test_actualizar_letra(dolar):
    """
    Verifica que actualizar() de Letra funcione con el valor del dólar.
    """
    letra = Letra(nombre="Letra1", moneda="ARS", precio_actual=100.0, dias_al_vencimiento=60, emisor="Gobierno")
    letra.actualizar(dolar.valor_actual)

def test_calculate_bono():
    bono = Bono(nombre="Bono1", moneda="ARS", cupon=5.0, valor_nominal=1000.0, frecuencia_pago=6, emisor="Gobierno")
    resultado = bono.calculate()
    assert isinstance(resultado, (int, float))

def test_actualizar_bono(dolar):
    bono = Bono(nombre="Bono1", moneda="ARS", cupon=5.0, valor_nominal=1000.0, frecuencia_pago=6, emisor="Gobierno")
    bono.actualizar(dolar.valor_actual)

def test_calculate_pase():
    pase = Pase(nombre="Pase1", moneda="ARS", plazo_dias=7, tipo_pase="interbancario")
    resultado = pase.calculate()
    assert isinstance(resultado, (int, float))

def test_actualizar_pase(dolar):
    pase = Pase(nombre="Pase1", moneda="ARS", plazo_dias=7, tipo_pase="interbancario")
    pase.actualizar(dolar.valor_actual)
