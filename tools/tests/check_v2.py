"""Equivalence test for build_graph.py schema 2: the old tool (build_graph_v8_backup.py) and the new one must give the same
edges, shortest paths and step counts, and DEAD / FRAMEWORK_ONLY must become UNREACHABLE, REACHABLE_AFTER_SETUP REACHABLE.
Both builds run in temporary copies with the same PYTHONHASHSEED, because the generated graphs break ties between equal
routes by hash order (two builds with different seeds already differ).

Usage (from work/): python3 tools/tests/check_v2.py [App ...]
"""
import csv
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

APPS = ['Currency', 'Diary', 'hash-checker', 'openlauncher', 'Omni-Notes', 'Vanilla-Music', 'AnyMemo', 'Markor', 'Aegis',
        'AmazeFileManager', 'AnkiDroid', 'MMEX', 'LibreTorrent']
MAP = {'REACHABLE': 'REACHABLE', 'REACHABLE_AFTER_SETUP': 'REACHABLE', 'DEAD': 'UNREACHABLE', 'FRAMEWORK_ONLY': 'UNREACHABLE'}
ENV = dict(os.environ, PYTHONHASHSEED='0')


def build(tool, app, prefix):
    tmp = tempfile.mkdtemp(prefix='v2_' + app + '_')
    dst = os.path.join(tmp, app)
    shutil.copytree('graphs/' + app, dst, ignore=shutil.ignore_patterns('out'))
    p = subprocess.run([sys.executable, tool, dst, prefix], capture_output=True, text=True, env=ENV)
    rows = {r['method']: r for r in csv.DictReader(open(os.path.join(dst, 'out', 'methods.csv'), encoding='utf-8'))}
    g = json.load(open(glob.glob(os.path.join(dst, 'out', '*_trigger_graph.json'))[0]))
    return p, rows, g, tmp


def main(argv):
    bad = 0
    for app in argv[1:] or APPS:
        if 'UNREACHABLE = {' in open('graphs/%s/graph_def.py' % app, encoding='utf-8').read():
            print('%-17s converted to schema 2 (graph_def.py has UNREACHABLE): the old tool cannot build it, skipped' % app)
            continue
        prefix = os.path.basename(glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]).replace('_trigger_graph.json', '')
        po, old, go, t1 = build('tools/build_graph_v8_backup.py', app, prefix)
        pn, new, gn, t2 = build('tools/build_graph.py', app, prefix)
        problems = []
        if pn.returncode != po.returncode:
            problems.append('exit code old %d new %d: %s' % (po.returncode, pn.returncode, (pn.stdout + pn.stderr)[-300:]))
        if len(gn['edges']) != len(go['edges']):
            problems.append('edges %d -> %d' % (len(go['edges']), len(gn['edges'])))
        if set(old) != set(new):
            problems.append('method sets differ')
        for m, o in old.items():
            n = new.get(m)
            if not n:
                continue
            if MAP[o['verdict']] != n['verdict']:
                problems.append('%s: verdict %s -> %s' % (m, o['verdict'], n['verdict']))
            if o['shortest_path'] != n['shortest_path'] or o['steps_from_launch'] != n['steps_from_launch']:
                problems.append('%s: path changed' % m)
        ids = [x['id'] for x in gn['edges']]
        if len(set(ids)) != len(ids):
            problems.append('edge ids not unique')
        print('%-17s edges %5d  methods %5d  unreachable %4d  %s' % (app, len(gn['edges']), len(new),
              sum(1 for r in new.values() if r['verdict'] == 'UNREACHABLE'), 'OK' if not problems else 'PROBLEMS'))
        for s in problems[:6]:
            print('    ' + s)
        bad += bool(problems)
        shutil.rmtree(t1, ignore_errors=True)
        shutil.rmtree(t2, ignore_errors=True)
    print('apps with problems:', bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
