from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def get_current_user(
    x_user_id: int | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Falta la cabecera X-User-Id")
    user = db.get(User, x_user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no válido")
    return user

def pagination_params(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    return {"skip": skip, "limit": limit}