import pytest
import pandas as pd
from src.processing.acronym_parser import parse_acronyms, detect_source_type, process_structured_file, process_unstructured_file
import os
import tempfile

def test_parse_acronyms():
    # Create a temporary CSV file for testing
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as f:
        f.write("Acronym,Definition\nNASA,National Aeronautics and Space Administration")
        input_file = f.name
    
    output_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False).name
    
    try:
        # Test the function
        result = parse_acronyms(input_file, output_file)
        assert result == True
        
        # Verify output exists
        assert os.path.exists(output_file)
        
        # Clean up
        os.unlink(input_file)
        os.unlink(output_file)
    except Exception as e:
        # Clean up even if test fails
        if os.path.exists(input_file):
            os.unlink(input_file)
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

def test_detect_source_type():
    # Test structured data
    df_structured = pd.DataFrame({
        "Acronym": ["NASA"],
        "Definition": ["National Aeronautics and Space Administration"]
    })
    assert detect_source_type(df_structured) == 'structured'
    
    # Test unstructured data
    df_unstructured = pd.DataFrame({
        "H1-1": ["NASA stands for National Aeronautics and Space Administration"]
    })
    assert detect_source_type(df_unstructured) == 'unstructured' 