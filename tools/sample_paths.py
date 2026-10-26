"""Print N random reachable methods with their taps and path (from graphs/<App>/out/methods.csv).
Usage: python3 -I sample_paths.py <App> <N> [seed] [--unhit] [--min-steps K]"""
import csv, random, sys
app, n = sys.argv[1], int(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 1
rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % app)))
rows = [r for r in rows if r['verdict'].startswith('REACHABLE')]
if '--unhit' in sys.argv:
    rows = [r for r in rows if r['monkey_hit'] != '1' and r['ape_hit'] != '1']
if '--min-steps' in sys.argv:
    k = int(sys.argv[sys.argv.index('--min-steps') + 1])
    rows = [r for r in rows if r['steps_from_launch'] and int(r['steps_from_launch']) >= k]
random.seed(seed)
for r in random.sample(rows, min(n, len(rows))):
    print('%s %s | steps %s' % (r['verdict'][:12], r['method'], r['steps_from_launch']))
    print('    taps:', r['gui_steps_on_shortest_path'][:230])
    print('    path:', ' > '.join(r['shortest_path'].split(' > ')[-9:])[:300])
    if r['note']: print('    note:', r['note'][:160])
