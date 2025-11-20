# /backend/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime

# Esquema para el Registro (entrada de datos del formulario)
class UserCreate(BaseModel):
    # Usamos EmailStr para validar que el formato sea un email válido
    email: EmailStr 
    password: str # Necesitamos la contraseña para el hash

# Esquema para la respuesta (lo que devolvemos al frontend después de crear un usuario)
class User(BaseModel):
    id: int
    email: EmailStr
    
    # Esta configuración permite que el modelo sea compatible con SQLAlchemy ORM
    class Config:
        from_attributes = True

# Esquema para los archivos de conversación
class ConversationFileBase(BaseModel):
    filename: str

class ConversationFileCreate(ConversationFileBase):
    # Podríamos incluir el contenido del archivo si fuera pequeño
    content: str

class ConversationFile(ConversationFileBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True