import requests
import os
import time

base_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative paths
pmid_file_path = os.path.join(base_dir, '/app/test.txt')
output_dir = os.path.join(base_dir, '/app/gst_abstract/abstract_xml')

# Define the relative paths
#pmid_file_path = "/home/shovan/nlputils/EDG_framework/context_term_new/pmid.txt"
#output_dir = "/home/shovan/nlputils/EDG_framework/context_term_new/biocxml_pubtator"

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Read the PMIDs from the text file
with open(pmid_file_path, 'r') as file:
    pmids = [line.strip() for line in file if line.strip()]

# Base URL for the PubTator API
#base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocxml?pmids="
base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocxml?pmids="
#extension = "&full=true"

# Iterate through each PMID and make individual requests
for pmid in pmids:
    #url = f"{base_url}{pmid}{extension}"
    url = f"{base_url}{pmid}"
    
    while True:
        # Make the HTTP GET request without the Accept header
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the response content as a file in the output directory
            output_file = os.path.join(output_dir, f"{pmid}.xml")
            with open(output_file, "wb") as file:
                file.write(response.content)
            print(f"File saved successfully for PMID: {pmid}")
            break  # Exit the loop and move to the next PMID
        elif response.status_code == 429:
            # Handle rate limiting
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            # Print the error message and headers to understand the supported formats
            try:
                error_message = response.json()
                print(f"Failed to retrieve data for PMID: {pmid}. HTTP Status Code: {response.status_code} Content-Type: {response.headers.get('Content-Type')} Error: {error_message}")
            except ValueError:
                print(f"Failed to retrieve data for PMID: {pmid}. HTTP Status Code: {response.status_code} Content-Type: {response.headers.get('Content-Type')} No JSON error message found.")
            break  # Exit the loop and move to the next PMID
