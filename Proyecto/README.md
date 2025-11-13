=======================================================     
GUÍA PARA CREAR, ACTIVAR Y ACTUALIZAR EL ENTORNO VIRTUAL 

Cada integrante debe seguir estos pasos una sola vez al inicio 
del proyecto y luego cuando se agreguen librerías nuevas. 



## 0.(Solo la primera vez) Crear el entorno virtual: 
python -m venv venv 

## 1. Activar el entorno virtual (cada vez que se trabaje en el proyecto): 
.\venv\Scripts\activate 

## 2. Instalar las librerías desde requirements.txt: 
pip install -r requirements.txt

## 3. Actualizar requirements.txt cuando se instalen nuevas librerías: 
pip freeze > requirements.txt 

## 4. Desactivar el entorno virtual (opcional): 
deactivate 


## Exepciones: En el paso 2 Valen debe ejecutar: 
pip install -r C:\Users\casti\Documents\GitHub\Proyectos_programacion2\Programacion_2\Proyecto\requirements.txt.txt






======================================================= 
LIBRERÍAS UTILIZADAS
======================================================= 

requests==2.32.3          # Para acceder a APIs o páginas web  
beautifulsoup4==4.12.3    # Para procesar HTML (scraping)  
pandas==2.2.2             # Para manejar tablas y CSVs  
selenium==4.21.0          # Para automatizar navegadores  
webdriver-manager==4.0.1  # Para gestionar drivers (Chrome, Edge, etc.)  
schedule==1.2.1           # Para tareas automáticas  
matplotlib==3.9.2
numpy==1.24.3
fastapi==0.102.0
uvicorn[standard]==0.23.1
pydantic==2.7.0
typing-extensions==4.8.0
httpx==0.24.0
python-dotenv==1.0.0
pytest==8.3.2
loguru==0.7.0



======================================================= 
ESTRUCTURA DEL PROYECTO
======================================================= 

proyecto/
│
│
├── main.py                  # Punto de entrada de la aplicación FastAPI y definición de rutas
|
├── config.py                # Configuración general: URLs de APIs, base de datos, secretos
|
├── models/                  # Clases de dominio
│   ├── instruments.py       # Clase abstracta FixedIncomeInstrument y clases concretas: Bono, Letraetc.
│   ├── dolar.py             # Clase Dolar (Observer), notifica cambios a instrumentos
│   ├── alerta.py            # Clase Alerta, evalúa condiciones y notifica usuarios
│   └── user.py              # Clases User y Session, manejo de roles y permisos
|
├── factory/                 # Patrón Factory para crear instrumentos financieros
│   └── fixed_income_factory.py
|
├── db/                      # Persistencia de datos
│   ├── abstract_db.py       # Clase base abstracta que define la interfaz de todas las bases de datos
│   ├── instruments_db.py    # Maneja almacenamiento de instrumentos
│   └── users_db.py          # Maneja usuarios y sesiones
|
├── api/                     # Integración con fuentes externas
│   └── cotizar_api.py       # Obtiene datos de bonos, tasas y tipo de cambio
|
├── auth/                    # Seguridad y autenticación
│   └── auth_service.py      # Login, logout y gestión de sesiones
|
├── utils/                   # Funciones auxiliares
│   └── helpers.py
|
├── tests/                   # Pruebas unitarias
│   ├── test_instruments.py
│   ├── test_alertas.py
│   └── test_auth.py
|
├── requirements.txt         # Dependencias del proyecto
|
└── README.md






Docker (hay q emprolijar)
# Definimos el python base que se va a utilizar para correr la imagen
# y con eso construir el contenedor (contiene las librerias, código, etc)
FROM python:3.11-slim

# Creamos, si no existe, el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos solo el contenido que esta dentro de la carpeta Proyecto al contenedor
# COPY . /app

# Instalamos las dependencias dentro del contenedor usando el python base
# RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto por donde la app va a recibir conexiones (x donde escucha peticiones)
EXPOSE 8000

"""
Se le dice a Docker que cuando arranque el contenedor, ejecute estos 
comandos para iniciar la aplicación.
Uvicorn, servidor web que corre la API de python.
main:cotizar, nombre del archivo y el de la variable donde se instancia FastAPI
--host 0.0.0.0, le dice a uvicorn que acepte conexiones desde cualquier IP, no 
solo desde dentro del contenedor (la local)
-- port 8000, es el puerto del contenedor que expusimos antes.
"""
CMD ["uvicorn", "main:cotizar", "--host", "0.0.0.0", "--port", "8000"]


# Asegurarse de estar en la carpeta Proyecto y no solo en Programacion_2 para ejecutalro.

## Para construir la imagen localmente:
En la terminal parado en la carpeta "Proyecto":
docker build -t nombre-de-tu-imagen:latest .

Explicación: 
- docker build, crea la imange
- -t nombre-de-tu-imagen:latest, le asigna un nombre y una etiqueta a la imagen
- ., indica que el dockerfile esta en el directorio actual

Ejemplo: 
docker build -t cotizar-api:latest

## Ejecutar la imagen localmente
una vez construida, la probamos ejecutando que crea un contenedor
docker run -p 8000:8000 cotizar-api:latest
Explicacion: 
- -p 8000:8000, mapea el puerto 8000 del contenedor al 8000 de nuestra máquina, así la podemos abrir en http://localhost:8000 en el navegado.
- cotizar-api:latest, nombre de la imagen que construiste

## Detener la app
si la ejecutamos en primer plano, se detiene con ctrl + c.

Para ejecutarla en segundo plano:
docker run -d -p 8000:8000 cotizar-api:lates
se detiene con:
-d (significa detached)


Si hay cambios en el código se vuelve a ejecutar en terminal (reemplaza todo lo que había con el código nuevo):
1. docker build -t cotizar-api:latest .
2. docker run -p 8000:8000 -e PORT=8000 cotizar-api:latest (para que funcione con render)

o para crear el contenedor y que se borre solo cuando termina de ejecutarse el comando:
docker run --rm -p 8000:8000 cotizar-api:latest 

activar docker:
docker start id_docker o nombre_docker

detener el docker:
docker stop id_docker o nombre_docker

detener todos los docker:
docker stop $(docker ps -q)



render command to start the app with each deploy:
uvicorn main:cotizar --host 0.0.0.0 --port $PORT



































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











1. Activar entorno virtual
- **Windows:**
```bash
.\venv\Scripts\activate
- **Linux / MacOS:**
```bash
source venv/bin/activate

2. Desactivar entorno virtual (opcional)
bash
Copiar código
deactivate
Instalación de Dependencias
Instalar todas las librerías necesarias desde el archivo requirements.txt:

bash
Copiar código
pip install -r requirements.txt
Si se agregan nuevas librerías, actualizar requirements.txt:

bash
Copiar código
pip freeze > requirements.txt
Estructura del Proyecto
text
Copiar código
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
Librerías Utilizadas
Algunas librerías clave y su propósito:

Librería	Versión	Uso principal
fastapi	0.121.1	Framework principal para crear la API
uvicorn	0.23.1	Servidor ASGI para ejecutar FastAPI
SQLAlchemy	2.0.31	ORM para interactuar con la base de datos
psycopg2-binary	2.9.9	Driver PostgreSQL para SQLAlchemy
pydantic	2.7.0	Validación y serialización de datos
requests	2.32.3	Consumo de APIs externas
beautifulsoup4	4.12.3	Web scraping de HTML
selenium	4.38.0	Automatización de navegador para scraping dinámico
webdriver-manager	4.0.1	Manejo automático de drivers para Selenium
schedule	1.2.1	Tareas programadas dentro de la API
pandas	2.2.2	Manejo de datos en tablas y CSV
numpy	1.24.3	Operaciones matemáticas y arrays
matplotlib	3.9.2	Visualización de datos
python-dotenv	1.0.0	Manejo de variables de entorno
pytest	8.3.2	Pruebas unitarias
loguru	0.7.0	Logging y registro de eventos

Nota: El archivo completo requirements.txt incluye todas las librerías necesarias para ejecutar la API.

Ejecución Local
Activar el entorno virtual:

bash
Copiar código
.\venv\Scripts\activate
Ejecutar la API con Uvicorn:

bash
Copiar código
uvicorn main:cotizar --reload
Acceder a la documentación interactiva: http://127.0.0.1:8000/docs

Pruebas Unitarias
Ejecutar todas las pruebas con pytest:

bash
Copiar código
pytest tests/
Despliegue con Docker y Render
La aplicación se desplegó en Render utilizando Docker como lenguaje.

Se configuró el directorio raíz como Proyecto.

Render utiliza el Dockerfile incluido en el proyecto, por lo que no es necesario configurar build o start commands manualmente.

Variable de entorno DB_URL configurada en Render para conexión con Supabase (contiene usuario, contraseña y URL de la base de datos).

Ejecutar Docker localmente (opcional)
Construir la imagen Docker:

bash
Copiar código
docker build -t cotizar-api:latest .
Ejecutar el contenedor:

bash
Copiar código
docker run -p 8000:8000 cotizar-api:latest
Acceder a la API en http://localhost:8000

Ejecutar en segundo plano (detached):

bash
Copiar código
docker run -d -p 8000:8000 cotizar-api:latest
Detener contenedores:

bash
Copiar código
docker stop <nombre_o_id_del_contenedor>
Para detener todos los contenedores:

bash
Copiar código
docker stop $(docker ps -q)
Notas
Se recomienda usar Python 3.11 para compatibilidad con todas las librerías.

Variables sensibles se manejan con .env localmente y DB_URL en Render.

La API integra datos de Supabase (PostgreSQL), scraping web y notificaciones de alertas.







