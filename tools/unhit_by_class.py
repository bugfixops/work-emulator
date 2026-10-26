"""Reachable-without-setup methods that neither APE nor Monkey ran, grouped by class (the paper's target list).
Usage: python3 -I unhit_by_class.py <App> [N] [--setup]   (--setup: the after-setup ones instead)"""
import csv, collections, sys
rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % sys.argv[1])))
n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 40
want = 'REACHABLE_AFTER_SETUP' if '--setup' in sys.argv else 'REACHABLE'
by = collections.defaultdict(list)
tot = collections.Counter()
for r in rows:
    c = r['method'].split('(')[0].rsplit('.', 1)[0]
    tot[c] += 1
    if r['monkey_hit'] == '' : continue
    if r['verdict'] == want and r['monkey_hit'] != '1' and r['ape_hit'] != '1' and 'needs environment' not in (r['note'] or ''):
        by[c].append(r['method'].split('(')[0].rsplit('.', 1)[1] + ('' if not r['gui_steps_on_shortest_path'] else ''))
print('%s unhit: %d' % (want, sum(len(v) for v in by.values())))
for c, ms in sorted(by.items(), key=lambda kv: -len(kv[1]))[:n]:
    print('%3d/%-3d %s | %s' % (len(ms), tot[c], c, ', '.join(ms[:8])))
