import pickle
import pandas as pd

# Load data from pickle file
with open('/usa/shovan/Glygen/mesh_to_doid/Files/name_to_doid.pk', 'rb') as file:
    data_dict = pickle.load(file)

# Ensure the data is a dictionary
if isinstance(data_dict, dict):
    # Convert dictionary to DataFrame
    data_df = pd.DataFrame(list(data_dict.items()), columns=['Identifier', 'Disease'])

    # Save to CSV
    data_df.to_csv('/usa/shovan/Glygen/mesh_to_doid/Output/output_file2.csv', index=False, encoding='utf-8')
else:
    print("Data is not in dictionary format.")
