import pandas as pd
import argparse
import os

def extract_grade3_acronyms(input_file, output_file=None):
    """
    Extracts all acronyms with Grade = 3 from the input CSV file.
    
    Parameters:
    input_file (str): Path to the input CSV file
    output_file (str, optional): Path to save the output CSV file. If not provided,
                                 will use input filename with '_grade3' appended.
    
    Returns:
    int: Number of Grade 3 acronyms found
    """
    try:
        # If output file is not specified, create one based on input filename
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_extracted_grade3.csv"
        
        print(f"Reading from: {input_file}")
        
        # Read the CSV file
        df = pd.read_csv(input_file, encoding='utf-8', low_memory=False)
        
        # Filter for Grade 3 acronyms only
        df['Grade'] = pd.to_numeric(df['Grade'], errors='coerce')
        grade3_df = df[df['Grade'] == 3]
        
        # Sort alphabetically by Acronym
        grade3_df = grade3_df.sort_values(by='Acronym')
        
        # Save to output file
        grade3_df.to_csv(output_file, index=False)
        
        # Get count
        count = len(grade3_df)
        
        print(f"Found {count} Grade 3 acronyms.")
        print(f"Saved to: {output_file}")
        
        return count
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 0

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Extract Grade 3 acronyms from a CSV file.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('--output_file', '-o', help='Path to save the output CSV file (optional)')
    
    args = parser.parse_args()
    
    # Run the extraction
    extract_grade3_acronyms(args.input_file, args.output_file)