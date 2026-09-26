from rq import Queue
from redis_connection import redis_connection


queue = Queue(connection=redis_connection)
