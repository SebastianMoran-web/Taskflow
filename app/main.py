import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import projects, tasks, debug
from app.config import CORS_ORIGINS
from app.exceptions import register_exception_handlers
from app.middleware import process_time_middleware, request_id_middleware


logging.basicConfig(

    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s ]",

)

tags_metadata = [
    {"name": "tasks", "description": "Gestión de tareas"},
    {"name": "projects", "description": "Gestión de proyectos"},
    {"name": "debug", "description": "Solo pruebas de la practica 1.4"}
]

app = FastAPI(title="Taskflow API", openapi_tags=tags_metadata)

register_exception_handlers(app)

app.middleware("http")(process_time_middleware)
app.middleware("http")(request_id_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Process-Time", "X-Request-ID"],

)

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(debug.router, prefix="/api/v1")