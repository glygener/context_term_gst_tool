import requests
import os
import time
import pandas as pd
import xml.etree.ElementTree as ET

# Define the base directory relative to the script location
base_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative paths
pmid_file_path = os.path.join(base_dir, '/app/test.txt')
spreadsheet_path = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/pmids_pmcids.xlsx')
missing_articles_path = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/missing_full_length_pmids.txt')

# Read the PMIDs from the text file
with open(pmid_file_path, 'r') as file:
    pmids = [line.strip() for line in file if line.strip()]

# Base URL for the PubTator API
base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocxml?pmids="
extension = "&full=true"

# List to store PMIDs and corresponding PMCIDs
pmid_pmcid_list = []

# List to store PMIDs without full-length articles
missing_pmids = []

# Iterate through each PMID and make individual requests
for pmid in pmids:
    url = f"{base_url}{pmid}{extension}"
    
    while True:
        # Make the HTTP GET request
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Parse the XML content from the response without saving to a file
                root = ET.fromstring(response.content)

                # Check if <section_type>INTRO</section_type> exists
                has_intro = any(infon.text == "INTRO" for infon in root.iter("infon"))

                if has_intro:
                    # Extract PMC ID and PMID from the XML
                    pmcid = None
                    pmid_extracted = None
                    for infon in root.iter("infon"):
                        if infon.get("key") == "article-id_pmc":
                            pmcid = infon.text
                        elif infon.get("key") == "article-id_pmid":
                            pmid_extracted = infon.text

                    if pmcid and pmid_extracted:
                        # Add "PMC" prefix to the PMCID
                        pmcid = f"PMC{pmcid}"
                        pmid_pmcid_list.append({"PMID": pmid_extracted, "PMCID": pmcid})
                        print(f"Full-length OA article found for PMID: {pmid_extracted}, PMCID: {pmcid}")
                else:
                    # Add to missing PMIDs list if no full-length article is found
                    missing_pmids.append(pmid)
                    print(f"No full-length article found for PMID: {pmid}")

            except ET.ParseError:
                print(f"Error parsing XML for PMID: {pmid}")
                missing_pmids.append(pmid)

            break  # Exit the loop and move to the next PMID
        elif response.status_code == 429:
            # Handle rate limiting
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            # Print the error message and headers
            try:
                error_message = response.json()
                print(f"Failed to retrieve data for PMID: {pmid}. HTTP Status Code: {response.status_code} Error: {error_message}")
            except ValueError:
                print(f"Failed to retrieve data for PMID: {pmid}. HTTP Status Code: {response.status_code} No JSON error message found.")
            missing_pmids.append(pmid)
            break  # Exit the loop and move to the next PMID

# Save the PMID and PMCID information to a spreadsheet
if pmid_pmcid_list:
    df = pd.DataFrame(pmid_pmcid_list)
    df.to_excel(spreadsheet_path, index=False)
    print(f"PMID and PMCID information saved to {spreadsheet_path}")
else:
    print("No full-length OA articles found.")

# Save missing PMIDs to a text file
if missing_pmids:
    with open(missing_articles_path, 'w') as file:
        for pmid in missing_pmids:
            file.write(f"{pmid}\n")
    print(f"PMIDs without full-length articles saved to {missing_articles_path}")
else:
    print("All PMIDs have full-length articles.")
