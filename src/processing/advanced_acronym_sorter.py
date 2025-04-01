#!/usr/bin/env python3
"""
Advanced Acronym Sorter

This script processes a CSV file containing acronyms, sorts them so duplicate
acronyms appear consecutively, and provides advanced options for sorting and analysis.

Usage:
    python advanced_acronym_sorter.py --input INPUT_FILE --output OUTPUT_FILE [options]

Options:
    --input            Path to the input CSV file
    --output           Path to the output CSV file
    --secondary-sort   Field to sort by within each acronym group (default: none)
    --report           Generate a detailed report of acronym statistics
    --report-file      File to write the report to (default: acronym_report.txt)
    --check-values     Check for inconsistent definitions or descriptions
"""

import pandas as pd
import argparse
import sys
import os
from datetime import datetime


def generate_report(df, report_file):
    """
    Generate a detailed report about the acronyms in the dataframe
    
    Args:
        df (pandas.DataFrame): The dataframe containing acronym data
        report_file (str): Path to the output report file
    """
    with open(report_file, 'w') as f:
        f.write("=== ACRONYM ANALYSIS REPORT ===\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Basic statistics
        total_entries = len(df)
        unique_acronyms = df['Acronym'].nunique()
        f.write(f"Total entries: {total_entries}\n")
        f.write(f"Unique acronyms: {unique_acronyms}\n")
        f.write(f"Average entries per acronym: {total_entries / unique_acronyms:.2f}\n\n")
        
        # Duplicates analysis
        dup_counts = df['Acronym'].value_counts()
        duplicated = dup_counts[dup_counts > 1]
        f.write(f"Acronyms with multiple entries: {len(duplicated)}\n")
        
        # Distribution of entries
        f.write("\nDistribution of entries per acronym:\n")
        distribution = dup_counts.value_counts().sort_index()
        for count, freq in distribution.items():
            f.write(f"  {count} entry/entries: {freq} acronym(s)\n")
        
        # Most duplicated acronyms
        f.write("\nTop 10 most duplicated acronyms:\n")
        for acronym, count in duplicated.nlargest(10).items():
            f.write(f"  {acronym}: {count} occurrences\n")
        
        # Grade distribution
        if 'Grade' in df.columns:
            f.write("\nGrade distribution:\n")
            grade_dist = df['Grade'].value_counts().sort_index()
            for grade, count in grade_dist.items():
                f.write(f"  Grade {grade}: {count} entries ({count/total_entries*100:.1f}%)\n")
        
        # Tag analysis
        if 'Tags' in df.columns:
            f.write("\nMost common tags:\n")
            # Split tags if they're in a comma-separated format
            all_tags = []
            for tags in df['Tags'].fillna(''):
                all_tags.extend([tag.strip() for tag in str(tags).split(',') if tag.strip()])
            
            tag_counts = pd.Series(all_tags).value_counts()
            for tag, count in tag_counts.nlargest(10).items():
                f.write(f"  {tag}: {count} occurrences\n")
    
    print(f"Report generated: {report_file}")


def check_inconsistencies(df):
    """
    Check for inconsistencies in definitions or descriptions for the same acronym
    
    Args:
        df (pandas.DataFrame): The dataframe containing acronym data
        
    Returns:
        pandas.DataFrame: A dataframe containing information about inconsistencies
    """
    inconsistencies = []
    
    # Group by acronym
    grouped = df.groupby('Acronym')
    
    for acronym, group in grouped:
        # Skip if only one entry
        if len(group) <= 1:
            continue
        
        # Check for different definitions
        if 'Definition' in group.columns and group['Definition'].nunique() > 1:
            inconsistencies.append({
                'Acronym': acronym,
                'Type': 'Definition',
                'Values': ', '.join(str(x) for x in group['Definition'].unique()),
                'Count': len(group)
            })
        
        # Check for different descriptions
        if 'Description' in group.columns and group['Description'].nunique() > 1:
            inconsistencies.append({
                'Acronym': acronym,
                'Type': 'Description',
                'Values': 'Multiple different descriptions',
                'Count': len(group)
            })
    
    return pd.DataFrame(inconsistencies)


def sort_acronyms(input_file, output_file, secondary_sort=None, 
                  report=False, report_file='acronym_report.txt',
                  check_values=False):
    """
    Reads a CSV file with acronyms, sorts it so duplicates are together,
    and writes the result to a new CSV file.

    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output CSV file
        secondary_sort (str): Column to sort by within each acronym group
        report (bool): Whether to generate a detailed report
        report_file (str): Path to the report file
        check_values (bool): Whether to check for inconsistent values
    """
    try:
        # Read the CSV file
        print(f"Reading file: {input_file}")
        df = pd.read_csv(input_file)
        
        # Get original row count for verification
        original_row_count = len(df)
        print(f"Original row count: {original_row_count}")
        
        # Determine sort columns
        sort_columns = ['Acronym']
        if secondary_sort and secondary_sort in df.columns:
            sort_columns.append(secondary_sort)
            print(f"Sorting by: {', '.join(sort_columns)}")
        else:
            print("Sorting by Acronym only")
        
        # Sort the dataframe
        sorted_df = df.sort_values(by=sort_columns)
        
        # Verify row count after sorting
        if len(sorted_df) != original_row_count:
            print("WARNING: Row count changed after sorting!")
        
        # Check for inconsistencies if requested
        if check_values:
            print("\nChecking for inconsistent values...")
            inconsistencies = check_inconsistencies(sorted_df)
            
            if len(inconsistencies) > 0:
                print(f"Found {len(inconsistencies)} inconsistencies!")
                print("\nSample inconsistencies:")
                print(inconsistencies.head())
                
                # Save inconsistencies to a file
                inconsistency_file = os.path.splitext(output_file)[0] + '_inconsistencies.csv'
                inconsistencies.to_csv(inconsistency_file, index=False)
                print(f"Full inconsistency report saved to: {inconsistency_file}")
            else:
                print("No inconsistencies found.")
        
        # Write the sorted dataframe to a new CSV file
        sorted_df.to_csv(output_file, index=False)
        print(f"Sorted data written to: {output_file}")
        
        # Generate a detailed report if requested
        if report:
            generate_report(sorted_df, report_file)
        
        return True
    
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return False


def main():
    """Main function to parse arguments and run the sorter"""
    parser = argparse.ArgumentParser(
        description='Advanced tool to sort acronyms in a CSV file so duplicates appear consecutively.'
    )
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    parser.add_argument('--secondary-sort', help='Column to sort by within each acronym group')
    parser.add_argument('--report', action='store_true', help='Generate a detailed report')
    parser.add_argument('--report-file', default='acronym_report.txt', help='Path for the report file')
    parser.add_argument('--check-values', action='store_true', help='Check for inconsistent values')
    
    args = parser.parse_args()
    
    if sort_acronyms(
        args.input, 
        args.output, 
        args.secondary_sort,
        args.report,
        args.report_file,
        args.check_values
    ):
        print("Processing completed successfully.")
    else:
        print("Processing failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()