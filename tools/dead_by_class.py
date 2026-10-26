"""List DEAD methods of a generated graph grouped by class.
Usage: python3 -I dead_by_class.py <App> [N]   (reads graphs/<App>/out/methods.csv; run from work/)"""
import csv, collections, sys
rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % sys.argv[1])))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
by = collections.defaultdict(list); tot = collections.Counter()
for r in rows:
    c = r['method'].rsplit('.', 1)[0] if '(' not in r['method'].split('.')[-1] else r['method'].rsplit('.', 1)[0]
    c = r['method'].split('(')[0].rsplit('.', 1)[0]
    tot[c] += 1
    if r['verdict'] == 'DEAD':
        by[c].append(r['method'].split('(')[0].rsplit('.', 1)[1])
print('DEAD %d of %d' % (sum(len(v) for v in by.values()), len(rows)))
for c, ms in sorted(by.items(), key=lambda kv: -len(kv[1]))[:n]:
    print('%3d/%-3d %s | %s' % (len(ms), tot[c], c, ', '.join(ms[:7])))
