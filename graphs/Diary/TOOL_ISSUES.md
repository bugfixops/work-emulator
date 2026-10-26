# Shared-tool issues seen while building Diary

Tool: `work/tools/build_graph.py` (md5 `3e630932a416d7e354daee88a20a360c`, unchanged during this build). Nothing in `tools/` was edited; every workaround lives in `graphs/Diary/graph_def.py`.

## 1. An env-dependent shortest path is shown without the "needs environment" note

`methods.csv` adds "needs environment: ..." only when a method has no env-free path at all (`env_gated`). The path it prints is the BFS shortest path with env edges allowed. When the shortest path uses an `env` edge but a longer env-free path exists, the CSV shows the env path and says nothing.

Affected in Diary (checked by re-running the same BFS on `out/diary_trigger_graph.json`):
- `Diary.alertDialog(int,String,int)` and `Diary$ZipTask.lambda$doInBackground$0`: the printed path needs `ENV_IO_ERROR`. Env-free alternative: Backup… with a path in a missing folder (`Diary.lambda$backup$19@BADPATH`).
- 10 methods whose shortest path runs through the first-start help text (`Diary.onResume -> S_DIARY_VIEW_CHANGED`, `env = ENV_PERM`): `Diary.save()`, `save(CharSequence)`, `eventCheck`, `positionCheck`, `updateWidgets`, `cancel`, `alertDialog(int,int,int,int,OnClickListener)`, `lambda$cancel$17`, `Diary$2.beforeTextChanged/onTextChanged/afterTextChanged`. ENV_PERM is the baseline's normal state, so these paths are still realistic.

Workaround: `NOTES` entries for the two ENV_IO_ERROR methods (they show in the CSV note column); the README explains the ENV_PERM case. A fix in the tool would be to print the env-free path when one exists, or to list the env conditions of the printed path.

## 2. Menu items without the `action_` prefix get no menu label

`menu_label()` only recognises `android.R.id.home` and ids starting with `action_`. Diary's ids are `share`, `addTime`, `goToDate`, and so on, so `gui_steps_on_shortest_path` falls back to the GUI edge's own text. Workaround (plan 4.3): each item's CALL edge carries its own `gui` step ("Tap More options (⋮) -> Share…"), so the CSV reads "Open the action bar menu (icons or More options ⋮) ; Tap More options (⋮) -> Share…".

## 3. Only `gui[0]` reaches the CSV; `needs_state` text never does

`gui_steps()` takes the first gui entry of each edge, so alternatives listed after it ("or tap Discard") are only in the JSON. Edges that differ by gesture were split into contexts where it mattered (picker results `@ADD_MEDIA` / `@ADD_FILE` / `@CANCELED`). The `needs_state` text of a `REACHABLE_AFTER_SETUP` path is not printed either; `NOTES` entries cover the two such methods (`DatePickerPreference.onSetInitialValue`, `FileUtils.getPathWithoutExtension`).

## 4. Evidence counts use the first word only

`build_report.txt` counts the leading label of each evidence string. Edges whose evidence combines labels (for example "SRC Diary.java:...; FW-MEMORY ...") count once, under the first label. The README gives both numbers (leading label, and edges that mention FW-MEMORY / UNVERIFIED / DYN anywhere).

## 5. Ties are broken by edge order

For two shortest paths of equal length the BFS keeps the one whose edges were defined first. This is deterministic but means the order of `e(...)` calls in `graph_def.py` decides which of two equally short journeys the CSV prints (for example the plain Save vs. `@BADPATH` path to `Diary$ZipTask.lambda$doInBackground$0`). Not a bug; worth knowing when reading paths.
