# Diary v1.105: method-level trigger graph (schema 2)

How every method of **Diary** is triggered, in the standard configuration: the instrumented debug build (`billthefarmer/diary@v1.105`, commit `07bb05c3b7a8`, APK sha256 `da194494...`), an API 27 emulator, permissions and fixtures as in `final_java_only`. Labels follow `handoff/SCHEMA_V2.md`: REACHABLE or UNREACHABLE, ENV and STATE gates, edge classes (explicit, standard, non-standard), and how each label was confirmed.

## What is in this folder

| File | What it is |
|---|---|
| `diary_trigger_graph.json` | pages, methods, `verdict`, `labels` (per-method fields), `edges` (with `edge_class`, `env_kinds`, `state_kinds`, stable ids), `paths` (verified paths only), `verification` (counts) |
| `methods.csv` | one row per method: verdict, UNREACHABLE reason, ENV and STATE kinds and texts, edge classes on the best route, whether an explicit/standard-only route exists, how the label was confirmed, path status, and the derived best route (`shortest_path`, `route_edge_ids`) |
| `../verification.csv` | the audit log: one row per label, edge or path that was checked, with result, how, and where (file:line) |
| `sanity_check.csv` | tool coverage (Monkey / APE, API 27) next to the labels; a one-way check only, it never sets a label |
| `diary_trigger_graph.html`, `build_report.txt` | the viewer and the validation report |

## Numbers

- **286 methods**, **34 pages** (including pseudo pages), **1435 edges**. Verdicts: **265 REACHABLE**, **21 UNREACHABLE**.
- UNREACHABLE by reason: framework_never_calls 4, no_trigger_in_app 17.
- ENV gates (methods): hardware 1, other 3, other_app 52, permission 3. STATE gates (methods): data 11, file 1, settings 2. Methods with no gate: 195.
- Edge classes: explicit 598, non_standard 14, page 214, standard 609. Non-standard edges: 14 (class named in res/xml/preferences.xml, constructed by the framework through reflection (GenericInflater.createItem); content URI resolved to the provider by its authority (ContentResolver); nothing in the app calls the provider method; implicit broadcast: Intent(ACTION_APPWIDGET_UPDATE) without a c).
- 33 reachable methods have a non-standard edge on their best route; 9 have no explicit-or-standard-only route at all.
- Labels confirmed by: INFERRED 29, SOURCE 257 (SOURCE: every edge of the best route cites a source line, in the app or in the Android 8.1 / library source; INFERRED: some edge rests on inference or on another app).

## How much to trust it

Verification log (`verification.csv`), counts of what was checked and found:

| Checked | Rows | Correct | Errors found (fixed) | Unclear |
|---|---:|---:|---:|---:|
| labels | 51 | 44 | 7 | 0 |
| edges (framework and other claims read against source) | 47 | 37 | 0 | 10 |
| paths (stratified sample, read step by step) | 30 | 18 | 7 | 5 |

Path status over all reachable methods: SOURCE_OK 25, UNCHECKED 240.
The rows are the items that were individually checked, not a random sample of all labels; see the notes below for how they were chosen and what the unclear rows wait for.

Edges whose evidence is not a source line (52 of 1435): E41cf8b5e (S_EXIT -> S_ENTRY); Eff02ee30 (Diary.onBackPressed@BROWSE -> Diary$1.onPageFinished); Ecc51ba5c (Diary.listYears -> Diary.lambda$listYears$1); Ee8021a1a (Diary.listMonths -> Diary.lambda$listMonths$2); Ed3097966 (Diary.listDays -> Diary.lambda$listDays$3); Ea16ba1a8 (Diary.sortFiles -> Diary.lambda$sortFiles$0); Ebfa0014d (Diary.loadMarkdown(CharSequence) -> Diary$1.onPageFinished); E03c29845 (S_DIARY_VIEW -> Diary$1.shouldOverrideUrlLoading); E30d249c1 (S_DIARY_VIEW_CHANGED -> Diary$1.shouldOverrideUrlLoading); Ed2f9b82e (S_DIARY_BROWSE -> Diary$1.shouldOverrideUrlLoading); Eb6f2a0d2 (S_DIARY_SEARCH@VIEW -> Diary$1.shouldOverrideUrlLoading); E5d9f47db (Diary.lambda$setListeners$6 -> Diary.onActionModeStarted) ...

Sanity check against tool coverage (never used to set a label): 187 methods ran in the 1-hour Monkey / APE runs on API 27; **0** of them are labelled UNREACHABLE.

## What the re-audit changed (compared with the schema 1 graph)
- **Labels.** ENV and STATE are structured fields now. DEAD, FRAMEWORK_ONLY and REACHABLE_AFTER_SETUP are gone: the graph has 21 UNREACHABLE methods (framework_never_calls 4, no_trigger_in_app 17), each with a reason and a source reference, and their call sites were grepped again in all app sources, the resources and the manifest. What the first version called setup became STATE gates, environment conditions are ENV gates: 58 reachable methods have an ENV gate and 13 a STATE gate on their best route, over 75 env edges and 100 needs_state edges. Labels confirmed by SOURCE 257, INFERRED 29.
- **Evidence.** Every claim the first version recalled from memory (FW-MEMORY), took from the Monkey / APE coverage (DYN) or left UNVERIFIED was handled one by one. Framework claims were read against the Android 8.1.0_r1 sources on disk and cite file:line; the coverage segments were deleted (tool coverage is no evidence); app claims that only named lines now cite them as SRC. Claims about another app, the WebView engine (Chromium, native code outside the Java sources) and the libcore classes stay INFERRED and say what was not read: 20 edges lead with INFERRED, 387 with FW-SRC and 1028 with SRC, and 52 of the 1435 edges carry a claim without a source line. One claim was corrected, not only cited: in Android 8.1 `ContentResolver.openOutputStream` on a file: URI opens a `ParcelFileDescriptor`, not a `FileOutputStream` (ContentResolver.java:1241-1244).
- **Paths.** Reading the sampled routes against the source found 7 wrong paths among the 30 and 7 labels that had to change (table above). All are fixed in `graph_def.py`: (1) Back with an empty entry stack and `changeDate` saving an unchanged entry cannot hold after a launch, so the entry-stack and unsaved-changes guards are STATE session gates now and the widget routes go through Add time and Home (onPause saves); (2) `haveMedia` exists only in an instance that another app started, so those edges carry ENV other_app and the routes use the share sheet, the picker or an external intent; (3) guards that need entries saved earlier are STATE data gates (several day files for the sort comparator, the folder listings, a search match, an empty day for the template); (4) the Cancel item is visible only while the entry is changed, so the search-menu route to Cancel got the STATE session gate and the route now adds the time first.
- **Best route.** With STRICT the best route is the one with the fewest ENV kinds, then the fewest STATE kinds, then the fewest steps; a gate that another route avoids is not a blocker.
## How the checked paths were chosen
`tools/verify_sample.py Diary 30` (seed 20261025) picks methods by stratum (a non-standard edge on the route, an inferred label, a STATE gate, an ENV gate, a long route, the rest) and takes first the method that adds the most unseen edges. The strata depend on the labels, so the sample moved while the gates were corrected; the 30 paths in the log are the sample of the final graph. Every route was read step by step against the printed source lines, including guards and ENV / STATE gates (app lines from `final_java_only`, framework and library lines from `.plan/fw_src`). Result of the 30: 18 correct, 7 wrong and fixed, 5 unclear. The unclear paths contain a step that rests on code that was not read: the picker app, or `java.io` / `java.util` library code. The labels of all UNREACHABLE methods and of the 30 sampled methods are logged, and the edge rows cover the framework claims that were read against the AOSP and library sources and the ones that stay unclear.
## What waits for a device (API 27)
- **Replaying the sampled paths.** No path is DEVICE_OK: 25 are SOURCE_OK (read in the source), 240 are UNCHECKED.
- **Other apps.** The share sheet, the picker and the document creator, the print service, an app that sends SEND / VIEW / geo: intents or opens a file with the Editor, and the launcher that places, resizes and removes the widget (ENV other_app): their source was not read.
- **WebView.** What the Chromium engine does (`onPageFinished`, `shouldOverrideUrlLoading` for a tapped link, loading `content://` images, the text-selection action mode) is native code outside the Java sources.
- **Environment.** A 24-hour locale with a calendar account (the event methods, ENV other and other_app), runtime permissions that are not granted yet (ENV permission), a rotation (ENV hardware) and an I/O error when a file is written are conditions of the device that a replay has to create.
- **Unread library code.** `File.listFiles` calling the filter, `Arrays.sort` calling the comparator, a `ParcelFileDescriptor.open` that fails for a missing folder, and the DatePicker delegates calling the date listener: libcore and widget sources that are not on disk (the libcore files in `.plan/fw_src` hold only "404: Not Found").
## Hazard candidates (from reading the code, not reproduced)
1. `Diary.addMedia(Intent)`: an app that sends an image/audio/video without `EXTRA_STREAM` makes Diary dereference null (Diary.java:1615, the null check comes at 1618); `SEND_MULTIPLE` without a stream list fails the same way (1643).
2. `Diary.share()` with the MarkdownView never laid out (Use markdown off since the start) likely gets a null drawing cache and crashes in `Bitmap.createBitmap` (1813-1817; inferred).
3. The first start copies the help text into the empty page and marks it changed (2387), so leaving the app saves the help text as today's entry (598-600).
4. Event lines such as `@ 10:30 Dentist` (help.md:220) are parsed with the locale's SHORT time format, so in an en-US locale ("h:mm a") they never become calendar events, silently (1305-1323).
5. With Use markdown off, `shown` stays true, so Search looks in the hidden MarkdownView and highlights nothing (3337-3338).
6. `haveMedia` stays true when the date dialog for received media is cancelled; the next Go to date + OK inserts the media again (823-824, 1655).
7. The Editor opened with a content URI that `FileUtils.getPath` cannot map keeps `file == null`; Accept and Save then drop the edits silently and still return RESULT_OK (Editor.java:125-126, 411).
8. In the Editor without storage permission, Accept/Save request the permission and finish immediately (Editor.java:186-198, 400-409), so the grant result most likely arrives too late and the text is not written (unverified).
9. `FileUtils.getPath` would throw `ArrayIndexOutOfBoundsException` for an external-storage document id without ":" (502); unlikely from a normal picker.
10. `QueryHandler.onQueryComplete` never closes the cursor (leak).
11. Tapping ◀ / ▶ on the widget while Diary sits in the background may bring Diary to the front, because the invisible `DiaryWidgetUpdate` activity joins the existing task (the ActivityStarter lines were read; the affinity match and the return to Diary are inferred).
12. A failed backup shows the error alert and then still the "Backup complete" toast (3183-3202).
## Limits
- Pages, and which states count as separate pages, were modelled by hand; there is no standard definition behind them.
- The derived best route ignores guards on data and settings except those recorded as ENV or STATE. The path reading added gates for the guards it found contradicting a route (entry stack, unsaved changes, `haveMedia`, entry files, a search match, an empty day). Other guards are still only text on the edge, for example the enabled state of Previous, Next and Today, a tapped link to an existing entry, and the help text of the first start; read the guard on each edge. Only the sampled routes were read step by step, and 7 of the 30 were wrong, so other routes are likely to have such a gap too.
- A route can hold only for the first start of a fresh install and carry no gate for it: `FileUtils.getExtension` runs because the help text, with its images, is copied into the empty page and marks it changed (Diary.java:560-568); the label does not say that the diary must still be empty.
- `tools/show_route.py` stops with a ValueError on an evidence citation written as `File.java:570, 1696-1709` (comma and space), which many edges use. The sampled routes were printed from the JSON and `methods.csv` instead, with the cited lines read from the source tree.
- Hazard 11: the ActivityStarter lines (ActivityStarter.java:1496-1520, 1036-1050, 1754-1760, 1565-1580) show an existing task being reused for a NEW_TASK start; the affinity match in `findTaskLocked` and Diary coming to the front are still inferred.
- Routes that start in another app (share, picker, geo: link, external Editor start, widget) need a tester that can leave the package; the self-share routes assume Diary is listed in its own share sheet, the widget routes assume a stock launcher.

## JSON shape (short)

```
{ "schema": 2, "title", "screens": {page: description}, "methods": [...], "verdict": {method: REACHABLE|UNREACHABLE},
  "labels": {method: {unreachable: {kind, text}, env: [{kinds, text}], state: [{kinds, text}], route_edge_classes, explicit_standard_route,
                      confirmed_by, source_ref, path_status}},
  "edges": [ {id, src, dst, kind, edge_class, via, trigger, gui[], guard, reads[], writes[], note, needs_state, state_kinds, env, env_kinds, evidence, class_basis} ],
  "paths": [ {method, edges[], edge_classes, explicit_standard_only, env, state, verified_by, ref} ], "verification": {...} }
```

`src`/`dst` are methods (`Class.method`, overloads as `Class.method(Type,Type)`) or pages (`S_...`). A suffix `@CONTEXT` is the same method or page in a specific context. Edge ids are a hash of the edge content, so they stay stable when other edges change.
