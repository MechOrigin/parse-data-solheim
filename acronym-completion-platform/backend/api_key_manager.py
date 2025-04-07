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
        # Only look for GEMINI_API_KEY_1 through GEMINI_API_KEY_5
        for i in range(1, 6):  # 1 to 5
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and key != "your_gemini_api_key_here":  # Avoid placeholder values
                print(f"Loaded API key {i}: {key[:10]}...")
                self.api_keys.append(key)
                self.key_usage[key] = 0
                self.key_errors[key] = 0
                self.key_last_used[key] = 0
                self.key_quota_reset[key] = 0
        
        if not self.api_keys:
            raise ValueError("No valid Gemini API keys found in environment variables")
        
        print(f"Total API keys loaded: {len(self.api_keys)}")
    
    def get_available_key(self) -> Optional[str]:
        """Get an available API key using load balancing"""
        current_time = time.time()
        available_keys = []
        
        # Print status of all keys
        print("\nAPI Key Status:")
        for key in self.api_keys:
            key_status = "available"
            if current_time < self.key_quota_reset[key]:
                reset_time = self.key_quota_reset[key] - current_time
                key_status = f"quota reset in {int(reset_time)}s"
            
            print(f"Key {key[:10]}...: {key_status}, usage: {self.key_usage[key]}, errors: {self.key_errors[key]}")
        
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
            # If no keys are available, reset the quota for the least recently used key
            least_recent_key = min(self.api_keys, key=lambda k: self.key_last_used[k])
            print(f"All keys in quota reset, resetting quota for key: {least_recent_key[:10]}...")
            self.key_quota_reset[least_recent_key] = 0
            return least_recent_key
        
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
        print(f"Marked key {key[:10]}... as having an error. Reset in {retry_delay} seconds.")
    
    def reset_key_errors(self, key: str):
        """Reset error count for a key after successful use"""
        if self.key_errors[key] > 0:
            print(f"Resetting error count for key {key[:10]}...")
        self.key_errors[key] = 0
        self.key_quota_reset[key] = 0
    
    def get_key_count(self) -> int:
        """Get the number of available API keys"""
        return len(self.api_keys) 