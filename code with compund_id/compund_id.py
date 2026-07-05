# import requests
# import pandas as pd
# import os
# import time

# # Constants
# BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"
# OUTPUT_FILE = "pubchem_compounds_from.xlsx"
# RETRIES = 5
# INPUT_CSV = "compound_ids.csv"  # Update this if your file is named differently

# def fetch_compound_data(compound_id):
#     url = BASE_URL.format(compound_id)
#     for attempt in range(RETRIES):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 record = data.get("Record", {})
#                 chemical_name = record.get("RecordTitle", "N/A")

#                 sections = record.get("Section", [])
#                 molecular_weight, synonyms, iupac_name, cas_no, molecular_formula = ["N/A"] * 5

#                 for section in sections:
#                     heading = section.get("TOCHeading", "")
#                     subsections = section.get("Section", [])

#                     if heading == "Names and Identifiers":
#                         for sub in subsections:
#                             sub_heading = sub.get("TOCHeading", "")
#                             if sub_heading == "Computed Descriptors":
#                                 iupac_name = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")
#                             elif sub_heading == "Other Identifiers":
#                                 cas_no = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")
#                             elif sub_heading == "Depositor-supplied Synonyms":
#                                 synonyms_list = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
#                                 synonyms = "".join([f'"{entry.get("String", "")}", ' for entry in synonyms_list]) or "N/A"
#                                 synonyms = synonyms.rstrip(', ')  # To remove the trailing comma and space

#                             elif sub_heading == "Molecular Formula":
#                                 molecular_formula = sub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

#                     elif heading == "Chemical and Physical Properties":
#                         for sub in subsections:
#                             if sub.get("TOCHeading") == "Computed Properties":
#                                 molecular_weight = sub.get("Section", [{}])[0].get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")
#                                 if molecular_weight != "N/A":
#                                     molecular_weight += " g/mol"

#                 return [compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula]

#             elif response.status_code in [503, 429]:
#                 time.sleep(2 ** attempt)
#             elif response.status_code == 404:
#                 print(f"No data found for Compound ID {compound_id}")
#                 return None
#             else:
#                 print(f"Error {response.status_code} for Compound ID {compound_id}")
#                 return None
#         except requests.exceptions.RequestException as e:
#             print(f"Request failed for Compound ID {compound_id}: {e}")
#             time.sleep(2 ** attempt)
#     return None

# def write_to_excel(data_rows):
#     df = pd.DataFrame(data_rows, columns=[
#         "Compound ID", "Chemical Name", "Synonyms", 
#         "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"
#     ])
#     df.to_excel(OUTPUT_FILE, index=False)
#     print(f"\nSaved data to {OUTPUT_FILE}")

# def main():
#     if not os.path.exists(INPUT_CSV):
#         print(f"CSV file '{INPUT_CSV}' not found.")
#         return

#     df_input = pd.read_csv(INPUT_CSV)
#     if "compound_id" not in df_input.columns:
#         print("CSV must contain a column named 'compound_id'")
#         return

#     compound_ids = df_input["compound_id"].dropna().astype(int).tolist()
#     results = []

#     for cid in compound_ids:
#         print(f"Fetching data for Compound ID {cid}...")
#         result = fetch_compound_data(cid)
#         if result:
#             results.append(result)

#     if results:
#         write_to_excel(results)
#     else:
#         print("No data was successfully fetched.")

# if __name__ == "__main__":
#     main()



# import requests
# import pandas as pd
# import os
# import time
# from tqdm import tqdm

# # Constants
# BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"
# OUTPUT_FILE = "pubchem_compounds_from.xlsx"
# RETRIES = 5
# INPUT_CSV = "compound_ids.csv"  # Update this if your file is named differently

# def fetch_compound_data(compound_id):
#     url = BASE_URL.format(compound_id)
#     for attempt in range(RETRIES):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 record = data.get("Record", {})
#                 chemical_name = record.get("RecordTitle", "N/A")

#                 sections = record.get("Section", [])
#                 molecular_weight, synonyms, iupac_name, cas_no, molecular_formula = ["N/A"] * 5

#                 for section in sections:
#                     if section.get("TOCHeading") == "Names and Identifiers":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Descriptors":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "IUPAC Name":  # iupac name
#                                         iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                             if subsection.get("TOCHeading") == "Other Identifiers":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "CAS":  # CAS no
#                                         cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                             elif subsection.get("TOCHeading") == "Synonyms":
#                                 for subsub in subsection.get("Section", []):
#                                     if subsub.get("TOCHeading") == "Depositor-Supplied Synonyms":  # synonyms
#                                         chemical_name = subsub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                                         synonyms_list = subsub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
#                                         synonyms = [entry.get("String") for entry in synonyms_list if "String" in entry]

#                             if subsection.get("TOCHeading") == "Molecular Formula":  # molecular formula
#                                 molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                     if section.get("TOCHeading") == "Chemical and Physical Properties":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Properties":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "Molecular Weight":  # Molecular weight
#                                         molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                 return [compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula]

#             elif response.status_code in [503, 429]:
#                 time.sleep(2 ** attempt)
#             elif response.status_code == 404:
#                 print(f"No data found for Compound ID {compound_id}")
#                 return None
#             else:
#                 print(f"Error {response.status_code} for Compound ID {compound_id}")
#                 return None
#         except requests.exceptions.RequestException as e:
#             print(f"Request failed for Compound ID {compound_id}: {e}")
#             time.sleep(2 ** attempt)
#     return None

# def write_to_excel(data_rows):
#     df = pd.DataFrame(data_rows, columns=[
#         "Compound ID", "Chemical Name", "Synonyms", 
#         "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"
#     ])
#     df.to_excel(OUTPUT_FILE, index=False)
#     print(f"\nSaved data to {OUTPUT_FILE}")

# def main():
#     if not os.path.exists(INPUT_CSV):
#         print(f"CSV file '{INPUT_CSV}' not found.")
#         return

#     df_input = pd.read_csv(INPUT_CSV)
#     if "compound_id" not in df_input.columns:
#         print("CSV must contain a column named 'compound_id'")
#         return

#     compound_ids = df_input["compound_id"].dropna().astype(int).tolist()
#     results = []
#     failed_ids = []

#     for cid in tqdm(compound_ids, desc="Fetching compound data"):
#         result = fetch_compound_data(cid)
#         if result:
#             results.append(result)
#             time.sleep(0.5)  # To avoid rate limiting
#         else:
#             failed_ids.append(cid)

#     if results:
#         write_to_excel(results)
#     else:
#         print("No data was successfully fetched.")

#     if failed_ids:
#         print(f"\nFailed to fetch data for the following Compound IDs: {failed_ids}")

# if __name__ == "__main__":
#     main()



# import requests
# import pandas as pd
# import os
# import time
# from tqdm import tqdm

# # Constants
# BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"
# OUTPUT_FILE = "pubchem_compounds_from.xlsx"
# RETRIES = 5
# INPUT_CSV = "compound_ids.csv"  # Update this if your file is named differently

# def fetch_compound_data(compound_id):
#     url = BASE_URL.format(compound_id)
#     for attempt in range(RETRIES):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 record = data.get("Record", {})
#                 chemical_name = record.get("RecordTitle", "N/A")

#                 sections = record.get("Section", [])
#                 molecular_weight, synonyms, iupac_name, cas_no, molecular_formula = ["N/A"] * 5

#                 for section in sections:
#                     if section.get("TOCHeading") == "Names and Identifiers":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Descriptors":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "IUPAC Name":  # iupac name
#                                         iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                             if subsection.get("TOCHeading") == "Other Identifiers":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "CAS":  # CAS no
#                                         cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                             elif subsection.get("TOCHeading") == "Synonyms":
#                                 for subsub in subsection.get("Section", []):
#                                     if subsub.get("TOCHeading") == "Depositor-Supplied Synonyms":  # synonyms
#                                         chemical_name = subsub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                                         synonyms_list = subsub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
#                                         synonyms = '", "'.join([entry.get("String") for entry in synonyms_list if "String" in entry])
#                                         synonyms = f'"{synonyms}"' if synonyms else "N/A"

#                             if subsection.get("TOCHeading") == "Molecular Formula":  # molecular formula
#                                 molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                     if section.get("TOCHeading") == "Chemical and Physical Properties":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Properties":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "Molecular Weight":  # Molecular weight
#                                         molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                 return [compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula]

#             elif response.status_code in [503, 429]:
#                 time.sleep(2 ** attempt)
#             elif response.status_code == 404:
#                 print(f"No data found for Compound ID {compound_id}")
#                 return None
#             else:
#                 print(f"Error {response.status_code} for Compound ID {compound_id}")
#                 return None
#         except requests.exceptions.RequestException as e:
#             print(f"Request failed for Compound ID {compound_id}: {e}")
#             time.sleep(2 ** attempt)
#     return None

# def write_to_excel(data_rows):
#     df = pd.DataFrame(data_rows, columns=[
#         "Compound ID", "Chemical Name", "Synonyms", 
#         "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"
#     ])
#     df.to_excel(OUTPUT_FILE, index=False)
#     print(f"\nSaved data to {OUTPUT_FILE}")

# def main():
#     if not os.path.exists(INPUT_CSV):
#         print(f"CSV file '{INPUT_CSV}' not found.")
#         return

#     df_input = pd.read_csv(INPUT_CSV)
#     if "compound_id" not in df_input.columns:
#         print("CSV must contain a column named 'compound_id'")
#         return

#     compound_ids = df_input["compound_id"].dropna().astype(int).tolist()
#     results = []
#     failed_ids = []

#     for cid in tqdm(compound_ids, desc="Fetching compound data"):
#         result = fetch_compound_data(cid)
#         if result:
#             results.append(result)
#             time.sleep(0.5)  # To avoid rate limiting
#         else:
#             failed_ids.append(cid)

#     if results:
#         write_to_excel(results)
#     else:
#         print("No data was successfully fetched.")

#     if failed_ids:
#         print(f"\nFailed to fetch data for the following Compound IDs: {failed_ids}")

# if __name__ == "__main__":
#     main()


# import requests
# import pandas as pd
# import os
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import time

# # Constants
# BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"
# OUTPUT_FILE = "pubchem_compounds_from_1886.xlsx"
# RETRIES = 5
# NUM_THREADS = os.cpu_count() * 2
# BATCH_SIZE = 150
# INPUT_CSV = "compound_ids.csv"  # Your original input file

# def fetch_compound_data(compound_id):
#     url = BASE_URL.format(compound_id)
#     for attempt in range(RETRIES):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 record = data.get("Record", {})
#                 chemical_name = record.get("RecordTitle", "N/A")

#                 sections = record.get("Section", [])
#                 molecular_weight, synonyms, iupac_name, cas_no, molecular_formula = ["N/A"] * 5

#                 for section in sections:
#                     if section.get("TOCHeading") == "Names and Identifiers":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Descriptors":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "IUPAC Name":
#                                         iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

#                             if subsection.get("TOCHeading") == "Other Identifiers":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "CAS":
#                                         cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

#                             elif subsection.get("TOCHeading") == "Synonyms":
#                                 for subsub in subsection.get("Section", []):
#                                     if subsub.get("TOCHeading") == "Depositor-Supplied Synonyms":
#                                         synonyms_list = subsub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
#                                         synonyms = '", "'.join([entry.get("String") for entry in synonyms_list if "String" in entry])
#                                         synonyms = f'"{synonyms}"' if synonyms else "N/A"

#                             if subsection.get("TOCHeading") == "Molecular Formula":
#                                 molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

#                     if section.get("TOCHeading") == "Chemical and Physical Properties":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Properties":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "Molecular Weight":
#                                         molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

#                 return [compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula]

#             elif response.status_code in [503, 429]:
#                 time.sleep(2 ** attempt)
#             elif response.status_code == 404:
#                 print(f"No data found for Compound ID {compound_id}")
#                 return None
#             else:
#                 print(f"Error {response.status_code} for Compound ID {compound_id}")
#                 return None
#         except requests.exceptions.RequestException as e:
#             print(f"Request failed for Compound ID {compound_id}: {e}")
#             time.sleep(2 ** attempt)
#     return None

# def write_to_excel(data_rows):
#     df = pd.DataFrame(data_rows, columns=[
#         "Compound ID", "Chemical Name", "Synonyms",
#         "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"
#     ])

#     if os.path.exists(OUTPUT_FILE):
#         with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
#             df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
#     else:
#         df.to_excel(OUTPUT_FILE, index=False)

#     print(f"Saved {len(data_rows)} records to {OUTPUT_FILE}")

# def main():
#     if not os.path.exists(INPUT_CSV):
#         print(f"CSV file '{INPUT_CSV}' not found.")
#         return

#     df_input = pd.read_csv(INPUT_CSV)
#     if "compound_id" not in df_input.columns:
#         print("CSV must contain a column named 'compound_id'")
#         return

#     compound_ids = df_input["compound_id"].dropna().astype(int).tolist()

#     results = []
#     failed_ids = []

#     with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
#         futures = {executor.submit(fetch_compound_data, cid): cid for cid in compound_ids}

#         for future in as_completed(futures):
#             cid = futures[future]
#             try:
#                 res = future.result()
#                 if res:
#                     results.append(res)
#                     print(f"Fetched data for Compound ID {cid}")
#                 else:
#                     failed_ids.append(cid)

#                 if len(results) >= BATCH_SIZE:
#                     write_to_excel(results)
#                     results.clear()

#             except Exception as e:
#                 print(f"Error fetching data for Compound ID {cid}: {e}")
#                 failed_ids.append(cid)

#     if results:
#         write_to_excel(results)

#     if failed_ids:
#         print(f"Retrying {len(failed_ids)} failed IDs...")
#         retry_results = []
#         with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
#             retry_futures = {executor.submit(fetch_compound_data, cid): cid for cid in failed_ids}
#             for future in as_completed(retry_futures):
#                 cid = retry_futures[future]
#                 try:
#                     res = future.result()
#                     if res:
#                         retry_results.append(res)
#                         print(f"Fetched data for Compound ID {cid} on retry")
#                 except Exception as e:
#                     print(f"Retry failed for Compound ID {cid}: {e}")

#         if retry_results:
#             write_to_excel(retry_results)

#     print("Data extraction complete.")

# if __name__ == "__main__":
#     main()



import requests
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Constants
BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"
OUTPUT_FILE = "pubchem_compounds_from_36.xlsx"
RETRIES = 5
NUM_THREADS = os.cpu_count() * 2
BATCH_SIZE = 150
INPUT_CSV = "compound_ids.csv"  # Your original input file

def fetch_compound_data(compound_id):
    url = BASE_URL.format(compound_id)
    for attempt in range(RETRIES):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                record = data.get("Record", {})
                chemical_name = record.get("RecordTitle", "N/A")

                sections = record.get("Section", [])
                molecular_weight, synonyms, iupac_name, cas_no, molecular_formula = ["N/A"] * 5

                for section in sections:
                    if section.get("TOCHeading") == "Names and Identifiers":
                        for subsection in section.get("Section", []):
                            if subsection.get("TOCHeading") == "Computed Descriptors":
                                for subsubsection in subsection.get("Section", []):
                                    if subsubsection.get("TOCHeading") == "IUPAC Name":
                                        iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

                            if subsection.get("TOCHeading") == "Other Identifiers":
                                for subsubsection in subsection.get("Section", []):
                                    if subsubsection.get("TOCHeading") == "CAS":
                                        cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

                            elif subsection.get("TOCHeading") == "Synonyms":
                                for subsub in subsection.get("Section", []):
                                    if subsub.get("TOCHeading") == "Depositor-Supplied Synonyms":
                                        synonyms_list = subsub.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
                                        synonyms = '", "'.join([entry.get("String") for entry in synonyms_list if "String" in entry])
                                        synonyms = f'"{synonyms}"' if synonyms else "N/A"

                            if subsection.get("TOCHeading") == "Molecular Formula":
                                molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

                    if section.get("TOCHeading") == "Chemical and Physical Properties":
                        for subsection in section.get("Section", []):
                            if subsection.get("TOCHeading") == "Computed Properties":
                                for subsubsection in subsection.get("Section", []):
                                    if subsubsection.get("TOCHeading") == "Molecular Weight":
                                        molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", "N/A")

                return [compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula]

            elif response.status_code in [503, 429]:
                time.sleep(2 ** attempt)
            elif response.status_code == 404:
                print(f"No data found for Compound ID {compound_id}")
                return None
            else:
                print(f"Error {response.status_code} for Compound ID {compound_id}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed for Compound ID {compound_id}: {e}")
            time.sleep(2 ** attempt)
    return None

def write_to_excel(data_rows):
    df = pd.DataFrame(data_rows, columns=[
        "Compound ID", "Chemical Name", "Synonyms",
        "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"
    ])

    if os.path.exists(OUTPUT_FILE):
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
    else:
        df.to_excel(OUTPUT_FILE, index=False)

    print(f"Saved {len(data_rows)} records to {OUTPUT_FILE}")

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"CSV file '{INPUT_CSV}' not found.")
        return

    # Attempt to read CSV using UTF-8, fallback to Latin-1 if needed
    try:
        df_input = pd.read_csv(INPUT_CSV, encoding='utf-8')
    except UnicodeDecodeError:
        print("UTF-8 decoding failed. Retrying with Latin-1 encoding...")
        df_input = pd.read_csv(INPUT_CSV, encoding='latin1')

    if "compound_id" not in df_input.columns:
        print("CSV must contain a column named 'compound_id'")
        return

    # Clean compound_id: remove all non-digit characters
    df_input["compound_id"] = (
        df_input["compound_id"]
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)
    )

    # Drop rows where compound_id is now empty
    df_input = df_input[df_input["compound_id"].str.strip() != ""]

    # Convert to integer list
    compound_ids = df_input["compound_id"].astype(int).tolist()

    results = []
    failed_ids = []

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = {executor.submit(fetch_compound_data, cid): cid for cid in compound_ids}

        for future in as_completed(futures):
            cid = futures[future]
            try:
                res = future.result()
                if res:
                    results.append(res)
                    print(f"Fetched data for Compound ID {cid}")
                else:
                    failed_ids.append(cid)

                if len(results) >= BATCH_SIZE:
                    write_to_excel(results)
                    results.clear()

            except Exception as e:
                print(f"Error fetching data for Compound ID {cid}: {e}")
                failed_ids.append(cid)

    if results:
        write_to_excel(results)

    if failed_ids:
        print(f"Retrying {len(failed_ids)} failed IDs...")
        retry_results = []
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            retry_futures = {executor.submit(fetch_compound_data, cid): cid for cid in failed_ids}
            for future in as_completed(retry_futures):
                cid = retry_futures[future]
                try:
                    res = future.result()
                    if res:
                        retry_results.append(res)
                        print(f"Fetched data for Compound ID {cid} on retry")
                except Exception as e:
                    print(f"Retry failed for Compound ID {cid}: {e}")

        if retry_results:
            write_to_excel(retry_results)

    print("Data extraction complete.")

if __name__ == "__main__":
    main()
