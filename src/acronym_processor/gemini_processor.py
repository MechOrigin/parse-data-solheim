import time
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import google.generativeai as genai
from pathlib import Path
from api_key_cluster import APIKeyCluster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeminiAcronymProcessor:
    """
    A class to process acronyms using Google's Gemini API with load balancing
    across multiple API keys.
    """
    
    def __init__(
        self,
        api_cluster: APIKeyCluster,
        output_dir: str = "output",
        max_retries: int = 3,
        requests_per_minute: int = 60
    ):
        """
        Initialize the GeminiAcronymProcessor.
        
        Args:
            api_cluster (APIKeyCluster): Cluster of API keys for load balancing
            output_dir (str): Directory to save results
            max_retries (int): Maximum number of retries for failed requests
            requests_per_minute (int): Maximum requests per minute per API key
        """
        self.api_cluster = api_cluster
        self.max_retries = max_retries
        self.requests_per_minute = requests_per_minute
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results tracking
        self.results_file = self.output_dir / f"acronym_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.processed_acronyms = self._load_processed_acronyms()
        
        logger.info(f"Initialized GeminiAcronymProcessor with API key cluster")
    
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
                # Get next available API key
                api_key = self.api_cluster.get_next_key()
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
                model = genai.GenerativeModel('gemini-1.0-pro')
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
                    'api_key': api_key[:8] + '...',  # Only show first 8 chars for security
                    'attempt': attempt + 1,
                    'success': True
                })
                
                self.processed_acronyms[acronym] = result
                
                # Save after each successful processing
                self._save_results(list(self.processed_acronyms.values()))
                
                logger.info(f"Successfully processed acronym: {acronym}")
                return result
                
            except Exception as e:
                logger.error(f"Error processing {acronym} (attempt {attempt + 1}): {str(e)}")
                # Mark the API key as having an error
                self.api_cluster.mark_error(api_key)
                
                if attempt == self.max_retries - 1:
                    return {
                        'acronym': acronym,
                        'error': str(e),
                        'processed_at': datetime.now().isoformat(),
                        'attempt': attempt + 1,
                        'success': False
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