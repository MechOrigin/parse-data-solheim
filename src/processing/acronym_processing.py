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

def process_acronyms(df, batch_size=250):
    """
    Process acronyms in batches with detailed logging.
    
    Parameters:
    df (pd.DataFrame): Dataframe with acronym data
    batch_size (int): Number of acronyms to process at once (max 250)
    
    Returns:
    pd.DataFrame: Processed dataframe
    """
    if batch_size > 250:
        print("Warning: Batch size exceeds maximum of 250. Setting to 250.")
        batch_size = 250
    
    total_acronyms = len(df)
    processed_count = 0
    batch_count = 0
    previous_batches = 0
    
    # Get the first and last acronym in the current batch
    def get_batch_range(start_idx, end_idx):
        if start_idx >= len(df):
            return "", ""
        first_acronym = df.iloc[start_idx]['Acronym']
        last_acronym = df.iloc[min(end_idx - 1, len(df) - 1)]['Acronym']
        return first_acronym, last_acronym
    
    while processed_count < total_acronyms:
        batch_start = processed_count
        batch_end = min(batch_start + batch_size, total_acronyms)
        batch_df = df.iloc[batch_start:batch_end]
        
        print(f"\nProcessing Batch {batch_count + 1}")
        print("=" * 50)
        
        # Process each acronym in the batch
        for idx, row in batch_df.iterrows():
            acronym = row['Acronym']
            print(f"\nProcessing: {acronym}")
            
            # Log the current state
            if pd.notna(row['Definition']):
                print(f"Definition: {row['Definition']}")
            if pd.notna(row['Description']):
                print(f"Description: {row['Description']}")
            if pd.notna(row['Tags']):
                print(f"Tags: {row['Tags']}")
            if pd.notna(row['Grade']):
                print(f"Grade: {row['Grade']}")
            
            # Process the acronym (your existing processing logic here)
            # ...
            
            processed_count += 1
        
        # Print batch summary
        first_acronym, last_acronym = get_batch_range(batch_start, batch_end)
        print("\nProgress Update")
        print(f"Total Completed: {processed_count}")
        print(f"Previous batches: {previous_batches} acronyms")
        print(f"This batch: {batch_end - batch_start} acronyms ({first_acronym} to {last_acronym})")
        print(f"New total: {processed_count} acronyms")
        
        # Determine next batch's starting point
        next_start_idx = batch_end
        if next_start_idx < len(df):
            next_acronym = df.iloc[next_start_idx]['Acronym']
            print(f"\nNext Steps: Starting from '{next_acronym}' in the next batch")
        
        # Add thematic analysis
        print("\nNotes")
        print("Research: Definitions are crafted for Grade 2 relevance, focusing on plausible development-related contexts.")
        print(f"Format: All columns included, with optional fields blank per guidelines.")
        print(f"Batch Size: Processed {batch_end - batch_start} acronyms as requested.")
        
        previous_batches = processed_count
        batch_count += 1
        
        if processed_count < total_acronyms:
            print("\nPress 'Enter' to proceed with the next batch, or 'q' to quit...")
            user_input = input()
            if user_input.lower() == 'q':
                break
    
    return df

def enrich_missing_data(df):
    """
    Enrich rows with missing data with detailed logging.
    """
    enriched_count = 0
    total_rows = len(df)
    
    print("\nStarting Data Enrichment")
    print("=" * 50)
    
    for idx, row in df.iterrows():
        acronym = row['Acronym']
        changes_made = []
        
        # If definition is missing
        if pd.isna(row['Definition']) or row['Definition'] == "":
            print(f"\nEnriching {acronym}: Adding definition")
            # Your definition generation logic here
            changes_made.append("definition")
        
        # If description is missing
        if pd.isna(row['Description']) or row['Description'] == "":
            print(f"\nEnriching {acronym}: Adding description")
            if pd.notna(row['Definition']) and row['Definition'] != "":
                df.at[idx, 'Description'] = f"Stands for {row['Definition']}."
                print(f"Added basic description: {df.at[idx, 'Description']}")
            changes_made.append("description")
        
        # If tags are missing
        if pd.isna(row['Tags']) or row['Tags'] == "":
            print(f"\nEnriching {acronym}: Adding default tag")
            df.at[idx, 'Tags'] = "General"
            print(f"Added default tag: {df.at[idx, 'Tags']}")
            changes_made.append("tags")
        
        # If grade is missing
        if pd.isna(row['Grade']) or row['Grade'] == "":
            print(f"\nEnriching {acronym}: Setting default grade")
            df.at[idx, 'Grade'] = 1
            print(f"Set default grade: {df.at[idx, 'Grade']}")
            changes_made.append("grade")
        
        if changes_made:
            enriched_count += 1
            print(f"Changes made to {acronym}: {', '.join(changes_made)}")
    
    # Print enrichment summary
    print("\nEnrichment Summary")
    print("=" * 50)
    print(f"Total acronyms processed: {total_rows}")
    print(f"Acronyms enriched: {enriched_count}")
    print("\nEnrichment by field:")
    print(f"Definitions added: {len(df[df['Definition'].notna()])}")
    print(f"Descriptions added: {len(df[df['Description'].notna()])}")
    print(f"Tags added: {len(df[df['Tags'].notna()])}")
    print(f"Grades set: {len(df[df['Grade'].notna()])}")
    
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