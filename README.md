# Crypto Portfolio API

Proyecto backend en Python con FastAPI para registrar usuarios, activos, transacciones y consultar informacion de criptomonedas desde una API externa.

## Tecnologias

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Passlib con bcrypt

## Estructura

```text
app/
├── controllers/
├── models/
├── schemas/
├── services/
└── utils/
config/
tests/
main.py
requirements.txt
```

## Funcionalidades actuales

- CRUD de usuarios
- CRUD de activos
- CRUD de transacciones
- Consulta de precios y top de criptomonedas desde CoinGecko
- Persistencia con SQLite
- Validaciones basicas
- Pruebas unitarias con unittest

## Ejecucion

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Testing

```bash
python -m unittest discover -s tests
```
