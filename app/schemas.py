from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProjectCreate(BaseModel):

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

    id: int = Field(..., gt=0, description="Identificador único del proyecto")
    created_at: datetime = Field(..., description="Fecha y hora de creación")

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):

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


class TaskRead(TaskCreate):

    id: int = Field(..., gt=0, description="Identificador único de la tarea")
    completed: bool = Field(default=False, description="Estado de la tarea")
    created_at: datetime = Field(..., description="Fecha y hora de creación")

    model_config = ConfigDict(from_attributes=True)