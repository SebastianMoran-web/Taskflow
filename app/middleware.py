import time
import uuid

from fastapi import Request

from app.exceptions import unhandled_exception_handler

async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

async def process_time_middleware(request: Request, call_next):

    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        response = await unhandled_exception_handler(request, exc)

    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["x-Process-Time"] = f"{elapsed_ms} ms"
    return response
