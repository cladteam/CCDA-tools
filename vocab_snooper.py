import argparse
import re
import lxml.etree as ET
import os
from xml_ns import ns
from vocab_map_file import oid_map
import vocab_maps
import pandas as pd
from pathlib import Path
from foundry.transforms import Dataset
from collections import defaultdict

# mamba install -y -q lxml


# Global DataFrame to hold codes found
# Define the list with column headers for the DataFrame, sourced from /All of Us-cdb223/Identified: HIN - HIE/CCDA/transform/mapping-reference-files/ccda-value-set-mapping-table
# for comparision, edit as necessary per requirements.
columns = [
    "data_source", "resource", "data_element_path", "data_element_node", 
    "codeSystem", "src_cd", "src_cd_description","src_cd_count", "target_concept_id", 
    "target_concept_name", "target_domain_id", "target_vocabulary_id", 
    "target_concept_class_id", "target_standard_concept", "target_concept_code", 
    "target_tbl_column_name", "notes"
]

# Create an empty DataFrame with the specified columns
vocab_codes = pd.DataFrame(columns=columns)

def get_code_name(codeSystem, codeSystemName, code, concept_df):
    """
    Retrieves the concept name from a concept DataFrame based on the given code system, code system name, and code.
    Returns 'n/a' if no match is found.
    """
    if codeSystemName:
        vocabulary_id = re.sub(r' CT', '', codeSystemName)  # Remove unwanted text from codeSystemName
        concept_query = f"concept_code == '{code}' and vocabulary_id == '{vocabulary_id}'"
        concept_row = concept_df.query(concept_query)

        if concept_row.size > 1:
            concept_name = concept_row['concept_name'].values[0]
            vocabulary_id = concept_row['vocabulary_id'].values[0]
            return concept_name, vocabulary_id
        return 'n/a', 'n/a'
    return 'n/a', 'n/a'


def snoop_for_code_tag(tree, expr, ns, concept_df, vocab_codes):
    """
    Finds all elements matching the XPath expression (expr) in the XML tree and extracts relevant attributes.
    Appends the extracted information to the given vocab_codes DataFrame.
    """
    section_elements = tree.findall(expr, ns)
    for section_element in section_elements:
        # Extract attributes
        data_element_node = re.sub(r'{.*}', '', section_element.tag)
        src_cd = section_element.attrib.get('code')
        codeSystem = section_element.attrib.get('codeSystem')
        resource = section_element.attrib.get('codeSystemName')
        src_cd_description = section_element.attrib.get('displayName')
        #templateId = section_element.attrib.get('templateId')

        # Append to vocab_codes DataFrame
        new_row = pd.DataFrame([{
            'data_element_node': data_element_node,
            'src_cd': src_cd,
            'codeSystem': codeSystem,
            'resource': resource,
            'src_cd_description': src_cd_description,

        }])
        count_dict[(codeSystem,src_cd)] += 1
        # Concatenate the new row with the DataFrame
        combined_df = pd.concat([vocab_codes, new_row], ignore_index=True)
        if count_dict[(codeSystem,src_cd)] = 0:
            vocab_codes = pd.concat([vocab_codes, new_row], ignore_index=True)
        else
            pass
        # Check if the new row already exists in the DataFrame
        if combined_df.duplicated().iloc[-1]:
            print(combined_df.iloc[-1])
            existing_row = combined_df.iloc[0].index[0]
            duplicate_index = existing_row.index[0]
            vocab_codes.at[duplicate_index, 'src_cd_count'] += 1
            pass
            #print("Duplicate row exists. Skipping insertion.")
        else:
            vocab_codes = pd.concat([vocab_codes, new_row], ignore_index=True)
        ###
    return vocab_codes


def process_xml_file(file_path, concept_df, ns):
    """
    Process a single XML file, extract code elements, and return the resulting DataFrame.
    """
    try:
        tree = ET.parse(file_path)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return pd.DataFrame()  # Return an empty DataFrame
    except ET.XMLSyntaxError:
        print(f"Error: Failed to parse {file_path}.")
        return pd.DataFrame()  # Return an empty DataFrame

    # Initialize an empty DataFrame for vocab codes
    global vocab_codes

    # Extract code elements (tag-based and attribute-based)
    vocab_codes = snoop_for_code_tag(tree, ".//code", ns, concept_df, vocab_codes)
    vocab_codes = snoop_for_code_tag(tree, ".//*[@codeSystem]", ns, concept_df, vocab_codes)
    vocab_codes['data_source'] = 'ccda-xml'#os.path.basename(file_path)
    return vocab_codes


def process_directory(directory, concept_df, ns):
    """
    Process all XML files in a directory and return a combined DataFrame.
    """
    global vocab_codes

    # Loop through all XML files in the directory
    for file_path in Path(directory).rglob("*.xml"):
        print(f"Processing file: {file_path}")
        vocab_codes = process_xml_file(file_path, concept_df, ns)
        #all_vocab_codes = pd.concat([all_vocab_codes, file_vocab_codes], ignore_index=True)

    return vocab_codes


def main():
    """
    Main function that parses arguments, processes the XML file(s), extracts code elements, and cleans up the DataFrame.
    """
    parser = argparse.ArgumentParser(
        prog='CCDA - OMOP Code Snooper',
        description="Finds all code elements and shows what concepts they represent",
        epilog='epilog?')
    parser.add_argument('-f', '--filename', help="Filename of the XML file to parse")
    parser.add_argument('-d', '--directory', help="Directory containing XML files to parse")
    args = parser.parse_args()

    if not args.filename and not args.directory:
        print("Error: You must provide either a filename or a directory.")
        return

    print("Reading Vocabulary, this may take a minute...")
    # Load concept DataFrame (assuming you have this functionality available)
    concept_df = [] #vocab_maps.read_concept()

    all_vocab_codes = pd.DataFrame()

    # If a filename is provided, process that single file
    if args.filename:
        print(f"Processing single file: {args.filename}")
        all_vocab_codes = process_xml_file(args.filename, concept_df, ns)

    # If a directory is provided, process all XML files in that directory
    if args.directory:
        print(f"Processing all files in directory: {args.directory}")
        all_vocab_codes = process_directory(args.directory, concept_df, ns)

    # Clean up the DataFrame
    short_vocabs = all_vocab_codes[['src_cd','codeSystem']].drop_duplicates().sort_values(by='codeSystem')
    #short_vocabs = all_vocab_codes.drop_duplicates().sort_values(by='codeSystem')
###
    # Output to CSV
    #all_vocab_codes.to_csv('/foundry/outputs/vocab_discovered_codes_expanded.csv', index=False)
    #short_vocabs.to_csv('/foundry/outputs/vocab_discovered_codes.csv', index=False)
    
    #vocab_discovered_codescsv = Dataset.get("vocab_discovered_codescsv")
    #vocab_discovered_codescsv.upload_file("/foundry/outputs/vocab_discovered_codes.csv")

    #vocab_discovered_codes_expandedcsv = Dataset.get("vocab_discovered_codes_expandedcsv")
    #vocab_discovered_codes_expandedcsv.upload_file("/foundry/outputs/vocab_discovered_codes_expanded.csv")

    # Output as Dataset
    #vocab_discovered_codes_expanded = Dataset.get("vocab_discovered_codes_expanded")
    #vocab_discovered_codes_expanded.write_table(all_vocab_codes)
    
    #vocab_discovered_codes = Dataset.get("vocab_discovered_codes")
    #vocab_discovered_codes.write_table(short_vocabs)
###
    print(short_vocabs)


if __name__ == '__main__':
    main()
