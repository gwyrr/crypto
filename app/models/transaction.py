from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):
    """
    MODELO DE TRANSACCIONES
    Registra cada operacion de compra o venta realizada por un usuario.
    Almacena el precio de ejecucion, la cantidad y la fecha exacta.
    """
    __tablename__ = "transactions"

    # Identificador unico de la transaccion
    id = Column(Integer, primary_key=True, index=True)
    
    # Llave foranea al usuario que realizo la operacion
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Llave foranea al activo (crypto, etc) involucrado
    asset_id = Column(Integer, ForeignKey("assets.id"))
    
    # Tipo de operacion: 'buy' (compra) o 'sell' (venta)
    type = Column(String(10), nullable=False, default="buy")

    # Cantidad de unidades operadas (ej: 0.5 BTC)
    amount = Column(Float, nullable=False)
    
    # Precio unitario al que se ejecuto la operacion ($)
    buy_price = Column(Float, nullable=False)
    
    # Fecha y hora de la transaccion (UTC por defecto)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones: Acceso directo al objeto User y Asset
    owner = relationship("User", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")

    @property
    def is_buy(self) -> bool:
        """Helper para saber si es una compra."""
        return self.type == "buy"

    @property
    def is_sell(self) -> bool:
        """Helper para saber si es una venta."""
        return self.type == "sell"

    def calculate_investment(self):
        """
        Calcula el flujo de caja de la operacion.
        Retorna valor positivo para compras (salida de dinero/inversion)
        y negativo para ventas (entrada de dinero/recuperacion).
        """
        multiplier = 1 if self.is_buy else -1
        return self.amount * self.buy_price * multiplier

    def __str__(self):
        """Representacion legible en consola."""
        return f"transaction: user={self.user_id} asset={self.asset_id} amount={self.amount}"
