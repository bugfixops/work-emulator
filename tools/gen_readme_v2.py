"""Write graphs/<App>/out/README.md for a schema 2 graph from its build outputs.

Usage (from work/): python3 -I tools/gen_readme_v2.py <App>
Reads out/*_trigger_graph.json, out/methods.csv, out/sanity_check.csv, verification.csv (through the JSON), the dataset notes
(final_java_only/<App>/app/DATASET.txt) and the optional hand-written graphs/<App>/readme_notes.md, whose text is appended
under its own headings. All numbers come from the files, none is typed in.
"""
import collections
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_graph  # noqa: E402


def dataset(app):
    d = {}
    path = 'final_java_only/%s/app/DATASET.txt' % app
    if os.path.isfile(path):
        text = open(path, encoding='utf-8').read()
        for key in ('provenance', 'source_commit', 'sha256', 'apk', 'package', 'min_sdk', 'target_sdk'):
            m = re.search(r'^%s\s*:\s*(\S+)' % key, text, re.M)   # one line has a carriage return before the colon
            if m:
                d[key] = m.group(1)
    return d


def main(argv):
    app = argv[1]
    gdir = 'graphs/%s' % app
    jp = glob.glob('%s/out/*_trigger_graph.json' % gdir)[0]
    prefix = os.path.basename(jp).replace('_trigger_graph.json', '')
    g = json.load(open(jp))
    assert g.get('schema') == 2, 'not a schema 2 build'
    rows = list(csv.DictReader(open('%s/out/methods.csv' % gdir, encoding='utf-8')))
    labels, edges, verdict = g['labels'], g['edges'], g['verdict']
    ds = dataset(app)
    reach = [r for r in rows if r['verdict'] == 'REACHABLE']
    unre = [r for r in rows if r['verdict'] == 'UNREACHABLE']
    kinds = collections.Counter(r['unreachable_kind'] for r in unre)
    env_k, state_k = collections.Counter(), collections.Counter()
    for r in reach:
        for k in filter(None, r['env_kinds'].split(';')):
            env_k[k] += 1
        for k in filter(None, r['state_kinds'].split(';')):
            state_k[k] += 1
    cls = collections.Counter(x['edge_class'] for x in edges)
    nonstd = [x for x in edges if x['edge_class'] == 'non_standard']
    conf = collections.Counter(l['confirmed_by'] for l in labels.values())
    unsourced = [x for x in edges if not build_graph.edge_sourced(x)]
    pages = len(g['screens'])
    no_es = [r['method'] for r in reach if r['explicit_standard_route'] == 'no']
    nonstd_route = [r['method'] for r in reach if 'non_standard' in r['route_edge_classes']]
    ver = g.get('verification') or {}
    pstat = collections.Counter(l['path_status'] for l in labels.values() if l['path_status'])
    sanity = None
    sp = '%s/out/sanity_check.csv' % gdir
    if os.path.isfile(sp):
        s = list(csv.DictReader(open(sp, encoding='utf-8')))
        sanity = (sum(1 for r in s if r['monkey_hit'] == '1' or r['ape_hit'] == '1'), sum(1 for r in s if r['flag'] == 'CONTRADICTION'))
    L = []
    title = g['title'].replace(' trigger graph', '')
    L.append('# %s: method-level trigger graph (schema 2)' % title)
    L.append('')
    L.append('How every method of **%s** is triggered, in the standard configuration: the instrumented debug build%s, an API 27 emulator, permissions and fixtures as in `final_java_only`. '
             'Labels follow `handoff/SCHEMA_V2.md`: REACHABLE or UNREACHABLE, ENV and STATE gates, edge classes (explicit, standard, non-standard), and how each label was confirmed.' % (
                 app, ' (`%s`, commit `%s`, APK sha256 `%s`)' % (ds.get('provenance', ''), ds.get('source_commit', '')[:12], ds.get('sha256', '')[:8] + '...') if ds else ''))
    L.append('')
    L.append('## What is in this folder')
    L.append('')
    L.append('| File | What it is |')
    L.append('|---|---|')
    L.append('| `%s_trigger_graph.json` | pages, methods, `verdict`, `labels` (per-method fields), `edges` (with `edge_class`, `env_kinds`, `state_kinds`, stable ids), `paths` (verified paths only), `verification` (counts) |' % prefix)
    L.append('| `methods.csv` | one row per method: verdict, UNREACHABLE reason, ENV and STATE kinds and texts, edge classes on the best route, whether an explicit/standard-only route exists, how the label was confirmed, path status, and the derived best route (`shortest_path`, `route_edge_ids`) |')
    L.append('| `../verification.csv` | the audit log: one row per label, edge or path that was checked, with result, how, and where (file:line) |')
    L.append('| `sanity_check.csv` | tool coverage (Monkey / APE, API 27) next to the labels; a one-way check only, it never sets a label |')
    L.append('| `%s_trigger_graph.html`, `build_report.txt` | the viewer and the validation report |' % prefix)
    L.append('')
    L.append('## Numbers')
    L.append('')
    L.append('- **%d methods**, **%d pages** (including pseudo pages), **%d edges**. Verdicts: **%d REACHABLE**, **%d UNREACHABLE**.' % (len(rows), pages, len(edges), len(reach), len(unre)))
    L.append('- UNREACHABLE by reason: %s.' % (', '.join('%s %d' % kv for kv in sorted(kinds.items())) or 'none'))
    L.append('- ENV gates (methods): %s. STATE gates (methods): %s. Methods with no gate: %d.' % (
        ', '.join('%s %d' % kv for kv in sorted(env_k.items())) or 'none', ', '.join('%s %d' % kv for kv in sorted(state_k.items())) or 'none',
        sum(1 for r in reach if not r['env_kinds'] and not r['state_kinds'])))
    L.append('- Edge classes: %s. Non-standard edges: %d%s.' % (', '.join('%s %d' % kv for kv in sorted(cls.items())), len(nonstd),
                                                              ' (' + '; '.join(sorted({x['via'] for x in nonstd if x['via']}))[:300] + ')' if nonstd else ''))
    L.append('- %d reachable methods have a non-standard edge on their best route; %d have no explicit-or-standard-only route at all.' % (len(nonstd_route), len(no_es)))
    L.append('- Labels confirmed by: %s (SOURCE: every edge of the best route cites a source line, in the app or in the Android 8.1 / library source; INFERRED: some edge rests on inference or on another app).' % ', '.join('%s %d' % kv for kv in sorted(conf.items())))
    L.append('')
    L.append('## How much to trust it')
    L.append('')
    if ver:
        L.append('Verification log (`verification.csv`), counts of what was checked and found:')
        L.append('')
        L.append('| Checked | Rows | Correct | Errors found (fixed) | Unclear |')
        L.append('|---|---:|---:|---:|---:|')
        for t, name in (('label', 'labels'), ('edge', 'edges (framework and other claims read against source)'), ('path', 'paths (stratified sample, read step by step)')):
            v = ver[t]
            L.append('| %s | %d | %d | %d | %d |' % (name, v['checked'] + v['unclear'], v['correct'], v['errors_found'], v['unclear']))
        L.append('')
        L.append('Path status over all reachable methods: %s.' % ', '.join('%s %d' % kv for kv in sorted(pstat.items())))
        L.append('The rows are the items that were individually checked, not a random sample of all labels; see the notes below for how they were chosen and what the unclear rows wait for.')
    else:
        L.append('No verification log yet: every label is `UNCHECKED` and nothing is claimed beyond what the evidence column says.')
    L.append('')
    if unsourced:
        L.append('Edges whose evidence is not a source line (%d of %d): %s' % (len(unsourced), len(edges), '; '.join(
            '%s (%s -> %s)' % (x['id'], x['src'], x['dst']) for x in unsourced[:12]) + (' ...' if len(unsourced) > 12 else '')))
        L.append('')
    if sanity:
        L.append('Sanity check against tool coverage (never used to set a label): %d methods ran in the 1-hour Monkey / APE runs on API 27; **%d** of them are labelled UNREACHABLE.' % sanity)
        L.append('')
    notes = '%s/readme_notes.md' % gdir
    if os.path.isfile(notes):
        L.append(open(notes, encoding='utf-8').read().rstrip())
        L.append('')
    L.append('## JSON shape (short)')
    L.append('')
    L.append('```')
    L.append('{ "schema": 2, "title", "screens": {page: description}, "methods": [...], "verdict": {method: REACHABLE|UNREACHABLE},')
    L.append('  "labels": {method: {unreachable: {kind, text}, env: [{kinds, text}], state: [{kinds, text}], route_edge_classes, explicit_standard_route,')
    L.append('                      confirmed_by, source_ref, path_status}},')
    L.append('  "edges": [ {id, src, dst, kind, edge_class, via, trigger, gui[], guard, reads[], writes[], note, needs_state, state_kinds, env, env_kinds, evidence, class_basis} ],')
    L.append('  "paths": [ {method, edges[], edge_classes, explicit_standard_only, env, state, verified_by, ref} ], "verification": {...} }')
    L.append('```')
    L.append('')
    L.append('`src`/`dst` are methods (`Class.method`, overloads as `Class.method(Type,Type)`) or pages (`S_...`). A suffix `@CONTEXT` is the same method or page in a specific context. '
             'Edge ids are a hash of the edge content, so they stay stable when other edges change.')
    open('%s/out/README.md' % gdir, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('wrote %s/out/README.md (%d lines)' % (gdir, len(L)))


if __name__ == '__main__':
    main(sys.argv)
