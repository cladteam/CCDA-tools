#!/usr/bin/env python3
"""
builds a table of code and value

This versio correlates values and codes by path and puts them on the same row.
"""

import os
import argparse
import re
import lxml.etree as ET
from xml_ns import ns
from vocab_map_file import oid_map
import vocab_maps
import pandas as pd
from collections import defaultdict

ccda_code_values_columns = [ 'filename', 'section', 'codeSystem', 'code',
                             'value-type', 'value-unit',
                             'value-value', 'value-code', 'value-codeSystem',  'value-text',
                             'path']


def snoop_section(tree, filename):
    trace_df = pd.DataFrame(columns=ccda_code_values_columns)
    section_elements = tree.findall(".//section", ns)
    for section_element in section_elements:

        section_template_id = "n/a"
        section_template_ele = section_element.findall("templateId",ns)
        if len(section_template_ele) > 0:
            section_template_id = section_template_ele[0].get('root')

        entry_elements = section_element.findall("entry", ns)
        for entry_ele in entry_elements:

            value_dict = defaultdict(list)  # keys are paths
            value_elements = entry_ele.findall(".//value", ns)
            for value_ele in value_elements:
                value_path = re.sub(r'{.*?}', '', tree.getelementpath(value_ele))
                value_path = "/".join(value_path.split("/")[:-1])
                value_attribs_dict = { re.sub(r'{.*}', '', a):
                                       re.sub(r'{.*}', '', value_ele.attrib[a])
                                       for a in value_ele.attrib  }
                value_dict[value_path].append( (value_attribs_dict, value_ele.text) )

            code_elements = entry_ele.findall(".//code", ns)
            for code_ele in code_elements:
                code_path = re.sub(r'{.*?}', '', tree.getelementpath(code_ele))
                code_path = "/".join(code_path.split("/")[:-1])
                value_tuple_list = value_dict[code_path] # tuple is (dict, text)
                for value_tuple in value_tuple_list:
                    new_row = pd.DataFrame([{
                        'filename': filename,
                        'section': section_template_id,
                        'path': code_path,
                        'code': code_ele.get('code'),
                        'codeSystem': code_ele.get('codeSystem'),
                        'value-type': value_tuple[0].get('type', ''),
                        'value-unit': value_tuple[0].get('unit', ''),
                        'value-value': value_tuple[0].get('value', ''),
                        'value-code': value_tuple[0].get('code', ''),
                        'value-codeSystem': value_tuple[0].get('codeSystem', ''),
                        'value-text': value_tuple[1].strip() if value_tuple[1] else ''
                    }])
                    trace_df = pd.concat([trace_df, new_row], ignore_index=True)
    return(trace_df)


def main():

    parser = argparse.ArgumentParser(
        prog='CCDA - OMOP Code Snooper',
        description="finds all code elements and shows what concepts the represent",
        epilog='epilog?')
    parser.add_argument('-f', '--filename', help="filename to parse")
    parser.add_argument('-d', '--directory', help="directory of files to parse")
    args = parser.parse_args()

    if args.filename is not None:
        tree = ET.parse(args.filename)
        file_df = snoop_section(tree, args.filename)
        #pd.set_option('display.max_rows', len(file_df))
        print(file_df)
    elif args.directory is not None:
        all_files_df = pd.DataFrame(columns=ccda_code_values_columns)
        only_files = [f for f in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, f))]
        for filename in (only_files):
            if filename.endswith(".xml"):
                tree = ET.parse(os.path.join(args.directory, filename))
                file_df = snoop_section(tree, filename)
                all_files_df = pd.concat([all_files_df, file_df], ignore_index=True)
        #pd.set_option('display.max_rows', len(all_files_df))
        print(all_files_df)
        all_files_df.to_csv(f"raw_section_snooper_Chris.csv",
                                sep=",", header=True, index=False)
    else:
        logger.error("Did args parse let us  down? Have neither a file, nor a directory.")




if __name__ == '__main__':
    main()
