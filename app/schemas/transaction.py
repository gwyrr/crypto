from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    """
    ESQUEMA BASE DE TRANSACCIONES
    Define los campos requeridos para cualquier operacion de compra o venta.
    """
    # ID del activo operado (ej: Bitcoin)
    asset_id: int
    
    # Cantidad a operar (debe ser mayor a 0)
    amount: float = Field(gt=0)
    
    # Precio unitario al que se ejecuta la operacion (debe ser mayor a 0)
    buy_price: float = Field(gt=0)
    
    # Tipo de operacion: solo permite 'buy' o 'sell'
    type: str = Field(default="buy", pattern="^(buy|sell)$")


class TransactionCreate(TransactionBase):
    """
    ESQUEMA DE CREACION
    Se utiliza cuando un usuario envia una nueva operacion desde el frontend.
    """
    pass


class TransactionUpdate(BaseModel):
    """
    ESQUEMA DE ACTUALIZACION
    Permite modificar una transaccion existente. Todos los campos son opcionales.
    """
    asset_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    buy_price: float | None = Field(default=None, gt=0)
    type: str | None = Field(default=None, pattern="^(buy|sell)$")


class TransactionRead(TransactionBase):
    """
    ESQUEMA DE RESPUESTA (Lectura)
    Incluye informacion generada por el servidor como el ID, el usuario y la fecha.
    """
    id: int
    user_id: int
    date: datetime
    # Valor calculado (amount * buy_price)
    investment: float

    # Configuracion para trabajar con modelos de base de datos
    model_config = ConfigDict(from_attributes=True)
