"""Nodes that appear on the most shortest paths (hubs = likely shortcuts) and paths without any tap.
Usage: python3 -I hubs.py <App> [N]"""
import csv, collections, sys
rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % sys.argv[1])))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 25
cnt = collections.Counter(); notap = 0; total = 0
for r in rows:
    if not r['verdict'].startswith('REACHABLE') or not r['shortest_path']:
        continue
    total += 1
    nodes = r['shortest_path'].split(' > ')
    for x in nodes[1:-1]:
        cnt[x] += 1
    if not r['gui_steps_on_shortest_path'].strip():
        notap += 1
print('%d reachable with a path; %d have no tap at all' % (total, notap))
for x, c in cnt.most_common(n):
    print('%5d %s' % (c, x))
