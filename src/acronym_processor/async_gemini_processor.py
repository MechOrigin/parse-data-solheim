import asyncio
import time
import json
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime
import google.generativeai as genai
from pathlib import Path
import aiohttp
from tqdm import tqdm
from src.acronym_processor.validators import AcronymValidator
from src.acronym_processor.api_key_cluster import APIKeyCluster
import random
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AsyncGeminiAcronymProcessor:
    """
    An asynchronous class to process acronyms using Google's Gemini API with load balancing
    across multiple API keys.
    """
    
    def __init__(
        self,
        output_dir: str = "output/acronyms",
        max_retries: Optional[int] = None,
        requests_per_minute: Optional[int] = None,
        max_concurrent: Optional[int] = None,
        validate_results: Optional[bool] = None,
        min_description_length: Optional[int] = None,
        min_related_terms: Optional[int] = None,
        daily_limit: Optional[int] = None
    ):
        """
        Initialize the AsyncGeminiAcronymProcessor.
        
        Args:
            output_dir (str): Directory to save results
            max_retries (int): Maximum number of retries for failed requests
            requests_per_minute (int): Maximum requests per minute per API key
            max_concurrent (int): Maximum number of concurrent API calls
            validate_results (bool): Whether to validate results
            min_description_length (int): Minimum length for description field
            min_related_terms (int): Minimum number of related terms
            daily_limit (int): Maximum requests per day per API key
        """
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment variables
        self.max_retries = max_retries or int(os.getenv('MAX_RETRIES', '3'))
        self.requests_per_minute = requests_per_minute or int(os.getenv('RATE_LIMIT_PER_KEY', '60'))
        self.max_concurrent = max_concurrent or int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
        self.validate_results = validate_results if validate_results is not None else os.getenv('VALIDATE_RESULTS', 'true').lower() == 'true'
        self.min_description_length = min_description_length or int(os.getenv('MIN_DESCRIPTION_LENGTH', '20'))
        self.min_related_terms = min_related_terms or int(os.getenv('MIN_RELATED_TERMS', '1'))
        self.daily_limit = daily_limit or int(os.getenv('DAILY_LIMIT_PER_KEY', '60'))
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Initialize API key cluster
        self.api_cluster = APIKeyCluster.from_env(
            daily_limit=self.daily_limit,
            rate_limit=self.requests_per_minute
        )
        
        # Initialize validator if needed
        self.validator = None
        if self.validate_results:
            self.validator = AcronymValidator(
                min_description_length=self.min_description_length,
                min_related_terms=self.min_related_terms
            )
        
        # Initialize statistics
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "validation": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "errors": {
                    "structure": 0,
                    "content": 0,
                    "json": 0
                }
            }
        }
        
        logger.info(f"Initialized AsyncGeminiAcronymProcessor with {len(self.api_cluster.keys)} API keys")
        logger.info(f"Configuration: max_retries={self.max_retries}, requests_per_minute={self.requests_per_minute}, "
                   f"max_concurrent={self.max_concurrent}, validate_results={self.validate_results}")
    
    async def process_acronym(self, acronym: str) -> Dict[str, Optional[Dict]]:
        """
        Process a single acronym.
        
        Args:
            acronym: The acronym to process
            
        Returns:
            Dictionary with processing results
        """
        self.stats["total"] += 1
        
        # Check if already processed
        output_file = self.output_dir / f"{acronym}.json"
        if output_file.exists():
            return {"success": True, "acronym": acronym, "message": "Already processed"}
        
        # Check for error file
        error_file = self.output_dir / f"{acronym}_error.json"
        if error_file.exists():
            return {"success": False, "acronym": acronym, "message": "Previously failed"}
        
        async with self.semaphore:
            for attempt in range(self.max_retries):
                try:
                    # Get next available API key
                    api_key = await asyncio.get_event_loop().run_in_executor(
                        None, self.api_cluster.wait_for_available_key
                    )
                    
                    if not api_key:
                        return {
                            "success": False,
                            "acronym": acronym,
                            "error": "No available API keys",
                            "attempt": attempt + 1
                        }
                    
                    # Configure Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.0-pro')
                    
                    # Generate prompt
                    prompt = f"""
                    Please provide information about the acronym "{acronym}" in the following JSON format:
                    {{
                        "acronym": "{acronym}",
                        "full_name": "Full name of the acronym",
                        "description": "Detailed description of what it means and how it's used",
                        "context": "Common contexts or industries where it's used",
                        "related_terms": ["List", "of", "related", "terms"],
                        "industry": "Primary industry or field"
                    }}
                    
                    Ensure the response is valid JSON and the full name contains the acronym.
                    """
                    
                    # Get response
                    response = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: model.generate_content(prompt)
                    )
                    
                    # Parse response
                    result = json.loads(response.text)
                    result["processed_at"] = datetime.now().isoformat()
                    result["api_key"] = api_key[:8] + "..."  # Only show first 8 chars for security
                    result["attempt"] = attempt + 1
                    
                    # Clean and validate result
                    if self.validator:
                        result = self.validator.clean_result(result)
                        validation = self.validator.validate(result)
                        
                        if not validation["is_valid"]:
                            self.stats["validation"]["total"] += 1
                            self.stats["validation"]["invalid"] += 1
                            for error_type in validation["errors"]:
                                self.stats["validation"]["errors"][error_type] += 1
                            
                            if attempt < self.max_retries - 1:
                                continue
                            
                            return {
                                "success": False,
                                "acronym": acronym,
                                "error": "Validation failed",
                                "validation_errors": validation["errors"],
                                "attempt": attempt + 1
                            }
                        
                        self.stats["validation"]["total"] += 1
                        self.stats["validation"]["valid"] += 1
                    
                    # Save result
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                    
                    self.stats["success"] += 1
                    return {"success": True, "acronym": acronym, "result": result}
                    
                except Exception as e:
                    error_str = str(e)
                    retry_after = None
                    
                    # Extract retry_after from error message if available
                    if "retry_delay" in error_str:
                        try:
                            retry_after = int(error_str.split("seconds")[0].split()[-1])
                        except (ValueError, IndexError):
                            pass
                    
                    # Mark error in API key cluster
                    self.api_cluster.mark_error(api_key, e, retry_after)
                    
                    if attempt == self.max_retries - 1:
                        self.stats["failed"] += 1
                        return {
                            "success": False,
                            "acronym": acronym,
                            "error": error_str,
                            "attempt": attempt + 1
                        }
                    
                    # Wait before retrying
                    wait_time = (2 ** attempt) * float(os.getenv('RETRY_DELAY', '2'))
                    if retry_after:
                        wait_time = max(wait_time, retry_after)
                    await asyncio.sleep(wait_time)
    
    async def process_batch(self, acronyms: List[str]) -> List[Dict]:
        """
        Process a batch of acronyms concurrently.
        
        Args:
            acronyms: List of acronyms to process
            
        Returns:
            List of processing results
        """
        tasks = []
        for acronym in acronyms:
            task = asyncio.create_task(self.process_acronym(acronym))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Print summary
        logger.info("\nProcessing Summary:")
        logger.info(f"Total acronyms processed: {self.stats['total']}")
        logger.info(f"Successful: {self.stats['success']}")
        logger.info(f"Failed: {self.stats['failed']}")
        
        if self.validate_results:
            logger.info("\nValidation Summary:")
            logger.info(f"Total validated: {self.stats['validation']['total']}")
            logger.info(f"Valid: {self.stats['validation']['valid']}")
            logger.info(f"Invalid: {self.stats['validation']['invalid']}")
            logger.info("\nValidation Errors:")
            for error_type, count in self.stats['validation']['errors'].items():
                logger.info(f"{error_type}: {count}")
        
        # Print API key usage summary
        key_stats = self.api_cluster.get_key_stats()
        logger.info("\nAPI Key Usage Summary:")
        for key, stats in key_stats.items():
            logger.info(f"API Key {key[:8]}...: {stats['requests_today']} requests today, {stats['error_count']} errors")
        
        return results 