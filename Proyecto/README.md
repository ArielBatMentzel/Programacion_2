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
8. [Ejecución con docker (local)](#Ejecución-con-docker-(-local-))  
9. [Despliegue en Render](#Despliegue-en-Render)

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

## Ejecución con docker (local)
> Esta opción permite probar la API en un contenedor Docker local, sin depender de Render ni del entorno local de Python.
### 1. Descargar [Docker Desktop](https://www.docker.com/products/docker-desktop/), que incluye el motor Docker (para ejecutar `docker build` y `docker run`) y una interfaz para probar nuestras imagenes y contenedores.
### 2. Construir la imagen Docker:
Desde la carpeta `Proyecto/`
```bash
docker build -t cotizar-api:latest .
```
### 3. Ejecutar el contenedor:
```bash
docker run -p 8000:8000 cotizar-api:latest
```
- Acceder a la API en `http://localhost:8000`
### 4. Ejecutar en segundo plano (sin bloquear la terminal):
```bash
docker run -d -p 8000:8000 cotizar-api:latest
```
### 5. Detener contenedores:
```bash
docker stop <nombre_o_id_del_contenedor>
```
- O para detener todos los contenedores:
```bash
docker stop $(docker ps -q)
```

---

## Despliegue en Render
> Cómo desplegar la API en Render utilizando Docker.
Render ejecutará el contenedor de forma automática cada vez que se haga un nuevo push a GitHub (en `main`).
### 1. Subir el proyecto a Github
- Asegurarse de que el proyecto esté dentro de una carpeta llamada Proyecto
### 2. Crear un nuevo servicio web en Render
1. Entrar a [Render](https://render.com/) y crearse una cuenta.
2. Iniciar un nuevo proyecto **New Web Service**.
3. Conectar el proyecto con el repositorio de Github.
4. Durante la configuración:
- - En **Root Directory**, seleccionar la carpeta `Proyecto`
- - En **Language**, seleccionar `Docker` (no `python`).
- - Con esto, Render detecta el `Dockerfile` automáticamente.
- - En **Region**, elegir la más cercana
### 3. Variables de entorno
En la sección **Environment Variables**, agregar:
```bash
DB_URL=postgresql://usuario:contraseña@host:puerto/nombre_basedatos
```
Es la variable que apunta a la base de datos de Supabase
> Actualmente el modo gratuito de Supabase no incluye **IPv6**, por lo que hay que utilizar la variable de Session Pooler de Supabase (**IPv4**).
### 4. Deploy Automático
Render construirá la imagen Docker y desplegará el servicio. 
Cada vez que se haga un push al repositorio, Render volvera a hacer el Deploy.
Una vez desplegado, Render ofrecerá una URL para verificar el funcionamiento del Servicio Web.


## Notas
-Se recomienda usar Python 3.11 para compatibilidad con todas las librerías.

-Variables sensibles se manejan con `.env` localmente y `DB_URL` en Render.

-La API integra datos de Supabase (PostgreSQL), scraping web y notificaciones de alertas.