import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.config import CORS_ORIGINS
from app.database import Base, engine
from app.exceptions import register_exception_handlers
from app.middleware import process_time_middleware, request_id_middleware
from app.routers import categories, debug, projects, tasks, users
# Formato del log del servidor: aquí queda el detalle completo de los errores.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

Base.metadata.create_all(bind=engine)

tags_metadata = [
    {"name": "tasks", "description": "Gestión de tareas"},
    {"name": "projects", "description": "Gestión de proyectos"},
    {"name": "users", "description": "Gestión de usuarios"},
    {"name": "debug", "description": "Solo pruebas de la práctica 1.4 (eliminar en producción)"},
    {"name": "categories", "description": "Gestión de categorías"},
]

app = FastAPI(title="Taskflow API", openapi_tags=tags_metadata)

register_exception_handlers(app)

# ORDEN DE LOS MIDDLEWARES: el último que se añade es el más externo.
# Cadena resultante: CORS -> request_id -> process_time -> endpoint
app.middleware("http")(process_time_middleware)
app.middleware("http")(request_id_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # por defecto http://localhost:5173
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    # Por defecto el navegador oculta al JavaScript las cabeceras de respuesta
    # que no son estándar. Exponerlas permite al frontend leer el tiempo de
    # proceso y el id de petición (para reportar errores).
    expose_headers=["X-Process-Time", "X-Request-ID"],
)

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(debug.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")