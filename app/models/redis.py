# file: models/redis.py
from pydantic import BaseModel
from typing import Any, Dict, Optional, List

class RedisKey(BaseModel):
    namespace: str
    key: str
    value: Dict[str, Any]

class RedisKeyUpdate(BaseModel):
    namespace: str
    key: str
    value: Dict[str, Any]

class RedisKeyDelete(BaseModel):
    namespace: str
    key: str

class RedisNamespace(BaseModel):
    namespace: str

class RedisGetKey(BaseModel):
    namespace: str
    key: str
