import os
from datetime import datetime, timedelta
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

# Configuración básica de seguridad
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "una_clave_secreta_muy_segura_para_desarrollo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # El token durará 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Encripta la contraseña antes de guardarla en la BD."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con la encriptada."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Genera un token JWT para el usuario."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    """Decodifica el token y extrae la información."""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Retorna el diccionario con los datos del usuario (ej: {"sub": business_id})
    except (ExpiredSignatureError, InvalidTokenError):
        return None
