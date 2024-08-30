#!/usr/bin/env bash
set -euo pipefail

# snoop_all.sh
#
# Runs the header and section code snooper on known input files.
# Code/Term output  goes from the snoopers to files in a  "snooper_output" directory.
#  Ouptut here is summary data per file that goes to the  "output" directory. 
rm -rf output
mkdir output

FILES=(
    "../CCDA-data/resources/170.314b2_AmbulatoryToC.xml"
    "../CCDA-data/resources/CCDA_CCD_b1_Ambulatory_v2.xml"
    "../CCDA-data/resources/CCDA_CCD_b1_InPatient_v2.xml"
    "../CCDA-data/resources/ToC_CCDA_CCD_CompGuideSample_FullXML.xml"
    "../CCDA-data/resources/bennis_shauna_ccda.xml"
    "../CCDA-data/resources/eHX_Terry.xml"
    "../CCDA-data/resources/anna_flux.xml"
    "../CCDA-data/resources/healtheconnectak-ccd-20210226.2.xml"
    "../CCDA-data/resources/C-CDA_R2-1_CCD.xml"
    "../CCDA-data/resources/C-CDA_R2-1_CCD_modified.xml"
    "../CCDA-data/resources/Patient-502.xml"
)
    #"../CCDA-data/resources/Inpatient_Encounter_Discharged_to_Rehab_Location(C-CDA2.1).xml"

TOOLS=(
    "header_code_snooper.py"
    "section_code_snooper.py"
)


for ((i = 0; i < ${#FILES[@]}; i++)) ; do
    file=${FILES[$i]}
    outfile=$(basename $file)
    for tool in ${TOOLS[@]}; do
        echo "$tool $outfile"
        ./$tool -f "$file" >> "output/$outfile.out"
    done
done
