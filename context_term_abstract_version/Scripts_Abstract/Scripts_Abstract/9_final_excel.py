import pandas as pd
import os


base_dir = os.path.dirname(os.path.abspath(__file__))
# Load the recently updated Excel file
main_excel_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/new_dis_spec_tis_cel_output.xlsx')
main_df = pd.read_excel(main_excel_path)

# Load the reference sentences Excel file
reference_excel_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/sentences.xlsx')
reference_df = pd.read_excel(reference_excel_path)

# Identify and add missing sent_index for each pmid
new_rows = []
for pmid in reference_df['pmid'].unique():
    # Get unique sent_index for this pmid in both DataFrames
    main_sent_indices = main_df.loc[main_df['pmid'] == pmid, 'sent_index'].unique()
    ref_sent_indices = reference_df.loc[reference_df['pmid'] == pmid, 'sent_index'].unique()

    # Find missing sent_indices in the main DataFrame
    missing_indices = set(ref_sent_indices) - set(main_sent_indices)
    for index in missing_indices:
        sentence = reference_df[(reference_df['pmid'] == pmid) & (reference_df['sent_index'] == index)]['sent_text'].iloc[0]
        new_row = {
            'pmid': pmid,
            'entity': None,
            'entity_type': None,
            'start_offset': None,
            'end_offset': None,
            'source': None,
            'id': None,
            'doid_for_diseases': None,
            'uniprot_ac': None,
            'sent_index': index,
            'sentence': sentence
        }
        new_rows.append(new_row)

# Append new rows to the main DataFrame
if new_rows:
    new_df = pd.DataFrame(new_rows)
    final_df = pd.concat([main_df, new_df], ignore_index=True)
else:
    final_df = main_df

# Sort the DataFrame by pmid and then by sent_index
final_df.sort_values(by=['pmid', 'sent_index'], inplace=True)

# Save the updated DataFrame back to Excel
final_df.to_excel(main_excel_path, index=False)

print("Excel sheet has been updated successfully with missing rows added.")
