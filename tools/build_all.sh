#!/bin/bash
# Build the given apps and print a one-screen summary each. Usage (from work/): tools/build_all.sh App:prefix ...
for t in "$@"; do
  a=${t%%:*}; p=${t##*:}
  python3 -I tools/build_graph.py graphs/$a $p > /tmp/_b_$a.txt 2>&1
  echo "=== $a: $(grep -E '^methods' /tmp/_b_$a.txt)"
  grep -E '^verdicts|contradictions|^errors|^warnings' /tmp/_b_$a.txt | cut -c1-200
  grep -E "^Traceback|Error" /tmp/_b_$a.txt | head -3
done
