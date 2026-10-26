# Currency v1.58: method-level trigger graph (schema 2)

How every method of **Currency** is triggered, in the standard configuration: the instrumented debug build (`billthefarmer/currency@v1.58`, commit `fb95913b68ba`, APK sha256 `5b57bdd3...`), an API 27 emulator, permissions and fixtures as in `final_java_only`. Labels follow `handoff/SCHEMA_V2.md`: REACHABLE or UNREACHABLE, ENV and STATE gates, edge classes (explicit, standard, non-standard), and how each label was confirmed.

## What is in this folder

| File | What it is |
|---|---|
| `currency_trigger_graph.json` | pages, methods, `verdict`, `labels` (per-method fields), `edges` (with `edge_class`, `env_kinds`, `state_kinds`, stable ids), `paths` (verified paths only), `verification` (counts) |
| `methods.csv` | one row per method: verdict, UNREACHABLE reason, ENV and STATE kinds and texts, edge classes on the best route, whether an explicit/standard-only route exists, how the label was confirmed, path status, and the derived best route (`shortest_path`, `route_edge_ids`) |
| `../verification.csv` | the audit log: one row per label, edge or path that was checked, with result, how, and where (file:line) |
| `sanity_check.csv` | tool coverage (Monkey / APE, API 27) next to the labels; a one-way check only, it never sets a label |
| `currency_trigger_graph.html`, `build_report.txt` | the viewer and the validation report |

## Numbers

- **145 methods**, **22 pages** (including pseudo pages), **393 edges**. Verdicts: **140 REACHABLE**, **5 UNREACHABLE**.
- UNREACHABLE by reason: branch_never_taken 1, framework_never_calls 3, no_trigger_in_app 1.
- ENV gates (methods): hardware 1, network 31, other_app 16, tls_chain 13. STATE gates (methods): data 6. Methods with no gate: 94.
- Edge classes: explicit 112, non_standard 5, page 57, standard 219. Non-standard edges: 5 (class named in res/xml/preferences.xml, constructed by the framework through reflection (GenericInflater.createItem); implicit broadcast: Intent(ACTION_APPWIDGET_UPDATE) without a component, resolved by action name to the manifest receiver).
- 4 reachable methods have a non-standard edge on their best route; 1 have no explicit-or-standard-only route at all.
- Labels confirmed by: INFERRED 1, SOURCE 144 (SOURCE: every edge of the best route cites a source line, in the app or in the Android 8.1 / library source; INFERRED: some edge rests on inference or on another app).

## How much to trust it

Verification log (`verification.csv`), counts of what was checked and found:

| Checked | Rows | Correct | Errors found (fixed) | Unclear |
|---|---:|---:|---:|---:|
| labels | 47 | 24 | 23 | 0 |
| edges (framework and other claims read against source) | 23 | 20 | 0 | 3 |
| paths (stratified sample, read step by step) | 28 | 23 | 1 | 4 |

Path status over all reachable methods: SOURCE_OK 24, UNCHECKED 116.
The rows are the items that were individually checked, not a random sample of all labels; see the notes below for how they were chosen and what the unclear rows wait for.

Edges whose evidence is not a source line (8 of 393): Ee6434656 (S_EXIT -> S_ENTRY); E854be197 (S_NAV_POPUP -> S_MAIN_DISPLAY); Eb876502c (S_DLG_UPDATE -> S_MAIN_DISPLAY); E9c7fb26f (S_MAIN_DISPLAY -> S_MAIN_EDIT); Ee1252495 (S_MAIN_EDIT -> S_MAIN_DISPLAY); E1cfacc94 (S_ENTRY -> CurrencyWidgetConfigure.<init>@ADD); Ee3672287 (CurrencyWidgetConfigure.lambda$onCreate$1@ADD -> CurrencyWidgetProvider.<init>@DELETED); Eb645f0b9 (CurrencyWidgetConfigure.lambda$onCreate$1@ADD -> S_ENTRY)

Sanity check against tool coverage (never used to set a label): 103 methods ran in the 1-hour Monkey / APE runs on API 27; **0** of them are labelled UNREACHABLE.

## What the re-audit changed (compared with the schema 1 graph)

- **Labels.** ENV and STATE are structured fields now, and every guard of the 391 edges (52 distinct) was classified as a program condition, an ENV gate or a STATE gate. 23 of the 140 reachable labels changed: the 16 widget methods gained ENV `other_app` (a widget has to be placed through the launcher), `ChoiceDialog.onRestoreInstanceState` gained ENV `hardware` (only a rotation recreates the picker), and the 6 methods that read the bundled rates gained STATE `data` (they run only while no rates are saved: the first launch after an install or after clearing the data). DEAD and FRAMEWORK_ONLY became UNREACHABLE with a reason kind and a source reference; the 5 methods were re-read in the source and stay.
- **Widget broadcast.** `Main.updateWidgets`, `CurrencyWidgetConfigure` and `CurrencyWidgetUpdate` send `ACTION_APPWIDGET_UPDATE` without a component. In Android 8.1 an implicit broadcast to the manifest receiver of an app that targets SDK 26 or higher is normally skipped, but for this one action the system limits a broadcast sent by an app to the caller's own package (`ActivityManagerService.java:19199-19224`), and the skip needs both component and package to be null (`BroadcastQueue.java:1267-1279`), so the receiver gets it. (The first version of this note called that an open question; Kiro's Diary notes had the answer.)
- **Evidence.** The 74 framework claims that the first version recalled from memory (`FW-MEMORY`) were read against the Android 8.1.0_r1 source (and MPAndroidChart 3.1.0 for the chart's value formatter) and now cite file:line; none was wrong. The `DYN` evidence, which came from tool coverage, was removed. The edges that still rest on inference are listed above.
- **Paths.** One wrong derived route was found and fixed: the route to `ChartActivity$DateAxisValueFormatter.getFormattedValue` reached `onActivityResult` through the picker's Back button (RESULT_CANCELED, the method returns at once) and then took an edge that needs RESULT_OK. `onActivityResult` is now split into `@OK` and `@CANCEL` nodes. `tools/check_routes.py` looks for guards that contradict each other along a route: it flags this route in the old definition and nothing in the current one.
- **Best route.** Of all routes to a method the one with the fewest ENV kinds is taken, then the fewest STATE kinds, then the fewest steps. The two parser methods that need no network on the first launch (bundled rates) are an example: they carry STATE `data` and no ENV.

## How the checked paths were chosen

`tools/verify_sample.py Currency 30` (seed 20261025) picks methods by stratum (a non-standard edge, an inferred label, a STATE gate, an ENV gate, a long route, the rest), the method adding the most unseen edges first: 28 methods whose routes cover 109 of the 163 distinct edges on all best routes. Every step was read with `tools/show_route.py` against the cited source lines, including the guards. Of the 28: 23 correct, 1 wrong and fixed, 4 unclear.

## What waits for a device (API 27)

- **Launcher behaviour.** Placing the widget, starting its configure activity and deleting a widget whose configuration was cancelled are done by the launcher (another app); its source was not read. Affects the widget methods that need the launcher to place the widget.
- **Soft keyboard.** `Main.onEditorAction` needs the soft keyboard (or a hardware Enter key); IME behaviour was not read.

## Hazard candidates (from reading the code, not reproduced)

- `ChartActivity.onActivityResult`: picking a pair via **New chart** before any chart history has loaded (for example offline) calls `entryList.clear()` on `null` (ChartActivity.java:836), a likely `NullPointerException`.
- `CurrencyWidgetRefresh.onCreate`: when the network check fails, this invisible (`Theme.NoDisplay`) activity returns without `finish()`, which Android 6+ turns into an `IllegalStateException` (Activity.java:7098-7121 in 8.1).

## Limits

- Pages, and which states count as separate pages, were modelled by hand; there is no standard definition behind them.
- The derived best route ignores guards on data and settings except those recorded as ENV or STATE; read the guard text on each edge. Only the 28 sampled routes were read step by step.
- Unreachable branches inside reachable methods are listed in the `note` column (for example `Main.onOptionsItemSelected`: the Help and Settings cases can no longer be reached from that menu).
- Widget routes assume a launcher that starts the configure activity and deletes the widget when configuration is cancelled (Launcher3 does, not checked).

## JSON shape (short)

```
{ "schema": 2, "title", "screens": {page: description}, "methods": [...], "verdict": {method: REACHABLE|UNREACHABLE},
  "labels": {method: {unreachable: {kind, text}, env: [{kinds, text}], state: [{kinds, text}], route_edge_classes, explicit_standard_route,
                      confirmed_by, source_ref, path_status}},
  "edges": [ {id, src, dst, kind, edge_class, via, trigger, gui[], guard, reads[], writes[], note, needs_state, state_kinds, env, env_kinds, evidence, class_basis} ],
  "paths": [ {method, edges[], edge_classes, explicit_standard_only, env, state, verified_by, ref} ], "verification": {...} }
```

`src`/`dst` are methods (`Class.method`, overloads as `Class.method(Type,Type)`) or pages (`S_...`). A suffix `@CONTEXT` is the same method or page in a specific context. Edge ids are a hash of the edge content, so they stay stable when other edges change.
