import csv, glob, json, re, sys
sys.path.insert(0, 'tools')
import show_route
app = sys.argv[1]
g = json.load(open(glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]))
E = {x['id']: x for x in g['edges']}
rows = {r['method']: r for r in csv.DictReader(open('graphs/%s/out/methods.csv' % app, encoding='utf-8'))}
idx = show_route.source_index(app)
fl = show_route.built_flavors(app)
cache = {}
CTRL = re.compile(r'^\s*(\}\s*)?(else\b|if\s*\(|for\s*\(|while\s*\(|do\b|switch\s*\(|case\b|default:|try\b|catch\b|synchronized)|\?\s*$|->\s*\{\s*$')
DECL = re.compile(r'^\s*(public|private|protected|static|final|abstract|@Override|void|[A-Za-z_<>\[\],. ]+)\s+[A-Za-z_$][\w$]*\s*\([^;]*\)\s*(throws [\w., ]+)?\s*\{\s*$')


def lines_of(fname):
    p = show_route.find(idx, fname, fl)
    if not p:
        return None
    if p not in cache:
        cache[p] = open(p, encoding='utf-8', errors='replace').read().split('\n')
    return cache[p]


def guards(fname, n):
    L = lines_of(fname)
    if not L or not (1 <= n <= len(L)):
        return []
    ind = lambda s: len(s) - len(s.lstrip())
    cur = ind(L[n - 1])
    out = []
    i = n - 2
    while i >= 0:
        s = L[i]
        if not s.strip() or s.strip().startswith(('//', '*', '/*')):
            i -= 1
            continue
        if ind(s) < cur:
            t = s.strip()
            if DECL.match(s) or re.match(r'^\s*(public|private|protected)\b', s):
                break
            if CTRL.search(s):
                txt = '%d: %s' % (i + 1, t[:90])
                if re.match(r'^\}?\s*else\b', t) and not re.match(r'^\}?\s*else\s+if', t):
                    # pair the else with the if of the same indent
                    for j in range(i - 1, -1, -1):
                        u = L[j]
                        if u.strip() and ind(u) == ind(s) and re.match(r'^\s*(\}\s*else\s+)?if\s*\(', u) and not re.match(r'^\s*\}\s*else', u):
                            txt = '%d: NOT(%s) %s' % (j + 1, L[j].strip()[:80], '')
                            break
                out.append(txt)
            cur = ind(s)
        i -= 1
    return list(reversed(out))


seen = set()
for m in sys.argv[2:]:
    r = rows.get(m)
    if not r:
        print('MISSING', m); continue
    print('##', m, r['verdict'], 'env=', r['env_kinds'] or '-', 'state=', r['state_kinds'] or '-', 'steps=', len(r['route_edge_ids'].split()))
    for i, eid in enumerate(r['route_edge_ids'].split(), 1):
        x = E[eid]
        if eid in seen:
            continue
        seen.add(eid)
        extra = []
        if x['guard']: extra.append('G:' + x['guard'][:60])
        if x['env']: extra.append('ENV:' + x['env'][:50])
        if x['needs_state']: extra.append('ST:' + x['needs_state'][:60])
        print('  %2d %s/%s %s -> %s | %s %s | %s' % (i, x['kind'], x['edge_class'][:3], x['src'][:46], x['dst'][:46], x['trigger'][:60], ' '.join(extra), x['evidence'][:75].replace('\n', ' ')))
        mm = re.search(r'SRC ([\w./$-]+\.java):(\d+)(?:-\d+)? \(bytecode', x['evidence'] or '')
        if mm:
            gs = guards(mm.group(1), int(mm.group(2)))
            if gs:
                print('        in: ' + ' || '.join(gs))
