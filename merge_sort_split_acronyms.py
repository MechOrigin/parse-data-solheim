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
    current_chunks = []
    file_number = 1
    output_files = []
    current_size_estimate = 0
    
    # Estimate bytes per row based on a sample
    sample_size = min(1000, len(df))
    bytes_per_row = len(df.iloc[:sample_size].to_csv(index=False).encode('utf-8')) / sample_size
    
    print(f"Splitting data into files with maximum size of {max_size_mb} MB...")
    
    def save_chunks_to_file(chunks):
        nonlocal file_number, output_files
        if not chunks:
            return
            
        output_file = f"{output_prefix}_{file_number}.csv"
        combined_df = pd.concat(chunks, ignore_index=True)
        combined_df.to_csv(output_file, index=False)
        
        actual_size = get_file_size_mb(output_file)
        print(f"  - {output_file}: {len(combined_df)} rows, {actual_size:.2f} MB")
        output_files.append(output_file)
        file_number += 1
    
    # Process each acronym group
    for acronym, group in grouped:
        # Estimate group size in MB
        group_size_estimate = (len(group) * bytes_per_row) / (1024 * 1024)
        
        # If this group alone exceeds max_size_mb, split it
        if group_size_estimate > max_size_mb:
            # Save any accumulated chunks first
            if current_chunks:
                save_chunks_to_file(current_chunks)
                current_chunks = []
                current_size_estimate = 0
            
            print(f"Warning: Acronym '{acronym}' group is approximately {group_size_estimate:.2f} MB, exceeding the maximum file size.")
            print(f"This group will be split, breaking the requirement to keep identical acronyms together.")
            
            # Split this large group into chunks
            rows_per_file = int(len(group) * (max_size_mb / group_size_estimate))
            for i in range(0, len(group), rows_per_file):
                chunk = group.iloc[i:i+rows_per_file].copy()
                save_chunks_to_file([chunk])
                
        # If adding this group would exceed max_size_mb, save current chunks and start new file
        elif current_size_estimate + group_size_estimate > max_size_mb and current_chunks:
            save_chunks_to_file(current_chunks)
            current_chunks = [group]
            current_size_estimate = group_size_estimate
            
        # Otherwise, add this group to current chunks
        else:
            current_chunks.append(group)
            current_size_estimate += group_size_estimate
    
    # Save any remaining chunks
    if current_chunks:
        save_chunks_to_file(current_chunks)
    
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