import pandas as pd
import re
import os

# Define the blacklist of unwanted sub-strings
blacklist = {
    'oligosaccharides', 'carbohydrate', 'carbohydrates', 'oligosaccharide',
    'sia', 'sialic acid', 'core saccharides', 'core saccharide', 'neuraminic acid'
}
# Convert blacklist into a regex pattern that matches whole words and accounts for possible hyphens and spaces
blacklist_regex = r'\b(?:' + '|'.join(re.escape(word) for word in blacklist) + r')\b'

# Patterns to remove entire terms containing specific Alpha/Beta expressions
alpha_beta_patterns = [
    r'\b.*?\balpha\s*\d+(-{1,3}\d+)?\s*\w*?\b',  # Adjusted to match concatenated terms
    r'\b.*?\bbeta\s*\d+(-{1,3}\d+)?\s*\w*?\b',
    r'\b\d+-deoxy-\d+-N-acetylamino(?:-[a-zA-Z]+)*\b',  # Matches '2-deoxy-2-N-acetylamino' patterns
    r'[a-zA-Z]+(?:alpha|beta)\d+-->[a-zA-Z]+\d+'  # New pattern to catch glycan-specific naming conventions
]

# Load the data from the CSV file
base_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(base_dir, '/app/gst_full/Outputs/output_predictions1.csv') 
data = pd.read_csv(output_file)

# Function to remove blacklisted sub-strings and track removed terms
def remove_terms(bert_output):
    # Convert non-string values to an empty string to prevent errors
    if not isinstance(bert_output, str) or pd.isna(bert_output):
        return "", ""  # Return empty strings if it's not a valid string

    items = bert_output.split(' | ')
    cleaned_items = []
    removed_terms = set()

    for item in items:
        original_item = item.strip()  # Preserve original item for output, strip for clean processing
        modified_item = original_item.lower()  # Convert to lowercase for case-insensitive processing

        # Apply regex for alpha/beta patterns to determine if the entire item should be removed
        matched_any_pattern = False
        for pattern in alpha_beta_patterns:
            if re.search(pattern, modified_item, flags=re.IGNORECASE):
                matched_any_pattern = True
                matches = re.findall(pattern, modified_item, flags=re.IGNORECASE)
                for match in matches:
                    removed_terms.add(original_item)  # Track removed terms
        if matched_any_pattern:
            continue  # Skip adding this item to the cleaned_items if matched

        # Remove blacklisted words using refined regex and keep original casing
        new_item, num_subs = re.subn(blacklist_regex, '', original_item, flags=re.IGNORECASE)
        if num_subs > 0:  # Check if changes were made
            removed_terms.update(set(re.findall(blacklist_regex, original_item, flags=re.IGNORECASE)))
            original_item = new_item.strip()

        if original_item:  # Ensure it's not empty
            cleaned_items.append(original_item)

    final_cleaned_output = ' | '.join(cleaned_items).strip(' | ')

    return final_cleaned_output, ' | '.join(removed_terms)

# Ensure GST_BERT column is treated as a string and replace NaN with blank values
data['GST_BERT'] = data['GST_BERT'].astype(str).replace("nan", "").fillna("")

# Apply function to clean GST_BERT column
results = data['GST_BERT'].apply(remove_terms)

# Extract cleaned values
data['BERT_Output'] = results.apply(lambda x: x[0])
data['Removed_Terms'] = results.apply(lambda x: x[1])  # Uncomment if needed

columns_to_drop = ['predicted_labels', 'GST_BERT', 'I-GST_Start', 'Removed_Terms']  # Replace with actual column names
data = data.drop(columns=columns_to_drop, errors='ignore')

# Save the updated DataFrame to a new Excel file
final_output_file = os.path.join(base_dir, '/app/gst_full/Outputs/final_gst.xlsx')
data.to_excel(final_output_file, index=False)

print(f"The data has been processed and saved successfully at {final_output_file}.")
