import time
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import google.generativeai as genai
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeminiAcronymProcessor:
    """
    A class to process acronyms using Google's Gemini API with multiple API keys
    and rate limiting.
    """
    
    def __init__(
        self,
        api_keys: List[str],
        output_dir: str = "output",
        max_retries: int = 3,
        requests_per_minute: int = 60
    ):
        """
        Initialize the GeminiAcronymProcessor.
        
        Args:
            api_keys (List[str]): List of Gemini API keys to rotate through
            output_dir (str): Directory to save results
            max_retries (int): Maximum number of retries for failed requests
            requests_per_minute (int): Maximum requests per minute per API key
        """
        self.api_keys = api_keys
        self.current_key_index = 0
        self.requests_in_last_minute = 0
        self.last_minute_timestamp = time.time()
        self.max_retries = max_retries
        self.requests_per_minute = requests_per_minute
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results tracking
        self.results_file = self.output_dir / f"acronym_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.processed_acronyms = self._load_processed_acronyms()
        
        logger.info(f"Initialized GeminiAcronymProcessor with {len(api_keys)} API keys")
    
    def _load_processed_acronyms(self) -> Dict:
        """Load previously processed acronyms from results file."""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                return {item['acronym']: item for item in json.load(f)}
        return {}
    
    def _save_results(self, results: List[Dict]):
        """Save results to JSON file."""
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved {len(results)} results to {self.results_file}")
    
    def get_next_api_key(self) -> str:
        """Rotate through available API keys."""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def _check_rate_limit(self):
        """Check and handle rate limiting."""
        current_time = time.time()
        if current_time - self.last_minute_timestamp >= 60:
            self.requests_in_last_minute = 0
            self.last_minute_timestamp = current_time
        
        if self.requests_in_last_minute >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.last_minute_timestamp)
            logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            self.requests_in_last_minute = 0
            self.last_minute_timestamp = time.time()
    
    def process_acronym(self, acronym: str) -> Dict:
        """
        Process a single acronym using the Gemini API.
        
        Args:
            acronym (str): The acronym to process
            
        Returns:
            Dict: Results containing the acronym and its processed information
        """
        if acronym in self.processed_acronyms:
            logger.info(f"Skipping already processed acronym: {acronym}")
            return self.processed_acronyms[acronym]
        
        for attempt in range(self.max_retries):
            try:
                self._check_rate_limit()
                
                # Get next API key and configure
                api_key = self.get_next_api_key()
                genai.configure(api_key=api_key)
                
                # Prepare the prompt
                prompt = f"""
                Please provide the following information for the acronym "{acronym}":
                1. Full name/expansion
                2. Detailed description
                3. Common usage context
                4. Related terms or synonyms
                5. Industry/field of use
                
                Format the response as a JSON object with these keys:
                full_name, description, context, related_terms, industry
                """
                
                # Make the API call
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                
                # Parse and structure the response
                try:
                    result = json.loads(response.text)
                except json.JSONDecodeError:
                    # If response is not valid JSON, structure it manually
                    result = {
                        'full_name': '',
                        'description': response.text,
                        'context': '',
                        'related_terms': [],
                        'industry': ''
                    }
                
                # Add metadata
                result.update({
                    'acronym': acronym,
                    'processed_at': datetime.now().isoformat(),
                    'api_key_index': self.current_key_index,
                    'attempt': attempt + 1
                })
                
                self.requests_in_last_minute += 1
                self.processed_acronyms[acronym] = result
                
                # Save after each successful processing
                self._save_results(list(self.processed_acronyms.values()))
                
                logger.info(f"Successfully processed acronym: {acronym}")
                return result
                
            except Exception as e:
                logger.error(f"Error processing {acronym} (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    return {
                        'acronym': acronym,
                        'error': str(e),
                        'processed_at': datetime.now().isoformat(),
                        'attempt': attempt + 1
                    }
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def process_batch(self, acronyms: List[str]) -> List[Dict]:
        """
        Process a batch of acronyms.
        
        Args:
            acronyms (List[str]): List of acronyms to process
            
        Returns:
            List[Dict]: List of results for all processed acronyms
        """
        results = []
        total = len(acronyms)
        
        for i, acronym in enumerate(acronyms, 1):
            logger.info(f"Processing acronym {i}/{total}: {acronym}")
            result = self.process_acronym(acronym)
            results.append(result)
            
            # Progress update every 10 acronyms
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{total} acronyms processed ({(i/total)*100:.1f}%)")
        
        return results 