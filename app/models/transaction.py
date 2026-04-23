from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))

    amount = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("User", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")

    def calculate_investment(self):
        return self.amount * self.buy_price

    def __str__(self):
        return f"transaction: user={self.user_id} asset={self.asset_id} amount={self.amount}"
