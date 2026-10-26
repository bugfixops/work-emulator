"""Flag derived routes whose guards contradict each other (the derived path ignores guards, SCHEMA_V2.md section 4).

Usage (from work/): python3 -I tools/check_routes.py <App> [--all]
For every REACHABLE method it walks the best route (methods.csv route_edge_ids) and looks for a step whose guard or ENV gate contradicts an
earlier step of the same route: a RESULT_CANCELED step followed by a RESULT_OK guard, histMap == null followed by histMap != null
(unless the download completes in between), network off followed by network on. It is a heuristic over the guard text:
a hit is a route to read by hand (tools/show_route.py), not proof of an error. Prints one line per flagged method, or all with --all.
"""
import csv
import glob
import json
import re
import sys

PAIRS = [
    ('result', r'RESULT_CANCELED|Cancel tapped|Back closes the picker', r'RESULT_OK|Select tapped|resultCode == RESULT_OK|DISPLAY_MODE: setResult\(RESULT_OK'),
    ('histMap', r'histMap == null', r'histMap != null|history loaded'),
    ('network', r'network off|not \(network connected|not allowed by the Wi-Fi only', r'network connected|ECB download succeeds'),
]
DOWNLOAD_DONE = 'ECB download succeeds'   # an edge with this ENV gate is the download completing, which turns histMap == null into loaded


def text(x, keys):
    return ' '.join(str(x.get(k) or '') for k in keys)


def main(argv):
    app = argv[1]
    g = json.load(open(glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]))
    edges = {x['id']: x for x in g['edges']}
    flagged = 0
    for r in csv.DictReader(open('graphs/%s/out/methods.csv' % app, encoding='utf-8')):
        if r['verdict'] != 'REACHABLE':
            continue
        route = [edges[i] for i in r['route_edge_ids'].split()]
        hits = []
        for name, first, second in PAIRS:
            for i, a in enumerate(route):
                ta = text(a, ('trigger', 'guard', 'env'))
                if not re.search(first, ta):
                    continue
                for j, b in enumerate(route[i + 1:], i + 1):
                    tb = text(b, ('guard', 'env'))
                    if name == 'histMap' and any(DOWNLOAD_DONE in (e.get('env') or '') for e in route[i:j + 1]):
                        continue
                    if re.search(second, tb) and not re.search(first, tb):
                        hits.append('%s: %s [%s] then %s [%s]' % (name, a['id'], (a['guard'] or a['trigger'])[:40], b['id'], (b['guard'] or b['env'] or '')[:40]))
                        break
        if hits or '--all' in argv:
            flagged += bool(hits)
            print('%s %s' % (r['method'], '; '.join(hits[:3])))
    print('# %s: %d routes flagged' % (app, flagged))


if __name__ == '__main__':
    main(sys.argv)
