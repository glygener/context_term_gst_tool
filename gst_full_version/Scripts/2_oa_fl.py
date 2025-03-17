import os
import pandas as pd
import time
import requests
import xml.etree.ElementTree as ET

def read_pc_ids_from_excel(file_path, column_name="PMCID"):
    # Load the Excel file and extract the PMCID column
    df = pd.read_excel(file_path)
    # Ensure there are no NaN values and strip leading/trailing spaces
    pc_ids = df[column_name].dropna().astype(str).str.strip().tolist()
    return pc_ids

def download_article(pc_id, output_dir):
    url = f"https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/pmc_export/biocxml?pmcids={pc_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        file_path = os.path.join(output_dir, f"{pc_id}.xml")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {pc_id}")

        # Check if the file contains annotations
        if not has_annotations(file_path):
            print(f"Warning: {pc_id} does not contain any annotations.")
    elif response.status_code == 429:
        print(f"Rate limit exceeded for {pc_id}, will retry later.")
        return False
    else:
        print(f"Failed to download {pc_id}: Status code {response.status_code}")
    return True

def has_annotations(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    annotations = root.findall('.//annotation')
    return len(annotations) > 0

def main(pc_ids_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    pc_ids = read_pc_ids_from_excel(pc_ids_file)
    
    for pc_id in pc_ids:
        success = download_article(pc_id, output_dir)
        if not success:
            time.sleep(60)  # Wait for 60 seconds before retrying
            download_article(pc_id, output_dir)
        else:
            time.sleep(1)  # Short delay between requests to avoid rate limit


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pc_ids_file = os.path.join(base_dir, '/app/gst_full/Outputs/pmids_pmcids.xlsx')  # Replace with the path to your file containing PC IDs
    output_dir = os.path.join(base_dir, '/app/gst_full/bioc_xml_fl')  # Replace with your desired output directory
    
    main(pc_ids_file, output_dir)
