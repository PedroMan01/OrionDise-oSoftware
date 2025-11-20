# models.py (Ejemplo simplificado)
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base # Suponiendo que Base está definida en database.py

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relación: Un usuario puede tener múltiples archivos
    files = relationship("ConversationFile", back_populates="owner")

class ConversationFile(Base):
    __tablename__ = "conversation_files"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Clave externa
    filename = Column(String, index=True)
    filepath = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación: El archivo pertenece a un usuario
    owner = relationship("User", back_populates="files")