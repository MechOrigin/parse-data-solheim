import asyncio
import os
from dotenv import load_dotenv
from src.acronym_processor.async_gemini_processor import AsyncGeminiAcronymProcessor
from src.acronym_processor.validators import AcronymValidator

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the processor
    processor = AsyncGeminiAcronymProcessor(
        output_dir="output/acronyms",
        max_retries=3,
        requests_per_minute=60,
        max_concurrent=5,
        validate_results=True
    )
    
    # Test acronyms
    acronyms = ["API", "CRM", "HTML"]
    
    # Process each acronym
    for acronym in acronyms:
        print(f"\nProcessing acronym: {acronym}")
        result = await processor.process_acronym(acronym)
        print(f"Result: {result}")
        
        # If successful, print the details
        if result.get("success"):
            output_file = processor.output_dir / f"{acronym}.json"
            if output_file.exists():
                with open(output_file, 'r') as f:
                    data = f.read()
                    print(f"\nProcessed data for {acronym}:")
                    print(data)
        else:
            print(f"Failed to process {acronym}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main()) 