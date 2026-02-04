from backend.database import SessionLocal
from sqlalchemy import text

try:
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    print("DATABASE_CHECK_SUCCESS")
except Exception as e:
    print(f"DATABASE_CHECK_ERROR: {e}")
finally:
    db.close()
