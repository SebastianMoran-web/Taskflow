from datetime import datetime
from fastapi import FastAPI
from app.schemas import TaskCreate, TaskRead


app = FastAPI()

@app.post("/tasks" , response_model=TaskRead, status_code=201)
def crearTarea(Tarea: TaskCreate) :
    return TaskRead(

        id=1,
        completed=False,
        created_at=datetime.now(),
        title=Tarea.title,
        description=Tarea.description,
        project_id=Tarea.project_id

    )


