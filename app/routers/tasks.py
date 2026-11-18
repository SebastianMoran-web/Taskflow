from typing import Literal, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import pagination_params
from app.exceptions import NotFoundError
from app.models import Category, Project, Task, User
from app.schemas import TaskCreate, TaskPage, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise NotFoundError("Tarea", task_id, "TASK_NOT_FOUND")
    return task


def _check_refs(db: Session, project_id=None, category_id=None, assignee_id=None):
    """404 diferenciado según qué referencia no existe."""
    if project_id is not None and db.get(Project, project_id) is None:
        raise NotFoundError("Proyecto", project_id, "PROJECT_NOT_FOUND")
    if category_id is not None and db.get(Category, category_id) is None:
        raise NotFoundError("Categoría", category_id, "CATEGORY_NOT_FOUND")
    if assignee_id is not None and db.get(User, assignee_id) is None:
        raise NotFoundError("Usuario", assignee_id, "USER_NOT_FOUND")


@router.get("", response_model=TaskPage)
def list_tasks(
    project_id: Optional[int] = None,
    category_id: Optional[int] = None,
    completed: Optional[bool] = None,
    order_by: Literal["id", "title", "completed", "created_at"] = "id",
    page: dict = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    q = db.query(Task)
    if project_id is not None:
        q = q.filter(Task.project_id == project_id)
    if category_id is not None:
        q = q.filter(Task.category_id == category_id)
    if completed is not None:
        q = q.filter(Task.completed == completed)

    total = q.count()
    items = (
        q.order_by(getattr(Task, order_by))
        .offset(page["skip"])
        .limit(page["limit"])
        .all()
    )
    return {"total": total, "skip": page["skip"], "limit": page["limit"], "items": items}


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_task(db, task_id)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    _check_refs(db, data.project_id, data.category_id, data.assignee_id)
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = _get_task(db, task_id)
    changes = data.model_dump(exclude_unset=True)
    _check_refs(
        db,
        changes.get("project_id"),
        changes.get("category_id"),
        changes.get("assignee_id"),
    )
    for field, value in changes.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db.delete(_get_task(db, task_id))
    db.commit()