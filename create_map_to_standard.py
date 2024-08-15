#!/usr/bin/env python3

"""
    This creates a table that maps from (oid, vocabulary_code)
    to  OMOP standard concept_id, and is filtered down to just
    concepts detected by the code snoopers.

    For now, it's basically a test of how hard Pandas crashes under
    the load of those large OMOP vocabulary files.
    (as well as a crash-course in Pandas)

    Creates files as output:
    -  map_to_standard with (oid, concept_code, concept_id, domain_id)
    -  uber_map_to_standard.csv (section, oid, concept_code, concept_id, domain_id)
      - the section is the source section in the collection of CCDA documents used
        to create this mapping.

"""


import pandas as pd
import numpy as np
import argparse
import os


def main():
    """ produces a map from an input table of (oid, concept_code) to concept_id,
        mapping OIDs to vocabulary_ids,
        mapping (vocabulary_id, concept_code) to concept_id,
        then mapping concept_id to concept_id via the concept_relationship table.

        input file should have header: section,oid,concept_code,concept_name
        oid_map should have header: oid,vocabulary_id
    """

    # Get Args
    parser = argparse.ArgumentParser(
        prog='create mapping table from source side OIDs and codes',
        description="finds all code elements and shows what concepts the represent",
        epilog='epilog?')
    args = parser.parse_args()
    #group = parser.add_mutually_exclusive_group(required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--directory', help="directory of files to parse", default='snooper_output')
    group.add_argument('-f', '--filename', help="filename to parse")
    args = parser.parse_args()

    # Get Vocabularies
    (oid_map_df, concept_df, concept_relationship_df) = read_vocabulary_tables()


    # Get Data, collect
    uber_df = None
    if args.filename is not None:
        uber_df = map_code_file(args.filename , oid_map_df, concept_df, concept_relationship_df)
    elif args.directory is not None:
        only_files = [f for f in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, f))]
        for file in (only_files):
            print(f"dir: {args.directory} file:{file}")
            file_mapped_concepts_df = map_code_file(os.path.join(args.directory,file), oid_map_df, concept_df, concept_relationship_df)
            if uber_df is None:
                uber_df = file_mapped_concepts_df
            else:
                uber_df = pd.concat([uber_df, file_mapped_concepts_df])

    else:
        logger.error("Did args parse let us  down? Have neither a file, nor a directory.")


    # Combine Data
    uber_df.to_csv("uber_map_to_standard.csv", sep=",", header=True, index=False)

    # uber_df includes the section name. Remove it.
    map_to_standard_df = uber_df[ ['oid', 'concept_code', 'concept_id', 'domain_id'] ]
    map_to_standard_df = map_to_standard_df.drop_duplicates()
    map_to_standard_df.to_csv("map_to_standard.csv", sep=",", header=True, index=False)





def map_code_file(filename, oid_map_df, concept_df, concept_relationship_df):
    desired_columns = ['section', 'oid', 'concept_code', 'concept_id', 'domain_id']
    input_df = pd.read_csv(filename,
                             engine='c', header=0, sep=',',
                             on_bad_lines='warn',
                             dtype={
                                    'section': str,
                                    'oid': str,
                                    'concept_code': str,
                                    'concept_name': str
                                    }
                             )

    # Step 1: add vocabulary_id to input
    ###input_df =  input_df.join(oid_map_df, on='oid', how='left')
    # results in "You are trying to merge on object and int64 columns "
    input_w_vocab_df =  input_df.merge(oid_map_df, on='oid', how='left')

    # Step 2: map  input to OMOP concept_ids
    input_w_concept_id_df = input_w_vocab_df.merge(concept_df, on=['vocabulary_id', 'concept_code'], how='left')

    # Step 2.5 collect concepts that are already standard here
    already_standard_df = input_w_concept_id_df[ input_w_concept_id_df['standard_concept'] == 'S' ]
    already_standard_df = already_standard_df[desired_columns]
    already_standard_df.to_csv("already_" + filename, sep=",", header=True, index=False)


    # Step 3: map  input to OMOP standard concept_ids
    input_w_standard_df = input_w_concept_id_df.merge(concept_relationship_df,
                                                      left_on='concept_id',
                                                      right_on='concept_id_1')
    input_w_standard_df = input_w_standard_df[ ['section', 'oid',  'concept_code',  'concept_id_2'] ]  # still missing domain_id
    input_w_standard_df.columns=['section', 'oid',  'concept_code',  'concept_id']  # still missing domain_id
    input_w_standard_df.to_csv("debug_" + filename, sep=",", header=True, index=False)

    # Step 4:  map into concept again to pick up the domain_id from concept_id_2
    input_w_standard_df = input_w_standard_df.merge(concept_df, on='concept_id')
    input_w_standard_df = input_w_standard_df[ ['section', 'oid',  'concept_code_x','concept_id',  'domain_id'] ] 
    input_w_standard_df.columns=['section', 'oid',  'concept_code',  'concept_id', 'domain_id']  

    # Step 5, add the already_standard_df
    input_w_standard_df = pd.concat([input_w_standard_df,  already_standard_df])

    # Output  a debug file of just this input file's mapped terms
    #input_w_standard_df.to_csv("debug_" + filename, sep=",", header=True, index=False)

    #add where clause for standard concept or explore, we wont find a standard to standard

    # Q: DO WE GET MORE THAN ONE?? TODO
    #input_w_standard_df = input_w_standard_df[ 
    return input_w_standard_df


def read_vocabulary_tables():
    """ returns (oid_map_df, concept_df, concept_relationship_df)
    """
    print("READING OID MAP")
    oid_map_df = pd.read_csv("../CCDA-data/oid.csv", header=0,
                             on_bad_lines='warn',
                             dtype={ 'oid': str, 'vocabulary_id': str }
                             #engine='c', header=0, index_col=0, sep=',',
                            )
    print(f"....oid_map {len(oid_map_df)}  {list(oid_map_df)} ")

    print("READING CONCEPT.csv")
    concept_df = pd.read_csv("../CCDA_OMOP_Private/CONCEPT.csv",
                             engine='c', header=0, sep='\t',
                             #index_col=0,
                             on_bad_lines='warn',
                             dtype={
                                    #'concept_id': , 'Int64',
                                    'concept_id': np.int32 ,
                                    'concept_name': str,
                                    'domain_id' : str,
                                    'vocabulary_id' : str,
                                    'concept_class_id' : str,
                                    'standard_concept' : str,
                                    'concept_code': str,
                                    'invalid_reason': str,
                                    'valid_start_date' : str,
                                    'valid_end_date' : str,
                                    #'valid_start_date' : some proper date class TBD
                                    #'valid_end_date' : some proper date class TBD,
                                },
                                usecols = [0, 1, 2, 3, 4, 5, 6, 7] # no dates for now
                             )

    print(f"....have concept_df {len(concept_df)}  {list(concept_df)}")

    print("READING CONCEPT_RELATIONSHIP.csv")
    concept_relationship_df = pd.read_csv("../CCDA_OMOP_Private/CONCEPT_RELATIONSHIP.csv",
                             engine='c',
                             header=0,
                             # index_col=0,
                             sep='\t',
                             on_bad_lines='warn',
                             dtype={
                                    #'concept_id': , 'Int64',
                                    'concept_id_1': np.int32 ,
                                    'concept_id_2': np.int32 ,
                                    'relationship_id' : str,
                                    'valid_start_date' : str,
                                    'valid_end_date' : str,
                                    #'valid_start_date' : some proper date class TBD
                                    #'valid_end_date' : some proper date class TBD,
                                    'invalid_reason': str
                                }
                                #,usecols = [0, 1, 2] # no dates or date types for now
                             )
    # ONLY USING "MAPS TO"
    print(f".....concept_relationship_df {len(concept_relationship_df)} {list(concept_relationship_df)}")
    print(concept_relationship_df)

    print("===============")
    #concept_maps_to_df = concept_relationship_df[concept_relationship_df['relationship_id' == 'Maps to']]
    concept_maps_to_df = concept_relationship_df.query("relationship_id == 'Maps to'")

    print(f".....concept_maps_to_df {len(concept_maps_to_df)} {list(concept_maps_to_df)}")
    print(concept_maps_to_df)

    return (oid_map_df, concept_df, concept_maps_to_df)



if __name__ == '__main__':
    main()
