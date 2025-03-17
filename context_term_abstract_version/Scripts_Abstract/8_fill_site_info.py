import pandas as pd
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# Load JSON data
json_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/modified_pmid_results.json')
with open(json_file_path, 'r') as file:
    json_data = json.load(file)

# Load existing Excel file
excel_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/new_dis_spec_tis_cel_output.xlsx')
df = pd.read_excel(excel_file_path)

# Append new rows based on JSON data
new_rows = []
for entry in json_data:
    docId = entry.get('docId')
    if 'entity' in entry:  # Check if 'entity' key exists to handle empty entries
        for entity in entry['entity']:  # Correct key is 'entity'
            new_row = {
                'pmid': docId,
                'start_offset': entity.get('charStart'),
                'end_offset': entity.get('charEnd'),
                'entity': entity.get('entityText'),  
                'entity_type': 'Site',  
                'source': entity.get('source', 'SiteDetectorTool'),  # Use source from JSON or default
                'sentence': entity.get('sentence'),
                'sent_index': entity.get('sentenceIndex'),  # Add this if you have a 'sent_index' column
            }
            new_rows.append(new_row)

# Convert new rows to DataFrame
new_df = pd.DataFrame(new_rows)

# Append new DataFrame to the existing one
final_df = pd.concat([df, new_df], ignore_index=True)

# Convert 'pmid' and 'sent_index' to integers for proper sorting
final_df['pmid'] = final_df['pmid'].astype(int)
final_df['sent_index'] = final_df['sent_index'].astype(int)

# Sort the DataFrame
final_df.sort_values(by=['pmid', 'sent_index'], inplace=True)

column_order = ['pmid', 'entity', 'entity_type', 'start_offset', 'end_offset', 'source', 'id', 'doid_for_diseases', 'uniprot_ac', 'sent_index', 'sentence']
final_df = final_df[column_order]  # Reorder columns

# Save the updated DataFrame back to Excel
final_df.to_excel(excel_file_path, index=False)

print("Excel sheet has been updated successfully with new rows.")
