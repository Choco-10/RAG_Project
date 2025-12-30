import redis
import json
from typing import List, Dict

class RedisMemory:
    def __init__(self, host="localhost", port=6379, db=0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )

    def add_message(self, session_id: str, role: str, content: str):
        key = f"chat:{session_id}"
        message = {
            "role": role,
            "content": content
        }
        self.client.rpush(key, json.dumps(message))

    def get_history(self, session_id: str) -> List[Dict]:
        key = f"chat:{session_id}"
        messages = self.client.lrange(key, 0, -1)
        return [json.loads(m) for m in messages]

    def clear(self, session_id: str):
        self.client.delete(f"chat:{session_id}")
