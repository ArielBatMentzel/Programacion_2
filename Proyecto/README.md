# Estructura del Proyecto

proyecto/
├── main.py                  # Punto de entrada de la aplicación FastAPI y definición de rutas
├── config.py                # Configuración general: URLs de APIs, base de datos, secretos
├── models/                  # Clases de dominio
│   ├── instruments.py       # Clase abstracta FixedIncomeInstrument y clases concretas: Bono, Letra, etc.
│   ├── dolar.py             # Clase Dolar (Observer), notifica cambios a instrumentos
│   ├── alerta.py            # Clase Alerta, evalúa condiciones y notifica usuarios
│   └── user.py              # Clases User y Session, manejo de roles y permisos
├── factory/                 # Patrón Factory para crear instrumentos financieros
│   └── fixed_income_factory.py
├── db/                      # Persistencia de datos
│   ├── abstract_db.py       # Clase base abstracta que define la interfaz de todas las bases de datos
│   ├── instruments_db.py    # Maneja almacenamiento de instrumentos
│   └── users_db.py          # Maneja usuarios y sesiones
├── api/                     # Integración con fuentes externas
│   └── cotizar_api.py       # Obtiene datos de bonos, tasas y tipo de cambio
├── auth/                    # Seguridad y autenticación
│   └── auth_service.py      # Login, logout y gestión de sesiones
├── utils/                   # Funciones auxiliares
│   └── helpers.py
├── tests/                   # Pruebas unitarias
│   ├── test_instruments.py
│   ├── test_alertas.py
│   └── test_auth.py
├── requirements.txt         # Dependencias del proyecto
└── README.md
