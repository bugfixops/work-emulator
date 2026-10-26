# Omni-Notes 6.1.0: method-level trigger graph (schema 2)

How every method of **Omni-Notes** is triggered, in the standard configuration: the instrumented debug build (`tingsu/Omni-Notes@instrumented-version-6.1.0`, commit `a1d9354fc9b2`, APK sha256 `a7bd916b...`), an API 27 emulator, permissions and fixtures as in `final_java_only`. Labels follow `handoff/SCHEMA_V2.md`: REACHABLE or UNREACHABLE, ENV and STATE gates, edge classes (explicit, standard, non-standard), and how each label was confirmed.

## What is in this folder

| File | What it is |
|---|---|
| `omni-notes_trigger_graph.json` | pages, methods, `verdict`, `labels` (per-method fields), `edges` (with `edge_class`, `env_kinds`, `state_kinds`, stable ids), `paths` (verified paths only), `verification` (counts) |
| `methods.csv` | one row per method: verdict, UNREACHABLE reason, ENV and STATE kinds and texts, edge classes on the best route, whether an explicit/standard-only route exists, how the label was confirmed, path status, and the derived best route (`shortest_path`, `route_edge_ids`) |
| `../verification.csv` | the audit log: one row per label, edge or path that was checked, with result, how, and where (file:line) |
| `sanity_check.csv` | tool coverage (Monkey / APE, API 27) next to the labels; a one-way check only, it never sets a label |
| `omni-notes_trigger_graph.html`, `build_report.txt` | the viewer and the validation report |

## Numbers

- **1456 methods**, **68 pages** (including pseudo pages), **3803 edges**. Verdicts: **1202 REACHABLE**, **254 UNREACHABLE**.
- UNREACHABLE by reason: branch_never_taken 5, closed_by_configuration 21, framework_never_calls 34, no_trigger_in_app 194.
- ENV gates (methods): hardware 29, network 17, other 23, other_app 96, permission 125, system_event 5, time 17. STATE gates (methods): data 262, file 48, session 47, settings 40. Methods with no gate: 648.
- Edge classes: explicit 2305, non_standard 117, page 356, standard 1025. Non-standard edges: 117 (ACRA reads the BuildConfig class by reflection; ButterKnife: the generated binder / click listener is called by reflection or built by the generated code; EventBus: post() looks the subscribers up by event class; FragmentFactory instantiates the fragment by reflection; LayoutInflater builds the view).
- 259 reachable methods have a non-standard edge on their best route; 202 have no explicit-or-standard-only route at all.
- Labels confirmed by: INFERRED 1145, SOURCE 311 (SOURCE: every edge of the best route cites a source line, in the app or in the Android 8.1 / library source; INFERRED: some edge rests on inference or on another app).

## How much to trust it

Verification log (`verification.csv`), counts of what was checked and found:

| Checked | Rows | Correct | Errors found (fixed) | Unclear |
|---|---:|---:|---:|---:|
| labels | 288 | 281 | 7 | 0 |
| edges (framework and other claims read against source) | 49 | 15 | 34 | 0 |
| paths (stratified sample, read step by step) | 33 | 3 | 30 | 0 |

Path status over all reachable methods: SOURCE_OK 31, UNCHECKED 1170, WRONG 1.
The rows are the items that were individually checked, not a random sample of all labels; see the notes below for how they were chosen and what the unclear rows wait for.

Edges whose evidence is not a source line (356 of 3803): Ed965d44a (MainActivity.onCreate -> MainActivity_ViewBinding.<init>(MainActivity,View)); E7c78e9af (MainActivity.onCreate -> NavigationDrawerFragment.<init>); E449a3211 (NavigationDrawerFragment.<init> -> NavigationDrawerFragment.onCreate); E02a461c5 (NavigationDrawerFragment.<init> -> NavigationDrawerFragment.onCreateView); E0c960f14 (NavigationDrawerFragment.<init> -> NavigationDrawerFragment.onActivityCreated); E16eb2c51 (NavigationDrawerFragment.<init> -> NavigationDrawerFragment.onStart); E8c98d772 (ListFragment.<init> -> ListFragment.onCreate); Ef56e2127 (ListFragment.<init> -> ListFragment.onCreateView); E54b170af (ListFragment.<init> -> ListFragment.onActivityCreated); E995b7be1 (ListFragment.<init> -> ListFragment.onResume); E24faa205 (ListFragment.<init> -> ListFragment.onCreateOptionsMenu); E2b5eb400 (ListFragment.<init> -> ListFragment.onPrepareOptionsMenu) ...

Sanity check against tool coverage (never used to set a label): 848 methods ran in the 1-hour Monkey / APE runs on API 27; **0** of them are labelled UNREACHABLE.

## What the re-audit changed (compared with the schema 1 graph)

- **Labels.** The schema 1 graph had 731 reachable, 474 reachable after setup, 205 dead code and 46 framework-only methods. DEAD, FRAMEWORK_ONLY and REACHABLE_AFTER_SETUP are gone: ENV and STATE are structured fields, and the graph has 1,202 REACHABLE and 254 UNREACHABLE methods (no_trigger_in_app 194, framework_never_calls 34, closed_by_configuration 21, branch_never_taken 5). Every UNREACHABLE method was checked again: its name in the app sources, the layouts, menus and manifest, reflection, and every bytecode caller outside the unreachable set (only five methods have one, each explained in its reason); the label rows in `verification.csv` carry the reason of each.
- **Seven labels changed.** Five moved from reachable to UNREACHABLE: `DetailFragment.removeAttachment(Attachment)` (its only caller passes null into a branch that needs a list member), `SettingsFragment.lambda$onResume$16` (the preference `settings_colors_widget` is in no preference XML, so the listener is never registered), the two `BackupHelper.lambda$exportAttachments` lambdas (the only main-code caller passes null, which becomes an empty list) and `SystemHelper.closeCloseable` (its callers are the dead updater and `GeocodeHelper.autocomplete`, which returns early because `MAPS_API_KEY` is empty in the built APK). Two moved the other way: `BuildConfig.<clinit>` (ACRA reads the BuildConfig class by reflection, `@AcraCore(buildConfigClass = BuildConfig.class)`, `OmniNotes.java:45,75`; INFERRED) and the title drag listener `DetailFragment.lambda$initViewTitle$12` (the first graph called it dead because the test tools never drag onto the title; reachability does not depend on the tools).
- **The debug build.** The intro tour (`IntroActivity`, `IntroFragment`, six slides: 20 methods) is closed_by_configuration: `IntroActivity.mustRun()` is `!OmniNotes.isDebugBuild() && ...`, and the standard configuration is the debug build. The edge `mustRun -> OmniNotes.getAppContext` was removed for the same reason (the `&&` stops at the first operand in a debug build).
- **Evidence.** The first graph had 351 edges whose framework claim was written from memory (FW-MEMORY). Now 202 edges cite Android 8.1.0_r1 lines that were printed and read (15 distinct citations: AsyncTask, Handler, Dialog, View / AdapterView click, Activity back / result / finish, LayoutInflater, ActivityThread receiver start, ActivityStarter new-task result, IntentService, Filter, AppWidgetProvider, Parcel, SQLiteOpenHelper); 192 edges carry an INFERRED claim that says what was not read (androidx fragment lifecycle, MaterialDialogs, ButterKnife, EventBus, RxJava / SmartLocation, ACRA, LocalBroadcastManager, the JVM class-initialiser rule). No evidence is tagged FW-MEMORY, DYN or UNVERIFIED any more. Three citations were wrong and replaced: the IntentService, Filter and RxJava edges had cited AsyncTask.
- **Edge classes.** The first graph knew only explicit, standard and page. Now 117 edges are non-standard: EventBus posts (the subscriber is found by event class), ButterKnife binders and click listeners, the reflection loader in `NoteLoaderTask` (`getDeclaredMethod(...).invoke`), the Parcel CREATOR lookup, manifest receivers, services and the DashClock extension started by an action name, RxJava / SmartLocation callbacks, and ACRA. 2,305 edges are explicit and 1,025 standard.
- **Gates.** Gesture prose is a guard, not a state; permissions, other apps, the launcher, time, the location fix, a device locale and exceptions are ENV kinds; notes, categories, tags, attachments, backups, settings and "resumed before in this process" are STATE kinds. `MainActivity.onResume -> ListFragment.onResume / MainActivity.init` and the list page after a resume are valid only after an earlier resume; they now carry that STATE, and the cold start goes onResume -> checkPassword -> init -> ListFragment.
- **Paths, found by reading the routes against the source (30 of 33 checked paths had an error; 29 fixed in `graph_def.py`, one not fixed).** (1) 26 of the 33 first-graph routes used the shortcut that skips the checks of the first resume, one systematic error. (2) The rest were found one by one: the legacy import reached `importNotes`, which only the normal import calls (`importData` now runs per action); the route to `FileHelper.isMediaDocument` went through a merged note, whose attachments are `file://` URIs, while only a URI picked in another app reaches that code (the AttachmentTask path has its own context); Discard changes sent a new note to the widget refresh that only an existing note reaches (the flow is split into a new-note and an existing-note chain); Trash on a checklist opened with the FAB (Trash is hidden for a new note); `IntroActivity.mustRun` in a debug build; missing guards on the DashClock title, the alarm notification icon, the category save (empty name), the geocoder result, the prettified-dates preference, the first logging call, the file-logging switch, the SDK check in `initNotificationChannels` and the LeakCanary process; the CJK word counter text (it named Korean; the code names ja_JP, zh_CN and zh_TW). (3) One route stays wrong: `DbHelper.deleteNote(long,boolean)` goes through a FAB-created editor with the STATE "the open note is the result of Merge", which a STATE cannot express (see Limits).
- **Citations of calls found in the bytecode.** `tools/check_bytecode_lines.py` checks that the cited line of every bytecode-derived edge contains the callee: 11 edges cited a neighbouring line (javac attributes a call inside a chained call, or after a multi-line expression, to another line); all corrected. The checker also learned local classes (`Outer$1Name`).
- **Tool coverage** is only in `sanity_check.csv`: no UNREACHABLE method ran in the Monkey / APE runs (0 contradictions). 79 methods whose best route has an ENV gate ran anyway; that is expected where the runs granted permissions or the gate is an exception branch, and it never changes a label.

## How the checked paths were chosen

`tools/verify_sample.py Omni-Notes 30` draws 30 reachable methods, stratified by what their best route needs (non-standard edge, INFERRED label, STATE gate, ENV gate, long route, plain route), seed 20261025; the sample depends on the graph, so it was drawn again after the structural fixes and reached 273 distinct edges. `verification.csv` holds those 30 plus 3 methods read while sampling (`MediaStoreFactory.<init>`, `DynamicNavigationLookupTable.<init>`, `ListFragment.initNotesList`), 33 path rows in all: 3 correct, 29 fixed, 1 wrong. One sampled method, `DetailFragment.removeAttachment(Attachment)`, turned out UNREACHABLE while its route was read; its path row is kept and its label row is `fixed`. The first-graph routes were rebuilt from the original definitions to see which of them had the shortcut (all 26 non-plain ones had), so the rows tell what was wrong in the first graph; the routes logged are those of the final graph. Besides the paths, `verification.csv` has a label row for each of the 254 UNREACHABLE methods, one for each of the 32 sampled reachable methods whose route stays valid and for the two reachable methods that changed, and 49 edge rows (34 fixed, 15 correct: one per distinct framework citation read).

## What waits for a device (API 27)

Nothing here was confirmed on the emulator (confirmed_by DEVICE: 0). What a device check should settle:

- **Whether the postpone flow of `SnoozeActivity` crashes** (list "Add reminder", notification "postpone"; see the hazard below). If it does, `SnoozeActivity.onReminderPicked` and `onRecurrenceReminderPicked`, which run only after the picker, could not run in the standard configuration; whether a certain crash closes them (closed_by_configuration) is a decision for the rules, not for this file.
- The outside conditions of the 249 methods with an ENV gate: the document picker, camera, video and gallery apps (and the URI the picker app returns: a media-provider document for `FileHelper.isMediaDocument`); the share chooser and browser; the launcher home screen (list and note widgets, the "new note" shortcut) and the notification shade (reminder actions, the import-complete notification); the DashClock and Pushbullet host apps; `NotificationListener` access; the boot receiver; another app's intent (share, hashtag link, camera action).
- Time: a reminder set a minute ahead fires through `AlarmManager` and `AlarmReceiver` (ENV time).
- Location: the permission dialog, the 2 s timeout without a fix (`GeocodeHelper`), the geocoder and the Google Play services provider of the play flavor (`LocationGooglePlayServicesWithFallbackProvider`).
- An older database on disk (`DbHelper.onUpgrade`, `UpgradeProcessor`): needs an install over an older version.
- The device locale ja_JP, zh_CN or zh_TW for the ideogram word counter, and the file-logging switch turned on before the next process start (`LogDelegate` reads it once).
- The storage permission dialogs (export, import, delete backup, legacy import, logging switch).
- That a configuration change (rotation, a language change) relaunches `MainActivity` and the editor: `MainActivity` declares no `android:configChanges` (`AndroidManifest.xml:65-70`; only `GalleryActivity` does, line 119). The graph treats rotation as an ENV gate on the edges that need a recreated editor.

## Hazard candidates (from reading the code, not reproduced)

- **Opening a link or e-mail in a note needs a camera feature.** The "Open" button of the link dialog checks `IntentChecker.isAvailable(..., FEATURE_CAMERA)` (`DetailFragment.java:292-304`), so on a device without a camera feature it shows "no application can perform this action".
- **`SnoozeActivity` (reminder postpone) may throw on API 27.** It uses `OmniNotesTheme.NoDisplay` with `windowNoDisplay` true (`AndroidManifest.xml:167`, `styles.xml:57-64`), the app targets SDK 28 (`gradle.properties:21`), and its postpone branch shows the picker without calling `finish()` (`SnoozeActivity.java:82-93, 104-119`; `ReminderPickers.java:51-89`). `Activity.performResume` throws `IllegalStateException` when an activity whose window has no display has not finished before `onResume` completes and the target SDK is above 22 (`Activity.java:7003-7004, 7112-7123`, read in the Android 8.1 source). Not reproduced.
- **`MainActivity` misses `PasswordRemovedEvent` after its first stop.** It registers with EventBus in `onCreate` but unregisters in `onStop` and never registers again (`MainActivity.java:98,124`), so the "password removed" message and re-init do not happen after the app was in the background once.
- **An empty sketch is dropped silently.** `SketchFragment.save()` writes only when `SketchView.getBitmap()` is not null, which needs at least one stroke (`SketchView.java:204-207`); leaving an empty canvas shows no message.
- **List "Add reminder" ends the action mode at once.** `ListFragment.addReminders` starts `SnoozeActivity` with `FLAG_ACTIVITY_NEW_TASK` through `startActivityForResult` (`ListFragment.java:893-899`), and the activity manager answers such a start with `RESULT_CANCELED` immediately (`ActivityStarter.java:1355-1370`, read), so `onActivityResult` closes the action mode before the picker is used.
- Found while reading paths: the `S_DLG_DISCARD` back edge and several dialog and page returns are modelled as returning to the least-state page (see Limits); the real editor keeps the note it had.

## Limits

- **androidx, MaterialDialogs, ButterKnife, EventBus, RxJava / SmartLocation, ACRA and LocalBroadcastManager sources were not read.** 192 of the 3,803 edges carry an INFERRED claim, mostly the fragment lifecycle that every route through a fragment uses and the dialog callbacks, so 1,145 of 1,456 labels are confirmed INFERRED and 311 SOURCE. A path marked SOURCE_OK means every app step was read; the library steps on it are still INFERRED.
- **Bytecode-derived edges (1,437 of 3,803) carry no guards unless a rule added one.** The best route minimises the number of ENV-gated edges, then of STATE-gated edges, then the steps, and ignores guards, so a route that was not read can still contain a guarded step; 30 of the 33 routes that were read had an error. The label (REACHABLE) holds as long as some valid route exists, which was checked for the sampled methods only. Only 33 of 1,202 routes were read; the other 1,169 are UNCHECKED, and the guard-less bytecode edges are where more errors should be expected.
- **A STATE cannot say how a screen was opened.** The editor pages (new, edit, checklist, archived, trashed) and the list pages are modelled once; a note opened by Merge, from a widget or from a notification is a different start but the same page. `DbHelper.deleteNote(long,boolean)` needs the editor that Merge opens (`mergedNotesIds` from the intent, `DetailFragment.java:1616`), which the best route replaces with a FAB-created editor plus a STATE; it would need its own editor context with its own Back and save chain. Back from a dialog or a settings screen returns to the least-state page (`S_LIST@NOTES`, `S_DETAIL@NEW`) except where the origin is certain; the "Discard changes" flow is the one that was split by origin.
- Page edges (`ENTERS`) skip the code between a callback and the page it opens, so a route to code inside that stretch must use the explicit call edges; where both exist the best route may use the page edge and then a later gesture (for example the edge swipe that builds a new editor fragment) to reach the same constructor.
- androidx preference dialogs (language, colours, checked-items behaviour, max video size, snooze delay) are described in the tap text of the preference, not as pages. Runtime-permission dialogs are not pages: the permission is an ENV gate on the edge that needs it.
- Rotation and process recreation are modelled only as lifecycle callbacks (`onSaveInstanceState`, `OmniNotes.onConfigurationChanged`); the saved-state restore of the editor and the list is not.
- The standard configuration is the play flavor, debug build (`BuildConfig.BUILD_TYPE` "debug"), fresh install, API 27; the beta, alpha and foss sources are not part of it.

## JSON shape (short)

```
{ "schema": 2, "title", "screens": {page: description}, "methods": [...], "verdict": {method: REACHABLE|UNREACHABLE},
  "labels": {method: {unreachable: {kind, text}, env: [{kinds, text}], state: [{kinds, text}], route_edge_classes, explicit_standard_route,
                      confirmed_by, source_ref, path_status}},
  "edges": [ {id, src, dst, kind, edge_class, via, trigger, gui[], guard, reads[], writes[], note, needs_state, state_kinds, env, env_kinds, evidence, class_basis} ],
  "paths": [ {method, edges[], edge_classes, explicit_standard_only, env, state, verified_by, ref} ], "verification": {...} }
```

`src`/`dst` are methods (`Class.method`, overloads as `Class.method(Type,Type)`) or pages (`S_...`). A suffix `@CONTEXT` is the same method or page in a specific context. Edge ids are a hash of the edge content, so they stay stable when other edges change.
