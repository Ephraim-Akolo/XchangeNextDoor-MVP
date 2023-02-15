from datetime import datetime, timedelta
from jose import JWTError, jwt
from .settings import settings

def create_access_token(data:dict):
    to_encode = data.copy()
    exp = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode['exp'] = exp
    return jwt.encode(to_encode, settings.jwt_secret_key, settings.jwt_algorithm)


