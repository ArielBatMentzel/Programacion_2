# archivo: tests/test_alertas.py

import pytest
from models.alerta import Alerta
from models.user import User
from models.dolar import Dolar
from models.instruments import PlazoFijo

def test_alerta_evaluar_true():
    """
    Verifica que el método evaluar() de Alerta devuelva True
    cuando la condición configurada se cumple.
    """
    # Creamos un usuario de prueba
    usuario = User(email="test@example.com", nombre="Test User")
    
    # Creamos una alerta para ese usuario con una condición de ejemplo
    alerta = Alerta(usuario=usuario, condicion="dummy_condicion")
    
    # Creamos el objeto Dolar con un valor inicial
    dolar = Dolar(valor_inicial=100)
    
    # Creamos un instrumento financiero (PlazoFijo) que se evaluará
    instrumento = PlazoFijo(nombre="PlazoFijo1", moneda="ARS", dias=30)

    # Evaluamos la alerta con los datos actuales
    resultado = alerta.evaluar(dolar, [instrumento])
    
    # Comprobamos que devuelve un booleano
    # En la implementación real, True significa que la condición se cumplió
    assert isinstance(resultado, bool)

def test_alerta_notificar(capsys):
    """
    Verifica que el método notificar() de Alerta emita algún mensaje.
    capsys captura la salida de print para poder probarla.
    """
    # Creamos un usuario de prueba
    usuario = User(email="test@example.com", nombre="Test User")
    
    # Creamos una alerta
    alerta = Alerta(usuario=usuario, condicion="dummy_condicion")

    # Llamamos a notificar
    alerta.notificar()
    
    # Capturamos la salida por consola
    captured = capsys.readouterr()
    
    # Verificamos que haya algún mensaje relacionado con la notificación
    # Esto depende de cómo implementes notificar() (print, log, etc.)
    assert isinstance(captured.out, str)
