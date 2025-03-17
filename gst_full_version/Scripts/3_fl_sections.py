import os
import re
import xml.etree.ElementTree as ET

# Define the input and output directories
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, '/app/gst_full/bioc_xml_fl')
output_xml_dir = os.path.join(base_dir, '/app/gst_full/output_xml_section_FL')
output_text_dir = os.path.join(base_dir, '/app/gst_full/output_text_section_FL')
os.makedirs(output_xml_dir, exist_ok=True)
os.makedirs(output_text_dir, exist_ok=True)

# Function to create a new XML file for each section
def create_section_file(passages, annotations, doc_id, section_name, output_dir):
    collection = ET.Element('collection')
    source = ET.SubElement(collection, 'source')
    source.text = 'BioC-API'
    date = ET.SubElement(collection, 'date')
    key = ET.SubElement(collection, 'key')
    key.text = 'BioC.key'
    document = ET.SubElement(collection, 'document')
    id_elem = ET.SubElement(document, 'id')
    id_elem.text = doc_id
    pmcid_elem = ET.SubElement(document, 'pmcid')
    pmcid_elem.text = doc_id
    
    # Add passages to the document
    for passage in passages:
        new_passage = ET.SubElement(document, 'passage')
        for child in passage:
            new_passage.append(child)
    
    # Add annotations to the document
    for annotation in annotations:
        document.append(annotation)
    
    # Convert the ElementTree to a string
    tree = ET.ElementTree(collection)
    xml_str = ET.tostring(collection, encoding='unicode', method='xml')
    
    # Manually add DOCTYPE declaration
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE collection SYSTEM "BioC.dtd">\n' + xml_str
    
    # Create the filename
    section_name = section_name.replace(' ', '_').upper()
    output_file = os.path.join(output_dir, f'{doc_id}_{section_name}.xml')
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)

# Function to create text files for sections other than ABSTRACT
def create_text_files_for_section(doc_id, section_name, subsections, output_dir):
    section_name = section_name.replace(' ', '_').upper()
    i = 1
    merged_subsections = []
    current_title = ""
    for title, content in subsections:
        if content.strip():
            if current_title:
                merged_subsections.append((current_title.strip(), content))
                current_title = ""
            else:
                merged_subsections.append((title, content))
        else:
            current_title += title + " "
    for title, content in merged_subsections:
        output_file = os.path.join(output_dir, f'{doc_id}_{section_name}_Paragraph{i}.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f'{title}. ')
            f.write(f'{content} ')
        i += 1

# Function to create a single text file for the ABSTRACT section
def create_abstract_text_file(doc_id, section_name, title, subsections, output_dir):
    section_name = section_name.replace(' ', '_').upper()
    output_file = os.path.join(output_dir, f'{doc_id}_{section_name}.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'{title}. ')
        for i, content in enumerate(subsections):
            f.write(f'{content} ')

# Function to post-process and merge TITLE files with the next paragraph files
def post_process_title_files(output_text_dir):
    for filename in os.listdir(output_text_dir):
        if re.match(r'.*_TITLE_.*\.txt', filename):
            title_file_path = os.path.join(output_text_dir, filename)
            pmcid, section, _ = filename.split('_', 2)
            next_paragraph_file = None
            
            # Find the next paragraph file
            for next_filename in os.listdir(output_text_dir):
                if re.match(rf'{pmcid}_{section}_Paragraph\d+\.txt', next_filename):
                    if next_filename > filename:
                        next_paragraph_file = next_filename
                        break
            
            # If a next paragraph file is found, merge the content
            if next_paragraph_file:
                next_paragraph_file_path = os.path.join(output_text_dir, next_paragraph_file)
                with open(title_file_path, 'r', encoding='utf-8') as title_file, open(next_paragraph_file_path, 'a', encoding='utf-8') as paragraph_file:
                    paragraph_file.write(title_file.read())
                os.remove(title_file_path)

# Iterate through all XML files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.xml'):
        file_path = os.path.join(input_dir, filename)
        
        # Load the XML file
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f'Error parsing {filename}: {e}')
            continue
        
        # Extract document ID
        doc_id = root.find('document/id').text
        
        # Extract passages and their annotations
        sections = {}
        
        # Extract the front title
        front_title = ""
        for passage in root.findall('document/passage'):
            passage_type = passage.find('infon[@key="type"]').text if passage.find('infon[@key="type"]') is not None else ''
            if passage_type == 'front':
                front_title = passage.find('text').text if passage.find('text') is not None else ''
        
        for passage in root.findall('document/passage'):
            section_type = passage.find('infon[@key="section_type"]')
            section_name = section_type.text if section_type is not None else 'UNKNOWN'
            
            if section_name in ['TITLE', 'ABSTRACT', 'METHODS', 'RESULTS', 'DISCUSS', 'CONCL']:
                if section_name not in sections:
                    sections[section_name] = {'passages': [], 'annotations': [], 'subsections': []}
                
                sections[section_name]['passages'].append(passage)
                sections[section_name]['annotations'].extend(passage.findall('annotation'))
                
                # For text file creation
                passage_type = passage.find('infon[@key="type"]').text if passage.find('infon[@key="type"]') is not None else ''
                text = passage.find('text').text if passage.find('text') is not None else ''
                
                if section_name == 'ABSTRACT':
                    if text.strip():
                        sections[section_name]['subsections'].append(text.strip())
                else:
                    if passage_type.startswith('title') and text.strip():
                        sections[section_name]['subsections'].append((text.strip(), ''))
                    elif passage_type == "paragraph" and text.strip():   #Added this elif part later
                        # Handle paragraphs directly under section_type without titles
                        sections[section_name]['subsections'].append(('Paragraph', text.strip()))
                    elif text.strip() and sections[section_name]['subsections']:
                        title, _ = sections[section_name]['subsections'][-1]
                        sections[section_name]['subsections'][-1] = (title, text.strip())
                    elif text.strip():
                        sections[section_name]['subsections'].append(('Paragraph', text.strip()))
        
        # Create section files
        for section_name, content in sections.items():
            create_section_file(content['passages'], content['annotations'], doc_id, section_name, output_xml_dir)
            if section_name == 'ABSTRACT':
                create_abstract_text_file(doc_id, section_name, front_title, content['subsections'], output_text_dir)
            else:
                create_text_files_for_section(doc_id, section_name, content['subsections'], output_text_dir)

# Post-process and merge TITLE files with the next paragraph files
post_process_title_files(output_text_dir)

print(f'Processed XML files and created passage files in {output_xml_dir} and text files in {output_text_dir}')
