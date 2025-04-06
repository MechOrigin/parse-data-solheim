# Gemini Acronym Processor

A robust solution for processing large batches of acronyms using Google's Gemini API with multiple API keys, rate limiting, and result validation.

## Features

- Multiple API key rotation
- Rate limiting (60 requests per minute per key)
- Automatic retry with exponential backoff
- Progress tracking and resumable processing
- JSON output with detailed acronym information
- Comprehensive error handling
- Detailed logging
- Async processing with concurrent API calls
- Result validation and cleaning
- Command-line interface with configurable options

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   GEMINI_API_KEY_1=your_first_api_key
   GEMINI_API_KEY_2=your_second_api_key
   GEMINI_API_KEY_3=your_third_api_key
   GEMINI_API_KEY_4=your_fourth_api_key
   GEMINI_API_KEY_5=your_fifth_api_key
   ```

## Usage

### Basic Usage

1. Create a text file with acronyms (one per line):
   ```
   API
   CPU
   GPU
   ...
   ```

2. Run the processor:
   ```bash
   python src/acronym_processor/async_process_acronyms.py
   ```

### Command-line Options

The processor supports various command-line options:

```bash
python src/acronym_processor/async_process_acronyms.py --help
```

Available options:

- `--input`, `-i`: Path to input file with acronyms (default: `data/acronyms.txt`)
- `--output`, `-o`: Directory to save results (default: `output/acronyms`)
- `--max-retries`, `-r`: Maximum number of retries for failed requests (default: 3)
- `--requests-per-minute`, `-l`: Maximum requests per minute per API key (default: 60)
- `--max-concurrent`, `-c`: Maximum number of concurrent API calls (default: 5)
- `--no-validation`: Disable result validation
- `--min-description-length`: Minimum length for description field (default: 20)
- `--min-related-terms`: Minimum number of related terms (default: 1)

### Example

```bash
python src/acronym_processor/async_process_acronyms.py --input data/my_acronyms.txt --output output/results --max-concurrent 10
```

## Result Validation

The processor includes comprehensive validation for the results:

### Structure Validation

- Checks for required fields
- Validates field types
- Ensures fields are not empty
- Verifies minimum description length
- Ensures minimum number of related terms

### Content Validation

- Verifies that the full name contains the acronym
- Checks for placeholder text in descriptions
- Identifies duplicate related terms

### JSON Format Validation

- Ensures the result can be properly serialized to JSON

### Result Cleaning

The processor automatically cleans results by:

- Trimming whitespace from string fields
- Removing duplicate related terms
- Ensuring all required fields exist

## Output Format

The processor generates a JSON file with the following structure:

```json
{
  "acronym": "API",
  "full_name": "Application Programming Interface",
  "description": "A set of rules and protocols that allows different software applications to communicate with each other...",
  "context": "Software development, web services, mobile apps",
  "related_terms": ["REST API", "Web API", "API endpoint"],
  "industry": "Software Development, IT",
  "processed_at": "2024-04-05T12:34:56.789Z",
  "api_key_index": 0,
  "attempt": 1
}
```

## Validation Statistics

The processor provides validation statistics:

```
Validation Summary:
Total results: 100
Valid results: 95
Invalid results: 5
Error breakdown:
  Structure: 2
  Content: 3
  JSON: 0
```

## Implementation Details

### Rate Limiting

- 60 requests per minute per API key
- Automatic waiting when rate limit is reached
- Key rotation to maximize throughput

### Error Handling

- Automatic retry with exponential backoff
- Maximum 3 retry attempts
- Detailed error logging
- Failed requests are saved with error information

### Data Persistence

- Results are saved after each successful processing
- Processing can be resumed if interrupted
- Duplicate acronyms are skipped

## Best Practices

1. **API Key Management**
   - Use multiple API keys to increase throughput
   - Keep API keys secure in environment variables
   - Monitor usage per key

2. **Input Preparation**
   - Clean and validate acronyms before processing
   - Remove duplicates
   - Consider case sensitivity

3. **Resource Management**
   - Monitor memory usage for large batches
   - Use appropriate batch sizes
   - Implement proper error handling

## Limitations

- Free tier rate limits apply
- Response quality depends on Gemini API
- JSON parsing may fail for unformatted responses
- Network issues may affect processing

## Troubleshooting

1. **Rate Limit Errors**
   - Check API key usage
   - Verify rate limit settings
   - Consider adding more API keys

2. **JSON Parsing Errors**
   - Check response format
   - Verify prompt structure
   - Review error logs

3. **Network Issues**
   - Check internet connection
   - Verify API key validity
   - Review error logs

## Future Improvements

- Custom prompt templates
- Export to different formats (CSV, Excel)
- Web interface for monitoring
- API endpoint for processing
- Result caching
- Custom rate limiting rules
- Progress visualization 