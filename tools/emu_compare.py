"""Compare an emulator run (results of the work-emulator repo) with the trigger graphs and the baseline coverage.

Usage (from work/): python3 -I tools/emu_compare.py <run_dir> [<out_dir>]
<run_dir> holds one folder per app with methods_hit.csv and meta.json (the runs/<id>-<attempt> folder of the results branch).
Per app it reports, with the methods of the graph as the universe:
  hit / baseline   methods this run hit and methods the baseline Monkey run hit (same tool and seed, but random traces differ)
  overlap          share of the baseline-hit methods that this run hit too (harness check, Q5)
  contradictions   methods this run hit that the graph calls DEAD or FRAMEWORK_ONLY (a hit refutes the graph, Q1)
  new              methods this run hit that neither baseline run (Monkey, APE) hit: new dynamic evidence, split by verdict
Writes <out_dir>/SUMMARY.md, summary.json and <App>_{new_hits,contradictions,missed}.csv (default out_dir: <run_dir>/analysis).
"""
import collections
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_graph  # noqa: E402  (method naming must be the one that made methods.csv)

DEAD = ('DEAD', 'FRAMEWORK_ONLY')


def analyse(app, run_dir, out_dir):
    gdir = os.path.join('graphs', app)
    rows = json.load(open(os.path.join(gdir, 'method_list.json')))
    names, _ = build_graph.method_names(rows)
    info = {r['method']: r for r in csv.DictReader(open(os.path.join(gdir, 'out', 'methods.csv'), encoding='utf-8'))}
    base = {(c['class'], c['short'], c['desc']): c for c in json.load(open(os.path.join(gdir, 'coverage_baseline.json')))}
    ci = {}
    with open(os.path.join(run_dir, app, 'methods_hit.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            ci[(r['class'], r['method'], r['desc'])] = r['hit'] == '1'
    meta = json.load(open(os.path.join(run_dir, app, 'meta.json')))
    hit, b_monkey, b_any, both, new, bad, missed, absent = set(), set(), set(), set(), [], [], [], 0
    for name, row in zip(names, rows):
        k = (row['class'], row['name'], row['desc'])
        if k not in ci:
            absent += 1
        h = ci.get(k, False)
        b = base.get((row['class'], row['short'], row['desc']), {})
        bm, ba = bool(b.get('monkey')), bool(b.get('monkey') or b.get('ape'))
        if h:
            hit.add(name)
        if bm:
            b_monkey.add(name)
        if ba:
            b_any.add(name)
        verdict = (info.get(name) or {}).get('verdict', '?')
        if h and bm:
            both.add(name)
        if h and not ba:
            new.append(name)
        if h and verdict in DEAD:
            bad.append(name)
        if bm and not h:
            missed.append(name)

    def dump(suffix, items, extra=()):
        with open(os.path.join(out_dir, '%s_%s.csv' % (app, suffix)), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['method', 'verdict', 'steps_from_launch', 'note'] + list(extra))
            for m in items:
                r = info.get(m) or {}
                w.writerow([m, r.get('verdict', '?'), r.get('steps_from_launch', ''), r.get('note', '')])

    dump('new_hits', sorted(new))
    dump('contradictions', sorted(bad))
    dump('missed', sorted(missed))
    by_verdict = collections.Counter((info.get(m) or {}).get('verdict', '?') for m in new)
    return {'app': app, 'status': meta.get('status'), 'minutes': meta.get('minutes'), 'methods': len(rows), 'ci_hit': len(hit),
            'baseline_monkey_hit': len(b_monkey), 'both': len(both), 'overlap_pct': round(100.0 * len(both) / len(b_monkey), 1) if b_monkey else None,
            'ci_only_vs_monkey': len(hit - b_monkey), 'new_vs_monkey_and_ape': len(new), 'new_by_verdict': dict(by_verdict),
            'contradictions': len(bad), 'baseline_missed': len(missed), 'graph_methods_not_in_report': absent,
            'events': meta.get('events_injected') or meta.get('events_estimated'), 'crashes': meta.get('crashes'), 'anrs': meta.get('anrs')}


def main(argv):
    run_dir = argv[1]
    out_dir = argv[2] if len(argv) > 2 else os.path.join(run_dir, 'analysis')
    os.makedirs(out_dir, exist_ok=True)
    apps = sorted(d for d in os.listdir(run_dir) if os.path.isfile(os.path.join(run_dir, d, 'methods_hit.csv')))
    res = [analyse(a, run_dir, out_dir) for a in apps]
    lines = ['# Emulator run vs graphs and baseline', '',
             '| App | Status | Min | Graph methods | Run hit | Baseline Monkey hit | Overlap | Run only | New (no baseline) | Contradictions | Events | Crashes |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in res:
        lines.append('| %s | %s | %s | %d | %d | %d | %s%% | %d | %d | %d | %s | %s |' % (
            r['app'], r['status'], r['minutes'], r['methods'], r['ci_hit'], r['baseline_monkey_hit'], r['overlap_pct'], r['ci_only_vs_monkey'],
            r['new_vs_monkey_and_ape'], r['contradictions'], r['events'], r['crashes']))
    tot = collections.Counter()
    for r in res:
        for k in ('methods', 'ci_hit', 'baseline_monkey_hit', 'both', 'ci_only_vs_monkey', 'new_vs_monkey_and_ape', 'contradictions'):
            tot[k] += r[k]
    lines.append('| **Total** | | | %d | %d | %d | %.1f%% | %d | %d | %d | | |' % (
        tot['methods'], tot['ci_hit'], tot['baseline_monkey_hit'], 100.0 * tot['both'] / max(1, tot['baseline_monkey_hit']),
        tot['ci_only_vs_monkey'], tot['new_vs_monkey_and_ape'], tot['contradictions']))
    lines += ['', 'New hits by graph verdict (methods hit now that neither baseline run hit):', '']
    for r in res:
        lines.append('- %s: %s' % (r['app'], ', '.join('%s %d' % kv for kv in sorted(r['new_by_verdict'].items())) or 'none'))
    text = '\n'.join(lines) + '\n'
    open(os.path.join(out_dir, 'SUMMARY.md'), 'w', encoding='utf-8').write(text)
    json.dump(res, open(os.path.join(out_dir, 'summary.json'), 'w'), indent=1)
    sys.stdout.write(text)


if __name__ == '__main__':
    main(sys.argv)
