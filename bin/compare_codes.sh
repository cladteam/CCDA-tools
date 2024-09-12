#!/usr/bin/env bash
set -xo pipefail
pwd
ls
for file in snooper_output/*; do
    echo "File: \"$file\""
    base_file=$(basename "$file")
    echo "snooper_output/$base_file  tools_correct_output/$base_file"
    diff "snooper_output/$base_file" "tools_correct_output/$base_file"
done
