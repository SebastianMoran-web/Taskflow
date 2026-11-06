from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryDetail, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _obtener(category_id: int, db: Session) -> Category:
    categoria = db.get(Category, category_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="La categoría no existe")
    return categoria


@router.get("", response_model=list[CategoryRead])
def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return db.query(Category).order_by(Category.id).offset(skip).limit(limit).all()


@router.get("/{category_id}", response_model=CategoryDetail)
def detalle_categoria(category_id: int, db: Session = Depends(get_db)):
    return _obtener(category_id, db)


@router.post("", response_model=CategoryRead, status_code=201)
def crear_categoria(datos: CategoryCreate, db: Session = Depends(get_db)):
    nueva = Category(**datos.model_dump())
    db.add(nueva)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")
    db.refresh(nueva)
    return nueva


@router.put("/{category_id}", response_model=CategoryRead)
def editar_categoria(category_id: int, datos: CategoryUpdate, db: Session = Depends(get_db)):
    categoria = _obtener(category_id, db)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(categoria, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")
    db.refresh(categoria)
    return categoria


@router.delete("/{category_id}", status_code=204)
def eliminar_categoria(category_id: int, db: Session = Depends(get_db)):
    categoria = _obtener(category_id, db)
    db.delete(categoria)  
    db.commit()
    return Response(status_code=204)