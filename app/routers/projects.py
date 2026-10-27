from fastapi import APIRouter
from app.schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def crear_proyecto(proyecto: ProjectCreate):
    return ProjectRead(id=1, name=proyecto.name, description=proyecto.description)