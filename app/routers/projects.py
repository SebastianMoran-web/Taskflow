from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead, ProjectDetail, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def crear_proyecto(proyecto: ProjectCreate, db: Session = Depends(get_db)):
    nuevo = Project(**proyecto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("", response_model=list[ProjectRead])

def listar_proyectos(

    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)

):
    return db.query(Project).order_by(Project.id).offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model= ProjectDetail)

def detalle_proyecto( project_id: int, db: Session = Depends(get_db)):

    proyecto = db.get(Project, project_id)

    if not proyecto:
        raise HTTPException(status_code=404, detail="El proyecto no existe")
    return proyecto


@router.put("/{project_id}", response_model= ProjectRead)

def editar_proyecto( project_id: int, datos: ProjectUpdate, db: Session = Depends(get_db)):

    proyecto = db.get(Project, project_id)

    if not proyecto:
        raise HTTPException(status_code=404, detail="El proyecto no existe")
    for campo, valor in datos.model_dump(exclude_unset=True).items():

        setattr(proyecto, campo, valor)
    db.commit()
    db.refresh(proyecto)
    return proyecto



@router.delete("/{project_id}", status_code=204)

def eliminar_proyecto( project_id: int, db: Session = Depends(get_db)):

    proyecto = db.get(Project, project_id)

    if not proyecto:
        raise HTTPException(status_code=404, detail="El proyecto no existe")
    db.delete(proyecto)
    db.commit()
    return proyecto



