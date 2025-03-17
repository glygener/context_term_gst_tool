import json
import os
import pandas as pd
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

#output_folder = os.path.join(base_dir, 'Hydrox_Sep21_Test_Output')
output_excel_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/site_filter.xlsx')
site_json_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/pmid_results.json')
output_json = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/filtered_pmid_results.json')

# Load JSON data from the file
with open(site_json_file, 'r') as file:
    data = json.load(file)

# Prepare lists to hold rows of data for each category
filtered_rows = []
remaining_rows = []
blacklist = ["His"]

# Regular expressions for the patterns
#pattern1 = re.compile(r'^[a-zA-Z][\s\.-]*\d+$|^[a-zA-Z]\(\d+\)$|^[a-zA-Z][\s]*\(\d+\)$')
#pattern1 = re.compile(r'^(?!K\d+$)[a-zA-Z][\s\.-]*\d+$|^[a-zA-Z]\(\d+\)$|^[a-zA-Z][\s]*\(\d+\)$')
pattern = re.compile(r'^(?![SNT][\s\.-]*\d+$)[A-Za-z][\s\.-]*\d+$')
blacklist_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(term) for term in blacklist) + r')\b', re.IGNORECASE)
#pattern2 = re.compile(r'\b(residue|residues)\b\s*\d+-\d+', re.IGNORECASE)
#pattern3 = re.compile(r'(?<!\w\s)\b(residue|residues)\b\s+[a-zA-Z]+(\s+[a-zA-Z]+)*$', re.IGNORECASE)
#pattern_digits1 = re.compile(r'^[a-zA-Z]\d{5,}$', re.IGNORECASE)
pattern_digits = re.compile(r'^[a-zA-Z]\d{4}$')  # New pattern for letter followed by 4 or more digits

# Function to log matches for debugging
def log_matches(sites, doc_id, pattern, blacklist_pattern):
#def log_matches(sites, doc_id, pattern1, pattern_digits1, pattern_digits):
    for site in sites:
        print("DocID: {}, Site: {}".format(doc_id, site))
        print("  Matches pattern: {}".format(bool(pattern.search(site))))
        #print("  Matches pattern_digits1: {}".format(bool(pattern_digits1.search(site))))
        #print("  Matches pattern2: {}".format(bool(pattern2.search(site))))
        #print("  Matches pattern3: {}".format(bool(pattern3.search(site))))
        print("  Matches blacklist: {}".format(bool(blacklist_pattern.search(site))))
        #print("  Matches pattern_digits (letter + 3 digits): {}".format(bool(pattern_digits.search(site))))

# Iterate through each entry in the JSON data
for entry in data:
    if 'docId' in entry:
        doc_id = entry["docId"]
        specific_sites = [entity for entity in entry["entity"] if entity["entityType"] == "SpecificSite" or entity["entityType"] == "AminoAcid"]
        
        if specific_sites:
            specific_site_texts = [site["entityText"] for site in specific_sites]
            log_matches(specific_site_texts, doc_id, pattern, blacklist_pattern)  # Log the matches
            #log_matches(specific_site_texts, doc_id, pattern1, pattern_digits1, pattern_digits) 
            
            # Filter sites according to the patterns
            filtered_sites = [
                site for site in specific_sites if
                    ((pattern.search(site["entityText"]) or
                     (blacklist_pattern.search(site["entityText"])))
                )
            ]
            remaining_sites = [
                site for site in specific_sites if site not in filtered_sites
            ]
            
            if filtered_sites:
                filtered_rows.append([doc_id] + [site["entityText"] for site in filtered_sites])
            
            # Update the entry to remove filtered sites
            entry["entity"] = [entity for entity in entry["entity"] if entity not in filtered_sites]
            
            if remaining_sites:
                remaining_rows.append([doc_id] + [site["entityText"] for site in remaining_sites])
    else:
        print("docId not found in entry: ", entry)

# Save the updated JSON data to a new file
with open(output_json, 'w') as file:
    json.dump(data, file, indent=4)


# Determine the maximum number of SpecificSites to dynamically set column names
max_filtered_sites = max(len(row) - 1 for row in filtered_rows) if filtered_rows else 0
max_remaining_sites = max(len(row) - 1 for row in remaining_rows) if remaining_rows else 0

# Create column names dynamically based on the number of SpecificSites
filtered_columns = ["docId"] + ["SpecificSite{}".format(i+1) for i in range(max_filtered_sites)]
remaining_columns = ["docId"] + ["SpecificSite{}".format(i+1) for i in range(max_remaining_sites)]

# Create DataFrames from the rows
df_filtered = pd.DataFrame(filtered_rows, columns=filtered_columns)
df_remaining = pd.DataFrame(remaining_rows, columns=remaining_columns)

# Save DataFrames to separate sheets in an Excel file
with pd.ExcelWriter(output_excel_file) as writer:
    df_filtered.to_excel(writer, sheet_name="Filtered_Sites", index=False)
    df_remaining.to_excel(writer, sheet_name="Remaining_Sites", index=False)

print("Excel file with two sheets created successfully.")


print("Filtered JSON file created successfully.")