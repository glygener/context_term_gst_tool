import re
import os

def obo_to_tsv(obo_file_path, tsv_file_path):
    # Regular expressions to match ID, Name, and Synonym
    id_pattern = re.compile(r"id: (.+)")
    name_pattern = re.compile(r"name: (.+)")
    synonym_pattern = re.compile(r'synonym: "(.+?)" RELATED \[\]')
    term_start_pattern = re.compile(r"\[Term\]")

    # Updated pattern to exclude specific entries:
    # Digits, digits with decimals, one letter, one letter followed by a digit, two letters,
    # and patterns with digits that may contain slashes, dashes, and periods.
    exclude_pattern = re.compile(
        r"""
        ^\d+(\.\d+)?$|                               # Digits or digits with decimals
        ^\.\d+$|                                     # Starting with a decimal point followed by digits
        ^[A-Za-z](\d)?$|                             # One letter or one letter followed by a digit
        ^[A-Za-z]{2}$|                               # Two letters
        ^\d+([\-\/.]\d+)+$|                          # Sequences with digits and -, /, or .
        ^\d+(\.\d+)*(/|\-|\.)\d+(\.\d+)*$|           # Complex patterns with ., -, / (e.g., 10.84.2, 10/16.4.3)
        ^[A-Za-z]\s\d+$|                             # Single letter followed by space and digits
        ^[A-Za-z]-\d+$|                              # Single letter followed by dash and digits (e.g., G-2)
        ^(\d+[:\-\/.]){1,}\d+$|                      # Numeric sequences separated by colons, dashes (e.g., 1:2, 4:13:23)
        ^\#\d+                                        # Terms starting with # followed by digits
        """, 
        re.VERBOSE
    )

    # Read the OBO file
    with open(obo_file_path, 'r') as file:
        obo_data = file.read()

    # Split the data into terms
    blocks = obo_data.strip().split("\n\n")
    terms = [block for block in blocks if term_start_pattern.match(block)]

    # Prepare the TSV data
    tsv_data = []

    for term in terms:
        # Extract ID, Name, and Synonyms
        cell_line = "Tissue"
        cellosaurus = "Brenda"

        id_match = id_pattern.search(term)
        name_match = name_pattern.search(term)

        if id_match and name_match:
            cellosaurus_id = id_match.group(1)
            name = name_match.group(1).strip()

            # Check if name matches exclusion criteria
            if not exclude_pattern.match(name):
                synonyms = synonym_pattern.findall(term)
                if synonyms:
                    for synonym in synonyms:
                        # Check each synonym against exclusion criteria
                        if not exclude_pattern.match(synonym):
                            tsv_data.append([cell_line, synonym, cellosaurus_id, synonym, name, "synonym"])
                    # Append original name as well
                    tsv_data.append([cell_line, name, cellosaurus_id, name, name, "original"])
                else:
                    # If there are no synonyms, append the name as original
                    tsv_data.append([cell_line, name, cellosaurus_id, name, name, "original"])
        else:
            print(f"Skipping a term due to missing ID or Name: {term}")

    # Write to TSV file
    with open(tsv_file_path, 'w') as tsv_file:
        for line in tsv_data:
            tsv_file.write('\t'.join(line) + '\n')

# Define the base directory relative to the script location
base_dir = os.path.dirname(os.path.abspath(__file__))
#print(base_dir)

# Define the relative paths
obo_relative_path = os.path.join(base_dir, '/app/Dictionary/brenda.obo')  # Replace with the path to your OBO file
tsv_relative_path = os.path.join(base_dir, '/app/OGER/oger/test/testfiles/tissue.tsv')  # Replace with your desired TSV file path

# Call the function to convert the OBO file to TSV format
obo_to_tsv(obo_relative_path, tsv_relative_path)
