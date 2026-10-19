from datetime import datetime
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    """Datos que envia el cliente para crear una tarea"""

    title: str = Field(

        min_length=1,
        max_length=100,
        description="Titulo de la tarea (1-100)"

    )

    description: str | None = None

    project_id: int

class TaskRead(TaskCreate):

    """Datos que devuelve la API"""

    id:int
    completed: bool
    created_at: datetime

class ProjectCreate(BaseModel):
    """Datos para crear un proyecto"""

    name: str = Field(

        min_length=1, 
        max_length=100,
        descriptio= "Nombre del proyecto"

    )

    description: str | None = None

class ProjectRead(ProjectCreate):
    """Proyecto devuelto por la API"""

    id: int
    create_at: datetime