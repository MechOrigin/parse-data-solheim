import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from rate_limiter import RateLimiter
import asyncio
from typing import Optional, Dict, Any
import time

class AIService:
    def __init__(self, config=None):
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for .env file in: {os.path.join(os.getcwd(), '.env')}")
        load_dotenv()
        
        # Force the API key to be set
        api_key = "AIzaSyCZqWALaH7rxtl55oPps8njy6rG4SJRllo"
        os.environ["GEMINI_API_KEY"] = api_key
        
        print(f"Using Gemini API key: {api_key[:10]}...")  # Only print first 10 chars for security
        print(f"API key length: {len(api_key)}")
        print(f"API key format: {'valid' if api_key.startswith('AIzaSy') else 'invalid'}")
        
        genai.configure(api_key=api_key)
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
                self.rate_limiter = RateLimiter(
                    rate=rate_config["requests_per_second"],
                    burst=rate_config["burst_size"],
                    max_retries=rate_config["max_retries"]
                )
            else:
                # If rate limiting is disabled, create a dummy rate limiter that doesn't limit
                self.rate_limiter = RateLimiter(rate=1000, burst=1000, max_retries=0)
        else:
            # Default rate limiter if no config is provided
            self.rate_limiter = RateLimiter(rate=0.5, burst=1, max_retries=3)
    
    def _is_cache_valid(self, cache_key):
        """Check if a cached item is still valid based on TTL"""
        if not self.config or not self.config.caching["enabled"]:
            return False
            
        if cache_key not in self.cache_timestamps:
            return False
            
        ttl = self.config.caching["ttl_seconds"]
        timestamp = self.cache_timestamps[cache_key]
        return (time.time() - timestamp) < ttl
    
    async def _make_api_call(self, prompt: str, max_retries: int = None) -> Optional[str]:
        """Make an API call with retries and error handling"""
        # Update rate limiter in case config changed
        self._update_rate_limiter()
        
        # Use config max_retries if available, otherwise use default
        if max_retries is None and self.config and hasattr(self.config, 'rate_limiting'):
            max_retries = self.config.rate_limiting["max_retries"]
        elif max_retries is None:
            max_retries = 3
            
        for attempt in range(max_retries):
            try:
                async with self.rate_limiter:
                    response = await self.model.generate_content_async(prompt)
                    return response.text
            except Exception as e:
                print(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Wait before retrying
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
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