#!/usr/bin/env python3
"""
Acronym File Processor

This script:
1. Merges multiple CSV files containing acronyms
2. Sorts them so identical acronyms appear consecutively
3. Splits the result back into multiple files with size constraints

Usage:
    python merge_sort_split_acronyms.py --input file1.csv file2.csv file3.csv file4.csv file5.csv file6.csv 
                                        --output_prefix output_file 
                                        --max_size 29
"""

import pandas as pd
import argparse
import os
import sys
from pathlib import Path


def get_file_size_mb(file_path):
    """Return the file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)


def merge_files(input_files):
    """
    Merge multiple CSV files into a single dataframe
    
    Args:
        input_files (list): List of paths to CSV files
        
    Returns:
        pandas.DataFrame: Merged dataframe
    """
    dfs = []
    total_rows = 0
    
    print(f"Merging {len(input_files)} files...")
    
    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found. Skipping.")
            continue
            
        try:
            df = pd.read_csv(file_path)
            rows = len(df)
            total_rows += rows
            file_size = get_file_size_mb(file_path)
            
            print(f"  - {file_path}: {rows} rows, {file_size:.2f} MB")
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    if not dfs:
        print("No valid files to merge. Exiting.")
        sys.exit(1)
        
    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)
    print(f"Merged data: {len(merged_df)} rows (from original {total_rows} rows)")
    
    # Check if we lost any rows during the merge
    if len(merged_df) != total_rows:
        print(f"Warning: Row count mismatch. Original: {total_rows}, Merged: {len(merged_df)}")
    
    return merged_df


def sort_dataframe(df):
    """
    Sort the dataframe by the 'Acronym' column to ensure duplicates are consecutive
    
    Args:
        df (pandas.DataFrame): Dataframe to sort
        
    Returns:
        pandas.DataFrame: Sorted dataframe
    """
    print("Sorting data to group identical acronyms...")
    sorted_df = df.sort_values(by='Acronym')
    
    # Count how many acronyms have duplicates
    duplicates = sorted_df['Acronym'].duplicated(keep=False)
    dup_count = duplicates.sum()
    unique_dups = sorted_df.loc[duplicates, 'Acronym'].nunique()
    
    print(f"Found {dup_count} rows with duplicate acronyms ({unique_dups} unique acronyms have duplicates)")
    
    return sorted_df


def split_dataframe(df, output_prefix, max_size_mb):
    """
    Split a dataframe into multiple CSV files, keeping acronym groups together
    and respecting maximum file size
    
    Args:
        df (pandas.DataFrame): Dataframe to split
        output_prefix (str): Prefix for output file names
        max_size_mb (float): Maximum file size in MB
        
    Returns:
        list: List of output file paths
    """
    # Group by acronym to ensure we don't split identical acronyms across files
    grouped = df.groupby('Acronym', as_index=False)
    
    # Initialize variables
    current_file_df = pd.DataFrame(columns=df.columns)
    file_number = 1
    output_files = []
    current_size_estimate = 0
    temp_file = f"{output_prefix}_temp.csv"
    
    print(f"Splitting data into files with maximum size of {max_size_mb} MB...")
    
    # Function to save the current dataframe to a file
    def save_current_file():
        nonlocal file_number, current_file_df, output_files
        
        if len(current_file_df) == 0:
            return
            
        output_file = f"{output_prefix}_{file_number}.csv"
        current_file_df.to_csv(output_file, index=False)
        
        # Get actual file size
        actual_size = get_file_size_mb(output_file)
        
        print(f"  - {output_file}: {len(current_file_df)} rows, {actual_size:.2f} MB")
        output_files.append(output_file)
        
        # Reset for next file
        current_file_df = pd.DataFrame(columns=df.columns)
        file_number += 1
    
    # Process each acronym group
    for acronym, group in grouped:
        # Write current group to a temp file to get its size
        group.to_csv(temp_file, index=False)
        group_size = get_file_size_mb(temp_file)
        
        # If this group alone exceeds max_size_mb, we need to split it further
        if group_size > max_size_mb:
            print(f"Warning: Acronym '{acronym}' group is {group_size:.2f} MB, which exceeds the maximum file size.")
            print(f"This group will be split, breaking the requirement to keep identical acronyms together.")
            
            # Save any accumulated data first
            if len(current_file_df) > 0:
                save_current_file()
            
            # Split this large group into chunks
            rows_per_file = int(len(group) * (max_size_mb / group_size))
            for i in range(0, len(group), rows_per_file):
                current_file_df = group.iloc[i:i+rows_per_file].copy()
                save_current_file()
                
        # If adding this group would exceed max_size_mb, save current file and start a new one
        elif current_size_estimate + group_size > max_size_mb and len(current_file_df) > 0:
            save_current_file()
            current_file_df = group.copy()
            current_size_estimate = group_size
            
        # Otherwise, add this group to the current file
        else:
            current_file_df = pd.concat([current_file_df, group], ignore_index=True)
            current_size_estimate += group_size
    
    # Save the last file if there's data remaining
    if len(current_file_df) > 0:
        save_current_file()
    
    # Clean up temp file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    return output_files


def validate_results(input_files, output_files):
    """
    Validate that all data was preserved during the process
    
    Args:
        input_files (list): List of input file paths
        output_files (list): List of output file paths
    """
    # Count total rows in input files
    input_rows = sum(len(pd.read_csv(f)) for f in input_files if os.path.exists(f))
    
    # Count total rows in output files
    output_rows = sum(len(pd.read_csv(f)) for f in output_files)
    
    print("\nValidation Results:")
    print(f"  - Total input rows: {input_rows}")
    print(f"  - Total output rows: {output_rows}")
    
    if input_rows == output_rows:
        print("✅ Row count matches: All data was preserved")
    else:
        print(f"❌ Row count mismatch: Input had {input_rows} rows, output has {output_rows} rows")


def main():
    """Main function to parse arguments and run the processing"""
    parser = argparse.ArgumentParser(
        description='Merge, sort, and split CSV files containing acronyms.'
    )
    parser.add_argument('--input', required=True, nargs='+', 
                        help='Input CSV files (space-separated)')
    parser.add_argument('--output_prefix', required=True, 
                        help='Prefix for output file names')
    parser.add_argument('--max_size', type=float, default=29.0,
                        help='Maximum size of each output file in MB (default: 29)')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output_prefix)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process the files
    merged_df = merge_files(args.input)
    sorted_df = sort_dataframe(merged_df)
    output_files = split_dataframe(sorted_df, args.output_prefix, args.max_size)
    
    # Validate results
    validate_results(args.input, output_files)
    
    print(f"\nProcessing complete. Created {len(output_files)} output files.")


if __name__ == "__main__":
    main()