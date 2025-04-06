import os
import json
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class GrokService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GROK_API_KEY')
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable is not set")
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configure retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Cache for storing results
        self.cache = {}
    
    async def get_definition(self, acronym: str, grade: str = "general") -> str:
        """Get a definition for an acronym using Grok API"""
        # Check cache first
        cache_key = f"{acronym}_{grade}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""You are an acronym expansion engine. Given the acronym below, provide a clear and concise definition suitable for {grade} level understanding.

Acronym: {acronym}

Respond with just the definition, no additional text or formatting."""

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "model": "grok-1",
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                definition = result["choices"][0]["message"]["content"].strip()
                
                # Cache the result
                self.cache[cache_key] = definition
                
                return definition
            else:
                print(f"Error from Grok API: {response.status_code} - {response.text}")
                return f"Error: Could not generate definition for {acronym}"
        except Exception as e:
            print(f"Error generating definition for {acronym}: {str(e)}")
            return f"Error: Could not generate definition for {acronym}"
    
    async def enrich_acronym(self, acronym: str, definition: str, grade: str = "general") -> dict:
        """Enrich an acronym with additional information using Grok API"""
        # Check cache first
        cache_key = f"{acronym}_enriched_{grade}"
        if cache_key in self.cache:
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
            response = self.session.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "grok-1",
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant that enriches acronyms with additional information."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Grok API error for {acronym} enrichment: {response.text}")
                return {
                    "description": f"Error: {response.text}",
                    "tags": "error"
                }
            
            response_text = response.json()['choices'][0]['message']['content']
            
            # Extract JSON from response
            try:
                # Find JSON content between curly braces
                json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
                # Clean up the JSON string
                json_str = json_str.strip()
                # Remove any markdown code block indicators
                json_str = json_str.replace('```json', '').replace('```', '')
                # Parse the JSON
                result = json.loads(json_str)
                
                # Validate result structure
                required_keys = ['description', 'tags']
                if not all(key in result for key in required_keys):
                    raise ValueError("Missing required keys in AI response")
                
                # Cache the result
                self.cache[cache_key] = result
                return result
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error for {acronym} enrichment: {str(e)}")
                print(f"Raw response: {response_text}")
                return {
                    "description": "Error parsing response",
                    "tags": "error"
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error for {acronym} enrichment: {str(e)}")
            return {
                "description": f"Error: {str(e)}",
                "tags": "error"
            }
        except Exception as e:
            print(f"Error in Grok API for {acronym} enrichment: {str(e)}")
            return {
                "description": f"Error: {str(e)}",
                "tags": "error"
            }
    
    async def generate_content(self, acronym: str, prompt: str = None) -> dict:
        """Generate content for an acronym using Grok API"""
        # Check cache first
        if acronym in self.cache:
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
            response = self.session.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "grok-1",
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant that expands acronyms."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=30  # Add timeout
            )
            
            if response.status_code != 200:
                print(f"Grok API error for {acronym}: {response.text}")
                raise Exception(f"Grok API error: {response.text}")
            
            response_text = response.json()['choices'][0]['message']['content']
            
            # Extract JSON from response
            try:
                # Find JSON content between curly braces
                json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
                # Clean up the JSON string
                json_str = json_str.strip()
                # Remove any markdown code block indicators
                json_str = json_str.replace('```json', '').replace('```', '')
                # Parse the JSON
                result = json.loads(json_str)
                
                # Validate result structure
                required_keys = ['definition', 'description', 'tags']
                if not all(key in result for key in required_keys):
                    raise ValueError("Missing required keys in AI response")
                
                # Ensure tags is a list
                if isinstance(result['tags'], str):
                    result['tags'] = [tag.strip() for tag in result['tags'].split(',')]
                
                # Cache the result
                self.cache[acronym] = result
                return result
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error for {acronym}: {str(e)}")
                print(f"Raw response: {response_text}")
                raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error for {acronym}: {str(e)}")
            raise Exception(f"Error connecting to Grok API for acronym {acronym}: {str(e)}")
        except Exception as e:
            print(f"Error in Grok API for {acronym}: {str(e)}")
            raise Exception(f"Error generating content for acronym {acronym}: {str(e)}")
    
    def clear_cache(self):
        """Clear the results cache"""
        self.cache = {} 