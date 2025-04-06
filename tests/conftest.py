import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch

@pytest.fixture
def sample_acronym_data():
    return {
        "acronym": "API",
        "full_name": "Application Programming Interface",
        "description": "A set of rules and protocols that allows different software applications to communicate with each other.",
        "context": "Software development, web services, mobile apps",
        "related_terms": ["REST API", "Web API", "API endpoint"],
        "industry": "Software Development, IT",
        "processed_at": "2024-04-05T12:34:56.789Z",
        "api_key_index": 0,
        "attempt": 1
    }

@pytest.fixture
def mock_gemini_response():
    return {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": json.dumps({
                        "acronym": "API",
                        "full_name": "Application Programming Interface",
                        "description": "A set of rules and protocols that allows different software applications to communicate with each other.",
                        "context": "Software development, web services, mobile apps",
                        "related_terms": ["REST API", "Web API", "API endpoint"],
                        "industry": "Software Development, IT"
                    })
                }]
            }
        }]
    }

@pytest.fixture
def mock_api_keys():
    return {
        "GEMINI_API_KEY_1": "test_key_1",
        "GEMINI_API_KEY_2": "test_key_2",
        "GEMINI_API_KEY_3": "test_key_3"
    }

@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "output" / "acronyms"
    output_dir.mkdir(parents=True)
    return output_dir

@pytest.fixture
def mock_env_vars(monkeypatch, mock_api_keys):
    for key, value in mock_api_keys.items():
        monkeypatch.setenv(key, value)
    return mock_api_keys

@pytest.fixture
def mock_gemini_client():
    with patch("google.generativeai.GenerativeModel") as mock:
        yield mock

@pytest.fixture
def mock_aiohttp_session():
    with patch("aiohttp.ClientSession") as mock:
        yield mock

@pytest.fixture
def mock_tqdm():
    with patch("tqdm.tqdm") as mock:
        mock.return_value.__enter__.return_value = mock.return_value
        mock.return_value.__exit__.return_value = None
        yield mock 