from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas
from app.services.llm_service import orion_llm
import app.services.thought_service as thought_service
from app.services.audio_service import audio_service
from app.global_state import global_state
from datetime import datetime, timedelta

router = APIRouter()

class ChatRequest(BaseModel):
    mensaje: str
    user_id: int = 1 # Default to 1 for now if not provided, but ideally requires auth

@router.post("/activar")
async def chat_interaction(data: ChatRequest, db: Session = Depends(get_db)):
    """
    Main interaction point. 
    1. Saves User message.
    2. Gets LLM response.
    3. Generates Audio.
    4. Saves Assistant message.
    5. Returns text + audio URL.
    """
    user_id = data.user_id
    user_text = data.mensaje

    # 0. Update Activity
    global_state.update_interaction()

    # 1. Save User Message
    msg_in = schemas.MessageCreate(role="user", content=user_text)
    crud.create_message(db, user_id, msg_in)

    # 2. Get History & LLM Response (Hybrid: Semantic + Recent)
    # Fetch hybrid context
    # Fetch hybrid context
    context_data = crud.get_hybrid_context(db, user_id, user_text, limit_semantic=3, limit_recent=5)
    
    # Get User Profile
    user_profile = crud.get_user_profile(db, user_id, user_text)
    
    llm_history = []
    
    # 1. Perfil de Usuario (System)
    if user_profile:
        llm_history.append({"role": "system", "content": user_profile})

    # 1.5 INVESTIGACIONES RECIENTES
    recent_research = crud.get_formatted_knowledge(db, limit=5)
    if recent_research:
         research_text = f"[INVESTIGACIONES RECIENTES]\n{recent_research}"
         llm_history.append({"role": "system", "content": research_text})

    # 2. Contexto Semántico (Pensamientos y Recuerdos)
    for msg in context_data["semantic"]:
         llm_history.append({"role": msg.role, "content": msg.content})
         
    # 3. Historial Reciente (Chat Inmediato)
    for msg in context_data["recent"]:
         if msg.content != user_text:
             llm_history.append({"role": msg.role, "content": msg.content})
    
    # Define callback for tools
    def upsert_callback(content, category):
        crud.upsert_user_preference(db, user_id, content, category)

    def reflection_callback(topic):
        crud.add_reflection_topic(db, topic)

    llm_output = orion_llm.get_response(user_text, user_id, llm_history, upsert_callback=upsert_callback, reflection_callback=reflection_callback)
    
    # Check if we got a dict (expected) or string (fallback)
    if isinstance(llm_output, dict):
        response_text = llm_output.get("response", "Error parsing response")
        instructions = llm_output.get("instructions", "")
    else:
        response_text = str(llm_output)
        instructions = ""

    # 3. Generate Audio with Instructions
    audio_file = await audio_service.generate_audio(response_text, user_id=user_id, instructions=instructions)
    # Return relative path so frontend can construct URL based on its connection (IP/VPN)
    audio_url = f"/audio/{audio_file}" if audio_file else None

    # 4. Save Assistant Message
    # Note: If tools were called, the LLM exchange already happened. We just save the final text response.
    msg_out = schemas.MessageCreate(role="assistant", content=response_text, audio_path=audio_file)
    crud.create_message(db, user_id, msg_out)

    return {
        "text": response_text,
        "audio_url": audio_url,
        "instructions": instructions
    }

# Endpoint for just retrieving history if needed
@router.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    return crud.get_chat_history(db, user_id)

@router.delete("/history/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(user_id: int, db: Session = Depends(get_db)):
    crud.clear_chat_history(db, user_id)
    return

from fastapi import File, UploadFile
import shutil
import os
from pathlib import Path

@router.post("/chat_audio")
async def chat_audio_interaction(
    file: UploadFile = File(...), 
    user_id: int = 1, # Should be Form(...) but sticking to simple query param or default for now
    db: Session = Depends(get_db)
):
    """
    Receives audio file, transcribes it, and processes it as a chat message.
    """
    # 0. Update Activity
    global_state.update_interaction()

    # 1. Save temp file
    temp_filename = f"temp_{file.filename}"
    temp_path = Path("temp_audio")
    temp_path.mkdir(exist_ok=True)
    file_location = temp_path / temp_filename
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # 2. Transcribe
    transcribed_text = await audio_service.transcribe_audio(file_location)
    
    # Clean up temp file
    # file_location.unlink() # Keep it for debugging? Or delete. Let's delete to save space.
    try:
         os.remove(file_location)
    except:
         pass

    if not transcribed_text:
        raise HTTPException(status_code=400, detail="Could not transcribe audio")

    print(f"🎤 Transcription: {transcribed_text}")

    # 3. Process as normal chat
    # reusing the logic from chat_interaction roughly
    
    # Save User Message
    crud.create_message(db, user_id, schemas.MessageCreate(role="user", content=transcribed_text))

    # Get Hybrid Context
    # Get Hybrid Context
    context_data = crud.get_hybrid_context(db, user_id, transcribed_text, limit_semantic=5, limit_recent=5)
    
    # Get User Profile
    user_profile = crud.get_user_profile(db, user_id, transcribed_text)

    llm_history = []
    
    # 1. Perfil de Usuario
    if user_profile:
        llm_history.append({"role": "system", "content": user_profile})

    # 1.5 INVESTIGACIONES RECIENTES
    recent_research = crud.get_formatted_knowledge(db, limit=5)
    if recent_research:
         research_text = f"[INVESTIGACIONES RECIENTES]\n{recent_research}"
         llm_history.append({"role": "system", "content": research_text})

    # 2. Contexto Semántico
    for msg in context_data["semantic"]:
         llm_history.append({"role": msg.role, "content": msg.content})

    # 3. Historial Reciente
    for msg in context_data["recent"]:
        if msg.content != transcribed_text:
            llm_history.append({"role": msg.role, "content": msg.content})

    # Define callback
    def upsert_callback(content, category):
        crud.upsert_user_preference(db, user_id, content, category)

    def reflection_callback(topic):
        crud.add_reflection_topic(db, topic)

    # Get LLM Response
    llm_output = orion_llm.get_response(transcribed_text, user_id, llm_history, upsert_callback=upsert_callback, reflection_callback=reflection_callback)
    
    if isinstance(llm_output, dict):
        response_text = llm_output.get("response", "Error parsing response")
        instructions = llm_output.get("instructions", "")
    else:
        response_text = str(llm_output)
        instructions = ""

    # Generate Audio
    audio_file = await audio_service.generate_audio(response_text, user_id=user_id, instructions=instructions)
    audio_url = f"/audio/{audio_file}" if audio_file else None

    # Save Assistant Message
    crud.create_message(db, user_id, schemas.MessageCreate(role="assistant", content=response_text, audio_path=audio_file))

    return {
        "text": response_text,
        "audio_url": audio_url,
        "instructions": instructions,
        "transcription": transcribed_text
    }

# --- DEBUG ENDPOINTS ---
@router.post("/debug/force-think")
def force_think(db: Session = Depends(get_db)):
    """
    Triggers an immediate thought cycle (Priority/Forced).
    Useful for testing or manual intervention.
    """
    print("[Debug] Manual trigger: /debug/force-think")
    
    # We call generate_thought_cycle with force=True
    # The user_id is None for global agent thoughts
    thought_service.generate_thought_cycle(db, user_id=None, force=True)
    
    return {"status": "Ciclo de pensamiento forzado ejecutado."}
