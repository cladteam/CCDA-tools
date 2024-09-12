#!/usr/bin/env bash
for file in snooper_output/*; do
    base_file=$(basename "$file")
    diff "snooper_output/$base_file" "tools_correct_output/$base_file"
    if (( $? > 0 ))
    then
        echo "diff failed for $file with status $?"
    fi
done
