from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import os

# --- Importaciones de Módulos Locales ---
from . import models                 # Modelos de SQLAlchemy
from .database import engine, get_db # Conexión a la DDBB y Dependencia
from . import crud, schemas          # Lógica de CRUD y Esquemas de Datos
from .security import verify_password # Utilidad de verificación de contraseña

# --- IMPORTANTE: Importar el router de tu aplicación (IA / Activar) ---
from .app.routes import router as app_router 

# LÍNEA CRÍTICA: Crea las tablas en la base de datos (sql_app.db) si no existen
models.Base.metadata.create_all(bind=engine)

# Configuración del directorio de almacenamiento
STORAGE_DIR = "backend/file_storage"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# --- Inicialización de FastAPI ---
app = FastAPI()

# --- INTEGRACIÓN DEL ROUTER DE LA IA (Solución al error 404) ---
# Esto conecta las rutas de backend/app/routes.py (como /activar) con la app principal
app.include_router(app_router)


# --- Configuración de CORS ---
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


# --- Montaje de Archivos Estáticos ---
# Asegúrate de que la carpeta exista, si no, FastAPI lanzará un error al iniciar
AUDIO_DIR = "backend/app/audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)
    
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")


@app.get("/")
def root():
    return {"mensaje": "Backend de ORIÓN activo 🚀", "status": "Database Ready"}


# ==========================================
#      RUTAS DE AUTENTICACIÓN (AUTH)
# ==========================================

## 1. REGISTRO DE USUARIO
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El correo electrónico ya está registrado."
        )
    new_user = crud.create_user(db=db, user=user)
    return new_user

## 2. INICIO DE SESIÓN
@app.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generar token simple (fake)
    access_token = f"fake_token_for_user_{user.id}" 
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}


# ==========================================
#      RUTAS DE CRUD DE ARCHIVOS
# ==========================================

## 3. GUARDAR CONVERSACIÓN (Create)
@app.post("/files/save", response_model=schemas.ConversationFile, status_code=status.HTTP_201_CREATED)
def save_conversation(data: schemas.ConversationFileCreate, db: Session = Depends(get_db)):
    user_id_temp = 1 # ID temporal
    
    import time
    timestamp = int(time.time())
    unique_filename = f"user_{user_id_temp}_{timestamp}.txt"
    file_path = os.path.join(STORAGE_DIR, unique_filename)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data.content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al escribir el archivo en disco: {e}"
        )

    db_file = crud.create_conversation_file(
        db=db, 
        user_id=user_id_temp, 
        filename=unique_filename,
        filepath=file_path
    )
    return db_file

## 4. LISTAR CONVERSACIONES (Read List)
@app.get("/files/{user_id}", response_model=list[schemas.ConversationFile])
def get_conversations_list(user_id: int, db: Session = Depends(get_db)):
    files = crud.get_user_files(db, user_id=user_id)
    if not files:
        return []
    return files

## 5. OBTENER CONTENIDO (Read Content)
@app.get("/files/content/{file_id}")
def get_file_content(file_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_file_by_id(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado.")
        
    try:
        with open(db_file.filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al leer el archivo en disco.")

    return {
        "file_id": db_file.id,
        "filename": db_file.filename,
        "content": content
    }

## 6. ELIMINAR CONVERSACIÓN (Delete)
@app.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_file(file_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_file_by_id(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado.")
        
    if os.path.exists(db_file.filepath):
        try:
            os.remove(db_file.filepath)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error al eliminar el archivo físico del disco."
            )

    crud.delete_file(db, db_file)
    return Response(status_code=status.HTTP_204_NO_CONTENT)