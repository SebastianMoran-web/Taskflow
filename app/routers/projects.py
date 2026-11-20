from fastapi import APIRouter, Depends, status,Security
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies import pagination_params, get_current_user
from app.exceptions import NotFoundError
from app.models import Project, Task, User
from app.schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectRead,
    ProjectSummary,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise NotFoundError("Proyecto", project_id, "PROJECT_NOT_FOUND")
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(page: dict = Depends(pagination_params), db: Session = Depends(get_db)):
    return (
        db.query(Project)
        .order_by(Project.id)
        .offset(page["skip"])
        .limit(page["limit"])
        .all()
    )


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    # selectinload carga las tareas en 1 consulta extra (evita el problema N+1)
    project = (
        db.query(Project)
        .options(selectinload(Project.tasks))
        .filter(Project.id == project_id)
        .first()
    )
    if project is None:
        raise NotFoundError("Proyecto", project_id, "PROJECT_NOT_FOUND")
    return project


@router.get("/{project_id}/summary", response_model=ProjectSummary)
def project_summary(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(db, project_id)
    total, done = (
        db.query(func.count(Task.id), func.coalesce(func.sum(Task.completed), 0))
        .filter(Task.project_id == project_id)
        .one()
    )
    done = int(done)
    return {
        "id": project.id,
        "name": project.name,
        "total_tasks": total,
        "completed_tasks": done,
        "pending_tasks": total - done,
    }


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["projects:write"]),
):
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["projects:write"]),
):
    project = _get_project(db, project_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["projects:write"]),
):
    db.delete(_get_project(db, project_id))
    db.commit()