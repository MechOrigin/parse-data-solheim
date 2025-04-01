import pandas as pd
import os

def merge_acronym_files(file_paths):
    """
    Merge multiple acronym files into a single DataFrame.
    
    Args:
        file_paths: List of file paths to the acronym data files
        
    Returns:
        Merged DataFrame with all acronyms
    """
    all_data = []
    
    for file_path in file_paths:
        # Read each file into a DataFrame
        df = pd.read_csv(file_path)
        all_data.append(df)
        print(f"Read {file_path}: {len(df)} acronyms")
    
    # Concatenate all DataFrames
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # Remove duplicates based on Acronym column
    deduplicated_df = merged_df.drop_duplicates(subset=['Acronym'])
    
    print(f"\nTotal acronyms before deduplication: {len(merged_df)}")
    print(f"Total acronyms after deduplication: {len(deduplicated_df)}")
    print(f"Duplicates removed: {len(merged_df) - len(deduplicated_df)}")
    
    # Sort by Acronym
    sorted_df = deduplicated_df.sort_values('Acronym')
    
    return sorted_df

def save_merged_data(df, output_path):
    """
    Save the merged data to a CSV file.
    
    Args:
        df: DataFrame with merged acronym data
        output_path: Path to save the merged CSV file
    """
    df.to_csv(output_path, index=False)
    print(f"\nSaved merged data to {output_path}")

# List of file paths to merge
file_paths = [
    "grade4-acronyms-part1.txt",
    "grade4-acronyms-part2.txt",
    "grade4-acronyms-part3.txt",
    "grade4-acronyms-part4.txt",
    "grade4-acronyms-part5.txt",
    "grade4-acronyms-part6.txt",
    "grade4-acronyms-part7.txt",
    "grade4-acronyms-part8.txt",
    "grade4-acronyms-part9.txt",
    "grade4-acronyms-part10.txt",
    "grade4-acronyms-part11.txt",
    "grade4-acronyms-part12.txt",
    "grade4-acronyms-part13.txt",
    "grade4-acronyms-part14.txt",
    "grade4-acronyms-part15.txt",
    "grade4-acronyms-part16.txt",
    "grade4-acronyms-part17.txt",
    "grade4-acronyms-part18.txt",
    "grade4-acronyms-part19.txt",
    "grade4-acronyms-part20.txt",
    "grade4-acronyms-part21.txt",
    "grade4-acronyms-part22.txt",
    "grade4-acronyms-part23.txt",
    "grade4-acronyms-part24.txt",
    "grade4-acronyms-part25.txt",
    "grade4-acronyms-part26.txt",
    "grade4-acronyms-part27.txt",
    "grade4-acronyms-part28.txt",
    "grade4-acronyms-part29.txt",
    "grade4-acronyms-part30.txt",
    "grade4-acronyms-part31.txt",
    "grade4-acronyms-part32.txt",
    "grade4-acronyms-part33.txt",
    "grade4-acronyms-part34.txt",
    "grade4-acronyms-part35.txt",
    "grade4-acronyms-part36.txt",
    "grade4-acronyms-part37.txt",
    "grade4-acronyms-part38.txt",
    "grade4-acronyms-part39.txt",
    "grade4-acronyms-part40.txt",
    "grade4-acronyms-part41.txt",
    "grade4-acronyms-part42.txt",
    "grade4-acronyms-part43.txt",
    "grade4-acronyms-part44.txt",
    "grade4-acronyms-part45.txt",
    "grade4-acronyms-part46.txt",
    "grade4-acronyms-part47.txt",
    "grade4-acronyms-part48.txt",
    "grade4-acronyms-part49.txt"
]

# Create output directory if it doesn't exist
output_dir = "merged_output"
os.makedirs(output_dir, exist_ok=True)

# Merge the files
merged_df = merge_acronym_files(file_paths)

# Save the merged data
output_path = os.path.join(output_dir, "merged_acronyms.csv")
save_merged_data(merged_df, output_path)

# Display statistics about the merged data
print("\nMerged Data Statistics:")
print(f"Total unique acronyms: {len(merged_df)}")
print(f"Number of acronyms by grade:")
print(merged_df['Grade'].value_counts().sort_index())
print("\nNumber of acronyms by tag:")
print(merged_df['Tags'].value_counts().sort_values(ascending=False).head(10))