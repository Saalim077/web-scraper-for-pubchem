import requests
import csv
import time
import concurrent.futures

# Define the base URL
base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/"

# CSV file name
output_file = "pubchem_compounds.csv"

# Create the CSV file with the specified columns
def create_csv():
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["Compound ID", "Molecular Weight", "Synonyms", "IUPAC Name", "Chemical Name", "Molecular Formula", "CAS No"])

# Append data to the CSV file
def append_to_csv(compound_id, molecular_weight, synonyms, iupac_name, molecular_formula, cas_no, chemical_name):
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the data row
        writer.writerow([compound_id, molecular_weight, synonyms, iupac_name, chemical_name, molecular_formula, cas_no])

# Function to fetch data for a specific compound ID
def fetch_compound_data(compound_id):
    url = base_url.format(compound_id)
    try:
        response = requests.get(url, timeout=60)  # Set a timeout for the request
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
            chemical_name = data.get('Record', {}).get("RecordTitle")

            for section in sections:
                if section.get("TOCHeading") == "Names and Identifiers":
                    for subsection in section.get("Section", []):
                        if subsection.get("TOCHeading") == "Computed Descriptors":
                            for subsubsection in subsection.get("Section", []):
                                if subsubsection.get("TOCHeading") == "IUPAC Name":  # iupac name
                                    iupac_name = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

                        if subsection.get("TOCHeading") == "Other Identifiers":
                            for subsubsection in subsection.get("Section", []):
                                if subsubsection.get("TOCHeading") == "CAS":  # CAS no
                                    cas_no = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")
                        
                        elif subsection.get("TOCHeading") == "Synonyms":
                            for subsection in subsection.get("Section", []):
                                if subsection.get("TOCHeading") == "Depositor-Supplied Synonyms":  # synonyms
                                    chemical_name = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String") 
                                    synonyms_list = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [])
                                    # Extract all strings from the list
                                    synonyms = [entry.get("String") for entry in synonyms_list if "String" in entry]  
                        
                        if subsection.get("TOCHeading") == "Molecular Formula":  # molecular formula
                            molecular_formula = subsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")

                if section.get("TOCHeading") == "Chemical and Physical Properties":
                    for subsection in section.get("Section", []):
                        if subsection.get("TOCHeading") == "Computed Properties":
                            for subsubsection in subsection.get("Section", []):
                                if subsubsection.get("TOCHeading") == "Molecular Weight":  # Molecular weight
                                    molecular_weight = subsubsection.get("Information", [{}])[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String")            

            # Handle missing or unavailable fields
            chemical_name = chemical_name or "N/A"
            iupac_name = iupac_name or "N/A"
            synonyms = synonyms or "N/A"
            molecular_formula = molecular_formula or "N/A"
            molecular_weight = molecular_weight or "N/A"
            cas_no = cas_no or "N/A"

            return compound_id, molecular_weight, synonyms, iupac_name, molecular_formula, cas_no, chemical_name
        elif response.status_code == 404:
            print(f"Compound ID {compound_id} not found.")
        else:
            print(f"HTTP Error {response.status_code} for Compound ID {compound_id}")
    except requests.exceptions.RequestException as e:
        print(f"Request error for Compound ID {compound_id}: {e}")
    return None

# Function to fetch data and save it to CSV using multithreading
def fetch_and_save(compound_id):
    data = fetch_compound_data(compound_id)
    if data:
        append_to_csv(*data)
        print(f"Data for Compound ID {compound_id} saved to CSV.")
    else:
        print(f"Data for Compound ID {compound_id} could not be retrieved.")

# Main function to fetch data and save it to the CSV using multithreading
def main():
    # Create the CSV file (uncomment if needed to create the CSV file)
    # create_csv()

    # Set the range of compound IDs to iterate over
    start_id = 2001
    end_id = 10000  # Adjust this range as needed

    # Using ThreadPoolExecutor for multithreading
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks for each compound_id in the range to be fetched in parallel
        compound_ids = range(start_id, end_id + 1)
        executor.map(fetch_and_save, compound_ids)

if __name__ == "__main__":
    main()
