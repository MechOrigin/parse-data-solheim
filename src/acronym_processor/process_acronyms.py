import os
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from gemini_processor import GeminiAcronymProcessor
from api_key_cluster import APIKeyCluster
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_acronyms(file_path: str) -> List[str]:
    """Load acronyms from a file."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize API key cluster for load balancing
    api_cluster = APIKeyCluster.from_env(
        prefix="GEMINI_API_KEY_",
        daily_limit=60,
        rate_limit=60
    )
    logger.info(f"Initialized API key cluster with {len(api_cluster.keys)} keys")
    
    # Initialize processor
    processor = GeminiAcronymProcessor(
        api_cluster=api_cluster,
        output_dir="output/acronyms",
        max_retries=3,
        requests_per_minute=60
    )
    
    # Load acronyms from file
    acronyms_file = Path("data/acronyms.txt")
    if not acronyms_file.exists():
        raise FileNotFoundError(f"Acronyms file not found: {acronyms_file}")
    
    acronyms = load_acronyms(str(acronyms_file))
    logger.info(f"Loaded {len(acronyms)} acronyms to process")
    
    # Process acronyms
    results = processor.process_batch(acronyms)
    
    # Print summary
    successful = sum(1 for r in results if r.get('success', False))
    failed = len(results) - successful
    
    logger.info("\nProcessing Summary:")
    logger.info(f"Total acronyms processed: {len(results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    
    # Print API key usage summary
    key_stats = api_cluster.get_key_stats()
    logger.info("\nAPI Key Usage Summary:")
    for key, stats in key_stats.items():
        logger.info(f"API Key {key[:8]}...: {stats['requests_today']} requests today, {stats['error_count']} errors")

if __name__ == "__main__":
    main() 