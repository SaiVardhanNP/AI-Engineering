from rq import Retry

from rq_queue import queue
from jobs import retryable_job

job = queue.enqueue(retryable_job, retry=Retry(max=2, interval=[2, 4, 6]))

print(job.id)
