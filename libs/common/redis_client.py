import redis
import json
from .config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    def push_task(self, queue_name: str, payload: dict):
        self.client.rpush(queue_name, json.dumps(payload))

    def wait_for_task(self, queue_name: str, timeout=0):
        result = self.client.blpop(queue_name, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None

redis_client = RedisClient()