import pytest
import asyncio
from pathlib import Path
from src.acronym_processor.async_gemini_processor import AsyncGeminiAcronymProcessor

@pytest.mark.asyncio
async def test_process_acronym_success(mock_gemini_client, mock_env_vars, temp_output_dir):
    processor = AsyncGeminiAcronymProcessor(
        output_dir=temp_output_dir,
        max_retries=3,
        requests_per_minute=60,
        max_concurrent=5
    )
    
    mock_gemini_client.return_value.generate_content.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"acronym": "API", "full_name": "Application Programming Interface", "description": "A set of rules and protocols", "context": "Software development", "related_terms": ["REST API"], "industry": "IT"}'
                }]
            }
        }]
    }
    
    result = await processor.process_acronym("API")
    assert result["success"]
    assert result["acronym"] == "API"
    assert result["full_name"] == "Application Programming Interface"
    
    # Check if result was saved
    output_file = temp_output_dir / "API.json"
    assert output_file.exists()

@pytest.mark.asyncio
async def test_process_acronym_validation_failure(mock_gemini_client, mock_env_vars, temp_output_dir):
    processor = AsyncGeminiAcronymProcessor(
        output_dir=temp_output_dir,
        max_retries=3,
        requests_per_minute=60,
        max_concurrent=5,
        validate_results=True,
        min_description_length=50
    )
    
    mock_gemini_client.return_value.generate_content.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"acronym": "API", "full_name": "Application Programming Interface", "description": "Too short", "context": "Software development", "related_terms": ["REST API"], "industry": "IT"}'
                }]
            }
        }]
    }
    
    result = await processor.process_acronym("API")
    assert not result["success"]
    assert "validation" in result["error"]

@pytest.mark.asyncio
async def test_process_acronyms_batch(mock_gemini_client, mock_env_vars, temp_output_dir):
    processor = AsyncGeminiAcronymProcessor(
        output_dir=temp_output_dir,
        max_retries=3,
        requests_per_minute=60,
        max_concurrent=5
    )
    
    mock_gemini_client.return_value.generate_content.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"acronym": "API", "full_name": "Application Programming Interface", "description": "A set of rules and protocols", "context": "Software development", "related_terms": ["REST API"], "industry": "IT"}'
                }]
            }
        }]
    }
    
    acronyms = ["API", "CPU", "GPU"]
    results = await processor.process_acronyms(acronyms)
    
    assert len(results) == 3
    assert all(r["success"] for r in results)
    assert len(list(temp_output_dir.glob("*.json"))) == 3

@pytest.mark.asyncio
async def test_rate_limiting(mock_gemini_client, mock_env_vars, temp_output_dir):
    processor = AsyncGeminiAcronymProcessor(
        output_dir=temp_output_dir,
        max_retries=3,
        requests_per_minute=2,  # Very low rate limit for testing
        max_concurrent=5
    )
    
    mock_gemini_client.return_value.generate_content.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"acronym": "API", "full_name": "Application Programming Interface", "description": "A set of rules and protocols", "context": "Software development", "related_terms": ["REST API"], "industry": "IT"}'
                }]
            }
        }]
    }
    
    acronyms = ["API", "CPU", "GPU", "RAM", "ROM"]
    start_time = asyncio.get_event_loop().time()
    results = await processor.process_acronyms(acronyms)
    end_time = asyncio.get_event_loop().time()
    
    assert len(results) == 5
    assert all(r["success"] for r in results)
    # Should take at least 1.5 minutes due to rate limiting (2 requests per minute)
    assert end_time - start_time >= 90

@pytest.mark.asyncio
async def test_api_key_rotation(mock_gemini_client, mock_env_vars, temp_output_dir):
    processor = AsyncGeminiAcronymProcessor(
        output_dir=temp_output_dir,
        max_retries=3,
        requests_per_minute=60,
        max_concurrent=5
    )
    
    mock_gemini_client.return_value.generate_content.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": '{"acronym": "API", "full_name": "Application Programming Interface", "description": "A set of rules and protocols", "context": "Software development", "related_terms": ["REST API"], "industry": "IT"}'
                }]
            }
        }]
    }
    
    acronyms = ["API", "CPU", "GPU"]
    results = await processor.process_acronyms(acronyms)
    
    assert len(results) == 3
    assert all(r["success"] for r in results)
    
    # Check that API keys were rotated
    api_key_indices = [r["api_key_index"] for r in results]
    assert len(set(api_key_indices)) > 1  # Should use multiple API keys

@pytest.mark.asyncio
async def test_error_handling(mock_gemini_client, mock_env_vars, temp_output_dir):
    processor = AsyncGeminiAcronymProcessor(
        output_dir=temp_output_dir,
        max_retries=3,
        requests_per_minute=60,
        max_concurrent=5
    )
    
    # Simulate API error
    mock_gemini_client.return_value.generate_content.side_effect = Exception("API Error")
    
    result = await processor.process_acronym("API")
    assert not result["success"]
    assert "error" in result
    assert result["attempt"] == 1  # Should have tried once
    
    # Check error was logged
    error_file = temp_output_dir / "API_error.json"
    assert error_file.exists() 