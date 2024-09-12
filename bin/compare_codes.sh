#!/usr/bin/env bash
echo "starting compare"
pwd
ls
echo "comparing files"
for file in snooper_output/*; do
    echo "File: \"$file\" "
    base_file=$(basename "$file")
    echo "snooper_output/$base_file  tools_correct_output/$base_file"
    diff "snooper_output/$base_file" "tools_correct_output/$base_file"
    echo "diff status for $base_file $?"
done
exit 0
