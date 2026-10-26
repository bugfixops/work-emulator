import csv, sys
app = sys.argv[1]
rows = {r['method']: r for r in csv.DictReader(open('graphs/%s/out/methods.csv' % app, encoding='utf-8'))}
for m in sys.argv[2:]:
    r = rows.get(m)
    if not r: print('## MISSING', m); continue
    print('## %s [%s, %s steps] M=%s A=%s' % (m, r['verdict'], r['steps_from_launch'], r['monkey_hit'], r['ape_hit']))
    print('   taps:', r['gui_steps_on_shortest_path'])
    print('   path:', r['shortest_path'][:700])
    if r['note']: print('   note:', r['note'][:200])
