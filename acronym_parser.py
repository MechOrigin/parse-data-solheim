import pandas as pd
import os
import csv
import re
import argparse

def parse_acronyms(input_filename, output_filename, source_type=None):
    """
    Parse acronyms from a CSV file and output them to a new file.
    
    Args:
        input_filename (str): Path to the input CSV file
        output_filename (str): Path to the output CSV file
        source_type (str, optional): Type of source file - 'structured' or 'unstructured'
                                    If None, will auto-detect
    """
    try:
        print(f"Reading file: {input_filename}")
        
        # Read the CSV file
        df = pd.read_csv(input_filename, encoding='utf-8', on_bad_lines='skip', low_memory=False)
        
        print(f"CSV file has {df.shape[0]} rows and {df.shape[1]} columns")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Auto-detect source type if not specified
        if source_type is None:
            source_type = detect_source_type(df)
            print(f"Auto-detected source type: {source_type}")
        
        # Process based on source type
        if source_type == 'structured':
            # If the file is already structured with acronym columns
            process_structured_file(df, output_filename)
        else:
            # If the file is the unstructured data with many columns
            process_unstructured_file(df, output_filename)
        
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def detect_source_type(df):
    """Detect whether the file is structured or unstructured."""
    # Check if key acronym columns exist
    key_columns = ["Acronym", "Definition"]
    if all(col in df.columns for col in key_columns):
        return 'structured'
    
    # If we have text columns that might contain acronyms
    potential_text_columns = ['H1-1', 'H2-1', 'Title 1', 'Meta Description 1', 'Content Type']
    if any(col in df.columns for col in potential_text_columns):
        return 'unstructured'
    
    # Default to unstructured
    return 'unstructured'

def process_structured_file(df, output_filename):
    """Process a file that already has acronym structure."""
    # Required columns for the output
    required_columns = ["Acronym", "Definition", "Description", "Tags", "Grade"]
    existing_columns = df.columns.tolist()
    
    # Create a new DataFrame with only the required columns
    output_df = pd.DataFrame()
    
    # Copy existing columns or create empty ones
    for col in required_columns:
        if col in existing_columns:
            output_df[col] = df[col]
        else:
            output_df[col] = ""
    
    # Clean the data
    for col in output_df.columns:
        if output_df[col].dtype == 'object':  # For string columns
            output_df[col] = output_df[col].fillna("").astype(str).str.strip()
    
    # Fill numeric columns with default values
    if 'Grade' in output_df.columns:
        output_df['Grade'] = pd.to_numeric(output_df['Grade'], errors='coerce').fillna(0).astype(int)
    
    # Write to output file
    write_output(output_df, output_filename)

def process_unstructured_file(df, output_filename):
    """Extract acronyms from an unstructured file."""
    # Initialize an empty DataFrame for the output
    output_df = pd.DataFrame(columns=["Acronym", "Definition", "Description", "Tags", "Grade"])
    
    # Try to find acronyms in various text columns that might contain them
    potential_text_columns = [
        'H1-1', 'H2-1', 'H2-2', 'Title 1', 'Meta Description 1', 
        'Meta Keywords 1', 'Address', 'Content Type'
    ]
    text_columns = [col for col in potential_text_columns if col in df.columns]
    
    if not text_columns:
        # If none of our expected text columns exist, use all string columns
        text_columns = [col for col in df.columns if df[col].dtype == 'object']
        print(f"Using all string columns as potential text sources: {', '.join(text_columns)}")
    
    # Regular expression for finding acronyms (2-6 uppercase letters)
    acronym_pattern = re.compile(r'\b[A-Z]{2,6}\b')
    
    extracted_acronyms = set()
    
    # Extract acronyms from text columns
    for _, row in df.iterrows():
        for col in text_columns:
            text = str(row[col])
            if not pd.isna(text) and text:
                acronyms = acronym_pattern.findall(text)
                for acronym in acronyms:
                    if acronym not in extracted_acronyms and not is_common_word(acronym):
                        extracted_acronyms.add(acronym)
                        # Try to extract context for description
                        context = extract_context(text, acronym)
                        # Add a new row to the output DataFrame
                        new_row = {
                            "Acronym": acronym,
                            "Definition": "",  # These would need external lookup
                            "Description": context,
                            "Tags": get_tags_from_source(text, col),
                            "Grade": 0
                        }
                        output_df = pd.concat([output_df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Write to output file
    write_output(output_df, output_filename)

def is_common_word(word):
    """Check if the "acronym" is actually just a common word in all caps."""
    common_words = {'AND', 'THE', 'FOR', 'WITH', 'THIS', 'THAT', 'FROM', 'HAVE'}
    return word in common_words

def extract_context(text, acronym):
    """Try to extract some context around the acronym."""
    # Find the position of the acronym
    pos = text.find(acronym)
    if pos == -1:
        return ""
    
    # Extract some text around the acronym (50 chars before and after)
    start = max(0, pos - 50)
    end = min(len(text), pos + len(acronym) + 50)
    context = text[start:end]
    
    # Add ellipsis if we truncated the text
    if start > 0:
        context = f"...{context}"
    if end < len(text):
        context = f"{context}..."
    
    return context

def get_tags_from_source(text, column_name):
    """Generate tags based on the source column and content."""
    # Start with the column name as a tag
    tags = [column_name.replace('-', ' ').strip()]
    
    # Look for common categories in the text
    categories = [
        'tech', 'technology', 'medical', 'medicine', 'health', 'finance', 
        'business', 'education', 'science', 'computer', 'social', 'media'
    ]
    
    text_lower = text.lower()
    found_categories = [cat for cat in categories if cat in text_lower]
    
    # Combine all tags
    all_tags = tags + found_categories
    return ', '.join(all_tags[:3])  # Limit to 3 tags

def write_output(df, output_filename):
    """Write the output DataFrame to a CSV file."""
    print(f"Writing {len(df)} acronyms to {output_filename}")
    df.to_csv(output_filename, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Successfully wrote acronyms to {output_filename}")
    
    # Display the first few rows of processed data
    print("\nSample of processed data:")
    print(df.head())

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Parse acronyms from CSV files')
    parser.add_argument('--input', '-i', default=None, help='Input CSV filename')
    parser.add_argument('--output', '-o', default='parsed_acronyms.csv', help='Output CSV filename')
    parser.add_argument('--type', '-t', choices=['structured', 'unstructured'], 
                        default=None, help='Source type (will auto-detect if not specified)')
    
    args = parser.parse_args()
    
    # Get input filename
    input_filename = args.input
    if input_filename is None:
        # Try to find CSV files in the current directory
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files:
            print("No CSV files found in the current directory.")
            return
        
        # If there's only one CSV file, use it automatically
        if len(csv_files) == 1:
            input_filename = csv_files[0]
            print(f"Found CSV file: {input_filename}")
        else:
            # Let the user choose from available CSV files
            print("Multiple CSV files found. Please choose one:")
            for i, file in enumerate(csv_files, 1):
                print(f"{i}. {file}")
            
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(csv_files):
                input_filename = csv_files[choice-1]
            else:
                print("Invalid choice.")
                return
    
    # Run the parser
    success = parse_acronyms(input_filename, args.output, args.type)
    
    if success:
        print(f"\nAcronym parsing completed successfully!")
    else:
        print(f"\nAcronym parsing failed.")

if __name__ == "__main__":
    main()