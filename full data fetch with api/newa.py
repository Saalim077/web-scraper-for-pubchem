import requests
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Define the base URL
base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"

failed_id_track = []

# Function to fetch data for a specific compound ID with retry for 503 errors
def fetch_compound_data(compound_id, retries=20, backoff_factor=2):
    url = base_url.format(compound_id)
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=120)  # Set a timeout for the request
            if response.status_code == 200:
                data = response.json()
                molecular_weight = None
                synonyms = None
                iupac_name = None
                chemical_name = None
                molecular_formula = None
                cas_no = None
                drug_indication = None
                therapeutic_indication = None

                sections = data.get("Record", {}).get("Section", [])
                chemical_name = data.get("Record", {}).get("RecordTitle")

                for section in sections:
                    if section.get("TOCHeading") == "Names and Identifiers":
                        for subsection in section.get("Section", []):
                            if subsection.get("TOCHeading") == "Computed Descriptors":
                                for subsubsection in subsection.get("Section", []):
                                    if subsubsection.get("TOCHeading") == "IUPAC Name":
                                        iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
                            if subsection.get("TOCHeading") == "Other Identifiers":
                                for subsubsection in subsection.get("Section", []):
                                    if subsubsection.get("TOCHeading") == "CAS":
                                        cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
                            elif subsection.get("TOCHeading") == "Synonyms":
                                for item in subsection.get("Section", []):
                                    if item.get("TOCHeading") == "Depositor-Supplied Synonyms":
                                        synonyms_list = item.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
                                        synonyms = [entry.get("String") for entry in synonyms_list if "String" in entry]
                            elif subsection.get("TOCHeading") == "Molecular Formula":
                                molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

                    if section.get("TOCHeading") == "Chemical and Physical Properties":
                        for subsection in section.get("Section", []):
                            if subsection.get("TOCHeading") == "Computed Properties":
                                for subsubsection in subsection.get("Section", []):
                                    if subsubsection.get("TOCHeading") == "Molecular Weight":
                                        molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
                                        if molecular_weight:
                                            molecular_weight += " g/mol"

                    if section.get("TOCHeading") == "Drug and Medication Information":
                        for subsection in section.get("Section", []):
                            if subsection.get("TOCHeading") == "Drug Indication":
                                drug_indication_list = []
                                for info in subsection.get("Information", []):
                                    if "StringWithMarkup" in info.get("Value", {}):
                                        indications = info["Value"]["StringWithMarkup"]
                                        for entry in indications:
                                            indication_text = entry.get("String", "").strip()
                                            if indication_text and indication_text not in drug_indication_list:
                                                drug_indication_list.append(indication_text)
                                drug_indication = " ".join(drug_indication_list)

                            if subsection.get("TOCHeading") == "Therapeutic Uses":
                                therapeutic_indication = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

                molecular_weight = molecular_weight or "N/A"
                synonyms = ", ".join(synonyms) if synonyms else "N/A"
                iupac_name = iupac_name or "N/A"
                chemical_name = chemical_name or "N/A"
                molecular_formula = molecular_formula or "N/A"
                cas_no = cas_no or "N/A"
                drug_indication = drug_indication or "N/A"
                therapeutic_indication = therapeutic_indication or "N/A"

                return compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula, drug_indication, therapeutic_indication

            elif response.status_code == 503:
                time.sleep(backoff_factor ** attempt)
            elif response.status_code == 404:
                return None
            else:
                return None
        except requests.exceptions.RequestException:
            pass
    return None

# Function to append data to the Excel file
def append_to_excel(data_list, output_file):
    df = pd.DataFrame(data_list, columns=["Compound ID", "Chemical Name", "Synonyms", "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula", "Drug Indication", "Therapeutic Indication"])
    if os.path.exists(output_file):
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
    else:
        df.to_excel(output_file, index=False, header=True)

# Main function to fetch data
def fetch_data(start_id, end_id, output_file):
    failed_ids = []
    num_threads = 10
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(fetch_compound_data, compound_id): compound_id for compound_id in range(start_id, end_id + 1)}

        batch_data = []
        for future in as_completed(futures):
            result = future.result()
            if result:
                batch_data.append(result)
                print(f"✅ Fetched data for Compound ID: {result[0]}")
            else:
                failed_ids.append(futures[future])
                print(f"❌ Failed to fetch data for Compound ID: {futures[future]}")

            if len(batch_data) >= 20:
                append_to_excel(batch_data, output_file)
                batch_data = []

        if batch_data:
            append_to_excel(batch_data, output_file)

    if failed_ids:
        for compound_id in failed_ids:
            result = fetch_compound_data(compound_id)
            if result:
                append_to_excel([result], output_file)
                print(f"🔁 Retry successful for Compound ID: {compound_id}")
            else:
                print(f"⚠️ Retry failed for Compound ID: {compound_id}")

if __name__ == "__main__":
    # Example usage
    start_id = 1
    end_id = 100
    output_file = "compound_data.xlsx"
    fetch_data(start_id, end_id, output_file)
