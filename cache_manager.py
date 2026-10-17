"""
Jankiz Telegram Bot - High-Performance In-Memory Cache
======================================================
Stores pre-fetched and verified programming news & tips in memory
to deliver instant sub-second response times to all users.
"""

import time
import threading
from typing import Any, Optional, Dict

class FastCache:
    """Thread-safe in-memory cache with TTL."""
    
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if time.time() > entry["expires_at"]:
                del self._store[key]
                return None
            return entry["data"]

    def set(self, key: str, data: Any, ttl_seconds: int = 600):
        with self._lock:
            self._store[key] = {
                "data": data,
                "expires_at": time.time() + ttl_seconds
            }

    def clear(self):
        with self._lock:
            self._store.clear()

# Global cache instance
news_cache = FastCache()
