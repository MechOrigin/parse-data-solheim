import os
from typing import List, Optional
import time
from dotenv import load_dotenv
import random

class APIKeyManager:
    def __init__(self):
        load_dotenv()
        self.api_keys = []
        self.key_usage = {}  # Track usage per key
        self.key_errors = {}  # Track errors per key
        self.key_last_used = {}  # Track last use time per key
        self.key_quota_reset = {}  # Track quota reset time per key
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment variables"""
        # Look for GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
        i = 1
        while True:
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if not key:
                break
            print(f"Loaded API key {i}: {key[:10]}...")
            self.api_keys.append(key)
            self.key_usage[key] = 0
            self.key_errors[key] = 0
            self.key_last_used[key] = 0
            self.key_quota_reset[key] = 0
            i += 1
        
        # Also check for the default GEMINI_API_KEY
        default_key = os.getenv("GEMINI_API_KEY")
        if default_key and default_key not in self.api_keys:
            print(f"Loaded default API key: {default_key[:10]}...")
            self.api_keys.append(default_key)
            self.key_usage[default_key] = 0
            self.key_errors[default_key] = 0
            self.key_last_used[default_key] = 0
            self.key_quota_reset[default_key] = 0
        
        if not self.api_keys:
            raise ValueError("No Gemini API keys found in environment variables")
        
        print(f"Total API keys loaded: {len(self.api_keys)}")
    
    def get_available_key(self) -> Optional[str]:
        """Get an available API key using load balancing"""
        current_time = time.time()
        available_keys = []
        
        for key in self.api_keys:
            # Skip keys that are in quota reset period
            if current_time < self.key_quota_reset[key]:
                continue
            
            # Calculate key score based on usage and errors
            time_since_last_use = current_time - self.key_last_used[key]
            usage_score = self.key_usage[key]
            error_score = self.key_errors[key] * 10  # Errors count more than usage
            
            # Add some randomness to prevent all clients from choosing the same key
            random_factor = random.uniform(0.8, 1.2)
            key_score = (usage_score + error_score) * random_factor
            
            available_keys.append((key, key_score))
        
        if not available_keys:
            return None
        
        # Sort by score and pick the key with lowest score
        available_keys.sort(key=lambda x: x[1])
        selected_key = available_keys[0][0]
        
        # Update usage tracking
        self.key_usage[selected_key] += 1
        self.key_last_used[selected_key] = current_time
        
        return selected_key
    
    def mark_key_error(self, key: str, retry_delay: int = 60):
        """Mark a key as having an error"""
        self.key_errors[key] += 1
        self.key_quota_reset[key] = time.time() + retry_delay
    
    def reset_key_errors(self, key: str):
        """Reset error count for a key after successful use"""
        self.key_errors[key] = 0
        self.key_quota_reset[key] = 0
    
    def get_key_count(self) -> int:
        """Get the number of available API keys"""
        return len(self.api_keys) 