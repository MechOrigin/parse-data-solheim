import pandas as pd
import argparse
import os

def extract_grade2_acronyms(input_file, output_file=None):
    """
    Extracts all acronyms with Grade = 2 from the input CSV file.
    
    Parameters:
    input_file (str): Path to the input CSV file
    output_file (str, optional): Path to save the output CSV file. If not provided,
                                 will use input filename with '_grade2' appended.
    
    Returns:
    int: Number of Grade 2 acronyms found
    """
    try:
        # If output file is not specified, create one based on input filename
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_extracted_grade2.csv"
        
        print(f"Reading from: {input_file}")
        
        # Read the CSV file
        df = pd.read_csv(input_file, encoding='utf-8', low_memory=False)
        
        # Filter for Grade 2 acronyms only
        df['Grade'] = pd.to_numeric(df['Grade'], errors='coerce')
        grade2_df = df[df['Grade'] == 2]
        
        # Sort alphabetically by Acronym
        grade2_df = grade2_df.sort_values(by='Acronym')
        
        # Save to output file
        grade2_df.to_csv(output_file, index=False)
        
        # Get count
        count = len(grade2_df)
        
        print(f"Found {count} Grade 2 acronyms.")
        print(f"Saved to: {output_file}")
        
        return count
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 0

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Extract Grade 2 acronyms from a CSV file.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('--output_file', '-o', help='Path to save the output CSV file (optional)')
    
    args = parser.parse_args()
    
    # Run the extraction
    extract_grade2_acronyms(args.input_file, args.output_file) 