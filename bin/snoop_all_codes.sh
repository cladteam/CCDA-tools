#!/usr/bin/env bash

mkdir output 2> /dev/null
mkdir logs 2> /dev/null

FILES=(
    "../CCDA-data/resources/170.314b2_AmbulatoryToC.xml"
    "../CCDA-data/resources/CCDA_CCD_b1_Ambulatory_v2.xml"
    "../CCDA-data/resources/CCDA_CCD_b1_InPatient_v2.xml"
    "../CCDA-data/resources/Inpatient_Encounter_Discharged_to_Rehab_Location(C-CDA2.1).xml"
    "../CCDA-data/resources/ToC_CCDA_CCD_CompGuideSample_FullXML.xml"
    "../CCDA-data/resources/bennis_shauna_ccda.xml"
    "../CCDA-data/resources/eHX_Terry.xml"
    "../CCDA-data/resources/anna_flux.xml"
    "../CCDA-data/resources/healtheconnectak-ccd-20210226.2.xml"
)

TOOLS=(
)
    # "section_code_snooper.py"

for ((i = 0; i < ${#FILES[@]}; i++)) ; do
    file="${FILES[$i]}"
    echo $file
    base_file=`basename $file`
    echo "$base_file"
    ./header_code_snooper.py -f "$file"  > "output/${base_file}.header_codes"
    ./section_code_snooper.py -f "$file"  > /dev/null
    echo
done
