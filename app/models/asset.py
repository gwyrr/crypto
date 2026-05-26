from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Asset(Base):
    """
    MODELO BASE DE ACTIVOS
    Define la estructura basica para cualquier tipo de inversion en el sistema.
    Utiliza herencia polimorfica de SQLAlchemy para permitir extender a Criptos, Acciones, etc.
    """
    __tablename__ = "assets"

    # Identificador unico autoincremental
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre descriptivo (ej: Bitcoin)
    name = Column(String(100), nullable=False)
    
    # Simbolo o Ticker (ej: BTC)
    symbol = Column(String(20), nullable=False, unique=True)
    
    # Columna discriminadora para la herencia (identifica si es crypto, asset, etc)
    type = Column(String(50), nullable=False)

    # Relacion: Un activo puede estar presente en multiples transacciones
    transactions = relationship("Transaction", back_populates="asset")

    # Configuracion de herencia polimorfica
    __mapper_args__ = {
        "polymorphic_identity": "asset",
        "polymorphic_on": type,
    }

    def market_identifier(self):
        """
        Retorna el identificador que se usara para buscar precios en APIs externas.
        Por defecto usa el simbolo en minusculas.
        """
        return self.symbol.lower()

    def __str__(self):
        """Representacion legible en consola."""
        return f"asset: {self.name} [{self.symbol}]"


class Cryptocurrency(Asset):
    """
    MODELO DE CRIPTOMONEDAS
    Hereda de Asset y anade campos especificos para el mercado cripto.
    """
    __tablename__ = "cryptos"

    # Llave primaria vinculada a la tabla padre (Asset)
    id = Column(Integer, ForeignKey("assets.id"), primary_key=True)
    
    # ID especifico de la API (ej: 'bitcoin' para CoinGecko)
    api_id = Column(String(100))

    # Identidad polimorfica especifica
    __mapper_args__ = {
        "polymorphic_identity": "crypto",
    }

    def market_identifier(self):
        """
        Retorna el api_id (si esta configurado) para una busqueda mas precisa en la API.
        """
        return self.api_id or super().market_identifier()

    def __str__(self):
        """Representacion legible en consola."""
        return f"crypto: {self.name} [{self.symbol}]"
