"""Run the generator on the five hand-written apps and compare with the hand-written verdicts (tools/tests/_t_<App>/).
Writes tools/tests/calibration.json and prints a table. Usage (from work/): python3 -I tools/calibrate.py [--rebuild-inputs]
The test folders hold copies of method_list.json / coverage_baseline.json of graphs/<App> and a stub graph_def.py that only
calls gen_edges.apply(); auto_calls.json is regenerated with the current tools/extract_calls.py when missing or --rebuild-inputs."""
import collections, glob, json, os, subprocess, sys

APPS = [('Currency', 'currency'), ('Diary', 'diary'), ('hash-checker', 'hash-checker'), ('openlauncher', 'openlauncher'), ('Omni-Notes', 'Omni-Notes')]
ROOT = '<root>'
STUB = '''TITLE = '%s generated (calibration run)'
USE_AUTO = True
PREFER_SETUP_OVER_ENV = True
AUTO_DEAD = 'No route found by the generator'
import sys
sys.path.insert(0, TOOLS)
import gen_edges
gen_edges.apply(globals(), GDIR, '%s', {})
'''
res = {}
for app, pfx in APPS:
    d = 'tools/tests/_t_%s' % app
    os.makedirs(d, exist_ok=True)
    for f in ('method_list.json', 'coverage_baseline.json'):
        subprocess.run(['cp', 'graphs/%s/%s' % (app, f), d])
    if '--rebuild-inputs' in sys.argv or not os.path.exists(d + '/auto_calls.json'):
        b = '%s/final_java_only/%s/app' % (ROOT, app)
        (k, v), = json.load(open(b + '/class_files.json')).items()
        subprocess.run(['python3', '-I', 'tools/extract_calls.py', d] + [os.path.join(b, p) for p in v['classfiles']], capture_output=True)
    open(d + '/graph_def.py', 'w').write(STUB % (app, app))
    out = subprocess.run(['python3', '-I', 'tools/build_graph.py', d, 't'], capture_output=True, text=True).stdout
    a = json.load(open('graphs/%s/out/%s_trigger_graph.json' % (app, pfx)))['verdict']
    b = json.load(open('%s/out/t_trigger_graph.json' % d))['verdict']
    common = [m for m in a if m in b]
    dead = lambda x: x in ('DEAD', 'FRAMEWORK_ONLY')
    n = len(common)
    res[app] = {'methods': n,
                'dead_vs_alive': round(100.0 * sum(1 for m in common if dead(a[m]) == dead(b[m])) / n, 1),
                'exact': round(100.0 * sum(1 for m in common if a[m] == b[m]) / n, 1),
                'contradictions': int(next((l.split(' DEAD')[0].split()[-1] for l in out.split('\n') if 'contradictions' in l), -1))}
json.dump(res, open('tools/tests/calibration.json', 'w'), indent=1)
print('%-14s %8s %14s %8s %14s' % ('app', 'methods', 'dead-vs-alive', 'exact', 'contradictions'))
for app, r in res.items():
    print('%-14s %8d %13.1f%% %7.1f%% %14d' % (app, r['methods'], r['dead_vs_alive'], r['exact'], r['contradictions']))
