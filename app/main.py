from fastapi import FastAPI

app = FastAPI(title="Taskflow API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

