# PubChem Data Fetch Scripts

This folder contains Python scripts that fetch chemical and compound information from PubChem and save the results to Excel files.

## What this project does

The scripts are designed to collect data such as:
- Compound ID
- Chemical name
- Synonyms
- Molecular formula
- Molecular weight
- IUPAC name
- CAS number
- Drug and therapeutic indications (in some scripts)

The data is retrieved from the PubChem API and exported to Excel for further analysis.

## Folder structure

- code with cas number/
  - Scripts for fetching PubChem data using CAS numbers.

- code with chemical name/
  - Scripts for fetching PubChem data using chemical names.

- code with compund_id/
  - Scripts for fetching PubChem data using compound IDs.

- full data fetch with api/
  - Scripts for broader or batch-based PubChem data extraction.

## Requirements

Install the required Python packages:

```bash
pip install requests pandas openpyxl
```

## How to use

1. Open the folder that matches your input type.
2. Place your input file (for example, an Excel or CSV file) in the same folder or update the script path.
3. Run the Python script:

```bash
python your_script.py
```

4. Check the generated Excel file in the same folder.

## Notes

- Some scripts may require you to update the input file name or output file name inside the code.
- PubChem API requests may be rate-limited, so some scripts include retry logic and delays.
- Make sure your input file contains the correct column names expected by the script.

## Example input files

Depending on the script, the input may be:
- Excel file with CAS numbers
- Excel file with chemical names
- CSV file with compound IDs

## Disclaimer

These scripts use public PubChem data and should be used responsibly in accordance with PubChem usage policies.
