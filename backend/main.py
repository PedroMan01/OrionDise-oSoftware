from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import os

import models, crud, schemas
from database import engine, get_db
from security import verify_password
from app.routes import router as app_router
from app.services import thought_service
from app.global_state import global_state
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Initialize Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orion Assistant API")

# --- CORS ---
# --- CORS ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://100.76.72.19:5173", # Mobile/LAN access
    "*" 
]

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
# --- SCHEDULER ---
scheduler = AsyncIOScheduler()
import random # Local import to avoid top-level clutter or add to top

def check_inactivity_and_think():
    """
    Dynamic Scheduler:
    Checks for inactivity and triggers thoughts based on probability and eligibility.
    Run every 20 minutes.
    """
    print(f"[Scheduler] Running periodic check...")
    
    # Create DB Session
    db = next(get_db())
    try:
        # 1. Eligibility Check (Quota & Safety)
        if not thought_service.is_eligible_for_thought(db):
            print("[Scheduler] Thought eligibility check FAILED (Quota exceeded). Aborting.")
            return

        # 2. Inactivity Check
        last_active = global_state.get_last_interaction()
        delta_seconds = (datetime.now() - last_active).total_seconds()
        delta_minutes = delta_seconds / 60
        
        print(f"[Scheduler] Inactivity: {delta_minutes:.1f} minutes")
        
        # 3. Check for Pending Items (High Priority)
        # Using a direct query or helper
        pending_count = crud.get_pending_reflections(db) # Returns list, so len()
        # Wait, crud.get_pending_reflections returns a list of objects based on previous file view
        is_pending = len(pending_count) > 0 if isinstance(pending_count, list) else False
        
        # 4. Probability Logic
        probability = 0.0
        force = False
        
        if is_pending:
            probability = 1.0
            force = True
            print("[Scheduler] Pending items detected. Priority: MAX.")
        elif delta_minutes < 30:
            probability = 0.05 # 5% chance if very active
        elif 30 <= delta_minutes < 120:
            probability = 0.30 # 30% chance
        else:
             # > 120 minutes
             probability = 1.0
             
        # 5. Dice Roll
        roll = random.random()
        print(f"[Scheduler] Probability: {probability*100}% | Roll: {roll:.2f}")
        
        if roll < probability or force:
            print("[Scheduler] Triggering Thought Cycle!")
            thought_service.generate_thought_cycle(db, user_id=None, force=force)
        else:
            print("[Scheduler] Skipped based on dice roll.")

    except Exception as e:
        print(f"[Scheduler] Error in thought cycle: {e}")
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    # Initialize scheduler
    # Run every 20 minutes = 1200 seconds
    scheduler.add_job(check_inactivity_and_think, 'interval', minutes=20)
    scheduler.start()
    print("[System] APScheduler started (Interval: 20m).")

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