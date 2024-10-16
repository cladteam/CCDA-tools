#!/usr/bin/env python3
"""
    raw_section_snooper - looks for ANY sections (XML elemnent tagged "section"?),
        within each type:
        - entry: ;shows template Id, concepts and names if present,
        - title
        - code
        - value TBD

"""

import argparse
import re
import lxml.etree as ET
from xml_ns import ns
from vocab_map_file import oid_map
import vocab_maps


def get_code_name(codeSystem, codeSystemName, code, concept_df):
    if codeSystemName is not None:
        vocabulary_id  = re.sub(r' CT', '', codeSystemName)
        concept_query = f"concept_code == '{code}' and vocabulary_id == '{vocabulary_id}'"
        concept_row = concept_df.query(concept_query)
        concept_name = 'n/a'
        if  concept_row.size > 1:
            concept_name = concept_row['concept_name']

        return concept_name
    else:
        return "n/a"


def snoop_for_section_tag(tree, expr, filename, concept_df):
    section_elements = tree.findall(expr, ns)

    for section_element in section_elements:

        entry_elements = section_element.findall("entry", ns)

        for entry_ele in entry_elements:
            code_elements = entry_ele.findall(".//code", ns)
            for code_ele in code_elements:
                #concept_name = get_code_name(code_ele.get('code'), code_ele.get('codeSystem'), code_ele.get('codeSystemName'), concept_df)
                print(( f"        ENTRY-CODE "
                        f"{re.sub(r'{.*}', '', code_ele.tag)} "
                        f"{code_ele.get('codeSystem')} "
                        #f"{code_ele.get('codeSystemName')} "
                       # f"{code_ele.get('code')} {concept_name}"
                        ), end="")
                if code_ele.text is not None:
                    print(f" {code_ele.text.strip()} ")
                else:
                    print("")
                print(f"          CODE path:\"{re.sub(r'{.*?}', '', tree.getelementpath(code_ele))}\" " )

            value_elements = entry_ele.findall(".//value", ns)
            for value_ele in value_elements:
                print( (f"        ENTRY-VALUE {re.sub(r'{.*}', '', value_ele.tag)}"
                    f" {value_ele.attrib}"), end="")
                if code_ele.text is not None:
                    print(f" {value_ele.text}")
                else:
                    print("")
                print(f"          VALUE path:\"{re.sub(r'{.*?}', '', tree.getelementpath(code_ele))}\" " )

def main():
    parser = argparse.ArgumentParser(
        prog='CCDA - OMOP Code Snooper',
        description="finds all code elements and shows what concepts the represent",
        epilog='epilog?')
    parser.add_argument('-f', '--filename', required=True, help="filename to parse")
    args = parser.parse_args()

    #print("Reading Vocab, takes a minute")
    #concept_df = vocab_maps.read_concept()
    concept_df = None
    tree = ET.parse(args.filename)

    # regular section
    #snoop_for_section_tag(tree, "code", args.filename)
    snoop_for_section_tag(tree, ".//section", args.filename, concept_df)

    # section with organizer




if __name__ == '__main__':
    main()
