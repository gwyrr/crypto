from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """
    MODELO DE USUARIOS
    Representa a una persona registrada en la plataforma.
    Almacena credenciales de acceso y mantiene la relacion con sus inversiones.
    """
    __tablename__ = "users"

    # Identificador unico del usuario
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre de usuario unico (se usa para el login)
    username = Column(String(150), unique=True, index=True, nullable=False)
    
    # Correo electronico unico (se usa para contacto o recuperacion)
    email = Column(String(150), unique=True, index=True, nullable=False)
    
    # Contrasena cifrada (nunca se guarda en texto plano)
    hashed_password = Column(String(255), nullable=False)

    # Relacion: Un usuario puede tener muchisimas transacciones a lo largo del tiempo
    transactions = relationship("Transaction", back_populates="owner")

    def __str__(self):
        """Representacion legible en consola."""
        return f"Usuario: {self.username} | email: {self.email}"