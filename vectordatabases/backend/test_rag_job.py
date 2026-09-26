from rq_queue import queue
from rag_jobs import run_rag_job

job = queue.enqueue(
    run_rag_job,
    "What is this video about?",
    "ZHCB09O6zUk",
    3,
)

print(f"Job ID: {job.id}")