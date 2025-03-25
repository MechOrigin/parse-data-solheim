#!/usr/bin/env python3
"""
Acronym Sorter

This script processes a CSV file containing acronyms and sorts them so that
duplicate acronyms appear consecutively in the output file.

Usage:
    python acronym_sorter.py --input INPUT_FILE --output OUTPUT_FILE

Args:
    --input: Path to the input CSV file
    --output: Path to the output CSV file (sorted)
"""

import pandas as pd
import argparse
import sys


def sort_acronyms(input_file, output_file):
    """
    Reads a CSV file with acronyms, sorts it so duplicates are together,
    and writes the result to a new CSV file.

    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output CSV file
    """
    try:
        # Read the CSV file
        print(f"Reading file: {input_file}")
        df = pd.read_csv(input_file)
        
        # Get original row count for verification
        original_row_count = len(df)
        print(f"Original row count: {original_row_count}")
        
        # Count duplicates before sorting
        duplicate_count = df.duplicated(subset=['Acronym'], keep=False).sum()
        print(f"Rows with duplicate acronyms: {duplicate_count}")
        
        # Sort the dataframe by the 'Acronym' column
        # This will ensure that all instances of the same acronym are together
        sorted_df = df.sort_values(by='Acronym')
        
        # Verify row count after sorting
        if len(sorted_df) != original_row_count:
            print("WARNING: Row count changed after sorting!")
        
        # Write the sorted dataframe to a new CSV file
        sorted_df.to_csv(output_file, index=False)
        print(f"Sorted data written to: {output_file}")
        
        # Output statistics about the sorted data
        unique_acronyms = sorted_df['Acronym'].nunique()
        print(f"Number of unique acronyms: {unique_acronyms}")
        print(f"Average entries per acronym: {original_row_count / unique_acronyms:.2f}")
        
        # Sample of most duplicated acronyms
        dup_counts = sorted_df['Acronym'].value_counts()
        print("\nTop 5 most duplicated acronyms:")
        for acronym, count in dup_counts.head(5).items():
            print(f"  {acronym}: {count} occurrences")
        
        return True
    
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return False


def main():
    """Main function to parse arguments and run the sorter"""
    parser = argparse.ArgumentParser(description='Sort acronyms in a CSV file so duplicates appear consecutively.')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    if sort_acronyms(args.input, args.output):
        print("Processing completed successfully.")
    else:
        print("Processing failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()