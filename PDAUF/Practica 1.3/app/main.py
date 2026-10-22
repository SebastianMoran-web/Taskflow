from fastapi import FastAPI

from app.Routers import projects, system, tasks

tags_metadata = [
    {"name": "system", "description": "Estado y versión de la API"},
    {"name": "tasks", "description": "Gestión de tareas"},
    {"name": "projects", "description": "Gestión de proyectos"},
]

app = FastAPI(title="Taskflow API", openapi_tags=tags_metadata)

app.include_router(system.router)
app.include_router(tasks.router)
app.include_router(projects.router)
