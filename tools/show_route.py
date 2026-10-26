"""Print the best route of methods with the source lines every step cites (to read a path against the source).

Usage (from work/): python3 -I tools/show_route.py <App> <method> [<method> ...] [--max N] [--dedupe]
Needs a schema 2 build (graphs/<App>/out/methods.csv with route_edge_ids). For each method: the label, then every edge of the route
with kind, class, gates, guard and the lines of its evidence (`SRC File.java:12-30`) taken from the app's source tree.
--max N: print at most N lines per snippet (default 14). --dedupe: an edge already printed for an earlier method is listed in one line.
"""
import csv
import glob
import json
import os
import re
import sys

SRC_ROOT = 'final_java_only'
FLAVORS = ()


def source_index(app):
    idx = {}
    for root in glob.glob('%s/%s/app/*/' % (SRC_ROOT, app)):
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in ('build', 'test', 'androidTest', '.git')]
            if 'JacocoInstrument' in dp:
                continue
            for f in fn:
                if f.endswith(('.java', '.xml', '.kt')):
                    idx.setdefault(f, []).append(os.path.join(dp, f))
    return idx


def built_flavors(app):
    """Flavors the dataset APK was built from: the folders app/build/intermediates/javac/<flavor>Debug of the source tree."""
    out = set()
    for d in glob.glob('%s/%s/app/*/app/build/intermediates/javac/*Debug' % (SRC_ROOT, app)):
        out.add(os.path.basename(d)[:-len('Debug')])
    return out


def find(idx, name, flavors=()):
    cands = idx.get(os.path.basename(name), [])
    if '/' in name:
        tail = [c for c in cands if c.endswith(name)]
        cands = tail or cands
    # the same file name can exist in several flavor folders: take src/main or the flavor that was built, never another flavor
    cands = sorted(cands, key=lambda c: (not ('/src/main/' in c or any('/src/%s/' % f in c for f in flavors)), len(c)))
    return cands[0] if cands else None


def snippet(idx, ref, cap, flavors=()):
    """ref: 'File.java:12-30,45' -> printed lines"""
    m = re.match(r'(.+?):([0-9][0-9,\-]*)$', ref)
    if not m:
        return ['      (%s: no line numbers)' % ref]
    path = find(idx, m.group(1), flavors)
    if not path:
        return ['      (%s not found in the source tree)' % m.group(1)]
    lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    out = []
    for seg in m.group(2).split(','):
        a, _, b = seg.partition('-')
        a, b = int(a), int(b or a)
        for n in range(a, min(b, a + cap - 1) + 1):
            if 1 <= n <= len(lines):
                out.append('      %5d  %s' % (n, lines[n - 1].rstrip()[:170]))
        if b - a + 1 > cap:
            out.append('      ...  (%d more lines)' % (b - a + 1 - cap))
    return out


def main(argv):
    app = argv[1]
    global FLAVORS
    FLAVORS = built_flavors(app)
    cap = int(argv[argv.index('--max') + 1]) if '--max' in argv else 14
    dedupe = '--dedupe' in argv
    names = [a for i, a in enumerate(argv[2:], 2) if a not in ('--max', '--dedupe') and argv[i - 1] != '--max']
    seen = set()
    jp = glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]
    g = json.load(open(jp))
    edges = {x['id']: x for x in g['edges']}
    rows = {r['method']: r for r in csv.DictReader(open('graphs/%s/out/methods.csv' % app, encoding='utf-8'))}
    idx = source_index(app)
    for m in names:
        r = rows.get(m)
        if not r:
            print('## %s: no such method' % m)
            continue
        lab = g['labels'][m]
        print('## %s  %s  confirmed_by=%s path=%s' % (m, r['verdict'], lab['confirmed_by'], lab['path_status']))
        if r['verdict'] == 'UNREACHABLE':
            print('   %s: %s  [%s]' % (lab['unreachable']['kind'], lab['unreachable']['text'], lab['source_ref']))
            continue
        print('   env=%s state=%s classes=%s explicit_standard_route=%s' % (r['env_kinds'] or '-', r['state_kinds'] or '-', r['route_edge_classes'], r['explicit_standard_route']))
        for i, eid in enumerate(r['route_edge_ids'].split(), 1):
            x = edges[eid]
            if dedupe and eid in seen:
                print('  %2d. %s %s -> %s  (printed above)' % (i, eid, x['src'], x['dst']))
                continue
            seen.add(eid)
            gates = ''.join(' [ENV: %s]' % x['env'] for _ in [0] if x.get('env')) + ''.join(' [STATE: %s]' % x['needs_state'] for _ in [0] if x.get('needs_state'))
            print('  %2d. %s %s/%s%s%s\n      %s -> %s\n      %s' % (i, eid, x['kind'], x['edge_class'] + ('(' + x['via'] + ')' if x.get('via') else '') + ('*' if x.get('class_basis') == 'default' else ''),
                                                                 '', gates, x['src'], x['dst'], x['trigger']))
            if x.get('guard'):
                print('      guard: %s' % x['guard'])
            if x.get('note'):
                print('      note: %s' % x['note'])
            print('      evidence: %s' % x['evidence'])
            for seg in re.findall(r'(?:FW-)?SRC\s+([^\s;]+(?:\s*\([^)]*\))?)', x['evidence'] or ''):
                ref = seg.split(' (')[0]
                for line in snippet(idx, ref, cap, FLAVORS):
                    print(line)
        print()


if __name__ == '__main__':
    main(sys.argv)
