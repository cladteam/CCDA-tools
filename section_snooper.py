
"""
    section_snooper - looks for specfic sections driven by metadata, and shows any ID, CODE and VALUE elements within them. 
"""

import argparse
import xml.etree.ElementTree as ET  # https://docs.python.org/3/library/xml.etree.elementtree.html
from util.xml_ns import ns
from util.vocab_map_file import oid_map
from util import spark_util
from util.vocab_spark import VocabSpark

# INPUT_FILENAME = 'resources/CCDA_CCD_b1_InPatient_v2.xml'
INPUT_FILENAME = 'resources/CCDA_CCD_b1_Ambulatory_v2.xml'
spark_util_object = spark_util.SparkUtil()
spark = spark_util_object.get_spark()

parser = argparse.ArgumentParser(
    prog='CCDA - OMOP Code Snooper',
    description="finds all code elements and shows what concepts the represent",
    epilog='epilog?')
parser.add_argument('-f', '--filename', default=INPUT_FILENAME,
                    help="filename to parse")
args = parser.parse_args()

tree = ET.parse(INPUT_FILENAME)

SECTION_PATH = "./component/structuredBody/component/section"
SECTION_CODE = "./code"
# OBSERVATION_SECTION_CODE = "./code[@code=\"30954-2\"]"

#UNUSED
###entity_metadata = {  # can be recursive, hopefully not looping
###    'observation' : [ 'id', 'code', 'effectvieTime', 'value', referenceRange/observationRange ],
###    'procedure' : [ 'id', 'code', 'effectiveTime', 'targetSite', 'performer', 'participant']
###    'encounter' : ['id', 'code', 'effectiveTime', 'performer/assignedEntity', 'participant/participantRole', # provider, care_site
###                    'entryRelationship/observation', 'entryRelationship/act']
###    'act' : [ 'id', 'code', 'entryRelationship/observation' ]
###
###    'performer/assignedEntity'; [ 'id', 'code'],
###    'participant/participantRole': [ 'code', 'addr', 'telecom', 'playingEntity']
###    'entryRelationship/observation' : see obserg
###    'entryRelationship/act'  : see act
###}

section_metadata = {
    '48765-2': { # ALLERGIES # /entry/act?
        "./entry/"  : [ 'encounter', 'act' ]
    },
    '46240-8' : { # ECOUNTERS, HISTORY OF
        "./entry/encounter"  : [ 'encounter' ]
    },

    '11369-6' : { # IMMUNIZATION ***
        "./entry/substanceAdministration/consumable/manufacturedProduct/manufacturedMaterial" 
    },

    '10160-0' : { # MEDICATIONS, HISTORY OF ***
         "./entry/substanceAdministration/" : [ "consumable/manufacturedProduct/manufacturedMaterial",
                                                "performer",
                                                "entryRelationship/observation",
                                                "entryRelationship/supply/product/manufacturedProduct/manufacturedMaterial" ]
    },

    '10183-2' : { # HOSPITAL DISCHARGE ****
         "./entry/act/" :['id', 'code', 'effectiveTime', 'entryRelationship/substanceAdministration' ],
         "./entry/act/entryRelationship/substanceAdministration/consumable/manufacturedProduct/manufacturedMaterial" :[],
         "./entry/act/entryRelationship/substanceAdministration/performer/assignedEntity" :[],
         "./entry/act/entryRelationship/substanceAdministration/performer/assignedEntity/representedOrganization" :[]
    },

    '47519-4' : { # PROCEDURES, HISTORY OF
        "./entry/procedure" :[ 'procedure' ]
    },

    '474020-5' : { # FUNCTIONAL STATUS (observations)
        "./entry/observation" :  [ 'observation'] 
    },

    '30954-2' : { # RESULTS
        "./entry/organizer/component/observation"  :[ 'observation' ] # may be multiple components
    },

    '8716-3' :  { # VITAL SIGNS
        "./entry/organizer/component/observation" : [ 'observation' ] # may be multiple components
    },
}

section_elements = tree.findall(SECTION_PATH, ns)
print("\n\n")

for section_element in section_elements:

    section_type=''
    section_code=''
    #section_code_element = section_element.find(SECTION_CODE, ns)  # just a find doesn't work
    for section_code_element in section_element.findall(SECTION_CODE, ns):
        if 'displayName' in section_code_element.attrib:
            section_type = section_code_element.attrib['displayName']
        elif 'code' in section_code_element.attrib:
            section_type = section_code_element.attrib['code']
        section_code = section_code_element.attrib['code']
        if section_type == '':
           details = VocabSpark.lookup_omop(section_code) 
           if details is not None:
               section_type = details[2]

    print(f"SECTION type:\"{section_type}\" code:\"{section_code}\" ", end='')
    section_code = section_code_element.attrib['code']
    if section_code is not None and section_code in section_metadata:
        print(f"")
        for entity_path in section_metadata[section_code]:
            print(f"  path: {entity_path}")
            for entity in section_element.findall(entity_path, ns):
                print(f"    type:\"{section_type}\" code:\"{section_code}\", ", end='')

                # effectiveTime
                for time_element in entity.findall('./effectiveTime', ns):
                     if 'value' in time_element.attrib:
                        print(f" time:{time_element.attrib['value']}", end="")
                     else:
                        print((f" time:{time_element.attrib['low']}"
                               f" time:{time_element.attrib['high']}"), end="")

                # referenceRange

                # ID
                for id_element in entity.findall('./id', ns):
                    if 'root' in id_element:
                         print(f" root:{id_element.attrib['root']}", end="")
                    if 'translation' in id_element:
                         print(f" translation:{id_element.attrib['translation']},", end=' ')
                # CODE
                for code_element in entity.findall('./code', ns):
                    vocabulary_id = oid_map[code_element.attrib['codeSystem']][0]
                    print(f" code: {code_element.attrib['displayName']}, {vocabulary_id}, {code_element.attrib['code']}, ", end=' ')
       
                # VALUE 
                value_string="value: "
                for value_element in entity.findall('./value', ns):
                    if 'value' in value_element.attrib: 
                        value_string = f"{value_string}, {value_element.attrib['value']} "
                    else:
                        value_string = f"{value_string}, None "
                    if 'unit' in value_element.attrib: 
                        value_string = f"{value_string}, {value_element.attrib['unit']}  "
                    else:
                        value_string = f"{value_string}, None "
                    if 'xsi:type' in value_element.attrib: 
                        value_string = f"{value_string}, {value_element.attrib['xsi:type']} "
                    else:
                        value_string = f"{value_string}, None "
                print(value_string, end='')
                print("")
    else:
        print(f"No metadata for \"{section_code}\"     ")