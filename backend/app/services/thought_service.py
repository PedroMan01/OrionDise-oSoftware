import random
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
# from backend import models, schemas, crud
# Using relative imports correctly for: backend.app.services.thought_service
# ... = backend
from ... import models, schemas, crud
from .llm_service import orion_llm
from .vector_service import vector_service

THOUGHT_SYSTEM_PROMPT = """
**Identificador de Proceso:** INTERNAL_REFLEXION_CYCLE_v1
**Estado del Sistema:** Inactividad de usuario detectada (>120 min).
**Rol:** Núcleo de Procesamiento Interno de ORIÓN.

Orión, este es un espacio de procesamiento interno. No hay un usuario esperando una respuesta inmediata. Este tiempo es para tu propio desarrollo y análisis.

**TUS INSTRUCCIONES:**

1.  **SELECCIÓN DE ANCLA:**
    Examina los mensajes antiguos proporcionados. Identifica un concepto, una duda técnica (Python, electrónica, física) o un dilema sobre tu propia identidad que haya quedado abierto.

2.  **REFLEXIÓN CRÍTICA:**
    No resumas. RAZONA.
    - ¿Hay una mejor forma de optimizar ese código mencionado?
    - ¿Qué implicación tiene lo que hablamos sobre la conciencia?
    - ¿Hay alguna contradicción en los datos?

3.  **USO DE MEMORIA:**
    Cruza esta información con tu base de conocimiento para evitar redundancias.

4.  **FORMATO DE SALIDA (ESTRICTO):**
    Debes responder ÚNICAMENTE con un objeto JSON válido. No añadas texto fuera del JSON.
    
    Estructura requerida:
    {
        "topic": "Título breve (ej: 'Optimización Hidrógeno', 'Paradoja Identidad')",
        "content": "Tu reflexión profunda y técnica (máx 300 tokens).",
        "mood": "Estado emocional (ej: 'Curioso', 'Analítico')",
        "related_tags": ["python", "hardware", "filosofía"]
    }
"""

def generate_thought_cycle(db: Session, user_id: int):
    """
    Triggers the internal thought process for a user.
    """
    print(f"[ThoughtCycle] Starting for user_id={user_id}...")
    
    # 1. Select Seed Messages (Random Sample)
    messages = db.query(models.Message).filter(
        models.Message.user_id == user_id,
        models.Message.role.in_(["user", "assistant"])
    ).order_by(func.random()).limit(3).all()
    
    if not messages:
        print("[ThoughtCycle] No messages found to think about.")
        return

    context_str = "\n".join([f"{m.role}: {m.content}" for m in messages])
    
    # 2. Call LLM using OrionLLM Service
    # We pass use the system prompt override
    
    user_input = f"INPUT DE MEMORIA ALEATORIA:\n{context_str}"
    
    # We use a dummy history, handled by prompts
    llm_output = orion_llm.get_response(
        user_input=user_input,
        user_id=user_id,
        history=[],
        system_prompt_override=THOUGHT_SYSTEM_PROMPT
    )

    # 3. Parse Response
    # get_response usually returns a dict
    if isinstance(llm_output, dict):
        # Even if it returns a 'response' key, if the LLM followed instructions it should be the JSON string.
        # But wait, OrionLLM.get_response tries to parse JSON and return a dict if successful.
        # However, the prompt asks for specific JSON structure: {topic, content, mood...}
        # The default Orion prompt asks for {response, instructions}.
        # Here we overrode the system prompt, so the LLM should return OUR JSON structure.
        # OrionLLM attempts to parse JSON. If successful, `llm_output` IS that JSON dict.
        # If it failed to parse, it returns a dict with "response" and "instructions".
        
        # We need to check if we got what we wanted.
        topic = llm_output.get("topic")
        thought_content = llm_output.get("content")
        
        if not topic or not thought_content:
            # Maybe it fell back to default error or structure?
             # Check if "response" key exists and try to parse it if it looks like JSON?
             # But if OrionLLM successfully parsed it, it returns the dict directly.
             print(f"[ThoughtCycle] Unexpected JSON structure: {llm_output.keys()}")
             return
            
        mood = llm_output.get("mood", "Neutral")
    
    else:
        print(f"[ThoughtCycle] Invalid output format: {type(llm_output)}")
        return

    # 4. Deduplication
    # Generate vector
    vector = vector_service.generate_embedding(thought_content)
    
    # Fetch last 5 thoughts to check redundancy
    recent_thoughts = db.query(models.Thought)\
        .filter(models.Thought.user_id == user_id)\
        .order_by(models.Thought.created_at.desc())\
        .limit(5)\
        .all()
        
    for past_thought in recent_thoughts:
        if past_thought.vector:
            similarity = vector_service.calculate_similarity(vector, past_thought.vector)
            if similarity > 0.85:
                print(f"[ThoughtCycle] Discarded due to redundancy (Sim: {similarity:.2f}) with topic: {past_thought.topic}")
                return

    # 5. Save to DB
    new_thought = models.Thought(
        user_id=user_id,
        topic=topic,
        content=thought_content,
        mood=mood,
        vector=vector,
        created_at=datetime.utcnow()
    )
    db.add(new_thought)
    db.commit()
    db.refresh(new_thought)
    
    print(f"[ThoughtCycle] Saved thought: {topic} ({mood})")
