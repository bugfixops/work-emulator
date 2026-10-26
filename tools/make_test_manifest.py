"""Build the emulator test manifests: what to test for every app, with the expected outcome for each target.

Usage (from work/): python3 -I tools/make_test_manifest.py
Reads graphs/<App>/out/<prefix>_trigger_graph.json and methods.csv (verdicts, paths, baseline hits) and writes
  emulator_tests/<App>/targets.csv    one row per target method
  emulator_tests/SUMMARY.md           counts per app and category
Categories (expected = what the graph predicts when the emulator is run):
  CONTROL_HIT    the baseline ran it            -> HIT   (checks that the new harness reproduces the baseline)
  FRONTIER       first never-run node behind which many never-run methods sit (where the baseline stopped) -> HIT after crossing it
  CLEAN_SAMPLE   reachable, no setup, no env, never run   -> HIT when the path is followed
  SETUP_SAMPLE   reachable after setup, never run         -> HIT with the setup, NOT_HIT without it
  ENV_ENTRY      edge gated by another app / adb / the system that adb can inject (am start, am broadcast) -> HIT when injected
  ENV_SAMPLE     reachable only through another environment gate (network, picker, root, hardware) -> UNKNOWN (record what happens)
  DEAD_SAMPLE    graph says DEAD / FRAMEWORK_ONLY         -> NOT_HIT (any hit is a contradiction)
Every run also checks ALL dead methods passively (a hit on any of them is a contradiction).
Random samples use a fixed seed, so the manifest is reproducible.
"""
import collections
import csv
import glob
import json
import os
import random
import re

SEED = 20261025
APPS = [('Currency', 'hand'), ('Diary', 'hand'), ('hash-checker', 'hand'), ('openlauncher', 'hand'), ('Omni-Notes', 'hand'),
        ('Vanilla-Music', 'generated'), ('AnyMemo', 'generated'), ('Markor', 'generated'), ('Aegis', 'generated'),
        ('AmazeFileManager', 'generated'), ('AnkiDroid', 'generated'), ('MMEX', 'generated'), ('LibreTorrent', 'generated')]
N_FRONTIER, N_CONTROL, N_CLEAN, N_SETUP, N_ENV, N_DEAD = 10, 10, 20, 10, 10, 20


def base(n):
    return n.split('@')[0]


def frontier_nodes(rows, edges, hit):
    """{first never-run node: (count of never-run clean methods behind it, example chain info, [dependents])}"""
    out = collections.defaultdict(list)
    nodes = set()
    for x in edges:
        out[x['src']].append(x)
        nodes.add(x['src'])
        nodes.add(x['dst'])
    prev, dq = {}, collections.deque()
    for n in sorted(nodes):
        if not n.startswith('S_') and base(n) in hit:
            prev[n] = None
            dq.append(n)
    while dq:
        n = dq.popleft()
        for x in out.get(n, []):
            if x['kind'] == 'REGISTER' or x['dst'] in prev:
                continue
            prev[x['dst']] = x
            dq.append(x['dst'])
    first = {}
    for n in prev:
        first.setdefault(base(n), n)
    res = collections.defaultdict(lambda: {'n': 0, 'dep': [], 'edge': None})
    for r in rows:
        m = r['method']
        if r['verdict'] != 'REACHABLE' or m in hit or r['monkey_hit'] == '' or 'needs environment' in (r['note'] or '') or m not in first:
            continue
        chain, n = [], first[m]
        while prev.get(n):
            chain.append(prev[n])
            n = prev[n]['src']
        chain.reverse()
        k = next((i for i, x in enumerate(chain) if not x['dst'].startswith('S_') and base(x['dst']) not in hit), None)
        if k is None:
            continue
        fx = chain[k]
        key = base(fx['dst'])
        d = res[key]
        d['n'] += 1
        if len(d['dep']) < 5 and m != key:
            d['dep'].append(m)
        d['edge'] = (base(fx['src']), fx['kind'], (fx['evidence'] or '').split(';')[0])
    return res


def main():
    rng = random.Random(SEED)
    os.makedirs('emulator_tests', exist_ok=True)
    summary = []
    for app, how in APPS:
        jp = glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]
        g = json.load(open(jp))
        rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % app)))
        by = {r['method']: r for r in rows}
        hit = {r['method'] for r in rows if r['monkey_hit'] == '1' or r['ape_hit'] == '1'}
        observable = [r for r in rows if r['monkey_hit'] != '']
        targets = []

        def add(cat, m, expected, extra=None):
            r = by[m]
            note = r['note'] or ''
            setup = '; '.join(re.findall(r'needs earlier setup: ([^|]*)', note))
            env = '; '.join(re.findall(r'needs environment: ([^|]*)', note))
            row = {'category': cat, 'method': m, 'verdict': r['verdict'], 'expected': expected,
                   'baseline_hit': 1 if m in hit else 0, 'steps_from_launch': r['steps_from_launch'],
                   'taps': r['gui_steps_on_shortest_path'], 'path': r['shortest_path'], 'setup_needed': setup, 'env_needed': env,
                   'extra': extra or ''}
            targets.append(row)

        # frontier
        fr = frontier_nodes(rows, g['edges'], hit)
        top = sorted(fr.items(), key=lambda kv: -kv[1]['n'])[:N_FRONTIER]
        used = set()
        for node, d in top:
            if node in by:
                used.add(node)
                add('FRONTIER', node, 'HIT', 'behind it: %d never-run methods; entered from %s by %s (%s); examples: %s' % (
                    d['n'], d['edge'][0], d['edge'][1], d['edge'][2], ', '.join(d['dep'][:4])))
        # controls
        ctl = [r['method'] for r in observable if r['method'] in hit and r['steps_from_launch'] and int(r['steps_from_launch']) >= 3 and r['verdict'] == 'REACHABLE']
        for m in rng.sample(ctl, min(N_CONTROL, len(ctl))):
            add('CONTROL_HIT', m, 'HIT')
        # clean never run
        clean = [r['method'] for r in observable if r['verdict'] == 'REACHABLE' and r['method'] not in hit and r['method'] not in used and 'needs environment' not in (r['note'] or '')]
        for m in rng.sample(clean, min(N_CLEAN, len(clean))):
            add('CLEAN_SAMPLE', m, 'HIT')
        # setup
        setup = [r['method'] for r in observable if r['verdict'] == 'REACHABLE_AFTER_SETUP' and r['method'] not in hit and 'needs environment' not in (r['note'] or '')]
        for m in rng.sample(setup, min(N_SETUP, len(setup))):
            add('SETUP_SAMPLE', m, 'HIT with setup; NOT_HIT without it')
        # env entries that adb can inject
        inj = {}
        for x in g['edges']:
            e = x.get('env') or ''
            if e and x['kind'] in ('ENTRY', 'INTENT', 'FRAMEWORK', 'CALL') and re.search(r'another app|adb|system sends|incoming|share|launch intent|intent', e, re.I) and base(x['dst']) in by:
                inj.setdefault(base(x['dst']), (x['src'], x['kind'], e[:140]))
        inj_list = [m for m in inj if by[m]['verdict'].startswith('REACHABLE')]
        for m in rng.sample(inj_list, min(N_ENV, len(inj_list))):
            add('ENV_ENTRY', m, 'HIT when injected (am start / am broadcast)', 'gate on %s via %s: %s' % inj[m])
        # other env
        envm = [r['method'] for r in observable if r['verdict'].startswith('REACHABLE') and 'needs environment' in (r['note'] or '') and r['method'] not in inj and r['method'] not in hit]
        for m in rng.sample(envm, min(N_ENV, len(envm))):
            add('ENV_SAMPLE', m, 'UNKNOWN (record what happens)')
        # dead
        dead = [r['method'] for r in rows if r['verdict'] in ('DEAD', 'FRAMEWORK_ONLY') and not r['method'].startswith('S_')]
        for m in rng.sample(dead, min(N_DEAD, len(dead))):
            add('DEAD_SAMPLE', m, 'NOT_HIT')
        os.makedirs('emulator_tests/%s' % app, exist_ok=True)
        with open('emulator_tests/%s/targets.csv' % app, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            cols = ['id', 'category', 'method', 'verdict', 'expected', 'baseline_hit', 'steps_from_launch', 'taps', 'setup_needed', 'env_needed', 'extra', 'path']
            w.writerow(cols)
            for i, t in enumerate(targets, 1):
                t['id'] = '%s-%03d' % (app, i)
                w.writerow([t[c] for c in cols])
        cnt = collections.Counter(t['category'] for t in targets)
        summary.append((app, how, len(rows), len(hit), sum(1 for r in rows if r['verdict'] in ('DEAD', 'FRAMEWORK_ONLY')), cnt, len(targets), len(fr)))
    cats = ['CONTROL_HIT', 'FRONTIER', 'CLEAN_SAMPLE', 'SETUP_SAMPLE', 'ENV_ENTRY', 'ENV_SAMPLE', 'DEAD_SAMPLE']
    lines = ['# Emulator test targets (generated by tools/make_test_manifest.py)', '',
             '| App | Methods | Baseline-run | Dead (all checked passively) | ' + ' | '.join(cats) + ' | Targets |',
             '|---|---:|---:|---:|' + '---:|' * len(cats) + '---:|']
    tot = collections.Counter()
    for app, how, n, h, d, cnt, nt, nf in summary:
        lines.append('| %s | %d | %d | %d | %s | %d |' % (app, n, h, d, ' | '.join(str(cnt[c]) for c in cats), nt))
        tot.update(cnt)
    lines.append('| **Total** | | | | %s | %d |' % (' | '.join(str(tot[c]) for c in cats), sum(tot.values())))
    open('emulator_tests/SUMMARY.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
