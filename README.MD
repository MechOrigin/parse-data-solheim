# To run the parser

    python3 acronym_parser.py --input acronym-finder_1.csv --output my_acronyms.csv

## To run the sorter

    python3 advanced_acronym_sorter.py --input my_acronyms.csv --output sorted_acronyms.csv --secondary-sort Grade --report --check-values

### To run the merger/sorter

    python3 merge_sort_split_acronyms.py --input my_acronyms.csv my_acronyms-1.csv my_acronyms-2.csv my_acronyms-3.csv my_acronyms-4.csv my_acronyms-5.csv --output_prefix sorted_output --max_size 29

    