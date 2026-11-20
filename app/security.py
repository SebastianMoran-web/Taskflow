from datetime import datetime, timedelta, timezone
import uuid
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "RowletDisorder"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

revoked_refresh_tokens: set[str] = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: timedelta, token_type: str = "access") -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "type": token_type,
        "jti": str(uuid.uuid4()), 
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)