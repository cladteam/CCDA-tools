#!/usr/bin/env python3

"""
    This creates a table that maps from (oid, vocabulary_code) 
    to  OMOP standard concept_id, and is filtered down to just
    concepts detected by the code snoopers.

    For now, it's basically a test of how hard Pandas crashes under
    the load of those large OMOP vocabulary files.
    (as well as a crash-course in Pandas)
"""


import pandas as pd
import numpy as np
import argparse


def main():
    """ produces a map from an input table of (oid, concept_code) to concept_id,
        mapping OIDs to vocabulary_ids,
        mapping (vocabulary_id, concept_code) to concept_id,
        then mapping concept_id to concept_id via the concept_relationship table.

        input file should have header: section,oid,concept_code,concept_name
        oid_map should have header: oid,vocabulary_id
    """

    parser = argparse.ArgumentParser(
        prog='create mapping table from source side OIDs and codes',
        description="finds all code elements and shows what concepts the represent",
        epilog='epilog?')
    parser.add_argument('-f', '--filename', help="input codes filename to map", default='output/all_codes.csv')
    args = parser.parse_args()

    # Step 0: get data
    (oid_map_df, concept_df, concept_relationship_df) = read_tables()

    print("READING INPUT")
    input_df = pd.read_csv(args.filename,
                             engine='c', header=0, sep=',',
                             on_bad_lines='warn',
                             dtype={
                                    'section': str,
                                    'oid': str,
                                    'concept_code': str,
                                    'concept_name': str
                                    }
                             )
    print(f".....input_df {len(input_df)} {list(input_df)} ")
    #print(f".....input_df {input_df.dtypes}")

    # Step 1: add vocabulary_id to input
    print("1. ADD VOCABULARY_ID")
    ###input_df =  input_df.join(oid_map_df, on='oid', how='left') 
    # results in "You are trying to merge on object and int64 columns "
    input_w_vocab_df =  input_df.merge(oid_map_df, on='oid', how='left') 
    print(list(input_w_vocab_df))

    # Step 2: map  input to OMOP concept_ids
    print("2. ADD CONCEPT_ID")
    input_w_concept_id_df = input_w_vocab_df.merge(concept_df, on=['vocabulary_id', 'concept_code'], how='left')
    print(list(input_w_concept_id_df))

    # Step 3: map  input to OMOP standard concept_ids
    print("3. MAP to STANDARD")
    print(list(input_w_concept_id_df))
    print(list(concept_relationship_df))
    input_w_standard_df = input_w_concept_id_df.merge(concept_relationship_df,
                                                      left_on='concept_id',
                                                      right_on='concept_id_1')
    print(list(input_w_standard_df))
    print(len(input_w_standard_df))
    print(input_w_standard_df)



def read_tables():
    """ returns (oid_map_df, concept_df, concept_relationship_df)
    """
    print("READING OID MAP")
    oid_map_df = pd.read_csv("../CCDA-data/oid.csv", header=0,
                             on_bad_lines='warn',
                             dtype={ 'oid': str, 'vocabulary_id': str }
                             #engine='c', header=0, index_col=0, sep=',',
                            )
    print(f"....oid_map {len(oid_map_df)}  {list(oid_map_df)} ")
    #print(f"....oid_map {oid_map_df.dtypes}")

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
    #concept_relationship_df = pd.read_csv("../CCDA_OMOP_Private/CONCEPT_RELATIONSHIP.csv",
    concept_relationship_df = pd.read_csv("../CCDA_OMOP_Private/CONCEPT_RELATIONSHIP_100000.csv",
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
