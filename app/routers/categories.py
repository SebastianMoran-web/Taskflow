from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies import pagination_params
from app.exceptions import ConflictError, NotFoundError
from app.models import Category, Task
from app.schemas import CategoryCreate, CategoryDetail, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise NotFoundError("Categoría", category_id, "CATEGORY_NOT_FOUND")
    return category


def _check_name_free(db: Session, name: str, exclude_id: Optional[int] = None):
    q = db.query(Category).filter(Category.name == name)
    if exclude_id is not None:
        q = q.filter(Category.id != exclude_id)
    if q.first() is not None:
        raise ConflictError(
            f"Ya existe una categoría llamada '{name}'", "CATEGORY_NAME_DUPLICATED"
        )


@router.get("", response_model=list[CategoryRead])
def list_categories(page: dict = Depends(pagination_params), db: Session = Depends(get_db)):
    return (
        db.query(Category)
        .order_by(Category.id)
        .offset(page["skip"])
        .limit(page["limit"])
        .all()
    )


@router.get("/{category_id}", response_model=CategoryDetail)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(Category)
        .options(selectinload(Category.tasks))
        .filter(Category.id == category_id)
        .first()
    )
    if category is None:
        raise NotFoundError("Categoría", category_id, "CATEGORY_NOT_FOUND")
    return category


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    _check_name_free(db, data.name)
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    category = _get_category(db, category_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("name") is not None:
        _check_name_free(db, changes["name"], exclude_id=category_id)
    for field, value in changes.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = _get_category(db, category_id)
    n = db.query(func.count(Task.id)).filter(Task.category_id == category_id).scalar()
    if n:
        # Bloqueo: no se borra una categoría en uso (ver models.py)
        raise ConflictError(
            f"No se puede borrar la categoría {category_id}: tiene {n} tarea(s) "
            "asociada(s). Reasígnalas o bórralas primero.",
            "CATEGORY_IN_USE",
        )
    db.delete(category)
    db.commit()