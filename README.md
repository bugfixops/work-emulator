# Method-level trigger graphs with ground-truth labels (schema 2): work in progress

This branch holds the finished part of a hand-checked ground truth for 13 Java-only Android apps (a study of targeted testing tools). It is a snapshot, not a release: nothing here was confirmed on a device yet (`confirmed_by` DEVICE: 0), and the app sources are not included.

For every method of an app the graph says whether it is `REACHABLE` or `UNREACHABLE` in the standard configuration (instrumented debug build, API 27 emulator, fresh install), why (for UNREACHABLE), which environment (ENV) and in-app state (STATE) gates stand in the way, whether the best route uses explicit / standard / non-standard edges, and how each claim was confirmed (SOURCE, INFERRED, DEVICE). Tool coverage (Monkey / APE) is only a one-way sanity check and never sets a label.

## Status: 4 of 13 apps converted

| App | Methods | REACHABLE | UNREACHABLE | Checked paths (wrong or fixed / checked) |
|---|---|---|---|---|
| Currency | 145 | 140 | 5 | 1 / 24 |
| Diary | 286 | 265 | 21 | 7 / 25 |
| hash-checker | 529 | 507 | 22 | 13 / 37 |
| Omni-Notes | 1,456 | 1,202 | 254 | 30 / 33 (26 share one error, 1 left unfixed) |

Not converted yet: openlauncher (blocked, a half-edited definition), Vanilla-Music, AnyMemo, Markor, Aegis, AmazeFileManager, AnkiDroid, MMEX, LibreTorrent. Their old, generated graphs are not part of this branch because they do not meet the rules.

## Layout

- `graphs/<App>/graph_def.py`: the hand-written definition (pages, entry / lifecycle / GUI / callback edges with guards and evidence; direct calls come from the bytecode extractor).
- `graphs/<App>/out/`: `<app>_trigger_graph.json`, `methods.csv` (one row per method), `README.md` (numbers and caveats), `build_report.txt`, `sanity_check.csv`.
- `graphs/<App>/verification.csv`: the audit log (labels, edges and paths that were read against the source, with result and file:line).
- `graphs/<App>/readme_notes.md`: what the re-audit changed, how the paths were chosen, what waits for a device, hazard candidates, limits.
- `tools/`: `build_graph.py` (builder and validator), `extract_calls.py`, checkers (`check_citations.py`, `check_routes.py`, `check_bytecode_lines.py`), `scan_unreachable.py`, `cases.py`, `verify_sample.py`, `show_route.py`.
- `handoff/SCHEMA_V2.md` (the file format and the rules), `handoff/CONVERSION_RECIPE.md` (how an app is converted and the errors that reading the routes found), `handoff/examples/`.

## Rebuild

`python3 -I tools/build_graph.py graphs/<App> <prefix>` from the folder that holds `tools/` and `graphs/`, with the app sources under `final_java_only/<App>/` and the Android 8.1.0_r1 framework files under `fw_src/` (both left out here). Framework claims cite `FW-SRC core/java/android/...:lines` of that tag.

Names of people and local paths were removed from this copy.
