import sys
import os

# Ensure we can import backend modules if running as script from backend/
# But best to run as `python -m backend.verify_memory` from parent.

from backend.database import SessionLocal, engine
from backend import models, crud, schemas

def verify():
    # Init tables
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if vector column exists by trying to add a message with vector
        print("Testing DB Schema & Vector Generation...")
        try:
            msg = crud.create_message(db, 1, schemas.MessageCreate(role="user", content="Test Vector Memory"))
            if msg.vector is None:
                print("[X] Message saved but VECTOR is None. Check VectorService or DB Schema.")
            else:
                print(f"[OK] Message saved with Vector! Size: {len(msg.vector)} bytes")
        except Exception as e:
            print(f"[X] Error saving message (likely DB Schema mismatch): {e}")
            return

        # Test Semantic Retrieval
        print("\nTesting Hybrid Retrieval...")
        # 1. Insert seed data
        seeds = [
            ("user", "Me gusta la pizza de pepperoni"),
            ("user", "El sol es una estrella"),
            ("user", "Python es un lenguaje de programacion"),
            ("user", "Hoy es martes"),
            ("user", "Mi color favorito es el azul")
        ]
        for role, content in seeds:
            crud.create_message(db, 1, schemas.MessageCreate(role=role, content=content))
        
        # 2. Query
        query = "Que me gusta comer?"
        print(f"Query: '{query}'")
        context = crud.get_hybrid_context(db, 1, query, limit_semantic=2, limit_recent=2)
        
        print(f"Result ({len(context)} messages):")
        for m in context:
            print(f" - [{m.role}] {m.content} (ID: {m.id})")
            
        # Check if 'pizza' is finding 'pizza'
        has_pizza = any("pizza" in m.content.lower() for m in context)
        if has_pizza:
             print("[OK] Semantic Retrieval Successful (Found 'pizza')")
        else:
             print("[WARN] Semantic Retrieval might be weak or failed.")

    finally:
        db.close()

if __name__ == "__main__":
    verify()
