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
