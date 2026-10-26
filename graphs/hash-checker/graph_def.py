# hash-checker v3.7.3 (hash-checker/hash-checker@5cf7961, flavor thirdPartyStores, debug) trigger graph definition.
# Hand-written part: entry points, framework callbacks, gestures, pages, state/environment gates.
# Direct app->app calls come from tools/extract_calls.py (bytecode); USE_AUTO adds them to every pair not written here.
# Evidence labels: SRC (app lines read), FW-SRC (Android 8.1.0_r1 lines read), INFERRED (not read; the text says what was not read).

TITLE = 'hash-checker v3.7.3 trigger graph'
USE_AUTO = True

ENV_SAF = 'outside package: the system file picker (com.android.documentsui) must return a document'
ENV_EXT = 'outside package: another app (launcher shortcut, share/VIEW intent, adb) starts Hash Checker'
ENV_NOAPP = 'no app on the device can handle the intent (no browser / Play Store / email app)'
ENV_EXC = 'an exception is thrown (I/O, SQL, missing handler app, bad URI); LogUtils.e only logs it in debug builds'
NEED_GEN = 'A hash was generated first (the Export action needs a non-empty generated field)'
NEED_HIST = 'At least one hash was generated with "Save result to History" on (default on)'
ENV_RATE = 'six successful hash generations in one install (rate dialog shows when the counter equals 5, once)'

MODES = ['EMPTY', 'TEXT', 'FILE', 'FOLDER']
MAIN = lambda m: 'S_MAIN_' + m

SCREENS = {
    'S_ENTRY': 'Outside the app: launcher icon, launcher shortcuts (long-press), other apps or adb sending VIEW/SEND',
    'S_EXIT': 'MainActivity finished (double Back, "Exit now", old instance after a language/theme restart); the process may survive (App.appComponent is static)',
    'S_MAIN_PAUSED': 'Calculator on top, activity stopped (Home, recents, an external window on top)',
    'S_HISTORY_PAUSED': 'History on top, activity stopped',
    'S_SETTINGS_PAUSED': 'Settings on top, activity stopped',
    'S_FEEDBACK_PAUSED': 'Feedback on top, activity stopped',
    'S_WEB_PAUSED': 'Privacy-policy WebView on top, activity stopped',
    'S_MAIN_EMPTY': 'Calculator, no source selected (From button reads "From"): Generate and Export only show hint snackbars',
    'S_MAIN_TEXT': 'Calculator, Text source selected (From button reads "Text")',
    'S_MAIN_FILE': 'Calculator, File source selected via picker, VIEW or SEND (button reads "File")',
    'S_MAIN_FOLDER': 'Calculator, Folder source selected via the folder picker (button also reads "File")',
    'S_MAIN_GENERATING': 'Modal "Generating hash, please wait..." progress dialog while HashCalculatorTask runs; Back is ignored',
    'S_MAIN_EXIT_PENDING': 'Exit snackbar with "Exit now"; a second Back within 300 ms finishes the activity',
    'S_SNACKBAR_INFO': 'Info snackbar with an OK action (non-modal, disappears after a short time)',
    'S_SHEET_SOURCE': 'Bottom sheet "From": Text / File / Folder (variant = calculator mode underneath)',
    'S_SHEET_ACTIONS': 'Bottom sheet "Actions": Generate / Compare / Export .txt (variant = calculator mode underneath)',
    'S_SHEET_HASHTYPE': 'Bottom sheet with the 18 hash algorithms (variant = calculator mode underneath)',
    'S_DLG_TEXT_INPUT': 'Text input dialog (EditText + Close + Add, keyboard forced visible)',
    'S_DLG_RATE_APP': 'Alert dialog "If you like the app..." Rate / Cancel',
    'S_EXT_PICK_FILE': 'System file picker (ACTION_OPEN_DOCUMENT, */*) in another package',
    'S_EXT_PICK_FOLDER': 'System folder picker (ACTION_OPEN_DOCUMENT_TREE) in another package',
    'S_EXT_CREATE_TXT': 'System "save as" dialog (ACTION_CREATE_DOCUMENT text/plain) in another package',
    'S_EXT_CREATE_ZIP': 'System "save as" dialog (ACTION_CREATE_DOCUMENT application/zip) in another package',
    'S_EXT_OTHER_APP': 'Browser, Play Store or email chooser opened by an intent (no result returned)',
    'S_HISTORY_LOADING': 'History: progress bar while HistoryItemsLoaderTask runs',
    'S_HISTORY_EMPTY': 'History: "History items not found", trash icon hidden',
    'S_HISTORY_LIST': 'History: rows (tap copies the hash), trash icon visible',
    'S_DLG_CLEAR_HISTORY': 'Alert dialog "Delete all history items?" OK / Cancel',
    'S_SETTINGS': 'Settings preference list (Rate row hidden in this flavor)',
    'S_SHEET_LANGUAGES': 'Bottom sheet with 21 languages',
    'S_DLG_CHANGE_LANGUAGE': 'Alert dialog "restart to change the language" OK / Cancel',
    'S_SHEET_THEMES': 'Bottom sheet Light / Dark',
    'S_DLG_CHANGE_THEME': 'Alert dialog "restart to change the theme" OK / Cancel',
    'S_SHEET_PRIVACY': 'Bottom sheet with the privacy-policy link',
    'S_SHEET_AUTHOR': 'Bottom sheet with 6 author links',
    'S_SHEET_LIBRARIES': 'Bottom sheet with 2 library links',
    'S_FEEDBACK': 'Feedback page, message empty: Send does nothing',
    'S_FEEDBACK_TYPED': 'Feedback page, message typed: Send opens the email chooser',
    'S_WEB_PRIVACY': 'Privacy policy in a WebView',
}

# ------------------------------------------------------------------ verdicts
DEAD = {
    'OrmLiteConfigUtil.<init>': 'Build-time ORMLite config generator (OrmLiteConfigUtil.java:5-10); no caller in the app (all sources and the bytecode call scan searched)',
    'OrmLiteConfigUtil.main': 'Command-line main of the build-time generator; never called by the app (no caller in sources or bytecode)',
    'DbEntity.getId': 'SRC DbEntity.java:7-16 (no getId() call in the app sources or bytecode; the field is annotated @DatabaseField(generatedId = true) with no useGetSet); INFERRED ORMLite reads annotated fields by reflection and calls the getter only when useGetSet is set (ORMLite source not read)',
    'DbEntity.setId': 'SRC DbEntity.java:7-16 (no setId() call in the app sources or bytecode; the field is annotated @DatabaseField(generatedId = true) with no useGetSet); INFERRED ORMLite writes annotated fields by reflection and calls the setter only when useGetSet is set (ORMLite source not read)',
    'AppUtils.<init>': 'Private constructor of a static-only class; no "new AppUtils" in sources or bytecode',
    'HashConstants.<init>': 'Constructor of a constants-only class; never instantiated (sources and bytecode)',
    'JdkHashUtils.<init>': 'Private constructor of a static-only class; never instantiated',
    'LocalDataExporter.<init>': 'Constructor of a static-only class; never instantiated',
    'LogUtils.<init>': 'Constructor of a static-only class; never instantiated',
    'UIUtils.<init>': 'Private constructor of a static-only class; never instantiated',
    'WebUtils.<init>': 'Private constructor of a static-only class; never instantiated',
    'SettingsFragment.lambda$initRate$7': 'Registered only when BuildConfig.FLAVOR equals "googlePlay" (SettingsFragment.java:247-257); this build is flavor thirdPartyStores, so the else branch hides the row',
    'BaseFragment.setAllowBackAction': 'The base implementation (returns false) is overridden by every concrete BaseFragment (HashCalculatorFragment, HistoryFragment, FeedbackFragment, WebFragment), so the virtual call in appResume never reaches it',
    'BaseFragment.getBackActionIconResId': 'Called only when setAllowBackAction() is true (BaseFragment.java:53-60), and every fragment that returns true overrides it',
}
FRAMEWORK_ONLY = {
    'App.onTerminate': 'Nothing in the app calls it (SRC App.java:176); the framework calls Application.onTerminate only from the EXIT_APPLICATION message (FW-SRC core/java/android/app/ActivityThread.java:936-938, 1659-1664), which AMS sends through scheduleExit only when the process has no real pid or is system_server itself (FW-SRC services/core/java/com/android/server/am/ActivityManagerService.java:6919-6936, 23336-23340); a normal app process is killed instead',
    'OrmLiteLocalDataStorage.releaseHelper': 'Only caller is App.onTerminate (SRC App.java:178), which never runs in a normal app process (see App.onTerminate)',
    'OrmLiteLocalDataStorage.onUpgrade': 'SRC OrmLiteLocalDataStorage.java:31-33 (DATABASE_VERSION is 1, the first version, so no stored database can be older); INFERRED SQLiteOpenHelper calls onUpgrade only when the stored version is lower than the requested one (android.database.sqlite source not read)',
    'HistoryItem.equals': 'Object override with no app caller: HistoryItem objects are only held in Lists and shown (no equals / contains / indexOf / remove on them in the app sources); INFERRED ORMLite does not compare row objects unless an object cache is enabled (ORMLite source not read)',
    'HistoryItem.hashCode': 'Object override with no app caller: no HashMap / HashSet of HistoryItem in the app sources; INFERRED ORMLite does not hash row objects unless an object cache is enabled (ORMLite source not read)',
    'AppTextWatcher.onTextChanged': 'The only subclass HashCalculatorFragment$1 overrides it, so the framework always calls the override (HashCalculatorFragment.java:516-528)',
}

NOTES = {
    'MainActivity.onOptionsItemSelected': 'Never handles Up: android.R.id.home reaches the fragments (BaseFragment / SettingsFragment onOptionsItemSelected)',
    'HashCalculatorFragment.onViewCreated': 'Folder branch (startWithFolderSelection) unreachable in this flavor: MainActivity.getBundleForShortcutAction never sets the flag (MainActivity.java:113-123)',
    'HashCalculatorFragment.userActionSelect': 'default branch (throw IllegalArgumentException) is unreachable: every UserActionType is handled',
    'HistoryPresenterImpl.load': 'Hazard candidate: with 30 or more history rows only the newest 30 are ever shown; scrolling at rest never calls load() again because of the inverted isLoaded() (HistoryFragment.java:68-76, HistoryPresenterImpl.java:30-41)',
    'HistoryPresenterImpl.isLoaded': 'Misnamed/inverted: returns true when NOT loading and more pages remain, so HistoryFragment$1.canLoad (needs it false) is true only while a load runs or when everything is loaded; at rest the older pages are never requested',
    'SharedPreferencesSettings.setRefreshSelectedFileStatus': 'Only called when refresh_selected_file is true; no app code ever writes true, so it needs a pre-seeded preferences file',
    'SharedPreferencesSettings.getThemeAnalogue': 'Needs a legacy selected_theme value that is neither LIGHT nor DARK (old app versions); needs a pre-seeded preferences file',
    'HistoryItem.<init>()': 'Called by ORMLite through reflection when rows are read (INFERRED, ORMLite source not read)',
}

FW_LC = 'INFERRED androidx.fragment.app.FragmentManager runs the lifecycle of a fragment (create, view created, start, resume) after commit() (androidx source not read)'
RES_CANCEL_EV = "FW-SRC core/java/android/app/Activity.java:824, 5489-5497 (an activity that finishes without setResult reports mResultCode, which is RESULT_CANCELED by default) and core/java/android/app/ActivityThread.java:4253-4265 (a result is delivered to the starting activity through dispatchActivityResult, which ends in onActivityResult); INFERRED the system file picker (another app) finishes without a result on Back, and the androidx Fragment / FragmentActivity routes the result to the fragment's onActivityResult (picker app and androidx source not read)"
DLG_CANCEL_EV = 'FW-SRC core/java/android/app/Dialog.java:110, 352-358, 650-654, 1231-1237 (Back calls cancel() while the dialog is cancelable; cancel() sends the cancel message if one is set, then dismiss() closes the dialog); SRC AppAlertDialog.java:42 (the Cancel button calls dialog.cancel()); INFERRED androidx.appcompat.app.AlertDialog extends android.app.Dialog and keeps the default cancelable behaviour (androidx source not read)'
SHEET_STAYS = {'S_DLG_CHANGE_LANGUAGE': 'SRC LanguagesListAdapter.java:55-71 (the row opens the dialog; only OK dismisses the dialog and restarts, nothing dismisses the sheet)', 'S_DLG_CHANGE_THEME': "SRC ThemesListAdapter.java:62-78 (the dialog's OK dismisses the dialog and restarts the app; nothing dismisses the sheet)"}
PAUSE_EV = 'FW-SRC core/java/android/app/ActivityThread.java:3812-3826, 3878, 3893-3901 and core/java/android/app/Activity.java:7139-7143 (handlePauseActivity pauses the activity through performPauseActivity; Activity.performPause calls onPause); INFERRED Instrumentation.callActivityOnPause leads to Activity.performPause, and what makes the system send the pause (Home, recents, screen off, a window on top) (Instrumentation, ActivityStack and window manager source not read)'
RESUME_EV = 'FW-SRC core/java/android/app/ActivityThread.java:3534-3540, 3553-3556, 3608-3621 and core/java/android/app/Activity.java:7098-7107 (handleResumeActivity -> performResumeActivity -> Activity.performResume -> callActivityOnResume); INFERRED Instrumentation.callActivityOnResume calls Activity.onResume and the androidx FragmentActivity.onResume dispatches resume to the added fragments (Instrumentation and androidx source not read)'
FW_ADAPTER = 'INFERRED androidx RecyclerView.setAdapter makes the next layout pass call getItemCount, onCreateViewHolder and onBindViewHolder (androidx source not read)'
FW_TW = ('FW-SRC core/java/android/widget/TextView.java:5206-5208, 5257-5260, 5290-5297, 5300-5304, 5397-5403, 9309-9316, 9359-9366, 9375-9382 '
         '(setText(text) calls setText(text, type, true, 0), which calls beforeTextChanged, onTextChanged and afterTextChanged of every registered TextWatcher; '
         'afterTextChanged needs an Editable, which is created when watchers are registered); INFERRED android.widget.EditText extends TextView (EditText.java not read)')
HC = 'HashCalculatorFragment'

# ------------------------------------------------------------------ process start, entry points
e('S_ENTRY', 'App.<init>', 'ENTRY', 'Android starts the app process; the Application object is created before any component',
  gui=['Home screen: tap the Hash Checker icon'], evidence='SRC AndroidManifest.xml:9')
e('App.<init>', 'App.onCreate', 'LIFECYCLE', 'Application.onCreate runs right after construction', evidence='SRC App.java:53')
e('S_ENTRY', 'MainActivity.<init>', 'ENTRY', 'Tap the launcher icon (MAIN + LAUNCHER intent filter); the only activity',
  gui=['Home screen: tap the Hash Checker icon'], evidence='SRC AndroidManifest.xml:19-33')
# The intent that starts the app carries data down to the calculator fragment (MainActivity.create reads it, the fragment reads its arguments), so a start by
# another app is its own context all the way: @XURI (VIEW / SEND with a URI), @XTEXT and @XFILE (launcher shortcuts). The plain launcher start carries none.
START = {
    'XURI': dict(entry='Another app sends an explicit VIEW intent with a content:// URI (filter F2), or an explicit SEND with ClipData',
                 gui=['In another app: open a file with Hash Checker'], entry_ev='SRC AndroidManifest.xml:35-54; MainActivity.java:72-88',
                 guard='intent scheme is content/file, or ClipData present', create_ev='SRC MainActivity.java:82-88,93'),
    'XTEXT': dict(entry='Long-press the app icon and tap the "Text" launcher shortcut (explicit intent with action ACTION_START_WITH_TEXT)',
                  gui=['Long-press the Hash Checker icon -> tap the Text shortcut'], entry_ev='SRC App.java:83-97,137-150; MainActivity.java:113-123',
                  guard='no content/file scheme and no ClipData: the bundle is built from the intent action', create_ev='SRC MainActivity.java:89-93,113-123'),
    'XFILE': dict(entry='Long-press the app icon and tap the "File" launcher shortcut (explicit intent with action ACTION_START_WITH_FILE); the "Folder" shortcut sends an action this build ignores',
                  gui=['Long-press the Hash Checker icon -> tap the File shortcut'], entry_ev='SRC App.java:83-97,137-150; MainActivity.java:113-123',
                  guard='no content/file scheme and no ClipData: the bundle is built from the intent action', create_ev='SRC MainActivity.java:89-93,113-123'),
}
for _c, _d in START.items():
    _n = lambda m, _c=_c: m + '@' + _c
    if _c != 'XURI':   # the XURI entry is written out below, with its note
        e('S_ENTRY', _n('MainActivity.<init>'), 'ENTRY', _d['entry'], gui=_d['gui'], env=ENV_EXT, evidence=_d['entry_ev'])
    e(_n('MainActivity.<init>'), _n('MainActivity.onCreate'), 'LIFECYCLE', 'The system instantiates MainActivity, then calls onCreate', evidence='SRC MainActivity.java:50')
    e(_n('MainActivity.onCreate'), 'BaseActivity.onCreate@MainActivity_' + _c, 'CALL', 'Direct call', evidence='SRC MainActivity.java:52 (bytecode)')
    e('BaseActivity.onCreate@MainActivity_' + _c, _n('MainActivity.create'), 'CALL', 'Direct call', evidence='SRC BaseActivity.java:19 (bytecode)')
    e(_n('MainActivity.create'), 'MainActivity.showFragment@CALC_' + _c, 'CALL', 'showFragment(mainFragment): adds the calculator with the arguments built from the intent',
      guard=_d['guard'], evidence=_d['create_ev'])
    e('MainActivity.showFragment@CALC_' + _c, _n('HashCalculatorFragment.onAttach'), 'LIFECYCLE', 'FragmentTransaction.commit(): the fragment is attached',
      evidence=FW_LC + '; SRC MainActivity.java:96-103')
    e(_n('HashCalculatorFragment.onAttach'), 'BaseFragment.onCreateView@HashCalculatorFragment_' + _c, 'LIFECYCLE', 'onCreateView inflates the layout', evidence=FW_LC)
    e('BaseFragment.onCreateView@HashCalculatorFragment_' + _c, _n('HashCalculatorFragment.onViewCreated'), 'LIFECYCLE', 'onViewCreated', evidence=FW_LC)
e('MainActivity.create@XURI', 'MainActivity.getConfiguredBundleWithDataUri', 'CALL', 'VIEW (content/file scheme) or SEND with ClipData: bundle with the URI',
  guard='intent scheme is content/file, or ClipData present', evidence='SRC MainActivity.java:82-88')
# plain start (launcher icon): the automatic call edges for these two pairs are skipped once a hand edge covers the pair, so the plain ones are written out
e('MainActivity.onCreate', 'BaseActivity.onCreate@MainActivity', 'CALL', 'Direct call', evidence='SRC MainActivity.java:52 (bytecode)')
e('HashCalculatorFragment.onViewCreated', 'HashCalculatorFragment.checkExternalDataPresence', 'CALL', 'checkExternalDataPresence(bundle)', guard='the arguments bundle exists',
  evidence='SRC HashCalculatorFragment.java:503 (bytecode)')
e('HashCalculatorFragment.onViewCreated@XURI', 'HashCalculatorFragment.checkExternalDataPresence@XURI', 'CALL', 'checkExternalDataPresence(bundle)', guard='the arguments bundle exists',
  evidence='SRC HashCalculatorFragment.java:503 (bytecode)')
e('S_ENTRY', 'MainActivity.<init>@XURI', 'ENTRY',
  'Another app sends an explicit VIEW intent with a content:// URI (filter F2), or an explicit SEND with ClipData',
  gui=['In another app: open a file with Hash Checker'], env=ENV_EXT, evidence='SRC AndroidManifest.xml:35-54; MainActivity.java:72-88',
  note='The SEND filter has CATEGORY_LAUNCHER, not DEFAULT, so the app is not offered in the share sheet (INFERRED: the system only lists activities with CATEGORY_DEFAULT there; the resolver source was not read); only an explicit intent works')
e('MainActivity.<init>', 'MainActivity.onCreate', 'LIFECYCLE', 'The system instantiates MainActivity, then calls onCreate', evidence='SRC MainActivity.java:50')
e('MainActivity.onCreate', 'BaseActivity.getTheme@MainActivity', 'FRAMEWORK',
  'Window and layout creation call Activity.getTheme(), which BaseActivity overrides', evidence='INFERRED ContextThemeWrapper.getTheme is called when the window and the layout are created (ContextThemeWrapper.java not read); SRC BaseActivity.java:23-28')
e('MainActivity.create', 'HashCalculatorFragment.<clinit>', 'CALL', 'Class initialisation on first use (assert flag of fileNameFromUri)',
  guard='first instantiation in this process', evidence='SRC HashCalculatorFragment.java:339 (the only assert of the class); INFERRED javac gives a class that uses assert a static initializer for $assertionsDisabled, which the JVM runs on first use of the class (compiler / Java language rule, not read from a source)')
e('MainActivity.create', 'MainActivity.showFragment@CALC', 'CALL', 'showFragment(mainFragment): adds the calculator', evidence='SRC MainActivity.java:93')

# ------------------------------------------------------------------ fragments: show -> lifecycle -> page
FRAG = {   # key: (class, first page entered, window)
    'CALC': ('HashCalculatorFragment', MAIN('EMPTY')),
    'HISTORY': ('HistoryFragment', None),
    'SETTINGS': ('SettingsFragment', 'S_SETTINGS'),
    'FEEDBACK': ('FeedbackFragment', 'S_FEEDBACK'),
    'WEB': ('WebFragment', 'S_WEB_PRIVACY'),
}
for key, (F, page) in FRAG.items():
    sf = 'MainActivity.showFragment@' + key
    attach = impl(F, 'onAttach')
    create = impl(F, 'onCreate') if F != 'SettingsFragment' else 'SettingsFragment.onCreatePreferences'
    view = impl(F, 'onCreateView') if F != 'SettingsFragment' else None
    created = impl(F, 'onViewCreated')
    resume = impl(F, 'onResume')
    menu = impl(F, 'onCreateOptionsMenu')
    e(sf, attach, 'LIFECYCLE', 'FragmentTransaction.commit(): the fragment is attached', evidence=FW_LC + '; SRC MainActivity.java:96-103')
    e(attach, create, 'LIFECYCLE', 'onCreate (PreferenceFragmentCompat: onCreatePreferences)', evidence=FW_LC)
    prev = create
    if view:   # siblings of onAttach: a chain through the shared BaseFragment.onCreate would join all fragments
        e(attach, view, 'LIFECYCLE', 'onCreateView inflates the layout', evidence=FW_LC)
        prev = view
    if prev == create and create.startswith('BaseFragment.'):
        prev = attach
    e(prev, created, 'LIFECYCLE', 'onViewCreated', evidence=FW_LC)
    e(created, resume, 'LIFECYCLE', 'onStart -> onResume', evidence=FW_LC)
    e(resume, menu, 'FRAMEWORK', 'The options menu is created after the fragment resumes (setHasOptionsMenu(true))',
      evidence='INFERRED androidx FragmentActivity.onCreatePanelMenu offers the options menu to the added fragments, which call onCreateOptionsMenu (androidx source not read)')
    if page:
        e(resume, page, 'ENTERS', 'The fragment is visible', evidence=FW_LC)

e('MainActivity.create', 'HashCalculatorFragment.<init>', 'CALL', 'new HashCalculatorFragment()', evidence='SRC MainActivity.java:81')

# the calculator's text watchers and menu items
for m in MODES:
    P = MAIN(m)
    # menu: History / Settings
    for item, key, label in (('menu_main_section_history', 'HISTORY', 'History'), ('menu_main_section_settings', 'SETTINGS', 'Settings')):
        ois = 'MainActivity.onOptionsItemSelected@' + key
        e(P, ois, 'GUI', 'Tap the %s icon in the action bar (R.id.%s)' % (label, item), gui=['Tap the %s icon (top-right)' % label],
          evidence='SRC R/menu/menu_main.xml; MainActivity.java:126-138')
    # typing in the two hash fields
    e(P, 'HashCalculatorFragment$1.onTextChanged', 'GUI', 'Type or paste in the custom or generated hash field (shows the copy/clear icons)',
      gui=['Type or paste text in a hash field'], evidence='SRC HashCalculatorFragment.java:457-468,516-528')
    e(P, 'AppTextWatcher.beforeTextChanged', 'GUI', 'Typing in a hash field', gui=['Type or paste text in a hash field'], evidence='SRC AppTextWatcher.java:8-12')
    e(P, 'AppTextWatcher.afterTextChanged', 'GUI', 'Typing in a hash field', gui=['Type or paste text in a hash field'], evidence='SRC AppTextWatcher.java:20-24')
    # copy / clear icons (visible only while the field is not empty)
    for lam, what in (('4', 'copy the custom hash'), ('5', 'clear the custom hash'), ('6', 'copy the generated hash'), ('7', 'clear the generated hash')):
        e(P, 'HashCalculatorFragment.lambda$onViewCreated$' + lam, 'GUI', 'Tap the icon to ' + what, gui=['Type something in the field, then tap its icon to ' + what],
          needs_state='The field is not empty (the icons are INVISIBLE while it is empty)', evidence='SRC HashCalculatorFragment.java:445-455,519-526')
    # the three bottom sheets
    e(P, 'HashCalculatorFragment.lambda$onViewCreated$8', 'GUI', 'Tap the hash-type text', gui=['Tap the hash type (e.g. "md5")'],
      evidence='SRC HashCalculatorFragment.java:473')
    e(P, 'HashCalculatorFragment.lambda$onViewCreated$9', 'GUI', 'Tap the From button', gui=['Tap the "From" button'], evidence='SRC HashCalculatorFragment.java:476-479')
    e(P, 'HashCalculatorFragment.lambda$onViewCreated$10', 'GUI', 'Tap the Actions button', gui=['Tap the "Actions" button'], evidence='SRC HashCalculatorFragment.java:481-485')
    e(P, 'S_SHEET_HASHTYPE@' + m, 'ENTERS', 'Tap the hash-type text: the sheet opens over this page', gui=['Tap the hash type (e.g. "md5")'], evidence='SRC HashCalculatorFragment.java:260-263')
    e(P, 'S_SHEET_SOURCE@' + m, 'ENTERS', 'Tap the From button: the sheet opens over this page', gui=['Tap the "From" button'], evidence='SRC HashCalculatorFragment.java:476-479')
    e(P, 'S_SHEET_ACTIONS@' + m, 'ENTERS', 'Tap the Actions button: the sheet opens over this page', gui=['Tap the "Actions" button'], evidence='SRC HashCalculatorFragment.java:481-485')
    # system events on the page
    e(P, 'S_MAIN_PAUSED', 'ENTERS', 'Home / recents / screen off, or an external window opens on top', gui=['Press Home / recents / screen off'], evidence=PAUSE_EV)
    e(P, 'App.onConfigurationChanged', 'SYSTEM', 'A device-wide configuration change (locale, font scale, ...) reaches the Application; MainActivity is relaunched too (no android:configChanges; the portrait lock only stops rotation)',
      gui=['Change a device-wide setting (language, font size, ...)'], evidence='FW-SRC core/java/android/app/ActivityThread.java:4725-4733, 4836, 4854, 5025-5041 (handleConfigurationChanged collects the applications among the component callbacks and calls performConfigurationChanged, which calls their onConfigurationChanged); SRC AndroidManifest.xml:19-24 (MainActivity has no android:configChanges) and :22 (screenOrientation portrait, which only blocks rotation); INFERRED the system relaunches an activity whose configuration changed and that does not declare it in configChanges (ActivityRecord side not read)')
    e(P, 'MainActivity.onBackPressed@CALC', 'SYSTEM', 'Back on the calculator', gui=['Press Back'], evidence='SRC MainActivity.java:150-164')

e('HashCalculatorFragment.lambda$onViewCreated$8', 'HashCalculatorFragment.selectHashTypeFromList', 'CALL', 'selectHashTypeFromList()', evidence='SRC HashCalculatorFragment.java:473')
e('S_MAIN_PAUSED', impl(HC, 'onResume'), 'SYSTEM', 'The activity returns to the foreground; onResume reaches every added fragment', gui=['Return via recents or the launcher icon'],
  evidence=RESUME_EV)
e('App.onConfigurationChanged', 'App.setLocale', 'CALL', 'setLocale()', evidence='SRC App.java:172')

# validateTextCase runs on every resume and calls setText, which notifies the watchers
for n in ('convertToLowerCase', 'convertToUpperCase'):
    for cb in ('HashCalculatorFragment$1.onTextChanged', 'AppTextWatcher.beforeTextChanged', 'AppTextWatcher.afterTextChanged'):
        e('HashCalculatorFragment.' + n, cb, 'FRAMEWORK', 'editText.setText(...) notifies the TextWatchers', evidence=FW_TW + '; SRC HashCalculatorFragment.java:641-647')

# ------------------------------------------------------------------ bottom sheets (opened from the calculator or from Settings)
SHEET = {   # key: (sheet class, adapter class, holder class, opener method, page(s))
    'SOURCE': ('SourceSelectActionsBottomSheet', 'ActionsListAdapter', 'ActionsListAdapter$ActionHolder', 'HashCalculatorFragment.lambda$onViewCreated$9'),
    'ACTIONS': ('ActionSelectActionsBottomSheet', 'ActionsListAdapter', 'ActionsListAdapter$ActionHolder', 'HashCalculatorFragment.lambda$onViewCreated$10'),
    'HASHTYPE': ('GenerateToBottomSheet', 'HashesListAdapter', 'HashesListAdapter$HashesListHolder', 'HashCalculatorFragment.selectHashTypeFromList'),
    'LANGUAGES': ('LanguagesBottomSheet', 'LanguagesListAdapter', 'LanguagesListAdapter$LanguagesListHolder', 'SettingsFragment.lambda$initLanguageSettings$0'),
    'THEMES': ('ThemesBottomSheet', 'ThemesListAdapter', 'ThemesListAdapter$ThemesListHolder', 'SettingsFragment.lambda$initThemeSettings$1'),
    'PRIVACY': ('PrivacyPolicyWebLinksBottomSheet', 'WebLinksListAdapter', 'WebLinksListAdapter$WebLinksListHolder', 'SettingsFragment.lambda$initPrivacyPolicy$2'),
    'AUTHOR': ('AuthorWebLinksBottomSheet', 'WebLinksListAdapter', 'WebLinksListAdapter$WebLinksListHolder', 'SettingsFragment.lambda$initAuthorLinks$4'),
    'LIBRARIES': ('LibrariesWebLinksBottomSheet', 'WebLinksListAdapter', 'WebLinksListAdapter$WebLinksListHolder', 'SettingsFragment.lambda$initLibrariesLinks$5'),
}
ADAPT_KEY = {'ActionsListAdapter': 'ACTIONS_AD', 'HashesListAdapter': 'HASH_AD', 'LanguagesListAdapter': 'LANG_AD',
             'ThemesListAdapter': 'THEME_AD', 'WebLinksListAdapter': 'WEB_AD'}
HOLDER_BIND = {'ActionsListAdapter': 'ActionsListAdapter$ActionHolder.bind', 'HashesListAdapter': 'HashesListAdapter$HashesListHolder.bind',
               'LanguagesListAdapter': 'LanguagesListAdapter$LanguagesListHolder.bind', 'ThemesListAdapter': 'ThemesListAdapter$ThemesListHolder.bind',
               'WebLinksListAdapter': 'WebLinksListAdapter$WebLinksListHolder.bind'}
HOLDER_TYPE = {'ActionsListAdapter': 'Action', 'HashesListAdapter': 'HashType', 'LanguagesListAdapter': 'Language', 'ThemesListAdapter': 'Theme',
               'WebLinksListAdapter': 'WebLink'}
for key, (S, AD, HOLD, opener) in SHEET.items():
    attach = impl(S, 'onAttach') if S != 'ThemesBottomSheet' else None
    cview = impl(S, 'onCreateView')
    vcreated = impl(S, 'onViewCreated')
    base_vc = 'BaseListBottomSheet.onViewCreated@' + S
    prev = opener
    if attach:
        e(prev, attach, 'LIFECYCLE', 'show(): the bottom-sheet fragment is attached (Dagger injection in onAttach)', evidence=FW_LC)
        prev = attach
    e(prev, cview, 'LIFECYCLE', 'onCreateView inflates bottom_sheet_list_items', evidence=FW_LC)
    e(prev, vcreated, 'LIFECYCLE', 'onViewCreated (after onCreateView)', evidence=FW_LC)
    # the adapter is set inside the base class onViewCreated
    ob = 'BaseListAdapter.onBindViewHolder@' + ADAPT_KEY[AD]
    e(base_vc, 'BaseListAdapter.getItemCount', 'FRAMEWORK', 'rvItems.setAdapter(...) reads getItemCount', evidence=FW_ADAPTER + '; SRC BaseListBottomSheet.java:36-38')
    e(base_vc, impl(AD, 'onCreateViewHolder'), 'FRAMEWORK', 'RecyclerView creates the row views', evidence=FW_ADAPTER)
    e(base_vc, ob, 'FRAMEWORK', 'RecyclerView binds the rows', evidence=FW_ADAPTER)
    e(ob, HOLDER_BIND[AD], 'CALL', 'holder.bind(items.get(position))', evidence='SRC BaseListAdapter.java:43-45')
    if key in ('LANGUAGES', 'THEMES', 'PRIVACY', 'AUTHOR', 'LIBRARIES'):
        e(opener, 'BaseListBottomSheet.key', 'CALL', 'bottomSheet.show(fragmentManager, bottomSheet.key())', evidence='SRC SettingsFragment.java:163,175,187,210,222')

# ------------------------------------------------------------------ calculator sheets as pages (one variant per calculator mode)
SRC_ROWS = (('TEXT', 'Text', 'ENTER_TEXT'), ('FILE', 'File', 'SEARCH_FILE'), ('FOLDER', 'Folder', 'SEARCH_FOLDER'))
H = 'ActionsListAdapter$ActionHolder'
for m in MODES:
    pv = 'S_SHEET_SOURCE@' + m
    for ctx, label, _ in SRC_ROWS:
        e(pv, 'BaseListHolder.lambda$bind$0@SRC_' + ctx, 'GUI', 'Tap the "%s" row' % label, gui=['Tap "%s"' % label], evidence='SRC BaseListHolder.java:44; ActionsListAdapter.java:55-60')
    e(pv, MAIN(m), 'ENTERS', 'The sheet closes (a row was tapped and dismissBottomSheet ran, or Back / tap outside)', gui=['Press Back or tap outside the sheet'],
      evidence='SRC ActionsListAdapter.java:59')
    ph = 'S_SHEET_HASHTYPE@' + m
    e(ph, 'BaseListHolder.lambda$bind$0@HashesListAdapter$HashesListHolder', 'GUI', 'Tap a hash algorithm row', gui=['Tap a hash algorithm (e.g. "sha256")'],
      evidence='SRC BaseListHolder.java:44; HashesListAdapter.java:57-64')
    e(ph, MAIN(m), 'ENTERS', 'The sheet closes (row tapped, Back or tap outside)', gui=['Press Back or tap outside the sheet'], evidence='SRC HashesListAdapter.java:63')
    pa = 'S_SHEET_ACTIONS@' + m
    gen = 'GEN_NONE' if m == 'EMPTY' else 'GEN_' + m
    e(pa, 'BaseListHolder.lambda$bind$0@' + gen, 'GUI', 'Tap "Generate"', gui=['Tap "Generate"'], evidence='SRC BaseListHolder.java:44; ActionsListAdapter.java:55-60')
    e(pa, 'BaseListHolder.lambda$bind$0@COMPARE', 'GUI', 'Tap "Compare"', gui=['Tap "Compare"'], evidence='SRC BaseListHolder.java:44; ActionsListAdapter.java:55-60')
    e(pa, 'BaseListHolder.lambda$bind$0@' + ('EXP_NONE' if m == 'EMPTY' else 'EXP_OK'), 'GUI', 'Tap "Export .txt"', gui=['Tap "Export .txt"'],
      needs_state=None if m == 'EMPTY' else 'A hash was generated first (Export needs a non-empty generated field)', evidence='SRC BaseListHolder.java:44; ActionsListAdapter.java:55-60')
    e(pa, MAIN(m), 'ENTERS', 'The sheet closes (row tapped, Back or tap outside)', gui=['Press Back or tap outside the sheet'], evidence='SRC ActionsListAdapter.java:59')
# row listeners: lambda body -> callItemClick -> userActionSelect -> handler
ROWS = {   # context: (user action handler, page entered or None, guard)
    'SRC_TEXT': ('enterText', 'S_DLG_TEXT_INPUT'), 'SRC_FILE': ('openSystemFileManager', 'S_EXT_PICK_FILE'), 'SRC_FOLDER': ('openSystemFolderManager', 'S_EXT_PICK_FOLDER'),
    'GEN_NONE': ('generateHash@NONE', None), 'GEN_TEXT': ('generateHash@TEXT', None), 'GEN_FILE': ('generateHash@FILE', None), 'GEN_FOLDER': ('generateHash@FOLDER', None),
    'COMPARE': ('compareHashes', None), 'EXP_NONE': ('saveGeneratedHashAsTextFile@NONE', None), 'EXP_OK': ('saveGeneratedHashAsTextFile@OK', None),
}
for ctx, (handler, page) in ROWS.items():
    lam = 'BaseListHolder.lambda$bind$0@' + ctx
    cic = H + '.callItemClick@' + ctx
    usa = HC + '.userActionSelect@' + ctx
    e(lam, cic, 'CALL', 'callItemClick() of the ActionHolder', evidence='SRC BaseListHolder.java:44')
    e(cic, usa, 'CALL', 'userActionSelect(action.getUserActionType())', evidence='SRC ActionsListAdapter.java:55-58')
    e(usa, HC + '.' + handler, 'CALL', 'switch case for this action', evidence='SRC HashCalculatorFragment.java:166-189')
    if page:
        e(HC + '.' + handler, page, 'ENTERS', 'The action opens this window', evidence='SRC HashCalculatorFragment.java:191-212,365-368')
# generate: the selected source decides which branch of generateHash runs, and which task path follows
e(HC + '.generateHash@NONE', HC + '.showSnackbarWithoutAction', 'CALL', 'No source selected: hint snackbar "select an object"', guard='fileUri == null && folderUri == null && !isTextSelected',
  evidence='SRC HashCalculatorFragment.java:244-246')
for K in ('TEXT', 'FILE', 'FOLDER'):
    gh = HC + '.generateHash@' + K
    dib = 'HashCalculatorTask.doInBackground@' + K
    post = 'HashCalculatorTask.onPostExecute@' + K
    ctor = ('HashCalculatorTask.<init>(Context,HashType,String,HashCalculatorTaskTarget)' if K == 'TEXT'
            else 'HashCalculatorTask.<init>(Context,HashType,Uri,Uri,HashCalculatorTaskTarget)')
    g = 'isTextSelected' if K == 'TEXT' else ('fileUri != null' if K == 'FILE' else 'folderUri != null (else branch)')
    e(gh, 'AppProgressDialog.<init>', 'CALL', 'new AppProgressDialog(...)', guard=g, evidence='SRC HashCalculatorFragment.java:218')
    e(gh, 'AppProgressDialog.getDialog', 'CALL', '.getDialog()', guard=g, evidence='SRC HashCalculatorFragment.java:218')
    e(gh, 'HashType.getHashTypeFromString', 'CALL', 'HashType.getHashTypeFromString(tvSelectedHashType)', guard=g, evidence='SRC HashCalculatorFragment.java:217')
    e(gh, 'S_MAIN_GENERATING', 'ENTERS', 'progressDialog.show()', guard=g, evidence='SRC HashCalculatorFragment.java:219')
    e(gh, ctor, 'CALL', ('Text source: new HashCalculatorTask(context, type, text, target).execute()' if K == 'TEXT'
                         else 'File/folder source: new HashCalculatorTask(context, type, fileUri, folderUri, target).execute()'), guard=g,
      evidence='SRC HashCalculatorFragment.java:220-243')
    e(gh, dib, 'ASYNC', 'AsyncTask.execute(): doInBackground runs on a worker thread', guard=g, evidence='FW-SRC core/java/android/os/AsyncTask.java:219-224, 237-262, 594-596, 632-650, 326-334 (execute uses the serial executor, which hands each task to THREAD_POOL_EXECUTOR; the worker runnable calls doInBackground); SRC HashCalculatorFragment.java:226,234,242')
    e(dib, post, 'ASYNC', 'Worker finished: onPostExecute on the main thread', evidence='FW-SRC core/java/android/os/AsyncTask.java:369-374, 285, 705-713, 691-697 (postResult sends the result message to a handler on the main looper; its handleMessage calls finish, which calls onPostExecute unless the task was cancelled); SRC HashCalculatorTask.java:83-87')
    e(post, HC + '.lambda$new$1', 'CALL', 'completeListener.hashCalculationComplete(result)', evidence='SRC HashCalculatorTask.java:86; HashCalculatorFragment.java:111')
    e(post, MAIN(K), 'ENTERS', 'Result shown, progress dialog dismissed (back on the calculator in this mode)', evidence='SRC HashCalculatorFragment.java:111-150')
    e(dib, 'JdkHashCalculator.setHashType', 'CALL', 'hashCalculator.setHashType(hashType)', evidence='SRC HashCalculatorTask.java:68-69')
    e(dib, 'JdkHashCalculator.<init>', 'CALL', 'new JdkHashCalculator()', evidence='SRC HashCalculatorTask.java:68')
    frm = {'TEXT': 'JdkHashCalculator.fromString', 'FILE': 'JdkHashCalculator.fromFile(Context,Uri)', 'FOLDER': 'JdkHashCalculator.fromFolder(Context,Uri)'}[K]
    e(dib, frm, 'CALL', 'Source kind: ' + K.lower(), guard=g, evidence='SRC HashCalculatorTask.java:70-76')
e(HC + '.lambda$new$1', HC + '.showSnackbarWithoutAction', 'CALL', 'hashValue == null: snackbar "invalid selected source"', guard='the engine returned null', env=ENV_EXC,
  evidence='SRC HashCalculatorFragment.java:112-114')
e(HC + '.lambda$new$1', 'AppAlertDialog.<init>', 'CALL', 'Rate dialog', guard='canShowRateAppDialog()', needs_state=ENV_RATE, evidence='SRC HashCalculatorFragment.java:131-143')
e(HC + '.lambda$new$1', 'AppAlertDialog.show', 'CALL', 'Rate dialog shown', guard='canShowRateAppDialog()', needs_state=ENV_RATE, evidence='SRC HashCalculatorFragment.java:135-142')
e(HC + '.lambda$new$1', 'S_DLG_RATE_APP', 'ENTERS', 'Rate dialog shown', guard='canShowRateAppDialog()', needs_state=ENV_RATE, evidence='SRC HashCalculatorFragment.java:131-143')
e('S_DLG_RATE_APP', HC + '.lambda$new$0', 'GUI', 'Tap Rate', gui=['Tap "Rate"'], needs_state=ENV_RATE, evidence='SRC AppAlertDialog.java:41; HashCalculatorFragment.java:140')
e('S_DLG_RATE_APP', 'AppAlertDialog.lambda$show$0', 'GUI', 'Tap Cancel', gui=['Tap "Cancel"'], needs_state=ENV_RATE, evidence='SRC AppAlertDialog.java:42')
e(HC + '.lambda$new$0', 'WebUtils.openGooglePlay', 'CALL', 'WebUtils.openGooglePlay(context, view, settings, themeConfig)', needs_state=ENV_RATE, evidence='SRC HashCalculatorFragment.java:140')
e('WebUtils.openGooglePlay', 'S_EXT_OTHER_APP', 'ENTERS', 'market:// (or the https Play Store page) opens in another app', evidence='SRC WebUtils.java:28-36')
for dst in ('AppSnackbar.<init>(Context,View,int,Settings,ThemeConfig)', 'AppSnackbar.show@INFO'):
    e('WebUtils.openGooglePlay', dst, 'CALL', 'Neither market:// nor https could be opened: snackbar', guard='both startActivity calls throw ActivityNotFoundException', env=ENV_NOAPP,
      evidence='SRC WebUtils.java:37-46')
e('AppAlertDialog.show', 'AppAlertDialog.lambda$show$1', 'FRAMEWORK', 'alertDialog.show() fires the OnShowListener', evidence='FW-SRC core/java/android/app/Dialog.java:330-333, 392-397, 1294-1300 (show() ends with sendShowMessage, which sends the message that setOnShowListener stored); INFERRED androidx.appcompat.app.AlertDialog extends android.app.Dialog (androidx source not read); SRC AppAlertDialog.java:44-50')
# compare / export
e(HC + '.compareHashes', HC + '.showSnackbarWithoutAction', 'CALL', 'Snackbar "fill the fields" (a field is empty)', guard='a hash field is empty', evidence='SRC HashCalculatorFragment.java:255-257')
e(HC + '.compareHashes', HC + '.compareText', 'CALL', 'compareText(custom, generated)', guard='both hash fields not empty',
  needs_state='Both hash fields contain text (type in them or generate first)', evidence='SRC HashCalculatorFragment.java:250-254')
e(HC + '.compareHashes', HC + '.fieldIsNotEmpty', 'CALL', 'fieldIsNotEmpty(field) checks', evidence='SRC HashCalculatorFragment.java:250')
e(HC + '.saveGeneratedHashAsTextFile@NONE', HC + '.showSnackbarWithoutAction', 'CALL', 'Snackbar "generate a hash before export"', guard='no source or empty generated field',
  evidence='SRC HashCalculatorFragment.java:268-270')
e(HC + '.saveGeneratedHashAsTextFile@OK', HC + '.saveTextFile', 'CALL', 'saveTextFile(name)', guard='a source is selected and the generated field is not empty',
  needs_state=NEED_GEN, evidence='SRC HashCalculatorFragment.java:266-267')
for v in ('NONE', 'OK'):
    e(HC + '.saveGeneratedHashAsTextFile@' + v, HC + '.fieldIsNotEmpty', 'CALL', 'fieldIsNotEmpty(etGeneratedHash)', evidence='SRC HashCalculatorFragment.java:266')
e(HC + '.saveTextFile', 'S_EXT_CREATE_TXT', 'ENTERS', 'startActivityForResult(ACTION_CREATE_DOCUMENT)', evidence='SRC HashCalculatorFragment.java:273-286')
e(HC + '.saveTextFile', 'SharedPreferencesSettings.getLastHashType', 'CALL', 'file extension of the last hash type', evidence='SRC HashCalculatorFragment.java:283')
# text dialog
e(HC + '.enterText', 'TextInputDialog.<init>', 'CALL', 'new TextInputDialog(context, this, currentText).show()', evidence='SRC HashCalculatorFragment.java:365-368')
e(HC + '.enterText', impl('TextInputDialog', 'onCreate'), 'LIFECYCLE', 'Dialog.show() creates the dialog window and calls onCreate', evidence='FW-SRC core/java/android/app/Dialog.java:288-304, 401-406 (show() calls dispatchOnCreate while the dialog is not created yet; dispatchOnCreate calls onCreate); SRC HashCalculatorFragment.java:367, TextInputDialog.java:14, BaseDialog.java:15 (TextInputDialog extends BaseDialog extends android.app.Dialog)')
e('S_DLG_TEXT_INPUT', 'BaseDialog.lambda$initializeDialog$0', 'GUI', 'Tap Close', gui=['Tap "Close"'], evidence='SRC BaseDialog.java:32-35')
e('S_DLG_TEXT_INPUT', 'TextInputDialog.lambda$initializeDialog$0', 'GUI', 'Tap Add', gui=['Type some text, tap "Add"'], evidence='SRC TextInputDialog.java:36-40')
e('TextInputDialog.lambda$initializeDialog$0', HC + '.textValueEntered', 'CALL', 'textValueCallback.textValueEntered(text)', evidence='SRC TextInputDialog.java:38')
e(HC + '.textValueEntered', 'S_MAIN_TEXT', 'ENTERS', 'Text becomes the source', evidence='SRC HashCalculatorFragment.java:354-363')
e(impl('TextInputDialog', 'onCreate'), 'TextInputDialog.setupDialogStyle', 'CALL', 'setupDialogStyle() (soft input forced visible)', evidence='SRC BaseDialog.java:22-28; TextInputDialog.java:52-55')

# ------------------------------------------------------------------ results from other packages
for ctx, page, handler in (('PICK_FILE', 'S_EXT_PICK_FILE', 'selectFileFromSystemFileManager'),
                           ('PICK_FOLDER', 'S_EXT_PICK_FOLDER', 'selectFolderFromSystemFileManager'),
                           ('CREATE_TXT', 'S_EXT_CREATE_TXT', 'writeHashToFile')):
    ar = HC + '.onActivityResult@' + ctx
    e(page, ar, 'RESULT', 'The user picks / confirms in the system dialog: onActivityResult(requestCode, RESULT_OK, data)', gui=['In the system dialog: choose a document and confirm'],
      env=ENV_SAF, evidence='SRC HashCalculatorFragment.java:584-606')
    e(page, HC + '.onActivityResult@CANCELED', 'RESULT', 'Back / Cancel in the system dialog: onActivityResult with RESULT_CANCELED and no data (the method runs and does nothing)',
      gui=['Press Back in the system dialog'], evidence=RES_CANCEL_EV + '; SRC HashCalculatorFragment.java:585-586')
    e(ar, HC + '.' + handler, 'CALL', 'switch on requestCode', evidence='SRC HashCalculatorFragment.java:587-604')
e(HC + '.onActivityResult@CREATE_TXT', 'LogUtils.e', 'CALL', 'IOException while writing the .txt', env=ENV_EXC, evidence='SRC HashCalculatorFragment.java:596-598')
e(HC + '.selectFileFromSystemFileManager', HC + '.validateSelectedFile', 'CALL', 'validateSelectedFile(uri)', evidence='SRC HashCalculatorFragment.java:609-612')
e(HC + '.selectFolderFromSystemFileManager', HC + '.validateSelectedFolder', 'CALL', 'validateSelectedFolder(uri)', evidence='SRC HashCalculatorFragment.java:614-617')
e(HC + '.checkExternalDataPresence@XURI', HC + '.validateSelectedFile', 'CALL', 'URI from a VIEW/SEND intent', guard='the bundle carries URI_FROM_EXTERNAL_APP', env=ENV_EXT,
  gui=['In another app: open a file with Hash Checker (VIEW intent)'],
  needs_state='Hash Checker is started by another app with a VIEW intent or an explicit SEND with ClipData', evidence='SRC HashCalculatorFragment.java:539-545')
e(HC + '.validateSelectedFile', 'S_MAIN_FILE', 'ENTERS', 'File becomes the source', evidence='SRC HashCalculatorFragment.java:316-323')
e(HC + '.validateSelectedFolder', 'S_MAIN_FOLDER', 'ENTERS', 'Folder becomes the source', evidence='SRC HashCalculatorFragment.java:325-332')
e(HC + '.onViewCreated@XTEXT', HC + '.userActionSelect@SRC_TEXT', 'CALL', 'Launcher shortcut "Text": the text dialog opens at once', guard='startWithTextSelection', env=ENV_EXT,
  gui=['Long-press the Hash Checker icon -> tap the "Text" shortcut'], needs_state='Started from the launcher shortcut "Text"', evidence='SRC HashCalculatorFragment.java:490-492')
e(HC + '.onViewCreated@XFILE', HC + '.userActionSelect@SRC_FILE', 'CALL', 'Launcher shortcut "File": the file picker opens at once', guard='startWithFileSelection', env=ENV_EXT,
  gui=['Long-press the Hash Checker icon -> tap the "File" shortcut'], needs_state='Started from the launcher shortcut "File"', evidence='SRC HashCalculatorFragment.java:493-495')
# ------------------------------------------------------------------ hash engine, per hash type
# JDK types (MD5, SHA-x) and SHA3 go through MessageDigest; CRC-32, BLAKE2b and FNV-1a have their own code.
TYPES = {'CRC': 'CRC-32', 'BLAKE': 'BLAKE2b', 'FNV': 'FNV-1a (six sizes)', 'SHA3': 'SHA3-224/256/384/512 (Keccak provider)'}
NEED = lambda t: 'Choose %s in the hash-type sheet first (tap the hash type -> pick it); the choice is stored in preference last_type_value' % TYPES[t]
DIG = 'JdkHashCalculatorDigest'
e('JdkHashCalculator.setHashType', DIG + '.instanceFor(HashType)', 'CALL', 'JDK algorithms (MD5, SHA-1/2): instanceFor(hashType)', guard='!hashType.isKeccakj()', evidence='SRC JdkHashCalculator.java:34-35')
e(DIG + '.instanceFor(HashType)', DIG + '.setHashType', 'CALL', 'setHashType(hashType, null)', evidence='SRC JdkHashCalculatorDigest.java:35')
e(DIG + '.setHashType', 'HashType.getHashName', 'CALL', 'MessageDigest.getInstance(hashType.getHashName())', guard='not CRC-32, BLAKE2b or FNV-1a', evidence='SRC JdkHashCalculatorDigest.java:68-73')
for t in TYPES:
    e('JdkHashCalculator.setHashType', DIG + '.instanceFor(HashType)@' + t if t != 'SHA3' else DIG + '.instanceFor(HashType,String)@SHA3', 'CALL',
      'Special engine for ' + TYPES[t], guard='hash type is ' + TYPES[t], needs_state=NEED(t), evidence='SRC JdkHashCalculator.java:32-36')
    inst = DIG + '.instanceFor(HashType)@' + t if t != 'SHA3' else DIG + '.instanceFor(HashType,String)@SHA3'
    e(inst, DIG + '.setHashType@' + t, 'CALL', 'setHashType(hashType, provider)', needs_state=NEED(t), evidence='SRC JdkHashCalculatorDigest.java:35,45')
    e(inst, DIG + '.<init>', 'CALL', 'new JdkHashCalculatorDigest()', needs_state=NEED(t), evidence='SRC JdkHashCalculatorDigest.java:34,44')
e(DIG + '.setHashType@SHA3', 'HashType.getHashName', 'CALL', 'MessageDigest.getInstance(name, provider)', needs_state=NEED('SHA3'), evidence='SRC JdkHashCalculatorDigest.java:68-73')
e('JdkHashCalculator.setHashType', 'HashType.isKeccakj', 'CALL', 'hashType.isKeccakj()', evidence='SRC JdkHashCalculator.java:32')
e(DIG + '.setHashType@BLAKE', 'Blake2B.<init>()', 'CALL', 'blake2B = new Blake2B()', needs_state=NEED('BLAKE'), evidence='SRC JdkHashCalculatorDigest.java:56-58')
e(DIG + '.setHashType@BLAKE', 'Blake2B.<clinit>', 'CALL', 'Class initialisation on first use', needs_state=NEED('BLAKE'), evidence='SRC JdkHashCalculatorDigest.java:57 (new Blake2B()), Blake2B.java:9-34 (static fields); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e(DIG + '.setHashType@FNV', 'FNV1a.<init>', 'CALL', 'fnv1A = new FNV1a()', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:59-67')
e(DIG + '.setHashType@FNV', 'FNV1a.setInstance', 'CALL', 'fnv1A.setInstance(hashType.getTypeAsString())', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:66')
e(DIG + '.setHashType@FNV', 'HashType.getTypeAsString', 'CALL', 'hashType.getTypeAsString()', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:66')
e(DIG + '.setHashType@FNV', 'FNV1a.<clinit>', 'CALL', 'Class initialisation on first use', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:65 (new FNV1a()), FNV1a.java:8-15 (static fields); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
# per-type update/result: from-layer calls into the right variant
FROM = {'JdkHashCalculator.fromString': ('update(byte[])', ), 'JdkHashCalculator.fromFile(InputStream)': ('update(byte[],int)', ),
        'JdkHashCalculator.fromFolder(List)': ('update(byte[],int)', )}
for frm, (upd,) in FROM.items():
    e(frm, DIG + '.' + upd, 'CALL', 'jdkHashCalculatorDigest.update(...) for MD5/SHA-1/SHA-2', evidence='SRC JdkHashCalculator.java:46,72,106')
    e(frm, DIG + '.result', 'CALL', 'jdkHashCalculatorDigest.result()', evidence='SRC JdkHashCalculator.java:47,75,113')
    for t in TYPES:
        e(frm, DIG + '.' + upd + '@' + t, 'CALL', 'update(...) for ' + TYPES[t], needs_state=NEED(t), evidence='SRC JdkHashCalculator.java:46,72,106')
        e(frm, DIG + '.result@' + t, 'CALL', 'result() for ' + TYPES[t], needs_state=NEED(t), evidence='SRC JdkHashCalculator.java:47,75,113')
e(DIG + '.update(byte[])@BLAKE', 'Blake2B.reset', 'CALL', 'blake2B.reset()', needs_state=NEED('BLAKE'), evidence='SRC JdkHashCalculatorDigest.java:81-83')
e(DIG + '.update(byte[])@BLAKE', 'Blake2B.update(byte[])', 'CALL', 'blake2B.update(input)', needs_state=NEED('BLAKE'), evidence='SRC JdkHashCalculatorDigest.java:83')
e(DIG + '.update(byte[],int)@BLAKE', 'Blake2B.update(byte[],int,int)', 'CALL', 'blake2B.update(input, 0, length)', needs_state=NEED('BLAKE'), evidence='SRC JdkHashCalculatorDigest.java:96-97')
e(DIG + '.update(byte[])@FNV', 'FNV1a.reset', 'CALL', 'fnv1A.reset()', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:84-86')
e(DIG + '.update(byte[])@FNV', 'FNV1a.update(byte[])', 'CALL', 'fnv1A.update(input)', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:86')
e(DIG + '.update(byte[],int)@FNV', 'FNV1a.update(byte[],int,int)', 'CALL', 'fnv1A.update(input, 0, length)', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:98-99')
e(DIG + '.result@BLAKE', 'Blake2B.getValue', 'CALL', 'blake2B.getValue()', needs_state=NEED('BLAKE'), evidence='SRC JdkHashCalculatorDigest.java:109-110')
e(DIG + '.result@FNV', 'FNV1a.getValue', 'CALL', 'fnv1A.getValue()', needs_state=NEED('FNV'), evidence='SRC JdkHashCalculatorDigest.java:111-112')
e(DIG + '.result@CRC', 'JdkHashUtils.getStringFromLong', 'CALL', 'JdkHashUtils.getStringFromLong(crc32.getValue())', needs_state=NEED('CRC'), evidence='SRC JdkHashCalculatorDigest.java:107-108')
e(DIG + '.result', 'JdkHashUtils.getStringFromByteArray', 'CALL', 'JdkHashUtils.getStringFromByteArray(messageDigest.digest())', evidence='SRC JdkHashCalculatorDigest.java:114')
e(DIG + '.result@SHA3', 'JdkHashUtils.getStringFromByteArray', 'CALL', 'getStringFromByteArray(messageDigest.digest())', needs_state=NEED('SHA3'), evidence='SRC JdkHashCalculatorDigest.java:114')
e(DIG + '.result', 'JdkHashUtils.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC JdkHashCalculatorDigest.java:108,114 (JdkHashUtils.getStringFromLong / getStringFromByteArray), JdkHashUtils.java:7 (static HEX_DIGITS); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('JdkHashCalculator.fromFile(Context,Uri)', 'JdkHashCalculator.fromFile(InputStream)', 'CALL', 'fromFile(stream)', evidence='SRC JdkHashCalculator.java:54-55')
e('JdkHashCalculator.fromFolder(Context,Uri)', 'JdkHashCalculator.fromFolder(List)', 'CALL', 'fromFolder(streams)', evidence='SRC JdkHashCalculator.java:87-88')
e('JdkHashCalculator.fromFile(Context,Uri)', 'JdkHashCalculator.inputStreamFromUri', 'CALL', 'opens the stream', evidence='SRC JdkHashCalculator.java:54')
e('JdkHashCalculator.fromFolder(Context,Uri)', 'JdkHashCalculator.inputStreamsFormFolder', 'CALL', 'opens a stream per child', evidence='SRC JdkHashCalculator.java:87')
e('JdkHashCalculator.inputStreamsFormFolder', 'JdkHashCalculator.inputStreamFromUri', 'CALL', 'per child', evidence='SRC JdkHashCalculator.java:140')

# the three startActivity* calls catch ActivityNotFoundException and show a snackbar
for h, ln in (('openSystemFileManager', '197-200'), ('openSystemFolderManager', '208-211'), ('saveTextFile', '287-290')):
    e(HC + '.' + h, HC + '.showSnackbarWithoutAction', 'CALL', 'ActivityNotFoundException: snackbar "cannot start the file selector"', guard='no app can handle the intent',
      env=ENV_NOAPP, evidence='SRC HashCalculatorFragment.java:' + ln)
# ------------------------------------------------------------------ copy / progress / exit handling
e(HC + '.lambda$onViewCreated$4', HC + '.copyHashFromEditText', 'CALL', 'copyHashFromEditText(etCustomHash)', evidence='SRC HashCalculatorFragment.java:446')
e(HC + '.lambda$onViewCreated$6', HC + '.copyHashFromEditText', 'CALL', 'copyHashFromEditText(etGeneratedHash)', evidence='SRC HashCalculatorFragment.java:452')
e(HC + '.copyHashFromEditText', 'Clipboard.<init>', 'CALL', 'new Clipboard(context, hash).copy()', evidence='SRC HashCalculatorFragment.java:534')
e('Clipboard.copy', 'Clipboard.clear', 'ASYNC', 'handler.postDelayed(runnable, 60 s): the clipboard is cleared', needs_state='Wait 60 seconds after copying', evidence='SRC Clipboard.java:30-31,35-39')
for cb in ('HashCalculatorFragment$1.onTextChanged', 'AppTextWatcher.beforeTextChanged', 'AppTextWatcher.afterTextChanged'):
    for lam in ('5', '7'):
        e(HC + '.lambda$onViewCreated$' + lam, cb, 'FRAMEWORK', 'editText.setText("") notifies the TextWatchers', evidence=FW_TW + '; SRC HashCalculatorFragment.java:449,455')
e('AppSnackbar.show@INFO', 'S_SNACKBAR_INFO', 'ENTERS', 'Info snackbar shown (its action is OK)', guard='no custom action', evidence='SRC AppSnackbar.java:62-94')
e('S_SNACKBAR_INFO', 'AppSnackbar.lambda$show$0', 'GUI', 'Tap OK on the snackbar', gui=['Tap "OK" on the snackbar'], evidence='SRC AppSnackbar.java:68-71')
# exit via double Back
e('MainActivity.onBackPressed@CALC', HC + '.appBackClick', 'CALL', 'fragment.appBackClick() on the current fragment', evidence='SRC MainActivity.java:153-156')
e('MainActivity.onBackPressed@CALC', HC + '.appResume', 'CALL', 'last fragment .appResume()', evidence='SRC MainActivity.java:157-163')
e(HC + '.appBackClick', HC + '.showSnachbarWithAction', 'CALL', 'First Back: "press back again / Exit now" snackbar', guard='!isBackButtonDoubleTap', evidence='SRC HashCalculatorFragment.java:374-385')
e(HC + '.showSnachbarWithAction', 'AppSnackbar.<init>(Context,View,int,String,OnClickListener,Settings,ThemeConfig)', 'CALL', 'new AppSnackbar(..., action)', evidence='SRC HashCalculatorFragment.java:398-406')
e(HC + '.showSnachbarWithAction', 'AppSnackbar.show@ACTION', 'CALL', 'show(): the snackbar has a custom action ("Exit now")', evidence='SRC HashCalculatorFragment.java:406')
e(HC + '.showSnachbarWithAction', 'S_MAIN_EXIT_PENDING', 'ENTERS', 'Exit snackbar visible', evidence='SRC HashCalculatorFragment.java:378-383')
e(HC + '.showSnackbarWithoutAction', 'AppSnackbar.show@INFO', 'CALL', 'new AppSnackbar(...).show() with the OK action', evidence='SRC HashCalculatorFragment.java:161-163')
e(HC + '.appBackClick', HC + '.lambda$appBackClick$3', 'ASYNC', 'new Handler().postDelayed(..., 300): resets the double-tap flag', guard='first Back', evidence='SRC HashCalculatorFragment.java:384')
e('S_MAIN_EXIT_PENDING', HC + '.lambda$appBackClick$2', 'GUI', 'Tap "Exit now" in the snackbar', gui=['Tap "Exit now"'], evidence='SRC HashCalculatorFragment.java:382')
e('S_MAIN_EXIT_PENDING', 'MainActivity.onBackPressed@CALC', 'SYSTEM', 'Second Back within 300 ms finishes the activity', gui=['Press Back twice quickly'], needs_state='Second Back within 300 ms of the first',
  evidence='SRC HashCalculatorFragment.java:386-388')
e(HC + '.lambda$appBackClick$2', 'S_EXIT', 'ENTERS', 'activity.finish()', evidence='SRC HashCalculatorFragment.java:382')
e(HC + '.appBackClick', 'S_EXIT', 'ENTERS', 'activity.finish() on the second Back', guard='isBackButtonDoubleTap', needs_state='Second Back within 300 ms of the first', evidence='SRC HashCalculatorFragment.java:386-388')
e('S_EXIT', 'S_ENTRY', 'SYSTEM', 'Next launch; the process may survive, so App.appComponent and Dagger objects can be reused (not a cold start)', evidence='INFERRED after the last activity finishes the process may stay alive (process lifetime is not in the sources read); SRC App.java:38 (appComponent is a static field)')

# ------------------------------------------------------------------ history
e('MainActivity.onOptionsItemSelected@HISTORY', 'MainActivity.hideKeyboard', 'CALL', 'hideKeyboard()', evidence='SRC MainActivity.java:127')
e('MainActivity.onOptionsItemSelected@HISTORY', 'HistoryFragment.<init>', 'CALL', 'showFragment(new HistoryFragment())', evidence='SRC MainActivity.java:132-133')
e('MainActivity.onOptionsItemSelected@HISTORY', 'MainActivity.showFragment@HISTORY', 'CALL', 'showFragment(...)', evidence='SRC MainActivity.java:133')
e('MainActivity.onOptionsItemSelected@SETTINGS', 'MainActivity.hideKeyboard', 'CALL', 'hideKeyboard()', evidence='SRC MainActivity.java:127')
e('MainActivity.onOptionsItemSelected@SETTINGS', 'SettingsFragment.<init>', 'CALL', 'showFragment(new SettingsFragment())', evidence='SRC MainActivity.java:129-130')
e('MainActivity.onOptionsItemSelected@SETTINGS', 'MainActivity.showFragment@SETTINGS', 'CALL', 'showFragment(...)', evidence='SRC MainActivity.java:130')
for key in ('HISTORY', 'SETTINGS'):
    e('MainActivity.onOptionsItemSelected@' + key, impl(HC, 'onOptionsItemSelected'), 'FRAMEWORK',
      'The item is then offered to the added fragments in order (the calculator first); it is not a home item', evidence='INFERRED androidx FragmentActivity.onMenuItemSelected passes the item to the FragmentManager, which offers it to the added fragments in order (androidx source not read)')
HF = 'HistoryFragment'
e(impl(HF, 'onViewCreated'), 'HistoryPresenterImpl.<init>', 'CALL', 'new HistoryPresenterImpl()', evidence='SRC HistoryFragment.java:78')
e('HistoryPresenterImpl.load', 'HistoryItemsLoaderTask.doInBackground', 'ASYNC', 'HistoryItemsLoaderTask.execute(): worker thread', guard='portion not complete', evidence='FW-SRC core/java/android/os/AsyncTask.java:219-224, 237-262, 594-596, 632-650, 326-334 (execute uses the serial executor, which hands each task to THREAD_POOL_EXECUTOR; the worker runnable calls doInBackground); SRC HistoryPresenterImpl.java:39')
e('HistoryItemsLoaderTask.doInBackground', 'HistoryItemsLoaderTask.onPostExecute', 'ASYNC', 'onPostExecute on the main thread', evidence='FW-SRC core/java/android/os/AsyncTask.java:369-374, 285, 705-713, 691-697 (postResult sends the result message to a handler on the main looper; its handleMessage calls finish, which calls onPostExecute unless the task was cancelled); SRC HistoryItemsLoaderTask.java:33-35')
e('HistoryItemsLoaderTask.doInBackground', 'OrmLiteLocalDataStorage.historyItems', 'CALL', 'localDataStorage.historyItems(portion)', evidence='SRC HistoryItemsLoaderTask.java:28')
e('HistoryFragment.setLoading', 'S_HISTORY_LOADING', 'ENTERS', 'Progress bar visible', evidence='SRC HistoryFragment.java:111-114')
e('HistoryPresenterImpl.postLoad', 'HistoryFragment.setLoaded@EMPTY', 'CALL', 'view.setLoaded(items) with an empty first page', guard='no history rows', evidence='SRC HistoryPresenterImpl.java:50-53')
e('HistoryPresenterImpl.postLoad', 'HistoryFragment.setLoaded@ROWS', 'CALL', 'view.setLoaded(items) with rows', guard='at least one history row', needs_state=NEED_HIST,
  evidence='SRC HistoryPresenterImpl.java:50-53')
e('HistoryFragment.setLoaded@EMPTY', 'S_HISTORY_EMPTY', 'ENTERS', '"History items not found", trash hidden', evidence='SRC HistoryFragment.java:117-131')
e('HistoryFragment.setLoaded@ROWS', 'S_HISTORY_LIST', 'ENTERS', 'Rows shown', needs_state=NEED_HIST, evidence='SRC HistoryFragment.java:117-126')
for v in ('EMPTY', 'ROWS'):
    for dst in ('HistoryItemsAdapter.<init>', 'HistoryItemsAdapter.addHistoryItems'):
        e('HistoryFragment.setLoaded@' + v, dst, 'CALL', 'adapter creation / addHistoryItems', needs_state=NEED_HIST if v == 'ROWS' else None,
          guard='first load' if dst.endswith('<init>') else None, evidence='SRC HistoryFragment.java:120-126')
e('HistoryFragment.setLoaded@ROWS', 'HistoryItemsAdapter.onCreateViewHolder', 'FRAMEWORK', 'RecyclerView creates the row views', needs_state=NEED_HIST, evidence=FW_ADAPTER)
e('HistoryFragment.setLoaded@ROWS', 'HistoryItemsAdapter.onBindViewHolder', 'FRAMEWORK', 'RecyclerView binds the rows', needs_state=NEED_HIST, evidence=FW_ADAPTER)
e('HistoryFragment.setLoaded@ROWS', 'HistoryItemsAdapter.getItemCount', 'FRAMEWORK', 'RecyclerView reads the count', needs_state=NEED_HIST, evidence=FW_ADAPTER)
e('HistoryFragment.setLoaded@ROWS', 'HistoryFragment$1.onScrolled', 'FRAMEWORK', 'RecyclerView calls onScrolled(0,0) after layout', needs_state=NEED_HIST,
  evidence='INFERRED androidx RecyclerView calls OnScrollListener.onScrolled after the layout pass (androidx source not read)')
e('S_HISTORY_LIST', 'HistoryFragment$1.onScrolled', 'GUI', 'Scroll the list', gui=['Scroll the history list'], needs_state=NEED_HIST, evidence='SRC HistoryFragment.java:61-77')
e('S_HISTORY_LIST', 'HistoryItemHolder.lambda$bind$0', 'GUI', 'Tap a history row: its hash is copied', gui=['Tap a history row'], needs_state=NEED_HIST,
  evidence='SRC HistoryItemHolder.java:46')
e('HistoryItemHolder.lambda$bind$0', 'Clipboard.<init>', 'CALL', 'new Clipboard(context, hash).copy()', evidence='SRC HistoryItemHolder.java:46')
e('OrmLiteLocalDataStorage.historyItems', 'HistoryItem.<init>()', 'FRAMEWORK', 'ORMLite builds each row object by reflection (no-arg constructor)', needs_state=NEED_HIST,
  evidence='INFERRED ORMLite BaseDaoImpl.query builds each row object through its object factory, which calls the no-argument constructor by reflection (ORMLite source not read)')
for p in ('S_HISTORY_LOADING', 'S_HISTORY_EMPTY', 'S_HISTORY_LIST'):
    e(p, 'HistoryFragment.onOptionsItemSelected@HOME', 'GUI', 'Tap the Up arrow (android.R.id.home)', gui=['Tap the Up arrow (top-left)'], evidence='SRC HistoryFragment.java:89-107; BaseFragment.java:83-93')
    e(p, 'MainActivity.onBackPressed@HISTORY', 'SYSTEM', 'Back on History', gui=['Press Back'], evidence='SRC MainActivity.java:150-164')
    e(p, 'S_HISTORY_PAUSED', 'ENTERS', 'Home / recents / screen off', gui=['Press Home / recents / screen off'], evidence=PAUSE_EV)
e('S_HISTORY_PAUSED', impl(HF, 'onResume'), 'SYSTEM', 'Back in the foreground', gui=['Return via recents'], evidence=RESUME_EV)
e('HistoryFragment.onOptionsItemSelected@HOME', impl(HF, 'onOptionsItemSelected').replace('HistoryFragment.', 'BaseFragment.') + '@HistoryFragment', 'CALL', 'super.onOptionsItemSelected(item)', evidence='SRC HistoryFragment.java:107')
e('BaseFragment.onOptionsItemSelected@HistoryFragment', 'MainActivity.onBackPressed@HISTORY', 'CALL', 'activity.onBackPressed() (Up is enabled for History)', guard='home item', evidence='SRC BaseFragment.java:85-90')
e('S_HISTORY_LIST', 'HistoryFragment.onOptionsItemSelected@TRASH', 'GUI', 'Tap the trash icon in the action bar', gui=['Tap the trash icon (top-right)'], needs_state=NEED_HIST,
  evidence='SRC R/menu/menu_history.xml; HistoryFragment.java:89-105')
e('HistoryFragment.onOptionsItemSelected@TRASH', 'AppAlertDialog.<init>', 'CALL', 'new AppAlertDialog(...)', evidence='SRC HistoryFragment.java:93-103')
e('HistoryFragment.onOptionsItemSelected@TRASH', 'AppAlertDialog.show', 'CALL', '.show()', evidence='SRC HistoryFragment.java:103')
e('HistoryFragment.onOptionsItemSelected@TRASH', 'S_DLG_CLEAR_HISTORY', 'ENTERS', 'Confirmation dialog', evidence='SRC HistoryFragment.java:93-104')
e('S_DLG_CLEAR_HISTORY', 'HistoryFragment.lambda$onOptionsItemSelected$0', 'GUI', 'Tap OK', gui=['Tap "OK"'], evidence='SRC HistoryFragment.java:98-101')
e('S_DLG_CLEAR_HISTORY', 'AppAlertDialog.lambda$show$0', 'GUI', 'Tap Cancel', gui=['Tap "Cancel"'], evidence='SRC AppAlertDialog.java:42')
e('S_DLG_CLEAR_HISTORY', 'S_HISTORY_LIST', 'ENTERS', 'Cancel / Back closes the dialog; the history list is unchanged', gui=['Tap "Cancel" or press Back'],
  needs_state=NEED_HIST, evidence=DLG_CANCEL_EV)
e('HistoryFragment.lambda$onOptionsItemSelected$0', 'S_HISTORY_EMPTY', 'ENTERS', 'History cleared, trash hidden', evidence='SRC HistoryFragment.java:99-100')

# ------------------------------------------------------------------ settings
SF = 'SettingsFragment'
e('SettingsFragment.onCreatePreferences', 'SettingsPresenterImpl.<init>', 'CALL', 'new SettingsPresenterImpl()', evidence='SRC SettingsFragment.java:92')
ROW = (('lambda$initLanguageSettings$0', 'Language', 'S_SHEET_LANGUAGES'), ('lambda$initThemeSettings$1', 'Theme', 'S_SHEET_THEMES'),
       ('lambda$initPrivacyPolicy$2', 'Privacy policy', 'S_SHEET_PRIVACY'), ('lambda$initAuthorLinks$4', 'Author', 'S_SHEET_AUTHOR'),
       ('lambda$initLibrariesLinks$5', 'Libraries', 'S_SHEET_LIBRARIES'))
for lam, label, page in ROW:
    e('S_SETTINGS', 'SettingsFragment.' + lam, 'GUI', 'Tap the %s row' % label, gui=['Tap "%s"' % label], evidence='SRC SettingsFragment.java:158-224; R/xml/settings.xml')
    e('SettingsFragment.' + lam, page, 'ENTERS', 'The %s bottom sheet opens' % label.lower(), evidence='SRC SettingsFragment.java:158-224')
    e(page, 'S_SETTINGS', 'ENTERS', 'The sheet closes (row tapped, Back or tap outside)', gui=['Press Back or tap outside the sheet'], evidence='SRC BaseListAdapter.java:55-57 (dismissBottomSheet calls bottomSheet.dismiss()), WebLinksListAdapter.java:62,66 and ThemesListAdapter.java:50 (rows that dismiss the sheet); INFERRED Back or a tap outside dismisses a BottomSheetDialogFragment (material source not read)')
e('S_SETTINGS', 'SettingsFragment.lambda$initUserDataExport$3', 'GUI', 'Tap "Export user data"', gui=['Tap "Export user data"'], evidence='SRC SettingsFragment.java:194-202')
e('SettingsFragment.lambda$initUserDataExport$3', 'SettingsPresenterImpl.saveUserData', 'CALL', 'settingsPresenter.saveUserData()', evidence='SRC SettingsFragment.java:198')
e('SettingsPresenterImpl.saveUserData', 'OrmLiteLocalDataStorage.isHistoryItemsListIsEmpty', 'CALL', 'localDataStorage.isHistoryItemsListIsEmpty() (the name is inverted: true when rows exist)', evidence='SRC SettingsPresenterImpl.java:44; OrmLiteLocalDataStorage.java:107-109')
e('SettingsPresenterImpl.saveUserData', 'SettingsPresenter$SaveUserDataResult.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC SettingsPresenterImpl.java:50 (SaveUserDataResult.DONE is used); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('SettingsPresenterImpl.saveUserData', 'SettingsFragment.saveUserDataResult@EMPTY', 'CALL', 'History is empty: result EMPTY', guard='countOf() == 0', evidence='SRC SettingsPresenterImpl.java:55-57')
e('SettingsPresenterImpl.saveUserData', 'SettingsFragment.saveUserDataResult@DONE', 'CALL', 'History has rows: result DONE with an ACTION_CREATE_DOCUMENT intent', guard='countOf() > 0',
  needs_state=NEED_HIST, evidence='SRC SettingsPresenterImpl.java:44-50')
e('SettingsPresenterImpl.saveUserData', 'SettingsFragment.saveUserDataResult@ERROR', 'CALL', 'ActivityNotFoundException: result ERROR', guard='no app can create documents', env=ENV_EXC, evidence='SRC SettingsPresenterImpl.java:51-53')
e('SettingsPresenterImpl.saveUserData', 'LogUtils.e', 'CALL', 'ActivityNotFoundException', env=ENV_EXC, evidence='SRC SettingsPresenterImpl.java:52')
e('SettingsFragment.saveUserDataResult@EMPTY', 'AppSnackbar.<init>(Context,View,int,Settings,ThemeConfig)', 'CALL', 'snackbar "history is empty"', evidence='SRC SettingsFragment.java:308-319')
e('SettingsFragment.saveUserDataResult@EMPTY', 'AppSnackbar.show@INFO', 'CALL', 'show()', evidence='SRC SettingsFragment.java:317')
e('SettingsFragment.saveUserDataResult@ERROR', 'AppSnackbar.<init>(Context,View,int,Settings,ThemeConfig)', 'CALL', 'snackbar "cannot start the file selector"', env=ENV_EXC, evidence='SRC SettingsFragment.java:296-306')
e('SettingsFragment.saveUserDataResult@ERROR', 'AppSnackbar.show@INFO', 'CALL', 'show()', env=ENV_EXC, evidence='SRC SettingsFragment.java:305')
e('SettingsFragment.saveUserDataResult@DONE', 'S_EXT_CREATE_ZIP', 'ENTERS', 'startActivityForResult(ACTION_CREATE_DOCUMENT application/zip)', needs_state=NEED_HIST,
  evidence='SRC SettingsFragment.java:293-295')
e('S_EXT_CREATE_ZIP', 'SettingsFragment.onActivityResult@OK', 'RESULT', 'The user confirms the file name: onActivityResult(FILE_CREATE, RESULT_OK, data)', gui=['In the system dialog: confirm the file name'],
  env=ENV_SAF, needs_state=NEED_HIST, evidence='SRC SettingsFragment.java:119-124')
e('S_EXT_CREATE_ZIP', 'SettingsFragment.onActivityResult@CANCELED', 'RESULT', 'Back / Cancel: onActivityResult with no data (does nothing)', gui=['Press Back in the system dialog'], needs_state=NEED_HIST,
  evidence=RES_CANCEL_EV + '; SRC SettingsFragment.java:120-123')
e('SettingsFragment.onActivityResult@OK', 'SettingsFragment.copyUserDataToUserFolder', 'CALL', 'copyUserDataToUserFolder(data.getData())', evidence='SRC SettingsFragment.java:121-123')
e('SettingsFragment.copyUserDataToUserFolder', 'LocalDataExporter.exportDatabase', 'CALL', 'LocalDataExporter.exportDatabase(context, storage)', evidence='SRC SettingsFragment.java:129')
e('SettingsFragment.copyUserDataToUserFolder', 'LogUtils.e', 'CALL', 'IOException', env=ENV_EXC, evidence='SRC SettingsFragment.java:138-140')
e('S_SETTINGS', 'SettingsFragment.lambda$initHelpWithTranslations$6', 'GUI', 'Tap "Help with translation"', gui=['Tap "Help with translation"'], evidence='SRC SettingsFragment.java:229-240')
e('S_SETTINGS', 'SettingsFragment.lambda$initAppVersionInfo$9', 'GUI', 'Tap the version row', gui=['Tap the "Version" row'], evidence='SRC SettingsFragment.java:276-287')
e('S_SETTINGS', 'SettingsFragment.lambda$initFeedback$8', 'GUI', 'Tap "Feedback"', gui=['Tap "Feedback"'], evidence='SRC SettingsFragment.java:262-273')
e('SettingsFragment.lambda$initFeedback$8', 'FeedbackFragment.<init>', 'CALL', 'activity.showFragment(new FeedbackFragment())', evidence='SRC SettingsFragment.java:268')
e('SettingsFragment.lambda$initFeedback$8', 'MainActivity.showFragment@FEEDBACK', 'CALL', 'showFragment(...)', evidence='SRC SettingsFragment.java:268')
for lam in ('lambda$initHelpWithTranslations$6', 'lambda$initAppVersionInfo$9'):
    e('SettingsFragment.' + lam, 'WebUtils.openWebLink', 'CALL', 'WebUtils.openWebLink(context, url)', evidence='SRC SettingsFragment.java:233,281')
e('WebUtils.openWebLink', 'S_EXT_OTHER_APP', 'ENTERS', 'ACTION_VIEW opens the browser', evidence='SRC WebUtils.java:50-56')
e('WebUtils.openWebLink', 'LogUtils.e', 'CALL', 'ActivityNotFoundException (no browser)', env=ENV_NOAPP, evidence='SRC WebUtils.java:53-55')
e('S_SETTINGS', 'SettingsFragment.onOptionsItemSelected', 'GUI', 'Tap the Up arrow (android.R.id.home)', gui=['Tap the Up arrow (top-left)'], evidence='SRC SettingsFragment.java:336-345')
e('SettingsFragment.onOptionsItemSelected', 'MainActivity.onBackPressed@SETTINGS', 'CALL', 'activity.onBackPressed()', guard='home item', evidence='SRC SettingsFragment.java:337-342')
e('S_SETTINGS', 'MainActivity.onBackPressed@SETTINGS', 'SYSTEM', 'Back on Settings', gui=['Press Back'], evidence='SRC MainActivity.java:150-164')
e('S_SETTINGS', 'S_SETTINGS_PAUSED', 'ENTERS', 'Home / recents / screen off', gui=['Press Home / recents / screen off'], evidence=PAUSE_EV)
e('S_SETTINGS_PAUSED', 'SettingsFragment.onResume', 'SYSTEM', 'Back in the foreground', gui=['Return via recents'], evidence=RESUME_EV)
e('SettingsFragment.onResume', 'SettingsFragment.appResume', 'CALL', 'appResume()', evidence='SRC SettingsFragment.java:324-327')
# Back out of fragments
e('MainActivity.onBackPressed@HISTORY', 'BaseFragment.appBackClick', 'CALL', 'History: appBackClick() removes the fragment', evidence='SRC MainActivity.java:153-156; BaseFragment.java:124-129')
e('MainActivity.onBackPressed@HISTORY', HC + '.appResume', 'CALL', 'The calculator becomes the last fragment: appResume()', evidence='SRC MainActivity.java:157-163')
e('MainActivity.onBackPressed@SETTINGS', 'SettingsFragment.appBackClick', 'CALL', 'Settings: appBackClick() removes the fragment', evidence='SRC SettingsFragment.java:349-351')
e('MainActivity.onBackPressed@SETTINGS', HC + '.appResume', 'CALL', 'The calculator becomes the last fragment: appResume()', evidence='SRC MainActivity.java:157-163')
e('MainActivity.onBackPressed@FEEDBACK', 'BaseFragment.appBackClick', 'CALL', 'Feedback: appBackClick()', evidence='SRC BaseFragment.java:124-129')
e('MainActivity.onBackPressed@FEEDBACK', 'SettingsFragment.appResume', 'CALL', 'Settings becomes the last fragment: appResume()', evidence='SRC MainActivity.java:157-163')
e('MainActivity.onBackPressed@WEB', 'BaseFragment.appBackClick', 'CALL', 'Web: appBackClick()', evidence='SRC BaseFragment.java:124-129')
e('MainActivity.onBackPressed@WEB', 'SettingsFragment.appResume', 'CALL', 'Settings becomes the last fragment: appResume()', evidence='SRC MainActivity.java:157-163')
for src in ('MainActivity.onBackPressed@HISTORY', 'MainActivity.onBackPressed@SETTINGS'):
    # the calculator keeps the source it had; only the empty page is modelled so that Back can never invent a selected source
    e(src, MAIN('EMPTY'), 'ENTERS', 'Back returns to the calculator (it keeps the source it had; modelled for the empty page)', evidence='SRC MainActivity.java:150-164')
for src in ('MainActivity.onBackPressed@FEEDBACK', 'MainActivity.onBackPressed@WEB'):
    e(src, 'S_SETTINGS', 'ENTERS', 'Back returns to Settings', evidence='SRC MainActivity.java:150-164')
# language and theme restarts
e('S_SHEET_LANGUAGES', 'BaseListHolder.lambda$bind$0@LanguagesListAdapter$LanguagesListHolder', 'GUI', 'Tap a language', gui=['Tap a language'], evidence='SRC LanguagesListAdapter.java:55-72')
e('S_SHEET_THEMES', 'BaseListHolder.lambda$bind$0@THEME_SAME', 'GUI', 'Tap the theme that is already selected', gui=['Tap the current theme'], evidence='SRC ThemesListAdapter.java:48-54')
e('S_SHEET_THEMES', 'BaseListHolder.lambda$bind$0@THEME_OTHER', 'GUI', 'Tap the other theme', gui=['Tap the other theme'], evidence='SRC ThemesListAdapter.java:48-54')
e('BaseListHolder.lambda$bind$0@THEME_SAME', 'ThemesListAdapter$ThemesListHolder.callItemClick@SAME', 'CALL', 'callItemClick()', evidence='SRC BaseListHolder.java:44')
e('BaseListHolder.lambda$bind$0@THEME_OTHER', 'ThemesListAdapter$ThemesListHolder.callItemClick@OTHER', 'CALL', 'callItemClick()', evidence='SRC BaseListHolder.java:44')
e('ThemesListAdapter$ThemesListHolder.callItemClick@SAME', 'BaseListAdapter.dismissBottomSheet', 'CALL', 'same theme: dismissBottomSheet()', evidence='SRC ThemesListAdapter.java:49-50')
e('ThemesListAdapter$ThemesListHolder.callItemClick@OTHER', 'ThemesListAdapter$ThemesListHolder.showThemeApplyDialog', 'CALL', 'different theme: showThemeApplyDialog()', evidence='SRC ThemesListAdapter.java:51-53')
e('ThemesListAdapter$ThemesListHolder.callItemClick@SAME', 'ThemeConfigImpl.currentTheme', 'CALL', 'themeConfig.currentTheme()', evidence='SRC ThemesListAdapter.java:49')
e('ThemesListAdapter$ThemesListHolder.callItemClick@OTHER', 'ThemeConfigImpl.currentTheme', 'CALL', 'themeConfig.currentTheme()', evidence='SRC ThemesListAdapter.java:49')
e('LanguagesListAdapter$LanguagesListHolder.callItemClick', 'S_DLG_CHANGE_LANGUAGE', 'ENTERS', 'Restart-warning dialog', evidence='SRC LanguagesListAdapter.java:55-70')
e('ThemesListAdapter$ThemesListHolder.showThemeApplyDialog', 'S_DLG_CHANGE_THEME', 'ENTERS', 'Restart-warning dialog', evidence='SRC ThemesListAdapter.java:62-77')
e('S_DLG_CHANGE_LANGUAGE', 'LanguagesListAdapter$LanguagesListHolder.lambda$callItemClick$0', 'GUI', 'Tap OK', gui=['Tap "OK"'], evidence='SRC LanguagesListAdapter.java:61-68')
e('S_DLG_CHANGE_THEME', 'ThemesListAdapter$ThemesListHolder.lambda$showThemeApplyDialog$0', 'GUI', 'Tap OK', gui=['Tap "OK"'], evidence='SRC ThemesListAdapter.java:68-75')
for p, back in (('S_DLG_CHANGE_LANGUAGE', 'S_SHEET_LANGUAGES'), ('S_DLG_CHANGE_THEME', 'S_SHEET_THEMES')):
    e(p, 'AppAlertDialog.lambda$show$0', 'GUI', 'Tap Cancel', gui=['Tap "Cancel"'], evidence='SRC AppAlertDialog.java:42')
    e(p, back, 'ENTERS', 'Cancel / Back closes the dialog; the bottom sheet underneath stays', gui=['Tap "Cancel" or press Back'],
      evidence=DLG_CANCEL_EV + '; ' + SHEET_STAYS[p])
e('LanguagesListAdapter$LanguagesListHolder.lambda$callItemClick$0', 'AppUtils.restartApp', 'CALL', 'AppUtils.restartApp(activity)', evidence='SRC LanguagesListAdapter.java:65-67')
e('ThemesListAdapter$ThemesListHolder.lambda$showThemeApplyDialog$0', 'AppUtils.restartApp', 'CALL', 'AppUtils.restartApp(activity)', evidence='SRC ThemesListAdapter.java:72-74')
e('AppUtils.restartApp', 'MainActivity.<init>', 'INTENT', 'startActivity(new Intent(activity, MainActivity.class)) then finish() of the old instance', evidence='SRC AppUtils.java:16-20')
e('AppUtils.restartApp', 'S_EXIT', 'ENTERS', 'The old MainActivity instance finishes', evidence='SRC AppUtils.java:19')
# web-link rows: privacy -> WebView; author/libraries -> browser
for key in ('PRIVACY', 'AUTHOR', 'LIBRARIES'):
    ctx = 'PRIVACY' if key == 'PRIVACY' else 'LINK'
    e('S_SHEET_' + key, 'BaseListHolder.lambda$bind$0@WEB_' + ctx, 'GUI', 'Tap a link row', gui=['Tap a link'], evidence='SRC WebLinksListAdapter.java:55-67')
e('BaseListHolder.lambda$bind$0@WEB_PRIVACY', 'WebLinksListAdapter$WebLinksListHolder.callItemClick@PRIVACY', 'CALL', 'callItemClick()', evidence='SRC BaseListHolder.java:44')
e('BaseListHolder.lambda$bind$0@WEB_LINK', 'WebLinksListAdapter$WebLinksListHolder.callItemClick@LINK', 'CALL', 'callItemClick()', evidence='SRC BaseListHolder.java:44')
e('WebLinksListAdapter$WebLinksListHolder.callItemClick@PRIVACY', 'WebFragment.<init>', 'CALL', 'activity.showFragment(new WebFragment(link))', evidence='SRC WebLinksListAdapter.java:57-61')
e('WebLinksListAdapter$WebLinksListHolder.callItemClick@PRIVACY', 'MainActivity.showFragment@WEB', 'CALL', 'showFragment(...)', evidence='SRC WebLinksListAdapter.java:60')
e('WebLinksListAdapter$WebLinksListHolder.callItemClick@LINK', 'WebUtils.openWebLink', 'CALL', 'WebUtils.openWebLink(context, link)', evidence='SRC WebLinksListAdapter.java:65')
# web page and feedback page
e(impl('WebFragment', 'onViewCreated'), 'S_WEB_PRIVACY', 'FRAMEWORK', 'webView.loadUrl(url): the privacy policy loads', evidence='SRC WebFragment.java:38-43')
e('S_WEB_PRIVACY', impl('WebFragment', 'onOptionsItemSelected'), 'GUI', 'Tap the Up arrow', gui=['Tap the Up arrow (top-left)'], evidence='SRC BaseFragment.java:83-93')
e(impl('WebFragment', 'onOptionsItemSelected'), 'MainActivity.onBackPressed@WEB', 'CALL', 'activity.onBackPressed()', guard='home item', evidence='SRC BaseFragment.java:85-90')
e('S_WEB_PRIVACY', 'MainActivity.onBackPressed@WEB', 'SYSTEM', 'Back on the web page', gui=['Press Back'], evidence='SRC MainActivity.java:150-164')
e('S_WEB_PRIVACY', 'S_WEB_PAUSED', 'ENTERS', 'Home / recents / screen off', gui=['Press Home / recents / screen off'], evidence=PAUSE_EV)
e('S_WEB_PAUSED', impl('WebFragment', 'onResume'), 'SYSTEM', 'Back in the foreground', gui=['Return via recents'], evidence=RESUME_EV)
FB = 'FeedbackFragment'
e(impl(FB, 'onViewCreated'), 'FeedbackPresenterImpl.<init>', 'CALL', 'new FeedbackPresenterImpl()', evidence='SRC FeedbackFragment.java:50')
e(impl(FB, 'onViewCreated'), 'FeedbackPresenterImpl.<clinit>', 'CALL', 'Class initialisation on first use (static Feedback object)', evidence='SRC FeedbackPresenterImpl.java:15-21 (static Feedback field initializer); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('S_FEEDBACK', 'S_FEEDBACK_TYPED', 'ENTERS', 'Type a message', gui=['Type a message in the feedback field'], evidence='SRC R/layout/fragment_feedback.xml')
e('S_FEEDBACK', 'FeedbackFragment.onOptionsItemSelected@SEND_EMPTY', 'GUI', 'Tap Send with an empty message', gui=['Tap "Send" (top-right)'], evidence='SRC FeedbackFragment.java:68-77')
e('S_FEEDBACK_TYPED', 'FeedbackFragment.onOptionsItemSelected@SEND', 'GUI', 'Tap Send with a message', gui=['Tap "Send" (top-right)'], evidence='SRC FeedbackFragment.java:68-77')
for p in ('S_FEEDBACK', 'S_FEEDBACK_TYPED'):
    e(p, 'FeedbackFragment.onOptionsItemSelected@HOME', 'GUI', 'Tap the close icon (android.R.id.home)', gui=['Tap the X (top-left)'], evidence='SRC FeedbackFragment.java:61-67')
    e(p, 'MainActivity.onBackPressed@FEEDBACK', 'SYSTEM', 'Back on Feedback', gui=['Press Back'], evidence='SRC MainActivity.java:150-164')
    e(p, 'S_FEEDBACK_PAUSED', 'ENTERS', 'Home / recents / screen off', gui=['Press Home / recents / screen off'], evidence=PAUSE_EV)
e('S_FEEDBACK_PAUSED', impl(FB, 'onResume'), 'SYSTEM', 'Back in the foreground', gui=['Return via recents'], evidence=RESUME_EV)
e('FeedbackFragment.onOptionsItemSelected@HOME', 'MainActivity.onBackPressed@FEEDBACK', 'CALL', 'activity.onBackPressed()', evidence='SRC FeedbackFragment.java:62-67')
e('FeedbackFragment.onOptionsItemSelected@SEND_EMPTY', 'BaseFragment.onOptionsItemSelected@FeedbackFragment', 'CALL', 'super.onOptionsItemSelected(item)', evidence='SRC FeedbackFragment.java:78')
e('FeedbackFragment.onOptionsItemSelected@SEND', 'BaseFragment.onOptionsItemSelected@FeedbackFragment', 'CALL', 'super.onOptionsItemSelected(item)', evidence='SRC FeedbackFragment.java:78')
e('FeedbackFragment.onOptionsItemSelected@SEND', 'FeedbackPresenterImpl.sendFeedback', 'CALL', 'feedbackPresenter.sendFeedback(email, message, subject)', evidence='SRC FeedbackFragment.java:71-75')
e('FeedbackPresenterImpl.sendFeedback', 'FeedbackFragment.sendEmail', 'CALL', 'view.sendEmail(emailIntent)', evidence='SRC FeedbackPresenterImpl.java:45')
e('FeedbackFragment.sendEmail', 'S_EXT_OTHER_APP', 'ENTERS', 'startActivity(createChooser(...)): the email chooser', evidence='SRC FeedbackFragment.java:107-113')
e('FeedbackFragment.sendEmail', 'LogUtils.e', 'CALL', 'ActivityNotFoundException', env=ENV_NOAPP, evidence='SRC FeedbackFragment.java:114-116')
e(impl(FB, 'onViewCreated'), 'FeedbackPresenterImpl.init', 'CALL', 'feedbackPresenter.init(this)', evidence='SRC FeedbackFragment.java:51')

# ------------------------------------------------------------------ data layer, settings, theme, language
e('App.onCreate', 'OrmLiteLocalDataStorage.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC App.java:56 (new OrmLiteLocalDataStorage); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('App.onCreate', 'SharedPreferencesSettings.getSelectedTheme', 'CALL', 'settings.getSelectedTheme().getThemeResId()', evidence='SRC App.java:68')
e('SharedPreferencesSettings.getSelectedTheme', 'Theme.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC SharedPreferencesSettings.java:104 (Theme.values()); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('SharedPreferencesSettings.getLanguage', 'Language.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC SharedPreferencesSettings.java:68 (Language.valueOf); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('SharedPreferencesSettings.getLastHashType', 'HashType.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC SharedPreferencesSettings.java:42 (HashType.MD5); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('SourceSelectActionsBottomSheet.getActions', 'Action.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC SourceSelectActionsBottomSheet.java:39 (Action.TEXT); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('Action.<clinit>', 'UserActionType.<clinit>', 'CALL', 'Action constants reference UserActionType', evidence='SRC Action.java:13-18')
e('PrivacyPolicyWebLinksBottomSheet.getLinks', 'WebLink.<clinit>', 'CALL', 'Class initialisation on first use', evidence='SRC PrivacyPolicyWebLinksBottomSheet.java:37 (WebLink.PRIVACY_POLICY); INFERRED the JVM runs <clinit> on first use of the class (Java language rule, not read from a source)')
e('HistoryItemsLoaderTask.doInBackground', 'OrmLiteLocalDataStorage.onCreate', 'FRAMEWORK', 'The first DAO use opens the database; SQLiteOpenHelper calls onCreate when the file does not exist',
  guard='database file missing (first use)', evidence='INFERRED SQLiteOpenHelper.getDatabaseLocked calls onCreate when the database file does not exist (android.database.sqlite source not read); SRC OrmLiteLocalDataStorage.java:43-53')
e(HC + '.lambda$new$1', 'OrmLiteLocalDataStorage.onCreate', 'FRAMEWORK', 'localDataStorage.addHistoryItem(...) opens the database; onCreate runs if the file does not exist',
  guard='database file missing (first use) and "Save result to History" on', evidence='INFERRED SQLiteOpenHelper opens the database on first use and calls onCreate when the file does not exist (android.database.sqlite source not read); SRC OrmLiteLocalDataStorage.java:43-53')
e('OrmLiteLocalDataStorage.onCreate', 'LogUtils.e', 'CALL', 'SQLException while creating the table', env=ENV_EXC, evidence='SRC OrmLiteLocalDataStorage.java:49-51')

# every LogUtils.e call site sits in a catch block: they are all environment-gated
for c in AUTO['calls']:
    if c['dst'] == 'LogUtils.e' and c['src'] != 'SharedPreferencesSettings.getLastHashType':   # that catch needs a pre-seeded preference (see below)
        e(c['src'], 'LogUtils.e', 'CALL', 'catch block logs the exception', env=ENV_EXC, evidence='SRC %s:%s (bytecode)' % (c['file'], c['line']))

SUPPRESS = {
    'LogUtils.e',                                    # replaced by the environment-gated edges above
    'BaseListHolder.lambda$bind$0',                  # plain node: CHA to every holder; contexts are wired by hand
    ('App.onTerminate', 'OrmLiteLocalDataStorage.releaseHelper'),
}
for c in AUTO['calls']:
    if c['dst'] in ('BaseFragment.setAllowBackAction', 'BaseFragment.getBackActionIconResId'):
        SUPPRESS.add((c['src'], c['dst']))
# a holder only handles its own item type: drop the CHA edges from bind() to the other enums
_own = {'ActionsListAdapter$ActionHolder': 'Action', 'HashesListAdapter$HashesListHolder': 'HashType', 'LanguagesListAdapter$LanguagesListHolder': 'Language',
        'ThemesListAdapter$ThemesListHolder': 'Theme', 'WebLinksListAdapter$WebLinksListHolder': 'WebLink'}
for c in AUTO['calls']:
    if c['src'].startswith('BaseListHolder.bind') and c['dst'].split('.')[0] in set(_own.values()):
        holder = c['src'].split('@')[1] if '@' in c['src'] else None
        if holder is None or _own.get(holder) != c['dst'].split('.')[0]:
            SUPPRESS.add((c['src'], c['dst']))


# ---------------------------------------------------------------- schema 2 (see handoff/SCHEMA_V2.md)
import re

# DEAD and FRAMEWORK_ONLY become UNREACHABLE: (kind, reason, source reference of the declaration, how confirmed).
_UNREACHABLE_KIND = { "OrmLiteConfigUtil.<init>": "no_trigger_in_app", "OrmLiteConfigUtil.main": "no_trigger_in_app", "DbEntity.getId": "no_trigger_in_app", "DbEntity.setId": "no_trigger_in_app", "AppUtils.<init>": "no_trigger_in_app", "HashConstants.<init>": "no_trigger_in_app", "JdkHashUtils.<init>": "no_trigger_in_app", "LocalDataExporter.<init>": "no_trigger_in_app", "LogUtils.<init>": "no_trigger_in_app", "UIUtils.<init>": "no_trigger_in_app", "WebUtils.<init>": "no_trigger_in_app", "SettingsFragment.lambda$initRate$7": "closed_by_configuration", "BaseFragment.setAllowBackAction": "no_trigger_in_app", "BaseFragment.getBackActionIconResId": "no_trigger_in_app", "App.onTerminate": "framework_never_calls", "OrmLiteLocalDataStorage.releaseHelper": "no_trigger_in_app", "OrmLiteLocalDataStorage.onUpgrade": "framework_never_calls", "HistoryItem.equals": "no_trigger_in_app", "HistoryItem.hashCode": "no_trigger_in_app", "AppTextWatcher.onTextChanged": "no_trigger_in_app" }
_UNREACHABLE_REF = { "OrmLiteConfigUtil.<init>": "OrmLiteConfigUtil.java:5", "OrmLiteConfigUtil.main": "OrmLiteConfigUtil.java:7", "DbEntity.getId": "DbEntity.java:10", "DbEntity.setId": "DbEntity.java:14", "AppUtils.<init>": "AppUtils.java:12", "HashConstants.<init>": "HashConstants.java:3", "JdkHashUtils.<init>": "JdkHashUtils.java:9", "LocalDataExporter.<init>": "LocalDataExporter.java:14", "LogUtils.<init>": "LogUtils.java:7", "UIUtils.<init>": "UIUtils.java:10", "WebUtils.<init>": "WebUtils.java:18", "SettingsFragment.lambda$initRate$7": "SettingsFragment.java:247-257", "BaseFragment.setAllowBackAction": "BaseFragment.java:53", "BaseFragment.getBackActionIconResId": "BaseFragment.java:58", "App.onTerminate": "App.java:176", "OrmLiteLocalDataStorage.releaseHelper": "OrmLiteLocalDataStorage.java:61", "OrmLiteLocalDataStorage.onUpgrade": "OrmLiteLocalDataStorage.java:56", "HistoryItem.equals": "HistoryItem.java:83", "HistoryItem.hashCode": "HistoryItem.java:99", "AppTextWatcher.onTextChanged": "AppTextWatcher.java:16" }
_UNREACHABLE_KIND['AppTextWatcher.onTextChanged'] = 'framework_never_calls'   # TextView would call it, but the only subclass overrides it
_UNREACHABLE_KIND['SharedPreferencesSettings.setRefreshSelectedFileStatus'] = 'closed_by_configuration'
_UNREACHABLE_KIND['SharedPreferencesSettings.getThemeAnalogue'] = 'closed_by_configuration'
_UNREACHABLE_REF['SharedPreferencesSettings.setRefreshSelectedFileStatus'] = 'HashCalculatorFragment.java:573-582'
_UNREACHABLE_REF['SharedPreferencesSettings.getThemeAnalogue'] = 'SharedPreferencesSettings.java:116-139'
DEAD['SharedPreferencesSettings.setRefreshSelectedFileStatus'] = ('SRC HashCalculatorFragment.java:573-582 (called only when refreshSelectedFile() is true) and SRC SharedPreferencesSettings.java:182-195 '
    '(the only writer, setRefreshSelectedFileStatus, is called with false only): no in-app action ever stores true, so the branch is open only when the preferences file is pre-seeded, '
    'which a fresh install of the standard configuration does not have')
DEAD['SharedPreferencesSettings.getThemeAnalogue'] = ('SRC SharedPreferencesSettings.java:116-139 (reached only when the stored selected_theme is neither LIGHT nor DARK) and SRC SharedPreferencesSettings.java:141-147 '
    '(the app only ever stores Theme.LIGHT or Theme.DARK): needs a preferences file from an old app version, which a fresh install of the standard configuration does not have')
SUPPRESS.add(('HashCalculatorFragment.checkFileManagerChanged', 'SharedPreferencesSettings.setRefreshSelectedFileStatus'))
SUPPRESS.add(('SharedPreferencesSettings.getTheme', 'SharedPreferencesSettings.getThemeAnalogue'))
# getLastHashType catches IllegalArgumentException only for a stored value that is not an enum name; the app stores HashType.toString() only (HashCalculatorFragment.java:432, SharedPreferencesSettings.java:30-35), so that catch needs a pre-seeded preference
SUPPRESS.add(('SharedPreferencesSettings.getLastHashType', 'LogUtils.e'))
# validateAppTheme calls saveTheme(DARK) only for a stored theme that is neither LIGHT nor DARK (old app versions): a pre-seeded preference again
SUPPRESS.add(('SharedPreferencesSettings.validateAppTheme', 'SharedPreferencesSettings.saveTheme'))
UNREACHABLE = {}
for _m, _t in list(DEAD.items()) + list(FRAMEWORK_ONLY.items()):
    UNREACHABLE[_m] = (_UNREACHABLE_KIND[_m], _t, _UNREACHABLE_REF[_m], 'SOURCE')
DEAD, FRAMEWORK_ONLY = {}, {}

ENV_KINDS_OF = { "outside package: another app (launcher shortcut, share/VIEW intent, adb) starts Hash Checker": [ "other_app" ], "an exception is thrown (I/O, SQL, missing handler app, bad URI); LogUtils.e only logs it in debug builds": [ "other" ], "no app on the device can handle the intent (no browser / Play Store / email app)": [ "other_app" ], "outside package: the system file picker (com.android.documentsui) must return a document": [ "other_app" ] }
STATE_KINDS_OF = { "The field is not empty (the icons are INVISIBLE while it is empty)": [ "session" ], "A hash was generated first (Export needs a non-empty generated field)": [ "session" ], "six successful hash generations in one install (rate dialog shows when the counter equals 5, once)": [ "data" ], "Both hash fields contain text (type in them or generate first)": [ "session" ], "A hash was generated first (the Export action needs a non-empty generated field)": [ "session" ], "Preference refresh_selected_file is true (no app code ever writes true; only a pre-seeded preferences file does)": [ "settings" ], "Preference selected_theme holds a legacy value (old app version); needs a pre-seeded preferences file": [ "settings" ], "Choose CRC-32 in the hash-type sheet first (tap the hash type -> pick it); the choice is stored in preference last_type_value": [ "settings" ], "Choose BLAKE2b in the hash-type sheet first (tap the hash type -> pick it); the choice is stored in preference last_type_value": [ "settings" ], "Choose FNV-1a (six sizes) in the hash-type sheet first (tap the hash type -> pick it); the choice is stored in preference last_type_value": [ "settings" ], "Choose SHA3-224/256/384/512 (Keccak provider) in the hash-type sheet first (tap the hash type -> pick it); the choice is stored in preference last_type_value": [ "settings" ], "Second Back within 300 ms of the first": [ "session" ], "At least one hash was generated with \"Save result to History\" on (default on)": [ "data" ] }

ENV_OTHER_APP = 'another app starts Hash Checker (launcher shortcut, share / VIEW intent, adb)'
ENV_TIME = 'time passes (the app waits for a timer)'
ENV_KINDS_OF[ENV_OTHER_APP] = ['other_app']
ENV_KINDS_OF[ENV_TIME] = ['time']


# Lines of calls found by the bytecode scan that the line table puts one line early (a `new X(...)` inside a chained call) or on the last line of a
# multi-line expression: the corrected line, found with tools/check_bytecode_lines.py.
FIX_LINES = {
    ('ActionsBottomSheet.getItemsAdapter', 'ActionsListAdapter.<init>', 'SRC ActionsBottomSheet.java:28 (bytecode)'): 'SRC ActionsBottomSheet.java:24-28 (bytecode line was 28)',
    ('ActionsBottomSheet.getItemsAdapter@ActionSelectActionsBottomSheet', 'ActionsListAdapter.<init>', 'SRC ActionsBottomSheet.java:28 (bytecode)'): 'SRC ActionsBottomSheet.java:24-28 (bytecode line was 28)',
    ('ActionsBottomSheet.getItemsAdapter@SourceSelectActionsBottomSheet', 'ActionsListAdapter.<init>', 'SRC ActionsBottomSheet.java:28 (bytecode)'): 'SRC ActionsBottomSheet.java:24-28 (bytecode line was 28)',
    ('App.onCreate', 'DatabaseHelperModule.<init>', 'SRC App.java:70 (bytecode)'): 'SRC App.java:71 (bytecode line was 70)',
    ('App.onCreate', 'LangHelperModule.<init>', 'SRC App.java:72 (bytecode)'): 'SRC App.java:73 (bytecode line was 72)',
    ('App.onCreate', 'SettingsHelperModule.<init>', 'SRC App.java:71 (bytecode)'): 'SRC App.java:72 (bytecode line was 71)',
    ('App.onCreate', 'SharedPreferencesSettings.<init>', 'SRC App.java:58 (bytecode)'): 'SRC App.java:57 (bytecode line was 58)',
    ('App.onCreate', 'ThemeConfigImpl.<init>', 'SRC App.java:73 (bytecode)'): 'SRC App.java:74 (bytecode line was 73)',
    ('App.onCreate', 'ThemeHelperModule.<init>', 'SRC App.java:73 (bytecode)'): 'SRC App.java:74 (bytecode line was 73)',
    ('GenerateToBottomSheet.getItemsAdapter', 'HashesListAdapter.<init>', 'SRC GenerateToBottomSheet.java:44 (bytecode)'): 'SRC GenerateToBottomSheet.java:40-44 (bytecode line was 44)',
    ('HistoryItemsAdapter.onCreateViewHolder', 'HistoryItemHolder.<init>', 'SRC HistoryItemsAdapter.java:33 (bytecode)'): 'SRC HistoryItemsAdapter.java:32 (bytecode line was 33)',
    ('LanguagesBottomSheet.getItemsAdapter', 'LanguagesListAdapter.<init>', 'SRC LanguagesBottomSheet.java:40 (bytecode)'): 'SRC LanguagesBottomSheet.java:37-40 (bytecode line was 40)',
    ('LanguagesListAdapter$LanguagesListHolder.callItemClick', 'AppAlertDialog.<init>', 'SRC LanguagesListAdapter.java:69 (bytecode)'): 'SRC LanguagesListAdapter.java:56-69 (bytecode line was 69)',
    ('ThemesBottomSheet.getItemsAdapter', 'ThemesListAdapter.<init>', 'SRC ThemesBottomSheet.java:38 (bytecode)'): 'SRC ThemesBottomSheet.java:37 (bytecode line was 38)',
    ('ThemesListAdapter$ThemesListHolder.showThemeApplyDialog', 'AppAlertDialog.<init>', 'SRC ThemesListAdapter.java:76 (bytecode)'): 'SRC ThemesListAdapter.java:63-76 (bytecode line was 76)',
}


# Guards of bytecode-derived edges inside the hash classes that the bytecode scan cannot see (found by reading routes).
STATE_BLOCK = 'The hashed input is longer than one 128-byte block (only then does update() compress a full buffer; getValue always compresses the last block)'
STATE_KINDS_OF[STATE_BLOCK] = ['data']
FNV_SIZE_STATE = 'Choose the FNV-1a %s-bit type in the hash-type sheet (FNV1a.update dispatches on the selected type)'
for _n in ('32', '64', '128', '256', '512', '1024'):
    STATE_KINDS_OF[FNV_SIZE_STATE % _n] = ['settings']


def EDIT(x):
    """STATE texts that are really another app or time, as structured ENV; corrected source lines of bytecode-derived edges; guards of the hash classes."""
    if x['dst'] == 'Blake2B.compress' and x['src'] in ('Blake2B.update(byte)', 'Blake2B.update(byte[],int,int)'):
        x['guard'] = 'a 128-byte block is already buffered and more input arrives'
        x['needs_state'] = STATE_BLOCK
        x['evidence'] = (x['evidence'] or '') + '; SRC Blake2B.java:91-107, 109-131 (compress only when the buffer is full)'
    _m = re.match(r'FNV1a\.update(\d+)\(', x['dst'])
    if _m and x['src'].startswith('FNV1a.update('):
        x['guard'] = 'this.type equals FNV_1A_%s' % _m.group(1)
        x['needs_state'] = FNV_SIZE_STATE % _m.group(1)
        x['evidence'] = (x['evidence'] or '') + '; SRC FNV1a.java:73-118 (the switch on this.type picks the size)'
    _GUARD = {('App.setLocale', 'LanguageConfigImpl.setLanguage(Language)'): 'preference key_language is not stored yet: first launch after install (if !settings.languageIsInitialized(), App.java:154)',
              ('App.onCreate', 'App.createShortcuts'): 'shortcuts not created yet: first launch after install (if !settings.isShortcutsIsCreated(), App.java:76)',
              ('App.onCreate', 'SharedPreferencesSettings.saveShortcutsStatus'): 'shortcuts not created yet: first launch after install (if !settings.isShortcutsIsCreated(), App.java:76)'}
    if (x['src'], x['dst']) in _GUARD and not x['guard']:
        x['guard'] = _GUARD[(x['src'], x['dst'])]
    if x['src'] == 'App.createShortcuts' and x['dst'].startswith('App.getShortcutFor') and not x['guard']:
        x['guard'] = 'SDK_INT >= 26 (true on API 27) and a ShortcutManager exists (App.java:84-86)'
    for (src, dst, old), new in FIX_LINES.items():
        if x['src'] == src and x['dst'] == dst and old in (x['evidence'] or ''):
            x['evidence'] = x['evidence'].replace(old, new)
    t = x['needs_state'] or ''
    if t.startswith(('Hash Checker is started by another app', 'Started from the launcher shortcut')):
        x['needs_state'], x['env'] = None, x['env'] or ENV_OTHER_APP
    elif t.startswith('Wait 60 seconds'):
        x['needs_state'], x['env'] = None, x['env'] or ENV_TIME


def CLASSIFY(x):
    """Edge classes that differ from the default of their kind (see SCHEMA_V2.md)."""
    dst = x['dst'].split('@')[0]
    if x['kind'] == 'CALL' and dst.split('.')[0] in ('ThemeHelperModule', 'LangHelperModule', 'SettingsHelperModule', 'DatabaseHelperModule') and not dst.endswith('.<init>'):
        return ('non_standard', 'Dagger dependency injection: the generated component calls the module method; nothing in the app calls it')
    if dst == 'HistoryItem.<init>()':
        return ('non_standard', 'ORMLite builds the row object by reflection')
    if x['kind'] == 'ENTRY' and dst.endswith('.<clinit>'):
        return ('standard', 'JVM class initialisation')
    if x['kind'] == 'LIFECYCLE' and dst.endswith('.onAttach'):
        return ('standard', 'show() hands the fragment to the FragmentManager, which attaches it; the Dagger injection is the call made inside onAttach, not this edge')
    if x['kind'] == 'SYSTEM' and x['src'] == 'S_EXIT' and x['dst'] == 'S_ENTRY':
        return ('page', 'page transition of the model: the next launch')
    if x['src'] == 'App.onCreate' and dst == 'DaggerAppComponent$Builder.<init>':
        return ('explicit', 'direct call from app code to the generated builder (App.java:70)')
    return None

STRICT = True
