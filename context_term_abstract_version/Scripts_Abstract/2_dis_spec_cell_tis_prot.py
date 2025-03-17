import os
import xml.etree.ElementTree as ET
import pandas as pd
import re
import csv
from Bio import Entrez
import time
from oger.ctrl.router import Router, PipelineServer

# Set your email
Entrez.email = "shovan@udel.edu"  # Replace with your email

# Function to fetch UniProt IDs for a specific GeneID
def fetch_uniprot_ids(gene_id, max_retries=3, wait_time=2):
    """
    Fetch UniProt IDs for a given GeneID from Entrez, with retries on failure.

    Args:
        gene_id (str): The NCBI GeneID to fetch data for.
        max_retries (int): Maximum number of retries for failed requests.
        wait_time (int): Initial wait time between retries in seconds.

    Returns:
        str: A string containing merged UniProt IDs separated by "|".
    """
    retries = 0
    while retries < max_retries:
        try:
            # Fetch Gene data from Entrez
            handle = Entrez.efetch(db="gene", id=gene_id, rettype="xml")
            raw_data = handle.read()

            # Parse the XML response
            root = ET.fromstring(raw_data)

            # Collect UniProt IDs
            uniprot_ids = set()  # Use a set to avoid duplicates
            for dbxref in root.findall(".//Dbtag"):
                db = dbxref.find("./Dbtag_db")
                if db is not None and db.text == "UniProtKB/Swiss-Prot":
                    uniprot_id = dbxref.find("./Dbtag_tag/Object-id/Object-id_str")
                    if uniprot_id is not None:
                        print(f"Found UniProt ID: {uniprot_id.text} for {gene_id}")
                        uniprot_ids.add(uniprot_id.text)

            # Merge IDs into a single string separated by "|"
            return "| ".join(uniprot_ids)

        except ET.ParseError as e:
            print(f"XML Parsing Error for GeneID {gene_id}: {e}")
            return ""
        except Exception as e:
            retries += 1
            print(f"Error fetching UniProt IDs for GeneID {gene_id}: {e}")
            if retries < max_retries:
                print(f"Retrying ({retries}/{max_retries}) in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            else:
                print(f"Max retries reached for GeneID {gene_id}. Returning empty string.")
                return ""

base_dir = os.path.dirname(os.path.abspath(__file__))

input_dir = os.path.join(base_dir, '/app/abstract_version/abstract_xml')
output_text_dir = os.path.join(base_dir, '/app/abstract_version/abstract_text')
excel_output_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/dis_spec_tis_cel_output.xlsx')

# Define the paths
#input_dir = "/home/shovan/nlputils/EDG_framework/context_term_new/biocxml_pubtator"
#output_text_dir = "/home/shovan/nlputils/EDG_framework/context_term_new/abstract_text"
#excel_output_path = "/home/shovan/nlputils/EDG_framework/context_term_new/Outputs/dis_spec_tis_cel_output_19thDec.xlsx"
#excel_sentences = "/home/shovan/nlputils/EDG_framework/context_term_new/Outputs/sentences.xlsx"
# Initialize a list to store sentence data
sentences_data = []
# Create the output directory if it doesn't exist
if not os.path.exists(output_text_dir):
    os.makedirs(output_text_dir)

# Initialize a list to store annotation data for the Excel file
annotations_data = []

# Blacklist for PubTator entities
blacklist_pubtator = [
    r'oil(s)?', r'toxi(c|city|cities)?', r'htert', r'hpv-c33a', r'hpv-', r'c57bl/6j', r'nmri-foxn1nu', r'tum(or|ors|our|ours)', r'malignanc(y|ies)', r'necros(is|es)', r'metastas(is|es)', r'failure(s)?', r'death(s)?', r'myocardial(s)?', r'fungal(s)?', r'prostate(s)?', r'kidney(s)?', r'bladder(s)?'
    ]


def get_sentence(text, start_offset, end_offset):
    """
    Extract the sentence containing the entity based on start and end offsets,
    carefully handling abbreviations and valid sentence boundaries.
    """
    # Define common abbreviations that should not end sentences
    abbreviations = {'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'St.', 'Jr.', 'e.g.', 'i.e.', 'cf.', 'vs.', 'Vs.' 'etc.', 'fig.', 'figs.', 'Figs.', 'Tab.', 'tab.', 'Table.'}
    i = 0
    sentence_start = 0
    sentence_end = len(text)

    # Iterate over each character in the text
    while i < len(text) - 1:
        # Check if the current character is a period
        if text[i] == '.':
            # Look ahead to check if the next characters qualify this as a sentence end
            if i + 1 < len(text) and text[i + 1] == ' ':
                if i + 2 < len(text) and text[i + 2].isupper():
                    # Check if the text leading to the period is an abbreviation
                    possible_abbreviation = text[max(0, i - 5):i + 1].strip()
                    if not any(possible_abbreviation.endswith(abbrev) for abbrev in abbreviations):
                        # Consider this as a sentence end
                        if i >= end_offset:
                            sentence_end = i + 1
                            break
                        elif i < start_offset:
                            sentence_start = i + 2
            elif i + 1 < len(text) and text[i + 1].islower():
                # Handle cases where a period is part of "A." but not a sentence end
                i += 1
                continue
        i += 1

    # Return the sentence containing the entity
    return text[sentence_start:sentence_end].strip()





def filter_blacklisted_entities(entities, blacklist):
    """
    Excludes entities that are in the blacklist or match the blacklist patterns.
    """
    filtered_entities = []
    for entity in entities:
        entity_text = entity['entity'].lower()
        if any(re.fullmatch(pattern, entity_text) for pattern in blacklist):
            continue
        filtered_entities.append(entity)
    return filtered_entities

def filter_entities_with_blacklisted_endings(entities, blacklist):
    """
    Excludes entities if the last term or the ending part matches any blacklisted terms.
    """
    filtered_entities = []
    for entity in entities:
        entity_text = entity['entity'].lower()
        entity_terms = entity_text.split()
        last_term = entity_terms[-1]
        if any(re.fullmatch(pattern, last_term) for pattern in blacklist):
            continue
        if any(entity_text.endswith(re.sub(r'\(.*\)', '', pattern)) for pattern in blacklist):
            continue
        filtered_entities.append(entity)
    return filtered_entities

# Step 1: Process PubTator XML files
for filename in os.listdir(input_dir):
    if filename.endswith('.xml'):
        file_path = os.path.join(input_dir, filename)
        
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Initialize variables to store the title and abstract text
        title_text = ""
        abstract_text = ""
        
        # Extract the PMID
        pmid_elem = root.find('.//document/id')
        pmid = pmid_elem.text if pmid_elem is not None else "Unknown_PMID"
        
        # Extract title and abstract text
        for passage in root.findall('.//passage'):
            passage_type_elem = passage.find('infon[@key="type"]')
            passage_type = passage_type_elem.text if passage_type_elem is not None else ""
            if passage_type == 'title':
                title_text = passage.find('text').text if passage.find('text') is not None else ""
            elif passage_type == 'abstract':
                abstract_text = passage.find('text').text if passage.find('text') is not None else ""
        
        # Concatenate the title and abstract text
        concatenated_text = title_text + " " + abstract_text
        
        # Save the concatenated text to a file
        output_text_file = os.path.join(output_text_dir, f"{pmid}.txt")
        with open(output_text_file, 'w') as text_file:
            text_file.write(concatenated_text)
        
        # Extract annotation information
        for annotation in root.findall('.//annotation'):
            entity = annotation.find('text').text if annotation.find('text') is not None else ""
            entity_type_elem = annotation.find('infon[@key="type"]')
            entity_type = entity_type_elem.text if entity_type_elem is not None else ""
            identifier_elem = annotation.find('infon[@key="identifier"]')
            identifier = identifier_elem.text if identifier_elem is not None else ""
            location_elem = annotation.find('location')
            start_offset = int(location_elem.get('offset')) if location_elem is not None else ""
            end_offset = start_offset + len(entity) if start_offset != "" else ""
            
            if entity_type.lower() in ['disease', 'species', 'cellline', 'gene']:
                sentence = get_sentence(concatenated_text, start_offset, end_offset)
                annotations_data.append({
                    'pmid': pmid,
                    'entity': entity,
                    'entity_type': entity_type.capitalize(),
                    'source': 'PUBTATOR',
                    'id': identifier,
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                    'sentence': sentence
                })

# Filter out blacklisted entities from PubTator data
annotations_data = filter_blacklisted_entities(annotations_data, blacklist_pubtator)
annotations_data = filter_entities_with_blacklisted_endings(annotations_data, blacklist_pubtator)

def custom_parse_doid_string(doid_str):
    try:
        # Remove curly braces and split by comma
        doid_str = doid_str.strip("{}")
        doid_pairs = doid_str.split(", ")

        # Construct a list from the split values
        doid_list = []
        for pair in doid_pairs:
            if ":" in pair:
                key, value = pair.split(":")
                doid_list.append(value.strip())
        
        return doid_list
    except Exception as e:
        print("Failed to parse:", doid_str, "Error:", e)
        return []

def load_mesh_to_doid_mapping(filename):
    mesh_to_doid = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            mesh_id = row[0]
            doid_dict_str = row[1]
            #print("Read from CSV:", mesh_id, doid_dict_str)  # Debugging line
            doid_list = custom_parse_doid_string(doid_dict_str)
            mesh_to_doid[mesh_id] = doid_list
    return mesh_to_doid

# Function to map mesh_id to doid using the loaded mapping
def map_mesh_to_doid(mesh_id):
    standardized_mesh_id = "MESH:" + mesh_id if not mesh_id.startswith("MESH:") else mesh_id
    doid_list = mesh_to_doid_mapping.get(standardized_mesh_id, None)
    if doid_list is None:
        return 'Not found'  # or any other default value you prefer
    else:
        return '|'.join(['DOID:' + doid for doid in doid_list])

# Step 2: Load existing annotations and create a set of already processed annotations
annotations_df = pd.DataFrame(annotations_data)
processed_entities = set(annotations_df.apply(lambda row: (row['pmid'], row['entity'], row['start_offset'], row['end_offset']), axis=1))

# Configuration for the Router
#conf_cellline = Router(termlist_path=os.path.join(base_dir, '/app/OGER/oger/test/testfiles/cell_line.tsv'))
#conf_tissue = Router(termlist_path="/home/shovan/nlputils/EDG_framework/context_term_new/OGER/oger/test/testfiles/tissue.tsv")
#mesh_to_doid_mapping = load_mesh_to_doid_mapping("/home/shovan/nlputils/EDG_framework/context_term_new/mesh_to_doid/Output/mesh_to_doid.csv")

conf_tissue = Router(termlist_path=os.path.join(base_dir, '/app/OGER/oger/test/testfiles/tissue.tsv'))
mesh_to_doid_mapping = load_mesh_to_doid_mapping(os.path.join(base_dir, '/app/mesh_to_doid/Output/mesh_to_doid.csv'))

# Initialize the PipelineServer with the configuration
#pl_cellline = PipelineServer(conf_cellline)
pl_tissue = PipelineServer(conf_tissue)

# Blacklist of words to be excluded from entities for tissue with patterns for plurals
blacklist_tissue_patterns = [
    r'adult(s)?', r'animal(s)?', r'ax(is|es)', r'oil(s)?', r'medi(a|um)', r'back', r'secretion(s)?', r'cell\s*culture(s)?', 
    r'immune\s*system(s)?', r'root(s)?', r'needle(s)?', r'tissue\s*culture(s)?', r'stem(s)?', r'white-matter(s)?', 
    r'cardiovascular\s*system(s)?', r'fiber(s)?', r'tum(or|ors|our|ours)', r'node(s)?', r'scale(s)?' r'fibroblast(s)?', r'bud(s)?', 
    r'tract(s)?', r'brain(s)?', r'plant(s)?', r'milk(s)?', r'fruit(s)?', r'seed(s)?', r'colostrum', r'scale(s)?', r'\S*culture(s)?',
    r'bone(s)?', r'tail(s)?', r'biofilm(s)?', r'eye(s)?', r'tear(s)?', r'fungi', r'culture supernatant'
]

# Additional function to exclude patterns like 'P=.001' or 'n = 14'
def filter_letter_equal_numeric_patterns(entities):
    pattern = re.compile(r'^[a-zA-Z]\s*=\s*(\d+(\.\d+)?|\.\d+)$')
    return [entity for entity in entities if not pattern.match(entity[0])]

def filter_specific_patterns(entities):
    # Pattern to detect 'a 33' type entities
    letter_numeric_pattern = re.compile(r'^[a-zA-Z]\s+\d+$')
    # Pattern to detect '1 h' type entities
    numeric_unit_pattern = re.compile(r'^\d+\s+[a-zA-Z]$')

    filtered_entities = []
    for entity in entities:
        entity_text = entity[0]
        
        # Check for 'a 33' type patterns and exclude them
        if letter_numeric_pattern.match(entity_text):
            continue  # Skip this entity
        
        # Check for '1 h' type patterns and exclude them
        if numeric_unit_pattern.match(entity_text):
            continue  # Skip this entity
        
        filtered_entities.append(entity)
    
    return filtered_entities

def filter_blacklisted_entities_for_oger(entities, blacklist):
    """
    Excludes entities that are in the blacklist or match the blacklist patterns.
    """
    filtered_entities = []
    for entity in entities:
        entity_text = entity[0].lower()
        if any(re.fullmatch(pattern, entity_text) for pattern in blacklist):
            continue
        filtered_entities.append(entity)
    return filtered_entities

def filter_entities_with_blacklisted_endings_for_oger(entities, blacklist):
    """
    Excludes entities if the last term or the ending part matches any blacklisted terms.
    """
    filtered_entities = []
    for entity in entities:
        entity_text = entity[0].lower()
        entity_terms = entity_text.split()
        last_term = entity_terms[-1]
        if any(re.fullmatch(pattern, last_term) for pattern in blacklist):
            continue
        if any(entity_text.endswith(re.sub(r'\(.*\)', '', pattern)) for pattern in blacklist):
            continue
        filtered_entities.append(entity)
    return filtered_entities

def is_whole_word_match(text, start, end):
    """
    Enhanced check for ensuring an entity is a whole word within the text.
    Checks the characters immediately before and after the entity's span.
    """
    # Check character before start, if it exists and is alphanumeric or '-', not a whole word
    if start > 0 and (text[start-1].isalnum() or text[start-1] == '-'):
        return False

    # Check character after end, if it exists and is alphanumeric or '-', not a whole word
    if end < len(text) and (text[end].isalnum() or text[end] == '-'):
        return False

    return True

def filter_overlapping_entities(entities):
    """
    Removes overlapping entities, keeping the longest match for each overlapping set.
    """
    entities.sort(key=lambda x: (x[1], -(x[2] - x[1])))
    filtered_entities = []
    last_end = -1
    for entity in entities:
        _, start, end, _ = entity
        if start > last_end:
            filtered_entities.append(entity)
            last_end = end
    return filtered_entities

def filter_single_letters_digits(entities):
    """
    Excludes entities that are single letters or digits.
    """
    return [entity for entity in entities if not (len(entity[0]) == 1 and entity[0].isalnum())]

def process_document(file_path, pmid, pl, blacklist):
    """
    Processes a single document: loads, matches entities, applies filtering.
    """
    coll = pl.load_one(file_path, 'txt')
    pl.process(coll)
    entities = []

    with open(file_path, 'r') as file:
        full_text = file.read()

        for doc in coll:
            for section in doc:
                for entity in section.iter_entities():
                    if len(entity.info) >= 4:
                        # Perform a stricter check for whole word matches
                        if is_whole_word_match(full_text, entity.start, entity.end):
                            info_parts = (entity.info[0], entity.info[2], entity.info[3], entity.info[1])
                            entities.append((entity.text, entity.start, entity.end, info_parts))

    # Apply filtering steps
    filtered_entities = filter_overlapping_entities(entities)
    filtered_entities = filter_single_letters_digits(filtered_entities)
    filtered_entities = filter_blacklisted_entities_for_oger(filtered_entities, blacklist)
    filtered_entities = filter_entities_with_blacklisted_endings_for_oger(filtered_entities, blacklist)
    filtered_entities = filter_letter_equal_numeric_patterns(filtered_entities)
    filtered_entities = filter_specific_patterns(filtered_entities)

    # Define patterns to match cell-related terms and their plurals
    cell_related_patterns = [
        r'cell(s)?', r'cell\s*line(s)?', r'cellline(s)?'
    ]

    # Exclude already processed entities and those ending with cell-related terms
    filtered_entities = [
        entity for entity in filtered_entities 
        if (pmid, entity[0], entity[1], entity[2]) not in processed_entities 
        and not any(re.search(pattern + r'$', entity[0].lower()) for pattern in cell_related_patterns)
    ]

    return filtered_entities

# Process each text file for Tissue
for pmid_file in os.listdir(output_text_dir):
    if pmid_file.endswith('.txt'):
        pmid = pmid_file.split('.')[0]
        file_path = os.path.join(output_text_dir, pmid_file)
        entities = process_document(file_path, pmid, pl_tissue, blacklist_tissue_patterns)
        for entity_text, entity_start, entity_end, info_parts in entities:
            with open(file_path, 'r') as file:
                full_text = file.read()
            sentence = get_sentence(full_text, entity_start, entity_end)
            annotations_data.append({
                'pmid': pmid,
                'entity': entity_text,
                'entity_type': 'Tissue',
                'source': 'BRENDA',
                'id': info_parts[2],
                'start_offset': entity_start,
                'end_offset': entity_end,
                'sentence': sentence
            })

# Update the DataFrame with new annotations
annotations_df = pd.DataFrame(annotations_data)
annotations_df['doid_for_diseases'] = annotations_df.apply(lambda row: map_mesh_to_doid(row['id']) if row['entity_type'].lower() == 'disease' else '', axis=1)
annotations_df['uniprot_AC'] = annotations_df.apply(lambda row: fetch_uniprot_ids(row['id']) if row['entity_type'].lower() == 'gene' else '', axis=1)

# Define a list of words to keep even if DOID is not found
words_to_keep = ['cardiac hypertrophy']

# Filter out rows where DOID is not found, except for the words to keep
annotations_df = annotations_df[
    (annotations_df['doid_for_diseases'] != 'Not found') | 
    (annotations_df['entity'].str.lower().isin(words_to_keep))
]

# Sort the DataFrame by PMID and by start_offset and end_offset to ensure sequential output
annotations_df.sort_values(by=['pmid', 'start_offset', 'end_offset'], inplace=True)

# Save the updated DataFrame to the Excel file
annotations_df.to_excel(excel_output_path, index=False)

print("Process completed successfully.")
