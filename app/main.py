from fastapi import FastAPI

app = FastAPI(title="Taskflow API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def get_version():
    return {"version": "1.0.0"}

@app.get("/ping")
def ping():
    return {"ping": "pong"}