# Diary graph: verification record (first iteration)

All commands were run from `<root>/work`. Tools were not modified (`tools/build_graph.py` md5 `3e630932a416d7e354daee88a20a360c` before and after).

## Build

`python3 -I tools/build_graph.py graphs/Diary diary` -> exit 0, `errors: 0`, `warnings: 0`.
Final report: 286 methods, 34 pages (75 page nodes with variants), 1435 edges; 263 REACHABLE, 2 REACHABLE_AFTER_SETUP, 17 DEAD, 4 FRAMEWORK_ONLY.

## Gates

- **a. Contradictions with the baseline: 0.** None of the 21 DEAD/FRAMEWORK_ONLY methods ran in APE or Monkey (`build_report.txt`: "0 DEAD/FRAMEWORK_ONLY but hit").
- **b. Every baseline-hit method has a path.** 187 universe methods ran in APE or Monkey; with 0 errors (no UNRESOLVED) and 0 contradictions, all 187 are REACHABLE except `DatePickerPreference.onSetInitialValue` (APE-hit), which is REACHABLE_AFTER_SETUP (it needs a date page saved on an earlier Settings visit).
- **c. Negative verdicts enumerate call sites and scope.** Each of the 17 DEAD reasons names every call site of the target symbol (or "no call site") and ends with the search-scope sentence (11 sources text search, bytecode invoke/invokedynamic scan of the 23 compiled classes, res/ XML, manifest, reflection/string dispatch, JacocoInstrument). Each of the 4 FRAMEWORK_ONLY reasons also lists the framework call sites found (Preference.java:292-294 is the only `onGetDefaultValue` caller in the downloaded preference sources; ContentProvider.Transport insert/update/delete only after `enforceWritePermission`) and the framework files searched.
- **d. Shortest paths read.** I read the `shortest_path` and `gui_steps_on_shortest_path` of all 78 candidate targets first, then of all 187 baseline-hit methods (265 paths, including the 36 named in plan step 9). Shortcuts found and fixed are listed below; every fix was followed by a rebuild and a re-read of the affected paths.

## Round A cross-check against bytecode (both directions)

Script over `.plan/app_callers.txt` vs the built JSON:
- App call sites without a matching non-REGISTER edge: 34, all explained: 22 `invokedynamic` listener/lambda creations (modelled as REGISTER edges), 8 calls made only inside DEAD methods (`getEntries` x2, `copyFile(Context,Uri,Uri)` x2, the `getThumbnail` overloads x4), `Diary.cancel -> load` (unreachable else branch, NOTES), and the 3 lambda objects built in `FileUtils.<clinit>` (never invoked, DEAD).
- CALL edges without a bytecode call site: 31, all explained: constructors of private inner classes called through their synthetic constructor (`GestureListener`, `QueryTextListener`, `EntryDecorator`), class initialisation (`<clinit>` on first use), and interface calls (`PathStrategy`, `EventListener`) to their only implementation.

## Shortcuts found while reading paths, and the fix

| # | Method(s) | Wrong path | Fix |
|---|---|---|---|
| 1 | `FileProvider.query`, `copyOf(..)` x2, `SimplePathStrategy.getFileForUri` | Editor opened from Files -> `FileUtils.getDataColumn` -> `FileProvider.query` (a Files document is not Diary's own URI) | `@SELF` chain (`Diary.resolveContent@SELF -> FileUtils.getPath@SELF -> getDataColumn@SELF -> FileProvider.query`) used only by the self-share contexts `Diary.<init>@SELF_TEXT/@SELF_IMAGE`; now Share… -> an app reading the stream |
| 2 | `Diary.alertDialog(int,String,int)`, `QueryHandler.insertEvent`, `onInsertComplete` | onCreate -> today -> changeDate -> save() in a brand-new instance (changed is false there) | `@START` contexts for today/index/changeDate inside onCreate, without the save/animateAccept edges |
| 3 | `Diary.dateCheck(CharSequence,String)` | READ permission grant answered with the TEMPLATE branch | one permission page and result context per request code (`S_PERMISSION@DIARY_READ/_WRITE/_TEMPLATE`, `onRequestPermissionsResult@READ/...`) |
| 4 | `Editor.alertDialog(int,String,int)` | REQUEST_READ grant followed by the REQUEST_WRITE branch | Editor permission pages/results split per request code (`EDITOR_<ctx>_READ/_WRITE`); now type -> Accept -> write -> alert |
| 5 | `QueryHandler.insertEvent`, `onInsertComplete`, `Diary.eventCheck` | saving the help text, which has no line starting with "@ HH:MM" | `@EVENT` chain: type an event line -> `S_DIARY_EDIT_CHANGED@EVENT` -> Accept / pause -> `save()@EVENT` -> `eventCheck@EVENT`; the base edge got needs_state |
| 6 | `Diary.save()` and its callees | onPause / Back from an unchanged page | `onPause@CHANGED`, `onBackPressed@CHANGED/@EDIT_CHANGED` from the pages where changed can be true |
| 7 | `Diary.animateAccept` | S_DIARY_VIEW -> Back -> changeDate -> animateAccept (needs edit mode) | `changeDate(Calendar)@EDIT` (Back from edit pages) holds the edge; base changeDate has none |
| 8 | `Diary$QueryTextListener.onQueryTextChange` | S_DIARY_VIEW -> Edit tap -> onQueryTextChange (collapse happens only while searching) | `lambda$setListeners$10@SEARCH` / `$7@SEARCH` carry the collapse edges; the expansion edge got its gui step |
| 9 | `Diary.addLink`, `addLinkDialog`, `lambda$addLink$21` | gui step "Pick an image…" (an image goes to addMedia) | picker result contexts `@ADD_MEDIA`, `@ADD_FILE`, `@CANCELED` with their own gui |
| 10 | `Diary$ZipTask.lambda$doInBackground$0` | plain Save with the default path | `@BADPATH` gesture (path in a missing folder); base error edge marked `env = ENV_IO_ERROR`. The CSV still prints the env path on a tie (TOOL_ISSUES.md 1, 5); NOTES explain |
| 11 | `Editor.onRestoreInstanceState` | gui "Press Home ; Rotate the screen" | separate `onSaveInstanceState@ROTATE_<ctx>` for rotation |
| 12 | `SettingsFragment.onSharedPreferenceChanged@INDEX_PAGE/@TEMPLATE_PAGE` | OK without changing the date | `S_DLG_DATE_PREF@X_CHANGED` entered by the date-changed lambda; only its OK reports a change |
| 13 | `S_DIARY_BROWSE` | entered from `Diary$1.onPageFinished` (framework callback) | edge removed; the link handler `shouldOverrideUrlLoading` enters it |
| 14 | `Diary.template`, `dateCheck(CharSequence,String)`, `today` | base Edit tap / today() -> template() without the Settings steps | `@TEMPLATE` Edit tap from `S_DIARY_VIEW@TEMPLATE`; base edges have needs_state |

## Known approximations left as guard text (not shortcuts in the printed paths)

- Data guards: Previous/Next enabled, Up arrow shown, at least one entry for Find all, day/month/year folders for the navigation helpers.
- `Diary.template` needs an empty entry: the gui step says "On an empty day … tap the Edit button".
- Which `FileUtils.getPath` branch runs depends on the Files root the document comes from (gui hint on the Editor entry).
- `changeDate(Calendar) -> save()` (guard changed) is shared by all navigation handlers; the printed path of `save()` goes through `onPause@CHANGED`, so no path uses it.
- Dialogs return to `S_DIARY_VIEW` (or a named page) instead of the exact page they were opened from.
