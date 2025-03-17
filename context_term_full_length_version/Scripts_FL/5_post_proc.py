import re
import os
import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd

nltk.download('punkt')

def clean_problematic_entities(df):
    # Define the problematic patterns
    patterns = [
        r'\d+[A-Z]\),\s*\d+',    # Matches terms like "2H), 7", "1H), 4"
        r'[a-z],\s*\d+[A-Z]',    # Matches terms like "d, 2H"
        r'[A-Z]+\)\s*\d+',       # Matches terms like "Hz), 1"
        r'\d+\s*[A-Z]\s*,\s*\d+', # Matches terms like "2 H), 7"
        r'\d+\s*[A-Z]+\s*\d+'    # Matches terms like "1HNMR (CDCl3)"
    ]
    
    # Compile all the regex patterns
    combined_pattern = re.compile('|'.join(patterns))
    
    # Identify and remove rows with problematic patterns in the 'entity' column
    rows_to_remove = df[df['entity'].apply(lambda x: bool(combined_pattern.search(x)))].index
    df.drop(index=rows_to_remove, inplace=True)
    print(f"Removed {len(rows_to_remove)} rows with problematic entity patterns.")
    return df

# Custom sentence tokenizer to handle cases like 'i.e.', 'e.g.', 'fig.', etc.
def custom_sent_tokenize(text):
    # Define a tokenizer that doesn't split on "i.e.", "e.g.", etc.
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    
    # Add exceptions to the tokenizer
    abbreviations = ['i.e', 'e.g', 'fig', 'etc', 'Dr', 'Mr', 'Mrs', 'Ms']
    for abbr in abbreviations:
        if abbr not in tokenizer._params.abbrev_types:
            tokenizer._params.abbrev_types.add(abbr)
    
    return tokenizer.tokenize(text)

def extract_sentence_from_xml(pmcid, start_offset, end_offset, entity_text, xml_dir):
    # Build the path to the XML file based on the pmcid
    xml_filename = f'{pmcid}.xml'
    xml_filepath = os.path.join(xml_dir, xml_filename)

    # Check if the file exists
    if not os.path.exists(xml_filepath):
        print(f"XML file for PMCID {pmcid} not found.")
        return None

    # Parse the XML file
    tree = ET.parse(xml_filepath)
    root = tree.getroot()

    # Extract the full text content of the document
    for passage in root.iter('passage'):
        passage_text = passage.find('text').text
        passage_offset = int(passage.find('offset').text)

        # If the start_offset and end_offset fall within this passage's range
        if passage_offset <= start_offset < passage_offset + len(passage_text):
            # Calculate the relative offsets within this passage
            relative_start = start_offset - passage_offset
            relative_end = end_offset - passage_offset

            # Extract the passage that contains the entity
            entity_in_text = passage_text[relative_start:relative_end].strip()

            # Debugging: Print offsets and entity matching details
            print(f"\nDebug Info for PMCID {pmcid}:")
            print(f"Expected entity: '{entity_text}'")
            print(f"Found entity at offsets {start_offset}-{end_offset}: '{entity_in_text}'")
            print(f"Passage text: {passage_text[:60]}...")  # Print start of passage for context

            # Ensure the entity matches exactly
            if entity_in_text != entity_text.strip():
                print(f"Entity Mismatch in PMC{pmcid}: Expected '{entity_text}', Found '{entity_in_text}'")
                return None

            # Split the passage into sentences using the custom tokenizer
            sentences = custom_sent_tokenize(passage_text)

            # Find the sentence that contains the entity and confirm entity presence
            for sentence in sentences:
                if entity_text in sentence:
                    print(f"Sentence found: {sentence.strip()}")
                    return sentence.strip()

            # If no sentence is found, log the error
            print(f"Entity '{entity_text}' not found in any sentence in PMC{pmcid}.")

    print(f"Offsets {start_offset} to {end_offset} not found in XML for PMCID {pmcid}.")
    return None

def update_excel_with_sentences(excel_filepath, xml_dir, output_filepath):
    # Load the Excel file
    df = pd.read_excel(excel_filepath)

    df = clean_problematic_entities(df)

    rows_to_remove = []

    # Loop through rows where the source is PUBTATOR
    for index, row in df.iterrows():
        if row['source'] == 'PUBTATOR':  # Filter only PUBTATOR rows
            pmcid = str(row['pmcid'])  
            start_offset = row['start_offset']
            end_offset = row['end_offset']
            entity_text = row['entity']  # Assuming there's an 'entity' column with the entity text

            # Extract the sentence from the corresponding XML file
            sentence = extract_sentence_from_xml(pmcid, start_offset, end_offset, entity_text, xml_dir)
            
            # If a sentence is found and the entity is present, update it, else mark the row for removal
            if sentence and entity_text in sentence:
                df.at[index, 'sentence'] = sentence  # Update the sentence in the DataFrame
            else:
                # Mark the row for removal if entity not found in the sentence
                rows_to_remove.append(index)

    # Remove rows where the entity was not found in the sentence
    df.drop(index=rows_to_remove, inplace=True)

    # Save the updated DataFrame to a new Excel file
    df.to_excel(output_filepath, index=False)
    print(f"Updated Excel file saved to {output_filepath}, removed {len(rows_to_remove)} rows where the entity was not found in the sentence.")

# Update paths to your files

base_dir = os.path.dirname(os.path.abspath(__file__))
excel_filepath = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/fl_dis_spec_tis_cel_output.xlsx') # Update this path to your Excel file
xml_dir = os.path.join(base_dir, '/app/full_length_version/bioc_xml_fl')  # Update this path to the directory containing the XML files
output_filepath = os.path.join(base_dir, '/app/full_length_version/Outputs_FL/final_fl_dis_spec_tis_cel_output.xlsx')  # Path to save the updated Excel file

# Run the function to update the Excel with sentences and remove rows with no entity match
update_excel_with_sentences(excel_filepath, xml_dir, output_filepath)
