#!/usr/bin/env bash
set -xo pipefail
pwd
for file in snooper_output/*; do
    base_file=$(basename "$file")
    echo "snooper_output/$base_file  tools_correct_output/$base_file"
    diff "snooper_output/$base_file" "tools_correct_output/$base_file"
done
