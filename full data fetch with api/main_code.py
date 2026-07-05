import requests
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Define constants
BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"
OUTPUT_FILE = "pubchem_compounds_780001-800000xlsx.xlsx"
NUM_THREADS = os.cpu_count() * 2  # Dynamically set thread count based on CPU cores
RETRIES = 10  # Reduced retries to optimize waiting time
BATCH_SIZE = 150  # Batch size for writing to Excel

# Function to fetch data for a specific compound ID
def fetch_compound_data(compound_id):
    url = BASE_URL.format(compound_id)
    for attempt in range(RETRIES):
        try:
            response = requests.get(url, timeout=15)  # Reduced timeout for faster failures
            if response.status_code == 200:
                data = response.json()
                record = data.get("Record", {})
                chemical_name = record.get("RecordTitle", "N/A")

                sections = record.get("Section", [])
                molecular_weight, synonyms, iupac_name, cas_no, molecular_formula, drug_indication, therapeutic_indication = ["N/A"] * 7

                for section in sections:
                    heading = section.get("TOCHeading", "")
                    subsections = section.get("Section", [])

                    if heading == "Names and Identifiers":
                        for sub in subsections:
                            sub_heading = sub.get("TOCHeading", "")
                            if sub_heading == "Computed Descriptors":
                                iupac_name = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")
                            elif sub_heading == "Other Identifiers":
                                cas_no = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")
                            elif sub_heading == "Synonyms":
                                synonyms_list = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
                                synonyms = ", ".join([entry.get("String", "") for entry in synonyms_list]) or "N/A"
                            elif sub_heading == "Molecular Formula":
                                molecular_formula = sub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

                    elif heading == "Chemical and Physical Properties":
                        for sub in subsections:
                            if sub.get("TOCHeading") == "Computed Properties":
                                molecular_weight = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")
                                if molecular_weight != "N/A":
                                    molecular_weight += " g/mol"

                    elif heading == "Drug and Medication Information":
                        for sub in subsections:
                            if sub.get("TOCHeading") == "Drug Indication":
                                indications = sub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])
                                drug_indication = " ".join([entry.get("String", "") for entry in indications]) or "N/A"
                            elif sub.get("TOCHeading") == "Therapeutic Uses":
                                therapeutic_indication = sub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

                return compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula, drug_indication, therapeutic_indication

            elif response.status_code in [503, 429]:  # Retry only on temporary errors
                time.sleep(2 ** attempt)  # Exponential backoff
            elif response.status_code == 404:
                return None  # No data found
            else:
                return None  # Other HTTP errors
        except requests.exceptions.RequestException:
            time.sleep(2 ** attempt)

    return None  # Return None after exhausting retries

# Function to write data to Excel in batches
def write_to_excel(data_list):
    df = pd.DataFrame(data_list, columns=["Compound ID", "Chemical Name", "Synonyms", "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula", "Drug Indication", "Therapeutic Indication"])
    
    if os.path.exists(OUTPUT_FILE):
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
    else:
        df.to_excel(OUTPUT_FILE, index=False, header=True)

# Main function to fetch data and save it to the Excel file
def main():
    start_id = 780001
    end_id   = 800000
    failed_ids = []
    batch_data = []

    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = {executor.submit(fetch_compound_data, cid): cid for cid in range(start_id, end_id + 1)}

        for future in as_completed(futures):
            compound_id = futures[future]
            try:
                result = future.result()
                if result:
                    batch_data.append(result)
                    print(f"Data for Compound ID {compound_id} fetched.")
                else:
                    failed_ids.append(compound_id)

                if len(batch_data) >= BATCH_SIZE:
                    write_to_excel(batch_data)
                    batch_data.clear()
            except Exception as e:
                print(f"Error fetching data for Compound ID {compound_id}: {e}")
                failed_ids.append(compound_id)

    # Write any remaining data
    if batch_data:
        write_to_excel(batch_data)

    # Retry failed IDs in a separate batch
    if failed_ids:
        print(f"Retrying {len(failed_ids)} failed IDs...")
        batch_data.clear()
        
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            retry_futures = {executor.submit(fetch_compound_data, cid): cid for cid in failed_ids}

            for future in as_completed(retry_futures):
                retry_result = future.result()
                if retry_result:
                    batch_data.append(retry_result)
                    print(f"Data for Compound ID {compound_id} fetched on retry.")

        if batch_data:
            write_to_excel(batch_data)

    print("Data extraction complete.")

if __name__ == "__main__":
    main()