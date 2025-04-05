import asyncio
import time
from typing import Optional
import random

class RateLimiter:
    def __init__(self, rate: float = 0.5, burst: int = 1, max_retries: int = 3):
        """
        Initialize the rate limiter.
        
        Args:
            rate (float): Number of tokens per second (default: 0.5 = 1 request per 2 seconds)
            burst (int): Maximum number of tokens that can be accumulated
            max_retries (int): Maximum number of retry attempts
        """
        self.rate = rate
        self.burst = burst
        self.max_retries = max_retries
        self.tokens = burst
        self.last_update = time.time()
        self._lock = asyncio.Lock()
        self.retry_count = 0
    
    async def acquire(self) -> None:
        """
        Acquire a token from the bucket.
        If no tokens are available, wait until one becomes available.
        Implements exponential backoff for retries.
        """
        async with self._lock:
            while self.tokens <= 0:
                now = time.time()
                time_passed = now - self.last_update
                self.tokens = min(self.burst, self.tokens + time_passed * self.rate)
                self.last_update = now
                
                if self.tokens <= 0:
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0, 0.1)
                    wait_time = (1.0 / self.rate) * (1 + jitter)
                    
                    # Add exponential backoff for retries
                    if self.retry_count > 0:
                        backoff = min(30, 2 ** self.retry_count)  # Cap at 30 seconds
                        wait_time += backoff
                    
                    await asyncio.sleep(wait_time)
            
            self.tokens -= 1
    
    def reset_retry_count(self):
        """Reset the retry counter after a successful request"""
        self.retry_count = 0
    
    def increment_retry_count(self):
        """Increment the retry counter"""
        self.retry_count = min(self.retry_count + 1, self.max_retries)
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.reset_retry_count()
        else:
            self.increment_retry_count() 