# import requests
# from random import choice

# # List of proxies (from the list you provided)
# proxies_list = [
#     "123.45.67.89:443"
# ]

# # Select a random proxy from the list
# proxy = choice(proxies_list)

# # Set up proxies
# proxies = {
#     "http": f"http://{proxy}",
#     "https": f"https://{proxy}",
# }

# # URL to fetch data
# url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/1/JSON/"

# # Attempt to fetch data with retry logic and increased timeout, disabling SSL verification
# try:
#     response = requests.get(url, proxies=proxies, timeout=20, verify=False)  # Disable SSL verification
#     response.raise_for_status()  # Raise an error for bad status codes
#     print(response.json())
# except requests.exceptions.RequestException as e:
#     print(f"Request failed: {e}")

