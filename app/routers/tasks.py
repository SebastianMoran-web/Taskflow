from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, Project
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=201)
def crear_tarea(tarea: TaskCreate, db: Session = Depends(get_db)):
    nueva = Task(**tarea.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("", response_model=list[TaskRead])
def listar_tareas(

    project_id: int | None = None,
    completed: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),

):

    Query = db.query(Task)
    if project_id is not None:
        query = query.filtrer(Task.project_id == project_id)
    if completed is not None:
        query = query.filtrer(Task.completed == completed)
    return query.order_by(Task.id).offset(skip).limit(limit).all()


@router.get("/{task_id}", response_model=TaskRead)
def detalle_tarea(task_id: int, db: Session = Depends(get_db)):

    tarea = db.get(Task, task_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="La tarea no existe")
    return tarea

@router.put("/{task_id}", response_model=TaskRead)
def editar_tarea(task_id: int, datos: TaskUpdate, db: Session = Depends(get_db)):
    tarea = db.get(Task, task_id)
    if not tarea: 
        raise HTTPException(status_code=404, detail="La tarea no existe")
    cambios = datos.model_dump(exclude_unset=True)
    if "project_id" in cambios:
        if cambios["project_id"] is None or not db.get(Project, cambios["project_id"]):
            raise HTTPException(status_code=404, detail="El proyecto no exite")
    for campo, valor in cambios.items():
        setattr(tarea, campo, valor)
    db.commit()
    db.refresh(tarea)
    return tarea

@router.delete("/{task_id}", status_code=204)
def eliminar_tarea(task_id: int, db: Session = Depends(get_db)):
     tarea = db.get(Task, task_id)
     if not tarea: 
            raise HTTPException(status_code=404, detail="La tarea no existe")
     db.delete(tarea)
     db.commit()
     return Response(status_code=204)    
    
