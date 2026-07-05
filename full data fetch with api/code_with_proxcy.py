# import requests
# import csv
# import os
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import time

# # Define the base URL
# base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"

# # CSV file name
# output_file = "pubchem_compounds_30001-50000.csv"
# failed_id_track = []

# # Load proxies from a file
# def load_proxies(proxy_file="proxy.txt"):
#     proxies = []
#     if os.path.isfile(proxy_file):
#         with open(proxy_file, "r") as file:
#             proxies = [line.strip() for line in file.readlines()]
#     return proxies

# # Get the next available proxy from the list
# def get_next_proxy(proxies, current_proxy_index):
#     # Loop through the proxies and return the next one
#     next_index = (current_proxy_index + 1) % len(proxies)
#     return proxies[next_index], next_index

# # Function to fetch data for a specific compound ID with retry for 503 errors
# def fetch_compound_data(compound_id, retries=20, backoff_factor=2):
#     url = base_url.format(compound_id)
    
#     # Load proxies
#     proxies = load_proxies()
#     current_proxy_index = 0  # Start with the first proxy
    
#     if proxies:
#         proxy = {'http': proxies[current_proxy_index], 'https': proxies[current_proxy_index]}  # Use the first proxy
#     else:
#         proxy = None  # No proxy if the list is empty

#     for attempt in range(1, retries + 1):
#         try:
#             # Use requests.Session() to manage connections and apply the proxy
#             with requests.Session() as session:
#                 response = session.get(url, proxies=proxy, timeout=120)  # Set a timeout for the request
                
#                 if response.status_code == 200:
#                     # Parse the JSON response
#                     data = response.json()
#                     # Extract required fields
#                     molecular_weight = None
#                     synonyms = None
#                     iupac_name = None
#                     chemical_name = None
#                     molecular_formula = None
#                     cas_no = None

#                     sections = data.get("Record", {}).get("Section", [])
#                     chemical_name = data.get("Record", {}).get("RecordTitle")

#                     for section in sections:
#                         if section.get("TOCHeading") == "Names and Identifiers":
#                             for subsection in section.get("Section", []):
#                                 if subsection.get("TOCHeading") == "Computed Descriptors":
#                                     for subsubsection in subsection.get("Section", []):
#                                         if subsubsection.get("TOCHeading") == "IUPAC Name":
#                                             iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                                 if subsection.get("TOCHeading") == "Other Identifiers":
#                                     for subsubsection in subsection.get("Section", []):
#                                         if subsubsection.get("TOCHeading") == "CAS":
#                                             cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                                 elif subsection.get("TOCHeading") == "Synonyms":
#                                     for item in subsection.get("Section", []):
#                                         if item.get("TOCHeading") == "Depositor-Supplied Synonyms":
#                                             synonyms_list = item.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
#                                             # Extract all strings from the list
#                                             synonyms = [entry.get("String") for entry in synonyms_list if "String" in entry]
#                                 elif subsection.get("TOCHeading") == "Molecular Formula":
#                                     molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

#                         if section.get("TOCHeading") == "Chemical and Physical Properties":
#                             for subsection in section.get("Section", []):
#                                 if subsection.get("TOCHeading") == "Computed Properties":
#                                     for subsubsection in subsection.get("Section", []):
#                                         if subsubsection.get("TOCHeading") == "Molecular Weight":
#                                             molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
#                                             if molecular_weight:
#                                                 molecular_weight += " g/mol"  # Add unit to molecular weight

#                     # Handle missing or unavailable fields
#                     molecular_weight = molecular_weight or "N/A"
#                     synonyms = ", ".join(synonyms) if synonyms else "N/A"
#                     iupac_name = iupac_name or "N/A"
#                     chemical_name = chemical_name or "N/A"
#                     molecular_formula = molecular_formula or "N/A"
#                     cas_no = cas_no or "N/A"

#                     return compound_id, chemical_name, synonyms, molecular_weight, iupac_name, cas_no, molecular_formula

#                 elif response.status_code == 503:
#                     print(f"503 Error for Compound ID {compound_id}, attempt {attempt}. Changing proxy and retrying...")
#                     # Change proxy
#                     proxy, current_proxy_index = get_next_proxy(proxies, current_proxy_index)
#                     time.sleep(backoff_factor ** attempt)  # Exponential backoff
#                 elif response.status_code == 404:
#                     print(f"Compound ID {compound_id} not found.")
#                     return None
#                 else:
#                     print(f"HTTP Error {response.status_code} for Compound ID {compound_id}")
#                     return None
#         except requests.exceptions.RequestException as e:
#             print(f"Request error for Compound ID {compound_id}, attempt {attempt}: {e}")

#     print(f"Failed to fetch data for Compound ID {compound_id} after {retries} attempts.")
#     return None


# # Create the CSV file with the header
# def create_csv():
#     if not os.path.isfile(output_file):  # Only create the file if it doesn't exist
#         with open(output_file, mode="w", newline="", encoding="utf-8") as file:
#             writer = csv.writer(file)
#             writer.writerow(["Compound ID", "Chemical Name", "Synonyms", "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"])


# # Append data to the CSV file
# def append_to_csv(data_list):
#     with open(output_file, mode="a", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         writer.writerows(data_list)  # Write multiple rows at once


# # Main function to fetch data and save it to the CSV
# def main():
#     # Create the CSV file
#     create_csv()

#     # Set the range of compound IDs to iterate over
#     start_id = 30001
#     end_id = 50000  # Adjust this range as needed
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

#             # Write data to CSV in batches to reduce I/O overhead
#             if len(batch_data) >= 20:  # Adjust batch size as needed
#                 append_to_csv(batch_data)
#                 batch_data = []

#         # Write remaining data
#         if batch_data:
#             append_to_csv(batch_data)

#     # Retry for failed IDs
#     if failed_ids:
#         print(f"Retrying failed IDs: {failed_ids}")
#         failed_id_track.extend(failed_ids)
#         for compound_id in failed_ids:
#             result = fetch_compound_data(compound_id)
#             if result:
#                 append_to_csv([result])
#                 print(f"Data for Compound ID {compound_id} fetched on retry.")

# if __name__ == "__main__":
#     main()


# 








import requests
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

# Define the base URL
base_url = "http://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"

# CSV file name
output_file = "pubchem_compounds_50001-700001111111.csv"
failed_id_track = []

# List of proxy addresses (your proxy list)
proxies_list = [
    "103.117.192.10:80",
"47.254.158.115:8080",
"8.209.68.1:8024"
    # Add more proxies as needed
]

    # Add the rest of your proxies here...


# Function to test if a proxy is working
def test_proxy(proxy):
    test_url = "https://httpbin.org/ip"
    proxies = {
        "http": f"http://{proxy}",
        "https": f"https://{proxy}"
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working. Response: {response.json()}")
            return True
        else:
            print(f"Proxy {proxy} failed with status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Proxy {proxy} failed. Error: {e}")
        return False

# Function to fetch data for a specific compound ID with retry for 503 errors
def fetch_compound_data(compound_id, retries=20, backoff_factor=2):
    url = base_url.format(compound_id)
    
    # Rotate through proxies
    proxy = random.choice(proxies_list)
    proxies = {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}'
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=120, proxies=proxies, verify=False)
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
                print(f"503 Error for Compound ID {compound_id}, attempt {attempt}. Retrying with proxy {proxy}...")
                time.sleep(backoff_factor ** attempt)  # Exponential backoff
            elif response.status_code == 404:
                print(f"Compound ID {compound_id} not found.")
                return None
            else:
                print(f"HTTP Error {response.status_code} for Compound ID {compound_id} using proxy {proxy}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error for Compound ID {compound_id}, attempt {attempt}: {e} using proxy {proxy}")

    print(f"Failed to fetch data for Compound ID {compound_id} after {retries} attempts.")
    return None

# Create the CSV file with the header
def create_csv():
    if not os.path.isfile(output_file):  # Only create the file if it doesn't exist
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Compound ID", "Chemical Name", "Synonyms", "Molecular Weight", "IUPAC Name", "CAS No.", "Molecular Formula"])

# Append data to the CSV file
def append_to_csv(data_list):
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data_list)  # Write multiple rows at once

# Main function to fetch data and save it to the CSV
def main():
    # Create the CSV file
    create_csv()

    # Test all proxies and filter out the non-working ones
    global proxies_list
    proxies_list = [proxy for proxy in proxies_list if test_proxy(proxy)]

    # Set the range of compound IDs to iterate over
    start_id = 5
    end_id = 15  # Adjust this range as needed
    num_threads = 18  # Number of threads to use

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

            # Write data to CSV in batches to reduce I/O overhead
            if len(batch_data) >= 20:  # Adjust batch size as needed
                append_to_csv(batch_data)
                batch_data = []

        # Write remaining data
        if batch_data:
            append_to_csv(batch_data)

    # Retry for failed IDs
    if failed_ids:
        print(f"Retrying failed IDs: {failed_ids}")
        failed_id_track.extend(failed_ids)
        for compound_id in failed_ids:
            result = fetch_compound_data(compound_id)
            if result:
                append_to_csv([result])
                print(f"Data for Compound ID {compound_id} fetched on retry.")

if __name__ == "__main__":
    main()

