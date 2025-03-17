import os
import pandas as pd
import regex as re

# Define entity colors
entity_colors = {
    'Disease': '#FF0000',
    'Species': '#f83f93',
    'Tissue': '#17e8cf',
    'Cellline': '#800080',
    'Gene': '#0000FF',
    'Site': '#FFA500'  # Added Site entity
}

base_dir = os.path.dirname(os.path.abspath(__file__))

# Load the data from the Excel file
file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/1_new_dis_spec_tis_cel_output.xlsx')
data = pd.read_excel(file_path)

# Initialize the HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Context Term Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
        }
        .legend {
            display: flex;
            justify-content: flex-start;
            margin-bottom: 20px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-right: 20px;
        }
        .legend-color {
            display: inline-block;
            width: 15px;
            height: 15px;
            margin-right: 5px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
<h1>Context Term Detection</h1>

<div class="legend">
"""

# Add horizontal legend items for each entity type and color
for entity_type, color in entity_colors.items():
    html_content += f"""
    <div class="legend-item">
        <span class="legend-color" style="background-color:{color}"></span>{entity_type}
    </div>
    """

html_content += "</div>\n"

# Process each group by PMID
for pmid, group in data.groupby('pmid'):
    html_content += f"<h2>PMID: {pmid}</h2>\n"
    sentences_by_index = group.groupby('sent_index')

    # Process each sentence within the PMID
    for sent_index, sentence_group in sentences_by_index:
        sentence = sentence_group.iloc[0]['sentence']  # Get the base sentence
        entities = sentence_group.sort_values('start_offset', ascending=False)  # Reverse order to avoid offset issues

        # Highlight entities in the sentence
        for _, row in entities.iterrows():
            entity = row['entity']
            entity_type = row['entity_type']
            color = entity_colors.get(entity_type, 'black')  # Default to black if type is not found

            if pd.notna(entity):
                # Replace the first occurrence of the entity in the sentence with a colored span
                sentence = sentence.replace(
                    entity, f'<span style="color:{color}">{entity}</span>', 1
                )

        # Add the formatted sentence to the HTML content
        html_content += f"<p><b>{sent_index}.</b> {sentence}</p>\n"

# Close the HTML body
html_content += """
</body>
</html>
"""

# Write the HTML content to a file
output_html_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/highlighted_entities.html')
with open(output_html_path, "w") as html_file:
    html_file.write(html_content)

print(f"HTML file created successfully at: {output_html_path}")
