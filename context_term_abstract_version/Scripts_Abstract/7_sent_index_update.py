import pandas as pd
from difflib import SequenceMatcher
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# Load Excel files
dis_spec_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/dis_spec_tis_cel_output.xlsx')
sentences_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/sentences.xlsx')
output_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/new_dis_spec_tis_cel_output.xlsx')

dis_spec_df = pd.read_excel(dis_spec_file_path)
sentences_df = pd.read_excel(sentences_file_path)

# Ensure columns are lowercase for consistency
dis_spec_df.columns = dis_spec_df.columns.str.lower()
sentences_df.columns = sentences_df.columns.str.lower()

# Add a new column for sent_index
dis_spec_df['sent_index'] = -1  # Default to -1 if no match found

# Function to check similarity
def is_similar(sent1, sent2, threshold=0.95):
    ratio = SequenceMatcher(None, str(sent1).strip(), str(sent2).strip()).ratio()
    return ratio >= threshold, ratio

# Match sentences and update
for i, dis_row in dis_spec_df.iterrows():
    pmid = str(dis_row['pmid'])
    sentence_from_dis = str(dis_row['sentence']).strip()

    matching_sentences = sentences_df[sentences_df['pmid'].astype(str) == pmid]

    best_match = None
    best_ratio = 0
    best_index = -1

    for _, sent_row in matching_sentences.iterrows():
        sentence_from_sentences = str(sent_row['sent_text']).strip()
        match, ratio = is_similar(sentence_from_dis, sentence_from_sentences)
        
        if match and ratio > best_ratio:
            best_match = sentence_from_sentences
            best_index = sent_row['sent_index']
            best_ratio = ratio

    # Update if a good match is found
    if best_index != -1:
        dis_spec_df.at[i, 'sent_index'] = best_index
        dis_spec_df.at[i, 'sentence'] = best_match
        print(f"Updated row {i}: PMID {pmid} with sent_index {best_index} and sentence: {best_match}")

# Save the updated Excel file
dis_spec_df.to_excel(output_file_path, index=False)
print(f"Updated file saved to {output_file_path}")
