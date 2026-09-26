from fastapi import FastAPI
from rq.job import Job

from rq_queue import queue
from redis_connection import redis_connection
from jobs import failing_job

app = FastAPI()


@app.post("/jobs")
def create_job():
    job = queue.enqueue(failing_job)

    return {"job_id": job.id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = Job.fetch(job_id, connection=redis_connection)

    status = job.get_status()

    if status == "queued":
        api_status = "queued"
    elif status == "started":
        api_status = "processing"
    elif status == "finished":
        api_status = "completed"
    elif status == "failed":
        api_status = "failed"
    else:
        api_status = status

    return {"job_id": job.id, "status": api_status, "result": job.result, "error": job.exc_info}
