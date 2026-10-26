#!/bin/bash
# Regression check of the generator: run it on the five hand-written apps (tools/tests/_t_*) and print the agreement with the
# hand-written verdicts (also written to tools/tests/calibration.json). It must keep 0 baseline contradictions.
# Usage (from work/): tools/check_gen.sh
cd "$(dirname "$0")/.."
python3 -I tools/calibrate.py
