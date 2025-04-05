# Acronym Processing Project

This project processes and analyzes acronyms from various data sources, including grading and sorting functionality.

## Project Structure

```
/
├── data/
│   ├── raw/                 # Original input files
│   ├── processed/           # Processed data files
│   └── final/              # Final output files
├── src/
│   ├── processing/         # Data processing scripts
│   ├── grading/           # Grading related scripts
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── docs/                  # Documentation
└── output/                # Generated results
```

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

The project contains several main components:

1. **Data Processing**
   - Located in `src/processing/`
   - Includes scripts for parsing, sorting, and merging acronyms
   
   ### Acronym Counter (`src/processing/acronym_counter.py`)
   Counts acronyms based on various header parameters and generates statistics.
   
   Basic usage:
   ```bash
   # Generate summary statistics
   python3 src/processing/acronym_counter.py data/raw/your_input_file.csv
   
   # Count by a specific column
   python3 src/processing/acronym_counter.py data/raw/your_input_file.csv --column Grade
   
   # Count by multiple columns (cross-tabulation)
   python3 src/processing/acronym_counter.py data/raw/your_input_file.csv --columns Grade Tags
   
   # Specify custom output location
   python3 src/processing/acronym_counter.py data/raw/your_input_file.csv --output data/processed/custom_output.csv
   ```
   
   Features:
   - Summary statistics (total acronyms, unique acronyms, unique definitions, unique grades)
   - Column-based counting
   - Cross-tabulation by multiple columns
   - Detailed logging
   - Automatic output directory creation

2. **Grading System**
   - Located in `src/grading/`
   - Handles acronym grading and evaluation

3. **Utilities**
   - Located in `src/utils/`
   - Contains shared functionality and helper functions

## Configuration Options

The platform supports several configuration options to customize the acronym processing:

1. **Batch Size**
   - Control how many acronyms to process at once
   - Default: 25 acronyms per batch
   - Configurable through the settings panel
   - Example: Set to 250 for larger batches

2. **Grade Filtering**
   - Select specific grades or grade ranges to process
   - Options:
     - Single grade (e.g., Grade 2 only)
     - Grade range (e.g., Grades 5-4)
     - All grades (default)
   - Applied during initial processing

3. **Acronym Enrichment**
   - Toggle AI-powered enrichment of acronym data
   - Default: Enabled
   - When enabled:
     - Adds missing definitions
     - Generates descriptions
     - Suggests relevant tags
     - Uses web search and internal knowledge base
   - Can be disabled for faster processing

4. **Starting Point**
   - Option to begin processing from a specific acronym
   - Default: Disabled (processes from beginning)
   - When enabled:
     - Enter specific acronym (e.g., "DHA")
     - System scans acronyms file to find match
     - Processing begins from matched position
   - Useful for resuming interrupted processing

These settings can be configured through the platform's settings panel and are saved between sessions.

## Data Organization

- Raw data files are stored in `