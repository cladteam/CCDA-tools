#!/usr/bin/env bash
set -eou pipefail
pwd
for file in snooper_output/*; do
    base_file=$(basename "$file")
    diff "snooper_output/$base_file" "tools_correct_output/$base_file"
done
