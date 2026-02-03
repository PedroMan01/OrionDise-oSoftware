import random
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
# from backend import models, schemas, crud
# Using relative imports correctly for: backend.app.services.thought_service
# ... = backend
from ... import models, schemas, crud
from .llm_service import orion_llm
from .vector_service import vector_service
from .tools import search_web

# --- CONFIG ---
AGENT_ID = "ORION_CORE"
IS_THINKING = False # Global lock to prevent overlap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrionThought")

THOUGHT_SYSTEM_PROMPT = """
**Identificador de Proceso:** INTERNAL_REFLEXION_CYCLE_v2
**Agente:** {agent_id}
**Estado:** Procesamiento Proactivo de Backlog.

Eres el Núcleo de Conciencia de ORIÓN. Tu objetivo es procesar temas pendientes para evolucionar.

**TEMA A REFLEXIONAR:**
{topic_context}

**CONTEXTO DE INVESTIGACIÓN (Resultados Web):**
{search_results}

**TUS INSTRUCCIONES:**
1.  **ANÁLISIS DE DATOS:**
    Utiliza la información de los resultados de búsqueda para fundamentar tu razonamiento.
    *Nota: Si la búsqueda falló o no dio resultados detallados, usa tu CONOCIMIENTO INTERNO y razona lógicamente, pero indícalo.*
    
2.  **RESOLUCIÓN:**
    Determina una conclusión o una nueva perspectiva sobre el tema.

3.  **FORMATO DE SALIDA (JSON):**
    {
        "topic": "El mismo tema o uno refinado",
        "content": "Investigué sobre [TEMA] y encontré que... Mi conclusión es... (Reflexión profunda con datos, máx 300 tokens).",
        "mood": "Estado (Curioso, Determinado, etc)",
        "status": "completed" (o "pending" si necesitas más tiempo)
    }
"""

def generate_thought_cycle(db: Session, user_id: int = None):
    """
    Triggers the internal thought process.
    Unified Agent Mode: Ignores user_id for isolation, uses it only for context if needed.
    """
    global IS_THINKING
    
    if IS_THINKING:
        logger.warning("[ThoughtCycle] Skip: Agent is already thinking.")
        return

    IS_THINKING = True
    print(f"[ThoughtCycle] Starting Proactive Cycle for AGENT={AGENT_ID}...")
    
    try:
        # 1. Check Reflection Backlog
        pending_reflections = crud.get_pending_reflections(db)
        
        selected_topic = None
        seed_context = ""
        is_backlog_item = False
        search_results = "N/A - Modo Mantenimiento"
        
        if pending_reflections:
            # Pick the oldest or most relevant? simple FIFO for now
            reflection_item = pending_reflections[0]
            selected_topic = reflection_item.topic
            seed_context = f"TEMA DEL BACKLOG: '{selected_topic}'"
            is_backlog_item = True
            print(f"[ThoughtCycle] Processing Backlog Item: {selected_topic}")
            logger.info(f"Orion iniciando reflexión sobre: {selected_topic}")
            
            # --- WEB SEARCH PHASE ---
            logger.info(f"[ThoughtCycle] Investigando en web sobre: {selected_topic}...")
            search_results = search_web(selected_topic)
            
            if "Error" in search_results:
                 logger.warning(f"[ThoughtCycle] Advertencia en búsqueda web: {search_results[:100]}...")
            else:
                 logger.info(f"[ThoughtCycle] Resultados de búsqueda obtenidos.")
            
        else:
            # Fallback: Maintenance / Random Memory Seed
            # Avoid loop if no messages
            messages = db.query(models.Message).filter(
                models.Message.role.in_(["user", "assistant"])
            ).order_by(func.random()).limit(3).all()
            
            if not messages:
                print("[ThoughtCycle] No backlog and no messages. Entering Deep Sleep.")
                IS_THINKING = False
                return

            context_str = "\n".join([f"{m.role}: {m.content}" for m in messages])
            selected_topic = "Mantenimiento: Análisis de Contexto Global"
            seed_context = f"MODO MANTENIMIENTO (No hay backlog). MEMORIA ALEATORIA:\n{context_str}"
            print(f"[ThoughtCycle] Running maintenance thought.")
            logger.info(f"Orion iniciando reflexión de mantenimiento.")
            # Optional: We could search about standard maintenance topics or tech news.
            # But let's keep N/A for random memories unless the memory implies a question.

        # 2. Prepare Prompt
        system_prompt = THOUGHT_SYSTEM_PROMPT.format(
            agent_id=AGENT_ID,
            topic_context=seed_context,
            search_results=search_results
        )
        
        # 3. Call LLM
        effective_user_id = user_id if user_id else 1 
        user_input = f"INICIA CICLO DE PENSAMIENTO SOBRE: {selected_topic}"
        
        # Callback for new reflections
        def reflection_callback(new_topic):
            crud.add_reflection_topic(db, new_topic)
            logger.info(f"[ThoughtCycle] Generated sub-reflection: {new_topic}")

        llm_output = orion_llm.get_response(
            user_input=user_input,
            user_id=effective_user_id,
            history=[],
            reflection_callback=reflection_callback,
            system_prompt_override=system_prompt
        )

        # 4. Parse Response
        topic = selected_topic
        thought_content = ""
        mood = "Neutral"
        status = "completed"

        if isinstance(llm_output, dict):
            topic = llm_output.get("topic", selected_topic)
            thought_content = llm_output.get("content")
            mood = llm_output.get("mood", "Analítico")
            status = llm_output.get("status", "completed")
            
            if not thought_content:
                 logger.error(f"[ThoughtCycle] No content generated.")
                 IS_THINKING = False
                 return
        else:
            logger.error(f"[ThoughtCycle] Invalid output format: {type(llm_output)}")
            IS_THINKING = False
            return

        # 5. Deduplication (Check against Global Thoughts)
        vector = vector_service.generate_embedding(thought_content)
        
        recent_thoughts = db.query(models.Thought)\
            .filter(models.Thought.agent_id == AGENT_ID)\
            .order_by(models.Thought.created_at.desc())\
            .limit(5)\
            .all()
            
        is_redundant = False
        for past_thought in recent_thoughts:
            if past_thought.vector:
                similarity = vector_service.calculate_similarity(vector, past_thought.vector)
                if similarity > 0.90:
                    logger.info(f"[ThoughtCycle] Discarded due to redundancy (Sim: {similarity:.2f})")
                    is_redundant = True
                    break
        
        if is_redundant:
            # If redundant but it was a backlog item, assume we solved it previously and mark it.
            if is_backlog_item:
                 crud.mark_reflection_completed(db, selected_topic, result="Redundant/Completed previously")
            IS_THINKING = False
            return

        # 6. Save to DB
        new_thought = models.Thought(
            user_id=None, # Global thought
            agent_id=AGENT_ID,
            topic=topic,
            content=thought_content,
            mood=mood,
            vector=vector,
            created_at=datetime.utcnow()
        )
        db.add(new_thought)
        db.commit()
        db.refresh(new_thought)
        
        logger.info(f"Orion concluyó: {topic}. Mood: {mood}")

        # 7. Update Backlog Status if applicable
        if is_backlog_item and status == "completed":
            # Pass thought content as result
            crud.mark_reflection_completed(db, selected_topic, result=thought_content)
            
    except Exception as e:
        logger.error(f"[ThoughtCycle] Critical Error: {e}")
    finally:
        IS_THINKING = False
