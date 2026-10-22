from datetime import datetime

from fastapi import APIRouter

from app.schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(project: ProjectCreate):
    return ProjectRead(
        id=1,
        created_at=datetime.now(),
        name=project.name,
        description=project.description,
    )

