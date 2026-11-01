import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self):
        # key -> (timestamps list)
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_id: str, limit: int = 60, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Sliding window rate limit.
        Returns (is_allowed, remaining_requests)
        """
        current_time = time.time()
        with self.lock:
            # Clean old requests
            timestamps = self.requests[client_id]
            valid_timestamps = [t for t in timestamps if current_time - t < window_seconds]
            
            if len(valid_timestamps) >= limit:
                self.requests[client_id] = valid_timestamps
                return False, 0
            
            valid_timestamps.append(current_time)
            self.requests[client_id] = valid_timestamps
            return True, limit - len(valid_timestamps)

rate_limiter = RateLimiter()
