"""
Manejo global de errores.

Todas las respuestas de error de la API comparten el mismo esquema:

{"error": "mensaje legible", "error_code": "CODIGO_ESTABLE"}

El cliente puede mostrar `error` al usuario y programar su lógica contra
`error_code`, que no cambia aunque se reformule el mensaje.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("taskflow.errors")


# ---------- Excepciones de dominio (Práctica 1.6) ----------
class AppError(Exception):
    """Error de negocio con código HTTP y error_code propios."""
    status_code = 400

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code


class NotFoundError(AppError):
    """404: el recurso no existe. Ej: NotFoundError("Tarea", 5, "TASK_NOT_FOUND")"""
    status_code = 404

    def __init__(self, resource: str, resource_id: int, error_code: str):
        super().__init__(f"{resource} con id {resource_id} no existe", error_code)


class ConflictError(AppError):
    """409: la operación choca con el estado actual (duplicado, recurso en uso)."""
    status_code = 409


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "error_code": exc.error_code},
    )


# ---------- Handlers globales ----------
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Captura cualquier excepción no controlada y responde 500.

    Sin este handler, un fallo inesperado devuelve una página de error genérica
    (o el stacktrace en modo debug), lo que filtra detalles internos y rompe el
    contrato JSON de la API.

    El detalle completo se escribe solo en el log del servidor, con el
    request_id para localizarlo. El cliente recibe un mensaje genérico.
    """
    request_id = getattr(request.state, "request_id", "-")
    logger.error(
        "Excepción no controlada [request_id=%s] %s %s",
        request_id,
        request.method,
        request.url.path,
        exc_info=exc,  # incluye el stacktrace completo en el log interno
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail), "error_code": f"HTTP_{exc.status_code}"},
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "Datos de entrada no válidos",
            "error_code": "VALIDATION_ERROR",
            "details": jsonable_encoder(exc.errors()),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)