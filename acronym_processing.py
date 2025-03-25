import pandas as pd
import csv

def transform_acronym_data(input_file, output_file):
    """
    Transform and clean acronym data from CSV file.
    
    Parameters:
    input_file (str): Path to the input CSV file
    output_file (str): Path to save the transformed CSV file
    
    Returns:
    pd.DataFrame: The transformed dataframe
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully read {len(df)} rows from {input_file}")
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    # Convert Acronym and Definition columns to string type, replacing NaN with empty string
    df['Acronym'] = df['Acronym'].fillna('').astype(str)
    df['Definition'] = df['Definition'].fillna('').astype(str)
    
    # Check if required columns exist
    required_columns = ["Acronym", "Definition", "Description", "Tags", "Grade"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Warning: Missing columns: {missing_columns}")
        # Create missing columns with empty values
        for col in missing_columns:
            df[col] = ""
    
    # Import re for regular expressions
    import re

    # Process each row to clean up data and remove garbage
    for idx, row in df.iterrows():
        # Ensure acronym is uppercase and clean
        if pd.notna(row['Acronym']):
            # Keep only alphanumeric characters and spaces
            acronym = re.sub(r'[^\w\s]', '', row['Acronym'])
            df.at[idx, 'Acronym'] = acronym.strip().upper()
        
        # Clean up definition - remove HTML and garbage content
        if pd.notna(row['Definition']):
            definition = row['Definition']
            
            # Check if definition contains garbage-like content
            if (re.search(r'(\.com|\.html|cronymfinder|www\.)', definition, re.IGNORECASE) or 
                len(definition) > 100):  # Long definitions are often garbage
                definition = ""
            else:
                # Remove HTML tags
                definition = re.sub(r'<[^>]+>', '', definition)
                # Remove special characters and normalize whitespace
                definition = re.sub(r'[^\w\s\-\.,;:?!()]', '', definition)
                definition = re.sub(r'\s+', ' ', definition).strip()
            
            df.at[idx, 'Definition'] = definition
        
        # Clear descriptions entirely as requested
        df.at[idx, 'Description'] = ""
        
        # Clear tags entirely as requested
        df.at[idx, 'Tags'] = ""
        
        # Ensure grade is numeric and between 1-5
        if pd.notna(row['Grade']):
            try:
                grade = int(row['Grade'])
                df.at[idx, 'Grade'] = min(max(grade, 1), 5)  # Clamp between 1 and 5
            except ValueError:
                df.at[idx, 'Grade'] = 1  # Default to 1 if invalid
    
    # Remove rows where both Acronym and Definition are empty after stripping whitespace
    df = df[(df['Acronym'].str.strip() != '') | (df['Definition'].str.strip() != '')]
    print(f"Removed {len(df) - len(df)} rows with empty Acronym and Definition")
    
    # Select only the required columns and in the specified order
    result_df = df[required_columns]
    
    # Save to CSV
    try:
        result_df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"Successfully saved transformed data to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
    
    return result_df

def enrich_missing_data(df):
    """
    Enrich rows with missing data (optional function).
    This can be expanded to include external API calls or database lookups.
    
    Parameters:
    df (pd.DataFrame): Dataframe with acronym data
    
    Returns:
    pd.DataFrame: Enriched dataframe
    """
    for idx, row in df.iterrows():
        # If definition is missing
        if pd.isna(row['Definition']) or row['Definition'] == "":
            print(f"Warning: Missing definition for {row['Acronym']}")
            # Here you could add code to look up definitions from external sources
        
        # If description is missing
        if pd.isna(row['Description']) or row['Description'] == "":
            # Default description based on definition if available
            if pd.notna(row['Definition']) and row['Definition'] != "":
                df.at[idx, 'Description'] = f"Stands for {row['Definition']}."
                print(f"Added basic description for {row['Acronym']}")
        
        # If tags are missing
        if pd.isna(row['Tags']) or row['Tags'] == "":
            df.at[idx, 'Tags'] = "General"
            print(f"Added default tag for {row['Acronym']}")
        
        # If grade is missing
        if pd.isna(row['Grade']) or row['Grade'] == "":
            df.at[idx, 'Grade'] = 1
            print(f"Added default grade for {row['Acronym']}")
    
    return df

# Example usage
if __name__ == "__main__":
    import argparse
    import os
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process and transform acronym CSV data.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('--enrich', action='store_true', help='Enable data enrichment for missing values')
    
    args = parser.parse_args()
    
    # Generate output filename by adding '_processed' prefix to the input filename
    input_filename = os.path.basename(args.input_file)
    input_dirname = os.path.dirname(args.input_file)
    
    filename_no_ext, ext = os.path.splitext(input_filename)
    output_filename = f"{filename_no_ext}_processed{ext}"
    
    # If the input file included a directory path, include that in the output path
    if input_dirname:
        output_file = os.path.join(input_dirname, output_filename)
    else:
        output_file = output_filename
    
    print(f"Processing file: {args.input_file}")
    print(f"Output will be saved to: {output_file}")
    
    # Transform the data
    df = transform_acronym_data(args.input_file, output_file)
    
    # Optionally enrich missing data
    if df is not None and args.enrich:
        print("Performing data enrichment...")
        enriched_df = enrich_missing_data(df)
        
        # Generate enriched output filename
        enriched_filename = f"{filename_no_ext}_processed_enriched{ext}"
        if input_dirname:
            enriched_output = os.path.join(input_dirname, enriched_filename)
        else:
            enriched_output = enriched_filename
            
        enriched_df.to_csv(enriched_output, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"Data enrichment complete. Saved to {enriched_output}")
        
        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Total acronyms: {len(enriched_df)}")
        print(f"Acronyms by grade:")
        for grade in range(1, 6):
            count = len(enriched_df[enriched_df['Grade'] == grade])
            print(f"  Grade {grade}: {count} acronyms")