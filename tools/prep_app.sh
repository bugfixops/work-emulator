#!/bin/bash
# Build the three input files of a graph (method_list.json, coverage_baseline.json, auto_calls.json) for one app.
# Usage (from work/): tools/prep_app.sh <App folder name in final_java_only>
set -e
APP="$1"
ROOT=<root>
G="graphs/$APP"
mkdir -p "$G"
CDIRS=$(python3 -I -c "
import json,sys,os
b='$ROOT/final_java_only/$APP/app'
d=json.load(open(b+'/class_files.json'))
(k,v),=d.items()
print('\n'.join(os.path.join(b,p) for p in v['classfiles']))
")
ARGS=()
while IFS= read -r line; do ARGS+=("$line"); done <<< "$CDIRS"
python3 -I tools/list_methods.py "${ARGS[@]}" --exclude JacocoInstrument --exclude '/R$' --exclude BuildConfig \
  --jacoco "$ROOT/final_java_only/$APP/combined/report/report.xml" --json "$G/method_list.json" 2> "$G/.list_methods.log" >/dev/null
head -1 "$G/.list_methods.log"
python3 -I tools/coverage_methods.py "$ROOT/final_java_only/$APP" --json "$G/coverage_baseline.json" > /dev/null
python3 -I tools/extract_calls.py "$G" "${ARGS[@]}"
