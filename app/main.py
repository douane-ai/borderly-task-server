from fastapi import FastAPI, Response
from celery import Celery
from celery.result import AsyncResult
from enum import Enum
from pydantic import BaseModel
import celery_config
from celery.signals import worker_init, worker_shutdown
import dotenv

dotenv.load_dotenv()

# Start FastAPI, Celery and optional ngrok services
app = FastAPI(title="Fruit Task Service - Passionfruit")

celery = Celery(__name__)
celery.config_from_object(celery_config)

# Import tasks so Celery recognizes them
from utils import error_handler
from tasks import summarize

# map to task names
class TaskName(Enum):
    SummarizeFinding = "SummarizeFinding"

class Job(BaseModel):
    task: TaskName
    records: list[dict]


# API endpoints
@app.post("/")
async def async_tasks(response: Response, job: Job):
    task_ids = []
    for record in job.records:
        t = celery.signature(job.task.value)
        r = t.apply_async(kwargs=record, link_error=error_handler.s())
        task_ids.append(r.id)

    return task_ids

@app.get("/status")
async def status(response: Response, task_id: str):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result