#!/usr/bin/env bash

for file in output/*; do
    base_file=$(basename "$file")
    diff "snooper_output/$base_file" "tools_correct_output/$base_file"
done
