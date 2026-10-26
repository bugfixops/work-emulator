"""Write graphs/SUMMARY.md and handoff/FINAL_SUMMARY.md with numbers recomputed from graphs/*/out. Run from work/ after the builds.
Usage: python3 -I tools/write_summaries.py"""
import collections, csv, json, subprocess

cal = json.load(open('tools/tests/calibration.json'))
cal_da = ', '.join('%.1f%% (%s)' % (v['dead_vs_alive'], k) for k, v in cal.items())
cal_ex = ', '.join('%.1f%% (%s)' % (v['exact'], k) for k, v in cal.items())

table = subprocess.run(['python3', '-I', 'tools/summary_table.py'], capture_output=True, text=True).stdout


def frontier_count(app, node):
    rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % app)))
    return sum(1 for r in rows if r.get('frontier_first_unrun') == node)


def hits(app):
    rows = [r for r in csv.DictReader(open('graphs/%s/out/methods.csv' % app)) if r['monkey_hit'] != '']
    h = sum(1 for r in rows if r['monkey_hit'] == '1' or r['ape_hit'] == '1')
    return h, len(rows)


mm_h, mm_n = hits('MMEX')
ae_h, ae_n = hits('Aegis')
init_home = frontier_count('MMEX', 'MainActivity.initHomeFragment')

index = '''# Trigger graphs of the 13 Java-only apps

Each folder `graphs/<App>/out/` holds the same set of files as `share/` has for Currency: `<prefix>_trigger_graph.json` (pages, methods, verdicts, edges with evidence labels), `methods.csv` (one row per method: verdict, steps from launch, taps on the best path, path, baseline hits), `README.md` (numbers, how much to trust it, limits), `<prefix>_trigger_graph.html` (optional viewer) and `build_report.txt` (validation output). **The JSON and the CSV are the data.**

## Two ways of building

- **Hand-written** (Currency, Diary, hash-checker, openlauncher, Omni-Notes): the edge definitions were written by reading the source; state gates (`needs_state`) and environment gates (`env`) come from a human reading the code. Diary was made by Kiro with older tools.
- **Generated** (Vanilla-Music, AnyMemo, Markor, Aegis, AmazeFileManager, AnkiDroid, MMEX, LibreTorrent): `tools/gen_edges.py` derives entry points, lifecycle, callbacks, lambdas, intents, XML-instantiated classes and library glue (ButterKnife, EventBus, data binding, Dagger, Glide, Room, ...) from the bytecode, the manifest and `res/` XML; the per-app `graph_def.py` only adds a few gates; `review_notes.md` records what was reviewed by hand. Run on the five hand-written apps (`tools/calibrate.py`), the generator agrees with the hand-written graphs on **@CALDA@ of the methods for dead-versus-alive** and on @CALEX@ of the exact verdicts; the gap is `needs_state` (a human reads "needs a note / a folder / a setting" out of the code). So in the generated graphs `REACHABLE` means "no modelled setup", not "no setup".
- The generated graphs add five columns to `methods.csv` (`frontier_from`, `frontier_first_unrun`, `frontier_edge_kind`, `frontier_edge_evidence`, `steps_after_frontier`): for a method the baseline never ran, the edge where the chain from code that did run first enters code that never ran, i.e. the branch or event that blocked the baseline. Each generated README lists the ten frontier nodes that unlock the most never-run methods.

## Numbers (recomputed from the files by `tools/summary_table.py`)

''' + table + '''
"never run: dead / env / setup / clean" splits the methods that neither APE nor Monkey ran: dead or framework-only, reachable only through an outside environment, reachable after in-app setup, reachable with no modelled setup (the clearest target list for the paper). "baseline-run" counts the methods that ran in at least one of the two 1-hour API 27 runs. "contradictions" are dead or framework-only methods that ran anyway (must be 0).

## Rebuild

`python3 -I tools/build_graph.py graphs/<App> <prefix>` (from `work/`), then for generated apps `python3 -I tools/gen_readme.py <App> <prefix>` and `python3 -I tools/write_summaries.py`. `tools/check_gen.sh` re-runs the generator on the two hand-written apps and prints the agreement. The recipe, the tool facts and the rules learned are in `handoff/HANDOFF.md`.
'''
index = index.replace('@CALDA@', cal_da).replace('@CALEX@', cal_ex)
open('graphs/SUMMARY.md', 'w').write(index)

final = '''# Final summary: trigger graphs for the 13 Java-only apps (overnight run, 2026-10-24/25)

**Status: all 13 apps have `graphs/<App>/out/` with the graph JSON, `methods.csv`, `README.md` and the optional HTML viewer.** Index and rebuild commands: `graphs/SUMMARY.md`. Five graphs were written by hand earlier (Currency, Diary by Kiro, hash-checker, openlauncher, Omni-Notes); the other eight (Vanilla-Music, AnyMemo, Markor, Aegis, AmazeFileManager, AnkiDroid, MMEX, LibreTorrent) were produced overnight by a **generator** (`tools/gen_edges.py`) plus a short per-app review, because hand-writing took about 2.5 hours and 450k tokens per app and the eight apps hold 25.5k methods.

## Numbers (recomputed by `tools/summary_table.py`)

''' + table + '''
## What the generated graphs are, and are not

- Built from the bytecode call graph, `AndroidManifest.xml` and `res/` XML: entry points, lifecycle, callbacks of constructed classes, lambdas, intents, XML-instantiated classes, activity / permission results, `Handler` messages, and glue for ButterKnife, EventBus, data binding, Dagger / Hilt, Glide, Room, Icepick, Parceler, ORMLite, reflection by method name. Methods that nothing reaches are `DEAD` (automatic, `AUTO_DEAD`).
- **Validation.** 0 errors, 0 warnings and **0 contradictions with the baseline coverage** (no DEAD method ran in the 1-hour APE / Monkey runs) in all 8; every contradiction found during development was a missing generator rule and was fixed. Run on the five hand-written apps the generator agrees on @CALDA@ of the methods for dead-versus-alive, and on @CALEX@ of the exact verdicts. The five hand-written graphs were rebuilt with the changed tools and came out identical.
- **Limit that matters most:** `REACHABLE` in a generated graph means "no modelled setup". State gates beyond list rows (data that must exist, settings, files) are only modelled where `review_notes.md` / `graph_def.py` of the app lists them, so the split REACHABLE / REACHABLE_AFTER_SETUP is less reliable than in the hand-written graphs. Callbacks are reachable once an instance is constructed; Handler messages, EventBus subscribers and Dagger objects are linked from every send / post / graph-build site (INFERRED).
- **New in the generated CSVs:** the `frontier_*` columns say, for each never-run reachable method, where the chain from code that did run first enters code that never ran (a branch not taken, or an event nobody triggered). Each README lists the ten frontier nodes that unlock the most never-run methods.

## Findings about the baseline (from the hit counts)

- **MMEX: only @MMH@ of @MMN@ observable methods ran.** The hits stop at the tutorial, `SelectDatabaseActivity`, the password screen and the settings; no method of the packages `account`, `transactions`, `investment`, `reports`, `recurring`, `search`, `fragment`, `adapter` ran and `HomeFragment` was never created. `MainActivity.onCreate` ran but returns early when `showPrerequisite()` is true (the tutorial is still needed, or no valid database is selected: it starts `TutorialActivity` / `SelectDatabaseActivity` and calls `finish()`), so `initHomeFragment` never ran and @INIT@ never-run methods sit behind it. The MMEX graph gates those packages behind that prerequisite (read from `MainActivity.java`, stated in its README).
- **Aegis: @AEH@ of @AEN@.** The baseline got past the first-run setup and showed the vault list, but the vault stayed empty (`EntryAdapter.onBindViewHolder` never ran), and it never opened `EditEntryActivity` (add / edit an entry), the importers of the other authenticator apps, the backup preferences, or the unlock screen (`AuthActivity`).
- **LibreTorrent:** no method of the torrent detail screens ran (apparently no torrent was added; the fixtures have no `.torrent`).
- **Fixtures:** Vanilla-Music had 12 mp3 + 3 wav (so no fixture for the Opus / Ogg / FLAC / MP4 tag parsers); the Download folder has 19 files (`archive.zip`, `table.csv`, `todo.txt`, `tasks.org`, `notes.md`, `journal.md`, `sample_deck.apkg`, `sample.pdf`, `page.html`, `config.xml`, `data.json`, `events.ics`, `contacts.vcf`, six images), so csv, todo.txt and AnkiDroid-import files existed, but there is no fixture for 7z / gz / bz2 archives, apk or db files, Mnemosyne / SuperMemo files, `.jenc` notes or torrents; Markor's `Documents` fixture folder is missing.
- From earlier in the session: `merged.ec` omits the launch dump `00000.ec` (first-launch code can show `monkey_hit = 0` although it ran); one dump per run is unreadable; APE seems to wipe app data mid-run in Aegis, Markor and hash-checker; the reviewer's `share/methods.csv` drops the final tap in 4 rows whose path ends in `*.onOptionsItemSelected`.

## Open questions for the reviewer (unchanged, still unanswered)

1. Is device verification (emulator) required for each app, and for which edges?
2. Baseline tool: the draft says Monkey, `tool_run_set_38.csv` says APE.
3. The missing `fixtures/Documents` folder (Markor).
4. How were Aegis and MMEX set up on the baseline (coverage 25% and 6%)?
5. The draft counts 41 apps; here there are 13 Java-only apps.
6. Are generated graphs with class-level review acceptable as ground truth, or should selected apps be hand-curated further (the biggest gains: Aegis, MMEX, AnkiDroid, LibreTorrent state gates)?

## If more time is spent

- Hand-curate the `needs_state` gates of the biggest never-run clusters (each README lists them; `review_notes.md` says what is assumed) and re-run `tools/check_gen.sh`.
- Rebuild Diary with the current tools (Kiro's graph used older ones; its inputs `method_list.json` / `auto_calls.json` are not in `graphs/Diary/`).
- Verify the `FW-MEMORY` rules and the frontier edges on an emulator.
'''
final = final.replace('@CALDA@', cal_da).replace('@CALEX@', cal_ex).replace('@MMH@', str(mm_h)).replace('@MMN@', str(mm_n)).replace('@INIT@', str(init_home)).replace('@AEH@', str(ae_h)).replace('@AEN@', str(ae_n))
open('handoff/FINAL_SUMMARY.md', 'w').write(final)
print('wrote graphs/SUMMARY.md and handoff/FINAL_SUMMARY.md; MMEX %d/%d, initHomeFragment %d, Aegis %d/%d' % (mm_h, mm_n, init_home, ae_h, ae_n))
