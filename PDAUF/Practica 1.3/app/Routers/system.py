from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/version")
def get_version():
    return {"version": "1.0"}


@router.get("/ping")
def ping():
    return {"ping": "pong"}
