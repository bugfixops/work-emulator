import sys
sys.path.insert(0, 'tools')
import show_route
app = sys.argv[1]
idx = show_route.source_index(app)
fl = show_route.built_flavors(app)
for spec in sys.argv[2:]:
    f, rng = spec.split(':')
    a, _, b = rng.partition('-')
    a = int(a); b = int(b or a)
    p = show_route.find(idx, f, fl)
    if not p:
        print('NOFILE', f); continue
    L = open(p, encoding='utf-8', errors='replace').read().split('\n')
    print('=== %s:%d-%d' % (f, a, b))
    for i in range(a, min(b, len(L)) + 1):
        print('%4d %s' % (i, L[i-1][:150]))
