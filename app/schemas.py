from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# Los schemas de Pydantic definen el contrato de datos de entrada/salida de la API.
# Se diferencian de los modelos de BD en que no gestionan la persistencia,
# sino la validación, tipado y serialización de la interfaz HTTP.


class ProjectCreate(BaseModel):
    """Schema de entrada para registrar un proyecto."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre del proyecto (entre 1 y 100 caracteres)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción opcional del proyecto"
    )


class ProjectRead(ProjectCreate):
    """Schema de salida con los datos del proyecto."""
    id: int = Field(..., gt=0, description="Identificador único del proyecto")
    created_at: datetime = Field(..., description="Fecha y hora de creación")

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    """Schema de entrada para registrar una tarea."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Título de la tarea (mínimo 1, máximo 100 caracteres)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción opcional de la tarea"
    )
    project_id: int = Field(
        ...,
        gt=0,
        description="ID del proyecto asociado (debe ser mayor a 0)"
    )
    category_id: Optional[int] = Field(
        None, gt=0, description="ID de la categoría (opcional)"
    )
    assignee_id: Optional[int] = Field(
        None, gt=0, description="ID del usuario responsable (opcional)"
    )


class TaskRead(TaskCreate):
    """Schema de salida con la tarea completa."""
    id: int = Field(..., gt=0, description="Identificador único de la tarea")
    completed: bool = Field(default=False, description="Estado de la tarea")
    created_at: datetime = Field(..., description="Fecha y hora de creación")

    model_config = ConfigDict(from_attributes=True)


class TaskPage(BaseModel):
    """Respuesta paginada de GET /tasks, con metadatos de paginación."""
    total: int
    skip: int
    limit: int
    items: list[TaskRead]


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=120)


class UserRead(UserCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectDetail(ProjectRead):
    tasks: list[TaskRead] = []


class ProjectSummary(BaseModel):
    """Contadores de tareas de un proyecto."""
    id: int
    name: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    project_id: int | None = None
    category_id: int | None = None
    assignee_id: int | None = None


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class CategoryDetail(CategoryRead):
    tasks: list[TaskRead] = []