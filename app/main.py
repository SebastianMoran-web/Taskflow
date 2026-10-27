from fastapi import FastAPI

from app.routers import projects, tasks

tags_metadata = [
    {"name": "tasks", "description": "Gestión de tareas"},
    {"name": "projects", "description": "Gestión de proyectos"},
]

app = FastAPI(title="Taskflow API", openapi_tags=tags_metadata)

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")