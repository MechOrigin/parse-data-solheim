import os
import asyncio
import json
import argparse
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from async_gemini_processor import AsyncGeminiAcronymProcessor
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

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process acronyms using Google Gemini API')
    parser.add_argument('--input', '-i', type=str, default='data/acronyms.txt',
                        help='Path to input file with acronyms (one per line)')
    parser.add_argument('--output', '-o', type=str, default='output/acronyms',
                        help='Directory to save results')
    parser.add_argument('--max-retries', '-r', type=int, default=3,
                        help='Maximum number of retries for failed requests')
    parser.add_argument('--requests-per-minute', '-l', type=int, default=60,
                        help='Maximum requests per minute per API key')
    parser.add_argument('--max-concurrent', '-c', type=int, default=5,
                        help='Maximum number of concurrent API calls')
    parser.add_argument('--no-validation', action='store_true',
                        help='Disable result validation')
    parser.add_argument('--min-description-length', type=int, default=20,
                        help='Minimum length for description field')
    parser.add_argument('--min-related-terms', type=int, default=1,
                        help='Minimum number of related terms')
    parser.add_argument('--daily-limit', type=int, default=60,
                        help='Maximum requests per day per API key')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize processor with API key cluster
    processor = AsyncGeminiAcronymProcessor(
        output_dir=args.output,
        max_retries=args.max_retries,
        requests_per_minute=args.requests_per_minute,
        max_concurrent=args.max_concurrent,
        validate_results=not args.no_validation,
        min_description_length=args.min_description_length,
        min_related_terms=args.min_related_terms,
        daily_limit=args.daily_limit
    )
    
    # Load acronyms from file
    acronyms_file = Path(args.input)
    if not acronyms_file.exists():
        raise FileNotFoundError(f"Acronyms file not found: {acronyms_file}")
    
    acronyms = load_acronyms(str(acronyms_file))
    logger.info(f"Loaded {len(acronyms)} acronyms to process")
    
    # Process acronyms
    results = await processor.process_acronyms(acronyms)
    
    # Print summary
    successful = sum(1 for r in results if r.get('success', False))
    failed = len(results) - successful
    
    logger.info("\nProcessing Summary:")
    logger.info(f"Total acronyms processed: {len(results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    
    # Print API key usage summary
    key_stats = processor.api_cluster.get_key_stats()
    logger.info("\nAPI Key Usage Summary:")
    for key, stats in key_stats.items():
        logger.info(f"API Key {key[:8]}...: {stats['requests_today']} requests today, {stats['error_count']} errors")
    
    # Print validation summary if validation is enabled
    if processor.validator:
        logger.info("\nValidation Summary:")
        logger.info(f"Total results: {processor.stats['validation']['total']}")
        logger.info(f"Valid results: {processor.stats['validation']['valid']}")
        logger.info(f"Invalid results: {processor.stats['validation']['invalid']}")
        logger.info("Error breakdown:")
        for category, count in processor.stats['validation']['errors'].items():
            logger.info(f"  {category.capitalize()}: {count}")

if __name__ == "__main__":
    asyncio.run(main()) 