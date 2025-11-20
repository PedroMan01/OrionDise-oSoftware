from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import os

# Importaciones de Módulos Locales
from . import models                 # Modelos de SQLAlchemy
from .database import engine, get_db # Conexión a la DDBB y Dependencia
from . import crud, schemas          # Lógica de CRUD y Esquemas de Datos
from .security import verify_password # Utilidad de verificación de contraseña

# LÍNEA CRÍTICA: Crea las tablas en la base de datos (sql_app.db) si no existen
models.Base.metadata.create_all(bind=engine)

STORAGE_DIR = "backend/file_storage"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)
# --- Inicialización de FastAPI ---
app = FastAPI()

@app.post("/files/save", response_model=schemas.ConversationFile, status_code=status.HTTP_201_CREATED)
def save_conversation(data: schemas.ConversationFileCreate, db: Session = Depends(get_db)):
    # NOTA: En un proyecto real, el user_id vendría del token JWT

    # 1. Asignar un user_id temporal para pruebas (reemplazar con ID de token)
    user_id_temp = 1
    
    # 2. Generar un nombre de archivo único
    import time
    timestamp = int(time.time())
    unique_filename = f"user_{user_id_temp}_{timestamp}.txt"
    file_path = os.path.join(STORAGE_DIR, unique_filename)
    
    try:
        # 3. Guardar el contenido en un archivo .txt en el disco
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data.content)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al escribir el archivo en disco: {e}"
        )

    # 4. Registrar la metadata en la DDBB
    db_file = crud.create_conversation_file(
        db=db, 
        user_id=user_id_temp, 
        filename=unique_filename,
        filepath=file_path
    )
    
    return db_file

# --- Configuración de CORS ---

# URLs de tu frontend
FRONTEND_URL = "http://localhost:5173"

# Middleware oficial para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware estático para asegurar headers en archivos
class CORSMiddlewareStatic(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        return response

app.add_middleware(CORSMiddlewareStatic)


# --- Montaje de Rutas y StaticFiles ---

# Montar archivos estáticos (ajustado para la nueva estructura /backend)
app.mount("/audio", StaticFiles(directory="backend/app/audio"), name="audio")

@app.get("/")
def root():
    return {"mensaje": "Backend de ORIÓN activo 🚀", "status": "Database Ready"}


# --- RUTAS DE AUTENTICACIÓN (Create & Read) ---

## 1. REGISTRO DE USUARIO (CRUD: Create User)
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # Verificar si el email ya existe
    db_user = crud.get_user_by_email(db, email=user.email)
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El correo electrónico ya está registrado."
        )
    
    # Crear y guardar el nuevo usuario
    new_user = crud.create_user(db=db, user=user)
    
    # Devolver el nuevo usuario (sin la contraseña hasheada)
    return new_user


## 2. INICIO DE SESIÓN (CRUD: Read User & Verify Password)
@app.post("/login")
# Usamos el formulario estándar de OAuth2 para login (email y password)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # NOTA: OAuth2PasswordRequestForm usa 'username' y 'password'.
    # Usaremos 'username' para recibir el email.
    
    # 1. Buscar el usuario por email (username)
    user = crud.get_user_by_email(db, email=form_data.username)
    
    if not user:
        # El usuario no existe
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verificar la contraseña con el hash
    if not verify_password(form_data.password, user.hashed_password):
        # La contraseña no coincide
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Autenticación exitosa
    # Por ahora, solo devolvemos un mensaje de éxito. 
    # En un proyecto real, aquí se generaría un JWT (JSON Web Token).
    
    # Generar un token simple de ejemplo (reemplazar con JWT en el futuro)
    access_token = f"fake_token_for_user_{user.id}" 
    
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}
# /backend/main.py (Continuación)

## 4. OBTENER LISTA DE CONVERSACIONES (CRUD: Read List)
@app.get("/files/{user_id}", response_model=list[schemas.ConversationFile])
def get_conversations_list(user_id: int, db: Session = Depends(get_db)):
    
    # 1. Obtener los archivos de la DDBB para este usuario
    files = crud.get_user_files(db, user_id=user_id)
    
    if not files:
        # Devolver una lista vacía, no un error 404
        return []

    # 2. Devolver la lista de metadata (ID, filename, etc.)
    return files


## 5. OBTENER CONTENIDO ESPECÍFICO (CRUD: Read Content)
@app.get("/files/content/{file_id}")
def get_file_content(file_id: int, db: Session = Depends(get_db)):
    
    # 1. Buscar la metadata del archivo en la DDBB
    db_file = crud.get_file_by_id(db, file_id=file_id)
    
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado.")
        
    # 2. Leer el contenido del archivo físico en disco
    try:
        with open(db_file.filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al leer el archivo en disco.")

    # 3. Devolver el contenido y la metadata
    return {
        "file_id": db_file.id,
        "filename": db_file.filename,
        "content": content
    }
## 6. ELIMINAR CONVERSACIÓN (CRUD: Delete File)
@app.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_file(file_id: int, db: Session = Depends(get_db)):
    
    # 1. Buscar la metadata del archivo en la DDBB
    db_file = crud.get_file_by_id(db, file_id=file_id)
    
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado.")
        
    # 2. Eliminar el archivo físico del disco
    if os.path.exists(db_file.filepath):
        try:
            os.remove(db_file.filepath)
        except Exception:
            # Si no se puede borrar el archivo físico, lanzamos un error interno
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error al eliminar el archivo físico del disco."
            )

    # 3. Eliminar la entrada de la base de datos
    crud.delete_file(db, db_file)
    
    # 4. Devolver respuesta 204 No Content (éxito sin cuerpo de respuesta)
    return Response(status_code=status.HTTP_204_NO_CONTENT)