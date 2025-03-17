import pandas as pd
import os

# Load the recently updated Excel file
base_dir = os.path.dirname(os.path.abspath(__file__))
main_excel_path = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/after_site_fl_dis_spec.xlsx')
main_df = pd.read_excel(main_excel_path)

# Load the reference sentences Excel file
reference_excel_path = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/sentences.xlsx')
reference_df = pd.read_excel(reference_excel_path)

# Create a temporary 'pmcid_no_prefix' column for matching without removing 'PMC' from the original column
main_df['pmcid_no_prefix'] = main_df['pmcid'].str.replace(r'^PMC', '', regex=True).astype(str)
reference_df['pmcid_no_prefix'] = reference_df['pmcid'].astype(str)

# Ensure 'section' is treated as a string for proper matching
main_df['section'] = main_df['section'].astype(str)
reference_df['section'] = reference_df['section'].astype(str)

# Identify and add missing sent_index for each pmcid_no_prefix and section
new_rows = []
for (pmcid_no_prefix, section) in reference_df[['pmcid_no_prefix', 'section']].drop_duplicates().values:
    # Get unique sent_index for this pmcid_no_prefix and section in both DataFrames
    main_sent_indices = main_df.loc[
        (main_df['pmcid_no_prefix'] == pmcid_no_prefix) & (main_df['section'] == section), 'sent_index'
    ].unique()
    ref_sent_indices = reference_df.loc[
        (reference_df['pmcid_no_prefix'] == pmcid_no_prefix) & (reference_df['section'] == section), 'sent_index'
    ].unique()

    # Find missing sent_indices in the main DataFrame
    missing_indices = set(ref_sent_indices) - set(main_sent_indices)
    for index in missing_indices:
        sentence = reference_df[
            (reference_df['pmcid_no_prefix'] == pmcid_no_prefix) & 
            (reference_df['section'] == section) & 
            (reference_df['sent_index'] == index)
        ]['sent_text'].iloc[0]
        
        # Check if the current pmcid exists in the main DataFrame
        matching_rows = main_df.loc[main_df['pmcid_no_prefix'] == pmcid_no_prefix]
        if not matching_rows.empty:
            pmcid = matching_rows['pmcid'].iloc[0]  # Retain the original pmcid
        else:
            pmcid = f"PMC{pmcid_no_prefix}"  # Use a default or reconstructed value if missing
        
        new_row = {
            'pmcid': pmcid,
            'section': section,
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

# Sort the DataFrame to retain the original order of main file rows and append new rows
final_df['original_order'] = final_df.index
final_df['is_new'] = final_df['entity'].isna()  # Mark new rows for sorting

# First, sort by original order for existing rows, then append new rows
final_df.sort_values(by=['is_new', 'original_order', 'pmcid', 'section', 'sent_index'], inplace=True)

# Drop helper columns used for sorting and matching
final_df.drop(columns=['original_order', 'is_new', 'pmcid_no_prefix'], inplace=True)



# Save the updated DataFrame to a new Excel file
new_excel_path = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/14_fl_dis_spec_with_missing_rows.xlsx')
final_df.to_excel(new_excel_path, index=False)

print(f"Excel sheet has been updated successfully with missing rows added and saved to: {new_excel_path}")

mapping_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/pmids_pmcids.xlsx')
# Load the main Excel file and the mapping file
main_df2 = pd.read_excel(new_excel_path)
mapping_df = pd.read_excel(mapping_file)

# Ensure column names match and are lowercase
main_df2.rename(columns=lambda x: x.strip().lower(), inplace=True)
mapping_df.rename(columns=lambda x: x.strip().lower(), inplace=True)

# Ensure 'pmid' and 'pmcid' columns are strings for proper matching
main_df2['pmid'] = main_df2['pmid'].astype(str)
main_df2['pmcid'] = main_df2['pmcid'].astype(str)
mapping_df['pmid'] = mapping_df['pmid'].astype(str)
mapping_df['pmcid'] = mapping_df['pmcid'].astype(str)

# Create a dictionary for mapping pmcid -> pmid
pmcid_to_pmid_map = dict(zip(mapping_df['pmcid'], mapping_df['pmid']))

# Fill in missing pmid values in the main DataFrame
main_df2['pmid'] = main_df2.apply(
    lambda row: pmcid_to_pmid_map[row['pmcid']] if row['pmid'] == 'nan' and row['pmcid'] in pmcid_to_pmid_map else row['pmid'],
    axis=1
)

# Clean up 'pmid' values
main_df2['pmid'] = main_df2['pmid'].apply(lambda x: str(x).split('.')[0] if '.' in str(x) else str(x))

# Convert 'pmid' to numeric, setting invalid entries to NaN
main_df2['pmid'] = pd.to_numeric(main_df2['pmid'], errors='coerce')

# Handle missing or invalid PMIDs (e.g., drop rows or fill with a default value)
main_df2.dropna(subset=['pmid'], inplace=True)  # Drop rows with NaN PMIDs
# Alternatively, you can replace NaN PMIDs with a default value, e.g., 0
# main_df2['pmid'].fillna(0, inplace=True)

# Convert 'pmid' and 'sent_index' to integers for proper sorting
main_df2['pmid'] = main_df2['pmid'].astype(int)
main_df2['sent_index'] = main_df2['sent_index'].astype(int)

# Sort the DataFrame
main_df2.sort_values(by=['pmid', 'section', 'sent_index'], inplace=True)


# Save the updated file
updated_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/14_fl_dis_spec_with_missing_rows.xlsx')
main_df2.to_excel(updated_file, index=False)
print(f"Updated file saved to {updated_file}")
