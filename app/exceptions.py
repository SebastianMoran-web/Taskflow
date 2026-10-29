import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("taskflow.errors")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:

    request_id = getattr(request.state, "request_id", "-")
    logger.error(

        "Excepción no controlada [request_id=%s] %s %s",
        request_id,
        request.method,
        request.url.path,
        exc_info=exc,
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
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)