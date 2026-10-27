from datetime import datetime
from fastapi import APIRouter
from app.schemas import TaskCreate, TaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=201)
def crear_tarea(tarea: TaskCreate):
    return TaskRead(
        id=1,
        completed=False,
        created_at=datetime.now(),
        title=tarea.title,
        description=tarea.description,
        project_id=tarea.project_id,
    )