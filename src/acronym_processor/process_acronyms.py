import os
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from gemini_processor import GeminiAcronymProcessor

def load_acronyms(file_path: str) -> List[str]:
    """Load acronyms from a file."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
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
    processor = GeminiAcronymProcessor(
        api_keys=api_keys,
        output_dir="output/acronyms",
        max_retries=3,
        requests_per_minute=60
    )
    
    # Load acronyms from file
    acronyms_file = Path("data/acronyms.txt")
    if not acronyms_file.exists():
        raise FileNotFoundError(f"Acronyms file not found: {acronyms_file}")
    
    acronyms = load_acronyms(str(acronyms_file))
    print(f"Loaded {len(acronyms)} acronyms to process")
    
    # Process acronyms
    results = processor.process_batch(acronyms)
    
    # Print summary
    successful = sum(1 for r in results if 'error' not in r)
    failed = len(results) - successful
    
    print("\nProcessing Summary:")
    print(f"Total acronyms processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Results saved to: {processor.results_file}")

if __name__ == "__main__":
    main() 