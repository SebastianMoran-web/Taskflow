from fastapi import APIRouter

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/ping")
def ping():
    return{"ping": "pong"}

@router.get("/error")
def forzar_error():
    raise RuntimeError("Fallo forzado para probar el handler global")