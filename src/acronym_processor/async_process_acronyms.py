import os
import asyncio
import json
import argparse
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from async_gemini_processor import AsyncGeminiAcronymProcessor

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
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys from environment variables
    api_keys = [
        os.getenv('GEMINI_API_KEY_1'),
        os.getenv('GEMINI_API_KEY_2'),
        os.getenv('GEMINI_API_KEY_3'),
        os.getenv('GEMINI_API_KEY_4'),
        os.getenv('GEMINI_API_KEY_5')
    ]
    
    # Filter out None values
    api_keys = [key for key in api_keys if key]
    
    if not api_keys:
        raise ValueError("No API keys found in environment variables")
    
    # Initialize processor
    processor = AsyncGeminiAcronymProcessor(
        api_keys=api_keys,
        output_dir=args.output,
        max_retries=args.max_retries,
        requests_per_minute=args.requests_per_minute,
        max_concurrent=args.max_concurrent,
        validate_results=not args.no_validation,
        min_description_length=args.min_description_length,
        min_related_terms=args.min_related_terms
    )
    
    # Load acronyms from file
    acronyms_file = Path(args.input)
    if not acronyms_file.exists():
        raise FileNotFoundError(f"Acronyms file not found: {acronyms_file}")
    
    acronyms = load_acronyms(str(acronyms_file))
    print(f"Loaded {len(acronyms)} acronyms to process")
    
    # Process acronyms
    results = await processor.process_batch(acronyms)
    
    # Print summary
    successful = sum(1 for r in results if 'error' not in r)
    failed = len(results) - successful
    
    print("\nProcessing Summary:")
    print(f"Total acronyms processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Results saved to: {processor.results_file}")
    
    # Print API key usage summary
    print("\nAPI Key Usage Summary:")
    for i, usage in processor.key_usage.items():
        print(f"API Key {i+1}: {usage} requests")
    
    # Print validation summary if validation is enabled
    if processor.validate_results:
        print("\nValidation Summary:")
        print(f"Total results: {processor.validation_stats['total']}")
        print(f"Valid results: {processor.validation_stats['valid']}")
        print(f"Invalid results: {processor.validation_stats['invalid']}")
        print("Error breakdown:")
        for category, count in processor.validation_stats['errors'].items():
            print(f"  {category.capitalize()}: {count}")

if __name__ == "__main__":
    asyncio.run(main()) 