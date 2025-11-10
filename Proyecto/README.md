======================================================= 
GUÍA PARA CREAR, ACTIVAR Y ACTUALIZAR EL ENTORNO VIRTUAL 
======================================================= 
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
