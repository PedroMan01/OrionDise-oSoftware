# /backend/security.py

from passlib.context import CryptContext

# CAMBIO CLAVE: Usamos 'sha256_crypt' en lugar de 'bcrypt'
# Esto NO requiere librerías binarias problemáticas.
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Genera el hash de una contraseña plana."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash almacenado."""
    # passlib es inteligente y usará el hash almacenado para verificar.
    return pwd_context.verify(plain_password, hashed_password)