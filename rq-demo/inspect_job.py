from rq.job import Job
from redis_connection import redis_connection

job = Job.fetch("bb5a35f7-c804-4e93-9f52-53a26f908feb", connection=redis_connection)

print(job)

print(job.get_status())
print(job.result)