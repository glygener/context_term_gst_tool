
'''
import os
import pandas as pd
import regex as re

output_text_dir = "/home/shovan/nlputils/EDG_framework/Full_Length_Context_Term_Detection/output_text_section_jan"
excel_sentences = "/home/shovan/nlputils/EDG_framework/Full_Length_Context_Term_Detection/Outputs_Jan/sentences.xlsx"
sentences_data = []

def get_sentences(text):
    # Enhanced regex to handle sentence boundaries and exceptions like 'e.g.'
    text = re.sub(r"(\bFig\.)\s*\n\s*", r"\1 ", text, flags=re.IGNORECASE)  # Join lines with "Fig."
    text = re.sub(r"(\bTable\.)\s*\n\s*", r"\1 ", text, flags=re.IGNORECASE)  # Join lines with "Table."

    pattern = re.compile(
        r"""
        (?<!\b(?:Mr|Dr|Ms|Mrs|St|vs|fig|table|etc|i\.e|cf|Jr|Prof|Sr)\.)   # Avoid splitting after abbreviations
        (?<!\b[A-Z]\.)                                           # Avoid splitting after initials like 'P.'
        (?<!e\.g\.)                                              # Prevent splitting after 'e.g.'
        (?<!e\.g\.\s\(.*?\))                                     # Prevent splitting if 'e.g.' is followed by parentheses
        (?<!e\.g\.\s(?=[a-z]))                                   # Prevent splitting after 'e.g.' followed by lowercase
        \.\s(?=[A-Z])
        """,
        re.VERBOSE | re.IGNORECASE # Enables multi-line regex with comments
    )
    # Split the text using the pattern
    sentences = pattern.split(text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return [sentence if sentence.endswith('.') else sentence + '.' for sentence in sentences]

def process_text(file_path, pmcid, section):
    with open(file_path, 'r') as file:
        text = file.read()
        sentences = get_sentences(text)
        for i, sentence in enumerate(sentences):
            sentences_data.append({
                'pmcid': 'PMC' + pmcid,
                'section': section,
                'sent_index': i,
                'sent_text': sentence,
                'charStart': text.find(sentence),
                'charEnd': text.find(sentence) + len(sentence)
            })

def save_to_excel():
    sentences_df = pd.DataFrame(sentences_data)
    sentences_df.drop_duplicates(subset=['pmcid', 'section', 'sent_index', 'sent_text', 'charStart', 'charEnd'], inplace=True)
    sentences_df.to_excel(excel_sentences, index=False)

# Process each text file to extract sentences
for pmid_file in os.listdir(output_text_dir):
    if pmid_file.endswith('.txt'):
        # Extract PMCID and SECTION, assuming filename structure is consistent
        parts = pmid_file.split('_')
        pmcid = parts[0]
        if parts[-1].startswith("Paragraph") and parts[-1].endswith('.txt'):
            section = '_'.join(parts[1:-1])
        else:
            section = parts[1].replace('.txt', '')
        file_path = os.path.join(output_text_dir, pmid_file)
        process_text(file_path, pmcid, section)

save_to_excel()
print("Sentence extraction completed successfully.")
'''

import os
import pandas as pd
import regex as re

base_dir = os.path.dirname(os.path.abspath(__file__))
output_text_dir = os.path.join(base_dir, '/app/gst_full/output_text_section_FL')
excel_sentences = os.path.join(base_dir, '/app/gst_full/Outputs/sentences.xlsx')
sentences_data = []

def get_sentences(text):
    """
    Splits text into sentences while handling:
      1) Newlines after 'Fig.', 'Table.', and similar abbreviations
      2) Common scientific abbreviations (e.g. 'i.e.', 'e.g.', etc.)
      3) Merging any sentence ending with a known abbreviation into the following sentence
    """

    #
    # 1) UNIFY ALL NEWLINES
    #
    # Convert all newlines (and any surrounding whitespace) into a single space.
    # This helps ensure that something like "Fig.\nS6F-H)" stays on the same line.
    #
    text = re.sub(r"\s*\n\s*", " ", text)

    #
    # 2) SPLIT ON A PERIOD + SPACES + (UPPERCASE OR '(')
    #
    # This is a broad rule that looks for a period (.) followed by one or more spaces,
    # then an uppercase letter [A-Z] or an opening parenthesis [(]. 
    #
    # NOTE: We use 're.split()' with a lookbehind for the period, but we do NOT rely on 
    # variable-length negative lookbehinds. Instead, we handle abbreviation merging in step 3.
    #
    raw_sentences = re.split(r'(?<=\.)\s+(?=[A-Z(])', text)

    #
    # 3) MERGE SENTENCES ENDING WITH KNOWN ABBREVIATIONS
    #
    # If a 'sentence' ends with an abbreviation like "Fig.", we merge it with the next chunk.
    #
    abbreviations = {
        "Fig.", "Figs.", "Tab.", "Table.", "Mr.", "Dr.", "Ms.", "Mrs.", "St.", "vs.", 
        "etc.", "i.e.", "e.g.", "cf.", "Jr.", "Prof.", "Sr."
    }

    sentences = []
    for chunk in raw_sentences:
        chunk = chunk.strip()
        if not chunk:
            continue

        # If there are no sentences yet, add the first chunk
        if not sentences:
            sentences.append(chunk)
        else:
            last_sentence = sentences[-1]
            # Check if the last sentence ends with any known abbreviation
            if any(last_sentence.endswith(abbr) for abbr in abbreviations):
                # Merge this chunk with the previous (abbreviated) sentence
                sentences[-1] = last_sentence + " " + chunk
            else:
                sentences.append(chunk)

    #
    # 4) ENSURE EACH SENTENCE ENDS WITH A PERIOD
    #
    final_sentences = []
    for sent in sentences:
        sent = sent.strip()
        if not sent.endswith('.'):
            sent += '.'
        final_sentences.append(sent)

    return final_sentences

def process_text(file_path, pmcid, section):
    with open(file_path, 'r') as file:
        text = file.read()
        sentences = get_sentences(text)
        for i, sentence in enumerate(sentences):
            sentences_data.append({
                'pmcid': 'PMC' + pmcid,
                'section': section,
                'paragraph': paragraph,
                'sent_index': i,
                'sent_text': sentence,
                'charStart': text.find(sentence),
                'charEnd': text.find(sentence) + len(sentence)
            })

def save_to_excel():
    sentences_df = pd.DataFrame(sentences_data)
    sentences_df.drop_duplicates(
        subset=['pmcid', 'section', 'paragraph', 'sent_index', 'sent_text', 'charStart', 'charEnd'], 
        inplace=True
    )
    sentences_df.to_excel(excel_sentences, index=False)

# Process each text file to extract sentences
for pmid_file in os.listdir(output_text_dir):
    if pmid_file.endswith('.txt'):
        # Extract PMCID and SECTION from filename
        parts = pmid_file.split('_')
        pmcid = parts[0]
        
        if parts[-1].startswith("Paragraph") and parts[-1].endswith('.txt'):
            paragraph = parts[-1].replace('.txt', '')
            section = '_'.join(parts[1:-1])
        else:
            paragraph = None
            section = parts[1].replace('.txt', '')

        file_path = os.path.join(output_text_dir, pmid_file)
        process_text(file_path, pmcid, section)

save_to_excel()
print("Sentence extraction completed successfully.")




