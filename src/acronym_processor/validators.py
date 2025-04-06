import re
import json
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AcronymValidator:
    """
    Validator for acronym responses from the Gemini API.
    Checks structure, content quality, and format.
    """
    
    def __init__(self, min_description_length: int = 20, min_related_terms: int = 1):
        """
        Initialize the validator.
        
        Args:
            min_description_length (int): Minimum length for description field
            min_related_terms (int): Minimum number of related terms
        """
        self.min_description_length = min_description_length
        self.min_related_terms = min_related_terms
        
        # Required fields in the response
        self.required_fields = [
            'acronym', 
            'full_name', 
            'description', 
            'context', 
            'related_terms', 
            'industry'
        ]
        
        # Field types for validation
        self.field_types = {
            'acronym': str,
            'full_name': str,
            'description': str,
            'context': str,
            'related_terms': list,
            'industry': str
        }
    
    def validate_structure(self, result: Dict) -> Tuple[bool, List[str]]:
        """
        Validate the structure of the result.
        
        Args:
            result (Dict): The result to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of errors)
        """
        errors = []
        
        # Check for required fields
        for field in self.required_fields:
            if field not in result:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in self.field_types.items():
            if field in result and not isinstance(result[field], expected_type):
                errors.append(f"Field '{field}' should be of type {expected_type.__name__}")
        
        # Check for empty fields
        for field in self.required_fields:
            if field in result:
                if field == 'related_terms':
                    if not result[field] or len(result[field]) < self.min_related_terms:
                        errors.append(f"Field '{field}' should have at least {self.min_related_terms} items")
                elif not result[field] or (isinstance(result[field], str) and result[field].strip() == ''):
                    errors.append(f"Field '{field}' is empty")
        
        # Check description length
        if 'description' in result and isinstance(result['description'], str):
            if len(result['description'].strip()) < self.min_description_length:
                errors.append(f"Description is too short (minimum {self.min_description_length} characters)")
        
        return len(errors) == 0, errors
    
    def validate_content(self, result: Dict) -> Tuple[bool, List[str]]:
        """
        Validate the content quality of the result.
        
        Args:
            result (Dict): The result to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of errors)
        """
        errors = []
        
        # Check if full_name contains the acronym
        if 'acronym' in result and 'full_name' in result:
            acronym = result['acronym'].strip().upper()
            full_name = result['full_name'].strip().upper()
            
            # Check if acronym is in full_name or vice versa
            if acronym not in full_name and full_name not in acronym:
                errors.append(f"Full name '{result['full_name']}' does not contain acronym '{result['acronym']}'")
        
        # Check for common issues in description
        if 'description' in result and isinstance(result['description'], str):
            description = result['description'].strip()
            
            # Check for placeholder text
            placeholder_patterns = [
                r'\[.*?\]',
                r'<.*?>',
                r'\{.*?\}',
                r'placeholder',
                r'example',
                r'sample'
            ]
            
            for pattern in placeholder_patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    errors.append(f"Description contains placeholder text matching pattern: {pattern}")
        
        # Check for duplicate related terms
        if 'related_terms' in result and isinstance(result['related_terms'], list):
            seen = set()
            duplicates = []
            
            for term in result['related_terms']:
                term_lower = term.lower().strip()
                if term_lower in seen:
                    duplicates.append(term)
                seen.add(term_lower)
            
            if duplicates:
                errors.append(f"Duplicate related terms found: {', '.join(duplicates)}")
        
        return len(errors) == 0, errors
    
    def validate_json_format(self, result: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that the result can be properly serialized to JSON.
        
        Args:
            result (Dict): The result to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of errors)
        """
        errors = []
        
        try:
            # Try to serialize to JSON
            json.dumps(result)
        except (TypeError, ValueError) as e:
            errors.append(f"JSON serialization error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def validate(self, result: Dict) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Perform all validations on the result.
        
        Args:
            result (Dict): The result to validate
            
        Returns:
            Tuple[bool, Dict[str, List[str]]]: (is_valid, dict of validation errors by category)
        """
        structure_valid, structure_errors = self.validate_structure(result)
        content_valid, content_errors = self.validate_content(result)
        json_valid, json_errors = self.validate_json_format(result)
        
        all_errors = {
            'structure': structure_errors,
            'content': content_errors,
            'json': json_errors
        }
        
        is_valid = structure_valid and content_valid and json_valid
        
        if not is_valid:
            logger.warning(f"Validation failed for acronym '{result.get('acronym', 'UNKNOWN')}': {sum(len(errors) for errors in all_errors.values())} errors")
            for category, errors in all_errors.items():
                if errors:
                    logger.warning(f"{category.capitalize()} errors: {', '.join(errors)}")
        
        return is_valid, all_errors
    
    def clean_result(self, result: Dict) -> Dict:
        """
        Clean the result by fixing common issues.
        
        Args:
            result (Dict): The result to clean
            
        Returns:
            Dict: The cleaned result
        """
        cleaned = result.copy()
        
        # Clean string fields
        for field in ['acronym', 'full_name', 'description', 'context', 'industry']:
            if field in cleaned and isinstance(cleaned[field], str):
                cleaned[field] = cleaned[field].strip()
        
        # Clean related terms
        if 'related_terms' in cleaned and isinstance(cleaned['related_terms'], list):
            # Remove duplicates while preserving order
            seen = set()
            cleaned['related_terms'] = [term for term in cleaned['related_terms'] 
                                       if not (term.lower().strip() in seen or seen.add(term.lower().strip()))]
            
            # Remove empty terms
            cleaned['related_terms'] = [term for term in cleaned['related_terms'] if term.strip()]
        
        # Ensure all required fields exist
        for field in self.required_fields:
            if field not in cleaned:
                if field == 'related_terms':
                    cleaned[field] = []
                else:
                    cleaned[field] = ''
        
        return cleaned 