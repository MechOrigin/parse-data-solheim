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
from validators import AcronymValidator
from .api_key_cluster import APIKeyCluster
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AsyncGeminiAcronymProcessor:
    """
    An asynchronous class to process acronyms using Google's Gemini API with multiple API keys
    and rate limiting.
    """
    
    def __init__(
        self,
        output_dir: str = "output/acronyms",
        max_retries: int = 3,
        requests_per_minute: int = 60,
        max_concurrent: int = 5,
        validate_results: bool = True,
        min_description_length: int = 20,
        min_related_terms: int = 1,
        daily_limit: int = 60
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
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_retries = max_retries
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Initialize API key cluster
        self.api_cluster = APIKeyCluster.from_env(
            daily_limit=daily_limit,
            rate_limit=requests_per_minute
        )
        
        # Initialize validator if needed
        self.validator = None
        if validate_results:
            self.validator = AcronymValidator(
                min_description_length=min_description_length,
                min_related_terms=min_related_terms
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
                    model = genai.GenerativeModel('gemini-pro')
                    
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
                    result["api_key_index"] = list(self.api_cluster.keys.keys()).index(api_key)
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
                        except:
                            pass
                    
                    # Mark error for the API key
                    self.api_cluster.mark_error(api_key, e, retry_after)
                    
                    if attempt < self.max_retries - 1:
                        # Use exponential backoff with jitter
                        wait_time = min(30, 2 ** attempt + random.random())
                        logger.info(f"Waiting {wait_time:.1f} seconds before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    # Save error information
                    error_info = {
                        "acronym": acronym,
                        "error": str(e),
                        "attempt": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    with open(error_file, 'w') as f:
                        json.dump(error_info, f, indent=2)
                    
                    self.stats["failed"] += 1
                    return {
                        "success": False,
                        "acronym": acronym,
                        "error": str(e),
                        "attempt": attempt + 1
                    }
    
    async def process_acronyms(self, acronyms: List[str]) -> List[Dict[str, Optional[Dict]]]:
        """
        Process a list of acronyms concurrently.
        
        Args:
            acronyms: List of acronyms to process
            
        Returns:
            List of processing results
        """
        tasks = []
        with tqdm(total=len(acronyms), desc="Processing acronyms") as pbar:
            for acronym in acronyms:
                task = asyncio.create_task(self.process_acronym(acronym))
                task.add_done_callback(lambda _: pbar.update(1))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
        
        # Print summary
        print("\nProcessing Summary:")
        print(f"Total acronyms: {self.stats['total']}")
        print(f"Successful: {self.stats['success']}")
        print(f"Failed: {self.stats['failed']}")
        
        if self.validator:
            print("\nValidation Summary:")
            print(f"Total results: {self.stats['validation']['total']}")
            print(f"Valid results: {self.stats['validation']['valid']}")
            print(f"Invalid results: {self.stats['validation']['invalid']}")
            print("Error breakdown:")
            for error_type, count in self.stats['validation']['errors'].items():
                print(f"  {error_type}: {count}")
        
        # Print API key cluster health status
        health_status = self.api_cluster.get_health_status()
        print("\nAPI Key Cluster Health:")
        print(f"Total keys: {health_status['total_keys']}")
        print(f"Active keys: {health_status['active_keys']}")
        print(f"Quota limited keys: {health_status['quota_limited_keys']}")
        print(f"Daily limited keys: {health_status['daily_limited_keys']}")
        print(f"Minimum wait time: {health_status['min_wait_time']:.2f} seconds")
        
        print("\nAPI Key Usage:")
        for key, stats in health_status['keys'].items():
            print(f"\nKey {key[:8]}...:")
            print(f"  Requests today: {stats['requests_today']}/{stats['daily_limit']}")
            print(f"  Rate limit: {stats['rate_limit']} requests/minute")
            print(f"  Status: {'Active' if stats['is_active'] else 'Inactive'}")
            if stats['error_count'] > 0:
                print(f"  Errors: {stats['error_count']}")
            if stats['quota_reset_time']:
                print(f"  Quota reset: {stats['quota_reset_time']}")
        
        return results 