# /OrionFastAPI/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definición del archivo SQLite local
# Esto crea el archivo 'sql_app.db' en el mismo directorio.
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/sql_app.db"

# 2. Creación del motor (Engine)
# connect_args es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Creación de la Sesión (SessionLocal)
# Se utiliza para crear una sesión de base de datos por solicitud.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base Declarativa
# La clase base de la cual heredarán nuestros modelos (User, ConversationFile).
Base = declarative_base()

# 5. Función de Dependencia para obtener la DDBB
# Esta función se utiliza en las rutas de FastAPI (main.py)
# para obtener y cerrar la sesión de la base de datos automáticamente.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()