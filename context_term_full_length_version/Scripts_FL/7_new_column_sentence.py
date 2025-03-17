import pandas as pd
import os

# Load the Excel file
base_dir = os.path.dirname(os.path.abspath(__file__))
sentence_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/sentences.xlsx')
sentence_df = pd.read_excel(sentence_file)

# Ensure the 'pmcid' column is treated as strings
sentence_df['pmcid'] = sentence_df['pmcid'].astype(str)

# Remove the "PMC" prefix from the 'pmcid' column
sentence_df['pmcid'] = sentence_df['pmcid'].str.replace(r'^PMC', '', regex=True)

# Create the 'pmid' column based on the presence of the 'paragraph' column
if 'paragraph' in sentence_df.columns:
    sentence_df['pmid'] = sentence_df.apply(
        lambda row: f"{row['pmcid']}_{row['section']}_{row['paragraph']}" 
        if pd.notna(row['paragraph']) and row['paragraph'] != '' 
        else f"{row['pmcid']}_{row['section']}", 
        axis=1
    )
else:
    # If 'paragraph' column is missing, use only 'pmcid_section'
    sentence_df['pmid'] = sentence_df['pmcid'] + "_" + sentence_df['section']

# Save the updated file
sentence_df.to_excel(sentence_file, index=False)

print("File updated successfully!")
