from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="asset")

    __mapper_args__ = {
        "polymorphic_identity": "asset",
        "polymorphic_on": type,
    }

    def market_identifier(self):
        return self.symbol.lower()

    def __str__(self):
        return f"asset: {self.name} [{self.symbol}]"


class Cryptocurrency(Asset):
    __tablename__ = "cryptos"

    id = Column(Integer, ForeignKey("assets.id"), primary_key=True)
    api_id = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "crypto",
    }

    def market_identifier(self):
        return self.api_id or super().market_identifier()

    def __str__(self):
        return f"crypto: {self.name} [{self.symbol}]"
