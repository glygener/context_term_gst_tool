import pandas as pd
from rapidfuzz import fuzz, process
import os

# Load the files
base_dir = os.path.dirname(os.path.abspath(__file__))
final_fl_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/final_fl_dis_spec_tis_cel_output.xlsx')
sentences_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/sentences.xlsx')

final_fl_df = pd.read_excel(final_fl_file)
sentences_df = pd.read_excel(sentences_file)

# Ensure column names match
final_fl_df.rename(columns=lambda x: x.strip().lower(), inplace=True)
sentences_df.rename(columns=lambda x: x.strip().lower(), inplace=True)

# Convert 'pmcid' and 'section' columns to string in both dataframes
final_fl_df['pmcid'] = final_fl_df['pmcid'].astype(str)
sentences_df['pmcid'] = sentences_df['pmcid'].astype(str)

final_fl_df['section'] = final_fl_df['section'].astype(str)
sentences_df['section'] = sentences_df['section'].astype(str)

# Merge the files based on 'pmcid' and 'section'
merged_df = final_fl_df.merge(sentences_df, on=['pmcid', 'section'], how='left')

# Handle duplicate 'pmid' columns after the merge
if 'pmid_x' in merged_df.columns and 'pmid_y' in merged_df.columns:
    # Keep the 'pmid' from the left dataframe
    merged_df['pmid'] = merged_df['pmid_x']
    # Drop the unnecessary 'pmid_x' and 'pmid_y' columns
    merged_df.drop(columns=['pmid_x', 'pmid_y'], inplace=True)

# Initialize the new columns
merged_df['probability'] = -1.0
merged_df['sent_index'] = -1
merged_df['matched_sentence'] = None

# Function to match sentences with fuzzy matching
def match_sentences(row, sent_texts):
    sentence = row['sentence']
    if pd.notna(sentence):
        # Find the best match
        match = process.extractOne(sentence, sent_texts, scorer=fuzz.ratio)
        if match:
            # Get the probability and matched sentence
            prob = match[1]
            matched_sent = match[0]
            if prob >= 70:  # Only return index and matched sentence if probability >= 70
                sent_index = sentences_df[sentences_df['sent_text'] == matched_sent]['sent_index'].values[0]
                return prob, sent_index, matched_sent
            else:
                return prob, -1, None
    return -1, -1, None  # Default for no match or invalid sentence

# Use 'sent_text' column from sentences_df for matching
sent_texts_list = sentences_df['sent_text'].tolist()

# Apply the matching function row-wise
results = merged_df.apply(lambda row: match_sentences(row, sent_texts_list), axis=1)

# Assign results back to DataFrame
merged_df['probability'] = results.apply(lambda x: x[0])  # Always assign probability
merged_df['sent_index'] = results.apply(lambda x: x[1])  # Assign index if match is >= 70, else -1
merged_df['matched_sentence'] = results.apply(lambda x: x[2])  # Assign matched sentence if match is >= 70

# Replace the sentence column in final_fl_df with the matched sentence if there’s a match
merged_df['sentence'] = merged_df.apply(
    lambda row: row['matched_sentence'] if pd.notna(row['matched_sentence']) else row['sentence'],
    axis=1
)

# Drop unnecessary columns
columns_to_drop = ['sent_text', 'paragraph', 'pmid_y', 'charstart', 'charend', 'matched_sentence']  # List all columns you don't want


merged_df = merged_df.drop(columns=[col for col in columns_to_drop if col in merged_df.columns], errors='ignore')

column_order = ['pmid', 'pmcid', 'entity', 'entity_type', 'start_offset', 'end_offset', 'source', 'id', 'doid_for_diseases', 'uniprot_ac', 'sent_index', 'sentence', 'section', 'probability']
merged_df = merged_df[column_order] 

# Save the updated file
output_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/updated_final_fl_dis_spec.xlsx')
merged_df.to_excel(output_file, index=False)
print(f"Updated file saved to {output_file}")
