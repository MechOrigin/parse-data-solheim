import pytest
import pandas as pd
from src.grading.acronym_grader import grade_acronyms
import os
import tempfile

def test_grade_acronyms():
    # Create a temporary input CSV file for testing
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as f:
        f.write("Acronym,Definition,Description,Tags\n")
        f.write("NASA,National Aeronautics and Space Administration,Space agency,aviation government")
        input_file = f.name
    
    output_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False).name
    
    try:
        # Test the function
        grade_acronyms(input_file, output_file)
        
        # Verify output exists and contains expected data
        assert os.path.exists(output_file)
        df = pd.read_csv(output_file)
        assert len(df) > 0
        assert 'NASA' in df['Acronym'].values
        
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