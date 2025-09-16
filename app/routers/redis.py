# file: core/redis_helper.py
from internal.connector import getRedisConnection
import os
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class RedisHelper:
    def __init__(self):
        self.redis = getRedisConnection()

    def set_key(self, namespace: str, key: str, value: dict) -> bool:
        """Set a key in Redis under the given namespace."""
        try:
            namespaced_key = f"{namespace}:{key}"
            self.redis.set(namespaced_key, json.dumps(value, sort_keys=True))
            logger.info(f"Set key {namespaced_key} in Redis")
            return True
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

    def get_key(self, namespace: str, key: str):
        """Get a key's value from Redis, returns dict or None."""
        try:
            namespaced_key = f"{namespace}:{key}"
            val = self.redis.get(namespaced_key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    def delete_key(self, namespace: str, key: str) -> int:
        """Delete a key from Redis."""
        try:
            namespaced_key = f"{namespace}:{key}"
            result = self.redis.delete(namespaced_key)
            logger.info(f"Deleted key {namespaced_key} from Redis")
            return result
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return 0

    def list_keys(self, namespace: str):
        """List all keys under a namespace."""
        try:
            pattern = f"{namespace}:*"
            keys = self.redis.keys(pattern)
            return [key.split(":", 1)[1] for key in keys]
        except Exception as e:
            logger.error(f"Failed to list keys for namespace {namespace}: {e}")
            return []

    def get_all(self, namespace: str):
        """Return all items in a namespace as a list of dicts."""
        try:
            pattern = f"{namespace}:*"
            keys = self.redis.keys(pattern)
            all_items = []
            for key in keys:
                val = self.redis.get(key)
                if val:
                    all_items.append(json.loads(val))
            return all_items
        except Exception as e:
            logger.error(f"Failed to get all items for namespace {namespace}: {e}")
            return []

    def update_key(self, namespace: str, key: str, new_value: dict) -> bool:
        """Update a key only if the value has changed."""
        try:
            existing = self.get_key(namespace, key)
            if existing != new_value:
                return self.set_key(namespace, key, new_value)
            logger.info(f"No changes for key {key}, skipping update")
            return False
        except Exception as e:
            logger.error(f"Failed to update key {key}: {e}")
            return False

    def flush_namespace(self, namespace: str) -> int:
        """Delete all keys in a namespace."""
        try:
            pattern = f"{namespace}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            logger.info(f"Flushed namespace {namespace}")
            return len(keys)
        except Exception as e:
            logger.error(f"Failed to flush namespace {namespace}: {e}")
            return 0
