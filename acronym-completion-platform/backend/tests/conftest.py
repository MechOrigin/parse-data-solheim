import os
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pandas as pd
from typing import Generator, AsyncGenerator
from main import app

# Test data
TEST_ACRONYMS = [
    {
        "acronym": "ABC",
        "definition": "Test Definition 1",
        "description": "Test Description 1",
        "tags": "tag1,tag2",
        "grade": "3"
    },
    {
        "acronym": "XYZ",
        "definition": "Test Definition 2",
        "description": "Test Description 2",
        "tags": "tag3,tag4",
        "grade": "4"
    }
]

@pytest.fixture
def test_csv_path(tmp_path) -> str:
    """Create a temporary CSV file for testing."""
    df = pd.DataFrame(TEST_ACRONYMS)
    csv_path = tmp_path / "test_acronyms.csv"
    df.to_csv(csv_path, index=False)
    return str(csv_path)

@pytest.fixture
def auth_token(test_client) -> str:
    """Get authentication token for testing."""
    response = test_client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

@pytest.fixture
def test_client() -> Generator:
    """Create a TestClient instance for synchronous tests."""
    with TestClient(app) as client:
        # Get auth token
        response = client.post(
            "/token",
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        # Set default headers with auth token
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Create an AsyncClient instance for async tests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get auth token
        response = await client.post(
            "/token",
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        # Set default headers with auth token
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")

@pytest.fixture
def mock_csv_data():
    """Return mock CSV data for testing."""
    return TEST_ACRONYMS

@pytest.fixture
def mock_processed_results():
    """Return mock processed results for testing."""
    return [
        {
            **acronym,
            "enriched_definition": f"Enriched {acronym['definition']}",
            "enriched_description": f"Enriched {acronym['description']}"
        }
        for acronym in TEST_ACRONYMS
    ]
