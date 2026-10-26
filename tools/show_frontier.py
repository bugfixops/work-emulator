"""Show the source around the top frontier edges of a generated graph (where the baseline stopped).
Usage (from work/): python3 -I tools/show_frontier.py <App> [N] [context lines] [start rank]"""
import collections, csv, json, os, re, sys
app = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 7
start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % app)))
base = '<root>/final_java_only/%s/app' % app
(k, v), = json.load(open(base + '/class_files.json')).items()
srcdirs = [os.path.join(base, p) for p in v['sourcefiles'] if not re.search(r'/src/(androidTest|test)/', p)]
files = {}
for sd in srcdirs:
    for dp, _d, fs in os.walk(sd):
        for f in fs:
            if f.endswith('.java'):
                files.setdefault(f, os.path.join(dp, f))
by = collections.defaultdict(list)
for r in rows:
    if r.get('frontier_first_unrun'):
        by[r['frontier_first_unrun']].append(r)
for node, lst in sorted(by.items(), key=lambda kv: -len(kv[1]))[start:start + n]:
    r = lst[0]
    ev = r['frontier_edge_evidence']
    print('=== %s (%d never-run behind) <- %s [%s] %s' % (node, len(lst), r['frontier_from'], r['frontier_edge_kind'], ev))
    m = re.search(r'SRC (\S+?):(\d+)', ev)
    if m and m.group(1) in files:
        ls = open(files[m.group(1)], encoding='utf-8', errors='replace').read().split('\n')
        ln = int(m.group(2))
        for i in range(max(0, ln - ctx - 1), min(len(ls), ln + 2)):
            print('%5d %s %s' % (i + 1, '>' if i + 1 == ln else ' ', ls[i][:150]))
