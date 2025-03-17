import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# Load the Excel file
file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/new_dis_spec_tis_cel_output.xlsx')
data = pd.read_excel(file_path)

# Function to filter out nested entities
def remove_nested_entities(data):
    removed_rows = []

    # Sort the data by pmid, sent_index, start_offset, and end_offset for proper processing
    data = data.sort_values(by=['pmid', 'sent_index', 'start_offset', 'end_offset'], ascending=[True, True, True, False])

    # Iterate through each group of sentences
    filtered_indices = set()
    for (pmid, sent_index), group in data.groupby(['pmid', 'sent_index']):
        active_ranges = []
        for index, row in group.iterrows():
            start, end = row['start_offset'], row['end_offset']
            # Check if the current range is fully contained in an existing range
            if any(start >= r[0] and end <= r[1] for r in active_ranges):
                removed_rows.append(row)
            else:
                active_ranges.append((start, end))
                filtered_indices.add(index)

    # Filter the data to keep only non-nested entities
    filtered_data = data[data.index.isin(filtered_indices)]

    return filtered_data, removed_rows

# Apply the function
filtered_data, removed_rows = remove_nested_entities(data)

# Save the filtered data to a new file
filtered_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/1_new_dis_spec_tis_cel_output.xlsx')
filtered_data.to_excel(filtered_file_path, index=False)

# Save the removed rows to another file
removed_rows_df = pd.DataFrame(removed_rows)
removed_rows_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/removed_entities.xlsx')
removed_rows_df.to_excel(removed_rows_file_path, index=False)

print(f"Filtered entities saved to: {filtered_file_path}")
print(f"Removed entities saved to: {removed_rows_file_path}")
