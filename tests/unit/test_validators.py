import pytest
from src.acronym_processor.validators import AcronymValidator

def test_validate_structure_valid(sample_acronym_data):
    validator = AcronymValidator()
    result = validator.validate_structure(sample_acronym_data)
    assert result["is_valid"]
    assert not result["errors"]

def test_validate_structure_missing_field():
    validator = AcronymValidator()
    data = {
        "acronym": "API",
        "full_name": "Application Programming Interface"
    }
    result = validator.validate_structure(data)
    assert not result["is_valid"]
    assert "description" in result["errors"]
    assert "context" in result["errors"]
    assert "related_terms" in result["errors"]
    assert "industry" in result["errors"]

def test_validate_structure_empty_field():
    validator = AcronymValidator()
    data = {
        "acronym": "API",
        "full_name": "Application Programming Interface",
        "description": "",
        "context": "Software development",
        "related_terms": ["REST API"],
        "industry": "IT"
    }
    result = validator.validate_structure(data)
    assert not result["is_valid"]
    assert "description" in result["errors"]

def test_validate_content_valid(sample_acronym_data):
    validator = AcronymValidator()
    result = validator.validate_content(sample_acronym_data)
    assert result["is_valid"]
    assert not result["errors"]

def test_validate_content_acronym_mismatch():
    validator = AcronymValidator()
    data = {
        "acronym": "API",
        "full_name": "Central Processing Unit",  # Wrong full name
        "description": "A set of rules and protocols",
        "context": "Software development",
        "related_terms": ["REST API"],
        "industry": "IT"
    }
    result = validator.validate_content(data)
    assert not result["is_valid"]
    assert "full_name" in result["errors"]

def test_validate_content_placeholder():
    validator = AcronymValidator()
    data = {
        "acronym": "API",
        "full_name": "Application Programming Interface",
        "description": "Please provide a description",  # Placeholder text
        "context": "Software development",
        "related_terms": ["REST API"],
        "industry": "IT"
    }
    result = validator.validate_content(data)
    assert not result["is_valid"]
    assert "description" in result["errors"]

def test_validate_json_format_valid(sample_acronym_data):
    validator = AcronymValidator()
    result = validator.validate_json_format(sample_acronym_data)
    assert result["is_valid"]
    assert not result["errors"]

def test_validate_json_format_invalid():
    validator = AcronymValidator()
    data = {
        "acronym": "API",
        "full_name": "Application Programming Interface",
        "description": "A set of rules and protocols",
        "context": "Software development",
        "related_terms": ["REST API"],
        "industry": "IT",
        "invalid_field": object()  # Non-serializable object
    }
    result = validator.validate_json_format(data)
    assert not result["is_valid"]
    assert "json" in result["errors"]

def test_clean_result(sample_acronym_data):
    validator = AcronymValidator()
    data = {
        "acronym": " API ",  # Extra whitespace
        "full_name": " Application Programming Interface ",
        "description": " A set of rules and protocols ",
        "context": " Software development ",
        "related_terms": [" REST API ", " REST API ", " Web API "],  # Duplicates and whitespace
        "industry": " IT "
    }
    cleaned = validator.clean_result(data)
    assert cleaned["acronym"] == "API"
    assert cleaned["full_name"] == "Application Programming Interface"
    assert cleaned["description"] == "A set of rules and protocols"
    assert cleaned["context"] == "Software development"
    assert cleaned["related_terms"] == ["REST API", "Web API"]
    assert cleaned["industry"] == "IT"

def test_validate_min_description_length():
    validator = AcronymValidator(min_description_length=50)
    data = {
        "acronym": "API",
        "full_name": "Application Programming Interface",
        "description": "A short description",  # Too short
        "context": "Software development",
        "related_terms": ["REST API"],
        "industry": "IT"
    }
    result = validator.validate_structure(data)
    assert not result["is_valid"]
    assert "description" in result["errors"]

def test_validate_min_related_terms():
    validator = AcronymValidator(min_related_terms=2)
    data = {
        "acronym": "API",
        "full_name": "Application Programming Interface",
        "description": "A set of rules and protocols",
        "context": "Software development",
        "related_terms": ["REST API"],  # Only one term
        "industry": "IT"
    }
    result = validator.validate_structure(data)
    assert not result["is_valid"]
    assert "related_terms" in result["errors"] 