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

## Data Organization

- Raw data files are stored in `data/raw/`
- Processed intermediate files are in `data/processed/`
- Final output files are stored in `data/final/`

## Contributing

1. Follow the existing code structure
2. Use consistent naming conventions
3. Add appropriate documentation
4. Run tests before submitting changes

## License

[Add your license information here]