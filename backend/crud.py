from sqlalchemy.orm import Session
from . import models, schemas
from .security import hash_password
from datetime import datetime, timedelta

# --- USER OPERATIONS ---
def create_user(db: Session, user: schemas.UserCreate):
    hashed_pass = hash_password(user.password)
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_pass
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

# --- FILE OPERATIONS (Legacy/File Storage) ---
def create_conversation_file(db: Session, user_id: int, filename: str, filepath: str):
    db_file = models.ConversationFile(
        user_id=user_id,
        filename=filename,
        filepath=filepath
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_user_files(db: Session, user_id: int):
    return db.query(models.ConversationFile).filter(models.ConversationFile.user_id == user_id).all()

def get_file_by_id(db: Session, file_id: int):
    return db.query(models.ConversationFile).filter(models.ConversationFile.id == file_id).first()

def delete_file(db: Session, db_file: models.ConversationFile):
    db.delete(db_file)
    db.commit()
    return True

# --- CHAT/MESSAGE OPERATIONS (New) ---
import numpy as np
from .app.services.vector_service import vector_service

def create_message(db: Session, user_id: int, message: schemas.MessageCreate):
    # Generate embedding
    embedding_bytes = vector_service.generate_embedding(message.content)
    
    db_message = models.Message(
        user_id=user_id,
        role=message.role,
        content=message.content,
        audio_path=message.audio_path,
        vector=embedding_bytes
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_history(db: Session, user_id: int, limit: int = 50):
    return db.query(models.Message).filter(models.Message.user_id == user_id).order_by(models.Message.created_at.asc()).limit(limit).all()

def get_hybrid_context(db: Session, user_id: int, query_text: str, limit_semantic: int = 3, limit_recent: int = 5):
    """
    Retrieves a hybrid context:
    1. Top 'limit_semantic' semantically relevant items (Messages + Thoughts).
    2. Last 'limit_recent' messages from immediate history.
    """
    # 1. Get recent messages (Immediate Context)
    recent_messages = db.query(models.Message)\
        .filter(models.Message.user_id == user_id)\
        .order_by(models.Message.created_at.desc())\
        .limit(limit_recent)\
        .all()
    recent_messages.reverse() # Restore chronological order

    # 2. Get semantic Search (Messages + Thoughts)
    query_vector = vector_service.generate_embedding(query_text)
    
    # A. Messages
    all_messages = db.query(models.Message)\
        .filter(models.Message.user_id == user_id)\
        .filter(models.Message.vector != None)\
        .all()
        
    scored_items = []
    
    for msg in all_messages:
        # Exclude recent messages from semantic search to avoid redundancy if overlap
        if msg in recent_messages:
            continue
            
        score = vector_service.calculate_similarity(query_vector, msg.vector)
        scored_items.append({
            "score": score,
            "type": "message",
            "obj": msg,
            "content": f"{msg.role}: {msg.content}"
        })

    # B. Thoughts
    all_thoughts = db.query(models.Thought)\
        .filter(models.Thought.user_id == user_id)\
        .filter(models.Thought.vector != None)\
        .all()
        
    for thought in all_thoughts:
        score = vector_service.calculate_similarity(query_vector, thought.vector)
        scored_items.append({
            "score": score,
            "type": "thought",
            "obj": thought,
            "content": f"[PENSAMIENTO INTERNO]: {thought.content}"
        })
    
    # Sort by score
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    
    # Filter by relevance (>0.75) and take top N
    semantic_limit_threshold = 0.75
    top_semantic = [item for item in scored_items if item["score"] > semantic_limit_threshold][:limit_semantic]
    
    # Fallback Strategy: If query is short/empty or no relevant semantic results found
    # Include the last thought if it's recent (< 24h)
    if (not query_text or len(query_text) < 5 or not top_semantic):
         last_thought = db.query(models.Thought)\
             .filter(models.Thought.user_id == user_id)\
             .order_by(models.Thought.created_at.desc())\
             .first()
         
         if last_thought:
             # Check if within last 24h
             if last_thought.created_at > datetime.utcnow() - timedelta(hours=24):
                 # Check if not already in top_semantic (unlikely if empty, but good practice)
                 if not any(item["obj"] == last_thought for item in top_semantic):
                     top_semantic.append({
                        "score": 1.0, # Forced high score
                        "type": "thought",
                        "obj": last_thought,
                        "content": f"[PENSAMIENTO INTERNO]: {last_thought.content}"
                     })

    # 3. Construct Final Semantic List (as list of objects/synthetic messages)
    semantic_results = []
    
    # Helper class for localized Synthetic Messages
    class SyntheticMessage:
        def __init__(self, role, content):
            self.role = role
            self.content = content

    for item in top_semantic:
        if item["type"] == "message":
            semantic_results.append(item["obj"]) 
        else:
            # Thoughts -> System role to ensure high priority/instruction following
            semantic_results.append(SyntheticMessage(role="system", content=item["content"]))
            
    return {
        "recent": recent_messages,
        "semantic": semantic_results
    }

def clear_chat_history(db: Session, user_id: int):
    db.query(models.Message).filter(models.Message.user_id == user_id).delete()
    db.commit()
    return True

# --- USER PREFERENCE OPERATIONS ---
def upsert_user_preference(db: Session, user_id: int, content: str, category: str):
    """
    Inserts or updates a user preference.
    Checks for semantic similarity to avoid duplicates if dynamic.
    """
    # Generate vector if dynamic
    vector = None
    if category == 'dynamic':
        vector = vector_service.generate_embedding(content)
        
        # Check for existing similar preference to update/deduplicate
        # For now, simple check: if we have a very high similarity, update it.
        # Or if "static", check by content equality or strict category uniqueness if applicable?
        # Requirement: "No guardes la misma preferencia múltiples veces; si el contenido es similar, actualiza".
        
        existing_prefs = db.query(models.UserPreference)\
            .filter(models.UserPreference.user_id == user_id)\
            .filter(models.UserPreference.category == 'dynamic')\
            .filter(models.UserPreference.vector != None)\
            .all()
            
        best_match = None
        best_score = 0.85 # Threshold
        
        for pref in existing_prefs:
            score = vector_service.calculate_similarity(vector, pref.vector)
            if score > best_score:
                best_score = score
                best_match = pref
        
        if best_match:
            # Update existing
            best_match.content = content
            best_match.vector = vector
            # best_match.created_at = datetime.utcnow() # Optional update timestamp
            db.commit()
            db.refresh(best_match)
            return best_match

    # If static, maybe check for exact content or if we want to allow multiple static items?
    # Usually static items are "Name is Bob", "Don't use emojis".
    # If we have "Name is Bob" and then "Name is Alice", maybe we should just add it?
    # Or if category is static, maybe we assume they are unique instructions?
    # Let's just add them for now unless exact match.
    
    if category == 'static':
        # Simple exact match check to avoid literal duplicates
        existing = db.query(models.UserPreference)\
            .filter(models.UserPreference.user_id == user_id)\
            .filter(models.UserPreference.category == 'static')\
            .filter(models.UserPreference.content == content)\
            .first()
        if existing:
            return existing

    new_pref = models.UserPreference(
        user_id=user_id,
        category=category,
        content=content,
        vector=vector
    )
    db.add(new_pref)
    db.commit()
    db.refresh(new_pref)
    return new_pref

def get_user_profile(db: Session, user_id: int, query_text: str = "") -> str:
    """
    Returns a formatted string of the user profile:
    - All 'static' preferences.
    - Top 3 'dynamic' preferences relevant to query_text.
    """
    # 1. Get Static
    static_prefs = db.query(models.UserPreference)\
        .filter(models.UserPreference.user_id == user_id)\
        .filter(models.UserPreference.category == 'static')\
        .all()
        
    # 2. Get Dynamic (Top 3)
    dynamic_content = []
    if query_text:
        query_vector = vector_service.generate_embedding(query_text)
        
        dynamic_prefs = db.query(models.UserPreference)\
            .filter(models.UserPreference.user_id == user_id)\
            .filter(models.UserPreference.category == 'dynamic')\
            .filter(models.UserPreference.vector != None)\
            .all()
            
        scored = []
        for pref in dynamic_prefs:
            score = vector_service.calculate_similarity(query_vector, pref.vector)
            scored.append((score, pref))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        top_dynamic = [pref for score, pref in scored[:3]]
        dynamic_content = [f"- {p.content}" for p in top_dynamic]
    else:
        # If no query, maybe return recent 3?
        # Or just empty? Prompt says "recuperada por relevancia".
        # If no query (e.g. activation without text?), maybe nothing.
        pass

    # Format Output
    profile_lines = ["[PERFIL DEL USUARIO]"]
    
    if static_prefs:
        profile_lines.append("Datos Permanentes:")
        for p in static_prefs:
            profile_lines.append(f"- {p.content}")
            
    if dynamic_content:
        profile_lines.append("Datos Relevantes:")
        profile_lines.extend(dynamic_content)
        
    if len(profile_lines) == 1:
        return "" # No profile info
        
    return "\n".join(profile_lines)
