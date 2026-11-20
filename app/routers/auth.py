from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ConflictError
from app.models import User
from app.schemas import RefreshRequest, TokenResponse, UserCreate, UserRead
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    create_token,
    get_password_hash,
    revoked_refresh_tokens,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_scopes_for_role(role: str) -> list[str]:
    if role == "admin":
        return ["tasks:write", "projects:write"]
    return ["tasks:write"]


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise ConflictError("El nombre de usuario ya está registrado", "USERNAME_TAKEN")
    if db.query(User).filter(User.email == data.email).first():
        raise ConflictError("El email ya está registrado", "EMAIL_TAKEN")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()

    # Mensaje genérico: no revela si el usuario existe o si falló la contraseña
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scopes = _get_scopes_for_role(user.role)
    access_token = create_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )
    refresh_token = create_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido o revocado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti: str | None = payload.get("jti")
        username: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if not jti or not username or token_type != "refresh" or jti in revoked_refresh_tokens:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception

    revoked_refresh_tokens.add(jti)

    scopes = _get_scopes_for_role(user.role)
    new_access = create_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )
    new_refresh = create_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }