# import requests
# import pandas as pd
# import os
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import time

# # Define the base URL
# base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"

# # Excel file name
# output_file = "pubchem_compounds_170000000-170000100.xlsx"
# failed_id_track = []

# # Function to fetch data for a specific compound ID with retry for 503 errors
# def fetch_compound_data(compound_id, retries=20, backoff_factor=2):
#     url = base_url.format(compound_id)
#     for attempt in range(1, retries + 1):
#         try:
#             response = requests.get(url, timeout=120)  # Set a timeout for the request
#             if response.status_code == 200:
#                 # Parse the JSON response
#                 data = response.json()
#                 # Extract required fields
#                 molecular_weight = None
#                 synonyms = None
#                 iupac_name = None
#                 chemical_name = None
#                 molecular_formula = None
#                 cas_no = None

#                 sections = data.get("Record", {}).get("Section", [])
#                 chemical_name = data.get("Record", {}).get("RecordTitle")

#                 for section in sections:
#                     if section.get("TOCHeading") == "Names and Identifiers":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Descriptors":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "IUPAC Name":
#                                         iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                             if subsection.get("TOCHeading") == "Other Identifiers":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "CAS":
#                                         cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                             elif subsection.get("TOCHeading") == "Synonyms":
#                                 for item in subsection.get("Section", []):
#                                     if item.get("TOCHeading") == "Depositor-Supplied Synonyms":
#                                         synonyms_list = item.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
#                                         # Extract all strings from the list
#                                         synonyms = [entry.get("String") for entry in synonyms_list if "String" in entry]
#                             elif subsection.get("TOCHeading") == "Molecular Formula":
#                                 molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                     if section.get("TOCHeading") == "Chemical and Physical Properties":
#                         for subsection in section.get("Section", []):
#                             if subsection.get("TOCHeading") == "Computed Properties":
#                                 for subsubsection in subsection.get("Section", []):
#                                     if subsubsection.get("TOCHeading") == "Molecular Weight":
#                                         molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                                         if molecular_weight:
#                                             molecular_weight += " g/mol"  # Add unit to molecular weight

#                 # Handle missing or unavailable fields
#                 molecular_weight = molecular_weight or "N/A"
#                 synonyms = ", ".join(synonyms) if synonyms else "N/A"
#                 iupac_name = iupac_name or "N/A"
#                 chemical_name = chemical_name or "N/A"
#                 molecular_formula = molecular_formula or "N/A"
#                 cas_no = cas_no or "N/A"

#                 return compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula

#             elif response.status_code == 503:
#                 print(f"503 Error for Compound ID {compound_id}, attempt {attempt}. Retrying...")
#                 time.sleep(backoff_factor ** attempt)  # Exponential backoff
#             elif response.status_code == 404:
#                 print(f"Compound ID {compound_id} not found.")
#                 return None
#             else:
#                 print(f"HTTP Error {response.status_code} for Compound ID {compound_id}")
#                 return None
#         except requests.exceptions.RequestException as e:
#             print(f"Request error for Compound ID {compound_id}, attempt {attempt}: {e}")

#     print(f"Failed to fetch data for Compound ID {compound_id} after {retries} attempts.")
#     return None


# # Function to append data to the Excel file
# def append_to_excel(data_list):
#     df = pd.DataFrame(data_list, columns=["Compound ID", "Chemical Name", "Synonyms", "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"])
#     if os.path.exists(output_file):
#         with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
#             df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
#     else:
#         df.to_excel(output_file, index=False, header=True)


# # Main function to fetch data and save it to the Excel file
# def main():
#     # Set the range of compound IDs to iterate over
#     start_id = 1
#     end_id = 100  # Adjust this range as needed
#     num_threads = 15  # Number of threads to use

#     failed_ids = []  # To keep track of failed compound IDs

#     # Use ThreadPoolExecutor for multithreading
#     with ThreadPoolExecutor(max_workers=num_threads) as executor:
#         futures = {executor.submit(fetch_compound_data, compound_id): compound_id for compound_id in range(start_id, end_id + 1)}

#         batch_data = []  # Collect data in batches to reduce file I/O operations
#         for future in as_completed(futures):
#             compound_id = futures[future]
#             try:
#                 result = future.result()
#                 if result:
#                     batch_data.append(result)
#                     print(f"Data for Compound ID {compound_id} fetched.")
#                 else:
#                     failed_ids.append(compound_id)
#             except Exception as e:
#                 print(f"Error fetching data for Compound ID {compound_id}: {e}")
#                 failed_ids.append(compound_id)

#             # Write data to Excel in batches to reduce I/O overhead
#             if len(batch_data) >= 20:  # Adjust batch size as needed
#                 append_to_excel(batch_data)
#                 batch_data = []

#         # Write remaining data
#         if batch_data:
#             append_to_excel(batch_data)

#     # Retry for failed IDs
#     if failed_ids:
#         print(f"Retrying failed IDs: {failed_ids}")
#         failed_id_track.extend(failed_ids)
#         for compound_id in failed_ids:
#             result = fetch_compound_data(compound_id)
#             if result:
#                 append_to_excel([result])
#                 print(f"Data for Compound ID {compound_id} fetched on retry.")


# if __name__ == "__main__":
#     main()



import requests
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Define the base URL
base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"

# Excel file name
output_file = "pubchem_compounds_530001-550000xlsx.xlsx"
failed_id_track = []

# Function to fetch data for a specific compound ID with retry for 503 errors
def fetch_compound_data(compound_id, retries=5, backoff_factor=2):
    url = base_url.format(compound_id)
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=120)  # Set a timeout for the request
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                # Extract required fields
                molecular_weight = None
                synonyms = None
                iupac_name = None
                chemical_name = None
                molecular_formula = None
                cas_no = None

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
                                        # Extract all strings from the list
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
                                            molecular_weight += " g/mol"  # Add unit to molecular weight

                # Handle missing or unavailable fields
                molecular_weight = molecular_weight or "N/A"
                synonyms = ", ".join(synonyms) if synonyms else "N/A"
                iupac_name = iupac_name or "N/A"
                chemical_name = chemical_name or "N/A"
                molecular_formula = molecular_formula or "N/A"
                cas_no = cas_no or "N/A"

                return compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula

            elif response.status_code == 503:
                print(f"503 Error for Compound ID {compound_id}, attempt {attempt}. Retrying...")
                time.sleep(backoff_factor ** attempt)  # Exponential backoff
            elif response.status_code == 404:
                print(f"Compound ID {compound_id} not found.")
                return None
            else:
                print(f"HTTP Error {response.status_code} for Compound ID {compound_id}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error for Compound ID {compound_id}, attempt {attempt}: {e}")

    print(f"Failed to fetch data for Compound ID {compound_id} after {retries} attempts.")
    return None

# Function to append data to the Excel file
def append_to_excel(data_list):
    df = pd.DataFrame(data_list, columns=["Compound ID", "Chemical Name", "Synonyms", "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"])
    # Check if the file exists to decide whether to append or create a new one
    if os.path.exists(output_file):
        # If the file exists, append data without writing the header again
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
    else:
        # If the file doesn't exist, create a new file with the header
        df.to_excel(output_file, index=False, header=True)

# Main function to fetch data and save it to the Excel file
def main():
    # Set the range of compound IDs to iterate over
    start_id = 530001
    end_id = 550000  # Adjust this range as needed
    num_threads = 15  # Number of threads to use

    failed_ids = []  # To keep track of failed compound IDs

    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(fetch_compound_data, compound_id): compound_id for compound_id in range(start_id, end_id + 1)}

        batch_data = []  # Collect data in batches to reduce file I/O operations
        for future in as_completed(futures):
            compound_id = futures[future]
            try:
                result = future.result()
                if result:
                    batch_data.append(result)
                    print(f"Data for Compound ID {compound_id} fetched.")
                else:
                    failed_ids.append(compound_id)
            except Exception as e:
                print(f"Error fetching data for Compound ID {compound_id}: {e}")
                failed_ids.append(compound_id)

            # Write data to Excel in batches to reduce I/O overhead
            if len(batch_data) >= 100:  # Increased batch size
                append_to_excel(batch_data)
                batch_data = []

        # Write remaining data
        if batch_data:
            append_to_excel(batch_data)

    # Retry for failed IDs
    if failed_ids:
        print(f"Retrying failed IDs: {failed_ids}")
        failed_id_track.extend(failed_ids)
        for compound_id in failed_ids:
            result = fetch_compound_data(compound_id)
            if result:
                append_to_excel([result])
                print(f"Data for Compound ID {compound_id} fetched on retry.")

if __name__ == "__main__":
    main()