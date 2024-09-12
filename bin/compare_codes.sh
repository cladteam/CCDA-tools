#!/usr/bin/env bash
set -euxo pipefail
pwd
ls
for file in snooper_output/*; do
    base_file=$(basename "$file")
    echo "snooper_output/$base_file  tools_correct_output/$base_file"
    diff "snooper_output/$base_file" "tools_correct_output/$base_file"
    if $(( $? gt 0 ))
    then
        echo "diff failed for $file with status $?"
    fi
done
