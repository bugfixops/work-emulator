"""One table for all 13 apps, recomputed from graphs/<App>/out/*.json and methods.csv. Prints markdown.
Usage (from work/): python3 -I tools/summary_table.py"""
import csv, collections, glob, json, os
APPS = [('Currency', 'hand'), ('Diary', 'hand (Kiro)'), ('hash-checker', 'hand'), ('openlauncher', 'hand'), ('Omni-Notes', 'hand'),
        ('Vanilla-Music', 'generated'), ('AnyMemo', 'generated'), ('Markor', 'generated'), ('Aegis', 'generated'),
        ('AmazeFileManager', 'generated'), ('AnkiDroid', 'generated'), ('MMEX', 'generated'), ('LibreTorrent', 'generated')]
print('| App | method | methods | pages | edges | reachable | after setup | dead | framework-only | baseline-run | never run: dead / env / setup / clean | contradictions |')
print('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|')
tot = collections.Counter()
for app, how in APPS:
    jp = glob.glob('graphs/%s/out/*_trigger_graph.json' % app)
    if not jp:
        print('| %s | %s | missing |' % (app, how)); continue
    g = json.load(open(jp[0]))
    rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % app)))
    v = collections.Counter(r['verdict'] for r in rows)
    obs = [r for r in rows if r['monkey_hit'] != '']
    hit = lambda r: r['monkey_hit'] == '1' or r['ape_hit'] == '1'
    unhit = [r for r in obs if not hit(r)]
    ud = sum(1 for r in unhit if r['verdict'] in ('DEAD', 'FRAMEWORK_ONLY'))
    ue = sum(1 for r in unhit if r['verdict'].startswith('REACHABLE') and 'needs environment' in (r['note'] or ''))
    us = sum(1 for r in unhit if r['verdict'] == 'REACHABLE_AFTER_SETUP' and 'needs environment' not in (r['note'] or ''))
    uc = sum(1 for r in unhit if r['verdict'] == 'REACHABLE' and 'needs environment' not in (r['note'] or ''))
    contra = sum(1 for r in obs if hit(r) and r['verdict'] in ('DEAD', 'FRAMEWORK_ONLY'))
    print('| %s | %s | %d | %d | %d | %d | %d | %d | %d | %d | %d / %d / %d / %d | %d |' % (
        app, how, len(rows), len(g['screens']), len(g['edges']), v['REACHABLE'], v['REACHABLE_AFTER_SETUP'], v['DEAD'],
        v['FRAMEWORK_ONLY'], sum(1 for r in obs if hit(r)), ud, ue, us, uc, contra))
    tot.update({'m': len(rows), 'e': len(g['edges'])})
print('\nTotal: %d methods, %d edges in 13 graphs.' % (tot['m'], tot['e']))
