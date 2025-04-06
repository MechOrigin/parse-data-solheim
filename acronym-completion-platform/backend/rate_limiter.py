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
        self.last_error_time = None
        self.quota_exhausted = False
        self.quota_reset_time = None
    
    async def acquire(self) -> None:
        """
        Acquire a token from the bucket.
        If no tokens are available, wait until one becomes available.
        Implements exponential backoff for retries.
        """
        async with self._lock:
            # Check if we're in quota exhausted state
            if self.quota_exhausted:
                if self.quota_reset_time and time.time() < self.quota_reset_time:
                    wait_time = self.quota_reset_time - time.time()
                    print(f"Quota exhausted, waiting {wait_time:.1f} seconds for reset...")
                    await asyncio.sleep(wait_time)
                    # Reset tokens after quota reset
                    self.tokens = self.burst
                    self.quota_exhausted = False
                    self.quota_reset_time = None
                else:
                    self.quota_exhausted = False
                    self.quota_reset_time = None
                    self.tokens = self.burst  # Reset tokens after quota reset
            
            while self.tokens <= 0:
                now = time.time()
                time_passed = now - self.last_update
                self.tokens = min(self.burst, self.tokens + time_passed * self.rate)
                self.last_update = now
                
                if self.tokens <= 0:
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0, 0.1)
                    base_wait_time = (1.0 / self.rate) * (1 + jitter)
                    
                    # Add exponential backoff for retries
                    if self.retry_count > 0:
                        # Calculate backoff with a maximum of 60 seconds
                        backoff = min(60, 2 ** self.retry_count)
                        # Add some randomness to the backoff
                        backoff = backoff * (1 + random.uniform(-0.1, 0.1))
                        wait_time = base_wait_time + backoff
                    else:
                        wait_time = base_wait_time
                    
                    # If we've had recent errors, add additional delay
                    if self.last_error_time and (now - self.last_error_time) < 60:
                        wait_time *= 2  # Increased multiplier for recent errors
                    
                    await asyncio.sleep(wait_time)
            
            self.tokens -= 1
    
    def reset_retry_count(self):
        """Reset the retry counter after a successful request"""
        self.retry_count = 0
        self.last_error_time = None
    
    def increment_retry_count(self):
        """Increment the retry counter and update last error time"""
        self.retry_count = min(self.retry_count + 1, self.max_retries)
        self.last_error_time = time.time()
    
    def set_quota_exhausted(self, reset_seconds: int):
        """Set quota as exhausted with a reset time"""
        self.quota_exhausted = True
        self.quota_reset_time = time.time() + reset_seconds
        print(f"Quota exhausted, will reset in {reset_seconds} seconds")
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.reset_retry_count()
        else:
            self.increment_retry_count()
            # Check if this is a quota error
            if exc_val and "quota" in str(exc_val).lower():
                # Try to extract retry delay from error message
                import re
                match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', str(exc_val))
                if match:
                    reset_seconds = int(match.group(1))
                    self.set_quota_exhausted(reset_seconds) 