"""Pick a stratified sample of REACHABLE methods whose best routes are to be verified against the source (SCHEMA_V2.md, section 4).

Usage (from work/): python3 -I tools/verify_sample.py <App> [N] [seed]
Strata (a method may belong to several): ENV gate, STATE gate, a non_standard edge on the route, a label confirmed only by inference,
a long route (12 or more steps), and the rest (PLAIN). Each stratum gets a quota; inside a stratum the method that adds the most edges
not yet covered by the sample comes first, ties are broken by the seed, so the sample is reproducible and spreads over many edges.
Prints one line per picked method: stratum, steps, number of new edges.
"""
import csv
import random
import sys

QUOTA = [('NONSTD', 4), ('INFERRED', 4), ('STATE', 3), ('ENV', 6), ('LONG', 6), ('PLAIN', 7)]


def strata(r):
    s = []
    if r['env_kinds']:
        s.append('ENV')
    if r['state_kinds']:
        s.append('STATE')
    if 'non_standard' in r['route_edge_classes']:
        s.append('NONSTD')
    if r['confirmed_by'] == 'INFERRED':
        s.append('INFERRED')
    if int(r['steps_from_launch'] or 0) >= 12:
        s.append('LONG')
    return s or ['PLAIN']


def main(argv):
    app = argv[1]
    n = int(argv[2]) if len(argv) > 2 else 30
    seed = int(argv[3]) if len(argv) > 3 else 20261025
    rng = random.Random(seed)
    rows = [r for r in csv.DictReader(open('graphs/%s/out/methods.csv' % app, encoding='utf-8')) if r['verdict'] == 'REACHABLE']
    rng.shuffle(rows)
    total = sum(q for _, q in QUOTA)
    picked, covered = [], set()
    for name, q in QUOTA:
        q = max(1, round(q * n / total))
        pool = [r for r in rows if name in strata(r) and r not in [p[0] for p in picked]]
        for _ in range(q):
            if not pool:
                break
            pool.sort(key=lambda r: -len(set(r['route_edge_ids'].split()) - covered))
            r = pool.pop(0)
            new = set(r['route_edge_ids'].split()) - covered
            covered |= new
            picked.append((r, name, len(new)))
    print('# %s: %d of %d reachable methods, %d distinct edges on their routes (seed %d)' % (app, len(picked), len(rows), len(covered), seed))
    for r, name, new in picked:
        print('%-9s steps %-3s new edges %-3d %s' % (name, r['steps_from_launch'], new, r['method']))


if __name__ == '__main__':
    main(sys.argv)
