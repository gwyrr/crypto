# Crypto Portfolio API - Proyecto Final (Programacion V)

![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)
![Testing](https://img.shields.io/badge/Testing-Pytest-yellow.svg)

Sistema integral de gestion de portafolios de criptomonedas desarrollado como proyecto final para la asignatura **Programacion V**. La aplicacion simula un entorno real de desarrollo, implementando una arquitectura escalable, codigo limpio, seguridad mediante JWT e integracion con APIs externas en tiempo real.

##  Objetivos y Cumplimiento de la Rubrica

El proyecto fue diseñado acorde a los parametros solicitados:

1. **Programacion Orientada a Objetos (POO):** Uso intensivo de clases, encapsulamiento (`@property` en modelos), herencia (polimorfismo con SQLAlchemy entre `Asset` y `Cryptocurrency`) y metodos dunder (`__str__`).
2. **Consumo de APIs Externas:** Integracion robusta con la API de **CoinGecko** a traves de la libreria `requests`, incluyendo manejo de errores `try-except` y parseo seguro de JSON.
3. **Persistencia y ORM:** Uso de **SQLite** gestionado a traves de **SQLAlchemy**, con operaciones CRUD completas y relaciones bidireccionales (`ForeignKey`, `relationship`).
4. **Control de Versiones y Dependencias:** Gestion de paquetes mediante `requirements.txt` y uso de entornos virtuales (`venv`). Repositorio gestionado con Git (ramas, commits semanticos).
5. **Arquitectura Modular:** Separacion de responsabilidades clara (Controladores, Servicios, Modelos, Esquemas y Utilidades).
6. **Manejo de Errores y Validaciones:** Validacion estricta de datos de entrada usando Pydantic y manejo de excepciones HTTP personalizadas para reglas de negocio (ej. prevencion de venta sin saldo).
7. **Pruebas (Testing):** Cobertura de pruebas unitarias sobre modelos, rutas y lógica de servicios utilizando `pytest`.

## Arquitectura del Proyecto

```text
/proyecto
│
├── app/
│   ├── controllers/      # Rutas y Endpoints de la API (FastAPI Routers)
│   ├── dependencies/     # Inyeccion de dependencias (ej. Autenticación)
│   ├── models/           # Modelos de base de datos SQLAlchemy (POO)
│   ├── schemas/          # Esquemas Pydantic para validacion I/O
│   ├── services/         # Logica de negocio core e integraciones
│   ├── static/           # Frontend Web (HTML, CSS, JS)
│   └── utils/            # Utilidades generales (Hashing, JWT)
│
├── config/               # Configuraciones y variables de entorno
├── tests/                # Pruebas unitarias (pytest)
├── .env                  # Variables de entorno locales
├── main.py               # Punto de entrada de la aplicacion
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Documentacion
```

##  Instalacion y Ejecucion

### 1. Clonar el repositorio y crear el entorno virtual
```bash
git clone <https://github.com/gwyrr/crypto.git>
cd "PROYECTO PYTHON"
python -m venv venv
```

### 2. Activar el entorno e instalar dependencias
**En Windows:**
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

**En Mac/Linux:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Ejecutar el servidor de desarrollo
El proyecto utiliza Uvicorn como servidor ASGI.
```bash
python -m uvicorn main:app --reload
```
de no funcionar poner:
```bash
py -m uvicorn main:app --reload
```
Una vez iniciado, la aplicacion web estara disponible en: `http://127.0.0.1:8000/app/`
La documentacion interactiva de la API (Swagger UI) esta en: `http://127.0.0.1:8000/docs`

## Pruebas Unitarias (Testing)
Para verificar el correcto funcionamiento de los modulos principales, ejecuta la suite de pruebas usando `pytest`:

```bash
python -m pytest tests/
```
Esto validara la logica de calculo de inversiones, los servicios de usuarios y el manejo de tokens de seguridad.

##  Funcionalidades Core

- **Autenticacion Segura:** Registro y login con encriptacion de contraseñas (`bcrypt`) y emision de JSON Web Tokens (`JWT`).
- **Dashboard Dinamico:** Interfaz web tipo Glassmorphism responsiva que carga datos asincronamente desde el backend.
- **Cotizacion en Tiempo Real:** Interfaz conectada a CoinGecko para auto-completar el precio de mercado exacto en el momento de crear una transaccion.
- **Gestor de Portafolio:** Seguimiento de ganancias no realizadas (flotantes) y ganancias realizadas, calculando el rendimiento historico de las inversiones con alta precision.
