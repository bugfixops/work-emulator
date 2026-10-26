# hash-checker v3.7.3: method-level trigger graph (schema 2)

How every method of **hash-checker** is triggered, in the standard configuration: the instrumented debug build (`hash-checker/hash-checker@master`, commit `5cf7961b8860`, APK sha256 `f90f4c68...`), an API 27 emulator, permissions and fixtures as in `final_java_only`. Labels follow `handoff/SCHEMA_V2.md`: REACHABLE or UNREACHABLE, ENV and STATE gates, edge classes (explicit, standard, non-standard), and how each label was confirmed.

## What is in this folder

| File | What it is |
|---|---|
| `hash-checker_trigger_graph.json` | pages, methods, `verdict`, `labels` (per-method fields), `edges` (with `edge_class`, `env_kinds`, `state_kinds`, stable ids), `paths` (verified paths only), `verification` (counts) |
| `methods.csv` | one row per method: verdict, UNREACHABLE reason, ENV and STATE kinds and texts, edge classes on the best route, whether an explicit/standard-only route exists, how the label was confirmed, path status, and the derived best route (`shortest_path`, `route_edge_ids`) |
| `../verification.csv` | the audit log: one row per label, edge or path that was checked, with result, how, and where (file:line) |
| `sanity_check.csv` | tool coverage (Monkey / APE, API 27) next to the labels; a one-way check only, it never sets a label |
| `hash-checker_trigger_graph.html`, `build_report.txt` | the viewer and the validation report |

## Numbers

- **529 methods**, **39 pages** (including pseudo pages), **1314 edges**. Verdicts: **507 REACHABLE**, **22 UNREACHABLE**.
- UNREACHABLE by reason: closed_by_configuration 3, framework_never_calls 3, no_trigger_in_app 16.
- ENV gates (methods): other 1, other_app 33, time 1. STATE gates (methods): data 33, session 12, settings 42. Methods with no gate: 404.
- Edge classes: explicit 874, non_standard 48, page 89, standard 303. Non-standard edges: 48 (Dagger dependency injection: the generated component calls the module method; nothing in the app calls it; ORMLite builds the row object by reflection).
- 5 reachable methods have a non-standard edge on their best route; 5 have no explicit-or-standard-only route at all.
- Labels confirmed by: INFERRED 453, SOURCE 76 (SOURCE: every edge of the best route cites a source line, in the app or in the Android 8.1 / library source; INFERRED: some edge rests on inference or on another app).

## How much to trust it

Verification log (`verification.csv`), counts of what was checked and found:

| Checked | Rows | Correct | Errors found (fixed) | Unclear |
|---|---:|---:|---:|---:|
| labels | 52 | 50 | 2 | 0 |
| edges (framework and other claims read against source) | 35 | 9 | 26 | 0 |
| paths (stratified sample, read step by step) | 37 | 24 | 13 | 0 |

Path status over all reachable methods: SOURCE_OK 37, UNCHECKED 470.
The rows are the items that were individually checked, not a random sample of all labels; see the notes below for how they were chosen and what the unclear rows wait for.

Edges whose evidence is not a source line (157 of 1314): Ec9b0d520 (MainActivity.showFragment@CALC_XURI -> HashCalculatorFragment.onAttach@XURI); Ee781a5b8 (HashCalculatorFragment.onAttach@XURI -> BaseFragment.onCreateView@HashCalculatorFragment_XURI); Ee861279f (BaseFragment.onCreateView@HashCalculatorFragment_XURI -> HashCalculatorFragment.onViewCreated@XURI); E21ea7944 (MainActivity.showFragment@CALC_XTEXT -> HashCalculatorFragment.onAttach@XTEXT); Ef8b0149d (HashCalculatorFragment.onAttach@XTEXT -> BaseFragment.onCreateView@HashCalculatorFragment_XTEXT); E3a41bb03 (BaseFragment.onCreateView@HashCalculatorFragment_XTEXT -> HashCalculatorFragment.onViewCreated@XTEXT); E51602476 (MainActivity.showFragment@CALC_XFILE -> HashCalculatorFragment.onAttach@XFILE); E1a2c0ce6 (HashCalculatorFragment.onAttach@XFILE -> BaseFragment.onCreateView@HashCalculatorFragment_XFILE); Ee7706acf (BaseFragment.onCreateView@HashCalculatorFragment_XFILE -> HashCalculatorFragment.onViewCreated@XFILE); E2cbba8c6 (MainActivity.onCreate -> BaseActivity.getTheme@MainActivity); Ee606bb4f (MainActivity.create -> HashCalculatorFragment.<clinit>); E3755babd (MainActivity.showFragment@CALC -> HashCalculatorFragment.onAttach) ...

Sanity check against tool coverage (never used to set a label): 404 methods ran in the 1-hour Monkey / APE runs on API 27; **0** of them are labelled UNREACHABLE.

## What the re-audit changed (compared with the schema 1 graph)

- **Labels.** The schema 1 graph had 419 reachable, 90 reachable after setup, 14 dead code and 6 framework-only methods. DEAD, FRAMEWORK_ONLY and REACHABLE_AFTER_SETUP are gone: ENV and STATE are structured fields, and the graph has 507 REACHABLE and 22 UNREACHABLE methods (closed_by_configuration 3, framework_never_calls 3, no_trigger_in_app 16). Every UNREACHABLE method was grepped again in the sources of all three source sets (main, thirdPartyStores, googlePlay), the resources and the manifest (label rows in `verification.csv`).
- **Two methods moved from reachable to UNREACHABLE (closed_by_configuration).** `SharedPreferencesSettings.setRefreshSelectedFileStatus` and `getThemeAnalogue` can only run when the preferences file is pre-seeded: the app only ever writes `false` to `refresh_selected_file` and only LIGHT or DARK as the theme. Rule used everywhere in this graph: a branch that needs state no in-app action can create is closed in the standard configuration (fresh install); its edge is removed, and a method that other edges reach stays REACHABLE. Two more edges were removed for the same reason: the catch in `getLastHashType` (the app only stores `HashType.toString()`) and the `saveTheme(DARK)` call inside `validateAppTheme`.
- **`App.onTerminate`** was a memory claim ("never called on a device"). It now cites the Android 8.1 source: only the EXIT_APPLICATION message calls it (`ActivityThread.java:1659-1664`), and the activity manager sends that message only for a process with no real pid or for system_server itself (`ActivityManagerService.java:6919-6936, 23336-23340`).
- **Evidence.** The framework claims written from memory (FW-MEMORY, on 126 edges) were handled one by one: 49 FW-SRC citations now point at Android 8.1.0_r1 lines that were printed and read (AsyncTask, Dialog, TextView.setText, activity pause / resume, configuration change, activity results); every claim about androidx, ORMLite, SQLiteOpenHelper, the picker app or the JVM is written as INFERRED and says what was not read. No evidence is tagged FW-MEMORY, DYN or UNVERIFIED any more.
- **Edge classes.** Dagger injector calls (the generated component calls the module, nothing in the app does) and the ORMLite row constructor are non-standard (48 edges). The module constructors in `App.onCreate` are plain `new` calls and are explicit. The nine edges the build flagged for review (fragment `onAttach`, `S_EXIT -> S_ENTRY`, the builder call) were decided one by one in `CLASSIFY`.
- **Paths, found by reading the routes against the source (13 of 37 checked paths had an error, all fixed in `graph_def.py`).** (1) Four routes started with the plain launcher entry but needed data only a start by another app carries (the VIEW / SEND URI and the two launcher shortcuts): the start by another app is now its own context (`@XURI`, `@XTEXT`, `@XFILE`) from the entry edge down to `onViewCreated`; the schema 1 notes said the CSV's first tap stayed the launcher icon, which was this error. (2) Two routes used an edge that needs a pre-seeded preference (`LogUtils.e`, `saveTheme`). (3) Missing guards: `Blake2B.update -> compress` runs only for more than one 128-byte block (the route now goes through `getValue -> doFinal -> compress`), `FNV1a.update -> updateN` only for the selected size, first-launch guards on `setLocale` and shortcut creation. (4) One wrong hand-written edge (`HashCalculatorFragment.<init> -> $1.<init>`: `$1` is the TextWatcher built in `watcherForInputField`). (5) Three module constructors were classed non-standard.
- **Citations of calls found in the bytecode.** `tools/check_bytecode_lines.py` checks that the cited line of every bytecode-derived edge contains the callee: 15 edges cited a line one too early (javac attributes a `new` inside a chained call to the previous line) or the last line of a multi-line expression; all corrected. `show_route.py` was also fixed: with two flavors it printed the googlePlay copy of `MainActivity.java` instead of the built thirdPartyStores one.
- **Tool coverage** is only in `sanity_check.csv`: no UNREACHABLE method ran in the Monkey / APE runs.

## How the checked paths were chosen

`tools/verify_sample.py hash-checker 30` draws 30 reachable methods, stratified by what their best route needs (non-standard edge, INFERRED label, STATE gate, ENV gate, long route, plain route), seed 20261025. The sample depends on the graph, so it was drawn again after each batch of fixes changed some best routes; `verification.csv` holds the final 30 plus 7 methods that were read earlier in the work (`LogUtils.e`, `AppTextWatcher.<init>`, `ThemeConfigImpl.setCurrentTheme`, `HashCalculatorFragment.selectFileFromSystemFileManager` and the three module constructors), 37 path rows in all: 24 correct, 13 with an error found and fixed (error rate 0.351, from `build_report.txt`). Of the final 30, 8 had an error. Each route was read step by step against the printed source, including guards and the ENV / STATE gates; a step that goes through the androidx FragmentManager or RecyclerView was read on the app side only and stays INFERRED in the evidence. All rows are `SOURCE`; none was replayed on a device. The label rows are the 22 UNREACHABLE methods plus the 30 sampled reachable ones (50 correct, 2 fixed), and the edge rows are the FW-SRC citations that were read and the edges that were corrected.

## What waits for a device (API 27)

Nothing here was confirmed on the emulator (confirmed_by DEVICE: 0). What a device check should settle: that the system file picker (`com.android.documentsui`) returns the document or tree the routes assume, for file, folder and the two `ACTION_CREATE_DOCUMENT` exports; that the launcher shortcuts "Text" and "File" start `MainActivity` with the action the code reads, and that an explicit VIEW intent with a `content://` URI starts the file path (`adb shell am start` can send it); that the 60-second clipboard clear fires; that a configuration change relaunches `MainActivity` (the manifest has no `android:configChanges`; the portrait lock only stops rotation). No method is closed by the API level: the shortcut code needs SDK_INT 26 or higher, true on API 27.

## Hazard candidates (from reading the code, not reproduced)

- **History shows at most the newest 30 rows.** `HistoryPresenterImpl.isLoaded()` is inverted (true when not loading and more pages remain), so `HistoryFragment$1.canLoad` is false at rest and page 2 is never requested.
- **`WebFragment` has no no-argument constructor** (`WebFragment.java:27-29`), so recreating the activity with the privacy page on screen (multi-window resize, process restore) would throw when the framework re-instantiates it.
- **Empty-history crash candidate:** `HistoryFragment.setLoaded` calls `primaryMenuButton.setVisible(false)` for an empty first page; `primaryMenuButton` is set in `onCreateOptionsMenu`, so if the loader finishes first it is null (timing not checked).
- `OrmLiteLocalDataStorage.isHistoryItemsListIsEmpty()` returns `countOf() > 0` (inverted name; callers handle it correctly: `SettingsPresenterImpl.saveUserData` takes the export branch when it is true).
- Found while reading paths: the `FILE_CREATE` case of `HashCalculatorFragment.onActivityResult` calls `writeHashToFile` for any non-null data without checking the result code (`HashCalculatorFragment.java:593-599`), unlike the file and folder cases.

## Limits

- **androidx, material and ORMLite sources were not read.** 157 of the 1314 edges carry an INFERRED claim, mostly the fragment lifecycle that every route through a fragment uses, so 453 of 529 labels are confirmed INFERRED and 76 SOURCE (see the table above). A path marked SOURCE_OK means every app step was read; the androidx steps on it are still INFERRED.
- **Bytecode-derived edges (654 of 1314) carry no guards.** The best route is the shortest one and ignores guards, so a route that was not read can still contain a guarded step; 13 of the 37 routes that were read did. The label (REACHABLE) holds as long as some valid route exists, which was checked for the sampled methods only.
- Only 37 of 507 routes were read; the other 470 are UNCHECKED.
- Pages and their modes were modelled by hand. The three calculator bottom sheets exist once per calculator mode (empty / text / file / folder). Back from History or Settings is modelled as returning to the empty calculator page; the real app keeps the source it had. The nodes of a start by another app exist only up to `onViewCreated`; the calls made inside `onViewCreated` are inherited from the plain node.
- Recreation (multi-window, process death, a configuration change) and the Dagger-generated code are not modelled beyond the injector edges. The "Folder" launcher shortcut is ignored by this flavor (`MainActivity.getBundleForShortcutAction` has no folder case).
- The standard configuration is the thirdPartyStores debug build (DATASET.txt and `BuildConfig.FLAVOR` agree); the googlePlay sources are not part of it.

## JSON shape (short)

```
{ "schema": 2, "title", "screens": {page: description}, "methods": [...], "verdict": {method: REACHABLE|UNREACHABLE},
  "labels": {method: {unreachable: {kind, text}, env: [{kinds, text}], state: [{kinds, text}], route_edge_classes, explicit_standard_route,
                      confirmed_by, source_ref, path_status}},
  "edges": [ {id, src, dst, kind, edge_class, via, trigger, gui[], guard, reads[], writes[], note, needs_state, state_kinds, env, env_kinds, evidence, class_basis} ],
  "paths": [ {method, edges[], edge_classes, explicit_standard_only, env, state, verified_by, ref} ], "verification": {...} }
```

`src`/`dst` are methods (`Class.method`, overloads as `Class.method(Type,Type)`) or pages (`S_...`). A suffix `@CONTEXT` is the same method or page in a specific context. Edge ids are a hash of the edge content, so they stay stable when other edges change.
