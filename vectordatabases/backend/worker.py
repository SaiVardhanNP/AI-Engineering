from rq import Worker
from redis_connection import redis_connection
from rq_queue import queue

worker = Worker([queue], connection=redis_connection)


worker.work()
