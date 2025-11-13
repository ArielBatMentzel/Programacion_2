# API Cotizar

Este proyecto es una API desarrollada en **FastAPI** para obtener y procesar información financiera: tipo de cambio, bonos, letras, alertas, usuarios y otros instrumentos de renta fija.  
Está diseñada para ejecutarse localmente con Python y también se puede desplegar en **Render** utilizando Docker.

---

## Contenido

1. [Requisitos](#requisitos)  
2. [Entorno Virtual](#entorno-virtual)  
3. [Instalación de Dependencias](#instalación-de-dependencias)  
4. [Estructura del Proyecto](#estructura-del-proyecto)  
5. [Librerías Utilizadas](#librerías-utilizadas)  
6. [Ejecución Local](#ejecución-local)  
7. [Pruebas Unitarias](#pruebas-unitarias)  
8. [Despliegue con Docker y Render](#despliegue-con-docker-y-render)  

---

## Requisitos

- Python 3.11 o 3.13  
- Docker (opcional, para despliegue en contenedor)  
- Git (para clonar el repositorio)  
- Supabase (base de datos PostgreSQL)  
- Variables de entorno:  
  - `.env` local para desarrollo  
  - `DB_URL` en Render (incluye usuario, contraseña y URL de la base de datos Supabase)

---

## Entorno Virtual
Para evitar conflictos de librerías, se recomienda crear y activar un entorno virtual:
### 0. Crear entorno virtual (solo la primera vez)
```bash
python -m venv venv
```
### 1. Activar entorno virtual
- **Windows:**
```bash
.\venv\Scripts\activate
```
- **Linux / MacOS:**
```bash
source venv/bin/activate
```
### 2. Desactivar entorno virtual (opcional)
```bash
deactivate
```

---

## Instalación de Dependencias
Instalar todas las librerías necesarias desde el archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```
Si se agregan nuevas librerías, actualizar `requirements.txt`:
```bash
pip freeze > requirements.txt
```

---

## Estructura del Proyecto
```text
Proyecto/
│
├── .dockerignore
├── .env
├── Dockerfile
├── main.py
├── README.md
├── requirements.txt
├── auth/
│   ├── auth_api.py
│   ├── auth_service.py
│   └── __init__.py
├── codigo_local/
│   ├── scrap_bandas_cambiarias_db_local.py
│   ├── scrap_bono_db_local.py
│   ├── scrap_dolar_db_local.py
│   ├── scrap_letras_db_local.py
│   ├── scrap_plazos_fijos_db_local.py
│   └── users_db_local.py
├── datasets/
│   ├── bandas_nov2025_dic2028.csv
│   ├── bonos_argentinos_vencimiento.csv
│   └── letras_argentinas_vencimiento.csv
├── db/
│   └── abstract_db.py
├── datos_financieros/
│   ├── crear_db_financieros_local.py
│   ├── datos_financieros.db
│   └── __init__.py
├── usuarios/
│   ├── crear_admin.py
│   ├── crear_db_usuarios_local.py
│   ├── users_db.py
│   └── usuarios.db
├── factory/
│   ├── fixed_income_factory.py
│   └── __init__.py
├── models/
│   ├── alerta.py
│   ├── dolar.py
│   ├── instruments.py
│   ├── user.py
│   └── __init__.py
├── source/
│   ├── scrap_all.py
│   ├── scrap_bandas_cambiarias.py
│   ├── scrap_bono.py
│   ├── scrap_dolar.py
│   ├── scrap_letras.py
│   └── scrap_plazos_fijos.py
├── tests/
│   ├── test_alertas.py
│   ├── test_auth.py
│   └── test_instruments.py
└── utils/
    ├── armar_estructura_txt.py
    ├── conexion_db.py
    ├── helpers.py
    ├── init_path.py
    ├── obtener_banda_cambiaria.py
    ├── obtener_ultimo_valor_dolar.py
    ├── scrapper.py
    └── __init__.py
```

---

## Librerías Utilizadas
Algunas librerías clave y su propósito:

| Librería | Versión | Uso principal |
|-----------|----------|-----------------------------|
| `fastapi` | 0.121.1 | Framework principal para crear la API |
| `uvicorn` | 0.23.1 | Servidor ASGI para ejecutar FastAPI |
| `SQLAlchemy` | 2.0.31 | ORM para interactuar con la base de datos |
| `psycopg2-binary` | 2.9.9 | Driver PostgreSQL para SQLAlchemy |
| `pydantic` | 2.7.0 | Validación y serialización de datos |
| `requests` | 2.32.3 | Consumo de APIs externas |
| `beautifulsoup4` | 4.12.3 | Web scraping de HTML |
| `selenium` | 4.38.0 | Automatización de navegador para scraping dinámico |
| `webdriver-manager` | 4.0.1 | Manejo automático de drivers para Selenium |
| `schedule` | 1.2.1 | Tareas programadas dentro de la API |
| `pandas` | 2.2.2 | Manejo de datos en tablas y CSV |
| `numpy` | 1.24.3 | Operaciones matemáticas y arrays |
| `matplotlib` | 3.9.2 | Visualización de datos |
| `python-dotenv` | 1.0.0 | Manejo de variables de entorno |
| `pytest` | 8.3.2 | Pruebas unitarias |
| `loguru` | 0.7.0 | Logging y registro de eventos |

> Nota: El archivo completo requirements.txt incluye todas las librerías necesarias para ejecutar la API.

---

## Ejecución Local
### 1. Pararse dentro de la carpeta Proyecto del repositorio
```bash
cd Proyecto
```
### 1. Activar el entorno virtual:
```bash
.\venv\Scripts\activate
```
### 2. Ejecutar la API con Uvicorn:
```bash
uvicorn main:cotizar --reload
```
- Acceder a la documentación interactiva: `http://127.0.0.1:8000/docs`
- Para detener el servidor apretar `ctrl + c` en la terminal.
---

## Pruebas Unitarias
Ejecutar todas las pruebas con `pytest`:
```bash
pytest tests/
```

---

## Despliegue con Docker y Render

-La aplicación se desplegó en Render utilizando Docker como lenguaje.  

-Se configuró el directorio raíz como `Proyecto`.  

-Render utiliza el Dockerfile incluido en el proyecto, por lo que no es necesario configurar build o start commands manualmente.  

-Variable de entorno `DB_URL` configurada en Render para conexión con Supabase (contiene usuario, contraseña y URL de la base de datos).  

### Ejecutar Docker localmente (opcional)
### 1. Descargamos Docker Desktop, que incluye el motor Docker (para ejecutar `docker build` y `docker run`) y una interfaz para probar nuestras imagenes y contenedores e manera local
[Docker Desktop](https://www.docker.com/products/docker-desktop/)
### 2. Construir la imagen Docker:
```bash
docker build -t cotizar-api:latest .
```
### 3. Ejecutar el contenedor:
```bash
docker run -p 8000:8000 cotizar-api:latest
```
- Acceder a la API en `http://localhost:8000`
### 4. Ejecutar en segundo plano (detached):
```bash
docker run -d -p 8000:8000 cotizar-api:latest
```
### 5. Detener contenedores:
```bash
docker stop <nombre_o_id_del_contenedor>
```
- Para detener todos los contenedores:
```bash
docker stop $(docker ps -q)
```

---

## Notas
-Se recomienda usar Python 3.11 para compatibilidad con todas las librerías.

-Variables sensibles se manejan con `.env` localmente y `DB_URL` en Render.

-La API integra datos de Supabase (PostgreSQL), scraping web y notificaciones de alertas.







