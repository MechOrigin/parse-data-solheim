# Acronym Processing Toolkit

A comprehensive suite of Python tools for processing, organizing, and managing acronym datasets.

## Overview

This toolkit allows you to:
- **Parse** raw acronym data into a structured format
- **Sort** acronyms and group duplicates together
- **Merge** multiple files and split them into size-constrained chunks
- **Analyze** acronym quality and consistency

## 🔧 Requirements

- Python 3.6+
- pandas (`pip install pandas`)

## 🚀 Quick Start

### 1. Parse Raw Acronym Data

Convert raw data into a structured format with defined fields:

```bash
python3 acronym_parser.py --input acronym-finder_1.csv --output my_acronyms.csv
```

This creates a CSV with standardized fields: Acronym, Definition, Description, Tags, and Grade.

### 2. Sort Acronyms and Group Duplicates

Organize your acronym file by sorting and performing advanced analysis:

```bash
python3 advanced_acronym_sorter.py --input my_acronyms.csv --output sorted_acronyms.csv --secondary-sort Grade --report --check-values
```

Options:
- `--secondary-sort Grade`: Sort duplicates by their grade/importance
- `--report`: Generate detailed acronym statistics
- `--check-values`: Identify inconsistencies across duplicate acronyms

### 3. Merge & Split for Large Datasets

Combine multiple files, ensure duplicates are grouped, and split into manageable chunks:

```bash
python3 merge_sort_split_acronyms.py --input my_acronyms.csv my_acronyms-1.csv my_acronyms-2.csv my_acronyms-3.csv my_acronyms-4.csv my_acronyms-5.csv --output_prefix sorted_output --max_size 29
```

Features:
- Merges multiple input files into one
- Sorts to group identical acronyms together
- Intelligently splits into multiple files with a maximum size (in MB)
- Preserves all data with validation checks

## 📊 Data Structure

The toolkit works with CSV files containing the following fields:

| Field       | Description                                              |
|-------------|----------------------------------------------------------|
| Acronym     | The abbreviation (e.g., "API")                           |
| Definition  | The expanded form (e.g., "Application Programming Interface") |
| Description | Detailed explanation of the acronym's meaning and usage  |
| Tags        | Categories or domains relevant to the acronym            |
| Grade       | Numeric value (1-5) indicating importance or relevance   |

## 📝 Detailed Usage

### Acronym Parser

```bash
python3 acronym_parser.py --input <raw_data.csv> --output <processed_data.csv>
```

The parser extracts acronyms from raw data and enriches them with definitions, descriptions, tags, and grades.

### Advanced Acronym Sorter

```bash
python3 advanced_acronym_sorter.py --input <input.csv> --output <output.csv> [options]
```

Options:
- `--secondary-sort COLUMN`: Sort within each acronym group by this column
- `--report`: Generate a detailed report of acronym statistics
- `--report-file FILENAME`: Custom filename for the report (default: acronym_report.txt)
- `--check-values`: Check for inconsistent definitions or descriptions

### Merge-Sort-Split Tool

```bash
python3 merge_sort_split_acronyms.py --input <file1.csv> <file2.csv> ... --output_prefix <prefix> --max_size <size_in_mb>
```

Parameters:
- `--input`: List of input CSV files to process
- `--output_prefix`: Prefix for output filenames (will be numbered)
- `--max_size`: Maximum size of each output file in MB (default: 29)

## 🔍 Testing & Verification

For testing purposes, you can generate sample data files:

```bash
python3 generate_test_files.py --num_files 6 --rows_per_file 1000 --output_dir ./test_files
```

## 📄 File Naming Conventions

- Input files: Any valid CSV filename
- Sorted output: `sorted_acronyms.csv`
- Merged & split output: `[prefix]_1.csv`, `[prefix]_2.csv`, etc.
- Reports: `acronym_report.txt` (default)
- Inconsistency reports: `[output]_inconsistencies.csv`

## 🤝 Contributing

Contributions to improve the toolkit are welcome. Please ensure any modifications maintain data integrity and follow the existing code style.

## 📋 Todo / Future Improvements

- Add web interface for easier file management
- Implement enhanced duplicate detection algorithms
- Add visual reporting options
- Extend description generation capabilities


## Practical Use Snippets

## To run the parser

```bash
python3 acronym_parser.py --input acronym-finder_1.csv --output my_acronyms.csv
```

## To run the sorter

```bash
python3 advanced_acronym_sorter.py --input my_acronyms.csv --output sorted_acronyms.csv --secondary-sort Grade --report --check-values
```

### To run the merger/sorter

```bash
python3 merge_sort_split_acronyms.py --input my_acronyms.csv my_acronyms-1.csv my_acronyms-2.csv my_acronyms-3.csv my_acronyms-4.csv my_acronyms-5.csv --output_prefix sorted_output --max_size 29
```

### To run grader

```bash
python3 acronym_grader.py sorted_output_1.csv sorted_output_graded.csv
```

