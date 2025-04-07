import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class APIKeyStats:
    """Statistics for a single API key."""
    key: str
    requests_today: int = 0
    last_request_time: Optional[datetime] = None
    daily_limit: int = 60  # Free tier limit per day
    rate_limit: int = 60  # Requests per minute
    is_active: bool = True
    error_count: int = 0
    last_error_time: Optional[datetime] = None
    quota_reset_time: Optional[datetime] = None
    consecutive_errors: int = 0
    last_successful_request: Optional[datetime] = None

class APIKeyCluster:
    """Manages a cluster of API keys with rate limiting and error handling."""
    
    def __init__(self, keys: List[str], daily_limit: int = 60, rate_limit: int = 60):
        """
        Initialize the API key cluster.
        
        Args:
            keys: List of API keys
            daily_limit: Maximum requests per day per key (free tier limit)
            rate_limit: Maximum requests per minute per key
        """
        self.keys: Dict[str, APIKeyStats] = {
            key: APIKeyStats(
                key=key,
                daily_limit=daily_limit,
                rate_limit=rate_limit
            ) for key in keys
        }
        self.current_key_index = 0
        self.last_reset_time = datetime.now()
        self.min_wait_time = float(os.getenv('RETRY_DELAY', '1.0'))  # Minimum wait time between requests in seconds
        
        logger.info(f"Initialized APIKeyCluster with {len(keys)} keys")
        logger.info(f"Daily limit: {daily_limit}, Rate limit: {rate_limit}")
        
    @classmethod
    def from_env(cls, prefix: str = "GEMINI_API_KEY_", daily_limit: Optional[int] = None, rate_limit: Optional[int] = None) -> 'APIKeyCluster':
        """
        Create an API key cluster from environment variables.
        
        Args:
            prefix: Prefix for environment variable names
            daily_limit: Maximum requests per day per key (overrides env var)
            rate_limit: Maximum requests per minute per key (overrides env var)
        """
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment variables
        daily_limit = daily_limit or int(os.getenv('DAILY_LIMIT_PER_KEY', '60'))
        rate_limit = rate_limit or int(os.getenv('RATE_LIMIT_PER_KEY', '60'))
        
        # Get API keys
        keys = []
        i = 1
        while True:
            key = os.getenv(f"{prefix}{i}")
            if not key:
                break
            keys.append(key)
            i += 1
        
        if not keys:
            raise ValueError(f"No API keys found with prefix {prefix}")
        
        return cls(keys, daily_limit, rate_limit)
    
    def get_next_available_key(self) -> Optional[str]:
        """
        Get the next available API key that hasn't exceeded its limits.
        
        Returns:
            The next available API key or None if all keys are rate limited
        """
        now = datetime.now()
        
        # Reset daily counters if it's a new day
        if (now - self.last_reset_time).days >= 1:
            self._reset_daily_counts()
        
        # Try all keys in rotation
        for _ in range(len(self.keys)):
            key_stats = self.keys[self._get_next_key()]
            
            # Skip inactive keys
            if not key_stats.is_active:
                continue
            
            # Check if key is in quota reset period
            if key_stats.quota_reset_time and now < key_stats.quota_reset_time:
                continue
            
            # Check daily limit
            if key_stats.requests_today >= key_stats.daily_limit:
                continue
            
            # Check rate limit
            if key_stats.last_request_time:
                time_since_last = (now - key_stats.last_request_time).total_seconds()
                if time_since_last < self.min_wait_time:
                    continue
            
            # Update stats
            key_stats.requests_today += 1
            key_stats.last_request_time = now
            key_stats.last_successful_request = now
            key_stats.consecutive_errors = 0
            
            logger.debug(f"Using API key: {key_stats.key[:8]}... (requests today: {key_stats.requests_today})")
            return key_stats.key
        
        return None
    
    def _get_next_key(self) -> str:
        """Get the next key in rotation."""
        keys = list(self.keys.keys())
        key = keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(keys)
        return key
    
    def _reset_daily_counts(self):
        """Reset daily request counts for all keys."""
        now = datetime.now()
        for stats in self.keys.values():
            stats.requests_today = 0
        self.last_reset_time = now
        logger.info("Reset daily request counts for all API keys")
    
    def mark_error(self, key: str, error: Exception, retry_after: Optional[int] = None):
        """
        Mark an error for a specific API key.
        
        Args:
            key: The API key that encountered an error
            error: The error that occurred
            retry_after: Number of seconds to wait before retrying (for quota errors)
        """
        if key in self.keys:
            stats = self.keys[key]
            stats.error_count += 1
            stats.last_error_time = datetime.now()
            stats.consecutive_errors += 1
            
            # Check for quota errors
            error_str = str(error)
            if "quota" in error_str.lower() or "429" in error_str:
                if retry_after:
                    stats.quota_reset_time = datetime.now() + timedelta(seconds=retry_after)
                    logger.warning(f"API key {key[:8]}... quota exceeded. Reset in {retry_after} seconds")
                else:
                    # Default to 60 seconds if no retry_after provided
                    stats.quota_reset_time = datetime.now() + timedelta(seconds=60)
                    logger.warning(f"API key {key[:8]}... quota exceeded. Reset in 60 seconds")
            
            # Deactivate key if it has too many consecutive errors
            max_retries = int(os.getenv('MAX_RETRIES', '3'))
            if stats.consecutive_errors >= max_retries:
                stats.is_active = False
                logger.warning(f"Deactivated API key {key[:8]}... due to {stats.consecutive_errors} consecutive errors")
            
            # Increase wait time if we're getting rate limited
            if "rate" in error_str.lower() or "429" in error_str:
                self.min_wait_time = min(5.0, self.min_wait_time * 1.5)
                logger.info(f"Increased minimum wait time to {self.min_wait_time:.2f} seconds")
    
    def reactivate_key(self, key: str):
        """
        Reactivate a previously deactivated API key.
        
        Args:
            key: The API key to reactivate
        """
        if key in self.keys:
            stats = self.keys[key]
            if not stats.is_active:
                stats.is_active = True
                stats.consecutive_errors = 0
                stats.quota_reset_time = None
                logger.info(f"Reactivated API key {key[:8]}...")
    
    def get_key_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all API keys.
        
        Returns:
            Dictionary with statistics for each key
        """
        return {
            key: {
                "requests_today": stats.requests_today,
                "error_count": stats.error_count,
                "is_active": stats.is_active,
                "consecutive_errors": stats.consecutive_errors,
                "last_successful_request": stats.last_successful_request.isoformat() if stats.last_successful_request else None,
                "quota_reset_time": stats.quota_reset_time.isoformat() if stats.quota_reset_time else None
            }
            for key, stats in self.keys.items()
        }
    
    def wait_for_available_key(self, timeout: int = 300) -> Optional[str]:
        """
        Wait for an available API key.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            An available API key or None if timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            key = self.get_next_available_key()
            if key:
                return key
            
            # Check if any keys are in quota reset period
            now = datetime.now()
            reset_times = [
                (k, stats.quota_reset_time) 
                for k, stats in self.keys.items() 
                if stats.quota_reset_time and now < stats.quota_reset_time
            ]
            
            if reset_times:
                # Find the earliest reset time
                earliest_key, earliest_time = min(reset_times, key=lambda x: x[1])
                wait_seconds = (earliest_time - now).total_seconds()
                logger.info(f"Waiting {wait_seconds:.1f} seconds for API key {earliest_key[:8]}... quota reset")
                time.sleep(min(wait_seconds, 10))  # Wait at most 10 seconds at a time
            else:
                # If no keys are in reset period, wait a short time and try again
                time.sleep(1)
        
        logger.warning("Timeout waiting for available API key")
        return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the API key cluster.
        
        Returns:
            Dictionary with health status information
        """
        now = datetime.now()
        active_keys = sum(1 for stats in self.keys.values() if stats.is_active)
        quota_limited_keys = sum(1 for stats in self.keys.values() if stats.quota_reset_time and now < stats.quota_reset_time)
        daily_limited_keys = sum(1 for stats in self.keys.values() if stats.requests_today >= stats.daily_limit)
        
        return {
            "total_keys": len(self.keys),
            "active_keys": active_keys,
            "quota_limited_keys": quota_limited_keys,
            "daily_limited_keys": daily_limited_keys,
            "min_wait_time": self.min_wait_time,
            "keys": self.get_key_stats()
        } 