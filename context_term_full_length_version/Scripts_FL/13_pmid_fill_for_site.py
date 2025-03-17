import pandas as pd
import os

# File paths
base_dir = os.path.dirname(os.path.abspath(__file__))
main_excel_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/updated_final_fl_dis_spec.xlsx')
mapping_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/pmids_pmcids.xlsx')

# Load the main Excel file and the mapping file
main_df = pd.read_excel(main_excel_file)
mapping_df = pd.read_excel(mapping_file)

# Ensure column names match and are lowercase
main_df.rename(columns=lambda x: x.strip().lower(), inplace=True)
mapping_df.rename(columns=lambda x: x.strip().lower(), inplace=True)

# Ensure 'pmid' and 'pmcid' columns are strings for proper matching
main_df['pmid'] = main_df['pmid'].astype(str)
main_df['pmcid'] = main_df['pmcid'].astype(str)
mapping_df['pmid'] = mapping_df['pmid'].astype(str)
mapping_df['pmcid'] = mapping_df['pmcid'].astype(str)

# Create a dictionary for mapping pmcid -> pmid
pmcid_to_pmid_map = dict(zip(mapping_df['pmcid'], mapping_df['pmid']))

# Fill in missing pmid values in the main DataFrame
main_df['pmid'] = main_df.apply(
    lambda row: pmcid_to_pmid_map[row['pmcid']] if row['pmid'] in ['nan', 'None', ''] and row['pmcid'] in pmcid_to_pmid_map else row['pmid'],
    axis=1
)



# Clean up 'pmid' values
main_df['pmid'] = main_df['pmid'].apply(lambda x: str(x).split('.')[0] if '.' in str(x) else str(x))

# Handle invalid or missing PMIDs by replacing them with NaN
main_df['pmid'] = pd.to_numeric(main_df['pmid'], errors='coerce')

# Drop rows with NaN PMIDs if they are not needed
main_df.dropna(subset=['pmid'], inplace=True)

# Convert 'pmid' and 'sent_index' to integers for proper sorting
main_df['pmid'] = main_df['pmid'].astype(int)
main_df['sent_index'] = main_df['sent_index'].astype(int)

# Sort the DataFrame
main_df.sort_values(by=['pmid', 'section', 'sent_index'], inplace=True)

# Save the updated file
updated_file = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/after_site_fl_dis_spec.xlsx')
main_df.to_excel(updated_file, index=False)
print(f"Updated file saved to {updated_file}")
