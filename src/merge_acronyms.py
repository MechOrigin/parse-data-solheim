import pandas as pd
import glob
import os
from pathlib import Path
from dotenv import load_dotenv
from acronym_processor.api_key_cluster import APIKeyCluster
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_empty_row(row):
    """Check if a row is effectively empty (all values are empty strings or NaN)"""
    return row.isna().all() or (row == '').all()

def merge_acronym_files(input_pattern, output_file):
    """
    Merge multiple acronym CSV files into a single file.
    Takes header from first file and combines all data.
    
    Args:
        input_pattern (str): Glob pattern to match input files (e.g., "data/raw/grade2-acronyms_*.csv")
        output_file (str): Path to output file
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize API key cluster for load balancing
    api_cluster = APIKeyCluster.from_env(
        prefix="GEMINI_API_KEY_",
        daily_limit=60,
        rate_limit=60
    )
    logger.info(f"Initialized API key cluster with {len(api_cluster.keys)} keys")
    
    # Get list of files matching pattern
    input_files = sorted(glob.glob(input_pattern))
    
    if not input_files:
        logger.warning(f"No files found matching pattern: {input_pattern}")
        return
    
    logger.info(f"Found {len(input_files)} files to process")
    logger.info("Files to merge: %s", "\n- ".join(input_files))
    
    # Read first file to get header
    first_df = pd.read_csv(input_files[0])
    header = first_df.columns.tolist()
    
    # Initialize list to store all dataframes
    all_dfs = []
    total_rows = 0
    
    # Process all files
    for i, file in enumerate(input_files, 1):
        try:
            # Skip empty files
            if os.path.getsize(file) == 0:
                logger.info(f"Skipping empty file: {file}")
                continue
                
            # Read the file
            df = pd.read_csv(file)
            
            # Skip header for all files except the first one
            if file != input_files[0]:
                df = df.iloc[1:]
            
            # Remove rows where all values are empty/NaN
            df = df.dropna(how='all')
            
            # Remove rows where all values are empty strings
            df = df[~df.apply(is_empty_row, axis=1)]
            
            if not df.empty:
                all_dfs.append(df)
                total_rows += len(df)
                logger.info(f"Processed file {i}/{len(input_files)}: {file} ({len(df)} rows)")
            else:
                logger.info(f"Skipping file with no valid data: {file}")
                
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")
            continue
    
    if not all_dfs:
        logger.warning("No valid data found in any files")
        return
        
    # Combine all dataframes
    logger.info("Merging all dataframes...")
    merged_df = pd.concat(all_dfs, ignore_index=True)
    
    # Remove any remaining empty rows
    merged_df = merged_df.dropna(how='all')
    merged_df = merged_df[~merged_df.apply(is_empty_row, axis=1)]
    
    # Ensure all columns are present
    for col in header:
        if col not in merged_df.columns:
            merged_df[col] = ""
    
    # Reorder columns to match original header
    merged_df = merged_df[header]
    
    # Save merged file
    logger.info(f"Saving merged file to {output_file}...")
    merged_df.to_csv(output_file, index=False)
    logger.info(f"Merged {len(all_dfs)} files into {output_file}")
    logger.info(f"Total rows: {len(merged_df)}")
    logger.info(f"Average rows per file: {len(merged_df)/len(all_dfs):.1f}")
    
    # Log API key usage statistics
    key_stats = api_cluster.get_key_stats()
    logger.info("API Key Usage Statistics:")
    for key, stats in key_stats.items():
        logger.info(f"Key {key[:8]}...: {stats['requests_today']} requests today, {stats['error_count']} errors")

if __name__ == "__main__":
    # Process all grade2 acronym files
    input_pattern = "data/raw/grade2-acronyms_*.csv"
    output_file = "data/processed/merged_acronyms_all.csv"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    merge_acronym_files(input_pattern, output_file) 