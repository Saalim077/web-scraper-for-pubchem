# import pandas as pd
# import requests
# import os
# import re
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from openpyxl import load_workbook

# # Load input Excel file
# uploaded_excel_path = "Book12610866.xlsx"
# df = pd.read_excel(uploaded_excel_path)
# chemical_names = df.iloc[:, 0].dropna().astype(str).tolist()

# # Output file path
# output_path = "pubchem_results_with_cas_11589_saalim_full.xlsx"

# # Function to fetch data from PubChem
# def get_pubchem_data_with_cas(compound_name):
#     base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
#     headers = {"User-Agent": "Mozilla/5.0"}

#     try:
#         prop_url = f"{base_url}/compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
#         syn_url = f"{base_url}/compound/name/{compound_name}/synonyms/JSON"

#         prop_response = requests.get(prop_url, headers=headers, timeout=8)
#         prop_response.raise_for_status()
#         props = prop_response.json()["PropertyTable"]["Properties"][0]

#         try:
#             syn_response = requests.get(syn_url, headers=headers, timeout=8)
#             syn_response.raise_for_status()
#             synonyms = syn_response.json()["InformationList"]["Information"][0].get("Synonym", [])
#         except:
#             synonyms = []

#         all_synonyms = [compound_name] + synonyms
#         cas_number = next((s for s in all_synonyms if re.fullmatch(r"\d{2,7}-\d{2}-\d", s)), "")

#         return {
#             "Name": compound_name,
#             "CID": props.get("CID", ""),
#             "Formula": props.get("MolecularFormula", ""),
#             "Weight": props.get("MolecularWeight", ""),
#             "IUPAC": props.get("IUPACName", ""),
#             "CAS": cas_number,
#             "Synonyms": ", ".join(f'"{s}"' for s in all_synonyms[:100])
#         }

#     except Exception as e:
#         return {
#             "Name": compound_name, "CID": "", "Formula": "", "Weight": "",
#             "IUPAC": "", "CAS": "", "Synonyms": f"Error: {e}"
#         }

# # Multithreaded fetching
# results = []
# with ThreadPoolExecutor(max_workers=10) as executor:
#     future_to_name = {executor.submit(get_pubchem_data_with_cas, name): name for name in chemical_names}
#     for i, future in enumerate(as_completed(future_to_name), 1):
#         result = future.result()
#         results.append(result)
#         print(f"Processed {i}/{len(chemical_names)}: {result['Name']}")

# # Write all results at once
# df_result = pd.DataFrame(results)

# if not os.path.exists(output_path):
#     df_result.to_excel(output_path, index=False)
# else:
#     with pd.ExcelWriter(output_path, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
#         existing = pd.read_excel(output_path)
#         df_result.to_excel(writer, startrow=len(existing)+1, header=False, index=False)



import pandas as pd
import requests
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from openpyxl import load_workbook

# Load input Excel file
uploaded_excel_path = "Book12610866.xlsx"
df = pd.read_excel(uploaded_excel_path)
chemical_names = df.iloc[:, 0].dropna().astype(str).tolist()

# Output file path
output_path = "pubchem_results_with_cas_11589_saalim_full_2.xlsx"

# Function to fetch data from PubChem
def get_pubchem_data_with_cas(compound_name):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        prop_url = f"{base_url}/compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
        syn_url = f"{base_url}/compound/name/{compound_name}/synonyms/JSON"

        prop_response = requests.get(prop_url, headers=headers, timeout=8)
        prop_response.raise_for_status()
        props = prop_response.json()["PropertyTable"]["Properties"][0]

        try:
            syn_response = requests.get(syn_url, headers=headers, timeout=8)
            syn_response.raise_for_status()
            synonyms = syn_response.json()["InformationList"]["Information"][0].get("Synonym", [])
        except:
            synonyms = []

        all_synonyms = [compound_name] + synonyms
        cas_number = next((s for s in all_synonyms if re.fullmatch(r"\d{2,7}-\d{2}-\d", s)), "")
        
        # Construct the PubChem source URL
        pubchem_url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{props.get('CID', '')}"

        return {
            "Name": compound_name,
            "CID": props.get("CID", ""),
            "Formula": props.get("MolecularFormula", ""),
            "Weight": props.get("MolecularWeight", ""),
            "IUPAC": props.get("IUPACName", ""),
            "CAS": cas_number,
            "Synonyms": ", ".join(f'"{s}"' for s in all_synonyms[:100]),
            "Source_URL": pubchem_url  # Add the source URL here
        }

    except Exception as e:
        return {
            "Name": compound_name, "CID": "", "Formula": "", "Weight": "",
            "IUPAC": "", "CAS": "", "Synonyms": f"Error: {e}", "Source_URL": ""
        }

# Multithreaded fetching
results = []
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_name = {executor.submit(get_pubchem_data_with_cas, name): name for name in chemical_names}
    for i, future in enumerate(as_completed(future_to_name), 1):
        result = future.result()
        results.append(result)
        print(f"Processed {i}/{len(chemical_names)}: {result['Name']}")

# Write all results at once
df_result = pd.DataFrame(results)

if not os.path.exists(output_path):
    df_result.to_excel(output_path, index=False)
else:
    with pd.ExcelWriter(output_path, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
        existing = pd.read_excel(output_path)
        df_result.to_excel(writer, startrow=len(existing)+1, header=False, index=False)
