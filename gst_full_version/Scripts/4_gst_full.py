import pandas as pd
import re
import os

# Load the Excel file
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, '/app/gst_full/Outputs/final_gst.xlsx')
data = pd.read_excel(file_path)

# Ensure necessary columns exist
required_columns = {'pmcid', 'section', 'paragraph', 'sent_index', 'sent_text', 'BERT_Output'}
missing_columns = required_columns - set(data.columns)
if missing_columns:
    raise ValueError(f"The following required columns are missing from the dataset: {missing_columns}")

# Create a grouping key based on PMCID_SECTION_Paragraph or PMCID_SECTION
data['grouping_key'] = data.apply(
    lambda row: f"{row['pmcid']}_{row['section']}_{row['paragraph']}"
    if pd.notna(row['paragraph']) else f"{row['pmcid']}_{row['section']}", axis=1
)

# Prepare HTML output with CSS styling
html_content = '''<html><head>
<style>
    .highlight { color: blue; font-weight: bold; }
    body { font-family: Arial, sans-serif; }
    h1 { text-align: center; }
    h2 { color: darkred; }
    .sentence { margin-bottom: 10px; }
</style>
</head><body>
<h1>Highlighted GST ML Predictions for Full-Length Articles</h1>'''

# Group data by the newly created grouping key
for group_key, group in data.groupby('grouping_key'):
    html_content += f'<h2>{group_key}</h2>'

    # Iterate through each sentence in this group
    for _, row in group.iterrows():
        sent_index = row['sent_index']
        sent_text = row['sent_text']
        predictions = str(row['BERT_Output']).split()  # Assuming space-separated terms

        # Sort predictions by length in descending order to ensure longer terms are highlighted first
        predictions = sorted(predictions, key=len, reverse=True)

        # Highlight each prediction in the sent_text
        for prediction in predictions:
            pattern = r'(?<!\w){}(?!\w)'.format(re.escape(prediction))
            replacement = f'<span class="highlight">{prediction}</span>'
            sent_text = re.sub(pattern, replacement, sent_text, flags=re.IGNORECASE)

        # Add formatted text to HTML output
        html_content += f'<p class="sentence"><b>Sentence {sent_index}:</b> {sent_text}</p>'

html_content += '</body></html>'

# Save the HTML content to a file
html_file_path = os.path.join(base_dir, '/app/gst_full/Outputs/Highlighted_ML_Predictions_Full.html')
with open(html_file_path, 'w') as file:
    file.write(html_content)

print(f"HTML file created successfully: {html_file_path}")
