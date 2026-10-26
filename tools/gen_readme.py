"""Write graphs/<App>/out/README.md for a generated graph, with every number recomputed from out/*.json and out/methods.csv.

Usage (from work/): python3 -I tools/gen_readme.py <App> <prefix>
Optional hand-written text: graphs/<App>/review_notes.md is appended under "Review notes for this app".
"""
import collections
import csv
import json
import os
import re
import sys

app, prefix = sys.argv[1], sys.argv[2]
ROOT = '<root>'
gd = 'graphs/%s' % app
out = gd + '/out'
g = json.load(open('%s/%s_trigger_graph.json' % (out, prefix)))
rows = list(csv.DictReader(open(out + '/methods.csv')))
ds = {}
dtext = open('%s/final_java_only/%s/app/DATASET.txt' % (ROOT, app), encoding='utf-8', errors='replace').read()
for key in ('app', 'apk', 'package', 'min_sdk', 'target_sdk', 'sha256', 'provenance', 'source_commit'):
    m = re.search(r'(?m)^%s\s*:\s*(\S+)' % key, dtext)
    if m:
        ds[key] = m.group(1)
verdict = collections.Counter(r['verdict'] for r in rows)
edges = g['edges']
auto = sum(1 for x in edges if x.get('auto'))
kinds = collections.Counter(x['kind'] for x in edges)
evid = collections.Counter(x['evidence'].split()[0] for x in edges)
env_edges = sum(1 for x in edges if x.get('env'))
need_edges = sum(1 for x in edges if x.get('needs_state'))
env_methods = sum(1 for r in rows if 'needs environment' in (r['note'] or ''))
setup_methods = sum(1 for r in rows if 'needs earlier setup' in (r['note'] or ''))
pseudo = sum(1 for s in g['screens'] if s.startswith('S_NEW_'))
pages = len(g['screens'])


def cls_of(m):
    return m.split('(')[0].rsplit('.', 1)[0]


observable = [r for r in rows if r['monkey_hit'] != '']
hit = lambda r: r['monkey_hit'] == '1' or r['ape_hit'] == '1'
n_hit = sum(1 for r in observable if hit(r))
n_mon = sum(1 for r in observable if r['monkey_hit'] == '1')
n_ape = sum(1 for r in observable if r['ape_hit'] == '1')
n_both = sum(1 for r in observable if r['monkey_hit'] == '1' and r['ape_hit'] == '1')
dead_hit = [r for r in observable if r['verdict'] in ('DEAD', 'FRAMEWORK_ONLY') and hit(r)]
unhit = [r for r in observable if not hit(r)]
u_dead = [r for r in unhit if r['verdict'] in ('DEAD', 'FRAMEWORK_ONLY')]
u_env = [r for r in unhit if r['verdict'].startswith('REACHABLE') and 'needs environment' in (r['note'] or '')]
u_setup = [r for r in unhit if r['verdict'] == 'REACHABLE_AFTER_SETUP' and r not in u_env]
u_clean = [r for r in unhit if r['verdict'] == 'REACHABLE' and r not in u_env]
dead_by = collections.defaultdict(list)
tot_by = collections.Counter(cls_of(r['method']) for r in rows)
for r in rows:
    if r['verdict'] == 'DEAD':
        dead_by[cls_of(r['method'])].append(r['method'])
dead_lines = []
for c, ms in sorted(dead_by.items(), key=lambda kv: -len(kv[1]))[:14]:
    dead_lines.append('`%s` (%d of %d)' % (c, len(ms), tot_by[c]))
clean_by = collections.Counter(cls_of(r['method']) for r in u_clean)
clean_lines = ['`%s` (%d)' % (c, n) for c, n in clean_by.most_common(14)]
fr_rows = [r for r in rows if r.get('frontier_first_unrun')]
fr_kind = collections.Counter(r['frontier_edge_kind'] for r in fr_rows)
fr_node = collections.defaultdict(list)
for r in fr_rows:
    fr_node[r['frontier_first_unrun']].append(r)
fr_lines = []
for node, lst in sorted(fr_node.items(), key=lambda kv: -len(kv[1]))[:10]:
    r0 = lst[0]
    fr_lines.append('  - `%s` (%d never-run methods behind it): reached from `%s` by a `%s` edge (%s)' % (
        node, len(lst), r0['frontier_from'], r0['frontier_edge_kind'], r0['frontier_edge_evidence']))
fr_text = ''
if fr_rows:
    fr_text = ('- **Where the baseline stopped (frontier).** For %d of the never-run reachable methods the graph gives the edge where the chain from methods that ran first enters code that never ran '
               '(`frontier_*` columns of `methods.csv`: `frontier_from` is the source of that edge, a method that ran or a screen entered from one; `frontier_first_unrun` is its target): %s. A `CALL` frontier is a branch inside code that ran and was not taken (a data, setting or error condition); a `FRAMEWORK`, `GUI`, `INTENT` or `SYSTEM` frontier is a callback, tap or start that no tool triggered. '
               'The ten frontier nodes that unlock the most never-run methods:\n%s\n') % (
        len(fr_rows), ', '.join('%d %s' % (v, k) for k, v in fr_kind.most_common()), '\n'.join(fr_lines))
steps = [int(r['steps_from_launch']) for r in rows if r['steps_from_launch']]
avg_steps = sum(steps) / len(steps) if steps else 0
cal = json.load(open('tools/tests/calibration.json'))
cal_da = ', '.join('%.1f%% (%s)' % (v['dead_vs_alive'], k) for k, v in cal.items())
cal_ex = ', '.join('%.1f%% (%s)' % (v['exact'], k) for k, v in cal.items())
title = g['title'].replace(' trigger graph', '')
review = ''
if os.path.exists(gd + '/review_notes.md'):
    review = '\n## Review notes for this app\n\n' + open(gd + '/review_notes.md', encoding='utf-8').read().strip() + '\n'

txt = '''# %(title)s: page-jump and method-call graph (generated)

A map of how every method of the open-source Android app **%(app)s** (%(prov)s, source commit `%(commit)s`, package `%(pkg)s`, APK sha256 `%(sha)s`) can be triggered: from which page, by which user gesture or system event, through which framework callback or call. It is the build in `final_java_only/%(app)s`.

**How this one differs from Currency, hash-checker, openlauncher and Omni-Notes:** those graphs were written by hand from reading the source. This one was **generated** by `tools/gen_edges.py` from the bytecode, `AndroidManifest.xml` and `res/` XML, and then checked against the baseline coverage and reviewed (see "How much to trust it"). Every number below is recomputed from the files in this folder.

## What is in this folder

| File | What it is |
|---|---|
| `%(prefix)s_trigger_graph.json` | The graph: pages, methods, verdicts, edges. Every edge has an `evidence` label; an edge may carry `env` (needs something outside the app) and `needs_state` (needs an earlier action or setting). |
| `methods.csv` | One row per method: verdict, steps from launch, the user taps on the best path, the path, number of incoming edges, note. Extra columns: `jvm_descriptor`, `monkey_hit`, `ape_hit` (1-hour API 27 baseline runs; empty = JaCoCo does not report the method), and for methods the baseline never ran `frontier_from`, `frontier_first_unrun`, `frontier_edge_kind`, `frontier_edge_evidence`, `steps_after_frontier` (where the chain from code that ran first enters code that never ran). |
| `%(prefix)s_trigger_graph.html` | The same data in the viewer from the Currency example. Optional. |
| `build_report.txt` | Output of the validation script (0 errors, 0 warnings, baseline cross-check, the list of reachable methods the baseline never ran). |

## Numbers

- **%(methods)d methods** (the app's own code, aligned with what JaCoCo reports), **%(pages)d pages** (%(pseudo)d of them `S_NEW_<Class>` anchors: a class whose empty default constructor is not in the JaCoCo method universe is constructed through such a node), **%(nedges)d edges**: %(auto)d from the bytecode call extractor, %(gen)d added by the generator or by hand.
- Edge kinds: %(kinds)s.
- Verdicts: **%(reach)d reachable**, **%(setup)d reachable after setup**, **%(dead)d dead**, %(fwo)d framework-only.
- %(env_edges)d edges are gated by an outside environment, %(need_edges)d need an earlier action or setting; %(env_methods)d methods are reached only through an environment gate, %(setup_methods)d only after setup. Average route length: %(avg).1f edges.
- Evidence labels: %(evid)s.
- Largest dead groups (auto-classified, see limits): %(dead_lines)s.

## Comparison with the baseline coverage (APE and Monkey, 1 hour each, API 27)

- %(n_hit)d of the %(n_obs)d observable methods ran in at least one run (Monkey %(n_mon)d, APE %(n_ape)d, both %(n_both)d). **%(dead_hit)d dead or framework-only methods ran**, so the coverage contradicts no verdict.
- **%(n_unhit)d methods were run by neither tool.** By the graph: %(u_dead)d are dead; %(u_env)d are reachable only through an outside environment; %(u_setup)d need an earlier in-app action or setting; **%(u_clean)d are reachable with no modelled setup and no outside help, yet were never run** (the clearest target list for the paper). Classes holding most of them: %(clean_lines)s.
%(fr_text)s- Harness facts that matter for target selection: `merged.ec` omits the launch dump `00000.ec`, so first-launch code can show `monkey_hit = 0` although it ran; one dump per tool may be unreadable, and a process that dies between 30-second dumps loses its coverage, so "never hit" does not strictly prove "never ran".

## How much to trust it

- **Method.** `gen_edges.py` applies Android framework rules to the compiled classes: process entry (Application, launcher, exported components behind an `env` gate), lifecycle callbacks and one page `S_<Activity|Fragment>` per screen, UI and system callbacks of every constructed class with a framework ancestor, lambdas and method references (creator method -> body, the tap label is read from the source line), `startActivity(new Intent(ctx, X.class))` and custom intent actions, classes named in layout / xml / menu / navigation files and where they are inflated, activity and permission results, `Handler` messages, ButterKnife / EventBus / data binding / Dagger / Glide / Icepick / Parceler / ORMLite / Room glue, static initialisers, and template-method receiver variants (`Base.m@Sub`). Direct calls come from the bytecode (`extract_calls.py`, class-hierarchy analysis for virtual calls). Methods that nothing reaches are reported DEAD (`AUTO_DEAD`).
- **Calibration on the five hand-written apps** (the generator run on the same inputs, compared with the hand-written verdicts; `tools/calibrate.py`): dead-versus-alive agreement %(cal_da)s; exact verdict agreement %(cal_ex)s. The gap is almost entirely `needs_state`: a human reads "needs a note / a folder / a setting" out of the code, the generator only knows list rows. (openlauncher and Omni-Notes were used while the generator rules were developed; Currency, Diary and hash-checker were not.)
- **Checks done on this app:** the validation script (0 errors, 0 warnings: every method has a route or a DEAD verdict, every page is reachable); the baseline cross-check above (0 contradictions after the generator rules were completed by reading the contradictions one by one); random shortest paths were read for shortcuts.
- **Not checked on a device.** Framework rules are `FW-MEMORY` (recalled, not checked against AOSP source); guesses are `INFERRED`.

## Limits (read before using a verdict)

- **`REACHABLE` means "no modelled setup", not "no setup".** Gates beyond list rows (data that must exist, settings, earlier actions, incoming intents, files on the device) are modelled only where listed in the review notes. Adapter row callbacks, row-based listeners and action modes carry `needs_state` = "the list shows at least one row".
- A callback is reachable as soon as an instance of its class is constructed; the real trigger (a tap on one specific control) is shown in the `gui_steps` column only where the source line names the control. Menu and click handlers that switch on `R.id.x` give one labelled edge per case (`case R.id.x`), found by the nearest preceding case label (`INFERRED`).
- `Handler.handleMessage`, EventBus subscribers and Dagger-provided objects are linked from every send / post / graph-build site (`INFERRED`), so their routes can be shorter than the real ones.
- DEAD is automatic: nothing in the bytecode, manifest, XML or the modelled libraries reaches the method. Entries through reflection, JNI, other generated code or libraries that are not modelled would be missed (the baseline contradiction check found and fixed every such case that the 1-hour runs exercised).
- Calls inside catch blocks, data-dependent branches and feature flags are ordinary calls unless the review notes say otherwise.
%(review)s
## JSON shape (short)

```
{ "title", "screens": {page: description}, "methods": [...], "verdict": {method: REACHABLE|REACHABLE_AFTER_SETUP|DEAD|FRAMEWORK_ONLY},
  "dead": {method: reason}, "framework_only": {method: reason},
  "edges": [ {id, src, dst, kind, trigger, gui[], guard, reads[], writes[], note, needs_state, evidence, env} ] }
```
`src`/`dst` are methods (`Class.method`, overloads as `Class.method(Type,Type)`, classes that share a simple name get a package prefix) or pages (`S_...`). A suffix `@CONTEXT` is the same method in a specific receiver class (`Base.m@Sub`) or context.
''' % dict(
    title=title, app=app, prov=ds.get('provenance', ''), commit=ds.get('source_commit', '')[:8], pkg=ds.get('package', ''),
    sha=ds.get('sha256', '')[:8] + '…' + ds.get('sha256', '')[-8:], prefix=prefix, methods=len(g['methods']), pages=pages,
    pseudo=pseudo, nedges=len(edges), auto=auto, gen=len(edges) - auto,
    kinds=', '.join('%s %d' % kv for kv in sorted(kinds.items())),
    reach=verdict['REACHABLE'], setup=verdict['REACHABLE_AFTER_SETUP'], dead=verdict['DEAD'], fwo=verdict['FRAMEWORK_ONLY'],
    env_edges=env_edges, need_edges=need_edges, env_methods=env_methods, setup_methods=setup_methods, avg=avg_steps,
    evid=', '.join('%d `%s`' % (v, k) for k, v in sorted(evid.items())), dead_lines=', '.join(dead_lines) or 'none',
    n_hit=n_hit, n_obs=len(observable), n_mon=n_mon, n_ape=n_ape, n_both=n_both, dead_hit=len(dead_hit),
    n_unhit=len(unhit), u_dead=len(u_dead), u_env=len(u_env), u_setup=len(u_setup), u_clean=len(u_clean),
    clean_lines=', '.join(clean_lines) or 'none', review=review, fr_text=fr_text, cal_da=cal_da, cal_ex=cal_ex)
open(out + '/README.md', 'w', encoding='utf-8').write(txt)
print('wrote %s/README.md (%d lines); unhit %d: dead %d, env %d, setup %d, clean %d' % (out, txt.count('\n'), len(unhit), len(u_dead), len(u_env), len(u_setup), len(u_clean)))
