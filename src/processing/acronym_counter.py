#!/usr/bin/env python3
"""
Acronym Counter Script

This script counts acronyms in CSV files based on header parameters.
It provides various counting methods and outputs the results to a CSV file.

Usage:
    # Generate summary statistics
    python3 acronym_counter.py data/raw/your_input_file.csv
    
    # Count by a specific column
    python3 acronym_counter.py data/raw/your_input_file.csv --column Grade
    
    # Count by multiple columns (cross-tabulation)
    python3 acronym_counter.py data/raw/your_input_file.csv --columns Grade Tags
    
    # Specify custom output location
    python3 acronym_counter.py data/raw/your_input_file.csv --output data/processed/custom_output.csv

Arguments:
    input_file: Path to the input CSV file
    --output, -o: Path to the output CSV file (default: data/processed/{input_file}_counts.csv)
    --column, -c: Column to count by
    --columns, -cols: Multiple columns for cross-tabulation
    --summary, -s: Generate summary statistics

Features:
    - Summary statistics (total acronyms, unique acronyms, unique definitions, unique grades)
    - Column-based counting
    - Cross-tabulation by multiple columns
    - Detailed logging
    - Automatic output directory creation

Requirements:
    - Python 3.6 or higher
    - pandas
    - pathlib (built-in)
    - typing (built-in)
"""

import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AcronymCounter:
    def __init__(self, input_file: str):
        """Initialize the AcronymCounter with an input file."""
        self.input_file = input_file
        self.df = None
        self.load_data()

    def load_data(self) -> None:
        """Load the CSV data into a pandas DataFrame."""
        try:
            # Try reading with different parameters
            self.df = pd.read_csv(self.input_file, quoting=1, escapechar='\\', on_bad_lines='skip')
            logger.info(f"Successfully loaded {len(self.df)} rows from {self.input_file}")
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise

    def count_by_column(self, column: str) -> pd.DataFrame:
        """Count acronyms by a specific column."""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in the data")
        
        # Create a DataFrame with the counts
        counts = self.df[column].value_counts().reset_index()
        counts.columns = [column, 'count']
        counts = counts.sort_values(by=column)  # Sort by the column values
        
        logger.info(f"Counted {len(counts)} unique values in column '{column}'")
        return counts

    def count_by_multiple_columns(self, columns: List[str]) -> pd.DataFrame:
        """Count acronyms by multiple columns and return a cross-tabulation."""
        if not all(col in self.df.columns for col in columns):
            missing = [col for col in columns if col not in self.df.columns]
            raise ValueError(f"Columns not found in the data: {missing}")
        
        crosstab = pd.crosstab(*[self.df[col] for col in columns])
        logger.info(f"Created cross-tabulation for columns: {columns}")
        return crosstab

    def get_summary_stats(self) -> pd.DataFrame:
        """Get summary statistics about the acronyms."""
        stats = pd.DataFrame([
            {"Metric": "Total Acronyms", "Count": len(self.df)},
            {"Metric": "Unique Acronyms", "Count": self.df['Acronym'].nunique()},
            {"Metric": "Unique Definitions", "Count": self.df['Definition'].nunique()},
            {"Metric": "Unique Grades", "Count": self.df['Grade'].nunique() if 'Grade' in self.df.columns else 0}
        ])
        logger.info("Generated summary statistics")
        return stats

def save_results(results: pd.DataFrame, output_file: str) -> None:
    """Save the counting results to a CSV file."""
    try:
        results.to_csv(output_file, index=False)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Count acronyms based on header parameters')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('--output', '-o', help='Output CSV file path', default=None)
    parser.add_argument('--column', '-c', help='Column to count by')
    parser.add_argument('--columns', '-cols', nargs='+', help='Multiple columns for cross-tabulation')
    parser.add_argument('--summary', '-s', action='store_true', help='Generate summary statistics')
    
    args = parser.parse_args()

    # Get the workspace root directory (parent of src directory)
    workspace_root = Path(__file__).parent.parent.parent

    # Set default output path if not provided
    if args.output is None:
        input_path = Path(args.input_file)
        output_path = workspace_root / 'data' / 'processed' / f"{input_path.stem}_counts.csv"
        args.output = str(output_path)
    else:
        # Convert relative output path to absolute path from workspace root
        args.output = str(workspace_root / args.output)

    # Create output directory if it doesn't exist
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    try:
        counter = AcronymCounter(args.input_file)
        
        if args.summary:
            results = counter.get_summary_stats()
        elif args.columns:
            results = counter.count_by_multiple_columns(args.columns)
        elif args.column:
            results = counter.count_by_column(args.column)
        else:
            results = counter.get_summary_stats()
        
        save_results(results, args.output)
        logger.info("Processing completed successfully")

    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    main() 