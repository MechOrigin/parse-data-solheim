import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from rate_limiter import RateLimiter
import asyncio
from typing import Optional, Dict, Any
import time
import re
from api_key_manager import APIKeyManager

class AIService:
    def __init__(self, config=None):
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for .env file in: {os.path.join(os.getcwd(), '.env')}")
        load_dotenv()
        
        # Initialize API key manager
        self.api_key_manager = APIKeyManager()
        print(f"Loaded {self.api_key_manager.get_key_count()} API keys")
        
        # Initialize with first available key
        self.current_key = self.api_key_manager.get_available_key()
        if not self.current_key:
            raise ValueError("No available API keys")
        
        print(f"Using initial Gemini API key: {self.current_key[:10]}...")
        genai.configure(api_key=self.current_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Cache for storing results
        self.cache = {}
        self.cache_timestamps = {}
        
        # Store config reference
        self.config = config
        
        # Initialize rate limiter with default values
        self.rate_limiter = None
        self._update_rate_limiter()
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = None
    
    def _update_rate_limiter(self):
        """Update rate limiter based on configuration"""
        if self.config and hasattr(self.config, 'rate_limiting'):
            rate_config = self.config.rate_limiting
            if rate_config["enabled"]:
                # Convert requests per minute to requests per second
                requests_per_second = rate_config["requests_per_minute"] / 60
                burst_size = rate_config.get("burst_size", 5)  # Increased default burst size
                max_retries = rate_config.get("max_retries", 5)  # Increased default retries
                self.rate_limiter = RateLimiter(
                    rate=requests_per_second,
                    burst=burst_size,
                    max_retries=max_retries
                )
            else:
                # If rate limiting is disabled, create a dummy rate limiter that doesn't limit
                self.rate_limiter = RateLimiter(rate=1000, burst=1000, max_retries=0)
        else:
            # Default rate limiter if no config is provided - more lenient defaults
            self.rate_limiter = RateLimiter(rate=1.0, burst=5, max_retries=5)  # 1 request per second, burst of 5
    
    def _is_cache_valid(self, cache_key):
        """Check if a cached item is still valid based on TTL"""
        if not self.config or not self.config.caching["enabled"]:
            return False
            
        if cache_key not in self.cache_timestamps:
            return False
            
        # Convert minutes to seconds
        ttl = self.config.caching["ttl_minutes"] * 60
        timestamp = self.cache_timestamps[cache_key]
        return (time.time() - timestamp) < ttl
    
    async def _make_api_call(self, prompt: str, max_retries: int = None) -> Optional[str]:
        """Make an API call with retries and error handling"""
        # Update rate limiter in case config changed
        self._update_rate_limiter()
        
        # Use config max_retries if available, otherwise use default
        if max_retries is None:
            if self.config and hasattr(self.config, 'rate_limiting'):
                max_retries = self.config.rate_limiting.get("max_retries", 3)
            else:
                max_retries = 3
            
        print(f"Making API call with max_retries={max_retries}")
            
        for attempt in range(max_retries):
            try:
                async with self.rate_limiter:
                    # Get a new API key if needed
                    if not self.current_key or time.time() < self.api_key_manager.key_quota_reset.get(self.current_key, 0):
                        self.current_key = self.api_key_manager.get_available_key()
                        if not self.current_key:
                            raise Exception("No available API keys")
                        print(f"Switching to API key: {self.current_key[:10]}...")
                        print(f"Current key usage: {self.api_key_manager.key_usage[self.current_key]}")
                        print(f"Current key errors: {self.api_key_manager.key_errors[self.current_key]}")
                        genai.configure(api_key=self.current_key)
                        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
                    
                    response = await self.model.generate_content_async(prompt)
                    # Reset error count on success
                    self.api_key_manager.reset_key_errors(self.current_key)
                    print(f"Successful API call with key: {self.current_key[:10]}...")
                    return response.text
            except Exception as e:
                error_str = str(e)
                print(f"API call failed (attempt {attempt + 1}/{max_retries}): {error_str}")
                
                # Extract retry delay from error message if available
                retry_delay = None
                if "retry_delay" in error_str:
                    try:
                        # Try to extract seconds from the error message
                        match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', error_str)
                        if match:
                            retry_delay = int(match.group(1))
                    except:
                        pass
                
                # Mark current key as having an error
                if self.current_key:
                    print(f"Marking key {self.current_key[:10]}... as having an error")
                    self.api_key_manager.mark_key_error(self.current_key, retry_delay or 60)
                    print(f"Key errors after marking: {self.api_key_manager.key_errors[self.current_key]}")
                
                if attempt < max_retries - 1:
                    # Use API-provided retry delay if available, otherwise use exponential backoff
                    if retry_delay is not None:
                        wait_time = retry_delay
                    else:
                        wait_time = 2 ** attempt
                    
                    print(f"Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"All {max_retries} attempts failed. Last error: {error_str}")
                    raise
    
    async def get_definition(self, acronym: str, grade: str = "general") -> str:
        """Get a definition for an acronym using Gemini API"""
        # Check cache first
        cache_key = f"{acronym}_{grade}"
        if cache_key in self.cache and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        prompt = f"""You are an acronym expansion engine. Given the acronym below, provide a clear and concise definition suitable for {grade} level understanding.

Acronym: {acronym}

Respond with just the definition, no additional text or formatting."""

        try:
            definition = await self._make_api_call(prompt)
            if definition:
                definition = definition.strip()
                # Cache the result
                self.cache[cache_key] = definition
                self.cache_timestamps[cache_key] = time.time()
                return definition
            return f"Error: Could not generate definition for {acronym}"
        except Exception as e:
            print(f"Error generating definition for {acronym}: {str(e)}")
            return f"Error: Could not generate definition for {acronym}"
    
    async def enrich_acronym(self, acronym: str, definition: str, grade: str = "general") -> Dict[str, Any]:
        """Enrich an acronym with additional information using Gemini API"""
        # Check if enrichment is enabled
        if self.config and hasattr(self.config, 'enrichment') and not self.config.enrichment["enabled"]:
            return {
                "description": "Enrichment disabled",
                "tags": "enrichment_disabled"
            }
            
        # Check cache first
        cache_key = f"{acronym}_enriched_{grade}"
        if cache_key in self.cache and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        prompt = f"""You are an acronym enrichment engine. Given the acronym and its definition below, provide additional information suitable for {grade} level understanding.

Acronym: {acronym}
Definition: {definition}

Please provide:
1. A detailed description (2-3 sentences) that explains the acronym's meaning, usage, and importance.
2. A list of 3-5 relevant tags (comma-separated) that categorize this acronym.

Respond in JSON format:
{{
  "description": "...",
  "tags": "..."
}}"""

        try:
            response_text = await self._make_api_call(prompt)
            if response_text:
                # Extract JSON from response
                try:
                    # Find JSON content between curly braces
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = response_text[start:end]
                        result = json.loads(json_str)
                        
                        # Cache the result
                        self.cache[cache_key] = result
                        self.cache_timestamps[cache_key] = time.time()
                        
                        return result
                    else:
                        raise ValueError("No JSON found in response")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON for {acronym} enrichment: {str(e)}")
                    print(f"Response text: {response_text}")
                    return {
                        "description": "Error parsing response",
                        "tags": "error"
                    }
            return {
                "description": "Error: Could not generate enrichment",
                "tags": "error"
            }
        except Exception as e:
            print(f"Error enriching acronym {acronym}: {str(e)}")
            return {
                "description": f"Error: {str(e)}",
                "tags": "error"
            }
    
    async def generate_content(self, acronym: str, prompt: str = None) -> Dict[str, Any]:
        """Generate content for an acronym using Gemini API"""
        # Check cache first
        if acronym in self.cache and self._is_cache_valid(acronym):
            return self.cache[acronym]
        
        # Use provided prompt or default
        if prompt is None:
            prompt = f"""You are an acronym expansion engine. Given the acronym below, return:

1. Definition: The standard meaning of the acronym.
2. Description: A one-sentence business-relevant summary of its usage or application.
3. Tags: A list of 3–5 comma-separated keywords relevant to industry, usage, or category.

Acronym: {acronym}

Respond in JSON:
{{
  "definition": "...",
  "description": "...",
  "tags": ["...", "...", "..."]
}}"""
        else:
            # Replace {acronym} placeholder in the prompt if it exists
            prompt = prompt.replace("{acronym}", acronym)

        try:
            response_text = await self._make_api_call(prompt)
            if response_text:
                # Extract JSON from response
                try:
                    # Find JSON content between curly braces
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = response_text[start:end]
                        result = json.loads(json_str)
                        
                        # Cache the result
                        self.cache[acronym] = result
                        self.cache_timestamps[acronym] = time.time()
                        
                        return result
                    else:
                        raise ValueError("No JSON found in response")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON for {acronym}: {str(e)}")
                    print(f"Response text: {response_text}")
                    return {
                        "definition": "Error parsing response",
                        "description": "Error parsing response",
                        "tags": ["error"]
                    }
            return {
                "definition": "Error: Could not generate content",
                "description": "Error: Could not generate content",
                "tags": ["error"]
            }
        except Exception as e:
            print(f"Error generating content for {acronym}: {str(e)}")
            return {
                "definition": f"Error: {str(e)}",
                "description": "Error generating content",
                "tags": ["error"]
            }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache = {}
        self.cache_timestamps = {} 