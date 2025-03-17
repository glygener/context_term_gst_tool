import json
import pandas as pd
import os


base_dir = os.path.dirname(os.path.abspath(__file__))
# Load the JSON file
json_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/filtered_pmid_results.json')
excel_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/sentences.xlsx')
updated_json_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/modified_pmid_results.json')

# Load JSON and Excel files
with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

excel_data = pd.read_excel(excel_file_path)

# Create a lookup dictionary from the Excel file
sentence_lookup = {
    (str(row['pmid']), int(row['sent_index'])): row['sent_text']
    for _, row in excel_data.iterrows()
}

# Update sentences in JSON data
for entry in json_data:
    doc_id = entry.get('docId')
    if not doc_id or 'entity' not in entry:
        continue

    for entity in entry['entity']:
        sent_index = entity.get('sentenceIndex')
        if sent_index is not None:
            # Look up the sentence text based on pmid and sent_index
            sentence = sentence_lookup.get((doc_id, sent_index))
            if sentence:
                entity['sentence'] = sentence

# Save the updated JSON file
with open(updated_json_file_path, 'w') as updated_json_file:
    json.dump(json_data, updated_json_file, indent=4)

print(f"Updated JSON saved to {updated_json_file_path}")
