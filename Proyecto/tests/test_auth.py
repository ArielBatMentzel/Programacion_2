"""
Pruebas automatizadas para el flujo de autenticación de usuarios: 
registro, 
inicio de sesión, 
obtención del usuario actual ,
cierre de sesión.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from auth.auth_api import router as auth_router
from fastapi import FastAPI

# Creamos una app temporal solo para test
app = FastAPI()
app.include_router(auth_router)

client = TestClient(app)


def test_registrar_y_login_usuario():
    # Registrar
    response = client.post("/auth/registrar", json={
        "nombre_usuario": "testuser",
        "contraseña": "123456",
        "nombre_completo": "Test User",
        "email": "test@test.com",
        "telefono": "0"
    })
    assert response.status_code in (201, 400)  # 400 si ya existe

    # Login
    response = client.post("/auth/iniciar_sesion", data={
        "username": "testuser",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_usuario_actual():
    # Primero login para obtener token
    response = client.post("/auth/iniciar_sesion", data={
        "username": "testuser",
        "password": "123456"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Consultar usuario actual
    response = client.get(
        "/auth/usuario_actual",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre_usuario"] == "testuser"
    assert "tipo" in data


def test_cerrar_sesion():
    # Login para obtener token
    response = client.post("/auth/iniciar_sesion", data={
        "username": "testuser",
        "password": "123456"
    })
    token = response.json()["access_token"]

    # Cerrar sesión
    response = client.post(
        "/auth/cerrar_sesion",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "mensaje" in response.json()

