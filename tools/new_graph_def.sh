#!/bin/bash
# Write the stub graph_def.py of a generated app (does not overwrite an existing one).
# Usage (from work/): tools/new_graph_def.sh <App> "<Title>"
APP="$1"; TITLE="$2"
F="graphs/$APP/graph_def.py"
[ -e "$F" ] && { echo "$F exists"; exit 1; }
cat > "$F" <<PY
# $TITLE
# Generated part: tools/gen_edges.py derives entry points, lifecycle, callbacks, lambdas, intents, XML-instantiated classes
# from the bytecode, AndroidManifest.xml and res/ XML (see its docstring). Direct app->app calls come from
# tools/extract_calls.py. Everything below gen_edges.apply() is hand-written refinement for this app.
# Rebuild: python3 -I tools/build_graph.py graphs/$APP <prefix>

TITLE = '$TITLE'
USE_AUTO = True
PREFER_SETUP_OVER_ENV = True
AUTO_DEAD = ('Generated graph: no route found. Nothing in the app calls it and no entry point (manifest component, lifecycle or '
             'UI callback of a constructed class, lambda, XML reference, class literal, intent action) leads to it. '
             'Probably unused code; entries through reflection, JNI or code generators are not modelled.')

import sys
sys.path.insert(0, TOOLS)
import gen_edges

CFG = {
    'GROUPS': [],           # [(regex on node name, 'needs'|'env'|'guard', text)]
    'STATIC_ADAPTERS': [],  # adapters whose rows exist without user data
}

gen_edges.apply(globals(), GDIR, '$APP', CFG)

# ------------------------------------------------------------------ hand-written refinement
PY
echo "wrote $F"
