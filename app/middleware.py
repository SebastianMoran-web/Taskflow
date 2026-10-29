"""
Un middleware es código que envuelve todas las peticiones: ve la request antes de llegar al endpoint
y la response antes de llegar al cliente. Sirve para comportamiento transversal sin repetirlo en cada ruta

Orden de ejecución:

CORS -> request_id_middleware -> process_time_middleware -> endpoint

La respuesta recorre el camino inverso. Por eso:
  * CORS es el más externo: así también llegan sus cabeceras a las respuestas
    de error y el navegador puede leer un 500 en lugar de ver un fallo de CORS.
  * request_id va fuera de process_time: el id ya existe cuando se registra
    un error, y la cabecera X-Request-ID se añade a toda respuesta.


"""

import time
import uuid

from fastapi import Request

from app.exceptions import unhandled_exception_handler

async def request_id_middleware(request: Request, call_next):

    """
    Le asigna un ID a la petición.
    Sin una ID, no se puede identificar la linea con fallos, en caso de error. La ID se genera en el servidor para evitar falsificaciones
    
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

async def process_time_middleware(request: Request, call_next):

    """
    
    Devuelve el tiemppo de proceso en ms, se puede ver en el DevTools
    
    Por qué captura aquí las excepciones: una excepción no controlada la
    gestiona la capa más externa de Starlette (ServerErrorMiddleware), que está
    POR FUERA de todos los middlewares. Su respuesta 500 no pasaría por
    aquí y saldría sin X-Process-Time ni cabeceras CORS. Capturándola dentro,
    reutilizamos el mismo handler global y la respuesta 500 recibe todas las
    cabeceras como cualquier otra.

    
    """

    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        response = await unhandled_exception_handler(request, exc)

    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["x-Process-Time"] = f"{elapsed_ms} ms"
    return response
