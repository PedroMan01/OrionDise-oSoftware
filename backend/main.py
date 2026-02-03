from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import os

from . import models, crud, schemas
from .database import engine, get_db
from .security import verify_password
from .app.routes import router as app_router
from .app.services import thought_service
from .app.global_state import global_state
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Initialize Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orion Assistant API")

# --- CORS ---
origins = ["*"] # Allow all for VPN/Dev access
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(app_router) 

# --- STATIC FILES ---
from pathlib import Path

# ... (imports)

# --- STATIC FILES ---
BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "app" / "audio"
if not AUDIO_DIR.exists():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

@app.get("/")
def root():
    return {"message": "Orion Backend Online 🚀"}

# --- SCHEDULER ---
scheduler = AsyncIOScheduler()

def check_inactivity_and_think():
    """
    Checks if user has been inactive for > 120 minutes (7200 seconds).
    If so, triggers a thought cycle.
    """
    last_active = global_state.get_last_interaction()
    delta_seconds = (datetime.now() - last_active).total_seconds()
    
    print(f"[Scheduler] Checking inactivity... Delta: {delta_seconds}s")
    
    if delta_seconds > 7200: # 120 minutes (Global inactivity for now)
        print("[Scheduler] Inactivity detected. Triggering thought cycle for ALL users.")
        # We need a db session here. 
        # Since this is a job, we create a new session
        db = next(get_db())
        try:
            # Multi-user support
            users = db.query(models.User).all()
            for user in users:
                print(f"[Scheduler] Thinking for User {user.id} ({user.email})...")
                thought_service.generate_thought_cycle(db, user_id=user.id) 
        except Exception as e:
            print(f"[Scheduler] Error in thought cycle: {e}")
        finally:
            db.close()

@app.on_event("startup")
def startup_event():
    # Initialize scheduler
    # Run every 30 minutes = 1800 seconds
    scheduler.add_job(check_inactivity_and_think, 'interval', minutes=30)
    scheduler.start()
    print("[System] APScheduler started.")

# --- AUTH ---

@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": f"fake_token_{user.id}", 
        "token_type": "bearer",
        "user_id": user.id
    }

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deletes a user and all their associated data (messages, files) via Cascade.
    """
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}