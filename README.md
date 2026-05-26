# Crypto Portfolio API - Proyecto Final (Programacion V)

![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)
![MySQL](https://img.shields.io/badge/Database-MySQL-4479A1.svg)
![Testing](https://img.shields.io/badge/Testing-Pytest-yellow.svg)

Sistema integral de gestion de portafolios de criptomonedas desarrollado como proyecto final para la asignatura **Programacion V**. La aplicacion simula un entorno real de desarrollo, implementando una arquitectura escalable, codigo limpio, seguridad mediante JWT e integracion con la base de datos **MySQL** y APIs externas en tiempo real.

##  Objetivos y Cumplimiento de la Rubrica

El proyecto fue diseñado acorde a los parametros solicitados:

1. **Programacion Orientada a Objetos (POO):** Uso de clases, encapsulamiento (`@property` en modelos), herencia (polimorfismo con SQLAlchemy entre `Asset` y `Cryptocurrency`) y metodos dunder (`__str__`).
2. **Consumo de APIs Externas:** Integracion robusta con la API de **CoinGecko** para obtener precios en tiempo real.
3. **Persistencia y ORM:** Conectado a **MySQL** a traves de **SQLAlchemy** con operaciones CRUD completas y relaciones bidireccionales (`ForeignKey`, `relationship`).
4. **Consulta SQL Util:** Implementacion de un endpoint estadistico (`GET /transactions/stats/popular`) que realiza una consulta agregada (`JOIN` y `GROUP BY`) para calcular el volumen total invertido y transacciones por cada activo.
5. **Control de Versiones y Dependencias:** Gestion de paquetes mediante `requirements.txt` (incluyendo drivers de MySQL `pymysql` y `cryptography`).
6. **Manejo de Errores y Validaciones:** Validaciones robustas con Pydantic y excepciones HTTP.

## Arquitectura del Proyecto

```text
/proyecto
│
├── app/
│   ├── controllers/      # Rutas y Endpoints de la API (FastAPI Routers)
│   ├── dependencies/     # Inyeccion de dependencias (ej. Autenticacion)
│   ├── models/           # Modelos de base de datos SQLAlchemy (con VARCHAR limitados para MySQL)
│   ├── schemas/          # Esquemas Pydantic para validacion I/O
│   ├── services/         # Logica de negocio core e integraciones
│   ├── static/           # Frontend Web (HTML, CSS, JS)
│   └── utils/            # Utilidades generales (Hashing, JWT)
│
├── config/               # Configuraciones y variables de entorno
├── tests/                # Pruebas unitarias (pytest)
├── .env                  # Variables de entorno (Conexion de MySQL)
├── main.py               # Punto de entrada de la aplicacion
├── schema.sql            # Script SQL de creacion de la base de datos
├── requirements.txt      # Dependencias del proyecto (incluye pymysql)
└── README.md             # Documentacion
```

##  Instalacion y Ejecucion

### 1. Clonar el repositorio y crear el entorno virtual
```bash
git clone <https://github.com/gwyrr/crypto.git>
cd "PROYECTO PYTHON"
python -m venv venv
```

### 2. Configurar la base de datos (MySQL)
1. Abre tu administrador de base de datos (por ejemplo, **MySQL Workbench**).
2. Crea la base de datos ejecutando el script en [schema.sql](file:///c:/Users/ALASKA/Desktop/MASTER/PROYECTO%20PYTHON/schema.sql) o creando un esquema vacio:
   ```sql
   CREATE DATABASE crypto_portfolio;
   ```
3. Edita el archivo `.env` en la raiz del proyecto para colocar tus credenciales de MySQL:
   ```env
   DATABASE_URL=mysql+pymysql://usuario:contrasena@localhost:3306/crypto_portfolio
   ```

### 3. Activar el entorno e instalar dependencias
**En Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
python -m pip install -r requirements.txt
```

**En Mac/Linux:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Ejecutar el servidor de desarrollo
```powershell
.\venv\Scripts\python -m uvicorn main:app --reload
```
Una vez iniciado, la aplicacion web estara disponible en: `http://127.0.0.1:8000/app/`
La documentacion interactiva de la API (Swagger UI) esta en: `http://127.0.0.1:8000/docs`

## Pruebas Unitarias (Testing)
Para verificar el correcto funcionamiento de los modulos principales:
```bash
python -m pytest tests/
```

##  Funcionalidades Core

- **Autenticacion Segura:** Registro y login con encriptacion de contraseñas (`bcrypt`) y emision de tokens JWT.
- **Cotizacion en Tiempo Real:** Interfaz conectada a CoinGecko para auto-completar el precio exacto al registrar transacciones.
- **Gestor de Portafolio:** Seguimiento de ganancias no realizadas y ganancias realizadas, calculando el rendimiento historico de las inversiones con alta precision.
- **Modulo de Estadisticas:** Consulta DDL optimizada para mostrar el ranking de popularidad de activos financieros por volumen global.
