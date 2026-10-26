"""Write graphs/<App>/KIRO_WORKLIST.md: one row per distinct evidence claim of a schema 2 build that no source line backs.

Usage (from work/): python3 -I tools/make_worklist.py <App>
Reads graphs/<App>/out/*_trigger_graph.json and out/methods.csv (build first). A claim is an evidence segment (split at ';') that starts with
FW-MEMORY, INFERRED, DYN or UNVERIFIED, on an edge whose evidence is not fully sourced. A segment that is only a tag (no text) is grouped by
the edge trigger. Each row gets an action from the rules below (first match wins; the rules of the app come first):
  S = read the cached framework / app lines and cite them, I = keep the claim but write INFERRED and say what was not read, R = delete a DYN segment.
A row with no rule shows '?'; the tool prints those so a rule can be added here. The list ends with the framework files that are on disk.
"""
import collections
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_graph as b  # noqa: E402

ANOTHER_APP = ('Another app does this (launcher, document picker, share sheet, receiving app, print service). Keep it as `INFERRED <what the other app does> '
               '(another app, its source was not read)`; the ENV other_app gate already says so.')
WEBVIEW = 'The WebView engine is native code that is not in the Java sources. Keep it as `INFERRED the WebView engine (Chromium, native code outside the Java sources) <what it does>`.'
LIBCORE = 'Java library code (libcore) is not held here. Keep it as `INFERRED java.io / java.util library behaviour (libcore source not read)`.'
ANDROIDX = ('The app uses the androidx library `%s` (not the android.app class), whose source is not held, and nothing may be downloaded. '
            'Keep the claim as `INFERRED androidx %s <what it does> (androidx source not read)`.')
APP_LINE = 'The text already names app lines. Turn it into `SRC File.java:<lines>`: print the lines (`sed -n` on the app source under final_java_only/<App>/app/), check they show what the claim says, keep a short reason in the text.'

COMMON = [
    (r'rotation triggers the relaunch', 'S', 'Delete this segment and add `SRC AndroidManifest.xml:<lines of the activity elements> (no android:configChanges)`. The relaunch itself is cited by the existing ActivityThread lines.'),
    (r'TextView\.onRestoreInstanceState', 'S', 'core/java/android/widget/TextView.java: find `onRestoreInstanceState`; cite the lines where it calls setText for the saved text.'),
    (r'Chromium|WebView|onPageFinished|WebViewClient', 'I', WEBVIEW),
    (r'picker returns a content|ChooserActivity|receiving apps|ContentResolver\.getType from the receiving|chooser is an activity|print preview|print spooler|DocumentsUI|Launcher3|PendingIntent started from the launcher', 'I', ANOTHER_APP),
    (r'libcore|Arrays\.sort|FileOutputStream', 'I', LIBCORE),
    (r'UNVERIFIED', 'I', 'Not checked. Reword as `INFERRED <the open point> (not checked)`.'),
    (r'DYN baseline|DYN ', 'R', 'Delete the DYN segment (tool coverage is not evidence). If the edge then has no support, read the code around it and cite the line, or write `INFERRED` with the reason.'),
]

BY_APP = {
    'Diary': [
        (r'DatePickerDialog Cancel', 'S', 'core/java/android/app/DatePickerDialog.java: the negative button gets a null listener; core/java/com/android/internal/app/AlertController.java: a button click dismisses the dialog.'),
        (r'default Back behaviour', 'S', 'Cite `core/java/android/app/Activity.java:3001-3010` (F_BACK) and `SRC Settings.java` (no onBackPressed override: grep it).'),
        (r'DatePicker calls OnDateChangedListener', 'S', 'core/java/android/widget/DatePicker.java (fetched): the lines where a change calls the OnDateChangedListener.'),
        (r'stopped activity restarts', 'S', 'core/java/android/app/ActivityThread.java: performRestartActivity / handleStartActivity; core/java/android/app/Activity.java: performRestart.'),
        (r'ActivityStarter', 'S', 'services/core/java/com/android/server/am/ActivityStarter.java (fetched): the lines that look for a task with the same affinity or add FLAG_ACTIVITY_NEW_TASK. If the edge also has an UNVERIFIED segment, keep that one as INFERRED.'),
        (r'collapse button|collapseActionView', 'S', 'core/java/android/widget/Toolbar.java (fetched): the collapse button of the expanded action view calls collapseActionView.'),
        (r'AlertDialog.*(OnCancelListener|cancel)|cancel without listener|null neutral listener', 'S', 'Cite the app lines the text names and core/java/android/app/Dialog.java (fetched): cancel() sends the cancel message only when set, then dismiss().'),
        (r'openInputStream', 'S', 'core/java/android/content/ContentResolver.java (fetched): openInputStream, openAssetFileDescriptor, and the call into the provider openFile.'),
        (r'ContentResolver\.query acquires', 'S', 'core/java/android/content/ContentResolver.java (fetched): query -> acquireUnstableProvider; core/java/android/app/ActivityThread.java: acquireProvider finds the local provider.'),
        (r'preference inflater', 'S', 'core/java/android/preference/GenericInflater.java (fetched): createItem uses mConstructorSignature (Context, AttributeSet) and constructor.newInstance.'),
        (r'Back finishes the root activity', 'I', 'Process lifetime is not in the sources read. Keep it as `INFERRED the process may stay alive after the last activity finishes`.'),
        (r'ActionMode', 'S', 'core/java/com/android/internal/policy/DecorView.java (fetched): startActionMode; core/java/android/app/Activity.java: onActionModeStarted. If the WebView part cannot be shown, keep that part INFERRED.'),
        (r'FragmentManager moves|fragment lifecycle follows|fragment resumes', 'S', 'core/java/android/app/FragmentManager.java:1141,1237,1322 (moveToState, performCreate, performResume) and the dispatchCreate / dispatchResume calls in core/java/android/app/Activity.java.'),
        (r'INFERRED SRC Diary\.java', 'S', APP_LINE),
        (r'DialogPreference dismissal', 'S', 'core/java/android/preference/DialogPreference.java:386-395 (onClick / onDismiss -> onDialogClosed).'),
    ],
    'hash-checker': [
        (r'FragmentManager runs the lifecycle after commit', 'I', ANDROIDX % ('androidx.fragment.app.FragmentManager', 'FragmentManager') + ' Say that show()/commit() schedule the transaction and the manager then runs the fragment lifecycle.'),
        (r'Fragment/FragmentActivity\.onCreatePanelMenu|Activity\.onMenuItemSelected -> FragmentManager', 'I', ANDROIDX % ('androidx.fragment.app.FragmentActivity', 'FragmentActivity') + ' The Activity side (Activity.java) may be read and cited separately if it is in the cache.'),
        (r'Fragment\.startActivityForResult delivers|RESULT_CANCELED on Back', 'S/I', 'S for the Activity side: core/java/android/app/Activity.java (cached): an activity that finishes without setResult returns RESULT_CANCELED (mResultCode). I for the androidx Fragment side: `INFERRED androidx Fragment routes startActivityForResult through its host and delivers the result to onActivityResult (androidx source not read)`.'),
        (r'RecyclerView', 'I', ANDROIDX % ('androidx.recyclerview.widget.RecyclerView', 'RecyclerView') + ' Say what it does (setAdapter -> layout -> adapter callbacks / scroll callbacks).'),
        (r'AsyncTask', 'S', 'core/java/android/os/AsyncTask.java (cached): execute -> executeOnExecutor(SERIAL_EXECUTOR) -> doInBackground in the worker; finish() -> onPostExecute / onCancelled on the main thread (via the Handler). Cite the lines you printed for the part the claim names.'),
        (r'Dialog\.show -> dispatchOnCreate|Dialog\.show -> OnShowListener', 'S', 'core/java/android/app/Dialog.java (cached): show() -> dispatchOnCreate -> onCreate; show() -> sendShowMessage -> OnShowListener. (androidx AlertDialog / AppCompatDialog extend android.app.Dialog; say the subclass part is INFERRED androidx.)'),
        (r'ContextThemeWrapper', 'I', 'core/java/android/view/ContextThemeWrapper.java is not in the cache. Keep it as `INFERRED ContextThemeWrapper.getTheme builds the theme from the wrapped context (source not read)`.'),
        (r'Application\.onConfigurationChanged', 'S', 'core/java/android/app/ActivityThread.java (cached): handleConfigurationChanged -> performConfigurationChangedForActivity / the ComponentCallbacks loop that reaches Application.onConfigurationChanged. Grep `onConfigurationChanged` and cite the lines you printed.'),
        (r'TextView\.setText always notifies', 'S', 'core/java/android/widget/TextView.java (cached): setText -> sendBeforeTextChanged / sendOnTextChanged / sendAfterTextChanged. Keep the existing SRC segment of the edge.'),
        (r'ORMLite|SQLiteOpenHelper', 'I', 'Library or framework code that is not in the cache (ORMLite; android.database.sqlite). Keep it as `INFERRED <what the library does> (source not read)`.'),
        (r'BottomSheetDialogFragment|AlertDialog dismissal', 'I', ANDROIDX % ('com.google.android.material.bottomsheet.BottomSheetDialogFragment / androidx.appcompat.app.AlertDialog', 'BottomSheetDialogFragment') + ' Say what dismiss does.'),
        (r'AlertDialog\.cancel|the sheet is not dismissed', 'S/I', 'S: core/java/android/app/Dialog.java (cached): cancel() sends the cancel message, then dismiss(). I: the dialog class is androidx.appcompat.app.AlertDialog; say `INFERRED androidx AlertDialog extends android.app.Dialog (androidx source not read)`. Keep the SRC LanguagesListAdapter / ThemesListAdapter line that shows the sheet is not dismissed.'),
        (r'INFERRED SRC .*\(assert\)', 'S', APP_LINE + ' The text says `(assert)`: print the line and say what the assert checks.'),
        (r'INFERRED SRC ', 'S', APP_LINE),
        (r'no text; trigger: Home / recents|no text; trigger: .*screen off', 'S', 'core/java/android/app/ActivityThread.java (cached): handlePauseActivity -> performPauseActivity -> Activity.performPause (core/java/android/app/Activity.java) -> onPause. Cite the lines you printed.'),
        (r'no text; trigger: (Back in the foreground|The activity returns to the foreground)', 'S/I', 'S: core/java/android/app/ActivityThread.java (cached) handleResumeActivity -> performResumeActivity -> Activity.performResume -> onResume. I for the fragment part: the androidx FragmentActivity.onResume dispatches resume to the added fragments (`INFERRED androidx FragmentActivity ... (androidx source not read)`).'),
        (r'no text; trigger: Class initialisation', 'I', 'JVM class initialisation on first use is a Java language rule, not in the sources read. Write `INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)`.'),
        (r'no text; trigger: Next launch', 'I', 'Process lifetime is not in the sources read. Write `INFERRED after the last activity finishes the process may stay alive, so static / Application state can be reused on the next launch`.'),
    ],
}


def action_for(app, text):
    for rx, act, hint in BY_APP.get(app, []) + COMMON:
        if re.search(rx, text, re.I):
            return act, hint
    return '?', 'No rule: read the edge, then either cite the framework lines (S) or reword it as INFERRED with the reason (I).'


def main(argv):
    app = argv[1]
    gdir = 'graphs/%s' % app
    jp = glob.glob('%s/out/*_trigger_graph.json' % gdir)[0]
    prefix = os.path.basename(jp).replace('_trigger_graph.json', '')
    g = json.load(open(jp))
    E = {x['id']: x for x in g['edges']}
    rows = list(csv.DictReader(open('%s/out/methods.csv' % gdir, encoding='utf-8')))

    claims = collections.OrderedDict()
    for x in g['edges']:
        if b.edge_sourced(x):
            continue
        for seg in (x['evidence'] or '').split(';'):
            seg = seg.strip()
            if not seg or seg.split()[0] not in ('FW-MEMORY', 'INFERRED', 'DYN', 'UNVERIFIED'):
                continue
            if seg in ('FW-MEMORY', 'INFERRED', 'DYN', 'UNVERIFIED'):          # a bare tag: the trigger says what it is about
                seg = '%s (no text; trigger: %s)' % (seg, (x['trigger'] or '').strip()[:110])
            claims.setdefault(seg, []).append(x['id'])
    affected = collections.defaultdict(set)
    for r in rows:
        if r['verdict'] != 'REACHABLE':
            continue
        for eid in r['route_edge_ids'].split():
            for seg, ids in claims.items():
                if eid in ids:
                    affected[seg].add(r['method'])
    order = sorted(claims.items(), key=lambda kv: (-len(affected[kv[0]]), -len(kv[1])))

    caches = [c for c in ('fw_src/android-8.1.0_r1', '%s/.plan/fw_src/android-8.1.0_r1' % gdir) if os.path.isdir(c)]
    local = []
    for c in caches:
        for dp, _, fn in os.walk(c):
            for f in fn:
                local.append((c, os.path.relpath(os.path.join(dp, f), c)))
    local.sort(key=lambda t: t[1])

    lines = ['# %s: evidence work list for the schema 2 conversion' % app, '',
             'Generated from the current build (`python3 -I tools/build_graph.py %s %s`). One row per distinct claim in `evidence` that no source line backs: **%d claims on %d edges**. '
             'Edit only `%s/graph_def.py`. After each batch rebuild and run `python3 -I tools/check_citations.py %s`.' % (
                 gdir, prefix, len(claims), len({i for ids in claims.values() for i in ids}), gdir, app), '',
             '**Actions.** `S` = read the framework / app lines and cite them as `FW-SRC <path>:<lines>` or `SRC File.java:<lines>`; `I` = keep the claim but make it start with `INFERRED` and say what is not read; '
             '`R` = remove a `DYN` segment (tool coverage is not evidence); `S/I` = two parts, see the row.',
             'A citation counts only if you printed the lines (`sed -n "<a>,<b>p" <file>`) and they show what the claim says. Never cite from memory.', '',
             '| # | Claim (as in the evidence) | Label | Edges | Methods that depend on it | Action | What to do / where to look | Find it with |', '|---:|---|---|---:|---:|---|---|---|']
    no_rule = []
    for i, (seg, ids) in enumerate(order, 1):
        label, text = seg.split(None, 1) if ' ' in seg else (seg, '')
        act, hint = action_for(app, seg)
        if act == '?':
            no_rule.append(seg)
        words = re.sub(r'[^\w ]', ' ', text.replace('no text; trigger:', '')).split()[:5]
        find = 'grep -n "%s" %s/graph_def.py' % (' '.join(words), gdir) if words else ''
        ex = E[ids[0]]
        lines.append('| %d | %s | %s | %d (e.g. %s %s -> %s) | %d | **%s** | %s | `%s` |' % (
            i, seg.replace('|', '/')[:190], label, len(ids), ex['kind'], ex['src'], ex['dst'], len(affected[seg]), act, hint, find.replace('|', '/')))

    unre = [(m, l['unreachable']) for m, l in g['labels'].items() if l.get('unreachable')]
    lines += ['', '## UNREACHABLE methods (%d): check each once more' % len(unre), '',
              'For each: grep the call sites in the app source (`grep -rn "<name>" final_java_only/%s/app/`), read the cited lines, and write one `label` row in `verification.csv` (result `correct`, or `fixed` after you changed it). '
              'A reason that has an `INFERRED` part stays INFERRED; do not add a citation you did not print.' % app, '',
              '| Method | Kind | Reason | Reference |', '|---|---|---|---|']
    for m, u in sorted(unre):
        lines.append('| %s | %s | %s | %s |' % (m, u['kind'], u['text'].replace('|', '/')[:400], g['labels'][m]['source_ref']))

    lines += ['', '## Framework files already on disk (use only these; do not download anything)', '']
    for c, rel in local:
        lines.append('- `%s/%s`' % (c, rel))
    open('%s/KIRO_WORKLIST.md' % gdir, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('%s: %d claims; %d without a rule; %d UNREACHABLE rows' % (app, len(claims), len(no_rule), len(unre)))
    for s in no_rule:
        print('  NO RULE:', s[:150])


if __name__ == '__main__':
    main(sys.argv)
