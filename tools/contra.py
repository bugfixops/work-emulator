"""Group the baseline contradictions of /tmp/_b_<App>.txt by class (first line of each group shows one method).
Usage: python3 -I contra.py <App> [N]"""
import collections, re, sys
txt = open('/tmp/_b_%s.txt' % sys.argv[1]).read()
c = collections.Counter(); ex = collections.defaultdict(list)
for m in re.finditer(r'CONTRADICTION: (\S+) is', txt):
    cls = m.group(1).rsplit('.', 1)[0]
    c[cls] += 1
    ex[cls].append(m.group(1).rsplit('.', 1)[1])
for k, v in c.most_common(int(sys.argv[2]) if len(sys.argv) > 2 else 30):
    print(v, k, '|', ', '.join(ex[k][:5]))
