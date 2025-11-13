# archivo: tests/test_auth.py

import pytest
from auth.auth_service import AuthService
from models.user import User

@pytest.fixture
def auth_service():
    """
    Fixture que crea un AuthService con un usuario de prueba.
    Se ejecuta antes de cada test que lo requiera.
    """
    service = AuthService()
    # Creamos un usuario de prueba y lo guardamos en la base
    user = User(email="test@example.com", nombre="Test User", tipo="normal")
    service.db.guardar_usuario(user)  # suponiendo que AuthService tiene atributo db: DataBaseUsuario
    return service

def test_login_valido(auth_service):
    """
    Verifica que el login con credenciales correctas genere un token válido.
    """
    token = auth_service.login(email="test@example.com", contraseña="dummy")
    
    # El token no debe ser None
    assert token is not None
    # El token debe ser un string
    assert isinstance(token, str)

def test_login_invalido(auth_service):
    """
    Verifica que el login con credenciales incorrectas devuelva None.
    """
    token = auth_service.login(email="noexiste@example.com", contraseña="dummy")
    assert token is None

def test_recuperar_contrasena(auth_service):
    """
    Verifica que la recuperación de contraseña se ejecute correctamente.
    Dependiendo de la implementación puede devolver True/False o simular envío de email.
    """
    resultado = auth_service.recuperar_contrasena(email="test@example.com")
    assert isinstance(resultado, bool)