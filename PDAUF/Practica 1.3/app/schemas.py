from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Datos que envía el cliente para crear una tarea"""

    title: str = Field(
        min_length=1,
        max_length=100,
        description="Título de la tarea (1-100)",
    )
    description: str | None = None
    project_id: int


class TaskRead(TaskCreate):
    """Datos que devuelve la API"""

    id: int
    completed: bool
    created_at: datetime


class ProjectCreate(BaseModel):
    """Datos para crear un proyecto"""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Nombre del proyecto",
    )
    description: str | None = None


class ProjectRead(ProjectCreate):
    """Proyecto devuelto por la API"""

    id: int
    created_at: datetime
