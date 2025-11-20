# /backend/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from .security import hash_password # Importamos la utilidad de hashing

# --- FUNCIÓN CREATE (Registro) ---
def create_user(db: Session, user: schemas.UserCreate):
    # 1. Hashear la contraseña antes de guardarla
    hashed_pass = hash_password(user.password)
    
    # 2. Crear la instancia del modelo de SQLAlchemy
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_pass
    )
    
    # 3. Agregar y guardar en la DDBB
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Obtener el ID generado por la DDBB
    
    return db_user

# --- FUNCIÓN READ (Verificación de existencia) ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# --- FUNCIÓN CREATE (Guardar Metadata del Archivo) ---
def create_conversation_file(db: Session, user_id: int, filename: str, filepath: str):
    """Guarda la metadata del archivo en la DDBB."""
    
    db_file = models.ConversationFile(
        user_id=user_id,
        filename=filename,
        filepath=filepath
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file

# --- FUNCIÓN READ (Listar Archivos por Usuario) ---
def get_user_files(db: Session, user_id: int):
    """Obtiene todos los archivos registrados para un usuario específico."""
    return db.query(models.ConversationFile).filter(models.ConversationFile.user_id == user_id).all()

# --- FUNCIÓN READ (Obtener archivo por ID) ---
def get_file_by_id(db: Session, file_id: int):
    """Obtiene un archivo por su ID."""
    return db.query(models.ConversationFile).filter(models.ConversationFile.id == file_id).first()
# --- FUNCIÓN DELETE (Eliminar Archivo) ---
def delete_file(db: Session, db_file: models.ConversationFile):
    """Elimina la metadata del archivo de la DDBB."""
    # Eliminamos el objeto de SQLAlchemy
    db.delete(db_file)
    db.commit()
    return True # Éxito en la eliminación