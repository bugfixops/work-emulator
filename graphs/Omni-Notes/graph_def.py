# Omni-Notes 6.1.0 (#745, tingsu/Omni-Notes@instrumented-version-6.1.0, flavor play, debug build) trigger graph definition.
# Hand-written part: entry points, lifecycle, GUI handlers, framework callbacks (EventBus, AsyncTask, ButterKnife, adapters),
# context variants for the big switch methods, state and environment gates.
# Direct app->app calls come from tools/extract_calls.py (bytecode); USE_AUTO adds them for every pair not written here.
# Lambda numbers (lambda$name$N) were mapped to their source by javac's order (inner lambdas are numbered before the outer one).

TITLE = 'Omni-Notes 6.1.0 trigger graph'
USE_AUTO = True

ENV_EXT = 'outside package: another app or the system sends the broadcast / intent / content call'
ENV_PICKER = 'outside package: an external activity (camera, video recorder, document picker, ringtone picker, share chooser, browser, maps) must be driven'
ENV_LAUNCHER = 'outside package: the launcher home screen (widget, shortcut) or the notification shade must be operated'
ENV_BOOT = 'outside package: the device reboots (BOOT_COMPLETED)'
ENV_HOSTAPP = 'outside package: the DashClock or Pushbullet host app must be installed and call the extension'
ENV_LOCATION = 'the device delivers a location fix (GPS or network provider; a mock location on the emulator)'
ENV_GEO = 'the device delivers a location fix (GPS or network provider; a mock location on the emulator); the network is reachable (the Android Geocoder behind SmartLocation queries a network service)'
ENV_NOFIX = 'no location fix arrives within the 2 s timeout (location services off or no provider)'
ENV_MIC = 'the microphone records audio (audio hardware; a virtual microphone on the emulator)'
ENV_EXC = 'a runtime exception (I/O, illegal state, missing handler app) is thrown'

NEED_NOTE = 'At least one note exists (tap +, type, Back)'
NEED_ARCH_NAV = 'An archived note exists, so the Archive entry shows in the drawer (dynamic menu, default on)'
NEED_REM_NAV = 'A note with a reminder exists, so the Reminders entry shows in the drawer'
NEED_TRASH_NAV = 'A trashed note exists, so the Trash entry shows in the drawer'
NEED_UNCAT_NAV = 'Settings > Navigation > "Show uncategorized" is on (default off) and an uncategorized note exists'
NEED_CATEGORY = 'At least one category exists (create it from a note or the CAB: Category > Add category)'
NEED_TAGS = 'At least one #tag is written in some note'
NEED_PWD = 'A password was set (Settings > Data > Password)'
NEED_PWD_ACCESS = 'A password is set and Settings > Data > "Request password on access" is on (default off)'
NEED_LOCKED = 'A locked note exists (needs a password; Lock in the note menu, then Back to save)'
NEED_ATTACH = 'The open note has at least one attachment'
NEED_IMAGE = 'The open note has an image, sketch or video attachment'
NEED_AUDIO = 'The open note has an audio recording'
NEED_FILE = 'The open note has a file attachment'
NEED_SKETCH = 'The open note has a sketch attachment'
NEED_REMINDER = 'The open note has a reminder'
NEED_LOCATION = 'The open note has a location'
NEED_LINK = 'The note title or content contains a link, e-mail address or #hashtag'
NEED_CHECKED = 'The open checklist has at least one checked item'
NEED_BACKUP = 'A backup folder exists under /sdcard/Omni Notes (Settings > Sync > Export)'
NEED_PERM_STORAGE = 'The storage permission is granted'
NEED_PERM_LOCATION = 'ACCESS_FINE_LOCATION is granted'
NEED_PERM_AUDIO = 'RECORD_AUDIO is granted'
NEED_INSTANT = 'Settings > Behaviors > "Instant search" is on (default off)'
NEED_SWIPE = 'Settings > Behaviors > "Enable swipe" is on (default on) and the list is not Uncategorized'
NEED_SWIPE_TRASH = 'Settings > Behaviors > "Swipe to trash" is on (default off)'
NEED_FAB_LONG = 'Settings > Interface > "FAB expansion behaviour" is on (default off)'
NEED_AUTOLOC = 'Settings > Behaviors > "Auto location" is on (default off)'
NEED_REMINDER_FIRED = 'A reminder was set a minute ahead and its alarm fired (the notification is in the shade)'
NEED_SPRINGPAD = 'A Springpad export zip is available to pick'
NEED_EXISTING = 'The open note already exists (it was opened from the list or saved before; a note created in this editor has no id yet)'
NEED_RESTART = 'The process was restarted after data was written (second start)'

NAVS = ('NOTES', 'ARCHIVE', 'REMINDERS', 'TRASH', 'UNCAT', 'CATEGORY')
NAV_NAME = {'NOTES': 'Notes', 'ARCHIVE': 'Archive', 'REMINDERS': 'Reminders', 'TRASH': 'Trash', 'UNCAT': 'Uncategorized', 'CATEGORY': 'a category'}
NAV_NEED = {'NOTES': None, 'ARCHIVE': NEED_ARCH_NAV, 'REMINDERS': NEED_REM_NAV, 'TRASH': NEED_TRASH_NAV, 'UNCAT': NEED_UNCAT_NAV, 'CATEGORY': NEED_CATEGORY}

FW_EB = 'INFERRED greenrobot EventBus 2.4: post() calls the subscribers registered for the event class (onEvent: posting thread, onEventMainThread: main, onEventAsync: pool) (EventBus source not read)'
FW_ASYNC = ('FW-SRC core/java/android/os/AsyncTask.java:219-224, 237-262, 594-596, 632-650, 326-334, 369-374, 285, 705-713, 691-697 (execute uses the serial executor, which hands each task to '
            'THREAD_POOL_EXECUTOR and the worker calls doInBackground; postResult sends the result to a main-looper handler whose handleMessage calls finish, which calls onPostExecute)')
FW_POST = ('FW-SRC core/java/android/os/Handler.java:97-107, 355-358, 427-430, 789-791 (post and postDelayed queue the Runnable as the callback of a message; dispatchMessage runs it through handleCallback on the handler looper thread); '
           'INFERRED that looper is the main looper because the handler is created on the main thread (Handler constructor not read)')
FW_VIEW = ('FW-SRC core/java/android/view/View.java:6289-6296, 6370-6376, 11768-11774, 23109-23128 and core/java/android/widget/AdapterView.java:314-321 (performClick, performLongClick and the touch and drag dispatch call the listener '
           'registered with setOnClickListener / setOnLongClickListener / setOnTouchListener / setOnDragListener; performItemClick calls the OnItemClickListener); '
           'INFERRED the other callbacks the edge names (adapter getView, scroll and animation listeners, RecyclerView) are called by the ListView / RecyclerView / animation machinery (source not read)')
FW_BIND = 'INFERRED ButterKnife.bind(...) reflectively calls the generated X_ViewBinding(target, source) constructor (ButterKnife source not read)'
FW_FRAG = 'INFERRED androidx.fragment.app.FragmentManager drives the fragment lifecycle callbacks (androidx source not read)'
RES_CANCEL = 'FW-SRC core/java/android/app/Activity.java:824, 5489-5497 (an activity that finishes without setResult reports mResultCode, which is RESULT_CANCELED by default) and core/java/android/app/ActivityThread.java:4253-4265 (a result is delivered to the starting activity through dispatchActivityResult, which ends in onActivityResult); INFERRED the other app (camera, picker) finishes without a result on Back, and the androidx fragment hands the result to the fragment (other app and androidx source not read)'
BACK_DLG = 'FW-SRC core/java/android/app/Dialog.java:352-358, 650-654, 1231-1237 (Back calls cancel() while the dialog is cancelable; cancel() sends the cancel message if one is set, then dismiss() closes the dialog); INFERRED the MaterialDialog library builds an android.app.Dialog subclass and keeps the cancelable default (library source not read)'
BACK_ACT = 'FW-SRC core/java/android/app/Activity.java:3001-3010 (the platform onBackPressed pops the fragment back stack or finishes the activity); INFERRED the androidx FragmentActivity / AppCompatActivity does the same unless the activity overrides onBackPressed (androidx source not read)'
BACK_EXT = 'INFERRED the other app (camera or picker) finishes when Back is pressed and the result reaches the caller as RESULT_CANCELED (another app, source not read)'
FW_MD = 'INFERRED MaterialDialogs calls the registered button / item callbacks (library source not read)'

# ------------------------------------------------------------------ pages
SCREENS = {
    'S_ENTRY': 'Outside the app: launcher, share sheet, widget, shortcut, notification, boot, other apps or adb',
    'S_EXIT': 'The process ended (Back from the list, System.exit after reset / language change / restore)',
    'S_MAIN_PAUSED': 'MainActivity is stopped: Home key, another app or a system screen on top',
    'S_LIST': 'ListFragment in MainActivity; variants NOTES, ARCHIVE, REMINDERS, TRASH, UNCAT, CATEGORY (the navigation); list, FAB, search icon, sort/view menu',
    'S_LIST_FAB': 'FAB menu expanded: note, camera, checklist buttons and an overlay',
    'S_LIST_SEARCH_EDIT': 'SearchView expanded with focus: keyboard, uncompleted-checklist and tags icons',
    'S_LIST_SEARCH_RESULT': 'List showing search results with the search label bar and its cancel (X)',
    'S_LIST_CAB': 'Multi-select action mode (CAB); variants by navigation class and count: NOTES1, NOTESN, ARCH1, ARCHN, CATEG1, CATEGN, TRASH',
    'S_LIST_UNDO': 'List with the undo bar after archive, trash or remove category; any touch commits',
    'S_SORT_MENU': 'Sort sub-menu: title, creation, last modification, reminder',
    'S_DRAWER': 'Navigation drawer open (variant = the list navigation underneath): nav entries, categories, Settings footer',
    'S_DLG_EMPTY_TRASH': 'Confirm "Empty trash"',
    'S_DLG_DELETE_NOTES': 'Confirm permanent delete of the selected notes (CAB in Trash)',
    'S_DLG_CATEGORIZE_LIST': 'Dialog "Categorize as": category list, Add category, Remove category (CAB)',
    'S_DLG_TAG_NOTES': 'Multi-choice tags dialog for the selected notes (CAB)',
    'S_DLG_FILTER_TAGS': 'Multi-choice tags dialog that filters the list (search bar)',
    'S_CATEGORY': 'CategoryActivity (dialog theme); variants NEW_LIST, NEW_DETAIL, EDIT (EDIT shows Delete)',
    'S_DLG_COLOR_CHOOSER': 'ColorChooserDialog over CategoryActivity',
    'S_DLG_DELETE_CATEGORY': 'Confirm category deletion',
    'S_DLG_PASSWORD': 'Password request dialog; variants per caller (APP_ACCESS, OPEN_NOTE, SWIPE, CAB, EMPTY_TRASH_DIALOG, DELETE_NOTES, DETAIL_OPEN, DETAIL_LOCK, PWD_REMOVE, PWD_CONFIRM, SETTINGS_ACCESS)',
    'S_DLG_PASSWORD_RESET': 'Security-question dialog that removes the password',
    'S_DETAIL': 'DetailFragment (note editor); variants NEW, EDIT, CHECKLIST, ARCHIVED, TRASHED',
    'S_DLG_ATTACH': 'Attachment popup: camera, recording, video, files, sketch, location, timestamp, pushbullet',
    'S_DLG_CATEGORIZE_DETAIL': 'Dialog "Categorize as" from the editor',
    'S_DLG_TAGS_DETAIL': 'Multi-choice tags dialog from the editor',
    'S_DLG_DISCARD': 'Confirm "Discard changes"',
    'S_DLG_DELETE_NOTE': 'Confirm permanent delete of the open trashed note',
    'S_DLG_REMOVE_CHECKLIST': 'Keep-checked / keep-checkmarks options when leaving checklist mode',
    'S_DLG_ATTACHMENT_ACTIONS': 'Long-press on an attachment: share, delete, delete all, (edit for sketches)',
    'S_DLG_DELETE_ALL_ATTACHMENTS': 'Confirm "Delete all attachments"',
    'S_DLG_REMOVE_REMINDER': 'Confirm removal of the note reminder',
    'S_DLG_REMOVE_LOCATION': 'Confirm removal of the note location',
    'S_DLG_LOCATION': 'Location search dialog (autocomplete, use current location)',
    'S_DLG_LINK': 'Dialog for a link / e-mail / hashtag tapped in the text: Open, Copy',
    'S_REMINDER_PICKER': 'SublimePicker dialog (date, time, recurrence); variants DETAIL, SNOOZE',
    'S_SKETCH': 'SketchFragment: canvas, stroke, eraser, undo, redo, erase',
    'S_SKETCH_POPUP': 'Stroke or eraser PopupWindow (variants STROKE, ERASER)',
    'S_DLG_ERASE_SKETCH': 'Confirm "Erase sketch"',
    'S_GALLERY': 'GalleryActivity: pager of image, sketch and video attachments',
    'S_NOTE_INFO': 'NoteInfosActivity (dialog): statistics of the open note',
    'S_EXT_CAMERA': 'External camera or video recorder (another package)',
    'S_EXT_PICKER': 'External document picker or ringtone picker (another package)',
    'S_EXT_APP': 'Another app or system screen without a result (share chooser, browser, maps, viewer)',
    'S_SETTINGS': 'SettingsActivity root: sub-screens, beta, manual, tour, changelog, statistics, about',
    'S_SETTINGS_DATA': 'Settings > Data: sync, password, password access, reset all data',
    'S_SETTINGS_SYNC': 'Settings > Data > Sync: export, import, legacy import, integrity check, auto backup, Springpad',
    'S_SETTINGS_INTERFACE': 'Settings > Interface: language, colours, FAB behaviour, attachments on bottom, pretty dates',
    'S_SETTINGS_NAVIGATION': 'Settings > Navigation: dynamic menu, category count, show uncategorized, drawer on exit',
    'S_SETTINGS_BEHAVIORS': 'Settings > Behaviors: checked items, instant search, swipe, swipe to trash, auto location, max video size',
    'S_SETTINGS_NOTIFICATIONS': 'Settings > Notifications: vibration, ringtone, snooze delay',
    'S_SETTINGS_PRIVACY': 'Settings > Privacy: crash reports, analytics, file logging',
    'S_DLG_EXPORT': 'Dialog "Export": backup name',
    'S_DLG_IMPORT': 'Dialog "Import": list of backups (tap restores, long-press deletes)',
    'S_DLG_IMPORT_CONFIRM': 'Confirm restoring a backup',
    'S_DLG_BACKUP_DELETE': 'Confirm deleting a backup',
    'S_DLG_FOLDER_CHOOSER': 'FolderChooserDialog (legacy import)',
    'S_DLG_LEGACY_IMPORT_CONFIRM': 'Confirm legacy import of the chosen folder',
    'S_DLG_RESET_DATA': 'Confirm "Reset all data"',
    'S_DLG_CHANGELOG': 'Changelog dialog',
    'S_DLG_TOUR_AGAIN': 'Confirm "Show tour again"',
    'S_PASSWORD': 'PasswordActivity (dialog theme); variants UNSET_SETTINGS, UNSET_DETAIL (opened by the editor Lock item), SET_SETTINGS',
    'S_DLG_REMOVE_PASSWORD': 'Confirm "unlock all notes" (remove password)',
    'S_STATS': 'StatsActivity (dialog theme; loads the statistics asynchronously)',
    'S_ABOUT': 'AboutActivity (WebView of about.html)',
    'S_NOTIF_REMINDER': 'Notification shade with a reminder notification (tap, Snooze, Add reminder)',
    'S_NOTIF_BACKUP': 'Notification shade with the backup / import notification',
    'S_HOME_WIDGET': 'Launcher home screen with an Omni Notes widget (variants SIMPLE, LIST) or the Add note shortcut',
    'S_WIDGET_CONFIG': 'WidgetConfigurationActivity: all notes or one category, thumbnails, timestamps',
}


def gui(src, dst, text, kind='GUI', **kw):
    e(src, dst, kind, text, gui=[text], **kw)


def sup(*pairs):
    for p in pairs:
        SUPPRESS.add(p)


# ================================================================== A. process start, MainActivity, lifecycle
e('S_ENTRY', 'OmniNotes.<init>', 'ENTRY', 'The process starts', gui=['Home screen of another launcher: tap the Omni Notes icon'], evidence='SRC AndroidManifest.xml:47-55')
e('OmniNotes.<init>', 'OmniNotes.attachBaseContext', 'LIFECYCLE', 'The system calls attachBaseContext (ACRA init)', evidence='SRC OmniNotes.java:73-77')
e('OmniNotes.<init>', 'OmniNotes.onCreate', 'LIFECYCLE', 'The system calls Application.onCreate', evidence='SRC OmniNotes.java:80-93')
e('S_ENTRY', 'MainActivity.<init>', 'ENTRY', 'MAIN / LAUNCHER intent starts MainActivity', gui=['Home screen of another launcher: tap the Omni Notes icon'], evidence='SRC AndroidManifest.xml:65-114')
for cb in ('BaseActivity.attachBaseContext', 'MainActivity.onCreate', 'MainActivity.onResume'):
    e('MainActivity.<init>', cb, 'LIFECYCLE', 'Activity lifecycle callback', evidence='SRC MainActivity.java:93-120; BaseActivity.java:72-100')
e('MainActivity.onCreate', 'MainActivity_ViewBinding.<init>(MainActivity,View)', 'FRAMEWORK', 'ButterKnife.bind(this)', evidence=FW_BIND + '; SRC MainActivity.java:97')
e('MainActivity.onCreate', 'NavigationDrawerFragment.<init>', 'FRAMEWORK', 'setContentView inflates the static <fragment> of activity_main.xml', evidence='SRC res/layout/activity_main.xml:54-61; ' + FW_FRAG)
for cb in ('onCreate', 'onCreateView', 'onActivityCreated', 'onStart'):
    e('NavigationDrawerFragment.<init>', 'NavigationDrawerFragment.' + cb, 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC NavigationDrawerFragment.java:62-93')
# ListFragment lifecycle: siblings of <init> (never chain through a shared node)
for cb in ('onCreate', 'onCreateView', 'onActivityCreated', 'onResume', 'onCreateOptionsMenu', 'onPrepareOptionsMenu'):
    e('ListFragment.<init>', 'ListFragment.' + cb, 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC ListFragment.java:205-400')
e('ListFragment.<init>', 'BaseFragment.onStart', 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC BaseFragment.java:32-35')
e('ListFragment.<init>', 'ListFragment_ViewBinding.<init>', 'FRAMEWORK', 'ButterKnife.bind(this, view)', evidence=FW_BIND + '; SRC ListFragment.java:233')
e('ListFragment.onActivityCreated', 'ListFragment.init', 'CALL', 'init()', evidence='SRC ListFragment.java:246')
e('ListFragment.init', 'S_LIST@NOTES', 'ENTERS', 'The list is set up on the default navigation (Notes) and the load starts', guard='navigation pref is Notes (default)', evidence='SRC ListFragment.java:250-261; BaseActivity.java:98-99')
# the default navigation is persistent: a later start opens at the last navigation (not modelled; least-state page)
e('MainActivity.onResume', 'MainActivity.checkPassword', 'CALL', 'isPasswordAccepted is false on a cold start', evidence='SRC MainActivity.java:111-118')
e('MainActivity.checkPassword', 'MainActivity.init', 'CALL', 'no password gate: init()', evidence='SRC MainActivity.java:138-156')
e('MainActivity.init', 'ListFragment.<init>', 'CALL', 'adds the list fragment', guard='no fragment with tag fragment_list', evidence='SRC MainActivity.java:178-182')
e('MainActivity.init', 'MainActivity.handleIntents', 'CALL', 'handleIntents()', evidence='SRC MainActivity.java:183')
# static fields and class initialisers
e('MainActivity.<init>', 'MainActivity.<clinit>', 'LIFECYCLE', 'class initialisation', evidence='SRC MainActivity.java:75-82 (static field initialisers); INFERRED the class has a static initialiser that the JVM runs on first use of the class (Java language rule, not read from a source)')
# ---- intro tour: unreachable in the debug build
# mustRun() is `!isDebugBuild() && ...getAppContext()...` (IntroActivity.java:49): in the debug build the && stops at the first operand, so getAppContext is never called from here
sup(('IntroActivity.mustRun', 'OmniNotes.getAppContext'))
# ---- pause / stop / resume, rotation
e('S_LIST@NOTES', 'MainActivity.onPause', 'SYSTEM', 'Press Home or open another app', gui=['Press Home'], evidence='SRC MainActivity.java:308-311')
e('MainActivity.onPause', 'MainActivity.onStop', 'SYSTEM', 'the activity is no longer visible', evidence='SRC MainActivity.java:122-125')
e('MainActivity.onStop', 'S_MAIN_PAUSED', 'ENTERS', 'MainActivity is stopped (EventBus registration of MainActivity is gone)', evidence='SRC MainActivity.java:122-125')
e('S_MAIN_PAUSED', 'MainActivity.onResume', 'SYSTEM', 'Return to the app', gui=['Return to the app from the recent apps list'], evidence='SRC MainActivity.java:111-118')
e('MainActivity.onResume', 'S_LIST@NOTES', 'ENTERS', 'the activity is back', guard='isPasswordAccepted is true', needs_state='MainActivity was resumed before in this process (the static isPasswordAccepted is already true)', evidence='SRC MainActivity.java:77,111-118,166')
e('S_LIST@NOTES', 'MainActivity.onSaveInstanceState', 'SYSTEM', 'Rotate the device or press Home (the state is saved)', gui=['Rotate the device'], evidence='SRC MainActivity.java:301-304')
e('S_LIST@NOTES', 'OmniNotes.onConfigurationChanged', 'SYSTEM', 'A configuration change (rotation, locale) reaches the Application', gui=['Rotate the device'], evidence='SRC OmniNotes.java:113-117')
for cb in ('onPause', 'onSaveInstanceState'):
    e('S_LIST@NOTES', 'ListFragment.' + cb, 'SYSTEM', 'Press Home or rotate the device', gui=['Press Home'], evidence=FW_FRAG + '; SRC ListFragment.java:352-375')
e('S_LIST@NOTES', 'ListFragment.onDestroy', 'SYSTEM', 'The activity is destroyed (rotation or back out)', gui=['Rotate the device'], evidence=FW_FRAG + '; SRC ListFragment.java:215-218')
e('S_LIST@NOTES', 'BaseActivity.onKeyDown', 'GUI', 'Press the hardware Menu key (swallowed)', gui=['Press the hardware Menu key'], evidence='SRC BaseActivity.java:209-211')
e('S_LIST@NOTES', 'BaseActivity.onCreateOptionsMenu', 'FRAMEWORK', 'the toolbar menu is inflated (menu_list)', evidence=FW_VIEW + '; SRC BaseActivity.java:65-69')
# preference changes while the app runs
e('S_LIST@NOTES', 'MainActivity.onSharedPreferenceChanged', 'FRAMEWORK', 'a preference value changes (settings, navigation)', needs_state='A preference value was changed (Settings, drawer navigation)', evidence=FW_VIEW + '; SRC MainActivity.java:538-541')
e('MainActivity.onSharedPreferenceChanged', 'ListFragment.init', 'CALL', 'prefsChanged makes ListFragment.onResume re-run init()', needs_state='A preference value was changed (Settings, drawer navigation)', evidence='SRC ListFragment.java:392-395')


# ================================================================== helpers for splitting big switch methods into context variants
def clone_auto(src, variant, exclude=(), only=None, need=None, env=None, guard=None):
    """Copy the bytecode call edges of `src` onto `variant` (a context node of the same method), minus `exclude`."""
    seen = set()
    for c in AUTO['calls']:
        if c['src'] != src or c['dst'] in exclude or c['dst'] in seen:
            continue
        if only is not None and c['dst'] not in only:
            continue
        seen.add(c['dst'])
        e(variant, c['dst'], 'CALL', 'call made by %s' % src.split('.', 1)[1], needs_state=need, env=env, guard=guard,
          evidence='SRC %s:%d (bytecode)' % (c['file'], c['line']))


# ================================================================== A1. loader chain (AsyncTask + EventBus), drawer menus
LOADERS = {   # variant -> (DbHelper method called by reflection, state needed to reach it from initNotesList)
    'ALL': ('DbHelper.getAllNotes@NAV', None),
    'PATTERN': ('DbHelper.getNotesByPattern', 'A search was submitted (search bar) or instant search is on'),
    'TAG': ('DbHelper.getNotesByTag(String)', 'A hashtag link (hashtag://tag) was opened or tags were picked in the search tag filter'),
    'CHECK': ('DbHelper.getNotesByUncompleteChecklist', 'The "uncompleted checklists" icon of the search bar was used'),
    'CATEGORY': ('DbHelper.getNotesByCategory', 'The list was opened from a widget bound to a category (navigationTmp)'),
}
for q, (dbm, need) in LOADERS.items():
    env = ENV_LAUNCHER if q == 'CATEGORY' else None
    e('ListFragment.initNotesList', 'NoteLoaderTask.doInBackground@' + q, 'ASYNC', 'NoteLoaderTask.getInstance().executeOnExecutor(...) with the %s query' % q.lower(),
      needs_state=need, env=env, evidence=FW_ASYNC + '; SRC ListFragment.java:1051-1121')
    e('NoteLoaderTask.doInBackground@' + q, dbm, 'CALL', 'db.getClass().getDeclaredMethod(name).invoke(db): reflection', evidence='SRC async/notes/NoteLoaderTask.java:56-80; INFERRED java.lang.reflect.Method.invoke calls the method (libcore source not read)')
    e('NoteLoaderTask.doInBackground@' + q, 'NoteLoaderTask.onPostExecute', 'ASYNC', 'the list of notes is delivered on the main thread', evidence=FW_ASYNC + '; SRC async/notes/NoteLoaderTask.java:84-88')
e('ListFragment.initNotesList', 'NoteLoaderTask.<init>', 'CALL', 'the singleton task is created (private constructor)', evidence='SRC async/notes/NoteLoaderTask.java:37-51 (private constructor, singleton); INFERRED the class has a static initialiser that the JVM runs on first use of the class (Java language rule, not read from a source)')
e('ListFragment$2$1.onQueryTextChange', 'NoteLoaderTask.doInBackground@PATTERN', 'ASYNC', 'instant search loads the notes matching the typed text', needs_state=NEED_INSTANT, evidence=FW_ASYNC + '; SRC ListFragment.java:719-731')
e('NoteLoaderTask.onPostExecute', 'ListFragment.onEvent(NotesLoadedEvent)', 'FRAMEWORK', 'NotesLoadedEvent reaches the list fragment', evidence=FW_EB + '; SRC async/notes/NoteLoaderTask.java:87')
e('NoteLoaderTask.onPostExecute', 'NavigationDrawerFragment.onEvent(NotesLoadedEvent)', 'FRAMEWORK', 'NotesLoadedEvent reaches the drawer fragment (registered onStart..onStop)', evidence=FW_EB + '; SRC NavigationDrawerFragment.java:120-131')
sup(('ListFragment.initNotesList', 'NoteLoaderTask.doInBackground'))
# drawer menus are rebuilt on each load
e('NavigationDrawerFragment.buildMainMenu', 'MainMenuTask.doInBackground', 'ASYNC', 'task.executeOnExecutor(...)', evidence=FW_ASYNC + '; SRC NavigationDrawerFragment.java:217-220')
e('MainMenuTask.doInBackground', 'MainMenuTask.onPostExecute', 'ASYNC', 'the menu items are delivered on the main thread', evidence=FW_ASYNC + '; SRC async/MainMenuTask.java:63-86')
e('NavigationDrawerFragment.buildCategoriesMenu', 'CategoryMenuTask.onPreExecute', 'FRAMEWORK', 'AsyncTask.execute: onPreExecute on the main thread', evidence=FW_ASYNC + '; SRC NavigationDrawerFragment.java:211-214')
e('NavigationDrawerFragment.buildCategoriesMenu', 'CategoryMenuTask.doInBackground', 'ASYNC', 'task.executeOnExecutor(...)', evidence=FW_ASYNC + '; SRC NavigationDrawerFragment.java:211-214')
e('CategoryMenuTask.doInBackground', 'CategoryMenuTask.onPostExecute', 'ASYNC', 'the categories are delivered on the main thread', evidence=FW_ASYNC + '; SRC async/CategoryMenuTask.java:77-102')
e('CategoryMenuTask.buildCategoryMenu', 'CategoryMenuTask.lambda$buildCategoryMenu$1', 'ASYNC', 'mainActivity.runOnUiThread(...) wires the click listeners', evidence=FW_POST + '; SRC async/CategoryMenuTask.java:129-139')
e('MainMenuTask.<init>', 'MainMenuTask_ViewBinding.<init>', 'FRAMEWORK', 'ButterKnife.bind(this, view)', evidence=FW_BIND + '; SRC async/MainMenuTask.java:59')
e('MainMenuTask.onPostExecute', 'NavDrawerAdapter.getCount', 'FRAMEWORK', 'setAdapter: the ListView reads the rows', evidence=FW_VIEW + '; SRC async/MainMenuTask.java:72')
for cb in ('getView', 'getItemId'):
    e('MainMenuTask.onPostExecute', 'NavDrawerAdapter.' + cb, 'FRAMEWORK', 'the ListView binds the navigation rows', evidence=FW_VIEW + '; SRC async/MainMenuTask.java:72')
e('CategoryMenuTask.onPostExecute', 'CategoryBaseAdapter.getCount', 'FRAMEWORK', 'setAdapter: the category list reads the rows', evidence=FW_VIEW + '; SRC async/CategoryMenuTask.java:91')
for cb in ('getView', 'getItemId'):
    e('CategoryMenuTask.onPostExecute', 'CategoryBaseAdapter.' + cb, 'FRAMEWORK', 'the category list binds the rows', needs_state=NEED_CATEGORY, evidence=FW_VIEW + '; SRC async/CategoryMenuTask.java:91')
e('NavigationDrawerFragment.onEvent(NotesLoadedEvent)', 'NavigationDrawerFragment.refreshMenus', 'CALL', 'the drawer menus are rebuilt after a load', evidence='SRC NavigationDrawerFragment.java:120-131')
# EventBus events between components
e('CategoryActivity.lambda$deleteCategory$0', 'NavigationDrawerFragment.onEvent(CategoriesUpdatedEvent)', 'FRAMEWORK', 'CategoriesUpdatedEvent', evidence=FW_EB + '; SRC CategoryActivity.java:182')
e('CategoryActivity.lambda$deleteCategory$0', 'ListFragment.onEvent(CategoriesUpdatedEvent)', 'FRAMEWORK', 'CategoriesUpdatedEvent', evidence=FW_EB + '; SRC CategoryActivity.java:182')
e('ListFragment.onEvent(CategoriesUpdatedEvent)', 'ListFragment.initNotesList', 'CALL', 'reload', evidence='SRC ListFragment.java:1163-1165')
e('DynamicNavigationLookupTable.update', 'NavigationDrawerFragment.onEventMainThread', 'FRAMEWORK', 'DynamicNavigationReadyEvent', evidence=FW_EB + '; SRC models/misc/DynamicNavigationLookupTable.java:69')
for poster in ('NoteProcessor.afterProcess', 'DetailFragment.onNoteSaved'):
    for h in ('NavigationDrawerFragment.onEventAsync', 'DynamicNavigationLookupTable.onEventAsync'):
        e(poster, h, 'FRAMEWORK', 'NotesUpdatedEvent', evidence=FW_EB + '; SRC async/notes/NoteProcessor.java:61-67; DetailFragment.java:1615')
e('DynamicNavigationLookupTable.onEventAsync', 'DynamicNavigationLookupTable.update', 'CALL', 'rebuild the counts', evidence='SRC models/misc/DynamicNavigationLookupTable.java:75-77')
e('MainActivity.updateWidgets', 'UpdateWidgetsTask.doInBackground', 'ASYNC', 'new UpdateWidgetsTask(...).executeOnExecutor(...)', evidence=FW_ASYNC + '; SRC MainActivity.java:521-524')
e('UpdateWidgetsTask.doInBackground', 'UpdateWidgetsTask$WidgetUpdateSubscriber.<init>', 'CALL', 'the subscriber registers on the bus', evidence='SRC async/UpdateWidgetsTask.java:36')
e('NoteProcessor.afterProcess', 'UpdateWidgetsTask$WidgetUpdateSubscriber.onEvent', 'FRAMEWORK', 'NotesUpdatedEvent (only while an UpdateWidgetsTask subscriber is registered)', needs_state='A list change was committed (trash/archive/categorize) so updateWidgets() registered the subscriber', evidence=FW_EB + '; SRC async/UpdateWidgetsTask.java:40-50')
e('DetailFragment.onNoteSaved', 'UpdateWidgetsTask$WidgetUpdateSubscriber.onEvent', 'FRAMEWORK', 'NotesUpdatedEvent (only while an UpdateWidgetsTask subscriber is registered)', needs_state='A list change was committed (trash/archive/categorize) so updateWidgets() registered the subscriber', evidence=FW_EB + '; SRC async/UpdateWidgetsTask.java:40-50')
e('ListFragment.onEvent(NavigationUpdatedNavDrawerClosedEvent)', 'ListFragment.initNotesList', 'CALL', 'reload for the new navigation', evidence='SRC ListFragment.java:1155-1160')
# ---- drawer: open / close / entries
for n in NAVS:
    p = 'S_LIST@' + n
    gui(p, 'NavigationDrawerFragment$1.onDrawerOpened@' + n, 'Swipe in from the left edge or tap the menu icon', evidence='SRC NavigationDrawerFragment.java:172-188')
    e('NavigationDrawerFragment$1.onDrawerOpened@' + n, 'S_DRAWER@' + n, 'ENTERS', 'the drawer is open', evidence='SRC NavigationDrawerFragment.java:183-186')
    for dst in ('MainActivity.commitPending', 'MainActivity.finishActionMode'):
        e('NavigationDrawerFragment$1.onDrawerOpened@' + n, dst, 'CALL', 'opening the drawer commits pending undo and closes the action mode', evidence='SRC NavigationDrawerFragment.java:184-185')
    gui('S_DRAWER@' + n, 'MainActivity.onBackPressed@DRAWER_' + n, 'Press Back (or swipe the drawer closed)', evidence='SRC MainActivity.java:279-294')
    e('MainActivity.onBackPressed@DRAWER_' + n, 'MainActivity.getDrawerLayout', 'CALL', 'closeDrawer(START)', guard='navdrawer_on_exit is off (default)', evidence='SRC MainActivity.java:285-287')
    e('MainActivity.onBackPressed@DRAWER_' + n, 'NavigationDrawerFragment$1.onDrawerClosed@' + n, 'FRAMEWORK', 'the toggle reports the closed drawer', evidence=FW_VIEW + '; SRC NavigationDrawerFragment.java:178-181')
    e('NavigationDrawerFragment$1.onDrawerClosed@' + n, 'S_LIST@' + n, 'ENTERS', 'the list is shown again', evidence='SRC NavigationDrawerFragment.java:178-181')
    # nav entries
    for y in NAVS:
        if y == 'CATEGORY' or y == n:
            continue
        gui('S_DRAWER@' + n, 'MainMenuTask.lambda$onPostExecute$0@' + y, 'Tap "%s" in the drawer' % NAV_NAME[y], needs_state=NAV_NEED[y], evidence='SRC async/MainMenuTask.java:73-84')
    gui('S_DRAWER@' + n, 'CategoryMenuTask.lambda$buildCategoryMenuClickEvent$3', 'Tap a category in the drawer', needs_state=NEED_CATEGORY, evidence='SRC async/CategoryMenuTask.java:159-173')
    gui('S_DRAWER@' + n, 'CategoryMenuTask.lambda$buildCategoryMenuLongClickEvent$2', 'Long-press a category in the drawer', needs_state=NEED_CATEGORY, evidence='SRC async/CategoryMenuTask.java:144-157')
    gui('S_DRAWER@' + n, 'CategoryMenuTask.lambda$null$0', 'Tap Settings at the bottom of the drawer', evidence='SRC async/CategoryMenuTask.java:129-135; res/layout/fragment_navigation_drawer.xml:66-80')
for y in NAVS:
    if y == 'CATEGORY':
        continue
    v = 'MainMenuTask.lambda$onPostExecute$0@' + y
    e(v, 'S_LIST@' + y, 'ENTERS', 'updateNavigation(%s): the drawer closes and the list reloads for %s' % (y, NAV_NAME[y]), evidence='SRC async/MainMenuTask.java:73-84; NavigationDrawerFragment.java:143-156')
    for dst in ('BaseActivity.updateNavigation', 'NavigationItem.getArrayIndex', 'NavigationUpdatedEvent.<init>'):
        e(v, dst, 'CALL', 'call in the click handler', evidence='SRC async/MainMenuTask.java:73-84')
    e(v, 'NavigationDrawerFragment.onEvent(NavigationUpdatedEvent)', 'FRAMEWORK', 'NavigationUpdatedEvent', evidence=FW_EB + '; SRC async/MainMenuTask.java:82')
    e(v, 'NavDrawerAdapter.getItem', 'FRAMEWORK', 'mDrawerList.getItemAtPosition(position)', evidence=FW_VIEW + '; SRC async/MainMenuTask.java:82')
c3 = 'CategoryMenuTask.lambda$buildCategoryMenuClickEvent$3'
e(c3, 'S_LIST@CATEGORY', 'ENTERS', 'updateNavigation(categoryId): the list reloads for that category', evidence='SRC async/CategoryMenuTask.java:159-173')
e(c3, 'NavigationDrawerFragment.onEvent(NavigationUpdatedEvent)', 'FRAMEWORK', 'NavigationUpdatedEvent', evidence=FW_EB + '; SRC async/CategoryMenuTask.java:168')
e(c3, 'CategoryBaseAdapter.getItem', 'FRAMEWORK', 'getAdapter().getItem(position)', evidence=FW_VIEW + '; SRC async/CategoryMenuTask.java:162')
e('NavigationDrawerFragment.onEvent(NavigationUpdatedEvent)', 'NavigationDrawerFragment.lambda$onEvent$0', 'ASYNC', 'new Handler().postDelayed(post NavigationUpdatedNavDrawerClosedEvent, 400)', evidence=FW_POST + '; SRC NavigationDrawerFragment.java:153-154')
e('NavigationDrawerFragment.lambda$onEvent$0', 'ListFragment.onEvent(NavigationUpdatedNavDrawerClosedEvent)', 'FRAMEWORK', 'NavigationUpdatedNavDrawerClosedEvent', evidence=FW_EB + '; SRC NavigationDrawerFragment.java:153')
l2 = 'CategoryMenuTask.lambda$buildCategoryMenuLongClickEvent$2'
e(l2, 'MainActivity.editTag', 'CALL', 'editTag((Category) item)', evidence='SRC async/CategoryMenuTask.java:149-151')
e('MainActivity.editTag', 'ListFragment.editCategory', 'CALL', 'editCategory(tag)', evidence='SRC MainActivity.java:215-220')
e('ListFragment.editCategory', 'S_CATEGORY@EDIT', 'ENTERS', 'startActivityForResult(CategoryActivity) with the category', evidence='SRC ListFragment.java:1463-1467')
e('CategoryMenuTask.lambda$null$0', 'SettingsActivity.<init>', 'INTENT', 'startActivity(SettingsActivity)', evidence='SRC async/CategoryMenuTask.java:131-132')
e('SettingsActivity.<init>', 'S_SETTINGS', 'ENTERS', 'the settings root is shown', evidence='SRC SettingsActivity.java:54-61')
e('NavigationDrawerFragment.onEvent(SwitchFragmentEvent)', 'NavigationDrawerFragment.animateBurger', 'CALL', 'burger <-> arrow animation', evidence='SRC NavigationDrawerFragment.java:134-140')
e('NavigationDrawerFragment.animateBurger', 'NavigationDrawerFragment.lambda$animateBurger$1', 'ASYNC', 'ValueAnimator update listener', evidence=FW_VIEW + '; SRC NavigationDrawerFragment.java:229-232')
for poster in ('MainActivity.switchToList', 'DetailFragment.onAttach', 'DetailFragment.goHome'):
    e(poster, 'NavigationDrawerFragment.onEvent(SwitchFragmentEvent)', 'FRAMEWORK', 'SwitchFragmentEvent', evidence=FW_EB + '; SRC MainActivity.java:435; DetailFragment.java:334,1065')


# ================================================================== A2. list: rows, CAB, toolbar, search, undo, FAB
OPEN_AS = {'NOTES': 'EDIT', 'ARCHIVE': 'ARCHIVED', 'REMINDERS': 'EDIT', 'TRASH': 'TRASHED', 'UNCAT': 'EDIT', 'CATEGORY': 'EDIT'}
sup('ListFragment.lambda$initListView$3', 'ListFragment.lambda$initListView$4', 'ListFragment.lambda$initFab$0', 'ListFragment.lambda$onEvent$10',
    'ListFragment.performAction', 'ListFragment.onOptionsItemSelected', 'ListFragment$ModeCallback.onActionItemClicked', 'BaseActivity.requestPassword',
    'Fab.lambda$init$0', 'Fab.lambda$init$1', 'ListFragment.trashNotes', 'ListFragment.archiveNotes')
CAB_OF = {'NOTES': ('NOTES', True, False), 'REMINDERS': ('REMINDERS', True, False), 'ARCHIVE': ('ARCHIVE', False, True), 'UNCAT': ('UNCAT', True, True), 'CATEGORY': ('CATEGORY', True, True)}


def cab_pages(n):
    return ['S_LIST_CAB@TRASH'] if n == 'TRASH' else ['S_LIST_CAB@%s_1' % n, 'S_LIST_CAB@%s_N' % n]


for n in NAVS:
    p = 'S_LIST@' + n
    need_row = NEED_NOTE if n == 'NOTES' else None
    # open a note
    v = 'ListFragment.lambda$initListView$4@OPEN_' + n
    gui(p, v, 'Tap a note', needs_state=need_row, evidence='SRC ListFragment.java:519-527')
    e(v, 'ListFragment.editNote', 'CALL', 'editNote(note, view)', evidence='SRC ListFragment.java:521')
    e(v, 'S_DETAIL@' + OPEN_AS[n], 'ENTERS', 'the note opens in the editor after the zoom animation', evidence='SRC ListFragment.java:561-568,928-950; MainActivity.java:439-459')
    # start the action mode
    v = 'ListFragment.lambda$initListView$3@START_' + n
    gui(p, v, 'Long-press a note', needs_state=need_row, evidence='SRC ListFragment.java:507-516')
    for dst in ('ListFragment$ModeCallback.<init>', 'ListFragment.getActionMode', 'ListFragment.setCabTitle', 'ListFragment.toggleListViewItem'):
        e(v, dst, 'CALL', 'call in the long-click handler', evidence='SRC ListFragment.java:507-516')
    e(v, 'ListFragment$ModeCallback.onCreateActionMode', 'FRAMEWORK', 'startSupportActionMode calls the callback', evidence=FW_VIEW + '; SRC ListFragment.java:401-411')
    e(v, 'ListFragment$ModeCallback.onPrepareActionMode', 'FRAMEWORK', 'the action mode menu is prepared', evidence=FW_VIEW + '; SRC ListFragment.java:444-447')
    for cp in cab_pages(n)[:1]:
        e(v, cp, 'ENTERS', 'one note is selected: the contextual action bar replaces the toolbar', evidence='SRC ListFragment.java:507-516')
    # swipe to dismiss (library callback registered in onEvent(NotesLoadedEvent))
    if n != 'UNCAT':
        sv = 'ListFragment.lambda$onEvent$10@SWIPE_' + n
        gui(p, sv, 'Swipe a note sideways', needs_state=need_row if n == 'NOTES' else None, evidence='SRC ListFragment.java:1176-1222')
        for dst in ('ListFragment.finishActionMode', 'ListFragment.getSelectedNotes', 'LogDelegate.d', 'Navigation.checkNavigation(int)'):
            e(sv, dst, 'CALL', 'call in the swipe callback', evidence='SRC ListFragment.java:1177-1218')
        if n == 'TRASH':
            e(sv, 'ListFragment.trashNotes@UNTRASH', 'CALL', 'trashNotes(false): restore from trash', evidence='SRC ListFragment.java:1203-1205')
            e(sv, 'S_LIST@TRASH', 'ENTERS', 'the note disappears from the Trash list', evidence='SRC ListFragment.java:1272-1308')
        elif n == 'CATEGORY':
            e(sv, 'ListFragment.categorizeNotesExecute@NONE', 'CALL', 'categorizeNotesExecute(null): remove the category', evidence='SRC ListFragment.java:1207-1209')
            e(sv, 'S_LIST_UNDO@CATEGORIZE', 'ENTERS', 'the undo bar offers to undo', evidence='SRC ListFragment.java:1541-1547')
        elif n == 'ARCHIVE':
            e(sv, 'ListFragment.trashNotes@TRASH', 'CALL', 'trashNotes(true): swipe in Archive trashes', evidence='SRC ListFragment.java:1211-1214')
            e(sv, 'S_LIST_UNDO@TRASH', 'ENTERS', 'the undo bar offers to undo', evidence='SRC ListFragment.java:1301-1307')
        else:
            e(sv, 'ListFragment.archiveNotes@ARCHIVE', 'CALL', 'archiveNotes(true): swipe archives', evidence='SRC ListFragment.java:1215-1217')
            e(sv, 'S_LIST_UNDO@ARCHIVE', 'ENTERS', 'the undo bar offers to undo', evidence='SRC ListFragment.java:1431-1436')
            e(sv, 'S_LIST_UNDO@TRASH', 'ENTERS', 'the undo bar offers to undo (swipe to trash)', needs_state=NEED_SWIPE_TRASH, evidence='SRC ListFragment.java:1301-1307')
            e(sv, 'ListFragment.trashNotes@TRASH', 'CALL', 'trashNotes(true): "Swipe to trash" is on', needs_state=NEED_SWIPE_TRASH, evidence='SRC ListFragment.java:1211-1214')
        e(sv, 'PasswordHelper.requestPassword', 'CALL', 'a locked note asks for the password first', needs_state=NEED_LOCKED, evidence='SRC ListFragment.java:1191-1198')
        e(sv, 'S_DLG_PASSWORD@SWIPE', 'ENTERS', 'a locked note asks for the password', needs_state=NEED_LOCKED, evidence='SRC ListFragment.java:1191-1198')
    # toolbar items
    if n == 'REMINDERS':
        gui(p, 'ListFragment.onOptionsItemSelected@FILTER_REMOVE', 'Tap the "hide past reminders" icon', evidence='SRC ListFragment.java:764-765,780-791')
        gui(p, 'ListFragment.onOptionsItemSelected@FILTER', 'Tap the "show past reminders" icon', needs_state='The past-reminders filter was switched off with the other icon', evidence='SRC ListFragment.java:762-763')
    if n == 'CATEGORY':
        gui(p, 'ListFragment.onOptionsItemSelected@FILTER_CAT', 'Tap the "filter archived" icon', evidence='SRC ListFragment.java:766-767')
        gui(p, 'ListFragment.onOptionsItemSelected@FILTER_CAT_REMOVE', 'Tap the "show archived" icon', needs_state='The archived filter was switched on with the other icon', evidence='SRC ListFragment.java:768-769')
    if n != 'REMINDERS':
        gui(p, 'ListFragment.onOptionsItemSelected@SORT', 'Tap the sort icon', evidence='SRC ListFragment.java:770,831-833')
    gui(p, 'ListFragment.onOptionsItemSelected@CONTRACTED', 'Tap the "contracted view" icon', evidence='SRC ListFragment.java:772,837-839')
    gui(p, 'ListFragment.onOptionsItemSelected@EXPANDED', 'Tap the "expanded view" icon', needs_state='The contracted view was chosen with the other icon', evidence='SRC ListFragment.java:771,834-836')
    if n == 'TRASH':
        gui(p, 'ListFragment.onOptionsItemSelected@EMPTY_TRASH', 'Tap "Empty trash"', evidence='SRC ListFragment.java:773,840-842')
    # search
    gui(p, 'ListFragment$2.onMenuItemActionExpand', 'Tap the search icon', evidence='SRC ListFragment.java:688-735')
    # FAB (not shown in Archive, Reminders, Trash)
    if n in ('NOTES', 'UNCAT', 'CATEGORY'):
        gui(p, 'Fab.lambda$init$0@CLICK_' + n, 'Tap the + button', evidence='SRC models/views/Fab.java:62-68')
        gui(p, 'Fab.lambda$init$1@LONG_' + n, 'Long-press the + button', evidence='SRC models/views/Fab.java:69-76')
        e('Fab.lambda$init$0@CLICK_' + n, 'Fab.isExpanded', 'CALL', 'isExpanded()', evidence='SRC models/views/Fab.java:63')
        e('Fab.lambda$init$0@CLICK_' + n, 'Fab.performToggle', 'CALL', 'the FAB menu expands (default behaviour)', evidence='SRC models/views/Fab.java:66')
        e('Fab.lambda$init$0@CLICK_' + n, 'S_LIST_FAB', 'ENTERS', 'the FAB menu is open', evidence='SRC models/views/Fab.java:113-116')
        e('Fab.lambda$init$0@CLICK_' + n, 'Fab.performAction', 'CALL', 'performAction(v): a plain tap creates a note', needs_state=NEED_FAB_LONG, evidence='SRC models/views/Fab.java:63-64')
        e('Fab.lambda$init$1@LONG_' + n, 'Fab.performAction', 'CALL', 'performAction(v): a long-press creates a note (default)', evidence='SRC models/views/Fab.java:70-71')
        e('Fab.lambda$init$1@LONG_' + n, 'Fab.performToggle', 'CALL', 'a long-press expands the menu', needs_state=NEED_FAB_LONG, evidence='SRC models/views/Fab.java:72-73')
        e('Fab.lambda$init$1@LONG_' + n, 'ListFragment.lambda$initFab$0@MAIN', 'CALL', 'onFabItemClick(fab_expand_menu_button)', guard='not expanded', evidence='SRC models/views/Fab.java:118-125')
    if n == 'NOTES':
        gui(p, 'AbsListViewScrollDetector.onScroll', 'Scroll the notes list', needs_state='The list has enough notes to scroll (about 6 or more)', evidence='SRC models/views/Fab.java:77-93')
# FAB menu
e('ListFragment.lambda$initFab$0@MAIN', 'S_DETAIL@NEW', 'ENTERS', 'a new note is opened', evidence='SRC ListFragment.java:266-285')
for k, (lab, tgt) in {'NOTE': ('Tap the note button', 'NEW'), 'CAMERA': ('Tap the camera button', 'NEW'), 'CHECKLIST': ('Tap the checklist button', 'CHECKLIST')}.items():
    gui('S_LIST_FAB', 'Fab$2.onClick@' + k, lab, evidence='SRC models/views/Fab.java:94-111')
    e('Fab$2.onClick@' + k, 'ListFragment.lambda$initFab$0@' + k, 'CALL', 'onFabItemClick(id)', evidence='SRC models/views/Fab.java:106-111')
    e('ListFragment.lambda$initFab$0@' + k, 'S_DETAIL@' + tgt, 'ENTERS', 'a new %s is opened' % ('checklist' if k == 'CHECKLIST' else 'note'), evidence='SRC ListFragment.java:266-285')
    for dst in ('ListFragment.editNote', 'Note.<init>()'):
        e('ListFragment.lambda$initFab$0@' + k, dst, 'CALL', 'call in the FAB handler', evidence='SRC ListFragment.java:270-284')
for dst in ('ListFragment.editNote', 'Note.<init>()'):
    e('ListFragment.lambda$initFab$0@MAIN', dst, 'CALL', 'call in the FAB handler', evidence='SRC ListFragment.java:270')
gui('S_LIST_FAB', 'MainActivity.onBackPressed@FAB', 'Press Back', evidence='SRC MainActivity.java:279-294')
e('MainActivity.onBackPressed@FAB', 'ListFragment.closeFab', 'CALL', 'closeFab()', evidence='SRC MainActivity.java:289')
e('ListFragment.closeFab', 'Fab.performToggle', 'CALL', 'collapse the menu', guard='fab.isExpanded()', evidence='SRC ListFragment.java:291-297')
e('MainActivity.onBackPressed@FAB', 'S_LIST@NOTES', 'ENTERS', 'the FAB menu collapses', evidence='SRC MainActivity.java:289')
# back from the list: leave the app
for n in NAVS:
    gui('S_LIST@' + n, 'MainActivity.onBackPressed@LIST', 'Press Back', evidence='SRC MainActivity.java:279-294')
e('MainActivity.onBackPressed@LIST', 'ListFragment.closeFab', 'CALL', 'closeFab() returns false', evidence='SRC MainActivity.java:289')
e('MainActivity.onBackPressed@LIST', 'MainActivity.getDrawerLayout', 'CALL', 'drawer checks', evidence='SRC MainActivity.java:282-287')
e('MainActivity.onBackPressed@LIST', 'MainActivity.checkFragmentInstance', 'CALL', 'which fragment is shown', evidence='SRC MainActivity.java:258-279')
e('MainActivity.onBackPressed@LIST', 'S_EXIT', 'ENTERS', 'the activity finishes and the password gate is reset', evidence='SRC MainActivity.java:289-292')
# the empty-state easter egg
gui('S_LIST@NOTES', 'ListFragment.lambda$initEasterEgg$2', 'Tap the empty-list image', guard='no note exists (empty view shown)', evidence='SRC ListFragment.java:325-338')
e('ListFragment.lambda$initEasterEgg$2', 'ListFragment.stopJingles', 'CALL', 'stop an already running animation', guard='jinglesAnimation != null', needs_state='The empty-list image was tapped once before', evidence='SRC ListFragment.java:334-336')
e('ListFragment.lambda$initEasterEgg$2', 'ListFragment.lambda$null$1', 'ASYNC', 'empyListItem.post(start the jingles animation)', evidence=FW_POST + '; SRC ListFragment.java:329-333')
sup(('ListFragment.onEvent(NotesLoadedEvent)', 'ListFragment.restoreListScrollPosition'), ('ListFragment.onEvent(NotesLoadedEvent)', 'NoteAdapter.getClosestNotePosition'))
e('ListFragment.onEvent(NotesLoadedEvent)', 'ListFragment.restoreListScrollPosition', 'CALL', 'restore the scroll position', needs_state=NEED_NOTE, evidence='SRC ListFragment.java:1232-1237')
e('ListFragment.onEvent(NotesLoadedEvent)', 'NoteAdapter.getClosestNotePosition', 'CALL', 'Reminders: scroll to the closest reminder', needs_state=NEED_REM_NAV, evidence='SRC ListFragment.java:1233-1235')
e('ListFragment.onEvent(NotesLoadedEvent)', 'NoteAdapter.getView', 'FRAMEWORK', 'the ListView binds the rows', needs_state=NEED_NOTE, evidence=FW_VIEW + '; SRC ListFragment.java:1224')
e('ListFragment.onEvent(NotesLoadedEvent)', 'NoteViewHolder_ViewBinding.<init>', 'FRAMEWORK', 'new NoteViewHolder(view) binds with ButterKnife', evidence=FW_BIND + '; SRC models/holders/NoteViewHolder.java')
e('ListFragment.onEvent(NotesLoadedEvent)', 'TextWorkerTask.doInBackground', 'ASYNC', 'each bound row parses its text in an AsyncTask', needs_state=NEED_NOTE, evidence=FW_ASYNC + '; SRC models/adapters/NoteAdapter.java')
e('TextWorkerTask.doInBackground', 'TextWorkerTask.onPostExecute', 'ASYNC', 'the parsed text is delivered on the main thread', evidence=FW_ASYNC + '; SRC async/TextWorkerTask.java:50-75')


# ---- NoteProcessor: the template method is split per processor so that doInBackground calls the right processNote
sup(('NoteProcessor$NotesProcessorTask.doInBackground', 'NoteProcessorArchive.processNote'), ('NoteProcessor$NotesProcessorTask.doInBackground', 'NoteProcessorDelete.processNote'),
    ('NoteProcessor$NotesProcessorTask.doInBackground', 'NoteProcessorTrash.processNote'), ('NoteProcessor$NotesProcessorTask.doInBackground', 'NoteProcessorCategorize.processNote'),
    ('NoteProcessor$NotesProcessorTask.onPostExecute', 'NoteProcessorDelete.afterProcess'), ('NoteProcessor$NotesProcessorTask.onPostExecute', 'NoteProcessor.afterProcess'))
PROC = {'ARCHIVE': ('NoteProcessorArchive', ('ListFragment.archiveNote',)), 'TRASH': ('NoteProcessorTrash', ('ListFragment.trashNote',)),
        'CATEGORIZE': ('NoteProcessorCategorize', ('ListFragment.categorizeNote',)),
        'DELETE': ('NoteProcessorDelete', ('MainActivity.deleteNote', 'ListFragment.deleteNotesExecute', 'DetailFragment.deleteMergedNotes'))}
for k, (cls, callers) in PROC.items():
    for cal in callers:
        sup((cal, 'NoteProcessor.process'))
        e(cal, 'NoteProcessor.process@' + k, 'CALL', 'new %s(notes).process()' % cls, evidence='SRC (bytecode) call to NoteProcessor.process on a %s' % cls)
    e('NoteProcessor.process@' + k, 'NoteProcessor$NotesProcessorTask.<init>', 'CALL', 'creates the task', evidence='SRC async/notes/NoteProcessor.java:38-41')
    e('NoteProcessor.process@' + k, 'NoteProcessor$NotesProcessorTask.doInBackground@' + k, 'ASYNC', 'task.executeOnExecutor(...)', evidence=FW_ASYNC + '; SRC async/notes/NoteProcessor.java:38-41')
    e('NoteProcessor$NotesProcessorTask.doInBackground@' + k, cls + '.processNote', 'CALL', 'processNote(note) for each note', evidence='SRC async/notes/NoteProcessor.java:50-56')
    e('NoteProcessor$NotesProcessorTask.doInBackground@' + k, 'NoteProcessor$NotesProcessorTask.onPostExecute@' + k, 'ASYNC', 'the processed notes are delivered on the main thread', evidence=FW_ASYNC + '; SRC async/notes/NoteProcessor.java:59-62')
    e('NoteProcessor$NotesProcessorTask.onPostExecute@' + k, 'NoteProcessorDelete.afterProcess' if k == 'DELETE' else 'NoteProcessor.afterProcess', 'CALL', 'afterProcess(notes)', evidence='SRC async/notes/NoteProcessor.java:59-67')
# ---- CAB items
CAB_ITEMS = {  # item -> (label, protected, performAction continuation)
    'CATEGORY': ('Category', False), 'TAGS': ('Tags', False), 'SHARE': ('Share', False), 'MERGE': ('Merge', True), 'ARCHIVE': ('Archive', False), 'UNARCHIVE': ('Unarchive', False),
    'TRASH': ('Trash', False), 'UNTRASH': ('Restore from trash', False), 'DELETE': ('Delete', False), 'SELECT_ALL': ('Select all', True), 'REMINDER': ('Add reminder', False)}


def cab_items(n, count):
    if n == 'TRASH':
        return ['UNTRASH', 'DELETE', 'SELECT_ALL']
    show_archive, show_unarchive = CAB_OF[n][1], CAB_OF[n][2]
    items = ['REMINDER', 'CATEGORY', 'TAGS', 'TRASH', 'SELECT_ALL']
    items.append('SHARE' if count == '1' else 'MERGE')
    if show_archive:
        items.append('ARCHIVE')
    if show_unarchive:
        items.append('UNARCHIVE')
    return items


for n in NAVS:
    for page in cab_pages(n):
        count = 'T' if n == 'TRASH' else page[-1]
        for it in cab_items(n, count):
            lab, prot = CAB_ITEMS[it]
            need = None
            if it == 'UNARCHIVE' and n in ('UNCAT', 'CATEGORY') and count == '1':
                need = 'The selected note is archived'
            gui(page, 'ListFragment$ModeCallback.onActionItemClicked@' + it, 'Tap "%s" in the action bar' % lab, needs_state=need, evidence='SRC ListFragment.java:451-465,611-648')
        # tap another note: toggle selection
        if n == 'TRASH':
            tgt_more = 'S_LIST_CAB@TRASH'
            tv = 'ListFragment.lambda$initListView$4@TOGGLE_TRASH'
        else:
            tv = 'ListFragment.lambda$initListView$4@TOGGLE_' + n
        gui(page, tv, 'Tap another note (toggles its selection)', needs_state=NEED_NOTE if count != 'T' else None, evidence='SRC ListFragment.java:519-527,478-496')
        gui(page, 'ListFragment$ModeCallback.onDestroyActionMode@' + n, 'Press Back (closes the selection)', evidence='SRC ListFragment.java:416-440')
for n in NAVS:
    tv = 'ListFragment.lambda$initListView$4@TOGGLE_' + n
    for dst in ('ListFragment.toggleListViewItem', 'ListFragment.setCabTitle', 'ListFragment.getActionMode'):
        e(tv, dst, 'CALL', 'call in the item-click handler', evidence='SRC ListFragment.java:519-527')
    if n == 'TRASH':
        e(tv, 'S_LIST_CAB@TRASH', 'ENTERS', 'selection changes', evidence='SRC ListFragment.java:478-496')
        e(tv, 'S_LIST@TRASH', 'ENTERS', 'the last note was deselected: the action mode ends', evidence='SRC ListFragment.java:492-494')
    else:
        for target in cab_pages(n):
            e(tv, target, 'ENTERS', 'selection changes', needs_state=('At least two notes exist' if target.endswith('_N') else None), evidence='SRC ListFragment.java:478-496')
        e(tv, 'S_LIST@' + n, 'ENTERS', 'the last note was deselected: the action mode ends', evidence='SRC ListFragment.java:492-494')
    d = 'ListFragment$ModeCallback.onDestroyActionMode@' + n
    e(d, 'S_LIST@' + n, 'ENTERS', 'the contextual bar closes', evidence='SRC ListFragment.java:416-440')
    e(d, 'ListFragment$ModeCallback.onDestroyActionMode', 'CALL', 'onDestroyActionMode(mode)', evidence='SRC ListFragment.java:416-440')
sup(('ListFragment$ModeCallback.onDestroyActionMode', 'ListFragment.isFabAllowed(boolean)'))
for it, (lab, prot) in CAB_ITEMS.items():
    a = 'ListFragment$ModeCallback.onActionItemClicked@' + it
    pa = 'ListFragment.performAction@C_' + it
    e(a, 'ListFragment.getSelectedNotes', 'CALL', 'getSelectedNotes()', evidence='SRC ListFragment.java:451-465')
    e(a, pa, 'CALL', 'performAction(item, mode)', evidence='SRC ListFragment.java:451-463')
    if not prot:
        e(a, 'ListFragment$ModeCallback.lambda$onActionItemClicked$0', 'CALL', 'the password validator runs at once when no selected note is locked', evidence='SRC ListFragment.java:451-463; BaseActivity.java:115-134')
        e('ListFragment$ModeCallback.lambda$onActionItemClicked$0', pa, 'CALL', 'performAction after the password step', needs_state=NEED_LOCKED, evidence='SRC ListFragment.java:454-459')
        e(a, 'S_DLG_PASSWORD@CAB', 'ENTERS', 'a selected note is locked: the password dialog opens', needs_state=NEED_LOCKED, evidence='SRC BaseActivity.java:115-134')
    for dst in ('BaseFragment.isOptionsItemFastClick', 'ListFragment.checkSortActionPerformed'):
        e(pa, dst, 'CALL', 'call in performAction', evidence='SRC ListFragment.java:798-890')
tgt = {'CATEGORY': 'ListFragment.categorizeNotes', 'TAGS': 'ListFragment.tagNotes', 'SHARE': 'ListFragment.share', 'MERGE': 'ListFragment.merge', 'ARCHIVE': 'ListFragment.archiveNotes@ARCHIVE',
       'UNARCHIVE': 'ListFragment.archiveNotes@UNARCHIVE', 'TRASH': 'ListFragment.trashNotes@TRASH', 'UNTRASH': 'ListFragment.trashNotes@UNTRASH', 'DELETE': 'ListFragment.deleteNotes',
       'SELECT_ALL': 'ListFragment.selectAllNotes', 'REMINDER': 'ListFragment.addReminders'}
for it, dst in tgt.items():
    e('ListFragment.performAction@C_' + it, dst, 'CALL', 'the %s branch of the action switch' % it.lower(), evidence='SRC ListFragment.java:847-880')
# results of the CAB items
# page after an item (the nav class of the CAB is lost in the shared handler: least-state / exact page where the item implies it)
e('ListFragment.archiveNotes@ARCHIVE', 'S_LIST_UNDO@ARCHIVE', 'ENTERS', 'the undo bar appears', evidence='SRC ListFragment.java:1431-1436')
e('ListFragment.archiveNotes@UNARCHIVE', 'S_LIST@ARCHIVE', 'ENTERS', 'the notes leave the archive list', evidence='SRC ListFragment.java:1392-1429')
e('ListFragment.trashNotes@TRASH', 'S_LIST_UNDO@TRASH', 'ENTERS', 'the undo bar appears', evidence='SRC ListFragment.java:1301-1308')
e('ListFragment.trashNotes@UNTRASH', 'S_LIST@TRASH', 'ENTERS', 'the notes leave the Trash list', evidence='SRC ListFragment.java:1272-1297')
e('ListFragment.categorizeNotesExecute@NONE', 'S_LIST_UNDO@CATEGORIZE', 'ENTERS', 'the undo bar appears', evidence='SRC ListFragment.java:1541-1547')
e('ListFragment.categorizeNotesExecute@CAT', 'S_LIST@NOTES', 'ENTERS', 'the notes are categorized and the action mode ends', evidence='SRC ListFragment.java:1500-1549')
clone_auto('ListFragment.trashNotes', 'ListFragment.trashNotes@TRASH', exclude=('ListFragment.trashNote',))
clone_auto('ListFragment.trashNotes', 'ListFragment.trashNotes@UNTRASH', exclude=('ListFragment.trackModifiedNotes', 'ReminderHelper.removeReminder', 'UndoBarController.showUndoBar', 'Fab.hideFab', 'OmniNotes.getAppContext'))
clone_auto('ListFragment.archiveNotes', 'ListFragment.archiveNotes@ARCHIVE', exclude=('ListFragment.archiveNote',))
clone_auto('ListFragment.archiveNotes', 'ListFragment.archiveNotes@UNARCHIVE', exclude=('ListFragment.trackModifiedNotes', 'UndoBarController.showUndoBar', 'Fab.hideFab'))
sup('ListFragment.categorizeNotesExecute')
clone_auto('ListFragment.categorizeNotesExecute', 'ListFragment.categorizeNotesExecute@CAT', exclude=('ListFragment.trackModifiedNotes', 'UndoBarController.showUndoBar', 'Fab.hideFab'))
clone_auto('ListFragment.categorizeNotesExecute', 'ListFragment.categorizeNotesExecute@NONE', exclude=('ListFragment.categorizeNote',))
# category dialog (CAB)
e('ListFragment.categorizeNotes', 'S_DLG_CATEGORIZE_LIST', 'ENTERS', 'the categorize dialog opens', evidence='SRC ListFragment.java:1473-1497')
for cb in ('onCreateViewHolder', 'onBindViewHolder'):
    e('ListFragment.categorizeNotes', 'CategoryRecyclerViewAdapter.' + cb, 'FRAMEWORK', 'the dialog RecyclerView binds the category rows', needs_state=NEED_CATEGORY, evidence=FW_VIEW + '; SRC ListFragment.java:1479')
e('ListFragment.categorizeNotes', 'CategoryRecyclerViewAdapter.getItemCount', 'FRAMEWORK', 'the dialog RecyclerView asks for the row count', evidence=FW_VIEW + '; SRC ListFragment.java:1479')
e('ListFragment.categorizeNotes', 'RecyclerViewItemClickSupport$3.onChildViewAttachedToWindow', 'FRAMEWORK', 'rows attach: click listeners are installed', needs_state=NEED_CATEGORY, evidence=FW_VIEW + '; SRC models/listeners/RecyclerViewItemClickSupport.java')
e('S_DLG_CATEGORIZE_LIST', 'ListFragment.lambda$categorizeNotes$13', 'GUI', 'Tap "Add category"', gui=['Tap "Add category"'], evidence=FW_MD + '; SRC ListFragment.java:1484-1489')
e('ListFragment.lambda$categorizeNotes$13', 'S_CATEGORY@NEW_LIST', 'ENTERS', 'startActivityForResult(CategoryActivity, noHome)', evidence='SRC ListFragment.java:1485-1488')
gui('S_DLG_CATEGORIZE_LIST', 'ListFragment.lambda$categorizeNotes$14', 'Tap "Remove category"', evidence=FW_MD + '; SRC ListFragment.java:1489')
e('ListFragment.lambda$categorizeNotes$14', 'ListFragment.categorizeNotesExecute@NONE', 'CALL', 'categorizeNotesExecute(null)', evidence='SRC ListFragment.java:1489')
gui('S_DLG_CATEGORIZE_LIST', 'RecyclerViewItemClickSupport$1.onClick@LIST_CAT', 'Tap a category', needs_state=NEED_CATEGORY, evidence='SRC models/listeners/RecyclerViewItemClickSupport.java; ListFragment.java:1491-1494')
e('RecyclerViewItemClickSupport$1.onClick@LIST_CAT', 'ListFragment.lambda$categorizeNotes$15', 'CALL', 'OnItemClickListener.onItemClick', evidence='SRC ListFragment.java:1491-1494')
e('ListFragment.lambda$categorizeNotes$15', 'ListFragment.categorizeNotesExecute@CAT', 'CALL', 'categorizeNotesExecute(category)', evidence='SRC ListFragment.java:1493')
e('ListFragment.lambda$categorizeNotes$15', 'S_LIST@NOTES', 'ENTERS', 'the dialog closes and the notes are categorized', evidence='SRC ListFragment.java:1492-1493')
e('S_DLG_CATEGORIZE_LIST', 'S_LIST@NOTES', 'ENTERS', 'Press Back: the dialog is dismissed (the action mode stays)', gui=['Press Back'], evidence=BACK_DLG)
# result of CategoryActivity opened from the CAB or the drawer
sup(('ListFragment.onActivityResult', 'ListFragment.categorizeNotesExecute'))
# tags dialog (CAB)
sup(('ListFragment.tagNotes', 'TagsHelper.getPreselectedTagsArray(List,List)'), ('ListFragment.tagNotes', 'TagsHelper.getTagsArray'), ('ListFragment.filterByTags', 'TagsHelper.getTagsArray'))
for dst in ('TagsHelper.getPreselectedTagsArray(List,List)', 'TagsHelper.getTagsArray'):
    e('ListFragment.tagNotes', dst, 'CALL', 'builds the tag dialog', needs_state=NEED_TAGS, evidence='SRC ListFragment.java:1572-1576')
e('ListFragment.tagNotes', 'S_DLG_TAG_NOTES', 'ENTERS', 'the tag dialog opens', needs_state=NEED_TAGS, evidence='SRC ListFragment.java:1574-1582')
gui('S_DLG_TAG_NOTES', 'ListFragment.lambda$tagNotes$16', 'Tick tags and tap OK', evidence=FW_MD + '; SRC ListFragment.java:1578-1582')
e('ListFragment.lambda$tagNotes$16', 'ListFragment.tagNotesExecute', 'CALL', 'tagNotesExecute(...)', evidence='SRC ListFragment.java:1580')
e('ListFragment.lambda$tagNotes$16', 'S_LIST@NOTES', 'ENTERS', 'the dialog closes and the action mode ends', evidence='SRC ListFragment.java:1579-1605')
e('S_DLG_TAG_NOTES', 'S_LIST@NOTES', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
# delete (Trash CAB)
e('ListFragment.deleteNotes', 'S_DLG_DELETE_NOTES', 'ENTERS', 'the confirmation opens', evidence='SRC ListFragment.java:1352-1364')
gui('S_DLG_DELETE_NOTES', 'ListFragment.lambda$deleteNotes$12', 'Tap OK', evidence=FW_MD + '; SRC ListFragment.java:1356-1361')
e('ListFragment.lambda$deleteNotes$12', 'ListFragment.lambda$null$11', 'CALL', 'the password validator runs at once when no selected note is locked', evidence='SRC BaseActivity.java:115-134')
e('ListFragment.lambda$deleteNotes$12', 'S_DLG_PASSWORD@DELETE_NOTES', 'ENTERS', 'a selected note is locked', needs_state=NEED_LOCKED, evidence='SRC BaseActivity.java:115-134')
e('ListFragment.lambda$null$11', 'ListFragment.deleteNotesExecute', 'CALL', 'deleteNotesExecute()', evidence='SRC ListFragment.java:1358-1360')
e('ListFragment.lambda$null$11', 'S_LIST@TRASH', 'ENTERS', 'the notes are deleted for good', evidence='SRC ListFragment.java:1370-1382')
e('S_DLG_DELETE_NOTES', 'S_LIST@TRASH', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
# share
e('ListFragment.share', 'S_EXT_APP', 'ENTERS', 'the system share chooser opens', env=ENV_PICKER, evidence='SRC MainActivity.java:462-511')
e('MainActivity.shareNote', 'S_EXT_APP', 'ENTERS', 'startActivity(Intent.createChooser(...))', env=ENV_PICKER, evidence='SRC MainActivity.java:462-511')
# merge
e('ListFragment.merge', 'ListFragment.onEventAsync', 'FRAMEWORK', 'NotesMergeEvent (onEventAsync runs on a pool thread)', evidence=FW_EB + '; SRC ListFragment.java:1737-1746')
e('ListFragment.onEventAsync', 'ListFragment.lambda$onEventAsync$17', 'ASYNC', 'new Handler(mainLooper).post(open the merged note)', evidence=FW_POST + '; SRC ListFragment.java:1748-1766')
e('ListFragment.onEventAsync', 'NotesHelper.mergeNotes', 'CALL', 'NotesHelper.mergeNotes(...)', evidence='SRC ListFragment.java:1747')
e('ListFragment.lambda$onEventAsync$17', 'S_DETAIL@NEW', 'ENTERS', 'the merged (unsaved) note opens in the editor', evidence='SRC ListFragment.java:1763-1764')
# add reminders from the CAB: SnoozeActivity shows the picker
e('ListFragment.addReminders', 'SnoozeActivity.<init>', 'INTENT', 'startActivityForResult(SnoozeActivity, ACTION_POSTPONE)', evidence='SRC ListFragment.java:893-899')


# ---- toolbar items (ListFragment.onOptionsItemSelected -> performAction), one chain per item
TB = {'FILTER_REMOVE': 'ListFragment.filterReminders', 'FILTER': 'ListFragment.filterReminders', 'FILTER_CAT': 'ListFragment.filterCategoryArchived',
      'FILTER_CAT_REMOVE': 'ListFragment.filterCategoryArchived', 'SORT': 'ListFragment.initSortingSubmenu', 'SORT_ITEM': None, 'CONTRACTED': 'ListFragment.switchNotesView',
      'EXPANDED': 'ListFragment.switchNotesView', 'EMPTY_TRASH': 'ListFragment.emptyTrash', 'UNCOMPLETE': 'ListFragment.filterByUncompleteChecklists', 'TAGS': 'ListFragment.filterByTags'}
for t, dst in TB.items():
    oi = 'ListFragment.onOptionsItemSelected@' + t
    pa = 'ListFragment.performAction@T_' + t
    e(oi, 'ListFragment.getSelectedNotes', 'CALL', 'getSelectedNotes()', evidence='SRC ListFragment.java:780-791')
    if t == 'EMPTY_TRASH':
        e(oi, 'ListFragment.lambda$onOptionsItemSelected$6', 'CALL', 'BaseActivity.requestPassword asks nothing: no note is selected, so the validator runs at once', evidence='SRC ListFragment.java:781-787; BaseActivity.java:115-134')
        e('ListFragment.lambda$onOptionsItemSelected$6', pa, 'CALL', 'performAction(item, null)', evidence='SRC ListFragment.java:783-786')
    else:
        e(oi, pa, 'CALL', 'performAction(item, null)', evidence='SRC ListFragment.java:789')
    for d in ('BaseFragment.isOptionsItemFastClick', 'ListFragment.checkSortActionPerformed'):
        e(pa, d, 'CALL', 'call in performAction', evidence='SRC ListFragment.java:798-890')
    if dst:
        e(pa, dst, 'CALL', 'the %s branch of the toolbar switch' % t.lower(), evidence='SRC ListFragment.java:805-845')
gui('S_SORT_MENU', 'ListFragment.onOptionsItemSelected@SORT_ITEM', 'Tap a sort criterion', evidence='SRC ListFragment.java:587-602,996-1011')
e('ListFragment.onOptionsItemSelected@SORT_ITEM', 'S_LIST@NOTES', 'ENTERS', 'the list is re-sorted', evidence='SRC ListFragment.java:996-1011')
e('ListFragment.initSortingSubmenu', 'S_SORT_MENU', 'ENTERS', 'the sort sub-menu opens', evidence='SRC ListFragment.java:587-604')
e('ListFragment.emptyTrash', 'S_DLG_EMPTY_TRASH', 'ENTERS', 'the confirmation opens', evidence='SRC ListFragment.java:1018-1043')
gui('S_DLG_EMPTY_TRASH', 'ListFragment$3.onClick', 'Tap OK', evidence=FW_MD + '; SRC ListFragment.java:1022-1042')
e('ListFragment$3.onClick', 'ListFragment$3.lambda$onClick$0', 'CALL', 'the password validator runs at once when no locked note is among them', evidence='SRC ListFragment.java:1031-1038')
e('ListFragment$3.onClick', 'ListFragment.deleteNotesExecute', 'CALL', 'no locked note: deleteNotesExecute()', evidence='SRC ListFragment.java:1039')
e('ListFragment$3.onClick', 'S_DLG_PASSWORD@EMPTY_TRASH_DIALOG', 'ENTERS', 'a locked note is in the trash', needs_state=NEED_LOCKED, evidence='SRC ListFragment.java:1026-1038')
e('ListFragment$3.lambda$onClick$0', 'ListFragment.deleteNotesExecute', 'CALL', 'deleteNotesExecute()', needs_state=NEED_LOCKED, evidence='SRC ListFragment.java:1034-1036')
e('ListFragment$3.onClick', 'S_LIST@TRASH', 'ENTERS', 'the trash is emptied', evidence='SRC ListFragment.java:1039-1040')
e('S_DLG_EMPTY_TRASH', 'S_LIST@TRASH', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('ListFragment.deleteNotesExecute', 'ListFragment.finishActionMode', 'CALL', 'finishActionMode()', evidence='SRC ListFragment.java:1375')
# ---- search
e('ListFragment$2.onMenuItemActionExpand', 'S_LIST_SEARCH_EDIT', 'ENTERS', 'the search view expands and takes focus', evidence='SRC ListFragment.java:706-735')
e('ListFragment$2.onMenuItemActionExpand', 'ListFragment$2$1.<init>', 'CALL', 'installs the query listener', evidence='SRC ListFragment.java:710')
gui('S_LIST_SEARCH_EDIT', 'ListFragment.lambda$initSearchView$5', 'Focus the search field', evidence='SRC ListFragment.java:686')
gui('S_LIST_SEARCH_EDIT', 'ListFragment$2$1.onQueryTextChange', 'Type in the search field', evidence='SRC ListFragment.java:719-731')
gui('S_LIST_SEARCH_EDIT', 'ListFragment$2$1.onQueryTextSubmit', 'Press the search key on the keyboard', evidence='SRC ListFragment.java:712-716')
e('ListFragment$2$1.onQueryTextSubmit', 'MainActivity.onNewIntent', 'SYSTEM', 'with instant search off, SearchView sends ACTION_SEARCH to MainActivity (singleTop)', evidence='INFERRED SearchView submits the query as ACTION_SEARCH to the searchable activity (SearchView / SearchManager source not read); SRC ListFragment.java:714; AndroidManifest.xml:65-114')
e('ListFragment$2$1.onQueryTextSubmit', 'S_LIST_SEARCH_RESULT', 'ENTERS', 'the results are listed under a search label', evidence='SRC ListFragment.java:1087-1095')
e('MainActivity.onNewIntent', 'MainActivity.onResume', 'FRAMEWORK', 'the singleTop activity resumes after onNewIntent', evidence='INFERRED a singleTop activity that gets onNewIntent is resumed afterwards (Activity lifecycle: ActivityThread handleNewIntent not read); SRC MainActivity.java:111-120')
e('MainActivity.onResume', 'ListFragment.onResume', 'FRAMEWORK', 'the activity resumes its fragments', evidence=FW_FRAG)
gui('S_LIST_SEARCH_EDIT', 'ListFragment.onOptionsItemSelected@UNCOMPLETE', 'Tap the "uncompleted checklists" icon', evidence='SRC ListFragment.java:774')
gui('S_LIST_SEARCH_EDIT', 'ListFragment.onOptionsItemSelected@TAGS', 'Tap the tags icon', evidence='SRC ListFragment.java:775')
e('ListFragment.filterByUncompleteChecklists', 'S_LIST_SEARCH_RESULT', 'ENTERS', 'the uncompleted checklists are listed', evidence='SRC ListFragment.java:1797-1799')
e('ListFragment.filterByTags', 'S_DLG_FILTER_TAGS', 'ENTERS', 'the tag filter dialog opens', needs_state=NEED_TAGS, evidence='SRC ListFragment.java:1801-1836')
for d in ('TagsHelper.getTagsArray',):
    e('ListFragment.filterByTags', d, 'CALL', 'builds the tag dialog', needs_state=NEED_TAGS, evidence='SRC ListFragment.java:1811-1813')
gui('S_DLG_FILTER_TAGS', 'ListFragment.lambda$filterByTags$18', 'Tick tags and tap OK', evidence=FW_MD + '; SRC ListFragment.java:1815-1834')
e('ListFragment.lambda$filterByTags$18', 'S_LIST_SEARCH_RESULT', 'ENTERS', 'the notes with those tags are listed', evidence='SRC ListFragment.java:1823-1833')
e('S_DLG_FILTER_TAGS', 'S_LIST_SEARCH_EDIT', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
gui('S_LIST_SEARCH_EDIT', 'ListFragment$2.onMenuItemActionCollapse', 'Tap the back arrow of the search bar', evidence='SRC ListFragment.java:694-704')
e('ListFragment$2.onMenuItemActionCollapse', 'S_LIST@NOTES', 'ENTERS', 'the search view collapses and the full list returns', evidence='SRC ListFragment.java:694-704')
gui('S_LIST_SEARCH_RESULT', 'ListFragment.lambda$toggleSearchLabel$8', 'Tap the X of the search label', evidence='SRC ListFragment.java:1128')
e('ListFragment.lambda$toggleSearchLabel$8', 'ListFragment.toggleSearchLabel', 'CALL', 'toggleSearchLabel(false)', evidence='SRC ListFragment.java:1128')
e('ListFragment.lambda$toggleSearchLabel$8', 'S_LIST@NOTES', 'ENTERS', 'the label closes and the full list returns', evidence='SRC ListFragment.java:1131-1149')
gui('S_LIST_SEARCH_RESULT', 'MainActivity.onBackPressed@LIST', 'Press Back', evidence='SRC MainActivity.java:279-294')
v = 'ListFragment.lambda$initListView$4@OPEN_SEARCH'
gui('S_LIST_SEARCH_RESULT', v, 'Tap a result', evidence='SRC ListFragment.java:519-527')
e(v, 'ListFragment.editNote', 'CALL', 'editNote(note, view)', evidence='SRC ListFragment.java:521')
e(v, 'S_DETAIL@EDIT', 'ENTERS', 'the note opens in the editor', evidence='SRC ListFragment.java:928-950')
e('MainActivity.onNewIntent', 'MainActivity.handleIntents', 'CALL', 'handleIntents()', evidence='SRC MainActivity.java:194-202')
# ---- undo bar
e('UndoBarController$1.onClick', 'UndoBarController.hideUndoBar', 'CALL', 'hideUndoBar(false)', evidence='SRC models/UndoBarController.java:73')
e('UndoBarController$1.onClick', 'ListFragment.onUndo', 'CALL', 'mUndoListener.onUndo(token)', evidence='SRC models/UndoBarController.java:74; ListFragment.java:1647-1685')
e('UndoBarController$1.onClick', 'S_LIST@NOTES', 'ENTERS', 'the change is undone', evidence='SRC ListFragment.java:1647-1685')
e('InterceptorLinearLayout.onInterceptTouchEvent', 'ListFragment.onViewTouchOccurred', 'CALL', 'OnViewTouchedListener.onViewTouchOccurred', evidence='SRC models/views/InterceptorLinearLayout.java')
e('UndoBarController.hideUndoBar', 'UndoBarController$2.onAnimationEnd', 'FRAMEWORK', 'the fade-out ends', guard='!immediate', evidence=FW_VIEW + '; SRC models/UndoBarController.java:117-131')
# ---- category activity (new from CAB, new from editor, edit from drawer)
for v, cal in (('NEW_LIST', 'ListFragment.lambda$categorizeNotes$13'), ('EDIT', 'ListFragment.editCategory'), ('NEW_DETAIL', 'DetailFragment.lambda$categorizeNote$15')):
    e(cal, 'CategoryActivity.<init>', 'INTENT', 'startActivityForResult(CategoryActivity)', evidence='SRC ListFragment.java:1485-1488,1463-1467; DetailFragment.java:1259-1263')
e('CategoryActivity.<init>', 'CategoryActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC CategoryActivity.java:68-85')
e('CategoryActivity.onCreate', 'CategoryActivity_ViewBinding.<init>(CategoryActivity,View)', 'FRAMEWORK', 'ButterKnife.bind(this)', evidence=FW_BIND + '; SRC CategoryActivity.java:71')
sup('CategoryActivity.saveCategory', 'CategoryActivity.deleteCategory', 'CategoryActivity.showColorChooserCustomColors')
for v in ('NEW_LIST', 'NEW_DETAIL', 'EDIT'):
    p = 'S_CATEGORY@' + v
    gui(p, 'CategoryActivity_ViewBinding$1.doClick@' + v, 'Tap the colour circle', evidence='SRC CategoryActivity.java:93-101')
    e('CategoryActivity_ViewBinding$1.doClick@' + v, 'CategoryActivity.showColorChooserCustomColors@' + v, 'CALL', 'target.showColorChooserCustomColors()', evidence='INFERRED ButterKnife DebouncingOnClickListener forwards the click to the generated listener (ButterKnife source not read); SRC CategoryActivity.java:93-101')
    e('CategoryActivity.showColorChooserCustomColors@' + v, 'S_DLG_COLOR_CHOOSER@' + v, 'ENTERS', 'the colour dialog opens', evidence='SRC CategoryActivity.java:96-99')
    gui('S_DLG_COLOR_CHOOSER@' + v, 'CategoryActivity.onColorSelection@' + v, 'Pick a colour', evidence=FW_MD + '; SRC CategoryActivity.java:104-107')
    e('CategoryActivity.onColorSelection@' + v, 'S_CATEGORY@' + v, 'ENTERS', 'the colour is applied and the dialog closes', evidence='SRC CategoryActivity.java:104-107')
    e('CategoryActivity.onColorSelection@' + v, 'CategoryActivity.onColorSelection', 'CALL', 'onColorSelection(dialog, color)', evidence='SRC CategoryActivity.java:104-107')
    gui('S_DLG_COLOR_CHOOSER@' + v, 'CategoryActivity.onColorChooserDismissed@' + v, 'Press Back (dismiss)', evidence='SRC CategoryActivity.java:110-112')
    e('CategoryActivity.onColorChooserDismissed@' + v, 'S_CATEGORY@' + v, 'ENTERS', 'the dialog closes', evidence='SRC CategoryActivity.java:110-112')
    e('CategoryActivity.onColorChooserDismissed@' + v, 'CategoryActivity.onColorChooserDismissed', 'CALL', 'onColorChooserDismissed(dialog)', evidence='SRC CategoryActivity.java:110-112')
    gui(p, 'CategoryActivity_ViewBinding$2.doClick@' + v, 'Tap Save', evidence='SRC CategoryActivity.java:135-160')
    sv = 'CategoryActivity.saveCategory@' + v
    e('CategoryActivity_ViewBinding$2.doClick@' + v, sv, 'CALL', 'target.saveCategory()', evidence='INFERRED ButterKnife DebouncingOnClickListener forwards the click to the generated listener (ButterKnife source not read); SRC CategoryActivity.java:135-160')
    clone_auto('CategoryActivity.saveCategory', sv)
    if v == 'NEW_DETAIL':
        e(sv, 'DetailFragment.onActivityResult', 'RESULT', 'result OK with the category (request CATEGORY)', evidence='SRC CategoryActivity.java:156-158; DetailFragment.java:1438-1443')
        e(sv, 'S_DETAIL@NEW', 'ENTERS', 'the category is set on the note', evidence='SRC DetailFragment.java:1438-1443')
        gui(p, 'DetailFragment.onActivityResult', 'Press Back', kind='SYSTEM', evidence='SRC DetailFragment.java:1408-1451')
        e(p, 'S_DETAIL@NEW', 'ENTERS', 'Press Back: CategoryActivity finishes with RESULT_CANCELED', gui=['Press Back'], evidence=BACK_ACT)
    else:
        e(sv, 'ListFragment.onActivityResult@' + ('SAVED' if v == 'EDIT' else 'ADD_CATEGORY'), 'RESULT', 'result OK with the category', evidence='SRC CategoryActivity.java:156-158; ListFragment.java:955-993')
        e(sv, 'S_LIST@NOTES', 'ENTERS', 'the list shows "category saved"', evidence='SRC ListFragment.java:962-965')
        e(p, 'S_LIST@NOTES', 'ENTERS', 'Press Back: CategoryActivity finishes with RESULT_CANCELED', gui=['Press Back'], evidence=BACK_ACT)
        e(p, 'ListFragment.onActivityResult@CANCEL', 'RESULT', 'result of CategoryActivity (cancelled)', evidence='SRC ListFragment.java:955-993')
e('S_CATEGORY@EDIT', 'CategoryActivity_ViewBinding$3.doClick', 'GUI', 'Tap Delete', gui=['Tap Delete'], evidence='SRC CategoryActivity.java:162-188')
e('CategoryActivity_ViewBinding$3.doClick', 'CategoryActivity.deleteCategory', 'CALL', 'target.deleteCategory()', evidence='INFERRED ButterKnife DebouncingOnClickListener forwards the click to the generated listener (ButterKnife source not read); SRC CategoryActivity.java:162-165')
e('CategoryActivity.deleteCategory', 'S_DLG_DELETE_CATEGORY', 'ENTERS', 'the confirmation opens', evidence='SRC CategoryActivity.java:165-188')
gui('S_DLG_DELETE_CATEGORY', 'CategoryActivity.lambda$deleteCategory$0', 'Tap Confirm', evidence=FW_MD + '; SRC CategoryActivity.java:170-187')
e('CategoryActivity.lambda$deleteCategory$0', 'S_LIST@NOTES', 'ENTERS', 'the category is deleted and the list shows "category deleted"', evidence='SRC CategoryActivity.java:175-187')
e('CategoryActivity.lambda$deleteCategory$0', 'ListFragment.onActivityResult@DELETED', 'RESULT', 'RESULT_FIRST_USER', evidence='SRC CategoryActivity.java:185-186; ListFragment.java:966-968')
e('S_DLG_DELETE_CATEGORY', 'S_CATEGORY@EDIT', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
# ---- password dialogs, one page variant per caller
PWD = {  # key -> (caller node, state, validator lambda, page after SUCCESS, page after FAIL/cancel)
    'APP_ACCESS': ('MainActivity.checkPassword', NEED_PWD_ACCESS, 'MainActivity.lambda$checkPassword$0', 'S_LIST@NOTES', 'S_EXIT'),
    'OPEN_NOTE': ('ListFragment.editNote', NEED_LOCKED, 'ListFragment.lambda$editNote$7', 'S_DETAIL@EDIT', 'S_LIST@NOTES'),
    'EMPTY_TRASH_DIALOG': (None, NEED_LOCKED, 'ListFragment$3.lambda$onClick$0', 'S_LIST@TRASH', 'S_LIST@TRASH'),
    'DELETE_NOTES': (None, NEED_LOCKED, 'ListFragment.lambda$null$11', 'S_LIST@TRASH', 'S_LIST@TRASH'),
    'CAB': (None, NEED_LOCKED, 'ListFragment$ModeCallback.lambda$onActionItemClicked$0', 'S_LIST@NOTES', 'S_LIST@NOTES'),
    'DETAIL_OPEN': ('DetailFragment.checkNoteLock', NEED_LOCKED, 'DetailFragment.lambda$checkNoteLock$1', 'S_DETAIL@EDIT', 'S_LIST@NOTES'),
    'DETAIL_LOCK': ('DetailFragment.lockNote', NEED_PWD, 'DetailFragment.lambda$lockNote$20', 'S_DETAIL@EDIT', 'S_DETAIL@EDIT'),
    'PWD_REMOVE': ('PasswordActivity.lambda$initViews$1', NEED_PWD, 'PasswordActivity.lambda$null$0', 'S_PASSWORD@SET_SETTINGS', 'S_PASSWORD@SET_SETTINGS'),
    'PWD_CONFIRM': ('PasswordActivity.lambda$initViews$3', NEED_PWD, 'PasswordActivity.lambda$null$2', 'S_PASSWORD@SET_SETTINGS', 'S_PASSWORD@SET_SETTINGS'),
    'SETTINGS_ACCESS': ('SettingsFragment.lambda$onResume$12', NEED_PWD, 'SettingsFragment.lambda$null$11', 'S_SETTINGS_DATA', 'S_SETTINGS_DATA'),
    'SWIPE': (None, NEED_LOCKED, 'ListFragment.lambda$null$9', 'S_LIST_UNDO@ARCHIVE', 'S_LIST@NOTES'),
}
sup(('MainActivity.checkPassword', 'PasswordHelper.requestPassword'), ('ListFragment.editNote', 'PasswordHelper.requestPassword'), ('DetailFragment.checkNoteLock', 'PasswordHelper.requestPassword'),
    ('DetailFragment.lockNote', 'PasswordHelper.requestPassword'), ('ListFragment.lambda$onEvent$10', 'PasswordHelper.requestPassword'),
    ('PasswordActivity.lambda$initViews$1', 'PasswordHelper.requestPassword'), ('PasswordActivity.lambda$initViews$3', 'PasswordHelper.requestPassword'),
    ('SettingsFragment.lambda$onResume$12', 'PasswordHelper.requestPassword'))
for k, (cal, need, lam, ok_page, fail_page) in PWD.items():
    pg = 'S_DLG_PASSWORD@' + k
    if cal:
        e(cal, pg, 'ENTERS', 'PasswordHelper.requestPassword opens the password dialog', needs_state=need, evidence='SRC utils/PasswordHelper.java:49-102')
        e(cal, 'PasswordHelper.requestPassword', 'CALL', 'PasswordHelper.requestPassword(activity, validator)', needs_state=need, evidence='SRC utils/PasswordHelper.java:49-102')
    gui(pg, lam, 'Type the password and tap OK', needs_state=None, evidence='SRC utils/PasswordHelper.java:58-76')
    gui(pg, 'PasswordHelper.lambda$requestPassword$0@' + k, 'Type the password and tap OK', evidence='SRC utils/PasswordHelper.java:58-76')
    gui(pg, 'PasswordHelper.lambda$requestPassword$3@' + k, 'Press Done on the keyboard', evidence='SRC utils/PasswordHelper.java:91-98')
    gui(pg, 'PasswordHelper.lambda$requestPassword$1@' + k, 'Tap "Forgot password"', evidence='SRC utils/PasswordHelper.java:77-83')
    gui(pg, 'PasswordHelper.lambda$requestPassword$2@' + k, 'Press Back (cancel)', evidence='SRC utils/PasswordHelper.java:85-89')
    e('PasswordHelper.lambda$requestPassword$3@' + k, 'PasswordHelper.lambda$requestPassword$0@' + k, 'CALL', 'callOnClick on the positive button', evidence='SRC utils/PasswordHelper.java:91-96')
    e(lam, ok_page, 'ENTERS', 'the password was accepted', evidence='SRC utils/PasswordHelper.java:68-72')
    if fail_page != ok_page:
        e('PasswordHelper.lambda$requestPassword$2@' + k, fail_page, 'ENTERS', 'the dialog was cancelled (FAIL)', evidence='SRC utils/PasswordHelper.java:85-89')
        e('PasswordHelper.lambda$requestPassword$2@' + k, lam, 'CALL', 'validator.onPasswordValidated(FAIL)', evidence='SRC utils/PasswordHelper.java:88')
    e('PasswordHelper.lambda$requestPassword$1@' + k, 'S_DLG_PASSWORD_RESET', 'ENTERS', 'resetPassword shows the security question', evidence='SRC utils/PasswordHelper.java:78-81')
    e('PasswordHelper.lambda$requestPassword$1@' + k, lam, 'CALL', 'validator.onPasswordValidated(RESTORE)', evidence='SRC utils/PasswordHelper.java:80')
    e('PasswordHelper.lambda$requestPassword$0@' + k, lam, 'CALL', 'validator.onPasswordValidated(SUCCEED)', evidence='SRC utils/PasswordHelper.java:71')
e('PasswordHelper.requestPassword', 'PasswordHelper.lambda$requestPassword$4', 'ASYNC', 'new Handler().postDelayed(show the keyboard, 100)', evidence=FW_POST + '; SRC utils/PasswordHelper.java:101')
e('PasswordHelper.resetPassword', 'PasswordHelper.lambda$resetPassword$7', 'ASYNC', 'new Handler().postDelayed(show the keyboard, 100)', evidence=FW_POST + '; SRC utils/PasswordHelper.java:138')
gui('S_DLG_PASSWORD_RESET', 'PasswordHelper.lambda$resetPassword$5', 'Answer the security question and tap OK', evidence=FW_MD + '; SRC utils/PasswordHelper.java:115-127')
gui('S_DLG_PASSWORD_RESET', 'PasswordHelper.lambda$resetPassword$6', 'Press Done on the keyboard', evidence='SRC utils/PasswordHelper.java:130-136')
e('PasswordHelper.lambda$resetPassword$5', 'PasswordHelper.removePassword', 'CALL', 'removePassword()', evidence='SRC utils/PasswordHelper.java:123')
e('PasswordHelper.lambda$resetPassword$5', 'S_LIST@NOTES', 'ENTERS', 'the password is removed and all notes are unlocked', evidence='SRC utils/PasswordHelper.java:121-124')
e('PasswordHelper.lambda$resetPassword$6', 'PasswordHelper.lambda$resetPassword$5', 'CALL', 'callOnClick on the positive button', evidence='SRC utils/PasswordHelper.java:131-133')
e('PasswordHelper.resetPassword', 'S_DLG_PASSWORD_RESET', 'ENTERS', 'the dialog opens', needs_state=NEED_PWD, evidence='SRC utils/PasswordHelper.java:105-139')
e('PasswordHelper.removePassword', 'PasswordHelper.lambda$removePassword$8', 'ASYNC', 'Rx doOnNext for each locked note on a new thread', needs_state=NEED_LOCKED, evidence=FW_ASYNC + '; SRC utils/PasswordHelper.java:143-150')
e('PasswordHelper.removePassword', 'PasswordHelper.lambda$removePassword$9', 'ASYNC', 'Rx doOnCompleted on the main thread', evidence=FW_ASYNC + '; SRC utils/PasswordHelper.java:151-160')
e('PasswordHelper.lambda$removePassword$9', 'ListFragment.onEvent(PasswordRemovedEvent)', 'FRAMEWORK', 'PasswordRemovedEvent', evidence=FW_EB + '; SRC utils/PasswordHelper.java:158')
e('PasswordHelper.lambda$removePassword$9', 'MainActivity.onEvent', 'FRAMEWORK', 'PasswordRemovedEvent (MainActivity unregisters in onStop)', needs_state='MainActivity has not been stopped since it was created', evidence=FW_EB + '; SRC MainActivity.java:98,124,159')
e('PasswordHelper.lambda$removePassword$9', 'PasswordActivity.onEvent', 'FRAMEWORK', 'PasswordRemovedEvent (PasswordActivity is registered between onStart and onStop)', needs_state='PasswordActivity is open', evidence=FW_EB + '; SRC PasswordActivity.java:70-80,130')
e('ListFragment.onEvent(PasswordRemovedEvent)', 'ListFragment.initNotesList', 'CALL', 'reload', evidence='SRC ListFragment.java:1244-1246')


# ================================================================== B. note editor (DetailFragment)
DVARS = ('NEW', 'EDIT', 'CHECKLIST', 'ARCHIVED', 'TRASHED')
NEED_MERGED = 'The open note is the result of Merge (opened from the CAB with two or more notes selected)'
NEED_CHANGED = 'The note was changed (text, title, attachment, category, reminder or lock)'
for cb in ('onAttach', 'onCreate', 'onCreateView', 'onActivityCreated', 'onResume', 'onCreateOptionsMenu', 'onPrepareOptionsMenu'):
    e('DetailFragment.<init>', 'DetailFragment.' + cb, 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC DetailFragment.java:326-435,1005-1037')
e('DetailFragment.<init>', 'BaseFragment.onStart', 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC BaseFragment.java:32-35')
e('DetailFragment.<init>', 'DetailFragment_ViewBinding.<init>', 'FRAMEWORK', 'ButterKnife.bind(this, view)', evidence=FW_BIND + '; SRC DetailFragment.java:353')
sup(('DetailFragment.onActivityCreated', 'DetailFragment.addAttachment'), ('DetailFragment.onActivityCreated', 'Attachment.<init>(Uri,String)'), ('DetailFragment.init', 'DetailFragment.checkNoteLock'))
e('DetailFragment.init', 'DetailFragment.checkNoteLock', 'CALL', 'a locked note must be unlocked first', needs_state=NEED_LOCKED, evidence='SRC DetailFragment.java:461-464')
# intents that start the editor (share, widget, shortcut, notification): the conditional calls of handleIntents
HI = {'DetailFragment.takePhoto': ('Opened with the camera action (FAB camera, widget camera button)', None),
      'DetailFragment.importAttachments': ('Opened by a share intent', ENV_EXT), 'DbHelper.getNote': ('Opened from a shortcut or a reminder notification', ENV_LAUNCHER),
      'DbHelper.getCategory': ('Opened from a widget bound to a category', ENV_LAUNCHER), 'Note.setCategory': ('Opened from a widget bound to a category', ENV_LAUNCHER),
      'TextHelper.checkIntentCategory': ('Opened from a widget', ENV_LAUNCHER), 'BaseActivity.showToast': ('The shortcut note was deleted', ENV_LAUNCHER)}
for dst, (need, env) in HI.items():
    sup(('DetailFragment.handleIntents', dst))
    e('DetailFragment.handleIntents', dst, 'CALL', 'branch for a specific start intent', needs_state=need, env=env, evidence='SRC DetailFragment.java:500-592')
e('DetailFragment.handleIntents', 'Note.<init>(Note)', 'CALL', 'noteTmp = new Note(...)', evidence='SRC DetailFragment.java:454-459')
# ---- Back / Up arrow in the editor: empty new note, unchanged existing note, changed note
sup('MainActivity.onBackPressed', 'DetailFragment.saveAndExit', 'DetailFragment.saveNote', 'DetailFragment.goHome', 'DetailFragment.archiveNote', 'DetailFragment.trashNote', 'DetailFragment.toggleChecklist')
for pg in DVARS:
    if pg == 'NEW':
        gui('S_DETAIL@NEW', 'MainActivity.onBackPressed@DETAIL_EMPTY', 'Press Back without writing anything', evidence='SRC MainActivity.java:271-276; DetailFragment.java:1559-1573')
    else:
        gui('S_DETAIL@' + pg, 'MainActivity.onBackPressed@DETAIL_UNCHANGED', 'Press Back without changing the note', evidence='SRC MainActivity.java:271-276; DetailFragment.java:1575-1581')
    gui('S_DETAIL@' + pg, 'MainActivity.onBackPressed@DETAIL_SAVE', 'Change the note (type text or add something), then press Back', evidence='SRC MainActivity.java:271-276; DetailFragment.java:1583-1587')
    gui('S_DETAIL@' + pg, 'DetailFragment.lambda$onActivityCreated$0@' + ('EMPTY' if pg == 'NEW' else 'UNCHANGED'), 'Tap the Up arrow without changing the note', evidence='SRC DetailFragment.java:366,1144-1148')
    gui('S_DETAIL@' + pg, 'DetailFragment.lambda$onActivityCreated$0@SAVE', 'Change the note, then tap the Up arrow', evidence='SRC DetailFragment.java:366,1144-1148')
for kind in ('EMPTY', 'UNCHANGED', 'SAVE'):
    ob = 'MainActivity.onBackPressed@DETAIL_' + kind
    e(ob, 'MainActivity.checkFragmentInstance', 'CALL', 'which fragment is shown', evidence='SRC MainActivity.java:258-279')
    e(ob, 'DetailFragment.saveAndExit@' + kind, 'CALL', 'goBack = true; saveAndExit(fragment)', evidence='SRC MainActivity.java:271-276')
    up = 'DetailFragment.lambda$onActivityCreated$0@' + kind
    e(up, 'DetailFragment.navigateUp', 'CALL', 'navigateUp()', evidence='SRC DetailFragment.java:366,1144-1148')
    e('DetailFragment.navigateUp', 'DetailFragment.saveAndExit@' + kind, 'CALL', 'saveAndExit(this)', evidence='SRC DetailFragment.java:1144-1148')
    se = 'DetailFragment.saveAndExit@' + kind
    e(se, 'DetailFragment.saveNote@' + kind, 'CALL', 'saveNote(listener)', evidence='SRC DetailFragment.java:1547-1553')
    sn = 'DetailFragment.saveNote@' + kind
    for dst in ('DetailFragment.getNoteTitle', 'DetailFragment.getNoteContent', 'LogDelegate.d'):
        e(sn, dst, 'CALL', 'call in saveNote', evidence='SRC DetailFragment.java:1559-1587')
    e(sn, 'DetailFragment.goHome', 'CALL', 'goHome() (nothing to save)' if kind != 'SAVE' else 'goHome()', guard='empty note' if kind == 'EMPTY' else None, evidence='SRC DetailFragment.java:1566-1581')
    if kind == 'UNCHANGED':
        e(sn, 'DetailFragment.saveNotNeeded', 'CALL', 'saveNotNeeded()', evidence='SRC DetailFragment.java:1575')
    if kind == 'SAVE':
        e(sn, 'DetailFragment.saveNotNeeded', 'CALL', 'saveNotNeeded()', evidence='SRC DetailFragment.java:1575')
        e(sn, 'DetailFragment.lastModificationUpdatedNeeded', 'CALL', 'lastModificationUpdatedNeeded()', evidence='SRC DetailFragment.java:1585')
        e(sn, 'SaveNoteTask.<init>(OnNoteSaved,boolean)', 'CALL', 'new SaveNoteTask(listener, ...)', evidence='SRC DetailFragment.java:1585')
        e(sn, 'SaveNoteTask.doInBackground', 'ASYNC', 'executeOnExecutor(noteTmp)', evidence=FW_ASYNC + '; SRC DetailFragment.java:1585-1586')
e('SaveNoteTask.<init>(boolean)', 'SaveNoteTask.doInBackground', 'ASYNC', 'executeOnExecutor(note)', evidence=FW_ASYNC + '; SRC SnoozeActivity.java:63,74')
e('SaveNoteTask.doInBackground', 'SaveNoteTask.onPostExecute', 'ASYNC', 'the saved note is delivered on the main thread', evidence=FW_ASYNC + '; SRC async/notes/SaveNoteTask.java:100-106')
e('SaveNoteTask.<init>(OnNoteSaved,boolean)', 'SaveNoteTask.doInBackground', 'ASYNC', 'executeOnExecutor(note)', evidence=FW_ASYNC + '; SRC DetailFragment.java:1491,1585')
sup(('DetailFragment.onNoteSaved', 'DetailFragment.deleteMergedNotes'), ('DetailFragment.onNoteSaved', 'ReminderHelper.showReminderMessage'))
e('DetailFragment.onNoteSaved', 'DetailFragment.deleteMergedNotes', 'CALL', 'the merged source notes are deleted', needs_state=NEED_MERGED, evidence='SRC DetailFragment.java:1616')
e('DetailFragment.onNoteSaved', 'ReminderHelper.showReminderMessage', 'CALL', 'toast "alarm set on ..."', needs_state='A reminder was set or changed on the note', evidence='SRC DetailFragment.java:1617-1619')
e('SaveNoteTask.doInBackground', 'ReminderHelper.addReminder(Context,Note)', 'CALL', 'the reminder is in the future: schedule the alarm', needs_state=NEED_REMINDER, evidence='SRC async/notes/SaveNoteTask.java:58-65')
sup(('SaveNoteTask.doInBackground', 'ReminderHelper.addReminder(Context,Note)'))
# goHome: back to the list, or finish the activity when the editor was started from outside
e('DetailFragment.goHome', 'S_LIST@NOTES', 'ENTERS', 'the editor is popped and the list is shown again', guard='afterSavedReturnsToList', evidence='SRC DetailFragment.java:1052-1068')
e('DetailFragment.goHome', 'S_EXIT', 'ENTERS', 'the activity finishes: the editor was started from a widget, shortcut, share or notification', guard='!afterSavedReturnsToList', needs_state='The editor was opened from a widget, shortcut, share or notification', env=ENV_LAUNCHER, evidence='SRC DetailFragment.java:1045-1049')
sup(('DetailFragment.goHome', 'MainActivity.getDrawerToggle'), ('DetailFragment.goHome', 'SwitchFragmentEvent.<init>'), ('DetailFragment.goHome', 'BaseActivity.showToast'), ('DetailFragment.goHome', 'MainActivity.showMessage(String,Style)'))
for dst in ('MainActivity.getDrawerToggle', 'SwitchFragmentEvent.<init>', 'MainActivity.showMessage(String,Style)'):
    e('DetailFragment.goHome', dst, 'CALL', 'back to the list: burger icon, event, exit message', guard='afterSavedReturnsToList', evidence='SRC DetailFragment.java:1052-1068')
e('DetailFragment.goHome', 'BaseActivity.showToast', 'CALL', 'exit message as a toast when started from outside', needs_state='The editor was opened from a widget, shortcut, share or notification', env=ENV_LAUNCHER, evidence='SRC DetailFragment.java:1045-1049')
e('DetailFragment.goHome', 'ListFragment.onCreateView', 'FRAMEWORK', 'popBackStack recreates the list fragment view', evidence=FW_FRAG + '; SRC DetailFragment.java:1058-1060')
e('DetailFragment.goHome', 'ListFragment.onActivityCreated', 'FRAMEWORK', 'popBackStack recreates the list fragment view', evidence=FW_FRAG + '; SRC DetailFragment.java:1058-1060')
# leaving the app with the editor open saves the note
for pg in DVARS:
    gui('S_DETAIL@' + pg, 'DetailFragment.onPause', 'Press Home', kind='SYSTEM', evidence='SRC DetailFragment.java:417-434')
e('DetailFragment.onPause', 'DetailFragment.saveNote@SAVE', 'CALL', 'saveNote(this) when the editor is not closing', guard='!goBack', needs_state=NEED_CHANGED, evidence='SRC DetailFragment.java:426-428')
sup(('DetailFragment.onPause', 'DetailFragment.saveNote'))
e('DetailFragment.onPause', 'DetailFragment.onStop', 'SYSTEM', 'the activity stops', evidence='SRC DetailFragment.java:338-341')
e('DetailFragment.onStop', 'S_MAIN_PAUSED', 'ENTERS', 'the app is in the background', evidence='SRC DetailFragment.java:338-341')
for pg in DVARS:
    gui('S_DETAIL@' + pg, 'DetailFragment.onSaveInstanceState', 'Rotate the device or press Home', kind='SYSTEM', evidence='SRC DetailFragment.java:403-414')
# ---- toolbar menu of the editor
DM = {'ATTACHMENT': ('Attachment', 'DetailFragment.showAttachmentsPopup', DVARS), 'TAG': ('Tags', 'DetailFragment.addTags', DVARS), 'CATEGORY': ('Category', 'DetailFragment.categorizeNote', DVARS),
      'SHARE': ('Share', 'DetailFragment.shareNote', DVARS), 'CHECKLIST_ON': ('Checklist on', 'DetailFragment.toggleChecklist@ON', ('NEW', 'EDIT', 'ARCHIVED', 'TRASHED')),
      'CHECKLIST_OFF': ('Checklist off', 'DetailFragment.toggleChecklist@OFF', ('CHECKLIST',)), 'LOCK': ('Lock', 'DetailFragment.lockNote', DVARS),
      'ARCHIVE': ('Archive', 'DetailFragment.archiveNote@ARCHIVE', ('EDIT', 'CHECKLIST')), 'UNARCHIVE': ('Unarchive', 'DetailFragment.archiveNote@UNARCHIVE', ('ARCHIVED',)),
      'TRASH': ('Trash', 'DetailFragment.trashNote@TRASH', ('EDIT', 'CHECKLIST', 'ARCHIVED')), 'UNTRASH': ('Restore from trash', 'DetailFragment.trashNote@UNTRASH', ('TRASHED',)),
      'DELETE': ('Delete', 'DetailFragment.deleteNote', ('TRASHED',)), 'DISCARD': ('Discard changes', 'DetailFragment.discard', ('NEW',)), 'DISCARD_X': ('Discard changes', 'DetailFragment.discard@EXIST', ('EDIT', 'CHECKLIST', 'ARCHIVED', 'TRASHED')), 'NOTE_INFO': ('Info', 'DetailFragment.showNoteInfo', DVARS)}
sup('DetailFragment.onOptionsItemSelected')
for it, (lab, tgt_node, pages) in DM.items():
    oi = 'DetailFragment.onOptionsItemSelected@' + it
    for pg in pages:
        gui('S_DETAIL@' + pg, oi, 'Tap "%s" in the toolbar menu' % lab, needs_state=NEED_EXISTING if it in ('ARCHIVE', 'TRASH', 'DISCARD_X') and pg == 'CHECKLIST' else None,
            evidence='SRC DetailFragment.java:1074-1132,1033-1036; res/menu/menu_detail.xml')
    for dst in ('BaseFragment.isOptionsItemFastClick', 'OmniNotes.getAnalyticsHelper'):
        e(oi, dst, 'CALL', 'call in onOptionsItemSelected', evidence='SRC DetailFragment.java:1076,1129')
    e(oi, tgt_node, 'CALL', 'the %s branch of the menu switch' % it.lower(), evidence='SRC DetailFragment.java:1080-1127')
gui('S_DETAIL@EDIT', 'DetailFragment.onOptionsItemSelected@UNLOCK', 'Tap "Unlock" in the toolbar menu', needs_state=NEED_LOCKED, evidence='SRC DetailFragment.java:1023-1024,1097-1100')
e('DetailFragment.onOptionsItemSelected@UNLOCK', 'DetailFragment.lockNote', 'CALL', 'the unlock branch', evidence='SRC DetailFragment.java:1097-1100')
e('DetailFragment.onOptionsItemSelected@UNLOCK', 'BaseFragment.isOptionsItemFastClick', 'CALL', 'debounce', evidence='SRC DetailFragment.java:1076')
# targets of the menu
e('DetailFragment.showAttachmentsPopup', 'S_DLG_ATTACH', 'ENTERS', 'the attachment popup opens', evidence='SRC DetailFragment.java:1279-1315')
e('DetailFragment.showNoteInfo', 'NoteInfosActivity.<init>', 'INTENT', 'startActivity(NoteInfosActivity)', evidence='SRC DetailFragment.java:1135-1141')
e('NoteInfosActivity.<init>', 'NoteInfosActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC NoteInfosActivity.java:61-67')
e('NoteInfosActivity.onCreate', 'S_NOTE_INFO', 'ENTERS', 'the statistics dialog is shown', evidence='SRC NoteInfosActivity.java:61-67')
e('NoteInfosActivity.onCreate', 'NoteInfosActivity_ViewBinding.<init>(NoteInfosActivity,View)', 'FRAMEWORK', 'ButterKnife.bind(this)', evidence=FW_BIND + '; SRC NoteInfosActivity.java:64')
gui('S_NOTE_INFO', 'DetailFragment.onResume', 'Press Back', kind='SYSTEM', evidence='SRC NoteInfosActivity.java')
e('S_NOTE_INFO', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog activity finishes', gui=['Press Back'], evidence=BACK_ACT)
e('DetailFragment.shareNote', 'S_EXT_APP', 'ENTERS', 'the system share chooser opens', env=ENV_PICKER, evidence='SRC MainActivity.java:462-511')
# tags
sup(('DetailFragment.addTags', 'TagsHelper.getPreselectedTagsArray(Note,List)'), ('DetailFragment.addTags', 'TagsHelper.getTagsArray'), ('DetailFragment.addTags', 'Note.<init>()'))
for dst in ('TagsHelper.getPreselectedTagsArray(Note,List)', 'TagsHelper.getTagsArray', 'Note.<init>()'):
    e('DetailFragment.addTags', dst, 'CALL', 'builds the tag dialog', needs_state=NEED_TAGS, evidence='SRC DetailFragment.java:2056-2065')
e('DetailFragment.addTags', 'S_DLG_TAGS_DETAIL', 'ENTERS', 'the tags dialog opens', needs_state=NEED_TAGS, evidence='SRC DetailFragment.java:2062-2071')
gui('S_DLG_TAGS_DETAIL', 'DetailFragment.lambda$addTags$23', 'Tick tags and tap OK', evidence=FW_MD + '; SRC DetailFragment.java:2066-2070')
e('DetailFragment.lambda$addTags$23', 'DetailFragment.tagNote', 'CALL', 'tagNote(tags, which, note)', evidence='SRC DetailFragment.java:2068')
e('DetailFragment.lambda$addTags$23', 'S_DETAIL@NEW', 'ENTERS', 'the tag text is added to the note', evidence='SRC DetailFragment.java:2066-2070')
e('S_DLG_TAGS_DETAIL', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
# categories
sup(('DetailFragment.categorizeNote', 'RecyclerViewItemClickSupport.addTo'))
e('DetailFragment.categorizeNote', 'S_DLG_CATEGORIZE_DETAIL', 'ENTERS', 'the categorize dialog opens', evidence='SRC DetailFragment.java:1242-1276')
e('DetailFragment.categorizeNote', 'DetailFragment.lambda$categorizeNote$14', 'CALL', 'Observable.from(categories).map(...) runs per category', needs_state=NEED_CATEGORY, evidence='SRC DetailFragment.java:1245-1250')
e('DetailFragment.categorizeNote', 'RecyclerViewItemClickSupport.addTo', 'CALL', 'click support for the dialog list', evidence='SRC DetailFragment.java:1269')
for cb in ('onCreateViewHolder', 'onBindViewHolder'):
    e('DetailFragment.categorizeNote', 'CategoryRecyclerViewAdapter.' + cb, 'FRAMEWORK', 'the dialog RecyclerView binds the category rows', needs_state=NEED_CATEGORY, evidence=FW_VIEW + '; SRC DetailFragment.java:1254')
e('DetailFragment.categorizeNote', 'CategoryRecyclerViewAdapter.getItemCount', 'FRAMEWORK', 'the dialog RecyclerView asks for the row count', evidence=FW_VIEW + '; SRC DetailFragment.java:1254')
e('DetailFragment.categorizeNote', 'RecyclerViewItemClickSupport$3.onChildViewAttachedToWindow', 'FRAMEWORK', 'rows attach: click listeners are installed', needs_state=NEED_CATEGORY, evidence=FW_VIEW + '; SRC models/listeners/RecyclerViewItemClickSupport.java')
e('S_DLG_CATEGORIZE_DETAIL', 'DetailFragment.lambda$categorizeNote$15', 'GUI', 'Tap "Add category"', gui=['Tap "Add category"'], evidence=FW_MD + '; SRC DetailFragment.java:1259-1263')
e('DetailFragment.lambda$categorizeNote$15', 'S_CATEGORY@NEW_DETAIL', 'ENTERS', 'startActivityForResult(CategoryActivity, CATEGORY)', evidence='SRC DetailFragment.java:1260-1263')
gui('S_DLG_CATEGORIZE_DETAIL', 'DetailFragment.lambda$categorizeNote$16', 'Tap "Remove category"', evidence=FW_MD + '; SRC DetailFragment.java:1264-1267')
e('DetailFragment.lambda$categorizeNote$16', 'DetailFragment.setTagMarkerColor', 'CALL', 'setTagMarkerColor(null)', evidence='SRC DetailFragment.java:1266')
e('DetailFragment.lambda$categorizeNote$16', 'S_DETAIL@NEW', 'ENTERS', 'the category is removed from the note', evidence='SRC DetailFragment.java:1264-1267')
gui('S_DLG_CATEGORIZE_DETAIL', 'RecyclerViewItemClickSupport$1.onClick@DETAIL_CAT', 'Tap a category', needs_state=NEED_CATEGORY, evidence='SRC models/listeners/RecyclerViewItemClickSupport.java; DetailFragment.java:1269-1273')
e('RecyclerViewItemClickSupport$1.onClick@DETAIL_CAT', 'DetailFragment.lambda$categorizeNote$17', 'CALL', 'OnItemClickListener.onItemClick', evidence='SRC DetailFragment.java:1269-1273')
e('DetailFragment.lambda$categorizeNote$17', 'DetailFragment.setTagMarkerColor', 'CALL', 'setTagMarkerColor(category)', evidence='SRC DetailFragment.java:1271')
e('DetailFragment.lambda$categorizeNote$17', 'S_DETAIL@NEW', 'ENTERS', 'the note gets the category', evidence='SRC DetailFragment.java:1270-1273')
e('S_DLG_CATEGORIZE_DETAIL', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
# checklist
sup('DetailFragment.toggleChecklist')
e('DetailFragment.toggleChecklist@ON', 'DetailFragment.toggleChecklist2()', 'CALL', 'toggleChecklist2() turns the text into a checklist', evidence='SRC DetailFragment.java:1156-1159')
e('DetailFragment.toggleChecklist@ON', 'S_DETAIL@CHECKLIST', 'ENTERS', 'the note is shown as a checklist', evidence='SRC DetailFragment.java:1197-1237')
e('DetailFragment.toggleChecklist@OFF', 'DetailFragment.toggleChecklist2(boolean,boolean)', 'CALL', 'no item is checked: toggleChecklist2(true, false)', evidence='SRC DetailFragment.java:1163-1166')
e('DetailFragment.toggleChecklist@OFF', 'S_DETAIL@NEW', 'ENTERS', 'the note is shown as text again', evidence='SRC DetailFragment.java:1163-1166')
e('DetailFragment.toggleChecklist@OFF', 'DetailFragment$3.<init>', 'CALL', 'builds the keep-checked dialog', needs_state=NEED_CHECKED, evidence='SRC DetailFragment.java:1169-1191')
e('DetailFragment.toggleChecklist@OFF', 'S_DLG_REMOVE_CHECKLIST', 'ENTERS', 'checked items exist: the options dialog opens', needs_state=NEED_CHECKED, evidence='SRC DetailFragment.java:1169-1191')
gui('S_DLG_REMOVE_CHECKLIST', 'DetailFragment$3.onClick', 'Tap OK', evidence=FW_MD + '; SRC DetailFragment.java:1182-1190')
e('DetailFragment$3.onClick', 'DetailFragment.toggleChecklist2()', 'CALL', 'toggleChecklist2()', evidence='SRC DetailFragment.java:1189')
e('DetailFragment$3.onClick', 'S_DETAIL@NEW', 'ENTERS', 'the note is shown as text', evidence='SRC DetailFragment.java:1182-1190')
e('DetailFragment.toggleChecklist2(boolean,boolean)', 'DetailFragment.onCheckListChanged', 'FRAMEWORK', 'ChecklistManager reports changes', needs_state='The checklist was edited', evidence=FW_VIEW + '; SRC DetailFragment.java:1218-1220,2025-2027')
gui('S_DETAIL@CHECKLIST', 'DetailFragment.onCheckListChanged', 'Edit, add or check a checklist item', kind='GUI', evidence='SRC DetailFragment.java:2025-2027')
# lock / unlock
sup(('DetailFragment.lockNote', 'DetailFragment.lockUnlock'), ('DetailFragment.lockNote', 'Note.isPasswordChecked'))
e('DetailFragment.lockNote', 'PasswordActivity.<init>', 'INTENT', 'no password yet: startActivityForResult(PasswordActivity, SET_PASSWORD)', guard='prefs.password == null', evidence='SRC DetailFragment.java:1684-1688')
e('DetailFragment.lockNote', 'S_PASSWORD@UNSET_DETAIL', 'ENTERS', 'the password screen opens', guard='prefs.password == null', evidence='SRC DetailFragment.java:1684-1688')
e('DetailFragment.lockNote', 'DetailFragment.lockUnlock', 'CALL', 'the password was already confirmed or access is global', needs_state=NEED_PWD, evidence='SRC DetailFragment.java:1691-1694')
e('DetailFragment.lockNote', 'Note.isPasswordChecked', 'CALL', 'isPasswordChecked()', needs_state=NEED_PWD, evidence='SRC DetailFragment.java:1691')
e('DetailFragment.lockUnlock', 'S_DETAIL@NEW', 'ENTERS', 'the lock flag toggles ("save the note to lock it")', evidence='SRC DetailFragment.java:1708-1721')
e('DetailFragment.onActivityResult', 'DetailFragment.lockUnlock', 'CALL', 'result of the password screen', evidence='SRC DetailFragment.java:1428-1431')
sup(('DetailFragment.onActivityResult', 'DetailFragment.lockUnlock'), ('DetailFragment.onActivityResult', 'Attachment.<init>(Uri,String)'), ('DetailFragment.onActivityResult', 'DetailFragment.addAttachment'),
    ('DetailFragment.onActivityResult', 'DetailFragment.onActivityResultManageReceivedFiles'), ('DetailFragment.onActivityResult', 'ExpandableHeightGridView.autoresize'),
    ('DetailFragment.onActivityResult', 'DetailFragment.setTagMarkerColor'), ('DetailFragment.onActivityResult', 'Note.setCategory'), ('DetailFragment.onActivityResult', 'Note.setPasswordChecked'))


# ---- permissions (PermissionsHelper): the callback is a lambda, so every caller reaches its own callback
ENV_PERM = 'the runtime-permission dialog of the system must be answered (outside the package)'
NEED_PERM_DENIED = 'The permission was denied earlier (the rationale snackbar shows) or is not granted yet'
sup(('PermissionsHelper.requestPermission', 'PermissionsHelper.requestPermissionExecute'))
e('PermissionsHelper.requestPermission', 'PermissionsHelper.requestPermissionExecute', 'CALL', 'the permission is not granted: ask for it', needs_state=NEED_PERM_DENIED, env=ENV_PERM, evidence='SRC helpers/PermissionsHelper.java:40-54')
e('PermissionsHelper.requestPermission', 'PermissionsHelper.lambda$requestPermission$0', 'FRAMEWORK', 'The user taps OK on the rationale snackbar', needs_state=NEED_PERM_DENIED, env=ENV_PERM, evidence='SRC helpers/PermissionsHelper.java:42-46')
e('PermissionsHelper.lambda$requestPermission$0', 'PermissionsHelper.requestPermissionExecute', 'CALL', 'requestPermissionExecute(...)', env=ENV_PERM, evidence='SRC helpers/PermissionsHelper.java:44')
e('PermissionsHelper.requestPermissionExecute', 'PermissionsHelper.lambda$requestPermissionExecute$1', 'ASYNC', 'RxPermissions delivers the user answer', env=ENV_PERM, evidence=FW_ASYNC + '; SRC helpers/PermissionsHelper.java:58-67')
# ---- results of external activities (camera, video, document picker, password screen, category)
for k, cal in (('PHOTO', 'DetailFragment.takePhoto'), ('VIDEO', 'DetailFragment.takeVideo')):
    e(cal, 'S_EXT_CAMERA', 'ENTERS', 'startActivityForResult(%s)' % k.lower(), env=ENV_PICKER, evidence='SRC DetailFragment.java:1317-1357')
    e('S_EXT_CAMERA', 'DetailFragment.onActivityResult@' + k, 'RESULT', 'the %s result comes back (RESULT_OK)' % k.lower(), env=ENV_PICKER, evidence='SRC DetailFragment.java:1408-1424')
    for dst in ('DetailFragment.addAttachment', 'Attachment.<init>(Uri,String)', 'ExpandableHeightGridView.autoresize'):
        e('DetailFragment.onActivityResult@' + k, dst, 'CALL', 'the picture/video is attached', env=ENV_PICKER, evidence='SRC DetailFragment.java:1413-1424')
    e('DetailFragment.onActivityResult@' + k, 'S_DETAIL@NEW', 'ENTERS', 'back in the editor with the new attachment', env=ENV_PICKER, evidence='SRC DetailFragment.java:1408-1424')
e('S_EXT_CAMERA', 'DetailFragment.onActivityResult@CANCEL', 'RESULT', 'The user leaves the camera app with Back (or no camera app handles the intent): RESULT_CANCELED', evidence=RES_CANCEL + '; SRC DetailFragment.java:1408-1411')
e('S_EXT_CAMERA', 'S_DETAIL@NEW', 'ENTERS', 'Press Back from the camera', gui=['Press Back in the camera app'], evidence=BACK_EXT)
e('DetailFragment.startGetContentAction', 'S_EXT_PICKER@FILES', 'ENTERS', 'startActivityForResult(ACTION_GET_CONTENT)', env=ENV_PICKER, evidence='SRC DetailFragment.java:2147-2154')
e('S_EXT_PICKER@FILES', 'DetailFragment.onActivityResult@FILES', 'RESULT', 'files were chosen', env=ENV_PICKER, evidence='SRC DetailFragment.java:1425-1427')
e('DetailFragment.onActivityResult@FILES', 'DetailFragment.onActivityResultManageReceivedFiles', 'CALL', 'the chosen files are imported', env=ENV_PICKER, evidence='SRC DetailFragment.java:1426,1453-1466')
e('DetailFragment.onActivityResultManageReceivedFiles', 'AttachmentTask.doInBackground', 'ASYNC', 'new AttachmentTask(...).executeOnExecutor(...)', env=ENV_PICKER, evidence=FW_ASYNC + '; SRC DetailFragment.java:1462-1465')
e('AttachmentTask.doInBackground', 'AttachmentTask.onPostExecute', 'ASYNC', 'the attachment is delivered on the main thread', evidence=FW_ASYNC + '; SRC async/AttachmentTask.java:53-76')
e('DetailFragment.onActivityResult@FILES', 'S_DETAIL@NEW', 'ENTERS', 'back in the editor', env=ENV_PICKER, evidence='SRC DetailFragment.java:1408-1427')
e('S_EXT_PICKER@FILES', 'DetailFragment.onActivityResult@CANCEL', 'RESULT', 'The user leaves the picker with Back: RESULT_CANCELED', evidence=RES_CANCEL + '; SRC DetailFragment.java:1408-1411')
e('S_EXT_PICKER@FILES', 'S_DETAIL@NEW', 'ENTERS', 'Press Back in the picker', gui=['Press Back in the picker'], evidence=BACK_EXT)
e('S_PASSWORD@UNSET_DETAIL', 'DetailFragment.onActivityResult@PASSWORD', 'RESULT', 'PasswordActivity finishes with RESULT_OK (opened from the editor Lock item)', evidence='SRC PasswordActivity.java:243-246; DetailFragment.java:1428-1431')
e('DetailFragment.onActivityResult@PASSWORD', 'Note.setPasswordChecked', 'CALL', 'setPasswordChecked(true)', evidence='SRC DetailFragment.java:1429')
e('DetailFragment.onActivityResult@PASSWORD', 'DetailFragment.lockUnlock', 'CALL', 'lockUnlock()', evidence='SRC DetailFragment.java:1430')
e('DetailFragment.onActivityResult@PASSWORD', 'S_DETAIL@NEW', 'ENTERS', 'back in the editor', evidence='SRC DetailFragment.java:1428-1431')
sv = 'CategoryActivity.saveCategory@NEW_DETAIL'
e(sv, 'DetailFragment.onActivityResult@CATEGORY', 'RESULT', 'result OK with the category', evidence='SRC DetailFragment.java:1438-1443')
for dst in ('MainActivity.showMessage(int,Style)', 'Note.setCategory', 'DetailFragment.setTagMarkerColor'):
    e('DetailFragment.onActivityResult@CATEGORY', dst, 'CALL', 'the category is set on the note', evidence='SRC DetailFragment.java:1438-1443')
# ---- attachment popup
sup('DetailFragment$AttachmentOnClickListener.onClick')
sup(('DetailFragment.showAttachmentsPopup', 'DetailFragment.toggleAudioRecordingStop'))
e('DetailFragment.showAttachmentsPopup', 'DetailFragment.toggleAudioRecordingStop', 'CALL', 'toggleAudioRecordingStop(row)', evidence='SRC DetailFragment.java:1294')
AK = [('CAMERA', 'Camera', 'DetailFragment.takePhoto'), ('VIDEO', 'Video', 'DetailFragment.takeVideo'), ('SKETCH', 'Sketch', 'DetailFragment.takeSketch'),
      ('LOCATION', 'Location', 'DetailFragment.displayLocationDialog'), ('TIMESTAMP', 'Timestamp', 'DetailFragment.addTimestamp'), ('PUSHBULLET', 'Pushbullet', 'DetailFragment.getNoteContent')]
for k, lab, tgt in AK:
    gui('S_DLG_ATTACH', 'DetailFragment$AttachmentOnClickListener.onClick@' + k, 'Tap "%s" in the attachment popup' % lab, evidence='SRC DetailFragment.java:2267-2320')
    e('DetailFragment$AttachmentOnClickListener.onClick@' + k, tgt, 'CALL', 'the %s branch' % k.lower(), evidence='SRC DetailFragment.java:2272-2315')
    if k not in ('CAMERA', 'VIDEO', 'SKETCH'):
        e('DetailFragment$AttachmentOnClickListener.onClick@' + k, 'S_DETAIL@NEW', 'ENTERS', 'the popup closes', evidence='SRC DetailFragment.java:2319-2321')
e('DetailFragment$AttachmentOnClickListener.onClick@PUSHBULLET', 'DetailFragment.getNoteContent', 'CALL', 'mirrorMessage(...) with the note content', env=ENV_HOSTAPP, evidence='SRC DetailFragment.java:2309-2315')
gui('S_DLG_ATTACH', 'DetailFragment$AttachmentOnClickListener.onClick@FILES', 'Tap "Files" in the attachment popup', evidence='SRC DetailFragment.java:2292-2299')
e('DetailFragment$AttachmentOnClickListener.onClick@FILES', 'DetailFragment.startGetContentAction', 'CALL', 'storage permission granted: open the document picker', needs_state=NEED_PERM_STORAGE, evidence='SRC DetailFragment.java:2293-2295')
e('DetailFragment$AttachmentOnClickListener.onClick@FILES', 'DetailFragment.askReadExternalStoragePermission', 'CALL', 'storage permission missing: ask for it', needs_state=NEED_PERM_DENIED, env=ENV_PERM, evidence='SRC DetailFragment.java:2296-2298')
e('DetailFragment.askReadExternalStoragePermission', 'PermissionsHelper.requestPermission', 'CALL', 'requestPermission(READ_EXTERNAL_STORAGE)', evidence='SRC DetailFragment.java:2157')
e('DetailFragment.askReadExternalStoragePermission', 'DetailFragment.startGetContentAction', 'CALL', 'once granted, the picker opens', needs_state=NEED_PERM_DENIED, env=ENV_PERM, evidence='SRC DetailFragment.java:2159')
gui('S_DLG_ATTACH', 'DetailFragment$AttachmentOnClickListener.onClick@RECORD_START', 'Tap "Recording" in the attachment popup', evidence='SRC DetailFragment.java:2277-2281')
e('DetailFragment$AttachmentOnClickListener.onClick@RECORD_START', 'DetailFragment.startRecording', 'CALL', 'startRecording(view)', evidence='SRC DetailFragment.java:2279')
e('DetailFragment.startRecording', 'DetailFragment.lambda$startRecording$22', 'CALL', 'RECORD_AUDIO is granted: the recording starts', needs_state=NEED_PERM_AUDIO, env=ENV_MIC, evidence='SRC DetailFragment.java:1808-1838')
e('DetailFragment.lambda$startRecording$22', 'S_DLG_ATTACH@REC', 'ENTERS', 'recording: the popup stays open and shows "Stop"', evidence='SRC DetailFragment.java:1811-1813,2319-2321')
gui('S_DLG_ATTACH@REC', 'DetailFragment$AttachmentOnClickListener.onClick@RECORD_STOP', 'Tap "Stop" in the attachment popup', evidence='SRC DetailFragment.java:2277-2288')
for dst in ('DetailFragment.stopRecording', 'Attachment.<init>(Uri,String)', 'DetailFragment.addAttachment', 'ExpandableHeightGridView.autoresize'):
    e('DetailFragment$AttachmentOnClickListener.onClick@RECORD_STOP', dst, 'CALL', 'the recording is attached', evidence='SRC DetailFragment.java:2281-2286')
e('DetailFragment$AttachmentOnClickListener.onClick@RECORD_STOP', 'S_DETAIL@NEW', 'ENTERS', 'the popup closes', evidence='SRC DetailFragment.java:2319-2321')
e('DetailFragment.takeSketch', 'S_SKETCH@EMPTY', 'ENTERS', 'the sketch editor replaces the editor', evidence='SRC DetailFragment.java:1360-1384')
e('S_DLG_ATTACH', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the popup is dismissed', gui=['Press Back'], evidence=BACK_DLG)
# ---- text, reminder, location, attachments grid of the editor
for pg in DVARS:
    p = 'S_DETAIL@' + pg
    gui(p, 'DetailFragment.onTextChanged', 'Type in the note', evidence='SRC DetailFragment.java:2010-2023')
    gui(p, 'DetailFragment.lambda$initViewTitle$13', 'Press Next on the keyboard in the title', evidence='SRC DetailFragment.java:879-883')
    gui(p, 'DetailFragment.lambda$initViewTitle$12', 'Drag text (selected in the note, then long-press the selection and drag) or a checklist item over the title field: its OnDragListener consumes the drag events',
        needs_state='Some text is selected in the note content', evidence=FW_VIEW + '; SRC DetailFragment.java:871-874')
    gui(p, 'DetailFragment.onTouch', 'Touch the editor (an edge swipe opens a new note)', evidence='SRC DetailFragment.java:1903-1953')
    gui(p, 'DetailFragment$1.onTextLinkClick', 'Tap a link, e-mail or #hashtag in the text', needs_state=NEED_LINK, evidence='SRC DetailFragment.java:273-322')
    gui(p, 'DetailFragment.lambda$initViewReminder$2', 'Tap the reminder row', evidence='SRC DetailFragment.java:657-661')
    gui(p, 'DetailFragment.lambda$initViewReminder$4', 'Long-press the reminder row', evidence='SRC DetailFragment.java:663-675')
    gui(p, 'DetailFragment.lambda$initViewLocation$5', 'Tap the location text', needs_state=NEED_LOCATION, evidence='SRC DetailFragment.java:704-714')
    gui(p, 'DetailFragment.lambda$initViewLocation$6', 'Long-press the location text', needs_state=NEED_LOCATION, evidence='SRC DetailFragment.java:715-730')
    gui(p, 'DetailFragment.lambda$initViewAttachments$10', 'Long-press an attachment', needs_state=NEED_ATTACH, evidence='SRC DetailFragment.java:809-827')
e('DetailFragment.onTouch', 'DetailFragment.<init>', 'CALL', 'an edge swipe replaces the editor with a new DetailFragment', needs_state='The swipe starts within 30 px of the screen edge and moves 100 px', evidence='SRC DetailFragment.java:1916-1944')
e('DetailFragment.onTouch', 'S_DETAIL@NEW', 'ENTERS', 'a new empty note is opened', needs_state='The swipe starts within 30 px of the screen edge and moves 100 px', evidence='SRC DetailFragment.java:1933-1944')
e('DetailFragment$1.onTextLinkClick', 'S_DLG_LINK', 'ENTERS', 'the Open / Copy dialog opens', evidence='SRC DetailFragment.java:273-322')
e('DetailFragment$1.onTextLinkClick', 'DetailFragment$1.lambda$onTextLinkClick$2', 'ASYNC', 'new Handler().post(hide the keyboard)', evidence=FW_POST + '; SRC DetailFragment.java:317-320')
gui('S_DLG_LINK', 'DetailFragment$1.lambda$onTextLinkClick$0', 'Tap Open', evidence=FW_MD + '; SRC DetailFragment.java:281-305')
gui('S_DLG_LINK', 'DetailFragment$1.lambda$onTextLinkClick$1', 'Tap Copy', evidence=FW_MD + '; SRC DetailFragment.java:306-313')
e('DetailFragment$1.lambda$onTextLinkClick$0', 'S_EXT_APP', 'ENTERS', 'startActivity(ACTION_VIEW) opens the link in another app', env=ENV_PICKER, evidence='SRC DetailFragment.java:303')
e('DetailFragment$1.lambda$onTextLinkClick$1', 'S_DETAIL@NEW', 'ENTERS', 'the text is copied to the clipboard', evidence='SRC DetailFragment.java:306-313')
e('S_DLG_LINK', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('DetailFragment.lambda$initViewReminder$2', 'S_REMINDER_PICKER@DETAIL', 'ENTERS', 'the date / time / recurrence picker opens', evidence='SRC DetailFragment.java:657-661; utils/date/ReminderPickers.java:43-88')
e('DetailFragment.lambda$initViewReminder$4', 'S_DLG_REMOVE_REMINDER', 'ENTERS', 'the confirmation opens', evidence='SRC DetailFragment.java:663-675')
gui('S_DLG_REMOVE_REMINDER', 'DetailFragment.lambda$null$3', 'Tap OK', evidence=FW_MD + '; SRC DetailFragment.java:667-672')
e('DetailFragment.lambda$null$3', 'S_DETAIL@NEW', 'ENTERS', 'the reminder is removed from the note', evidence='SRC DetailFragment.java:667-672')
e('S_DLG_REMOVE_REMINDER', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('DetailFragment.lambda$initViewLocation$5', 'S_EXT_APP', 'ENTERS', 'startActivity(geo: / maps link)', env=ENV_PICKER, evidence='SRC DetailFragment.java:704-714')
e('DetailFragment.lambda$initViewLocation$6', 'S_DLG_REMOVE_LOCATION', 'ENTERS', 'the confirmation opens', evidence='SRC DetailFragment.java:715-730')
gui('S_DLG_REMOVE_LOCATION', 'DetailFragment$2.onClick', 'Tap OK', evidence=FW_MD + '; SRC DetailFragment.java:719-725')
e('DetailFragment$2.onClick', 'DetailFragment.fade', 'CALL', 'fade(locationTextView, false)', evidence='SRC DetailFragment.java:724')
e('DetailFragment$2.onClick', 'S_DETAIL@NEW', 'ENTERS', 'the location is removed from the note', evidence='SRC DetailFragment.java:719-725')
e('S_DLG_REMOVE_LOCATION', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('DetailFragment.fade', 'DetailFragment$4.onAnimationStart', 'FRAMEWORK', 'the fade animation starts', evidence=FW_VIEW + '; SRC DetailFragment.java:1873-1889')
e('DetailFragment.fade', 'DetailFragment$4.onAnimationEnd', 'FRAMEWORK', 'the fade animation ends', evidence=FW_VIEW + '; SRC DetailFragment.java:1873-1889')
# attachments grid: tap by attachment type, long-press actions
sup('DetailFragment.lambda$initViewAttachments$8')
for k, (text, need, tg) in {'FILE': ('Tap a file attachment', NEED_FILE, 'S_EXT_APP'), 'MEDIA': ('Tap an image, sketch or video attachment', NEED_IMAGE, 'S_GALLERY'),
                            'AUDIO': ('Tap an audio attachment', NEED_AUDIO, None)}.items():
    v = 'DetailFragment.lambda$initViewAttachments$8@' + k
    for pg in DVARS:
        gui('S_DETAIL@' + pg, v, text, needs_state=need, evidence='SRC DetailFragment.java:757-806')
    e(v, 'Attachment.getUri', 'CALL', 'attachment.getUri()', evidence='SRC DetailFragment.java:758-766')
    if k == 'FILE':
        for dst in ('FileProviderHelper.getShareableUri', 'StorageHelper.getMimeType(Context,Uri)', 'IntentChecker.isAvailable'):
            e(v, dst, 'CALL', 'call in the grid click handler', evidence='SRC DetailFragment.java:759-770')
        e(v, 'S_EXT_APP', 'ENTERS', 'startActivity(ACTION_VIEW) opens the file in another app', env=ENV_PICKER, evidence='SRC DetailFragment.java:763-770')
    if k == 'MEDIA':
        for dst in ('DetailFragment.getNoteTitle', 'DetailFragment.getNoteContent', 'TextHelper.parseTitleAndContent', 'Note.getAttachmentsList', 'FileProviderHelper.getShareableUri'):
            e(v, dst, 'CALL', 'call in the grid click handler', evidence='SRC DetailFragment.java:777-801')
        e(v, 'GalleryActivity.<init>', 'INTENT', 'startActivity(GalleryActivity)', evidence='SRC DetailFragment.java:797-801')
    if k == 'AUDIO':
        e(v, 'DetailFragment.playback', 'CALL', 'playback(view, uri)', evidence='SRC DetailFragment.java:803-805')
        e(v, 'S_DETAIL@NEW', 'ENTERS', 'the recording plays', evidence='SRC DetailFragment.java:1739-1757')
e('DetailFragment.startPlaying', 'DetailFragment.lambda$startPlaying$21', 'ASYNC', 'MediaPlayer completion listener', env=ENV_MIC, evidence=FW_VIEW + '; SRC DetailFragment.java:1780-1787')
e('DetailFragment.lambda$initViewAttachments$10', 'S_DLG_ATTACHMENT_ACTIONS', 'ENTERS', 'the attachment actions dialog opens', needs_state=NEED_ATTACH, evidence='SRC DetailFragment.java:809-827')
for dst in ('AttachmentAdapter.getItem', 'AttachmentsHelper.getSize'):
    e('DetailFragment.lambda$initViewAttachments$10', dst, 'CALL', 'call in the long-click handler', evidence='SRC DetailFragment.java:818-820')
sup('DetailFragment.performAttachmentAction')
PA = {'SHARE': ('Share', 'Tap "Share"', ['IntentChecker.isAvailable', 'FileProviderHelper.getShareableUri', 'StorageHelper.getMimeType(Context,Uri)', 'Attachment.getUri', 'OmniNotes.getAppContext', 'AttachmentAdapter.getItem']),
      'DELETE': ('Delete', 'Tap "Delete"', ['DetailFragment.removeAttachment(int)', 'ExpandableHeightGridView.autoresize']), 'DELETE_ALL': ('Delete all', 'Tap "Delete all"', []),
      'EDIT': ('Edit', 'Tap "Edit"', ['DetailFragment.takeSketch', 'AttachmentAdapter.getItem'])}
for k, (lab, text, calls) in PA.items():
    pa = 'DetailFragment.performAttachmentAction@' + k
    need = NEED_SKETCH if k == 'EDIT' else None
    gui('S_DLG_ATTACHMENT_ACTIONS', 'DetailFragment.lambda$null$9@' + k, text, needs_state=need, evidence=FW_MD + '; SRC DetailFragment.java:819-826')
    e('DetailFragment.lambda$null$9@' + k, pa, 'CALL', 'performAttachmentAction(position, i)', evidence='SRC DetailFragment.java:822-823')
    for dst in calls:
        e(pa, dst, 'CALL', 'the %s branch' % k.lower(), evidence='SRC DetailFragment.java:836-866')
e('DetailFragment.performAttachmentAction@SHARE', 'S_EXT_APP', 'ENTERS', 'the share intent opens another app', env=ENV_PICKER, evidence='SRC DetailFragment.java:838-846')
e('DetailFragment.performAttachmentAction@DELETE', 'S_DETAIL@NEW', 'ENTERS', 'the attachment is removed', evidence='SRC DetailFragment.java:848-852')
e('DetailFragment.performAttachmentAction@DELETE_ALL', 'S_DLG_DELETE_ALL_ATTACHMENTS', 'ENTERS', 'the confirmation opens', evidence='SRC DetailFragment.java:853-860')
gui('S_DLG_DELETE_ALL_ATTACHMENTS', 'DetailFragment.lambda$performAttachmentAction$11', 'Tap Confirm', evidence=FW_MD + '; SRC DetailFragment.java:856-858')
e('DetailFragment.lambda$performAttachmentAction$11', 'DetailFragment.removeAllAttachments', 'CALL', 'removeAllAttachments()', evidence='SRC DetailFragment.java:857')
e('DetailFragment.lambda$performAttachmentAction$11', 'S_DETAIL@NEW', 'ENTERS', 'all attachments are removed', evidence='SRC DetailFragment.java:856-858')
e('S_DLG_DELETE_ALL_ATTACHMENTS', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('DetailFragment.performAttachmentAction@EDIT', 'S_SKETCH@EMPTY', 'ENTERS', 'the sketch is opened for editing', evidence='SRC DetailFragment.java:861-863')
e('S_DLG_ATTACHMENT_ACTIONS', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('DetailFragment.initViewAttachments', 'AttachmentAdapter.getCount', 'FRAMEWORK', 'GridView reads the attachment count', evidence=FW_VIEW + '; SRC DetailFragment.java:753')
for cb in ('getView', 'getItemId'):
    e('DetailFragment.initViewAttachments', 'AttachmentAdapter.' + cb, 'FRAMEWORK', 'GridView binds the attachment cells', needs_state=NEED_ATTACH, evidence=FW_VIEW + '; SRC DetailFragment.java:753')
# the editor's action items that stay in place


# ---- sketch editor (S_SKETCH@EMPTY: nothing drawn yet; S_SKETCH@DRAWN: at least one stroke; Back saves only a drawn sketch, SketchView.getBitmap() is null for an empty canvas)
for cb in ('onCreate', 'onCreateView', 'onActivityCreated', 'onStart'):
    e('SketchFragment.<init>', 'SketchFragment.' + cb, 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC SketchFragment.java:80-130')
e('SketchFragment.<init>', 'SketchFragment_ViewBinding.<init>', 'FRAMEWORK', 'ButterKnife.bind(this, view)', evidence=FW_BIND + '; SRC SketchFragment.java:99')
e('SketchFragment.onCreateView', 'SketchView.<init>', 'FRAMEWORK', 'the layout inflates the SketchView', evidence='FW-SRC core/java/android/view/LayoutInflater.java:612-617, 645-648 (createView looks up the (Context, AttributeSet) constructor of the view class and calls newInstance); SRC res/layout/fragment_sketch.xml')
sup('SketchFragment.lambda$onActivityCreated$0', 'SketchFragment.lambda$onActivityCreated$1', 'SketchFragment.lambda$onActivityCreated$2')
for pg in ('EMPTY', 'DRAWN'):
    sp = 'S_SKETCH@' + pg
    for cb in ('onMeasure', 'onDraw'):
        e(sp, 'SketchView.' + cb, 'FRAMEWORK', 'layout and draw passes of the canvas', evidence=FW_VIEW + '; SRC models/views/SketchView.java')
    gui(sp, 'SketchView.onTouch', 'Draw on the canvas', evidence='SRC models/views/SketchView.java')
    gui(sp, 'SketchFragment.lambda$onActivityCreated$1@POPUP_' + pg, 'Tap the stroke icon', evidence='SRC SketchFragment.java:129-137')
    gui(sp, 'SketchFragment.lambda$onActivityCreated$2@MODE_' + pg, 'Tap the eraser icon (selects the eraser)', evidence='SRC SketchFragment.java:140-148')
    gui(sp, 'SketchFragment.lambda$onActivityCreated$2@POPUP_' + pg, 'Tap the eraser icon again', needs_state='The eraser is already selected', evidence='SRC SketchFragment.java:141-143')
    gui(sp, 'SketchFragment.lambda$onActivityCreated$1@MODE_' + pg, 'Tap the stroke icon (selects the stroke)', needs_state='The eraser is selected', evidence='SRC SketchFragment.java:132-136')
    gui(sp, 'SketchFragment.lambda$onActivityCreated$3', 'Tap undo', evidence='SRC SketchFragment.java:150')
    gui(sp, 'SketchFragment.lambda$onActivityCreated$4', 'Tap redo', evidence='SRC SketchFragment.java:152')
    gui(sp, 'SketchFragment$1.onClick', 'Tap erase', evidence='SRC SketchFragment.java:154-165')
    gui(sp, 'SketchFragment.lambda$onActivityCreated$0@UP_' + pg, 'Tap the Up arrow', evidence='SRC SketchFragment.java:107')
    gui(sp, 'MainActivity.onBackPressed@SKETCH_' + pg, 'Press Back', evidence='SRC MainActivity.java:255-269')
    e('SketchFragment.lambda$onActivityCreated$0@UP_' + pg, 'MainActivity.onBackPressed@SKETCH_' + pg, 'CALL', 'getActivity().onBackPressed()', evidence='SRC SketchFragment.java:107')
    for dst in ('SketchView.getMode', 'SketchFragment.showPopup'):
        e('SketchFragment.lambda$onActivityCreated$1@POPUP_' + pg, dst, 'CALL', 'call in the stroke click handler', evidence='SRC SketchFragment.java:129-137')
        e('SketchFragment.lambda$onActivityCreated$2@POPUP_' + pg, dst, 'CALL', 'call in the eraser click handler', evidence='SRC SketchFragment.java:140-148')
    for v in ('SketchFragment.lambda$onActivityCreated$1@MODE_' + pg, 'SketchFragment.lambda$onActivityCreated$2@MODE_' + pg):
        for dst in ('SketchView.getMode', 'SketchView.setMode'):
            e(v, dst, 'CALL', 'call in the click handler', evidence='SRC SketchFragment.java:129-148')
    e('SketchFragment.lambda$onActivityCreated$1@POPUP_' + pg, 'S_SKETCH_POPUP@STROKE_' + pg, 'ENTERS', 'the stroke popup opens', evidence='SRC SketchFragment.java:131,231-287')
    e('SketchFragment.lambda$onActivityCreated$2@POPUP_' + pg, 'S_SKETCH_POPUP@ERASER_' + pg, 'ENTERS', 'the eraser popup opens', evidence='SRC SketchFragment.java:142,231-287')
    # popups return to the page they came from
    for k in ('STROKE', 'ERASER'):
        pp = 'S_SKETCH_POPUP@%s_%s' % (k, pg)
        for cb in ('onProgressChanged', 'onStartTrackingTouch', 'onStopTrackingTouch'):
            gui(pp, 'SketchFragment$2.' + cb, 'Drag the size slider', evidence='SRC SketchFragment.java:264-286')
        gui(pp, 'SketchFragment.lambda$showPopup$5@' + pg, 'Tap outside the popup', evidence='SRC SketchFragment.java:246-252')
        e('SketchFragment.lambda$showPopup$5@' + pg, 'SketchFragment.lambda$showPopup$5', 'CALL', 'onDismiss', evidence='SRC SketchFragment.java:246-252')
        e('SketchFragment.lambda$showPopup$5@' + pg, sp, 'ENTERS', 'the popup closes', evidence='SRC SketchFragment.java:246-252')
    gui('S_SKETCH_POPUP@STROKE_' + pg, 'SketchView.setStrokeColor', 'Pick a stroke colour', evidence='SRC SketchFragment.java:189-194')
    # erase
for dst in ('SketchFragment$1.askForErase',):
    e('SketchFragment$1.onClick', dst, 'CALL', 'askForErase()', evidence='SRC SketchFragment.java:156-157')
e('SketchFragment$1.askForErase', 'S_DLG_ERASE_SKETCH', 'ENTERS', 'the confirmation opens', evidence='SRC SketchFragment.java:160-165')
e('SketchView.onTouch', 'S_SKETCH@DRAWN', 'ENTERS', 'a stroke is added to the canvas', evidence='SRC models/views/SketchView.java:165-185,260-280')
e('SketchView.onTouch', 'SketchFragment.onDrawChanged', 'CALL', 'OnDrawChangedListener.onDrawChanged()', evidence='SRC models/views/SketchView.java; SketchFragment.java:312-326')
gui('S_DLG_ERASE_SKETCH', 'SketchFragment$1.lambda$askForErase$0', 'Tap Confirm', evidence=FW_MD + '; SRC SketchFragment.java:163-164')
e('SketchFragment$1.lambda$askForErase$0', 'SketchView.erase', 'CALL', 'mSketchView.erase()', evidence='SRC SketchFragment.java:164')
e('SketchFragment$1.lambda$askForErase$0', 'S_SKETCH@EMPTY', 'ENTERS', 'the canvas is cleared', evidence='SRC SketchFragment.java:163-164')
e('S_DLG_ERASE_SKETCH', 'S_SKETCH@DRAWN', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('SketchFragment.showPopup', 'SketchFragment$2.<init>', 'CALL', 'installs the seek bar listener', evidence='SRC SketchFragment.java:264')
e('SketchFragment.lambda$onActivityCreated$3', 'SketchView.undo', 'CALL', 'mSketchView.undo()', evidence='SRC SketchFragment.java:150')
e('SketchFragment.lambda$onActivityCreated$4', 'SketchView.redo', 'CALL', 'mSketchView.redo()', evidence='SRC SketchFragment.java:152')
e('SketchFragment$2.onProgressChanged', 'SketchFragment.setSeekbarProgress', 'CALL', 'setSeekbarProgress(progress, mode)', evidence='SRC SketchFragment.java:278-283')
for pg in ('EMPTY', 'DRAWN'):
    ob = 'MainActivity.onBackPressed@SKETCH_' + pg
    for dst in ('MainActivity.checkFragmentInstance', 'SketchFragment.save', 'MainActivity.getFragmentManagerInstance'):
        e(ob, dst, 'CALL', 'Back in the sketch editor saves and pops it', evidence='SRC MainActivity.java:255-269')
    for cb in ('onCreateView', 'onActivityCreated', 'onResume'):
        e(ob, 'DetailFragment.' + cb, 'FRAMEWORK', 'popBackStack recreates the editor view', evidence=FW_FRAG + '; SRC MainActivity.java:266')
    e(ob, 'S_DETAIL@NEW', 'ENTERS', 'back in the editor' + (' with the sketch attached' if pg == 'DRAWN' else ' (an empty canvas is not saved)'), evidence='SRC MainActivity.java:258-269')
for dst in ('DetailFragment.addAttachment', 'Attachment.<init>(Uri,String)'):
    e('MainActivity.onBackPressed@SKETCH_DRAWN', dst, 'CALL', 'DetailFragment.onActivityCreated attaches the saved sketch (mainActivity.sketchUri)', guard='SketchView.getBitmap() != null (at least one stroke was drawn)', evidence='SRC SketchFragment.java:208-226; models/views/SketchView.java:204-207; DetailFragment.java:385-388')
# ---- gallery
e('GalleryActivity.<init>', 'GalleryActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC GalleryActivity.java:118-125')
e('GalleryActivity.<init>', 'GalleryActivity.onStart', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC GalleryActivity.java:127-131')
e('GalleryActivity.onCreate', 'S_GALLERY', 'ENTERS', 'the gallery pager is shown', evidence='SRC GalleryActivity.java:118-125')
e('GalleryActivity.onCreate', 'GalleryActivity_ViewBinding.<init>(GalleryActivity,View)', 'FRAMEWORK', 'ButterKnife.bind(this)', evidence=FW_BIND + '; SRC GalleryActivity.java:121')
sup(('GalleryActivity.initData', 'GalleryActivity.viewMedia'), ('GalleryActivity$1.click', 'GalleryActivity.viewMedia'))
e('GalleryActivity.initData', 'GalleryActivity.viewMedia', 'CALL', 'a video starts in the viewer at once', needs_state='The clicked attachment is a video', env=ENV_PICKER, evidence='SRC GalleryActivity.java:189-191')
e('GalleryActivity$1.click', 'GalleryActivity.viewMedia', 'CALL', 'a tap on a video opens the viewer', needs_state='The current gallery item is a video', env=ENV_PICKER, evidence='SRC GalleryActivity.java:109-113')
e('S_GALLERY', 'GalleryActivity.onCreateOptionsMenu', 'FRAMEWORK', 'the gallery menu is inflated', evidence=FW_VIEW + '; SRC GalleryActivity.java:134-138')
gui('S_GALLERY', 'GalleryActivity$1.onViewTouchOccurred', 'Touch the image', evidence='SRC GalleryActivity.java:77-107')
gui('S_GALLERY', 'InterceptorFrameLayout.onInterceptTouchEvent', 'Touch the image', evidence='SRC models/views/InterceptorFrameLayout.java; GalleryActivity.java:147')
e('InterceptorFrameLayout.onInterceptTouchEvent', 'GalleryActivity$1.onViewTouchOccurred', 'CALL', 'OnViewTouchedListener.onViewTouchOccurred', evidence='SRC models/views/InterceptorFrameLayout.java; GalleryActivity.java:85')
for cb in ('onPageSelected', 'onPageScrolled', 'onPageScrollStateChanged'):
    gui('S_GALLERY', 'GalleryActivity$2.' + cb, 'Swipe to another image', needs_state='The gallery has two or more images', evidence='SRC GalleryActivity.java:149-168')
gui('S_GALLERY', 'GalleryActivity.onOptionsItemSelected@SHARE', 'Tap Share in the gallery menu', evidence='SRC GalleryActivity.java:195-209')
gui('S_GALLERY', 'GalleryActivity.onOptionsItemSelected@VIEW', 'Tap "Open with" in the gallery menu', evidence='SRC GalleryActivity.java:195-209')
gui('S_GALLERY', 'GalleryActivity.onOptionsItemSelected@HOME', 'Tap the Up arrow', evidence='SRC GalleryActivity.java:195-209')
sup('GalleryActivity.onOptionsItemSelected')
e('GalleryActivity.onOptionsItemSelected@SHARE', 'GalleryActivity.shareMedia', 'CALL', 'shareMedia()', evidence='SRC GalleryActivity.java:200-202')
e('GalleryActivity.onOptionsItemSelected@VIEW', 'GalleryActivity.viewMedia', 'CALL', 'viewMedia()', evidence='SRC GalleryActivity.java:203-205')
e('GalleryActivity.onOptionsItemSelected@HOME', 'S_DETAIL@NEW', 'ENTERS', 'the gallery finishes', evidence='SRC GalleryActivity.java:197-199')
e('GalleryActivity.shareMedia', 'S_EXT_APP', 'ENTERS', 'startActivity(ACTION_SEND)', env=ENV_PICKER, evidence='SRC GalleryActivity.java:221-226')
e('GalleryActivity.viewMedia', 'S_EXT_APP', 'ENTERS', 'startActivity(ACTION_VIEW)', env=ENV_PICKER, evidence='SRC GalleryActivity.java:212-218')
gui('S_GALLERY', 'DetailFragment.onResume', 'Press Back', kind='SYSTEM', evidence='SRC GalleryActivity.java')
e('S_GALLERY', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the gallery finishes', gui=['Press Back'], evidence=BACK_ACT)
e('S_EXT_APP', 'MainActivity.onResume', 'SYSTEM', 'Return from the other app', gui=['Press Back in the other app'], evidence='SRC MainActivity.java:111-118')
# ---- reminder picker and SnoozeActivity
e('ReminderPickers.pick', 'ReminderPickers.showDateTimeSelectors', 'CALL', 'showDateTimeSelectors(...)', evidence='SRC utils/date/ReminderPickers.java:43-48')
e('ReminderPickers.showDateTimeSelectors', 'SublimePickerFragment.onCreateView', 'FRAMEWORK', 'pickerFrag.show(...) builds the picker view', evidence=FW_FRAG + '; SRC utils/date/ReminderPickers.java:88')
for v in ('DETAIL', 'SNOOZE'):
    pg = 'S_REMINDER_PICKER@' + v
    gui(pg, 'SublimePickerFragment$1.onDateTimeRecurrenceSet', 'Pick a date and time and tap OK', evidence='SRC utils/date/SublimePickerFragment.java:55-65')
    gui(pg, 'ReminderPickers$1.onDateTimeRecurrenceSet@' + v, 'Pick a date and time and tap OK', evidence='SRC utils/date/ReminderPickers.java:60-69')
    gui(pg, 'SublimePickerFragment$1.onCancelled', 'Tap Cancel', evidence='SRC utils/date/SublimePickerFragment.java:47-52')
sup(('ReminderPickers$1.onDateTimeRecurrenceSet', 'DetailFragment.onReminderPicked'), ('ReminderPickers$1.onDateTimeRecurrenceSet', 'DetailFragment.onRecurrenceReminderPicked'),
    ('ReminderPickers$1.onDateTimeRecurrenceSet', 'SnoozeActivity.onReminderPicked'), ('ReminderPickers$1.onDateTimeRecurrenceSet', 'SnoozeActivity.onRecurrenceReminderPicked'))
for v, cls in (('DETAIL', 'DetailFragment'), ('SNOOZE', 'SnoozeActivity')):
    n = 'ReminderPickers$1.onDateTimeRecurrenceSet@' + v
    for cb in ('onReminderPicked', 'onRecurrenceReminderPicked'):
        e(n, cls + '.' + cb, 'CALL', 'OnReminderPickedListener.%s' % cb, evidence='SRC utils/date/ReminderPickers.java:65-67')
    e(n, 'RecurrenceHelper.buildRecurrenceRuleByRecurrenceOptionAndRule', 'CALL', 'builds the recurrence rule', evidence='SRC utils/date/ReminderPickers.java:66-67')
e('ReminderPickers$1.onDateTimeRecurrenceSet@DETAIL', 'S_DETAIL@NEW', 'ENTERS', 'the picker closes and the editor shows the reminder', evidence='SRC DetailFragment.java:1992-2008')
e('ReminderPickers$1.onDateTimeRecurrenceSet@SNOOZE', 'S_LIST@NOTES', 'ENTERS', 'SnoozeActivity finishes and the list is shown', evidence='SRC SnoozeActivity.java:127-150')
e('SublimePickerFragment$1.onCancelled', 'ReminderPickers$1.onCancelled', 'CALL', 'mCallback.onCancelled()', evidence='SRC utils/date/SublimePickerFragment.java:47-52')
e('SublimePickerFragment$1.onCancelled', 'S_DETAIL@NEW', 'ENTERS', 'the picker closes', evidence='SRC utils/date/SublimePickerFragment.java:47-52')
e('SublimePickerFragment$1.onDateTimeRecurrenceSet', 'ReminderPickers$1.onDateTimeRecurrenceSet', 'CALL', 'mCallback.onDateTimeRecurrenceSet(...)', evidence='SRC utils/date/SublimePickerFragment.java:60-63')
e('SublimePickerFragment.<init>', 'SublimePickerFragment$1.<init>', 'CALL', 'creates the listener adapter', evidence='SRC utils/date/SublimePickerFragment.java:45-66')
sup('SnoozeActivity.onCreate')
e('SnoozeActivity.<init>', 'SnoozeActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC SnoozeActivity.java:82-93')
e('SnoozeActivity.onCreate', 'SnoozeActivity.postpone', 'CALL', 'several notes were sent from the list: postpone(nextMinute)', guard='no single note extra', evidence='SRC SnoozeActivity.java:88-92')
e('SnoozeActivity.postpone', 'S_REMINDER_PICKER@SNOOZE', 'ENTERS', 'the picker is shown over the list', evidence='SRC SnoozeActivity.java:116-119')
e('SnoozeActivity.postpone', 'ReminderPickers.<init>', 'CALL', 'new ReminderPickers(this, this).pick(...)', evidence='SRC SnoozeActivity.java:117-118')
e('SnoozeActivity.postpone', 'ReminderPickers.pick', 'CALL', 'pick(alarm, rule)', evidence='SRC SnoozeActivity.java:118')
for cb in ('onSharedPreferenceChanged',):
    pass
e('SnoozeActivity.onRecurrenceReminderPicked', 'SnoozeActivity.setNextRecurrentReminder', 'CALL', 'setNextRecurrentReminder(note)', evidence='SRC SnoozeActivity.java:138-150')
e('ListFragment.addReminders', 'ListFragment.onActivityResult@REMINDERS', 'RESULT', 'the NEW_TASK start returns RESULT_CANCELED at once', evidence='FW-SRC services/core/java/com/android/server/am/ActivityStarter.java:1355-1370 (a start with FLAG_ACTIVITY_NEW_TASK that asked for a result immediately sends RESULT_CANCELED back to the caller); SRC ListFragment.java:893-899,982-987')


# ================================================================== C. settings, password, statistics, about, backup
e('SettingsActivity.<init>', 'SettingsActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC SettingsActivity.java:54-61')
e('SettingsActivity.onCreate', 'SettingsActivity_ViewBinding.<init>(SettingsActivity,View)', 'FRAMEWORK', 'ButterKnife.bind(this)', evidence=FW_BIND + '; SRC SettingsActivity.java:57')
for cb in ('onCreate', 'onCreatePreferences', 'onStart', 'onResume'):
    e('SettingsFragment.<init>', 'SettingsFragment.' + cb, 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC SettingsFragment.java:93-140,673-677')
SPAGE = {'ROOT': 'S_SETTINGS', 'DATA': 'S_SETTINGS_DATA', 'SYNC': 'S_SETTINGS_SYNC', 'INTERFACE': 'S_SETTINGS_INTERFACE', 'NAVIGATION': 'S_SETTINGS_NAVIGATION',
         'BEHAVIORS': 'S_SETTINGS_BEHAVIORS', 'NOTIFICATIONS': 'S_SETTINGS_NOTIFICATIONS', 'PRIVACY': 'S_SETTINGS_PRIVACY'}
sup('SettingsActivity.onPreferenceStartFragment', 'SettingsActivity.onBackPressed')
for k in ('DATA', 'INTERFACE', 'NAVIGATION', 'BEHAVIORS', 'NOTIFICATIONS', 'PRIVACY'):
    v = 'SettingsActivity.onPreferenceStartFragment@' + k
    gui('S_SETTINGS', v, 'Tap "%s"' % k.capitalize(), evidence='SRC SettingsActivity.java:125-140; res/xml/settings.xml')
    e(v, 'SettingsFragment.<init>', 'FRAMEWORK', 'FragmentFactory.instantiate(pref.getFragment())', evidence='INFERRED androidx FragmentFactory.instantiate builds the fragment by reflection (androidx source not read); SRC SettingsActivity.java:129-132')
    e(v, SPAGE[k], 'ENTERS', 'the sub-screen opens on top of the root', evidence='SRC SettingsActivity.java:135-139')
gui('S_SETTINGS_DATA', 'SettingsActivity.onPreferenceStartFragment@SYNC', 'Tap "Sync"', evidence='SRC SettingsActivity.java:125-140; res/xml/settings_data.xml')
e('SettingsActivity.onPreferenceStartFragment@SYNC', 'SettingsFragment.<init>', 'FRAMEWORK', 'FragmentFactory.instantiate(pref.getFragment())', evidence='INFERRED androidx FragmentFactory.instantiate builds the fragment by reflection (androidx source not read); SRC SettingsActivity.java:129-132')
e('SettingsActivity.onPreferenceStartFragment@SYNC', 'S_SETTINGS_SYNC', 'ENTERS', 'the sub-screen opens', evidence='SRC SettingsActivity.java:135-139')
# back from settings
for k, pg in SPAGE.items():
    if k == 'ROOT':
        gui(pg, 'SettingsActivity.onBackPressed@ROOT', 'Press Back or the Up arrow', evidence='SRC SettingsActivity.java:63-84')
        e('SettingsActivity.onBackPressed@ROOT', 'MainActivity.onResume', 'SYSTEM', 'SettingsActivity finishes and MainActivity resumes', evidence='SRC SettingsActivity.java:78-83')
    else:
        gui(pg, 'SettingsActivity.onBackPressed@' + k, 'Press Back or the Up arrow', evidence='SRC SettingsActivity.java:63-84')
        e('SettingsActivity.onBackPressed@' + k, 'S_SETTINGS_DATA' if k == 'SYNC' else 'S_SETTINGS', 'ENTERS', 'the sub-screen is popped', evidence='SRC SettingsActivity.java:78-83')
for k in SPAGE:
    e('SettingsActivity.onBackPressed@' + k, 'SettingsActivity.onBackPressed', 'CALL', 'super.onBackPressed()', evidence='SRC SettingsActivity.java:82')
e('SettingsActivity.onBackPressed@ROOT', 'S_LIST@NOTES', 'ENTERS', 'the list is shown again', evidence='SRC SettingsActivity.java:78-83')
gui('S_SETTINGS', 'SettingsActivity.lambda$initUI$0', 'Tap the Up arrow', evidence='SRC SettingsActivity.java:65')
e('SettingsActivity.lambda$initUI$0', 'SettingsActivity.onBackPressed@ROOT', 'CALL', 'onBackPressed()', evidence='SRC SettingsActivity.java:65')
# root screen
gui('S_SETTINGS', 'SettingsFragment.lambda$onResume$25', 'Tap "Show tour again"', evidence='SRC SettingsFragment.java:521-535')
e('SettingsFragment.lambda$onResume$25', 'S_DLG_TOUR_AGAIN', 'ENTERS', 'the confirmation opens', evidence='SRC SettingsFragment.java:524-533')
gui('S_DLG_TOUR_AGAIN', 'SettingsFragment.lambda$null$24', 'Tap Confirm', evidence=FW_MD + '; SRC SettingsFragment.java:527-532')
e('SettingsFragment.lambda$null$24', 'SystemHelper.restartApp', 'CALL', 'restartApp()', evidence='SRC SettingsFragment.java:531')
e('S_DLG_TOUR_AGAIN', 'S_SETTINGS', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
gui('S_SETTINGS', 'SettingsFragment.lambda$onResume$19', 'Tap "Changelog"', evidence='SRC SettingsFragment.java:462-480')
e('SettingsFragment.lambda$onResume$19', 'S_DLG_CHANGELOG', 'ENTERS', 'the changelog dialog opens', evidence='SRC SettingsFragment.java:469-473')
e('S_DLG_CHANGELOG', 'S_SETTINGS', 'ENTERS', 'Tap OK or press Back', gui=['Tap OK'], evidence=BACK_DLG)
gui('S_SETTINGS', 'StatsActivity.<init>', 'Tap "Statistics"', kind='INTENT', evidence='SRC res/xml/settings.xml:111-117')
gui('S_SETTINGS', 'AboutActivity.<init>', 'Tap "About"', kind='INTENT', evidence='SRC res/xml/settings.xml:119-125')
# data screen
gui('S_SETTINGS_DATA', 'SettingsFragment.lambda$onResume$10', 'Tap "Password"', evidence='SRC SettingsFragment.java:320-327')
e('SettingsFragment.lambda$onResume$10', 'PasswordActivity.<init>', 'INTENT', 'startActivity(PasswordActivity)', evidence='SRC SettingsFragment.java:323-324')
e('SettingsFragment.lambda$onResume$10', 'S_PASSWORD@UNSET_SETTINGS', 'ENTERS', 'the password screen opens (no password yet)', evidence='SRC SettingsFragment.java:323-324')
e('SettingsFragment.lambda$onResume$10', 'S_PASSWORD@SET_SETTINGS', 'ENTERS', 'the password screen opens (password set)', needs_state=NEED_PWD, evidence='SRC SettingsFragment.java:323-324')
gui('S_SETTINGS_DATA', 'SettingsFragment.lambda$onResume$12', 'Tap "Request password on access"', needs_state=NEED_PWD, evidence='SRC SettingsFragment.java:330-346')
e('SettingsFragment.lambda$onResume$12', 'PasswordHelper.requestPassword', 'CALL', 'asks for the password before toggling', needs_state=NEED_PWD, evidence='SRC SettingsFragment.java:339-343')
gui('S_SETTINGS_DATA', 'SettingsFragment.lambda$onResume$21', 'Tap "Reset all data"', evidence='SRC SettingsFragment.java:483-503')
e('SettingsFragment.lambda$onResume$21', 'S_DLG_RESET_DATA', 'ENTERS', 'the confirmation opens', evidence='SRC SettingsFragment.java:487-500')
gui('S_DLG_RESET_DATA', 'SettingsFragment.lambda$null$20', 'Tap Confirm', evidence=FW_MD + '; SRC SettingsFragment.java:490-499')
for dst in ('StorageHelper.delete', 'StorageHelper.getAttachmentDir', 'StorageHelper.getCacheDir', 'SystemHelper.restartApp'):
    e('SettingsFragment.lambda$null$20', dst, 'CALL', 'wipes prefs, database, attachments and cache', evidence='SRC SettingsFragment.java:491-498')
e('SystemHelper.restartApp', 'S_EXIT', 'ENTERS', 'System.exit(0)', evidence='SRC utils/SystemHelper.java:34-44')
e('S_DLG_RESET_DATA', 'S_SETTINGS_DATA', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
# sync screen
gui('S_SETTINGS_SYNC', 'SettingsFragment.lambda$onResume$1', 'Tap "Export"', evidence='SRC SettingsFragment.java:141-157')
e('SettingsFragment.lambda$onResume$1', 'SettingsFragment.lambda$null$0', 'CALL', 'WRITE_EXTERNAL_STORAGE is granted: export(view)', needs_state=NEED_PERM_STORAGE, evidence='SRC SettingsFragment.java:150-152')
e('SettingsFragment.lambda$null$0', 'SettingsFragment.export', 'CALL', 'export(view)', evidence='SRC SettingsFragment.java:152')
e('SettingsFragment.export', 'S_DLG_EXPORT', 'ENTERS', 'the backup-name dialog opens', evidence='SRC SettingsFragment.java:625-669')
for cb in ('onTextChanged', 'beforeTextChanged', 'afterTextChanged'):
    gui('S_DLG_EXPORT', 'SettingsFragment$1.' + cb, 'Type a backup name', evidence='SRC SettingsFragment.java:634-656')
gui('S_DLG_EXPORT', 'SettingsFragment.lambda$export$32', 'Tap Confirm', evidence=FW_MD + '; SRC SettingsFragment.java:662-668')
e('SettingsFragment.lambda$export$32', 'BackupHelper.startBackupService', 'CALL', 'BackupHelper.startBackupService(name)', evidence='SRC SettingsFragment.java:667')
e('SettingsFragment.lambda$export$32', 'S_SETTINGS_SYNC', 'ENTERS', 'the export runs in the background', evidence='SRC SettingsFragment.java:658-668')
e('S_DLG_EXPORT', 'S_SETTINGS_SYNC', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
gui('S_SETTINGS_SYNC', 'SettingsFragment.lambda$onResume$2', 'Tap "Import"', evidence='SRC SettingsFragment.java:159-166')
e('SettingsFragment.lambda$onResume$2', 'SettingsFragment.importNotes', 'CALL', 'WRITE_EXTERNAL_STORAGE is granted: importNotes()', needs_state=NEED_PERM_STORAGE, evidence='SRC SettingsFragment.java:162-164')
sup(('SettingsFragment.importNotes', 'RecyclerViewItemClickSupport.addTo'))
e('SettingsFragment.importNotes', 'S_DLG_IMPORT', 'ENTERS', 'the backup list opens', needs_state=NEED_BACKUP, evidence='SRC SettingsFragment.java:539-622')
e('SettingsFragment.importNotes', 'SettingsFragment.lambda$importNotes$31', 'FRAMEWORK', 'importDialog.setOnShowListener fires when the dialog shows', needs_state=NEED_BACKUP, evidence=FW_VIEW + '; SRC SettingsFragment.java:556-619')
e('SettingsFragment.lambda$importNotes$31', 'RecyclerViewItemClickSupport.addTo', 'CALL', 'click support for the backup list', evidence='SRC SettingsFragment.java:558,595')
gui('S_DLG_IMPORT', 'SettingsFragment.lambda$importNotes$26', 'Tap Confirm', evidence=FW_MD + '; SRC SettingsFragment.java:550-553')
gui('S_DLG_IMPORT', 'RecyclerViewItemClickSupport$1.onClick@IMPORT', 'Tap a backup', evidence='SRC models/listeners/RecyclerViewItemClickSupport.java; SettingsFragment.java:558-592')
gui('S_DLG_IMPORT', 'RecyclerViewItemClickSupport$2.onLongClick@IMPORT', 'Long-press a backup', evidence='SRC models/listeners/RecyclerViewItemClickSupport.java; SettingsFragment.java:595-617')
e('RecyclerViewItemClickSupport$1.onClick@IMPORT', 'SettingsFragment.lambda$null$28', 'CALL', 'OnItemClickListener.onItemClick', evidence='SRC SettingsFragment.java:558')
e('RecyclerViewItemClickSupport$2.onLongClick@IMPORT', 'SettingsFragment.lambda$null$30', 'CALL', 'OnItemLongClickListener.onItemLongClick', evidence='SRC SettingsFragment.java:595')
e('SettingsFragment.lambda$null$28', 'S_DLG_IMPORT_CONFIRM', 'ENTERS', 'the restore confirmation opens', evidence='SRC SettingsFragment.java:573-591')
e('SettingsFragment.lambda$null$30', 'S_DLG_BACKUP_DELETE', 'ENTERS', 'the delete confirmation opens', evidence='SRC SettingsFragment.java:601-615')
gui('S_DLG_IMPORT_CONFIRM', 'SettingsFragment.lambda$null$27', 'Tap Confirm', evidence=FW_MD + '; SRC SettingsFragment.java:577-590')
gui('S_DLG_BACKUP_DELETE', 'SettingsFragment.lambda$null$29', 'Tap Confirm', evidence=FW_MD + '; SRC SettingsFragment.java:605-614')
e('SettingsFragment.lambda$null$27', 'S_SETTINGS_SYNC', 'ENTERS', 'the restore runs in the background', evidence='SRC SettingsFragment.java:582-590')
e('SettingsFragment.lambda$null$29', 'S_SETTINGS_SYNC', 'ENTERS', 'the backup is deleted in the background', evidence='SRC SettingsFragment.java:606-614')
for k in ('S_DLG_IMPORT', 'S_DLG_IMPORT_CONFIRM', 'S_DLG_BACKUP_DELETE'):
    e(k, 'S_SETTINGS_SYNC', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
gui('S_SETTINGS_SYNC', 'SettingsFragment.lambda$onResume$4', 'Tap "Import legacy data"', evidence='SRC SettingsFragment.java:169-181')
e('SettingsFragment.lambda$onResume$4', 'SettingsFragment.lambda$null$3', 'CALL', 'READ_EXTERNAL_STORAGE is granted: the folder chooser opens', needs_state=NEED_PERM_STORAGE, evidence='SRC SettingsFragment.java:174-178')
e('SettingsFragment.lambda$null$3', 'S_DLG_FOLDER_CHOOSER', 'ENTERS', 'new FolderChooserDialog.Builder(...).show(...)', evidence='SRC SettingsFragment.java:175-178')
gui('S_DLG_FOLDER_CHOOSER', 'SettingsActivity.onFolderSelection', 'Choose a folder', evidence='SRC SettingsActivity.java:99-113')
gui('S_DLG_FOLDER_CHOOSER', 'SettingsActivity.onFolderChooserDismissed', 'Press Back', evidence='SRC SettingsActivity.java:115-117')
e('SettingsActivity.onFolderSelection', 'S_DLG_LEGACY_IMPORT_CONFIRM', 'ENTERS', 'the legacy import confirmation opens', evidence='SRC SettingsActivity.java:100-111')
e('SettingsActivity.onFolderChooserDismissed', 'S_SETTINGS_SYNC', 'ENTERS', 'the chooser closes', evidence='SRC SettingsActivity.java:115-117')
gui('S_DLG_LEGACY_IMPORT_CONFIRM', 'SettingsActivity.lambda$onFolderSelection$1', 'Tap Confirm', evidence=FW_MD + '; SRC SettingsActivity.java:104-110')
e('SettingsActivity.lambda$onFolderSelection$1', 'S_SETTINGS_SYNC', 'ENTERS', 'the legacy import runs in the background', evidence='SRC SettingsActivity.java:104-110')
e('S_DLG_LEGACY_IMPORT_CONFIRM', 'S_SETTINGS_SYNC', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
gui('S_SETTINGS_SYNC', 'SettingsFragment.lambda$onResume$5', 'Tap "Import from Springpad"', evidence='SRC SettingsFragment.java:240-255')
e('SettingsFragment.lambda$onResume$5', 'S_EXT_PICKER@SPRINGPAD', 'ENTERS', 'startActivityForResult(ACTION_GET_CONTENT, application/zip)', env=ENV_PICKER, needs_state=NEED_SPRINGPAD, evidence='SRC SettingsFragment.java:243-252')
e('S_EXT_PICKER@SPRINGPAD', 'SettingsFragment.onActivityResult@SPRINGPAD', 'RESULT', 'a Springpad zip was chosen', env=ENV_PICKER, evidence='SRC SettingsFragment.java:683-691')
e('S_EXT_PICKER@SPRINGPAD', 'SettingsFragment.onActivityResult@CANCEL', 'RESULT', 'The user leaves the picker with Back: RESULT_CANCELED', evidence=RES_CANCEL + '; SRC SettingsFragment.java:680-681')
e('S_EXT_PICKER@SPRINGPAD', 'S_SETTINGS_SYNC', 'ENTERS', 'Press Back in the picker', gui=['Press Back in the picker'], evidence=BACK_EXT)
for dst in ('FileHelper.getPath',):
    e('SettingsFragment.onActivityResult@SPRINGPAD', dst, 'CALL', 'resolve the zip path', env=ENV_PICKER, evidence='SRC SettingsFragment.java:684-685')
e('SettingsFragment.onActivityResult@SPRINGPAD', 'S_SETTINGS_SYNC', 'ENTERS', 'the Springpad import runs in the background', env=ENV_PICKER, evidence='SRC SettingsFragment.java:686-691')
# interface / navigation / behaviour / notification / privacy screens
PREFS = [('INTERFACE', 'SettingsFragment.lambda$onResume$13', 'Tap "Language" and choose a language', None, 'S_EXIT'), ('INTERFACE', 'SettingsFragment.lambda$onResume$14', 'Tap "Colours" and choose an option', None, None),
         ('NAVIGATION', 'SettingsFragment.lambda$onResume$7', 'Switch "Show uncategorized"', None, None), ('BEHAVIORS', 'SettingsFragment.lambda$onResume$6', 'Switch "Swipe to trash"', None, None),
         ('BEHAVIORS', 'SettingsFragment.lambda$onResume$8', 'Switch "Auto location"', None, None), ('BEHAVIORS', 'SettingsFragment.lambda$onResume$9', 'Tap "Max video size" and type a value', None, None),
         ('BEHAVIORS', 'SettingsFragment.lambda$onResume$15', 'Tap "Checked items behaviour" and choose an option', None, None),
         ('NOTIFICATIONS', 'SettingsFragment.lambda$onResume$18', 'Tap "Snooze delay" and type a value', None, None), ('PRIVACY', 'SettingsFragment.lambda$onResume$23', 'Switch "File logging"', None, None)]
for k, lam, text, need, exitp in PREFS:
    gui(SPAGE[k], lam, text, needs_state=need, evidence='SRC SettingsFragment.java:276-516')
    if exitp:
        e(lam, exitp, 'ENTERS', 'the app restarts', evidence='SRC SettingsFragment.java:354-358')
e('SettingsFragment.lambda$onResume$13', 'LanguageHelper.updateLanguage', 'CALL', 'updateLanguage(value)', evidence='SRC SettingsFragment.java:355')
e('SettingsFragment.lambda$onResume$13', 'SystemHelper.restartApp', 'CALL', 'restartApp()', evidence='SRC SettingsFragment.java:356')
e('SettingsFragment.lambda$onResume$23', 'SettingsFragment.lambda$null$22', 'CALL', 'WRITE_EXTERNAL_STORAGE is granted: file logging is enabled', needs_state=NEED_PERM_STORAGE, evidence='SRC SettingsFragment.java:509-514')
e('SettingsFragment.lambda$onResume$23', 'PermissionsHelper.requestPermission', 'CALL', 'requestPermission(WRITE_EXTERNAL_STORAGE)', evidence='SRC SettingsFragment.java:510')
gui('S_SETTINGS_NOTIFICATIONS', 'SettingsFragment.lambda$onResume$17', 'Tap "Ringtone"', evidence='SRC SettingsFragment.java:413-439')
e('SettingsFragment.lambda$onResume$17', 'S_EXT_PICKER@RINGTONE', 'ENTERS', 'startActivityForResult(ACTION_RINGTONE_PICKER)', env=ENV_PICKER, evidence='SRC SettingsFragment.java:415-437')
e('S_EXT_PICKER@RINGTONE', 'SettingsFragment.onActivityResult@RINGTONE', 'RESULT', 'a ringtone was picked', env=ENV_PICKER, evidence='SRC SettingsFragment.java:693-697')
e('S_EXT_PICKER@RINGTONE', 'SettingsFragment.onActivityResult@CANCEL', 'RESULT', 'The user leaves the picker with Back: RESULT_CANCELED', evidence=RES_CANCEL + '; SRC SettingsFragment.java:680-681')
e('S_EXT_PICKER@RINGTONE', 'S_SETTINGS_NOTIFICATIONS', 'ENTERS', 'Press Back in the picker', gui=['Press Back in the picker'], evidence=BACK_EXT)
e('SettingsFragment.onActivityResult@RINGTONE', 'S_SETTINGS_NOTIFICATIONS', 'ENTERS', 'the ringtone preference is stored', env=ENV_PICKER, evidence='SRC SettingsFragment.java:693-697')
sup('SettingsFragment.onActivityResult')
for k in ('SPRINGPAD', 'RINGTONE', 'CANCEL'):
    e('SettingsFragment.onActivityResult@' + k, 'SettingsFragment.onActivityResult', 'CALL', 'onActivityResult(requestCode, resultCode, intent)', evidence='SRC SettingsFragment.java:680-701')
sup('SettingsFragment.lambda$onResume$16')
# ---- password screen
for cb in ('onCreate', 'onStart', 'onStop'):
    e('PasswordActivity.<init>', 'PasswordActivity.' + cb, 'LIFECYCLE', 'Activity lifecycle', evidence='SRC PasswordActivity.java:56-80')
e('PasswordActivity.<init>', 'BaseActivity.attachBaseContext', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC BaseActivity.java:72-75')
e('PasswordActivity.onCreate', 'BaseActivity.onCreate', 'CALL', 'super.onCreate', evidence='SRC PasswordActivity.java:57')
e('PasswordActivity.<init>', 'BaseActivity.onResume', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC BaseActivity.java:96-101')
for pg in ('UNSET_SETTINGS', 'UNSET_DETAIL', 'SET_SETTINGS'):
    p = 'S_PASSWORD@' + pg
    gui(p, 'PasswordActivity.lambda$initViews$3', 'Fill all five fields and tap OK', evidence='SRC PasswordActivity.java:103-118')
    gui(p, 'PasswordActivity.lambda$initViews$1', 'Tap "Remove password"', evidence='SRC PasswordActivity.java:91-101')
    gui(p, 'PasswordActivity.lambda$initViews$4', 'Tap "Forgot password"', evidence='SRC PasswordActivity.java:120-127')
    gui(p, 'PasswordActivity.onBackPressed@' + ('DETAIL' if pg == 'UNSET_DETAIL' else 'SETTINGS'), 'Press Back', evidence='SRC PasswordActivity.java:243-246')
sup('PasswordActivity.onBackPressed')
e('PasswordActivity.onBackPressed@SETTINGS', 'PasswordActivity.onBackPressed', 'CALL', 'setResult(RESULT_OK); finish()', evidence='SRC PasswordActivity.java:243-246')
e('PasswordActivity.onBackPressed@DETAIL', 'PasswordActivity.onBackPressed', 'CALL', 'setResult(RESULT_OK); finish()', evidence='SRC PasswordActivity.java:243-246')
e('PasswordActivity.onBackPressed@SETTINGS', 'S_SETTINGS_DATA', 'ENTERS', 'the password screen finishes', evidence='SRC PasswordActivity.java:243-246')
e('PasswordActivity.onBackPressed@DETAIL', 'S_DETAIL@NEW', 'ENTERS', 'the password screen finishes with RESULT_OK', evidence='SRC PasswordActivity.java:243-246')
e('PasswordActivity.onBackPressed@DETAIL', 'DetailFragment.onActivityResult@PASSWORD', 'RESULT', 'RESULT_OK with the SET_PASSWORD request', evidence='SRC DetailFragment.java:1428-1431')
sup(('PasswordActivity.lambda$initViews$3', 'PasswordActivity.updatePassword'), ('PasswordActivity.lambda$null$0', 'PasswordActivity.updatePassword'), ('PasswordActivity.lambda$null$2', 'PasswordActivity.updatePassword'))
e('PasswordActivity.lambda$initViews$3', 'PasswordActivity.checkData', 'CALL', 'checkData()', evidence='SRC PasswordActivity.java:104')
e('PasswordActivity.lambda$initViews$3', 'PasswordActivity.updatePassword', 'CALL', 'no password yet: set it straight away', guard='prefs.password == null', evidence='SRC PasswordActivity.java:114-116')
e('PasswordActivity.lambda$null$2', 'PasswordActivity.updatePassword', 'CALL', 'updatePassword(new password, question, answer)', evidence='SRC PasswordActivity.java:110-112')
e('PasswordActivity.lambda$null$0', 'PasswordActivity.updatePassword', 'CALL', 'updatePassword(null, null, null): remove the password', evidence='SRC PasswordActivity.java:93-97')
e('PasswordActivity.lambda$initViews$4', 'PasswordHelper.resetPassword', 'CALL', 'the security-question dialog opens', needs_state=NEED_PWD, evidence='SRC PasswordActivity.java:120-127')
e('PasswordActivity.updatePassword', 'S_DLG_REMOVE_PASSWORD', 'ENTERS', 'passwordText == null: "unlock all notes" confirmation', needs_state=NEED_PWD, evidence='SRC PasswordActivity.java:156-164')
gui('S_DLG_REMOVE_PASSWORD', 'PasswordActivity.lambda$updatePassword$5', 'Tap OK', evidence=FW_MD + '; SRC PasswordActivity.java:161-164')
e('PasswordActivity.lambda$updatePassword$5', 'PasswordHelper.removePassword', 'CALL', 'removePassword()', evidence='SRC PasswordActivity.java:164')
e('PasswordActivity.lambda$updatePassword$5', 'S_PASSWORD@UNSET_SETTINGS', 'ENTERS', 'the password is removed', evidence='SRC PasswordActivity.java:161-164')
e('S_DLG_REMOVE_PASSWORD', 'S_PASSWORD@SET_SETTINGS', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('PasswordActivity.updatePassword', 'PasswordActivity.lambda$updatePassword$6', 'ASYNC', 'Rx doOnSubscribe: the password preferences are written', evidence=FW_ASYNC + '; SRC PasswordActivity.java:168-195')
e('PasswordActivity.updatePassword', 'PasswordActivity.lambda$updatePassword$7', 'ASYNC', 'Rx doOnNext for each locked note', needs_state=NEED_LOCKED, evidence=FW_ASYNC + '; SRC PasswordActivity.java:177')
e('PasswordActivity.updatePassword', 'PasswordActivity.lambda$updatePassword$8', 'ASYNC', 'Rx doOnCompleted: "password changed" crouton', evidence=FW_ASYNC + '; SRC PasswordActivity.java:178-195')
e('PasswordActivity.lambda$updatePassword$8', 'PasswordActivity$2.onDisplayed', 'FRAMEWORK', 'Crouton lifecycle callback', evidence=FW_VIEW + '; SRC PasswordActivity.java:181-194')
e('PasswordActivity.lambda$updatePassword$8', 'PasswordActivity$2.onRemoved', 'FRAMEWORK', 'Crouton lifecycle callback (the screen closes)', evidence=FW_VIEW + '; SRC PasswordActivity.java:181-194')
e('PasswordActivity$2.onRemoved', 'PasswordActivity.onBackPressed@SETTINGS', 'CALL', 'onBackPressed()', evidence='SRC PasswordActivity.java:189-191')
e('PasswordActivity.onEvent', 'PasswordActivity$1.onDisplayed', 'FRAMEWORK', 'Crouton lifecycle callback', evidence=FW_VIEW + '; SRC PasswordActivity.java:136-150')
e('PasswordActivity.onEvent', 'PasswordActivity$1.onRemoved', 'FRAMEWORK', 'Crouton lifecycle callback (the screen closes)', evidence=FW_VIEW + '; SRC PasswordActivity.java:136-150')
e('PasswordActivity$1.onRemoved', 'PasswordActivity.onBackPressed@SETTINGS', 'CALL', 'onBackPressed()', evidence='SRC PasswordActivity.java:146-148')
# ---- statistics and about
e('StatsActivity.<init>', 'StatsActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC StatsActivity.java:32-37')
e('StatsActivity.onCreate', 'S_STATS', 'ENTERS', 'the statistics dialog opens', evidence='SRC StatsActivity.java:32-37')
e('StatsActivity$1StatsTask.<init>', 'StatsActivity$1StatsTask.doInBackground', 'ASYNC', 'executeOnExecutor', evidence=FW_ASYNC + '; SRC StatsActivity.java:41-56')
e('StatsActivity$1StatsTask.doInBackground', 'StatsActivity$1StatsTask.onPostExecute', 'ASYNC', 'the statistics are delivered on the main thread', evidence=FW_ASYNC + '; SRC StatsActivity.java:44-52')
e('S_STATS', 'S_SETTINGS', 'ENTERS', 'Press Back', gui=['Press Back'], evidence=BACK_ACT)
e('AboutActivity.<init>', 'AboutActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC AboutActivity.java:26-35')
e('AboutActivity.<init>', 'AboutActivity.onStart', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC AboutActivity.java:37-41')
e('AboutActivity.<init>', 'BaseActivity.attachBaseContext', 'LIFECYCLE', 'Activity lifecycle', evidence='SRC BaseActivity.java:72-75')
e('AboutActivity.onCreate', 'S_ABOUT', 'ENTERS', 'the about page is shown', evidence='SRC AboutActivity.java:26-35')
gui('S_ABOUT', 'AboutActivity.lambda$initUI$0', 'Tap the Up arrow', evidence='SRC AboutActivity.java:56')
e('AboutActivity.lambda$initUI$0', 'AboutActivity.onNavigateUp', 'CALL', 'onNavigateUp()', evidence='SRC AboutActivity.java:56')
e('AboutActivity.onNavigateUp', 'S_SETTINGS', 'ENTERS', 'onBackPressed(): the about page finishes', evidence='SRC AboutActivity.java:44-48')
e('S_ABOUT', 'S_SETTINGS', 'ENTERS', 'Press Back', gui=['Press Back'], evidence=BACK_ACT)


# ================================================================== D. entries from outside, receivers, services, widgets, notifications
# MainActivity.handleIntents serves several explicit actions; its calls are gated by what the sender must do
sup('MainActivity.handleIntents')
e('MainActivity.handleIntents', 'MainActivity.receivedIntent', 'CALL', 'the intent has an action: is it one of the custom actions?', needs_state='The intent has an action (ACTION_MAIN is set after a navigation change or a search)', evidence='SRC MainActivity.java:345-356')
HI_DST = {'SEND': ('MainActivity.receivedIntent', 'MainActivity.switchToDetail', 'Note.<init>()'),
          'SHORTCUT_NOTIF': ('MainActivity.receivedIntent', 'DbHelper.getInstance()', 'DbHelper.getNote', 'MainActivity.noteAlreadyOpened', 'MainActivity.switchToDetail', 'Note.<init>()'),
          'WIDGET_ADD': ('MainActivity.receivedIntent', 'MainActivity.switchToDetail', 'Note.<init>()'), 'WIDGET_LIST': ('MainActivity.receivedIntent',),
          'VIEW_HASHTAG': ('MainActivity.switchToList',), 'SEND_AND_EXIT': ('MainActivity.saveAndExit',), 'RESTART': ('SystemHelper.restartApp',)}
for k, dsts in HI_DST.items():
    for d in dsts:
        e('MainActivity.handleIntents@' + k, d, 'CALL', 'branch for the %s start intent' % k.lower(), evidence='SRC MainActivity.java:345-392')
INT = {  # variant -> (text, env, page entered, gui text from the entry page)
    'SEND': ('Share text or files to Omni Notes from another app', ENV_EXT, 'S_DETAIL@NEW'),
    'SHORTCUT_NOTIF': ('Open a note from a note shortcut or a reminder notification', ENV_LAUNCHER, 'S_DETAIL@EDIT'),
    'WIDGET_ADD': ('Tap + or the camera button of a widget, or the "Add note" shortcut', ENV_LAUNCHER, 'S_DETAIL@NEW'),
    'WIDGET_LIST': ('Tap the list part of a widget', ENV_LAUNCHER, 'S_LIST@NOTES'),
    'VIEW_HASHTAG': ('Open a hashtag://tag link', ENV_EXT, 'S_LIST_SEARCH_RESULT'),
    'SEND_AND_EXIT': ('Gmail AUTO_SEND intent', ENV_EXT, 'S_EXIT'),
    'RESTART': ('Tap the backup-import notification', ENV_LAUNCHER, 'S_EXIT'),
}
for k, (text, env, page) in INT.items():
    v = 'MainActivity.onNewIntent@' + k
    e('S_ENTRY', v, 'ENTRY', text, gui=[text], env=env, evidence='SRC AndroidManifest.xml:65-114; MainActivity.java:194-202,345-392')
    e(v, 'MainActivity.onNewIntent', 'CALL', 'onNewIntent(intent)', evidence='SRC MainActivity.java:194-202')
    e(v, 'MainActivity.handleIntents@' + k, 'CALL', 'handleIntents() sees this action', evidence='SRC MainActivity.java:194-202,345-392')
    e(v, page, 'ENTERS', 'handleIntents opens the matching screen', env=env, evidence='SRC MainActivity.java:345-392')
e('MainActivity.onNewIntent', 'MainActivity.handleIntents', 'CALL', 'handleIntents()', evidence='SRC MainActivity.java:194-202')
for k in ('WIDGET_ADD', 'WIDGET_LIST'):
    pass
# ---- reminder alarm -> notification -> SnoozeActivity actions
e('ReminderHelper.addReminder(Context,Note,long)', 'AlarmReceiver.onReceive', 'SYSTEM', 'AlarmManager fires the broadcast when the reminder time is reached', needs_state=NEED_REMINDER_FIRED, evidence='INFERRED the alarm service broadcasts to the receiver when the alarm time is reached (AlarmManagerService source not read); SRC utils/ReminderHelper.java:50-58; receiver/AlarmReceiver.java:53-65')
e('AlarmReceiver.onReceive', 'S_NOTIF_REMINDER', 'ENTERS', 'the reminder notification is posted', evidence='SRC receiver/AlarmReceiver.java:136')
e('AlarmReceiver.<init>', 'AlarmReceiver.onReceive', 'LIFECYCLE', 'the system instantiates the receiver and delivers the broadcast', needs_state=NEED_REMINDER_FIRED, evidence='SRC AndroidManifest.xml:189')
e('ReminderHelper.addReminder(Context,Note,long)', 'AlarmReceiver.<init>', 'SYSTEM', 'the system instantiates the receiver', needs_state=NEED_REMINDER_FIRED, evidence='FW-SRC core/java/android/app/ActivityThread.java:3141-3190 (handleReceiver instantiates the manifest receiver class and calls onReceive); INFERRED the alarm service sends the broadcast (AlarmManagerService source not read)')
for dst in ('ParcelableUtil.unmarshall(byte[],Creator)', 'Note.<init>(Parcel)', 'Note$1.createFromParcel'):
    pass
for k, text in {'SNOOZE': 'Tap "Snooze" on the notification', 'POSTPONE': 'Tap "Add reminder" on the notification', 'CLICK': 'Tap the reminder notification'}.items():   # ACTION_DISMISS is never sent: no code builds an intent with it (SnoozeActivity.java:96)
    v = 'SnoozeActivity.onCreate@' + k
    env = ENV_LAUNCHER
    e('S_NOTIF_REMINDER', v, 'GUI', text, gui=[text], env=env, evidence='SRC receiver/AlarmReceiver.java:85-113; SnoozeActivity.java:82-114')
    e(v, 'SnoozeActivity.manageNotification@' + k, 'CALL', 'manageNotification(prefs)', evidence='SRC SnoozeActivity.java:85-88')
    e('SnoozeActivity.manageNotification@' + k, 'SnoozeActivity.removeNotification', 'CALL', 'removeNotification(note)', evidence='SRC SnoozeActivity.java:113')
e('S_NOTIF_REMINDER', 'SnoozeActivity.<init>', 'INTENT', 'the notification actions start SnoozeActivity', env=ENV_LAUNCHER, evidence='SRC receiver/AlarmReceiver.java:85-113')
e('SnoozeActivity.manageNotification@SNOOZE', 'SnoozeActivity.updateNoteReminder(long,Note)', 'CALL', 'the reminder is moved by the snooze delay', evidence='SRC SnoozeActivity.java:99-103')
e('SnoozeActivity.manageNotification@POSTPONE', 'SnoozeActivity.postpone', 'CALL', 'postpone(...) opens the picker', evidence='SRC SnoozeActivity.java:104-106')
e('SnoozeActivity.manageNotification@POSTPONE', 'S_REMINDER_PICKER@SNOOZE', 'ENTERS', 'the picker opens over the launcher', evidence='SRC SnoozeActivity.java:104-106,116-119')
e('SnoozeActivity.manageNotification@CLICK', 'MainActivity.onNewIntent@SHORTCUT_NOTIF', 'INTENT', 'startActivity(MainActivity, ACTION_NOTIFICATION_CLICK)', env=ENV_LAUNCHER, evidence='SRC SnoozeActivity.java:107-111')
for k in ('SNOOZE', 'DISMISS'):
    e('SnoozeActivity.manageNotification@' + k, 'S_ENTRY', 'ENTERS', 'SnoozeActivity finishes: back to the launcher', evidence='SRC SnoozeActivity.java:98,103')
e('SnoozeActivity.updateNoteReminder(long,Note)', 'SnoozeActivity.updateNoteReminder(long,Note,boolean)', 'CALL', 'updateNoteReminder(reminder, note, false)', evidence='SRC SnoozeActivity.java:67-69')
sup(('SnoozeActivity.updateNoteReminder(long,Note,boolean)', 'SaveNoteTask.<init>(boolean)'))
e('SnoozeActivity.updateNoteReminder(long,Note,boolean)', 'SaveNoteTask.<init>(boolean)', 'CALL', 'updateNote == true: the note is saved', needs_state='A recurring reminder moved to its next occurrence', evidence='SRC SnoozeActivity.java:72-75')
# ---- boot
e('S_ENTRY', 'BootCompleteReceiver.<init>', 'ENTRY', 'BOOT_COMPLETED broadcast', gui=['Reboot the device'], env=ENV_BOOT, evidence='SRC AndroidManifest.xml:192-201')
e('BootCompleteReceiver.<init>', 'BootCompleteReceiver.onReceive', 'LIFECYCLE', 'the system delivers the broadcast', env=ENV_BOOT, evidence='SRC receiver/BootCompleteReceiver.java:29-33')
e('AlarmRestoreOnRebootService.enqueueWork', 'AlarmRestoreOnRebootService.<init>', 'SYSTEM', 'JobIntentService is created by the job scheduler', env=ENV_BOOT, evidence='INFERRED the job scheduler creates the JobIntentService and runs onHandleWork (JobIntentService source not read); SRC async/AlarmRestoreOnRebootService.java:40-47')
e('AlarmRestoreOnRebootService.<init>', 'AlarmRestoreOnRebootService.onHandleWork', 'LIFECYCLE', 'the job runs', env=ENV_BOOT, evidence='SRC async/AlarmRestoreOnRebootService.java:49-62')
# ---- notification listener (needs the system "notification access" grant)
e('S_ENTRY', 'NotificationListener.<init>', 'ENTRY', 'the system binds the notification listener', gui=['Grant notification access to Omni Notes in system settings'], env=ENV_EXT, evidence='SRC AndroidManifest.xml:209-217')
for cb in ('onCreate', 'onNotificationPosted', 'onNotificationRemoved', 'onDestroy'):
    e('NotificationListener.<init>', 'NotificationListener.' + cb, 'LIFECYCLE', 'listener service callback', env=ENV_EXT, evidence='SRC NotificationListener.java:36-58')
e('NotificationListener.onNotificationRemoved', 'NotificationListener.onEventAsync', 'FRAMEWORK', 'NotificationRemovedEvent', env=ENV_EXT, evidence=FW_EB + '; SRC NotificationListener.java:55,60-66')
# ---- backup / import service
sup('DataBackupIntentService.onHandleIntent')
SVC = {'EXPORT': ('BackupHelper.startBackupService', 'DataBackupIntentService.exportData'), 'IMPORT': ('SettingsFragment.lambda$null$27', 'DataBackupIntentService.importData@IMPORT'),
       'LEGACY': ('SettingsActivity.lambda$onFolderSelection$1', 'DataBackupIntentService.importData@LEGACY'), 'SPRINGPAD': ('SettingsFragment.onActivityResult@SPRINGPAD', 'DataBackupIntentService.importDataFromSpringpad'),
       'DELETE': ('SettingsFragment.lambda$null$29', 'DataBackupIntentService.deleteData')}
for k, (cal, tgt) in SVC.items():
    v = 'DataBackupIntentService.onHandleIntent@' + k
    env = ENV_PICKER if k == 'SPRINGPAD' else None
    e(cal, 'DataBackupIntentService.<init>', 'INTENT', 'startService(DataBackupIntentService, action %s)' % k.lower(), env=env, evidence='SRC SettingsFragment.java:585-590,608-613; BackupHelper.startBackupService')
    e(cal, v, 'ASYNC', 'IntentService.onHandleIntent runs on a worker thread', env=env, evidence=FW_ASYNC + '; SRC async/DataBackupIntentService.java:67-84')
    for dst in ('NotificationsHelper.<init>', 'NotificationsHelper.start'):
        e(v, dst, 'CALL', 'the progress notification is created', evidence='SRC async/DataBackupIntentService.java:71-72')
    e(v, tgt, 'CALL', 'the %s action' % k.lower(), env=env, evidence='SRC async/DataBackupIntentService.java:75-83')
    e(v, 'S_NOTIF_BACKUP', 'ENTERS', 'a completion notification is posted', env=env, evidence='SRC async/DataBackupIntentService.java:172-199')
e('S_NOTIF_BACKUP', 'MainActivity.onNewIntent@RESTART', 'GUI', 'Tap the import-complete notification', gui=['Tap the import-complete notification'], env=ENV_LAUNCHER, evidence='SRC async/DataBackupIntentService.java:176-188')
# importData runs once per action; the legacy flag (line 123) decides the folder (127) and the notes / database step (131-135)
sup(('DataBackupIntentService.importData', 'BackupHelper.importNotes'), ('DataBackupIntentService.importData', 'BackupHelper.importDB'), ('DataBackupIntentService.importData', 'StorageHelper.getBackupDir'))
for k in ('IMPORT', 'LEGACY'):
    v = 'DataBackupIntentService.importData@' + k
    e(v, 'DataBackupIntentService.createNotification', 'CALL', 'completion notification', evidence='SRC async/DataBackupIntentService.java:143-145')
e('DataBackupIntentService.importData@IMPORT', 'StorageHelper.getBackupDir', 'CALL', 'the backup folder of a normal import', guard='the action is a normal import, not the legacy one (importLegacy is false)', evidence='SRC async/DataBackupIntentService.java:123,127')
e('DataBackupIntentService.importData@IMPORT', 'BackupHelper.importNotes', 'CALL', 'the notes of the backup folder are imported', guard='the action is a normal import, not the legacy one (importLegacy is false)', evidence='SRC async/DataBackupIntentService.java:123,131-135')
e('DataBackupIntentService.importData@LEGACY', 'BackupHelper.importDB', 'CALL', 'the legacy database file is imported', guard='the action is the legacy import (importLegacy is true)', evidence='SRC async/DataBackupIntentService.java:123,131-133')
# ---- widgets, shortcut, extensions
for wp in ('ListWidgetProvider', 'SimpleWidgetProvider'):
    e('S_ENTRY', wp + '.<init>', 'ENTRY', 'the launcher adds the widget', gui=['Long-press the home screen and add the Omni Notes widget'], env=ENV_LAUNCHER, evidence='SRC AndroidManifest.xml:231-257')
    e(wp + '.<init>', 'WidgetProvider.<init>', 'CALL', 'super()', env=ENV_LAUNCHER, evidence='SRC widget/' + wp + '.java')
    e(wp + '.<init>', 'WidgetProvider.onUpdate@' + wp, 'SYSTEM', 'APPWIDGET_UPDATE', env=ENV_LAUNCHER, evidence='FW-SRC core/java/android/appwidget/AppWidgetProvider.java:57-67 (onReceive calls onUpdate for ACTION_APPWIDGET_UPDATE when the broadcast carries widget ids); SRC widget/WidgetProvider.java:49-60')
    e('WidgetProvider.onUpdate@' + wp, 'WidgetProvider.setLayout@' + wp, 'CALL', 'setLayout(...) for every widget id', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:54-58')
    e('WidgetProvider.setLayout@' + wp, wp + '.getRemoteViews', 'CALL', 'getRemoteViews(...)', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:107')
    e('WidgetProvider.onUpdate@' + wp, 'S_HOME_WIDGET@' + ('LIST' if wp == 'ListWidgetProvider' else 'SIMPLE'), 'ENTERS', 'the widget is drawn on the home screen', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:110')
    gui('S_HOME_WIDGET@' + ('LIST' if wp == 'ListWidgetProvider' else 'SIMPLE'), 'WidgetProvider.onAppWidgetOptionsChanged@' + wp, 'Resize the widget', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:62-69')
    e('WidgetProvider.onAppWidgetOptionsChanged@' + wp, 'WidgetProvider.setLayout@' + wp, 'CALL', 'setLayout(...)', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:67')
gui('S_HOME_WIDGET@LIST', 'MainActivity.onNewIntent@WIDGET_ADD', 'Tap + or the camera button of the widget', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:74-90')
gui('S_HOME_WIDGET@SIMPLE', 'MainActivity.onNewIntent@WIDGET_ADD', 'Tap + or the camera button of the widget', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:74-90')
gui('S_HOME_WIDGET@LIST', 'MainActivity.onNewIntent@WIDGET_LIST', 'Tap the title or a row of the widget', env=ENV_LAUNCHER, evidence='SRC widget/ListWidgetProvider.java:73-78')
gui('S_HOME_WIDGET@SIMPLE', 'MainActivity.onNewIntent@WIDGET_LIST', 'Tap the list button of the widget', env=ENV_LAUNCHER, evidence='SRC widget/WidgetProvider.java:80-84')
e('S_HOME_WIDGET@LIST', 'ListWidgetService.onGetViewFactory', 'SYSTEM', 'the launcher binds the RemoteViewsService', env=ENV_LAUNCHER, evidence='INFERRED the launcher binds the RemoteViewsService through RemoteViewsAdapter (launcher and RemoteViewsAdapter source not read); SRC widget/ListWidgetService.java:27-29')
e('ListWidgetService.onGetViewFactory', 'ListRemoteViewsFactory.<init>', 'CALL', 'new ListRemoteViewsFactory(...)', env=ENV_LAUNCHER, evidence='SRC widget/ListWidgetService.java:28')
for cb in ('onCreate', 'onDataSetChanged', 'getCount', 'getViewAt', 'getViewTypeCount', 'getLoadingView', 'getItemId', 'hasStableIds', 'onDestroy'):
    e('ListRemoteViewsFactory.<init>', 'ListRemoteViewsFactory.' + cb, 'SYSTEM', 'RemoteViewsAdapter calls the factory', env=ENV_LAUNCHER, evidence='INFERRED the launcher binds the RemoteViewsService through RemoteViewsAdapter (launcher and RemoteViewsAdapter source not read); SRC widget/ListRemoteViewsFactory.java:75-166')
e('BaseActivity.notifyAppWidgets', 'ListRemoteViewsFactory.onDataSetChanged', 'FRAMEWORK', 'notifyAppWidgetViewDataChanged reaches the factory', needs_state='A list widget is on the home screen', env=ENV_LAUNCHER, evidence='INFERRED notifyAppWidgetViewDataChanged reaches the RemoteViewsFactory through the launcher (AppWidgetManager and launcher source not read); SRC BaseActivity.java:163-172')
e('S_ENTRY', 'WidgetConfigurationActivity.<init>', 'ENTRY', 'the launcher starts the widget configuration', gui=['Add the Omni Notes list widget to the home screen'], env=ENV_LAUNCHER, evidence='SRC AndroidManifest.xml:222-229')
e('WidgetConfigurationActivity.<init>', 'WidgetConfigurationActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', env=ENV_LAUNCHER, evidence='SRC widget/WidgetConfigurationActivity.java:46-123')
e('WidgetConfigurationActivity.onCreate', 'S_WIDGET_CONFIG', 'ENTERS', 'the configuration dialog is shown', env=ENV_LAUNCHER, evidence='SRC widget/WidgetConfigurationActivity.java:46-123')
gui('S_WIDGET_CONFIG', 'WidgetConfigurationActivity.lambda$onCreate$0', 'Choose "All notes" or "Category"', needs_state=NEED_CATEGORY, env=ENV_LAUNCHER, evidence='SRC widget/WidgetConfigurationActivity.java:54-67')
gui('S_WIDGET_CONFIG', 'WidgetConfigurationActivity.lambda$onCreate$1', 'Tap OK', env=ENV_LAUNCHER, evidence='SRC widget/WidgetConfigurationActivity.java:76-104')
e('WidgetConfigurationActivity.lambda$onCreate$1', 'S_HOME_WIDGET@LIST', 'ENTERS', 'the widget is configured', env=ENV_LAUNCHER, evidence='SRC widget/WidgetConfigurationActivity.java:95-103')
e('WidgetConfigurationActivity.onCreate', 'CategoryBaseAdapter.<init>(Activity,List)', 'CALL', 'the category spinner adapter', env=ENV_LAUNCHER, evidence='SRC widget/WidgetConfigurationActivity.java:73')
e('S_ENTRY', 'ShortcutActivity.<init>', 'ENTRY', 'CREATE_SHORTCUT (launcher "add shortcut")', gui=['Add the Omni Notes "Add note" shortcut to the home screen'], env=ENV_LAUNCHER, evidence='SRC AndroidManifest.xml:170-179')
e('ShortcutActivity.<init>', 'ShortcutActivity.onCreate', 'LIFECYCLE', 'Activity lifecycle', env=ENV_LAUNCHER, evidence='SRC ShortcutActivity.java:30-45')
e('ShortcutActivity.onCreate', 'S_HOME_WIDGET@SIMPLE', 'ENTERS', 'the shortcut is created on the home screen', env=ENV_LAUNCHER, evidence='SRC ShortcutActivity.java:38-44')
gui('S_HOME_WIDGET@SIMPLE', 'MainActivity.onNewIntent@WIDGET_ADD', 'Tap the "Add note" shortcut', env=ENV_LAUNCHER, evidence='SRC ShortcutActivity.java:33-34; MainActivity.java:385-388')
e('S_ENTRY', 'ONDashClockExtension.<init>', 'ENTRY', 'the DashClock app binds the extension', gui=['Add the Omni Notes extension in the DashClock app'], env=ENV_HOSTAPP, evidence='SRC AndroidManifest.xml:264-286')
for cb in ('onInitialize', 'onUpdateData'):
    e('ONDashClockExtension.<init>', 'ONDashClockExtension.' + cb, 'LIFECYCLE', 'DashClock extension callback', env=ENV_HOSTAPP, evidence='SRC extensions/ONDashClockExtension.java:51-100')
e('ONDashClockExtension.onInitialize', 'ONDashClockExtension$DashClockUpdateReceiver.<init>', 'CALL', 'registers the local broadcast receiver', env=ENV_HOSTAPP, evidence='SRC extensions/ONDashClockExtension.java:51-60')
e('BaseActivity.notifyAppWidgets', 'ONDashClockExtension$DashClockUpdateReceiver.onReceive', 'FRAMEWORK', 'LocalBroadcastManager delivers INTENT_UPDATE_DASHCLOCK', needs_state='The DashClock extension is active', env=ENV_HOSTAPP, evidence='INFERRED LocalBroadcastManager delivers the broadcast to the registered receiver (support library source not read); SRC BaseActivity.java:171')
e('S_ENTRY', 'PushBulletExtension.<init>', 'ENTRY', 'the Pushbullet app binds the extension', gui=['Receive a Pushbullet message'], env=ENV_HOSTAPP, evidence='SRC AndroidManifest.xml:288-297')
for cb in ('onMessageReceived', 'onConversationDismissed'):
    e('PushBulletExtension.<init>', 'PushBulletExtension.' + cb, 'LIFECYCLE', 'Pushbullet extension callback', env=ENV_HOSTAPP, evidence='SRC extensions/PushBulletExtension.java:30-45')
e('PushBulletExtension.onMessageReceived', 'DetailFragment.onEventMainThread', 'FRAMEWORK', 'PushbulletReplyEvent', env=ENV_HOSTAPP, needs_state='The editor is open (DetailFragment is registered between onResume and onPause)', evidence=FW_EB + '; SRC extensions/PushBulletExtension.java:35; DetailFragment.java:2162-2165')


# ================================================================== E. remaining wiring: discard / delete dialogs, location, text watcher, parcels, animations, class initialisers
# Discard changes: a new note (plain chain) or a note that already exists (@EXIST chain); the existing-note branch saves the original again (line 1490-1493)
e('DetailFragment.discard', 'S_DLG_DISCARD', 'ENTERS', 'the confirmation opens', evidence='SRC DetailFragment.java:1471-1497')
gui('S_DLG_DISCARD', 'DetailFragment.lambda$discard$18', 'Tap OK', evidence=FW_MD + '; SRC DetailFragment.java:1475-1496')
e('DetailFragment.discard@EXIST', 'S_DLG_DISCARD@EXIST', 'ENTERS', 'the confirmation opens', evidence='SRC DetailFragment.java:1471-1497')
gui('S_DLG_DISCARD@EXIST', 'DetailFragment.lambda$discard$18@EXIST', 'Tap OK', evidence=FW_MD + '; SRC DetailFragment.java:1475-1496')
sup(('DetailFragment.lambda$discard$18', 'SaveNoteTask.<init>(OnNoteSaved,boolean)'), ('DetailFragment.lambda$discard$18', 'StorageHelper.delete'), ('DetailFragment.lambda$discard$18', 'Attachment.getUri'),
    ('DetailFragment.lambda$discard$18', 'BaseActivity.notifyAppWidgets'))
_EXISTS = 'the note already exists: noteOriginal.get_id() is not null (DetailFragment.java:1490)'
e('DetailFragment.lambda$discard$18@EXIST', 'SaveNoteTask.<init>(OnNoteSaved,boolean)', 'CALL', 'an existing note is restored to its original state', guard=_EXISTS, evidence='SRC DetailFragment.java:1490-1493')
e('DetailFragment.lambda$discard$18@EXIST', 'SaveNoteTask.doInBackground', 'ASYNC', 'executeOnExecutor(noteOriginal)', guard=_EXISTS, evidence=FW_ASYNC + '; SRC DetailFragment.java:1491')
e('DetailFragment.lambda$discard$18@EXIST', 'BaseActivity.notifyAppWidgets', 'CALL', 'the widgets are refreshed', guard=_EXISTS, evidence='SRC DetailFragment.java:1492')
for v in ('DetailFragment.lambda$discard$18', 'DetailFragment.lambda$discard$18@EXIST'):
    for dst in ('StorageHelper.delete', 'Attachment.getUri'):
        e(v, dst, 'CALL', 'attachments added in this session are deleted', needs_state='An attachment was added in this editing session', evidence='SRC DetailFragment.java:1476-1482')
    e(v, 'S_LIST@NOTES', 'ENTERS', 'the changes are dropped and the list is shown', evidence='SRC DetailFragment.java:1484-1495')
e('S_DLG_DISCARD', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('S_DLG_DISCARD@EXIST', 'S_DETAIL@EDIT', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('DetailFragment.deleteNote', 'S_DLG_DELETE_NOTE', 'ENTERS', 'the confirmation opens', evidence='SRC DetailFragment.java:1535-1545')
gui('S_DLG_DELETE_NOTE', 'DetailFragment.lambda$deleteNote$19', 'Tap OK', evidence=FW_MD + '; SRC DetailFragment.java:1539-1544')
e('DetailFragment.lambda$deleteNote$19', 'S_LIST@TRASH', 'ENTERS', 'the note is deleted for good and the list is shown', evidence='SRC DetailFragment.java:1539-1544')
e('S_DLG_DELETE_NOTE', 'S_DETAIL@TRASHED', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], evidence=BACK_DLG)
e('MainActivity.deleteNote', 'NoteProcessor.process@DELETE', 'CALL', 'new NoteProcessorDelete(...).process()', evidence='SRC MainActivity.java:514-518')
sup(('MainActivity.deleteNote', 'NoteProcessor.process'))
e('MainActivity.showMessage(String,Style)', 'MainActivity.lambda$showMessage$2', 'ASYNC', 'runOnUiThread(Crouton.makeText(...).show())', evidence=FW_POST + '; SRC MainActivity.java:532-535')
# text watcher of the content field and the title
for pg in DVARS:
    for cb in ('beforeTextChanged', 'afterTextChanged'):
        gui('S_DETAIL@' + pg, 'DetailFragment.' + cb, 'Type in the note', evidence='SRC DetailFragment.java:2010-2023')
# password caller edges that were suppressed with BaseActivity.requestPassword
for cal, need in (('ListFragment.lambda$deleteNotes$12', None), ('ListFragment$3.onClick', NEED_LOCKED), ('ListFragment.lambda$onOptionsItemSelected$6', None)):
    pass
for it in ('CATEGORY', 'TAGS', 'SHARE', 'ARCHIVE', 'UNARCHIVE', 'TRASH', 'UNTRASH', 'DELETE', 'REMINDER'):
    e('ListFragment$ModeCallback.onActionItemClicked@' + it, 'BaseActivity.requestPassword', 'CALL', 'requestPassword(activity, selected notes, validator)', evidence='SRC ListFragment.java:454')
e('ListFragment.onOptionsItemSelected@EMPTY_TRASH', 'BaseActivity.requestPassword', 'CALL', 'requestPassword(activity, selected notes, validator)', evidence='SRC ListFragment.java:783')
e('ListFragment.lambda$deleteNotes$12', 'BaseActivity.requestPassword', 'CALL', 'requestPassword(activity, selected notes, validator)', evidence='SRC ListFragment.java:1356')
e('ListFragment$3.onClick', 'BaseActivity.requestPassword', 'CALL', 'requestPassword(...) when a locked note is among them', needs_state=NEED_LOCKED, evidence='SRC ListFragment.java:1031-1038')
e('BaseActivity.requestPassword', 'PasswordHelper.requestPassword', 'CALL', 'a selected note is locked and password access is off: ask for the password', needs_state=NEED_LOCKED, evidence='SRC BaseActivity.java:115-134')
# ---- location
sup(('DetailFragment.initViewLocation', 'DetailFragment.getLocation'), ('DetailFragment.displayLocationDialog', 'DetailFragment.getLocation'), ('DetailFragment.initViewLocation', 'GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)'),
    ('DetailFragment.getLocation', 'PermissionsHelper.requestPermission'))
sup('GeocodeHelper$1.onNext', 'GeocodeHelper$1.onError', 'GeocodeHelper.getLocation', 'DetailFragment.lambda$getLocation$7')
e('DetailFragment.initViewLocation', 'DetailFragment.getLocation@AUTO', 'CALL', 'getLocation(this): a new note gets the current location', needs_state=NEED_AUTOLOC, evidence='SRC DetailFragment.java:700-702')
e('DetailFragment.initViewLocation', 'GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)', 'CALL', 'the note has coordinates but no address', needs_state=NEED_LOCATION, evidence='SRC DetailFragment.java:689-696')
e('DetailFragment.displayLocationDialog', 'DetailFragment.getLocation@DIALOG', 'CALL', 'getLocation(new OnGeoUtilResultListenerImpl(...))', evidence='SRC DetailFragment.java:947-949')
for k in ('AUTO', 'DIALOG'):
    gl = 'DetailFragment.getLocation@' + k
    lam = 'DetailFragment.lambda$getLocation$7@' + k
    ggl = 'GeocodeHelper.getLocation@' + k
    e(gl, 'PermissionsHelper.requestPermission', 'CALL', 'requestPermission(ACCESS_FINE_LOCATION, ..., callback)', evidence='SRC DetailFragment.java:733-737')
    e(gl, lam, 'CALL', 'ACCESS_FINE_LOCATION is granted: the callback runs', needs_state=NEED_PERM_LOCATION, evidence='SRC DetailFragment.java:734-736')
    e(lam, ggl, 'CALL', 'GeocodeHelper.getLocation(listener)', evidence='SRC DetailFragment.java:735-736')
    for dst in ('GeocodeHelper$1.<init>', 'GeocodeProviderBaseFactory.getProvider', 'OmniNotes.getAppContext'):
        e(ggl, dst, 'CALL', 'call in getLocation', evidence='SRC utils/GeocodeHelper.java:86-110')
    e(ggl, 'GeocodeHelper$1.onNext@' + k, 'FRAMEWORK', 'SmartLocation delivers a one-shot fix', env=ENV_LOCATION, evidence='INFERRED SmartLocation / RxJava deliver the fix (library source not read); SRC utils/GeocodeHelper.java:86-111')
    e(ggl, 'GeocodeHelper$1.onError@' + k, 'FRAMEWORK', 'no fix within 2 s: the observable times out', env=ENV_NOFIX, evidence='INFERRED RxJava delivers the timeout (library source not read); SRC utils/GeocodeHelper.java:91,105-108')
    e(ggl, 'GeocodeHelper$1.onCompleted', 'FRAMEWORK', 'the observable completes after the fix', env=ENV_LOCATION, evidence='INFERRED RxJava delivers the completion (library source not read); SRC utils/GeocodeHelper.java:100-103')
e('GeocodeHelper$1.onNext@AUTO', 'DetailFragment.onLocationRetrieved', 'CALL', 'listener.onLocationRetrieved(location)', env=ENV_LOCATION, evidence='SRC utils/GeocodeHelper.java:95')
e('GeocodeHelper$1.onNext@DIALOG', 'DetailFragment$OnGeoUtilResultListenerImpl.onLocationRetrieved', 'CALL', 'listener.onLocationRetrieved(location)', env=ENV_LOCATION, evidence='SRC utils/GeocodeHelper.java:95')
e('GeocodeHelper$1.onError@AUTO', 'DetailFragment.onLocationUnavailable', 'CALL', 'listener.onLocationUnavailable()', evidence='SRC utils/GeocodeHelper.java:106')
e('GeocodeHelper$1.onError@DIALOG', 'DetailFragment$OnGeoUtilResultListenerImpl.onLocationUnavailable', 'CALL', 'listener.onLocationUnavailable()', evidence='SRC utils/GeocodeHelper.java:106')
for k in ('AUTO', 'DIALOG'):
    for cb in ('onNext', 'onError'):
        e('GeocodeHelper$1.%s@%s' % (cb, k), 'GeocodeHelper$1.' + cb, 'CALL', '%s(...)' % cb, env=ENV_LOCATION if cb == 'onNext' else None, evidence='SRC utils/GeocodeHelper.java:92-110')
e('DetailFragment$OnGeoUtilResultListenerImpl.onLocationRetrieved', 'S_DLG_LOCATION', 'ENTERS', 'internet is available: the location search dialog opens', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2195-2255')
e('DetailFragment$OnGeoUtilResultListenerImpl.onLocationRetrieved', 'S_DETAIL@NEW', 'ENTERS', 'no internet: the coordinates are stored at once', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2204-2209')
e('DetailFragment$OnGeoUtilResultListenerImpl.onLocationRetrieved', 'PlacesAutoCompleteAdapter.<init>', 'CALL', 'the dialog autocomplete adapter', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2215-2216')
e('DetailFragment$OnGeoUtilResultListenerImpl.onLocationRetrieved', 'DetailFragment$OnGeoUtilResultListenerImpl$1.<init>', 'CALL', 'the text watcher of the search field', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2231')
e('DetailFragment$OnGeoUtilResultListenerImpl.onLocationUnavailable', 'S_DETAIL@NEW', 'ENTERS', 'a "location not found" message is shown', evidence='SRC DetailFragment.java:2190-2193')
e('DetailFragment.onLocationUnavailable', 'S_DETAIL@NEW', 'ENTERS', 'a "location not found" message is shown', evidence='SRC DetailFragment.java:969-972')
for cb in ('onTextChanged', 'beforeTextChanged', 'afterTextChanged'):
    gui('S_DLG_LOCATION', 'DetailFragment$OnGeoUtilResultListenerImpl$1.' + cb, 'Type an address', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2231-2252')
gui('S_DLG_LOCATION', 'PlacesAutoCompleteAdapter.getFilter', 'Type an address (the autocomplete list)', env=ENV_LOCATION, evidence='SRC models/adapters/PlacesAutoCompleteAdapter.java')
for cb in ('getCount', 'getItem'):
    e('S_DLG_LOCATION', 'PlacesAutoCompleteAdapter.' + cb, 'FRAMEWORK', 'AutoCompleteTextView reads the suggestions', env=ENV_LOCATION, evidence=FW_VIEW + '; SRC models/adapters/PlacesAutoCompleteAdapter.java')
e('PlacesAutoCompleteAdapter.getFilter', 'PlacesAutoCompleteAdapter$1.<init>', 'CALL', 'the filter', env=ENV_LOCATION, evidence='SRC models/adapters/PlacesAutoCompleteAdapter.java')
e('PlacesAutoCompleteAdapter.getFilter', 'PlacesAutoCompleteAdapter$1.performFiltering', 'ASYNC', 'Filter.filter runs performFiltering on a worker thread', env=ENV_LOCATION, evidence=FW_ASYNC + '; SRC models/adapters/PlacesAutoCompleteAdapter.java')
e('PlacesAutoCompleteAdapter$1.performFiltering', 'PlacesAutoCompleteAdapter$1.publishResults', 'ASYNC', 'the suggestions are published on the main thread', env=ENV_LOCATION, evidence=FW_ASYNC)
gui('S_DLG_LOCATION', 'DetailFragment$OnGeoUtilResultListenerImpl.lambda$onLocationRetrieved$0', 'Tap "Use current location" or Confirm', env=ENV_LOCATION, evidence=FW_MD + '; SRC DetailFragment.java:2220-2229')
e('DetailFragment$OnGeoUtilResultListenerImpl.lambda$onLocationRetrieved$0', 'S_DETAIL@NEW', 'ENTERS', 'the location is stored and the dialog closes', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2220-2229')
e('S_DLG_LOCATION', 'S_DETAIL@NEW', 'ENTERS', 'Press Back: the dialog is dismissed', gui=['Press Back'], env=ENV_LOCATION, evidence=BACK_DLG)
e('GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)', 'GeocodeHelper.lambda$getAddressFromCoordinates$0', 'FRAMEWORK', 'SmartLocation geocoding calls back with the address', env=ENV_GEO, evidence='INFERRED SmartLocation geocoding delivers the result (library source not read); SRC utils/GeocodeHelper.java:141-145')
e('GeocodeHelper.getCoordinatesFromAddress(String,OnGeoUtilResultListener)', 'GeocodeHelper.lambda$getCoordinatesFromAddress$1', 'FRAMEWORK', 'SmartLocation geocoding calls back with the coordinates', env=ENV_GEO, evidence='INFERRED SmartLocation geocoding delivers the result (library source not read); SRC utils/GeocodeHelper.java:166-171')
e('DetailFragment.onLocationRetrieved', 'GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)', 'CALL', 'resolves the address', env=ENV_LOCATION, evidence='SRC DetailFragment.java:963')
sup(('DetailFragment.onLocationRetrieved', 'GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)'))
e('DetailFragment$OnGeoUtilResultListenerImpl.lambda$onLocationRetrieved$0', 'GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)', 'CALL', 'use the current location', guard='the address field is empty', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2221-2225')
e('DetailFragment$OnGeoUtilResultListenerImpl.lambda$onLocationRetrieved$0', 'GeocodeHelper.getCoordinatesFromAddress(String,OnGeoUtilResultListener)', 'CALL', 'use the typed address', guard='the address field is not empty', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2225-2228')
sup(('DetailFragment$OnGeoUtilResultListenerImpl.lambda$onLocationRetrieved$0', 'GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)'), ('DetailFragment$OnGeoUtilResultListenerImpl.lambda$onLocationRetrieved$0', 'GeocodeHelper.getCoordinatesFromAddress(String,OnGeoUtilResultListener)'))
for dst in ('GeocodeHelper.getAddressFromCoordinates(Location,OnGeoUtilResultListener)', 'GeocodeHelper.getCoordinatesFromAddress(String,OnGeoUtilResultListener)'):
    e('DetailFragment$OnGeoUtilResultListenerImpl.lambda$onLocationRetrieved$0', dst, 'CALL', 'resolve the address / coordinates', env=ENV_LOCATION, evidence='SRC DetailFragment.java:2220-2229')
for k, v in (('GeocodeHelper.lambda$getAddressFromCoordinates$0', 'onAddressResolved'), ('GeocodeHelper.lambda$getCoordinatesFromAddress$1', 'onCoordinatesResolved')):
    sup((k, 'DetailFragment$OnGeoUtilResultListenerImpl.' + v))
# ---- Parcelable plumbing (framework writes and reads the notes, categories and attachments that travel in intents)
FWP = ('FW-SRC core/java/android/os/Parcel.java:1785-1791, 2867-2900 (writeParcelable calls writeToParcel; readParcelableCreator finds the static CREATOR field of the class by reflection, and readParcelable calls its createFromParcel); '
       'INFERRED Intent / Bundle extras and Intent.hasFileDescriptors reach them (Intent and Bundle source not read)')
e('ReminderHelper.addReminder(Context,Note,long)', 'Note.writeToParcel', 'FRAMEWORK', 'ParcelableUtil.marshall(note)', needs_state=NEED_REMINDER, evidence=FWP + '; SRC utils/ReminderHelper.java:53; utils/ParcelableUtil.java')
e('ReminderHelper.addReminder(Context,Note,long)', 'ParcelableUtil.marshall', 'CALL', 'marshalls the note into the alarm intent', needs_state=NEED_REMINDER, evidence='SRC utils/ReminderHelper.java:53')
sup(('ReminderHelper.addReminder(Context,Note,long)', 'ParcelableUtil.marshall'))
e('AlarmReceiver.onReceive', 'Note$1.createFromParcel', 'FRAMEWORK', 'ParcelableUtil.unmarshall(bytes, CREATOR)', needs_state=NEED_REMINDER_FIRED, evidence=FWP + '; SRC receiver/AlarmReceiver.java:56-57')
e('Note.writeToParcel', 'Category.writeToParcel', 'FRAMEWORK', 'dest.writeParcelable(category)', needs_state=NEED_CATEGORY, evidence=FWP + '; SRC models/Note.java')
e('Note.writeToParcel', 'Attachment.writeToParcel', 'FRAMEWORK', 'dest.writeList(attachments)', needs_state=NEED_ATTACH, evidence=FWP + '; SRC models/Note.java')
e('Note$1.createFromParcel', 'Note.<init>(Parcel)', 'CALL', 'new Note(parcel)', evidence='SRC models/Note.java')
e('Note.<init>(Parcel)', 'Category$1.createFromParcel', 'FRAMEWORK', 'readParcelable(category)', needs_state=NEED_CATEGORY, evidence=FWP + '; SRC models/Note.java')
e('Note.<init>(Parcel)', 'Attachment$1.createFromParcel', 'FRAMEWORK', 'readList(attachments)', needs_state=NEED_ATTACH, evidence=FWP + '; SRC models/Note.java')
e('Category$1.createFromParcel', 'Category.<init>(Parcel)', 'CALL', 'new Category(parcel)', evidence='SRC models/Category.java')
e('Attachment$1.createFromParcel', 'Attachment.<init>(Parcel)', 'CALL', 'new Attachment(parcel)', evidence='SRC models/Attachment.java')
for caller in ('DetailFragment.showNoteInfo', 'AlarmReceiver.createNotification'):
    for cb in ('writeToParcel', 'describeContents'):
        e(caller, 'Note.' + cb, 'FRAMEWORK', 'the note travels in an Intent extra', needs_state=NEED_REMINDER_FIRED if caller.startswith('Alarm') else None, evidence=FWP)
e('ListFragment.addReminders', 'Note.writeToParcel', 'FRAMEWORK', 'the selected notes travel in an Intent extra array', evidence=FWP + '; SRC ListFragment.java:896')
e('ListFragment.addReminders', 'Note.describeContents', 'FRAMEWORK', 'Intent.hasFileDescriptors', evidence=FWP)
e('NoteInfosActivity.onCreate', 'Note$1.createFromParcel', 'FRAMEWORK', 'getParcelable(INTENT_NOTE)', evidence=FWP + '; SRC NoteInfosActivity.java:65')
e('SnoozeActivity.onCreate', 'Note$1.createFromParcel', 'FRAMEWORK', 'getParcelableExtra / getExtras().get(INTENT_NOTE)', evidence=FWP + '; SRC SnoozeActivity.java:85-90')
e('DetailFragment.onSaveInstanceState', 'Note.writeToParcel', 'FRAMEWORK', 'the three notes are written to the saved state', needs_state='The editor state is saved (rotation, Home key) after the title or text was touched', evidence=FWP + '; SRC DetailFragment.java:403-414')
e('DetailFragment.onActivityCreated', 'Note$1.createFromParcel', 'FRAMEWORK', 'noteTmp = savedInstanceState.getParcelable("noteTmp")', needs_state='The editor was recreated after a rotation', evidence=FWP + '; SRC DetailFragment.java:376-381')
e('ListFragment.editCategory', 'Category.writeToParcel', 'FRAMEWORK', 'the category travels in an Intent extra', needs_state=NEED_CATEGORY, evidence=FWP + '; SRC ListFragment.java:1465')
e('ListFragment.editCategory', 'Category.describeContents', 'FRAMEWORK', 'Intent.hasFileDescriptors', needs_state=NEED_CATEGORY, evidence=FWP)
e('CategoryActivity.onCreate', 'Category$1.createFromParcel', 'FRAMEWORK', 'getParcelableExtra(INTENT_CATEGORY)', needs_state=NEED_CATEGORY, evidence=FWP + '; SRC CategoryActivity.java:73')
e('CategoryActivity.saveCategory', 'Category.writeToParcel', 'FRAMEWORK', 'the saved category travels back in the result Intent', evidence=FWP + '; SRC CategoryActivity.java:156-157')
e('DetailFragment.onActivityResult@CATEGORY', 'Category$1.createFromParcel', 'FRAMEWORK', 'intent.getParcelableExtra("category")', evidence=FWP + '; SRC DetailFragment.java:1440')
e('DetailFragment.lambda$initViewAttachments$8@MEDIA', 'Attachment.writeToParcel', 'FRAMEWORK', 'putParcelableArrayListExtra(GALLERY_IMAGES, images)', evidence=FWP + '; SRC DetailFragment.java:799')
e('DetailFragment.lambda$initViewAttachments$8@MEDIA', 'Attachment.describeContents', 'FRAMEWORK', 'Intent.hasFileDescriptors', evidence=FWP)
e('GalleryActivity.onCreate', 'Attachment$1.createFromParcel', 'FRAMEWORK', 'getParcelableArrayListExtra(GALLERY_IMAGES)', evidence=FWP + '; SRC GalleryActivity.java:172')
for cls in ('Note', 'Category', 'Attachment'):
    pass
# ---- animations and listeners driven by the framework
e('AnimationsHelper.zoomListItem', 'ListFragment$1.onAnimationEnd', 'FRAMEWORK', 'the zoom animation ends: the note opens', evidence=FW_VIEW + '; SRC ListFragment.java:561-568; utils/AnimationsHelper.java')
e('ListFragment.editNote', 'AnimationsHelper.zoomListItem', 'CALL', 'zoomListItem(...)', evidence='SRC ListFragment.java:922-923')
for cb in ('onAnimationStart', 'onAnimationEnd'):
    e('AnimationsHelper.expandOrCollapse', 'AnimationsHelper$1.' + cb, 'FRAMEWORK', 'the expand / collapse animation runs', needs_state='The search label was shown and closed', evidence=FW_VIEW + '; SRC utils/AnimationsHelper.java')
    e('Fab.animateFab', 'Fab$3.' + cb, 'FRAMEWORK', 'the FAB slide animation runs', evidence=FW_VIEW + '; SRC models/views/Fab.java:146-166')
for cb in ('onScrollStateChanged',):
    e('S_LIST@NOTES', 'AbsListViewScrollDetector.' + cb, 'GUI', 'Scroll the notes list', gui=['Scroll the notes list'], needs_state='The list has enough notes to scroll (about 6 or more)', evidence=FW_VIEW + '; SRC models/listeners/AbsListViewScrollDetector.java')
e('ListFragment.onUndo', 'NoteAdapter.add', 'FRAMEWORK', 'list.insert(position, note) calls the adapter\'s Insertable.add', needs_state='An archived or trashed note is undone in the Notes list', evidence='INFERRED the listviewanimations library calls the Insertable.add of the adapter (library source not read); SRC ListFragment.java:1659-1663')
e('NavigationDrawerFragment.<init>', 'NavigationDrawerFragment.onStop', 'LIFECYCLE', 'Fragment lifecycle callback', evidence=FW_FRAG + '; SRC NavigationDrawerFragment.java:75-79')
# ---- inflated views
e('ListFragment.onCreateView', 'InterceptorLinearLayout.<init>(Context,AttributeSet)', 'FRAMEWORK', 'the layout inflates the root', evidence='FW-SRC core/java/android/view/LayoutInflater.java:612-617, 645-648 (createView looks up the (Context, AttributeSet) constructor of the view class and calls newInstance); SRC res/layout/fragment_list.xml')
e('GalleryActivity.onCreate', 'InterceptorFrameLayout.<init>(Context,AttributeSet)', 'FRAMEWORK', 'the layout inflates the root', evidence='FW-SRC core/java/android/view/LayoutInflater.java:612-617, 645-648 (createView looks up the (Context, AttributeSet) constructor of the view class and calls newInstance); SRC res/layout/activity_gallery.xml')
e('DetailFragment.initViewAttachments', 'ExpandableHeightGridView.<init>(Context,AttributeSet)', 'FRAMEWORK', 'the ViewStub inflates the grid', evidence='INFERRED ViewStub.inflate inflates the layout (ViewStub source not read) and LayoutInflater then calls the view constructor; SRC res/layout/fragment_detail.xml')
e('MainActivity.onCreate', 'NonScrollableListView.<init>(Context,AttributeSet)', 'FRAMEWORK', 'the drawer layout inflates its two lists', evidence='FW-SRC core/java/android/view/LayoutInflater.java:612-617, 645-648 (createView looks up the (Context, AttributeSet) constructor of the view class and calls newInstance); SRC res/layout/fragment_navigation_drawer.xml')
e('DetailFragment.initViewAttachments', 'ExpandableHeightGridView.onMeasure', 'FRAMEWORK', 'measure pass of the grid', evidence=FW_VIEW)
e('AttachmentAdapter.getView', 'SquareImageView.<init>(Context,AttributeSet)', 'FRAMEWORK', 'the cell layout inflates the picture', needs_state=NEED_ATTACH, evidence='FW-SRC core/java/android/view/LayoutInflater.java:612-617, 645-648 (createView looks up the (Context, AttributeSet) constructor of the view class and calls newInstance); SRC res/layout/gridview_item.xml')
e('AttachmentAdapter.getView', 'SquareImageView.onMeasure', 'FRAMEWORK', 'measure pass of the cell', needs_state=NEED_ATTACH, evidence=FW_VIEW)
# ---- first use of classes with static initialisers
INIT = [('Note.<init>()', 'Note.<clinit>'), ('DbHelper.getInstance()', 'DbHelper.<clinit>'), ('Category.<init>(Long,String,String,String)', 'Category.<clinit>'),
        ('Attachment.<init>(Uri,String)', 'Attachment.<clinit>'), ('NotificationsHelper.initNotificationChannels', 'NotificationChannels.<clinit>'),
        ('SwitchFragmentEvent.<init>', 'SwitchFragmentEvent$Direction.<clinit>'), ('MainActivity.showMessage(String,Style)', 'ONStyle.<clinit>'), ('BaseActivity.requestPassword', 'PasswordValidator$Result.<clinit>'),
        ('SettingsFragment.onCreate', 'ResourcesUtils$ResourceIdentifiers.<clinit>'), ('ListRemoteViewsFactory.<init>', 'ListRemoteViewsFactory.<clinit>'),
        ('ONDashClockExtension.onUpdateData', 'ONDashClockExtension$Counters.<clinit>')]
for src, dst in INIT:
    e(src, dst, 'CALL', 'class initialisation on first use', evidence='INFERRED the class has a static initialiser that the JVM runs on first use of the class (Java language rule, not read from a source)')
e('Tag.<init>(String,Integer)', 'Tag.<clinit>', 'CALL', 'class initialisation on first use', needs_state=NEED_TAGS, evidence='SRC models/Tag.java (static CREATOR field); INFERRED the class has a static initialiser that the JVM runs on first use of the class (Java language rule, not read from a source)')
# ---- database creation and upgrade
e('DbHelper.getDatabase(boolean)', 'DbHelper.onCreate', 'FRAMEWORK', 'SQLiteOpenHelper creates the database on first access', guard='no database file yet', evidence='FW-SRC core/java/android/database/sqlite/SQLiteOpenHelper.java:266-270, 326-351 (getDatabaseLocked calls onCreate for a new database, onUpgrade for an older version, and onOpen afterwards); SRC db/DbHelper.java:180-188')
e('DbHelper.getDatabase(boolean)', 'DbHelper.onOpen', 'FRAMEWORK', 'SQLiteOpenHelper opens the database', evidence='FW-SRC core/java/android/database/sqlite/SQLiteOpenHelper.java:266-270, 326-351 (getDatabaseLocked calls onCreate for a new database, onUpgrade for an older version, and onOpen afterwards); SRC db/DbHelper.java')
e('DbHelper.getDatabase(boolean)', 'DbHelper.onUpgrade', 'FRAMEWORK', 'SQLiteOpenHelper upgrades an older database', env='an older database version is on disk (install an old build with data, then update)', evidence='FW-SRC core/java/android/database/sqlite/SQLiteOpenHelper.java:266-270, 326-351 (getDatabaseLocked calls onCreate for a new database, onUpgrade for an older version, and onOpen afterwards); SRC db/DbHelper.java:191-214')
e('UpgradeProcessor.process', 'UpgradeProcessor.getMethodsToLaunch', 'CALL', 'finds the upgrade methods', env='an older database version is on disk', evidence='SRC async/upgrade/UpgradeProcessor.java:68-95')
for ver in ('476', '480', '482', '501'):
    e('UpgradeProcessor.process', 'UpgradeProcessor.onUpgradeTo' + ver, 'CALL', 'reflection: onUpgradeTo%s' % ver, env='an older database version is on disk', evidence='SRC async/upgrade/UpgradeProcessor.java:68-95; INFERRED java.lang.reflect.Method.invoke calls the method (libcore source not read)')
e('DbHelper.onUpgrade', 'UpgradeProcessor.process', 'CALL', 'UpgradeProcessor.process(old, new)', env='an older database version is on disk', evidence='SRC db/DbHelper.java:191-214')


# ---- lambdas that the library (Rx, streams, Handler) runs synchronously or later
ENV_CJK = 'the device locale is ja_JP, zh_CN or zh_TW (the Application context carries the device locale; CountFactory.java:33-40 picks IdeogramsWordCounter)'
for c in AUTO['lambdas']:
    if c['dst'] in ('DbHelper.lambda$getTags$0', 'DbHelper.lambda$null$1', 'DbHelper.lambda$getNotesByTag$2', 'TagsHelper.lambda$removeTag$0', 'TagsHelper.lambda$removeTag$1', 'TagsHelper.lambda$removeTag$2',
                    'TagsHelper.lambda$removeTag$3', 'DefaultWordCounter.lambda$countChars$0', 'ReminderHelper.lambda$showReminderMessage$0',
                    'SpringImportHelper.lambda$importDataFromSpringpad$0', 'DynamicNavigationLookupTable.lambda$update$0'):
        e(c['src'], c['dst'], 'FRAMEWORK', 'the library / Handler runs the lambda', needs_state=NEED_TAGS if c['dst'].startswith(('DbHelper.lambda$getTags', 'DbHelper.lambda$null', 'DbHelper.lambda$getNotesByTag', 'TagsHelper.lambda')) else None,
          evidence='INFERRED Rx / streams / Handler run the lambda (RxJava and stream library source not read); SRC %s:%d' % (c['file'], c['line']))
e('IdeogramsWordCounter.countChars', 'IdeogramsWordCounter.lambda$countChars$0', 'FRAMEWORK', 'the stream runs the lambda', env=ENV_CJK, evidence='INFERRED the stream runs the lambda (java.util.stream source not read); SRC helpers/count/IdeogramsWordCounter.java')
for c in AUTO['calls']:
    if c['dst'].startswith('IdeogramsWordCounter.') and not c['src'].startswith('IdeogramsWordCounter.'):
        sup((c['src'], c['dst']))
        e(c['src'], c['dst'], 'CALL', 'the ideogram word counter is used only for CJK locales', env=ENV_CJK, evidence='SRC %s:%d (bytecode)' % (c['file'], c['line']))
e('S_HOME_WIDGET@LIST', 'ListWidgetService.<init>', 'SYSTEM', 'the launcher binds the RemoteViewsService', env=ENV_LAUNCHER, evidence='INFERRED the launcher binds the RemoteViewsService through RemoteViewsAdapter (launcher and RemoteViewsAdapter source not read); SRC AndroidManifest.xml:259-261')
e('DataBackupIntentService.exportData', 'BackupException.<init>', 'CALL', 'a backup step failed', env=ENV_EXC, evidence='SRC async/DataBackupIntentService.java')
# ---- verdicts
def _by(*prefixes):
    return [m for m in METHODS if any(m.startswith(p + '.') for p in prefixes)]


def _dead(names, reason):
    for n in names:
        if n in METHODS:
            DEAD[n] = reason


def _fw(names, reason):
    for n in names:
        if n in METHODS:
            FRAMEWORK_ONLY[n] = reason


R_UPDATER = 'The updater is never started: its only start site (new UpdaterTask) is commented out at MainActivity.java:107; AppVersionHelper and MiscUtils.isGooglePlayAvailable are used only by it'
_dead(_by('UpdaterTask', 'UpdaterTask$1', 'PlayStoreMetadataFetcherResult'), R_UPDATER)
_dead(['AppVersionHelper.getAppVersionFromPreferences', 'AppVersionHelper.getCurrentAppVersion', 'AppVersionHelper.isAppUpdated', 'AppVersionHelper.updateAppVersionInPreferences', 'MiscUtils.isGooglePlayAvailable'], R_UPDATER)
_dead(['Display.' + n for n in ('<init>', 'getActionbarHeight', 'getFullSize', 'getNavigationBarHeight', 'getNavigationBarHeightStandard', 'getRootView', 'getSoftButtonsBarHeight', 'getStatusBarHeight', 'getVisibleSize', 'orientationLandscape')], 'No caller anywhere in the app (unused screen-size helpers of Display)')
_dead(_by('VerticalSeekBar'), 'Never instantiated and in no layout: the sketch popups use a plain SeekBar (res/layout/popup_sketch_stroke.xml)')
_dead(_by('ImageAndTextItem', 'LoadingDialog') + ['PushBulletMessage.<init>'], 'Never instantiated and in no layout')
_dead(['GeocodeHelper.<init>', 'GeocodeHelper.onLocationChanged', 'GeocodeHelper.onStatusChanged', 'GeocodeHelper.onProviderEnabled', 'GeocodeHelper.onProviderDisabled', 'GeocodeHelper.getAddressFromCoordinates(Context,double,double)'],
      'GeocodeHelper is used only through its static methods; the LocationListener part is never instantiated, and the Context overload is called only by androidTest')
_dead(_by('GeocodeProviderFactory') + ['GeocodeProviderBaseFactory.<init>'], 'The play-flavor factory is compiled in but GeocodeHelper statically imports the base factory; the base factory has only static use')
_dead(['DbHelper.emptyTrash', 'DbHelper.getCategorizedCount', 'DbHelper.getChecklists', 'DbHelper.getMasked', 'DbHelper.getNotesWithLocation', 'DbHelper.getTodayReminders'], 'No caller: the list empties the trash with NoteProcessorDelete and none of these queries is used by the UI')
_fw(['DbHelper.getDatabaseName'], 'Override of SQLiteOpenHelper.getDatabaseName(): no app caller')
_dead(['BackupHelper.<init>', 'BackupHelper.deleteNote', 'BackupHelper.deleteNoteBackup', 'BackupHelper.exportAttachments(File)', 'BackupHelper.importAttachments(File)', 'BackupHelper.importAttachments(Note,File)',
       'BackupHelper.integrityCheck', 'BackupHelper.addIntegrityCheckError'], 'No caller in the app (integrityCheck is used by androidTest only; the "integrity check" preference has no handler)')
_dead(['StorageHelper.<init>', 'StorageHelper.copyDirectory', 'StorageHelper.createNewAttachmentFile(Context)', 'StorageHelper.getDbSyncDir', 'StorageHelper.getRealPathFromURI', 'StorageHelper.getStorageDir',
       'DateUtils.<init>', 'DateUtils.getDateFromString', 'DateUtils.getLongFromDateTime', 'DateUtils.getString(Date,String)', 'DateUtils.getString(long,String)', 'DateUtils.prettyTime(String)',
       'DateHelper.<init>', 'DateHelper.getSortableDate', 'DateHelper.getTimeShort(Context,int,int)', 'DateHelper.getTimeShort(Context,Long)', 'DateHelper.onDateSet', 'DateHelper.onTimeSet',
       'FileHelper.<init>', 'FileHelper.getFileExtension(File)', 'FileHelper.getFilePrefix(File)', 'FileHelper.getFilePrefix(String)', 'ColorsUtil.<init>', 'ColorsUtil.calculateColorLuminance', 'ColorsUtil.getContrastedColor',
       'AssetUtils.<init>', 'AssetUtils.exists', 'KeyboardUtils.<init>', 'KeyboardUtils.hideKeyboard(MainActivity)', 'LanguageHelper.<init>', 'LanguageHelper.getLocalizedString', 'IntentChecker.<init>',
       'IntentChecker.resolveActivityPackage', 'ReminderHelper.<init>', 'ReminderHelper.checkReminder', 'SystemHelper.<init>', 'SystemHelper.copyToClipboard', 'NotificationsHelper.cancel(int)', 'NotificationsHelper.setIcon'],
      'No caller in the app (static helpers kept for tests or never used; the constructors of static-only classes are never called)')
_dead(['AppVersionHelper.<init>', 'MiscUtils.<init>', 'TagsHelper.<init>', 'TextHelper.<init>', 'SqlParser.<init>', 'Security.<init>', 'ResourcesUtils.<init>', 'RecurrenceHelper.<init>', 'PermissionsHelper.<init>', 'PasswordHelper.<init>', 'ParcelableUtil.<init>',
       'ONStyle.<init>', 'NotificationChannels.<init>', 'NotesHelper.<init>', 'Navigation.<init>', 'LogDelegate.<init>', 'FileProviderHelper.<init>', 'CountFactory.<init>', 'ConnectionManager.<init>',
       'BitmapHelper.<init>', 'AttachmentsHelper.<init>', 'AnimationsHelper.<init>', 'AlphaManager.<init>', 'BuildConfig.<init>'], 'Constructor of a class with only static members: never called')
_dead(['SketchView.getStrokeSize', 'SketchView.getUndonePaths', 'SketchView.setPaths', 'SketchView.setUndonePaths', 'SquareImageView.getAsyncTask', 'SquareImageView.setAsyncTask', 'ExpandableHeightGridView.getItemHeight',
       'NavigationItem.setArrayIndex', 'NavigationItem.setIcon', 'NavigationItem.setIconSelected', 'NavigationItem.setText', 'Fab.lambda$setOverlay$2', 'Fab.lambda$setOverlay$3', 'Fab.setOverlay(int)', 'Fab.setOverlay(View)',
       'UndoBarController.isVisible', 'UndoBarController.onRestoreInstanceState', 'UndoBarController.onSaveInstanceState', 'Stats.getUsageTime', 'Stats.setUsageTime', 'NoteAdapter.colorNote(Note,View)', 'NoteAdapter.getNotes',
       'MainActivity.getSearchMenuItem', 'MainActivity.initNotesList', 'MainActivity.lambda$initNotesList$1', 'ListFragment.getSearchMenuItem', 'BaseActivity.getStringResourceByName', 'RecyclerViewItemClickSupport.detach',
       'RecyclerViewItemClickSupport.removeFrom', 'AbsListViewScrollDetector.setListView', 'AbsListViewScrollDetector.setScrollThreshold', 'AttachmentAdapter.getAttachmentsList',
       'AttachmentTask.<init>(Fragment,Uri,OnAttachingFileListener)', 'Note.<init>(Long,Long,String,String,Integer,Integer,String,String,Integer,String,String,Category,Integer,Integer)', 'Tag.<init>()',
       'DetailFragment$OnGeoUtilResultListenerImpl.onCoordinatesResolved', 'SettingsActivity.replaceFragment'], 'No caller in the app sources, layouts or reflection (SettingsActivity.replaceFragment runs only when its back stack list is non-empty and nothing ever fills it)')
_dead(['ShortcutHelper.addShortcut', 'ShortcutHelper.<init>', 'DetailFragment.addShortcut'], 'The "Add shortcut" menu item is never made visible: the line that showed it is commented out (DetailFragment.java:1032, res/menu/menu_detail.xml:73-78)')
_dead([m for m in _by('IntroActivity') if m != 'IntroActivity.mustRun'] + _by('IntroFragment', 'IntroFragment_ViewBinding') + _by('IntroSlide1', 'IntroSlide2', 'IntroSlide3', 'IntroSlide4', 'IntroSlide5', 'IntroSlide6'),
      'The intro tour never starts in this build: IntroActivity.mustRun() is false when BuildConfig.BUILD_TYPE is "debug" (OmniNotes.isDebugBuild)')
_fw(['MainActivity_ViewBinding.<init>(MainActivity)', 'SettingsActivity_ViewBinding.<init>(SettingsActivity)', 'NoteInfosActivity_ViewBinding.<init>(NoteInfosActivity)', 'GalleryActivity_ViewBinding.<init>(GalleryActivity)',
     'CategoryActivity_ViewBinding.<init>(CategoryActivity)'], 'ButterKnife calls the (target, source View) constructor; the one-argument activity constructor is never used')
_fw([m for m in METHODS if m.endswith('_ViewBinding.unbind')], 'ButterKnife Unbinder.unbind(): the app never stores or calls the Unbinder')
_fw(['SettingsActivity.onPointerCaptureChanged', 'CategoryActivity.onPointerCaptureChanged'], 'Activity pointer-capture callback (API 26+): the app never requests pointer capture')
_fw(['SketchFragment.onOptionsItemSelected', 'SettingsFragment.onOptionsItemSelected'], 'The toolbar navigation listener consumes the Up click (SettingsFragment sets no options menu), so the options-menu home item is not dispatched')
_fw(['DetailFragment.onConfigurationChanged'], 'MainActivity declares no configChanges, so fragments do not receive configuration callbacks')
_fw(['DetailFragment$4.onAnimationRepeat', 'AnimationsHelper$1.onAnimationRepeat', 'Fab$3.onAnimationCancel', 'RecyclerViewItemClickSupport$3.onChildViewDetachedFromWindow'], 'Animation / attach callback that nothing triggers in this app (no repeat count, no cancel, rows are not detached while the dialog shows)')
_fw(['Note$1.newArray', 'Category$1.newArray', 'Attachment$1.newArray', 'Tag$1.newArray', 'Tag$1.createFromParcel', 'Tag.<init>(Parcel)', 'Tag.describeContents', 'Tag.writeToParcel', 'Tag.toString', 'CategoryRecyclerViewAdapter.getItemId',
     'Category.toString'], 'Parcelable / adapter boilerplate that is never exercised: no array of these is read from a Parcel, Tag objects are never parceled, rows have no stable ids, toString is only an implicit call')
e('NotificationChannels.<clinit>', 'NotificationChannels$NotificationChannelNames.<clinit>', 'CALL', 'class initialisation on first use (the channel map refers to the enum)', evidence='SRC utils/notifications/NotificationChannels.java (static channel map); INFERRED the class has a static initialiser that the JVM runs on first use of the class (Java language rule, not read from a source)')

_fw(['ExpandableHeightGridView.<init>(Context)', 'ExpandableHeightGridView.<init>(Context,AttributeSet,int)', 'InterceptorFrameLayout.<init>(Context)', 'InterceptorLinearLayout.<init>(Context)',
     'NonScrollableListView.<init>(Context)', 'NonScrollableListView.<init>(Context,AttributeSet,int)', 'SquareImageView.<init>(Context)', 'SquareImageView.<init>(Context,AttributeSet,int)'],
    'Custom-view constructor that layout inflation never uses: inflation calls the (Context, AttributeSet) form, and no code calls the other forms')
e('CategoryRecyclerViewAdapter.onCreateViewHolder', 'CategoryViewHolder_ViewBinding.<init>', 'FRAMEWORK', 'new CategoryViewHolder(view) binds with ButterKnife', needs_state=NEED_CATEGORY, evidence=FW_BIND + '; SRC models/adapters/category/CategoryViewHolder.java')
# methods only reachable from dead code are dead too
SUPPRESS |= set(DEAD)
SUPPRESS |= set(FRAMEWORK_ONLY)

e('DetailFragment.onActivityResult@CANCEL', 'DetailFragment.onActivityResult', 'CALL', 'onActivityResult(requestCode, resultCode, intent)', evidence='SRC DetailFragment.java:1408-1451')
for k in ('PHOTO', 'VIDEO', 'FILES', 'PASSWORD', 'CATEGORY'):
    e('DetailFragment.onActivityResult@' + k, 'DetailFragment.onActivityResult', 'CALL', 'onActivityResult(requestCode, resultCode, intent)', evidence='SRC DetailFragment.java:1408-1451')


# ================================================================== F. corrections found by reading paths
# ---- undo bar: one page per pending change, each with its own commit
sup('ListFragment.commitPending')
for k, call in (('TRASH', 'ListFragment.trashNote'), ('ARCHIVE', 'ListFragment.archiveNote'), ('CATEGORIZE', 'ListFragment.categorizeNote')):
    pg = 'S_LIST_UNDO@' + k
    gui(pg, 'UndoBarController$1.onClick', 'Tap UNDO', evidence='SRC models/UndoBarController.java:70-76')
    gui(pg, 'InterceptorLinearLayout.onInterceptTouchEvent@' + k, 'Touch the list or anywhere else (the change is committed)', evidence='SRC models/views/InterceptorLinearLayout.java; ListFragment.java:529,572-575')
    e('InterceptorLinearLayout.onInterceptTouchEvent@' + k, 'ListFragment.onViewTouchOccurred@' + k, 'CALL', 'OnViewTouchedListener.onViewTouchOccurred', evidence='SRC models/views/InterceptorLinearLayout.java')
    e('ListFragment.onViewTouchOccurred@' + k, 'ListFragment.commitPending@' + k, 'CALL', 'commitPending()', evidence='SRC ListFragment.java:572-575')
    e('ListFragment.onViewTouchOccurred@' + k, 'LogDelegate.v', 'CALL', 'log', evidence='SRC ListFragment.java:573')
    clone_auto('ListFragment.commitPending', 'ListFragment.commitPending@' + k, only=(call, 'Fab.showFab', 'UndoBarController.hideUndoBar', 'LogDelegate.d', 'MainActivity.updateWidgets'))
    e('ListFragment.commitPending@' + k, 'S_LIST@NOTES', 'ENTERS', 'the change is committed and the list is shown without the undo bar', evidence='SRC ListFragment.java:1688-1718')
sup('InterceptorLinearLayout.onInterceptTouchEvent', 'ListFragment.onViewTouchOccurred')
e('InterceptorLinearLayout.onInterceptTouchEvent', 'ListFragment.onViewTouchOccurred', 'CALL', 'OnViewTouchedListener.onViewTouchOccurred', evidence='SRC models/views/InterceptorLinearLayout.java')
e('ListFragment.onViewTouchOccurred', 'ListFragment.commitPending', 'CALL', 'commitPending()', evidence='SRC ListFragment.java:572-575')
e('ListFragment.onViewTouchOccurred', 'LogDelegate.v', 'CALL', 'log', evidence='SRC ListFragment.java:573')
e('S_LIST@NOTES', 'InterceptorLinearLayout.onInterceptTouchEvent', 'GUI', 'Touch the notes list', gui=['Touch the notes list'], evidence='SRC models/views/InterceptorLinearLayout.java')
e('ListFragment.commitPending', 'MainActivity.updateWidgets', 'CALL', 'the widgets are refreshed', evidence='SRC ListFragment.java:1717')
for call, need in (('ListFragment.trashNote', 'A trash is pending (the undo bar shows)'), ('ListFragment.archiveNote', 'An archive is pending (the undo bar shows)'), ('ListFragment.categorizeNote', 'A "remove category" is pending (the undo bar shows)')):
    e('ListFragment.commitPending', call, 'CALL', 'the pending change is applied', needs_state=need, evidence='SRC ListFragment.java:1688-1715')
for dst in ('Fab.showFab', 'UndoBarController.hideUndoBar', 'LogDelegate.d'):
    e('ListFragment.commitPending', dst, 'CALL', 'the undo bar closes', needs_state='A trash, archive or remove-category is pending (the undo bar shows)', evidence='SRC ListFragment.java:1688-1715')
# ---- ListFragment.onActivityResult: one variant per result
sup('ListFragment.onActivityResult')
AR = {'SAVED': ['CategoriesUpdatedEvent.<init>', 'MainActivity.showMessage(int,Style)'], 'DELETED': ['MainActivity.showMessage(int,Style)'], 'ADD_CATEGORY': [], 'REMINDERS': ['ListFragment.finishActionMode'], 'CANCEL': []}
for k, dsts in AR.items():
    v = 'ListFragment.onActivityResult@' + k
    e(v, 'ListFragment.onActivityResult', 'CALL', 'onActivityResult(requestCode, resultCode, intent)', evidence='SRC ListFragment.java:955-993')
    for d in dsts:
        e(v, d, 'CALL', 'call in onActivityResult', evidence='SRC ListFragment.java:955-993')
for h in ('NavigationDrawerFragment.onEvent(CategoriesUpdatedEvent)', 'ListFragment.onEvent(CategoriesUpdatedEvent)'):
    e('ListFragment.onActivityResult@SAVED', h, 'FRAMEWORK', 'CategoriesUpdatedEvent after a category was saved', evidence=FW_EB + '; SRC ListFragment.java:962-965')
e('ListFragment.onActivityResult@ADD_CATEGORY', 'ListFragment.categorizeNotesExecute@CAT', 'CALL', 'categorizeNotesExecute(tag) after "Add category" from the CAB', evidence='SRC ListFragment.java:975-981')
e('ListFragment.onActivityResult@ADD_CATEGORY', 'Category$1.createFromParcel', 'FRAMEWORK', 'intent.getParcelableExtra(INTENT_CATEGORY)', evidence=FWP + '; SRC ListFragment.java:977')
# ---- sketch: an existing sketch is loaded as the canvas background only when it is edited
sup(('SketchFragment.onActivityCreated', 'SketchView.setBackgroundBitmap'))
e('SketchFragment.onActivityCreated', 'SketchView.setBackgroundBitmap', 'CALL', 'the existing sketch becomes the canvas background', guard='baseUri != null', needs_state=NEED_SKETCH + ' (opened with Edit)', evidence='SRC SketchFragment.java:111-120')
# ---- catch blocks and error branches
ENV_EXC2 = 'an exception is thrown (I/O error, missing algorithm, database failure)'
# createExternalStoragePrivateFile falls back to FileHelper.getPath only when the stream of the URI cannot be opened (StorageHelper.java:118-124).
# Only AttachmentTask hands it a content URI picked in another app; a merged note holds file:// URIs of its own copies, which never lead to a media document.
sup(('StorageHelper.createExternalStoragePrivateFile', 'FileHelper.getPath'), ('AttachmentTask.doInBackground', 'StorageHelper.createAttachmentFromUri(Context,Uri)'))
_CAF = 'StorageHelper.createAttachmentFromUri(Context,Uri)'
e('AttachmentTask.doInBackground', _CAF + '@PICK', 'CALL', 'createAttachmentFromUri(context, uri) with the URI chosen in the picker', evidence='SRC AttachmentTask.java:55 (bytecode)')
e(_CAF + '@PICK', 'StorageHelper.createAttachmentFromUri(Context,Uri,boolean)@PICK', 'CALL', 'Direct call', evidence='SRC StorageHelper.java:457 (bytecode)')
e('StorageHelper.createAttachmentFromUri(Context,Uri,boolean)@PICK', 'StorageHelper.createExternalStoragePrivateFile@PICK', 'CALL', 'the file is copied from the picked URI (moveSource is false)', guard='moveSource is false (StorageHelper.java:469-477)', evidence='SRC StorageHelper.java:477 (bytecode)')
e('StorageHelper.createExternalStoragePrivateFile@PICK', 'FileHelper.getPath', 'CALL', 'the stream of the picked URI cannot be opened: the path is looked up instead', guard='the call is inside a catch block: openInputStream or the copy throws an IOException (StorageHelper.java:118-124)', env=ENV_EXC2, evidence='SRC StorageHelper.java:124 (bytecode)')
for c in AUTO['calls']:
    if c['dst'] == 'LogDelegate.w(String,Throwable)':
        sup((c['src'], c['dst']))
        e(c['src'], c['dst'], 'CALL', 'warning logged in a catch block', env=ENV_EXC2, evidence='SRC %s:%d (bytecode)' % (c['file'], c['line']))
sup(('DbHelper.onCreate', 'DatabaseException.<init>'))
e('DbHelper.onCreate', 'DatabaseException.<init>', 'CALL', 'creating the database failed', env=ENV_EXC2, evidence='SRC db/DbHelper.java:180-188')
sup(('NoteLoaderTask.doInBackground', 'NotesLoadingException.<init>'))
for q in LOADERS:
    e('NoteLoaderTask.doInBackground@' + q, 'NotesLoadingException.<init>', 'CALL', 'the reflective query failed', env=ENV_EXC2, evidence='SRC async/notes/NoteLoaderTask.java:66-77')
# ---- data-dependent calls
sup(('Note.getCategory', 'Category.<init>(BaseCategory)'), ('Note.setCategory', 'Category.<init>(BaseCategory)'))
for src in ('Note.getCategory', 'Note.setCategory'):
    e(src, 'Category.<init>(BaseCategory)', 'CALL', 'a copy of the category is made', guard='category != null', needs_state=NEED_CATEGORY, evidence='SRC models/Note.java')
sup(('NotesHelper.getNoteInfos', 'StatsSingleNote.setCategoryName'))
e('NotesHelper.getNoteInfos', 'StatsSingleNote.setCategoryName', 'CALL', 'the category name is shown', guard='note.getCategory() != null', needs_state='The note has a category', evidence='SRC helpers/NotesHelper.java')
sup(('DbHelper.getNotes', 'Security.decrypt'), ('DbHelper.updateNote', 'Security.encrypt'))
e('DbHelper.getNotes', 'Security.decrypt', 'CALL', 'locked notes are decrypted when read', guard='note.isLocked()', needs_state=NEED_LOCKED, evidence='SRC db/DbHelper.java:220-222')
e('DbHelper.updateNote', 'Security.encrypt', 'CALL', 'locked notes are encrypted when written', guard='note.isLocked()', needs_state=NEED_LOCKED, evidence='SRC db/DbHelper.java:220-222')
sup(('ListFragment.initNotesList', 'TextHelper.checkIntentCategory'))
e('ListFragment.initNotesList', 'TextHelper.checkIntentCategory', 'CALL', 'the category of a widget condition', needs_state='The list was opened from a widget', env=ENV_LAUNCHER, evidence='SRC ListFragment.java:1099-1108')
for dst, need in (('DbHelper.getNotesArchived', NEED_ARCH_NAV), ('DbHelper.getNotesWithReminder', NEED_REM_NAV), ('DbHelper.getNotesTrashed', NEED_TRASH_NAV), ('DbHelper.getNotesUncategorized', NEED_UNCAT_NAV),
                  ('DbHelper.getNotesByCategory', NEED_CATEGORY), ('Navigation.getCategory', NEED_CATEGORY)):
    sup(('DbHelper.getAllNotes', dst))
    e('DbHelper.getAllNotes@NAV', dst, 'CALL', 'the query for the selected navigation', needs_state=need + ' and that navigation is selected', evidence='SRC db/DbHelper.java:329-346')
# getAllNotes(checkNavigation): true asks for the selected navigation (@NAV), anything else for all notes (@ALL); the hand edges below cover each pair, so the automatic ones are skipped
e('DbHelper.getAllNotes@NAV', 'Navigation.getNavigation', 'CALL', 'the selected navigation', guard='checkNavigation is TRUE', evidence='SRC db/DbHelper.java:331-332')
e('DbHelper.getAllNotes@NAV', 'DbHelper.getNotesActive', 'CALL', 'the Notes navigation (the default)', guard='checkNavigation is TRUE and the navigation is Notes', evidence='SRC db/DbHelper.java:333-335')
e('DbHelper.getAllNotes@ALL', 'DbHelper.getNotes', 'CALL', 'all notes, the navigation is ignored', guard='checkNavigation is not TRUE', evidence='SRC db/DbHelper.java:349-351')
for _caller, _line in (('UpgradeProcessor.onUpgradeTo501', 'async/upgrade/UpgradeProcessor.java:171'), ('DynamicNavigationLookupTable.lambda$update$0', 'models/misc/DynamicNavigationLookupTable.java:56'),
                       ('DbHelper.getStats', 'db/DbHelper.java:977'), ('BackupHelper.exportNotes', 'helpers/BackupHelper.java:60')):
    sup((_caller, 'DbHelper.getAllNotes'))
    e(_caller, 'DbHelper.getAllNotes@ALL', 'CALL', 'getAllNotes(false)', evidence='SRC ' + _line + ' (bytecode)')
sup(('DbHelper.getNotesByCategory', 'DbHelper.getAllNotes'))
e('DbHelper.getNotesByCategory', 'DbHelper.getAllNotes@NAV', 'CALL', 'getAllNotes(true) when the category id cannot be parsed', env=ENV_EXC2, guard='NumberFormatException', evidence='SRC db/DbHelper.java:668 (bytecode)')
# ---- editor: archive / trash / untrash save the note and leave
clone_auto('DetailFragment.archiveNote', 'DetailFragment.archiveNote@ARCHIVE')
clone_auto('DetailFragment.archiveNote', 'DetailFragment.archiveNote@UNARCHIVE')
clone_auto('DetailFragment.trashNote', 'DetailFragment.trashNote@TRASH', exclude=('ReminderHelper.addReminder(Context,Note)',))
clone_auto('DetailFragment.trashNote', 'DetailFragment.trashNote@UNTRASH', exclude=('ShortcutHelper.removeshortCut', 'ReminderHelper.removeReminder'))
for n in ('DetailFragment.archiveNote@ARCHIVE', 'DetailFragment.archiveNote@UNARCHIVE', 'DetailFragment.trashNote@TRASH', 'DetailFragment.trashNote@UNTRASH'):
    e(n, 'DetailFragment.saveNote@SAVE', 'CALL', 'the changed note is saved and the editor closes', evidence='SRC DetailFragment.java:1499-1533')
sup(('DetailFragment.archiveNote', 'DetailFragment.saveNote'), ('DetailFragment.trashNote', 'DetailFragment.saveNote'))
e('OmniNotes.attachBaseContext', 'BuildConfig.<clinit>', 'FRAMEWORK', 'a crash report is built: the ACRA collector reads the BuildConfig fields (buildConfigClass) by reflection, which initialises the class',
  env=ENV_EXC, evidence='SRC OmniNotes.java:45,75 (@AcraCore(buildConfigClass = BuildConfig.class), ACRA.init); INFERRED ACRA reads the BuildConfig fields by reflection when it builds a report (ACRA source not read); '
                       'no app code reads BuildConfig.DEBUG, the only non-constant field, and every other read is a compile-time constant that javac inlines')
SUPPRESS |= set(DEAD)
SUPPRESS |= set(FRAMEWORK_ONLY)

# the Tag objects are built per #tag found in a note
for c in AUTO['calls']:
    if c['dst'] == 'Tag.<init>(String,Integer)':
        sup((c['src'], c['dst']))
        e(c['src'], c['dst'], 'CALL', 'one Tag per #tag found in a note', needs_state=NEED_TAGS, evidence='SRC %s:%d (bytecode)' % (c['file'], c['line']))
SUPPRESS |= set(DEAD)

sup(('ListFragment.initTitle', 'DbHelper.getCategory'))
e('ListFragment.initTitle', 'DbHelper.getCategory', 'CALL', 'the title of a category navigation', guard='navigation is a category id', needs_state=NEED_CATEGORY + ' and it is selected in the drawer', evidence='SRC ListFragment.java:311-317')
sup(('DbHelper.updateNote', 'DbHelper.updateAttachment(long,Attachment,SQLiteDatabase)'), ('DbHelper.updateNote', 'Note.getAttachmentsListOld'))
e('DbHelper.updateNote', 'DbHelper.updateAttachment(long,Attachment,SQLiteDatabase)', 'CALL', 'each attachment of the note is written', needs_state=NEED_ATTACH, evidence='SRC db/DbHelper.java (updateNote)')
e('DbHelper.updateNote', 'Note.getAttachmentsListOld', 'CALL', 'removed attachments are compared', needs_state=NEED_ATTACH, evidence='SRC db/DbHelper.java (updateNote)')
SUPPRESS |= set(DEAD)

# declaration line of every UNREACHABLE method (tools/scan_unreachable.py --refs)
REFS = {
    'AbsListViewScrollDetector.setListView': 'AbsListViewScrollDetector.java:74',
    'AbsListViewScrollDetector.setScrollThreshold': 'AbsListViewScrollDetector.java:69',
    'AlphaManager.<init>': 'AlphaManager.java:26',
    'AnimationsHelper$1.onAnimationRepeat': 'AnimationsHelper.java:115',
    'AnimationsHelper.<init>': 'AnimationsHelper.java:37',
    'AppVersionHelper.<init>': 'AppVersionHelper.java:33',
    'AppVersionHelper.getAppVersionFromPreferences': 'AppVersionHelper.java:43',
    'AppVersionHelper.getCurrentAppVersion': 'AppVersionHelper.java:57',
    'AppVersionHelper.isAppUpdated': 'AppVersionHelper.java:37',
    'AppVersionHelper.updateAppVersionInPreferences': 'AppVersionHelper.java:52',
    'AssetUtils.<init>': 'AssetUtils.java:26',
    'AssetUtils.exists': 'AssetUtils.java:30',
    'Attachment$1.newArray': 'Attachment.java:92',
    'AttachmentAdapter.getAttachmentsList': 'AttachmentAdapter.java:132',
    'AttachmentTask.<init>(Fragment,Uri,OnAttachingFileListener)': 'AttachmentTask.java:39',
    'AttachmentsHelper.<init>': 'AttachmentsHelper.java:28',
    'BackupHelper.<init>': 'BackupHelper.java:55',
    'BackupHelper.addIntegrityCheckError': 'BackupHelper.java:345',
    'BackupHelper.deleteNote': 'BackupHelper.java:292',
    'BackupHelper.deleteNoteBackup': 'BackupHelper.java:280',
    'BackupHelper.exportAttachments(File)': 'BackupHelper.java:86',
    'BackupHelper.importAttachments(File)': 'BackupHelper.java:190',
    'BackupHelper.importAttachments(Note,File)': 'BackupHelper.java:190',
    'BackupHelper.integrityCheck': 'BackupHelper.java:318',
    'BaseActivity.getStringResourceByName': 'BaseActivity.java:153',
    'BitmapHelper.<init>': 'BitmapHelper.java:47',
    'BuildConfig.<init>': 'OmniNotes.java:56',
    'Category$1.newArray': 'Category.java:86',
    'Category.toString': 'Category.java:70',
    'CategoryActivity.onPointerCaptureChanged': 'CategoryActivity.java:115',
    'CategoryActivity_ViewBinding.<init>(CategoryActivity)': 'CategoryActivity.java:71',
    'CategoryActivity_ViewBinding.unbind': 'CategoryActivity.java:71',
    'CategoryRecyclerViewAdapter.getItemId': 'CategoryRecyclerViewAdapter.java:105',
    'CategoryViewHolder_ViewBinding.unbind': 'CategoryViewHolder.java:32',
    'ColorsUtil.<init>': 'ColorsUtil.java:25',
    'ColorsUtil.calculateColorLuminance': 'ColorsUtil.java:34',
    'ColorsUtil.getContrastedColor': 'ColorsUtil.java:39',
    'ConnectionManager.<init>': 'ConnectionManager.java:25',
    'CountFactory.<init>': 'CountFactory.java:25',
    'DateHelper.<init>': 'DateHelper.java:33',
    'DateHelper.getSortableDate': 'DateHelper.java:37',
    'DateHelper.getTimeShort(Context,Long)': 'DateHelper.java:81',
    'DateHelper.getTimeShort(Context,int,int)': 'DateHelper.java:81',
    'DateHelper.onDateSet': 'DateHelper.java:46',
    'DateHelper.onTimeSet': 'DateHelper.java:59',
    'DateUtils.<init>': 'DateUtils.java:38',
    'DateUtils.getDateFromString': 'DateUtils.java:54',
    'DateUtils.getLongFromDateTime': 'DateUtils.java:69',
    'DateUtils.getString(Date,String)': 'DateUtils.java:42',
    'DateUtils.getString(long,String)': 'DateUtils.java:42',
    'DateUtils.prettyTime(String)': 'DateUtils.java:177',
    'DbHelper.emptyTrash': 'DbHelper.java:542',
    'DbHelper.getCategorizedCount': 'DbHelper.java:935',
    'DbHelper.getChecklists': 'DbHelper.java:640',
    'DbHelper.getDatabaseName': 'DbHelper.java:158',
    'DbHelper.getMasked': 'DbHelper.java:646',
    'DbHelper.getNotesWithLocation': 'DbHelper.java:382',
    'DbHelper.getTodayReminders': 'DbHelper.java:624',
    'DetailFragment$4.onAnimationRepeat': 'DetailFragment.java:1880',
    'DetailFragment$OnGeoUtilResultListenerImpl.onCoordinatesResolved': 'DetailFragment.java:991',
    'DetailFragment.addShortcut': 'DetailFragment.java:1896',
    'DetailFragment.onConfigurationChanged': 'DetailFragment.java:437',
    'DetailFragment_ViewBinding.unbind': 'DetailFragment.java:353',
    'Display.<init>': 'Display.java:37',
    'Display.getActionbarHeight': 'Display.java:109',
    'Display.getFullSize': 'Display.java:76',
    'Display.getNavigationBarHeight': 'Display.java:103',
    'Display.getNavigationBarHeightStandard': 'Display.java:94',
    'Display.getRootView': 'Display.java:42',
    'Display.getSoftButtonsBarHeight': 'Display.java:143',
    'Display.getStatusBarHeight': 'Display.java:84',
    'Display.getVisibleSize': 'Display.java:66',
    'Display.orientationLandscape': 'Display.java:139',
    'ExpandableHeightGridView.<init>(Context)': 'ExpandableHeightGridView.java:31',
    'ExpandableHeightGridView.<init>(Context,AttributeSet,int)': 'ExpandableHeightGridView.java:31',
    'ExpandableHeightGridView.getItemHeight': 'ExpandableHeightGridView.java:86',
    'Fab$3.onAnimationCancel': 'Fab.java:162',
    'Fab.lambda$setOverlay$2': 'Fab.java:188',
    'Fab.lambda$setOverlay$3': 'Fab.java:188',
    'Fab.setOverlay(View)': 'Fab.java:188',
    'Fab.setOverlay(int)': 'Fab.java:188',
    'FileHelper.<init>': 'FileHelper.java:37',
    'FileHelper.getFileExtension(File)': 'FileHelper.java:200',
    'FileHelper.getFilePrefix(File)': 'FileHelper.java:185',
    'FileHelper.getFilePrefix(String)': 'FileHelper.java:185',
    'FileProviderHelper.<init>': 'FileProviderHelper.java:28',
    'GalleryActivity_ViewBinding.<init>(GalleryActivity)': 'GalleryActivity.java:121',
    'GalleryActivity_ViewBinding.unbind': 'GalleryActivity.java:121',
    'GeocodeHelper.<init>': 'GeocodeHelper.java:56',
    'GeocodeHelper.getAddressFromCoordinates(Context,double,double)': 'GeocodeHelper.java:121',
    'GeocodeHelper.onLocationChanged': 'GeocodeHelper.java:63',
    'GeocodeHelper.onProviderDisabled': 'GeocodeHelper.java:81',
    'GeocodeHelper.onProviderEnabled': 'GeocodeHelper.java:75',
    'GeocodeHelper.onStatusChanged': 'GeocodeHelper.java:69',
    'GeocodeProviderBaseFactory.<init>': 'GeocodeProviderBaseFactory.java:26',
    'GeocodeProviderFactory.<init>': 'GeocodeProviderFactory.java:26',
    'GeocodeProviderFactory.getProvider': 'GeocodeProviderFactory.java:30',
    'ImageAndTextItem.<init>': 'ImageAndTextItem.java:22',
    'ImageAndTextItem.getImage': 'ImageAndTextItem.java:33',
    'ImageAndTextItem.getText': 'ImageAndTextItem.java:43',
    'ImageAndTextItem.setImage': 'ImageAndTextItem.java:38',
    'ImageAndTextItem.setText': 'ImageAndTextItem.java:48',
    'IntentChecker.<init>': 'IntentChecker.java:30',
    'IntentChecker.resolveActivityPackage': 'IntentChecker.java:37',
    'InterceptorFrameLayout.<init>(Context)': 'InterceptorFrameLayout.java:32',
    'InterceptorLinearLayout.<init>(Context)': 'InterceptorLinearLayout.java:32',
    'IntroActivity.<init>': 'IntroActivity.java:29',
    'IntroActivity.init': 'IntroActivity.java:32',
    'IntroActivity.onBackPressed': 'IntroActivity.java:54',
    'IntroActivity.onDonePressed': 'IntroActivity.java:42',
    'IntroFragment.<init>': 'IntroFragment.java:32',
    'IntroFragment.onCreateView': 'IntroFragment.java:51',
    'IntroFragment_ViewBinding.<init>': 'IntroFragment.java:53',
    'IntroFragment_ViewBinding.unbind': 'IntroFragment.java:53',
    'IntroSlide1.<init>': 'IntroSlide1.java:26',
    'IntroSlide1.onActivityCreated': 'IntroSlide1.java:29',
    'IntroSlide2.<init>': 'IntroSlide2.java:25',
    'IntroSlide2.onActivityCreated': 'IntroSlide2.java:28',
    'IntroSlide3.<init>': 'IntroSlide3.java:25',
    'IntroSlide3.onActivityCreated': 'IntroSlide3.java:28',
    'IntroSlide4.<init>': 'IntroSlide4.java:25',
    'IntroSlide4.onActivityCreated': 'IntroSlide4.java:28',
    'IntroSlide5.<init>': 'IntroSlide5.java:25',
    'IntroSlide5.onActivityCreated': 'IntroSlide5.java:28',
    'IntroSlide6.<init>': 'IntroSlide6.java:30',
    'IntroSlide6.lambda$onActivityCreated$0': 'IntroSlide6.java:33',
    'IntroSlide6.onActivityCreated': 'IntroSlide6.java:33',
    'KeyboardUtils.<init>': 'KeyboardUtils.java:29',
    'KeyboardUtils.hideKeyboard(MainActivity)': 'KeyboardUtils.java:62',
    'LanguageHelper.<init>': 'LanguageHelper.java:37',
    'LanguageHelper.getLocalizedString': 'LanguageHelper.java:83',
    'ListFragment.getSearchMenuItem': 'ListFragment.java:1838',
    'ListFragment_ViewBinding.unbind': 'ListFragment.java:233',
    'LoadingDialog.<init>': 'LoadingDialog.java:28',
    'LoadingDialog.onBackPressed': 'LoadingDialog.java:35',
    'LogDelegate.<init>': 'LogDelegate.java:36',
    'MainActivity.getSearchMenuItem': 'MainActivity.java:205',
    'MainActivity.initNotesList': 'MainActivity.java:223',
    'MainActivity.lambda$initNotesList$1': 'MainActivity.java:223',
    'MainActivity_ViewBinding.<init>(MainActivity)': 'MainActivity.java:97',
    'MainActivity_ViewBinding.unbind': 'MainActivity.java:97',
    'MainMenuTask_ViewBinding.unbind': 'MainMenuTask.java:59',
    'MiscUtils.<init>': 'MiscUtils.java:26',
    'MiscUtils.isGooglePlayAvailable': 'MiscUtils.java:37',
    'Navigation.<init>': 'Navigation.java:34',
    'NavigationItem.setArrayIndex': 'NavigationItem.java:42',
    'NavigationItem.setIcon': 'NavigationItem.java:62',
    'NavigationItem.setIconSelected': 'NavigationItem.java:72',
    'NavigationItem.setText': 'NavigationItem.java:52',
    'NonScrollableListView.<init>(Context)': 'NonScrollableListView.java:30',
    'NonScrollableListView.<init>(Context,AttributeSet,int)': 'NonScrollableListView.java:30',
    'Note$1.newArray': 'Note.java:41',
    'Note.<init>(Long,Long,String,String,Integer,Integer,String,String,Integer,String,String,Category,Integer,Integer)': 'Note.java:49',
    'NoteAdapter.colorNote(Note,View)': 'NoteAdapter.java:249',
    'NoteAdapter.getNotes': 'NoteAdapter.java:135',
    'NoteInfosActivity_ViewBinding.<init>(NoteInfosActivity)': 'NoteInfosActivity.java:64',
    'NoteInfosActivity_ViewBinding.unbind': 'NoteInfosActivity.java:64',
    'NoteViewHolder_ViewBinding.unbind': 'NoteViewHolder.java:33',
    'NotesHelper.<init>': 'NotesHelper.java:42',
    'NotificationChannels.<init>': 'NotificationChannels.java:32',
    'NotificationsHelper.cancel(int)': 'NotificationsHelper.java:183',
    'NotificationsHelper.setIcon': 'NotificationsHelper.java:122',
    'ONStyle.<init>': 'ONStyle.java:29',
    'ParcelableUtil.<init>': 'ParcelableUtil.java:26',
    'PasswordHelper.<init>': 'PasswordHelper.java:46',
    'PermissionsHelper.<init>': 'PermissionsHelper.java:33',
    'PlayStoreMetadataFetcherResult.<init>': 'PlayStoreMetadataFetcherResult.java:20',
    'PlayStoreMetadataFetcherResult.getContentRating': 'PlayStoreMetadataFetcherResult.java:69',
    'PlayStoreMetadataFetcherResult.getDatePublished': 'PlayStoreMetadataFetcherResult.java:29',
    'PlayStoreMetadataFetcherResult.getFileSize': 'PlayStoreMetadataFetcherResult.java:37',
    'PlayStoreMetadataFetcherResult.getNumDownloads': 'PlayStoreMetadataFetcherResult.java:45',
    'PlayStoreMetadataFetcherResult.getOperatingSystems': 'PlayStoreMetadataFetcherResult.java:61',
    'PlayStoreMetadataFetcherResult.getSoftwareVersion': 'PlayStoreMetadataFetcherResult.java:53',
    'PlayStoreMetadataFetcherResult.setContentRating': 'PlayStoreMetadataFetcherResult.java:73',
    'PlayStoreMetadataFetcherResult.setDatePublished': 'PlayStoreMetadataFetcherResult.java:33',
    'PlayStoreMetadataFetcherResult.setFileSize': 'PlayStoreMetadataFetcherResult.java:41',
    'PlayStoreMetadataFetcherResult.setNumDownloads': 'PlayStoreMetadataFetcherResult.java:49',
    'PlayStoreMetadataFetcherResult.setOperatingSystems': 'PlayStoreMetadataFetcherResult.java:65',
    'PlayStoreMetadataFetcherResult.setSoftwareVersion': 'PlayStoreMetadataFetcherResult.java:57',
    'PushBulletMessage.<init>': 'PushBulletMessage.java:25',
    'RecurrenceHelper.<init>': 'RecurrenceHelper.java:41',
    'RecyclerViewItemClickSupport$3.onChildViewDetachedFromWindow': 'RecyclerViewItemClickSupport.java:61',
    'RecyclerViewItemClickSupport.detach': 'RecyclerViewItemClickSupport.java:99',
    'RecyclerViewItemClickSupport.removeFrom': 'RecyclerViewItemClickSupport.java:81',
    'ReminderHelper.<init>': 'ReminderHelper.java:40',
    'ReminderHelper.checkReminder': 'ReminderHelper.java:64',
    'ResourcesUtils.<init>': 'ResourcesUtils.java:23',
    'Security.<init>': 'Security.java:38',
    'SettingsActivity.onPointerCaptureChanged': 'SettingsActivity.java:120',
    'SettingsActivity.replaceFragment': 'SettingsActivity.java:71',
    'SettingsActivity_ViewBinding.<init>(SettingsActivity)': 'SettingsActivity.java:57',
    'SettingsActivity_ViewBinding.unbind': 'SettingsActivity.java:57',
    'SettingsFragment.onOptionsItemSelected': 'SettingsFragment.java:127',
    'ShortcutHelper.<init>': 'ShortcutHelper.java:40',
    'ShortcutHelper.addShortcut': 'ShortcutHelper.java:47',
    'SketchFragment.onOptionsItemSelected': 'SketchFragment.java:198',
    'SketchFragment_ViewBinding.unbind': 'SketchFragment.java:99',
    'SketchView.getStrokeSize': 'SketchView.java:262',
    'SketchView.getUndonePaths': 'SketchView.java:252',
    'SketchView.setPaths': 'SketchView.java:247',
    'SketchView.setUndonePaths': 'SketchView.java:257',
    'SqlParser.<init>': 'SqlParser.java:28',
    'SquareImageView.<init>(Context)': 'SquareImageView.java:32',
    'SquareImageView.<init>(Context,AttributeSet,int)': 'SquareImageView.java:32',
    'SquareImageView.getAsyncTask': 'SquareImageView.java:60',
    'SquareImageView.setAsyncTask': 'SquareImageView.java:55',
    'Stats.getUsageTime': 'Stats.java:205',
    'Stats.setUsageTime': 'Stats.java:210',
    'StorageHelper.<init>': 'StorageHelper.java:50',
    'StorageHelper.copyDirectory': 'StorageHelper.java:377',
    'StorageHelper.createNewAttachmentFile(Context)': 'StorageHelper.java:236',
    'StorageHelper.getDbSyncDir': 'StorageHelper.java:93',
    'StorageHelper.getRealPathFromURI': 'StorageHelper.java:222',
    'StorageHelper.getStorageDir': 'StorageHelper.java:78',
    'SystemHelper.<init>': 'SystemHelper.java:29',
    'SystemHelper.copyToClipboard': 'SystemHelper.java:64',
    'Tag$1.createFromParcel': 'Tag.java:67',
    'Tag$1.newArray': 'Tag.java:72',
    'Tag.<init>()': 'Tag.java:26',
    'Tag.<init>(Parcel)': 'Tag.java:26',
    'Tag.describeContents': 'Tag.java:43',
    'Tag.toString': 'Tag.java:56',
    'Tag.writeToParcel': 'Tag.java:49',
    'TagsHelper.<init>': 'TagsHelper.java:35',
    'TextHelper.<init>': 'TextHelper.java:43',
    'UndoBarController.isVisible': 'UndoBarController.java:155',
    'UndoBarController.onRestoreInstanceState': 'UndoBarController.java:143',
    'UndoBarController.onSaveInstanceState': 'UndoBarController.java:137',
    'UpdaterTask$1.<init>': 'UpdaterTask.java',
    'UpdaterTask$1.onClick': 'UpdaterTask.java:111',
    'UpdaterTask.<init>': 'UpdaterTask.java:66',
    'UpdaterTask.doInBackground': 'UpdaterTask.java:85',
    'UpdaterTask.getAppData': 'UpdaterTask.java:168',
    'UpdaterTask.isAlive': 'UpdaterTask.java:160',
    'UpdaterTask.isVersionUpdated': 'UpdaterTask.java:193',
    'UpdaterTask.onPostExecute': 'UpdaterTask.java:128',
    'UpdaterTask.onPreExecute': 'UpdaterTask.java:74',
    'UpdaterTask.promptUpdate': 'UpdaterTask.java:102',
    'UpdaterTask.restoreReminders': 'UpdaterTask.java:147',
    'UpdaterTask.showChangelog': 'UpdaterTask.java:152',
    'VerticalSeekBar.<init>(Context)': 'VerticalSeekBar.java:33',
    'VerticalSeekBar.<init>(Context,AttributeSet)': 'VerticalSeekBar.java:33',
    'VerticalSeekBar.<init>(Context,AttributeSet,int)': 'VerticalSeekBar.java:33',
    'VerticalSeekBar.onDraw': 'VerticalSeekBar.java:67',
    'VerticalSeekBar.onMeasure': 'VerticalSeekBar.java:60',
    'VerticalSeekBar.onSizeChanged': 'VerticalSeekBar.java:49',
    'VerticalSeekBar.onTouchEvent': 'VerticalSeekBar.java:76',
    'VerticalSeekBar.setOnSeekBarChangeListener': 'VerticalSeekBar.java:114',
    'VerticalSeekBar.setProgress': 'VerticalSeekBar.java:121',
}


# =============================================================== schema 2 (see handoff/SCHEMA_V2.md)
import re

REFS.setdefault('UpdaterTask$1.<init>', 'UpdaterTask.java:107')
REFS['SettingsFragment.lambda$onResume$16'] = 'SettingsFragment.java:396-410'
REFS['BackupHelper.lambda$exportAttachments$0'] = 'BackupHelper.java:132-136'
REFS['BackupHelper.lambda$exportAttachments$1'] = 'BackupHelper.java:132-136'
REFS['SystemHelper.closeCloseable'] = 'GeocodeHelper.java:173-175'
REFS['DetailFragment.removeAttachment(Attachment)'] = 'DetailFragment.java:1956-1962'
SUPPRESS |= {('DetailFragment.onAttachingFileErrorOccurred', 'DetailFragment.removeAttachment(Attachment)'),
             ('StorageHelper.getSize(File)', 'LogDelegate.e(String,Throwable)'),     # catch NoSuchMethodError: getBlockSizeLong exists on API 27 (SDK_INT >= 18 branch, StorageHelper.java:336-345)
             ('GeocodeHelper.autocomplete', 'SystemHelper.closeCloseable'), ('GeocodeHelper.autocomplete', 'LogDelegate.e(String,Throwable)'),
             ('GeocodeHelper.autocomplete', 'LogDelegate.e(String)')}     # after the empty-key return: MAPS_API_KEY is '' in the built APK (BuildConfig.class constant)

# DEAD and FRAMEWORK_ONLY become UNREACHABLE: (kind, reason, source reference, how confirmed). The legacy reason picks the group.
_NOCALL = 'bytecode call scan, sources, layouts / menus / manifest XML and reflection searched'
_GROUPS = [
    ('The updater is never started', 'no_trigger_in_app',
     'The updater is never started: its only start site, `new UpdaterTask(this).execute()`, is a comment ("Removed due to missing backend", MainActivity.java:107); AppVersionHelper and MiscUtils.isGooglePlayAvailable are called only by it (' + _NOCALL + ')'),
    ('No caller anywhere in the app (unused screen-size', 'no_trigger_in_app', 'No caller anywhere in the app: unused screen-size helpers of Display, they only call each other (' + _NOCALL + ')'),
    ('Never instantiated and in no layout: the sketch popups', 'no_trigger_in_app',
     'Never instantiated and in no layout or other XML: VerticalSeekBar is mentioned only by its own file (the sketch popups use a plain SeekBar, res/layout/popup_sketch_stroke.xml)'),
    ('Never instantiated and in no layout', 'no_trigger_in_app', 'Never instantiated and in no layout: only the declaration mentions the class (' + _NOCALL + ')'),
    ('GeocodeHelper is used only through', 'no_trigger_in_app',
     'GeocodeHelper is used only through its static methods and never instantiated, so its LocationListener methods are never registered; the Context overload of getAddressFromCoordinates is called only by androidTest (' + _NOCALL + ')'),
    ('The play-flavor factory', 'no_trigger_in_app',
     'The play-flavor factory is compiled in but GeocodeHelper statically imports the base factory (GeocodeHelper.java:21); the factory classes are never instantiated (' + _NOCALL + ')'),
    ('No caller: the list empties the trash', 'no_trigger_in_app', 'No caller: the list empties the trash with NoteProcessorDelete and none of these queries is called anywhere (' + _NOCALL + ')'),
    ('Override of SQLiteOpenHelper.getDatabaseName()', 'framework_never_calls',
     'No app caller of the DbHelper.getDatabaseName override (' + _NOCALL + '); FW-SRC core/java/android/database/sqlite/SQLiteOpenHelper.java:139 declares the base method and nothing else in SQLiteOpenHelper calls it'),
    ('No caller in the app (integrityCheck', 'no_trigger_in_app', 'No caller in the app: integrityCheck is used by androidTest only and the "integrity check" preference has no handler (' + _NOCALL + ')'),
    ('No caller in the app (static helpers', 'no_trigger_in_app', 'No caller in the app: static helper kept for tests or never used (' + _NOCALL + ')'),
    ('Constructor of a class with only static members', 'no_trigger_in_app', 'Constructor of a class with only static members: no `new` of the class anywhere (' + _NOCALL + ')'),
    ('The intro tour never starts', 'closed_by_configuration',
     'The intro tour never starts in the debug build: MainActivity starts IntroActivity only when mustRun() is true (MainActivity.java:103-105), and mustRun() is `!OmniNotes.isDebugBuild() && ...` (IntroActivity.java:48-51) with isDebugBuild() = BuildConfig.BUILD_TYPE.equals("debug") (OmniNotes.java:55-57); nothing else starts the activity (' + _NOCALL + ')'),
    ('The "Add shortcut" menu item', 'no_trigger_in_app',
     'The "Add shortcut" menu item is never visible: it is android:visible="false" in menu_detail.xml:73-78 and the line that showed it is commented out (DetailFragment.java:1032); nothing else selects it (' + _NOCALL + ')'),
    ('ButterKnife calls the (target, source View)', 'framework_never_calls',
     'Nothing calls the one-argument activity constructor of the generated binder (' + _NOCALL + '); INFERRED ButterKnife.bind(target) uses the (target, source View) constructor (ButterKnife source not read)'),
    ('ButterKnife Unbinder.unbind()', 'no_trigger_in_app',
     'The app never stores the Unbinder that ButterKnife.bind returns and never calls unbind (every ButterKnife.bind call ignores its result; ' + _NOCALL + ')'),
    ('Activity pointer-capture callback', 'framework_never_calls',
     'The app never requests pointer capture (no requestPointerCapture call; ' + _NOCALL + '); INFERRED the framework calls onPointerCaptureChanged only after a capture request (ViewRootImpl source not read)'),
    ('The toolbar navigation listener consumes', 'framework_never_calls',
     'setNavigationOnClickListener(v -> onBackPressed()) replaces the click handling of the Up button after setSupportActionBar (SettingsActivity.java:57-66; SketchFragment.java:107 after MainActivity.java:129), so the home item is not dispatched to onOptionsItemSelected; INFERRED the AppCompat toolbar dispatches the home item only through its own navigation listener (AppCompat source not read)'),
    ('MainActivity declares no configChanges', 'framework_never_calls',
     'MainActivity declares no android:configChanges (AndroidManifest.xml: only GalleryActivity does), so a configuration change relaunches the activity and its fragments get no onConfigurationChanged; INFERRED FragmentActivity forwards onConfigurationChanged to its fragments only when the activity receives it (androidx source not read)'),
    ('Animation / attach callback', 'framework_never_calls',
     'Nothing triggers this callback: the animations in these classes have no repeat count and are never cancelled (no setRepeatCount, no cancel() in Fab, AnimationsHelper, DetailFragment) and the rows are not detached while the dialog shows; INFERRED the framework calls it only for repeating or cancelled animations and detached children (animation and RecyclerView source not read)'),
    ('Parcelable / adapter boilerplate', 'framework_never_calls',
     'Nothing calls it: no array of these classes is read from a Parcel, Tag objects are never parceled, the category rows have no stable ids, and no explicit toString call or string conversion of a Category / Tag was found (' + _NOCALL + '); INFERRED the framework reaches them only through those paths'),
    ('Custom-view constructor that layout inflation never uses', 'framework_never_calls',
     'LayoutInflater calls the (Context, AttributeSet) constructor (FW-SRC core/java/android/view/LayoutInflater.java:612-617, 645-648) and the layouts use that form; no code calls this form (' + _NOCALL + ')'),
    ('No caller in the app sources, layouts or reflection', 'no_trigger_in_app', 'No caller in the app (' + _NOCALL + ')'),
]
_SPECIAL = {
    'SettingsActivity.replaceFragment': ('branch_never_taken',
        'replaceFragment runs only inside `if (!backStack.isEmpty())` (SettingsActivity.java:78-83); backStack is created empty (line 50) and nothing ever adds to it (the only other use is the remove at line 80)'),
    'DetailFragment$OnGeoUtilResultListenerImpl.onCoordinatesResolved': ('no_trigger_in_app',
        'The method body is empty ("Nothing to do", DetailFragment.java:2184-2187); the only call of the interface method, GeocodeHelper.getCoordinatesFromAddress (GeocodeHelper.java:164-171), is called with the DetailFragment itself (DetailFragment.java:2226-2227), never with this listener'),
    'BackupHelper.lambda$exportAttachments$0': ('branch_never_taken',
        'The filter lambda runs once per element of listOld, and listOld is an empty list in the app: the only main-code caller of the four-argument exportAttachments passes null (BackupHelper.java:99), which line 109 turns into an empty list; only androidTest passes a real list'),
    'BackupHelper.lambda$exportAttachments$1': ('branch_never_taken',
        'The forEach lambda runs once per element that passes the filter over listOld, and listOld is an empty list in the app (BackupHelper.java:99, 109, 132-136); only androidTest passes a real list'),
    'DetailFragment.removeAttachment(Attachment)': ('branch_never_taken',
        'Its only caller is onAttachingFileErrorOccurred, inside `if (noteTmp.getAttachmentsList().contains(mAttachment))` (DetailFragment.java:1956-1962), and the only caller of that method, AttachmentTask.onPostExecute, passes null (AttachmentTask.java:62-68), which the attachment list never contains; the other overload, removeAttachment(int), is used by the attachment popup (DetailFragment.java:849)'),
    'SystemHelper.closeCloseable': ('closed_by_configuration',
        'Its callers are the dead updater (UpdaterTask.java:185) and GeocodeHelper.autocomplete (GeocodeHelper.java:228), which runs after the early return for an empty key (GeocodeHelper.java:173-175); MAPS_API_KEY is "" in the built APK (BuildConfig.class constant)'),
    'SettingsFragment.lambda$onResume$16': ('branch_never_taken',
        'The OnPreferenceChangeListener is registered only if findPreference("settings_colors_widget") is not null (SettingsFragment.java:396-410), and that key is in no preference XML of any source set (only code mentions it)'),
}
UNREACHABLE = {}
for _m, _t in list(DEAD.items()) + list(FRAMEWORK_ONLY.items()):
    if _m in _SPECIAL:
        _k, _x = _SPECIAL[_m]
    else:
        _k, _x = next(((k, x) for pre, k, x in _GROUPS if _t.startswith(pre)), (None, None))
        assert _k, (_m, _t[:60])
    UNREACHABLE[_m] = (_k, _x, REFS.get(_m, '?'), 'INFERRED' if 'INFERRED' in _x else 'SOURCE')
for _m, (_k, _x) in _SPECIAL.items():
    UNREACHABLE.setdefault(_m, (_k, _x, REFS.get(_m, '?'), 'INFERRED' if 'INFERRED' in _x else 'SOURCE'))
DEAD, FRAMEWORK_ONLY = {}, {}

# ---- gates: kinds by rule (the texts are written in prose, so the rules read the words)
ENV_KINDS_OF, STATE_KINDS_OF = {}, {}
ENV_PERM_STATES = {NEED_PERM_STORAGE: 'the storage permission is granted to the app (runtime permission)', NEED_PERM_LOCATION: 'the location permission is granted to the app (runtime permission)',
                   NEED_PERM_AUDIO: 'the record-audio permission is granted to the app (runtime permission)',
                   NEED_PERM_DENIED: 'the app permission was denied or is not granted yet (the system permission dialog / the rationale snackbar)'}
ENV_NET = 'the network is reachable (ConnectivityManager reports an active network)'
_START_STATE = re.compile(r'^(Opened (from a widget|by a share intent|from a shortcut|with the camera action)|The editor was opened from a widget|The list was opened from a widget|A list widget is on the home screen|The DashClock extension is active)')


def _env_kinds(t):
    tl = t.lower()
    ks = set()
    if re.search(r'location fix|microphone|device is rotated|rotation', tl):
        ks.add('hardware')
    if re.search(r'permission', tl):
        ks.add('permission')
    if 'reboots' in tl:
        return ['system_event']
    if re.search(r'time passes', tl):
        ks.add('time')
    if re.search(r'network is reachable|internet', tl):
        ks.add('network')
    if re.search(r'outside package|dashclock|widget|opened|share intent|shortcut', tl):
        ks.add('other_app')
    if re.search(r'exception|older database|device locale is ja_jp', tl):
        ks.add('other')
    return sorted(ks) or None


def _state_kinds(t):
    for rx, ks in (
        (r'text is selected|resumed before in this process|PasswordActivity is open|MainActivity has not been stopped|DetailFragment is registered|state is saved|list change was committed|A search was submitted|eraser|empty-list image|checklist was edited|attachment was added|note was changed|changes are discarded|result of Merge|intent has an action|undone in the Notes list|search label was shown|uncompleted checklists|hashtag link|undo bar|second start|reminder alarm|A recurring reminder', ['session']),
        (r'locked note exists', ['data', 'settings']),
        (r'^Settings > .*(exists|exist)|"Show uncategorized"', ['settings', 'data']),
        (r'file-logging switch', ['settings']),
        (r'language preference is already stored|^Settings >|password was set|password is set|preference value was changed|filter was switched|contracted view|past-reminders filter|archived filter', ['settings']),
        (r'backup folder exists|zip is available|backup note files|legacy backup note files exists', ['file']),
        (r'categor|#tag|recurrence rule was chosen|note already exists|note has no title|note on the list widget|note has an image|note exists|notes exist|At least two notes|has a category|note has|open (note|checklist)|attachment|gallery|selected note is archived|shortcut note|link, e-mail|reminder exists|enough notes|is a video|reminder was set|drawer', ['data']),
    ):
        if re.search(rx, t):
            return ks
    return None


CATCH_EDGES = {
    ('AlarmReceiver.onReceive', 'LogDelegate.e(String,Throwable)'): ['AlarmReceiver.java:63'],
    ('BackupHelper.exportAttachments(NotificationsHelper,File,List,List)', 'LogDelegate.w(String)'): ['BackupHelper.java:118'],
    ('BackupHelper.exportNote', 'LogDelegate.e(String)'): ['BackupHelper.java:71'],
    ('BackupHelper.getImportNote', 'LogDelegate.e(String)'): ['BackupHelper.java:181'],
    ('BackupHelper.getImportNote', 'Note.<init>()'): ['BackupHelper.java:182'],
    ('BackupHelper.importAttachments(File,NotificationsHelper)', 'LogDelegate.e(String)'): ['BackupHelper.java:222'],
    ('BaseActivity.onCreate', 'LogDelegate.w(String,Throwable)'): ['BaseActivity.java:89'],
    ('DateUtils.getLocalizedDateTime', 'LogDelegate.e(String)'): ['DateUtils.java:112'],
    ('DbHelper.execSqlFile', 'LogDelegate.e(String,Throwable)'): ['DbHelper.java:281'],
    ('DbHelper.getNotesByCategory', 'DbHelper.getAllNotes'): ['DbHelper.java:668'],
    ('DetailFragment.handleIntents', 'LogDelegate.e(String,Throwable)'): ['DetailFragment.java:545'],
    ('DetailFragment.lambda$startRecording$22', 'LogDelegate.e(String,Throwable)'): ['DetailFragment.java:1835'],
    ('DetailFragment.lambda$startRecording$22', 'MainActivity.showMessage(int,Style)'): ['DetailFragment.java:1836'],
    ('DetailFragment.startPlaying', 'LogDelegate.e(String,Throwable)'): ['DetailFragment.java:1790'],
    ('DetailFragment.startPlaying', 'MainActivity.showMessage(int,Style)'): ['DetailFragment.java:1791'],
    ('DetailFragment.toggleChecklist2(boolean,boolean)', 'LogDelegate.e(String,Throwable)'): ['DetailFragment.java:1227'],
    ('Display.getUsableSize', 'LogDelegate.e(String,Throwable)'): ['Display.java:60'],
    ('FileHelper.getDataColumn', 'LogDelegate.e(String,Throwable)'): ['FileHelper.java:122'],
    ('FileHelper.getNameFromUri', 'LogDelegate.e(String,Throwable)'): ['FileHelper.java:169'],
    ('ListFragment.editNote2', 'LogDelegate.v'): ['ListFragment.java:939'],
    ('NoteAdapter.initText', 'LogDelegate.w(String,Throwable)'): ['NoteAdapter.java:182'],
    ('RecurrenceHelper.nextReminderFromRecurrenceRule(long,long,String)', 'LogDelegate.e(String)'): ['RecurrenceHelper.java:71'],
    ('Security.decrypt', 'LogDelegate.e(String)'): ['Security.java:102'],
    ('Security.encrypt', 'LogDelegate.w(String,Throwable)'): ['Security.java:76'],
    ('Security.md5', 'LogDelegate.w(String,Throwable)'): ['Security.java:57'],
    ('SettingsFragment.onResume', 'LogDelegate.e(String,Throwable)'): ['SettingsFragment.java:478'],
    ('SketchFragment.onActivityCreated', 'LogDelegate.e(String,Throwable)'): ['SketchFragment.java:118'],
    ('SketchFragment.save', 'LogDelegate.e(String,Throwable)'): ['SketchFragment.java:225'],
    ('SpringImportHelper.importDataFromSpringpad', 'LogDelegate.e(String)'): ['SpringImportHelper.java:277'],
    ('SpringImportHelper.importDataFromSpringpad', 'LogDelegate.w(String)'): ['SpringImportHelper.java:305'],
    ('SpringImportHelper.importDataFromSpringpad', 'NotificationsHelper.<init>'): ['SpringImportHelper.java:77'],
    ('SpringImportHelper.importDataFromSpringpad', 'NotificationsHelper.createNotification'): ['SpringImportHelper.java:78'],
    ('SpringImportHelper.importDataFromSpringpad', 'NotificationsHelper.setLedActive'): ['SpringImportHelper.java:80'],
    ('SpringImportHelper.importDataFromSpringpad', 'NotificationsHelper.show()'): ['SpringImportHelper.java:80'],
    ('SpringImportHelper.importDataFromSpringpad', 'StorageHelper.createAttachmentFromUri(Context,Uri,boolean)'): ['SpringImportHelper.java:275'],
    ('StorageHelper.copyFile(File,File)', 'LogDelegate.e(String,Throwable)'): ['StorageHelper.java:172'],
    ('StorageHelper.copyFile(InputStream,OutputStream)', 'LogDelegate.e(String,Throwable)'): ['StorageHelper.java:190'],
    ('StorageHelper.createAttachmentFromUri(Context,Uri,boolean)', 'LogDelegate.e(String)'): ['StorageHelper.java:474'],
    ('StorageHelper.createExternalStoragePrivateFile', 'FileHelper.getPath'): ['StorageHelper.java:124'],
    ('StorageHelper.createExternalStoragePrivateFile', 'LogDelegate.e(String,Throwable)'): ['StorageHelper.java:146'],
    ('StorageHelper.createNoMediaFile', 'LogDelegate.e(String)'): ['StorageHelper.java:311'],
    ('StorageHelper.delete', 'LogDelegate.e(String)'): ['StorageHelper.java:215'],
    ('SystemHelper.closeCloseable', 'LogDelegate.w(String,Throwable)'): ['SystemHelper.java:58'],
    ('UpdaterTask.doInBackground', 'LogDelegate.w(String,Throwable)'): ['UpdaterTask.java:95'],
    ('UpgradeProcessor.process', 'LogDelegate.e(String,Throwable)'): ['UpgradeProcessor.java:77'],
}


# Calls found by the bytecode scan whose line table puts them one or two lines early or late (tools/check_bytecode_lines.py)
FIX_LINES = {
    ('CategoryMenuTask.lambda$buildCategoryMenuClickEvent$3', 'NavigationUpdatedEvent.<init>', 'SRC CategoryMenuTask.java:169 (bytecode)'): 'SRC CategoryMenuTask.java:168 (bytecode line was 169)',
    ('CategoryMenuTask.onPostExecute', 'CategoryBaseAdapter.<init>(Activity,List,String)', 'SRC CategoryMenuTask.java:92 (bytecode)'): 'SRC CategoryMenuTask.java:91 (bytecode line was 92)',
    ('DbHelper.getAttachments', 'Attachment.<init>(long,Uri,String,long,long,String)', 'SRC DbHelper.java:805 (bytecode)'): 'SRC DbHelper.java:803 (bytecode line was 805)',
    ('DbHelper.getCategories', 'Category.<init>(Long,String,String,String,int)', 'SRC DbHelper.java:853 (bytecode)'): 'SRC DbHelper.java:851 (bytecode line was 853)',
    ('DbHelper.getCategory', 'Category.<init>(Long,String,String,String)', 'SRC DbHelper.java:927 (bytecode)'): 'SRC DbHelper.java:926 (bytecode line was 927)',
    ('DbHelper.getNotes', 'Category.<init>(Long,String,String,String)', 'SRC DbHelper.java:472 (bytecode)'): 'SRC DbHelper.java:471 (bytecode line was 472)',
    ('DetailFragment.categorizeNote', 'CategoryRecyclerViewAdapter.<init>(Activity,List)', 'SRC DetailFragment.java:1253 (bytecode)'): 'SRC DetailFragment.java:1254 (bytecode line was 1253)',
    ('ListFragment.categorizeNotes', 'CategoryRecyclerViewAdapter.<init>(Activity,List)', 'SRC ListFragment.java:1478 (bytecode)'): 'SRC ListFragment.java:1479 (bytecode line was 1478)',
    ('MainMenuTask.buildMainMenu', 'NavigationItem.<init>', 'SRC MainMenuTask.java:112 (bytecode)'): 'SRC MainMenuTask.java:111 (bytecode line was 112)',
    ('NotesHelper.addAttachments', 'Attachment.getUri', 'SRC NotesHelper.java:74 (bytecode)'): 'SRC NotesHelper.java:73 (bytecode line was 74)',
    ('ReminderHelper.lambda$showReminderMessage$0', 'DateHelper.getDateTimeShort', 'SRC ReminderHelper.java:91 (bytecode)'): 'SRC ReminderHelper.java:90 (bytecode line was 91)',
}


def EDIT(x):
    """Gates by rule: permissions, launcher / widget starts, rotation and time as ENV; the prose of a gesture as a guard."""
    env, st = x['env'], x['needs_state']
    parts = [env] if env else []
    if st in ENV_PERM_STATES:
        parts.append(ENV_PERM_STATES[st]); st = None
    elif st == NEED_REMINDER_FIRED:
        parts.append('time passes until the alarm of a reminder set a minute ahead fires'); st = 'A note has a reminder that was set a minute ahead'
    elif st and _START_STATE.search(st):
        parts.append(st); st = None
    elif st == 'The editor was recreated after a rotation':
        parts.append('the device is rotated (MainActivity has no configChanges, so the activity and the editor are recreated)'); st = None
    elif st and st.startswith('The swipe starts within 30 px'):
        x['guard'] = st; st = None
    if x['dst'] in ('S_DLG_LOCATION', 'S_DETAIL@NEW') and x['src'] == 'DetailFragment$OnGeoUtilResultListenerImpl.onLocationRetrieved':
        parts.append(ENV_NET)       # ConnectionManager.internetAvailable decides which branch runs (DetailFragment.java:2203-2209)
    if (x['src'], x['dst']) in (('StorageHelper.createNewAttachmentFileFromHttp', 'StorageHelper.getFromHttp'), ('SpringImportHelper.importDataFromSpringpad', 'StorageHelper.createNewAttachmentFileFromHttp')):
        parts.append(ENV_NET)
    if x['evidence'] and re.search(r'\bRx', x['trigger'] or '') and FW_ASYNC in x['evidence']:
        x['evidence'] = x['evidence'].replace(FW_ASYNC, 'INFERRED RxJava runs the operator callback on its scheduler (RxJava / RxPermissions source not read)')
    ev_ = x['evidence'] or ''
    if FW_ASYNC in ev_:
        t_ = x['trigger'] or ''
        if t_.startswith('IntentService.onHandleIntent'):
            x['evidence'] = ev_.replace(FW_ASYNC, 'FW-SRC core/java/android/app/IntentService.java:70-78, 112-132 (onCreate starts a HandlerThread; onStart queues the intent as a message and the ServiceHandler calls onHandleIntent on that worker thread)')
        elif 'Filter.filter runs performFiltering' in t_:
            x['evidence'] = ev_.replace(FW_ASYNC, 'FW-SRC core/java/android/widget/Filter.java:101-124, 215-241 (filter() posts the request to a HandlerThread whose RequestHandler calls performFiltering)')
        elif 'suggestions are published on the main thread' in t_:
            x['evidence'] = ev_.replace(FW_ASYNC, 'FW-SRC core/java/android/widget/Filter.java:262-285 (the ResultsHandler runs in the UI thread and calls publishResults)')
    if (x['src'], x['dst']) in CATCH_EDGES and not x['env']:
        mm_ = re.search(r'SRC ([\w./$-]+\.java:\d+) \(bytecode', x['evidence'] or '')
        if mm_ and mm_.group(1) in CATCH_EDGES[(x['src'], x['dst'])]:
            parts.append(ENV_EXC2)
            x['guard'] = x['guard'] or 'the call is inside a catch block: the exception is thrown'
    if (x['src'], x['dst']) == ('ShortcutHelper.removeshortCut', 'DateHelper.getFormattedDate'):
        x['guard'] = 'the note title is empty (ternary at ShortcutHelper.java:93-95)'
        st = 'The note has no title'
    if (x['src'], x['dst']) == ('ListRemoteViewsFactory.getViewAt', 'BitmapHelper.getBitmapFromAttachment'):
        x['guard'] = '!note.isLocked() && showThumbnails && the note has attachments (ListRemoteViewsFactory.java:119-121)'
        st = 'A note on the list widget has an attachment and the widget shows thumbnails'
    if (x['src'], x['dst']) == ('BitmapHelper.getBitmapFromAttachment', 'BitmapHelper.getImageBitmap'):
        x['guard'] = 'the attachment is a video, an image or a sketch (BitmapHelper.java:50-52)'
        st = 'A note has an image, sketch or video attachment'
    if (x['src'], x['dst']) == ('LanguageHelper.updateLanguage', 'LanguageHelper.getLocale'):
        x['guard'] = 'a language is passed in, or the language preference is already stored (LanguageHelper.java:50-58)'
        st = 'The language preference is already stored (an earlier start of the app, or the language was chosen in Settings)'
    if x['src'] == 'SnoozeActivity.setNextRecurrentReminder' and x['dst'].startswith('RecurrenceHelper.nextReminderFromRecurrenceRule'):
        x['guard'] = 'the note has a recurrence rule (SnoozeActivity.java:55-60)'
        st = 'A recurrence rule was chosen in the reminder picker'
    if (x['src'], x['dst']) == ('AttachmentTask.onPostExecute', 'DetailFragment.onAttachingFileErrorOccurred'):
        x['guard'] = 'mAttachment == null: the chosen file could not be copied (AttachmentTask.java:62-68)'
        parts.append(ENV_EXC2)
    if x['src'].startswith('BackupHelper.exportAttachments(NotificationsHelper') and x['dst'] == 'LogDelegate.w(String)':
        x['guard'] = 'for an attachment whose file is missing (BackupHelper.java:112-120)'
        st = 'A note has an attachment (the backup copies the attachments)'
    if (x['src'], x['dst']) == ('S_DLG_FOLDER_CHOOSER', 'SettingsActivity.onFolderSelection'):
        st = 'A folder with legacy backup note files exists on storage'
    if (x['src'], x['dst']) == ('DateHelper.getFormattedDate', 'DateUtils.prettyTime(Long)'):
        x['guard'] = 'the prettified-dates preference is on (default on; DateHelper.java:112-115)'
    if x['src'] == 'LogDelegate.isFileLoggingEnabled' and x['dst'] == 'OmniNotes.getSharedPreferences':
        x['guard'] = 'the first logging call in the process: the static fileLoggingEnabled is still null (LogDelegate.java:93-94)'
    if x['src'] == 'LogDelegate.isFileLoggingEnabled' and x['dst'] in ('OmniNotes.getAppContext', 'StorageHelper.getExternalStoragePublicDir'):
        x['guard'] = 'the file-logging preference is true when the process makes its first logging call (LogDelegate.java:93-99)'
        st = 'The file-logging switch was turned on in Settings in an earlier run of the app (LogDelegate reads it once per process)'
    if x['src'] == 'OmniNotes.onCreate' and x['dst'] in ('NotificationsHelper.initNotificationChannels', 'NotificationsHelper.<init>', 'OmniNotes.enableStrictMode'):
        x['guard'] = x['guard'] or "the app's own process: initLeakCanary() is false there (true only in LeakCanary's analyzer process, OmniNotes.java:83-85, 104-110)"
    if (x['src'], x['dst']) == ('ONDashClockExtension.onUpdateData', 'ONDashClockExtension.getNoteTitle'):
        x['guard'] = 'a note with a reminder that has not fired is due today or within 24 hours (ONDashClockExtension.java:79-96,122-132)'
        st = 'A note has a reminder that is due today or within 24 hours and has not fired yet'
    if (x['src'], x['dst']) == ('ONDashClockExtension.getNotesCounters', 'DateUtils.isSameDay'):
        x['guard'] = 'the note has a reminder that has not fired (ONDashClockExtension.java:124-126)'
        st = 'A note has a reminder that is due today or within 24 hours and has not fired yet'
    if (x['src'], x['dst']) == ('AlarmReceiver.createNotification', 'BitmapHelper.getBitmapFromAttachment'):
        x['guard'] = 'the reminded note has an attachment and the first one is not a file attachment (AlarmReceiver.java:120-125)'
        st = 'A note has an image, sketch or video attachment'
    if x['src'].startswith('CategoryActivity.saveCategory') and not x['guard']:
        x['guard'] = 'the name field is not empty (CategoryActivity.java:138-141)'
    if (x['src'], x['dst']) == ('MainActivity.onBackPressed@SKETCH_DRAWN', 'Attachment.<init>(Uri,String)') and 'INFERRED' not in (x['evidence'] or ''):
        x['evidence'] += '; INFERRED androidx FragmentManager pops the back stack and runs the lifecycle of the editor fragment again (androidx source not read)'
    if x['src'].startswith('GeocodeHelper.lambda$getCoordinatesFromAddress') and x['dst'] == 'DetailFragment.onCoordinatesResolved':
        x['guard'] = 'the geocoder returned at least one result (GeocodeHelper.java:167)'
    if (x['src'], x['dst']) == ('FileHelper.getPath', 'FileHelper.isMediaDocument'):
        x['guard'] = 'isDocumentUri(uri) is true and the document is neither an external-storage nor a downloads document (FileHelper.java:55-75)'
        parts.append('outside package: the picker app returns a document URI of another provider than external storage or downloads')
        st = None
    if (x['src'], x['dst']) == ('NotificationsHelper.initNotificationChannels', 'NotificationChannels.<clinit>'):
        x['guard'] = 'SDK_INT > 26: true on API 27; the class is first used by getChannels() inside that check (NotificationsHelper.java:56-57)'
    if (x['src'], x['dst']) == ('NotificationsHelper.initNotificationChannels', 'NotificationChannels.getChannels'):
        x['guard'] = 'SDK_INT > 26: true on API 27 (NotificationsHelper.java:56)'
    if (x['src'], x['dst']) == ('MainActivity.onResume', 'ListFragment.onResume'):
        x['guard'] = 'the ListFragment already exists (added by init() on the first resume)'
        st = 'MainActivity was resumed before in this process (the static isPasswordAccepted is already true)'
    if (x['src'], x['dst']) == ('MainActivity.onResume', 'MainActivity.init'):
        x['guard'] = 'isPasswordAccepted is true (MainActivity.java:113-114)'
        st = 'MainActivity was resumed before in this process (the static isPasswordAccepted is already true)'
    if (x['src'], x['dst']) == ('ListFragment.onResume', 'ListFragment.initNotesList'):
        x['guard'] = 'prefsChanged is false and the activity intent action is ACTION_SEARCH (ListFragment.java:389-397)'
        st = 'A search was submitted (search bar) or instant search is on'
    if (x['src'], x['dst']) == ('ListFragment.onResume', 'ListFragment.init'):
        x['guard'] = 'mainActivity.prefsChanged is true (ListFragment.java:389-393)'
        st = 'A preference value was changed (Settings, drawer navigation)'
    if x['src'] == 'NotesHelper.addAttachments' and x['dst'].startswith('StorageHelper.createAttachmentFromUri'):
        x['guard'] = 'keepMergedNotes is true and the merged note has attachments (NotesHelper.java:70-78)'
        st = 'A merged note has an attachment and "keep merged notes" is chosen in the merge dialog'
    if (x['src'], x['dst']) == ('FileHelper.getPath', 'MediaStoreFactory.<init>'):
        x['guard'] = 'isMediaDocument(uri): the URI is a document of the media provider (FileHelper.java:75-86)'
        parts.append('outside package: the picker app returns a document URI of the media provider (com.android.providers.media.documents)')
        st = None
    if (x['src'], x['dst']) == ('BackupHelper.importNotes', 'BackupHelper.importNote'):
        x['guard'] = 'the backup folder holds a note file named <13 digits>.json (BackupHelper.java:147)'
    if (x['src'], x['dst']) == ('BackupHelper.getImportNote', 'Note.buildFromJson'):
        x['guard'] = 'the note file is not empty (BackupHelper.java:175)'
    if (x['src'], x['dst']) == ('Note.buildFromJson', 'Attachment.<init>(BaseAttachment)'):
        x['guard'] = 'the note JSON has an attachments array'
        st = 'A backup folder exists whose note files contain attachments (exported earlier)'
    for (src_, dst_, old_), new_ in FIX_LINES.items():
        if x['src'] == src_ and x['dst'] == dst_ and old_ in (x['evidence'] or ''):
            x['evidence'] = x['evidence'].replace(old_, new_)
    x['needs_state'] = st
    x['env'] = '; '.join(dict.fromkeys(parts)) or None
    if x['env']:
        ks = set()
        for p_ in parts:
            ks |= set(_env_kinds(p_) or [])
        x['env_kinds'] = sorted(ks)
    if st:
        x['state_kinds'] = _state_kinds(st) or []


def CLASSIFY(x):
    """Edge classes that differ from the default of their kind (see SCHEMA_V2.md)."""
    ev = (x['evidence'] or '') + ' ' + (x['trigger'] or '')
    dst = x['dst'].split('@')[0]
    if 'greenrobot EventBus' in ev:
        return ('non_standard', 'EventBus: post() looks the subscribers up by event class')
    if 'ButterKnife.bind(' in ev or 'DebouncingOnClickListener' in ev:
        return ('non_standard', 'ButterKnife: the generated binder / click listener is called by reflection or built by the generated code')
    if 'Method.invoke' in ev or 'reflective' in ev or 'reflection: ' in ev:
        return ('non_standard', 'reflection (java.lang.reflect.Method / the loader looks the method up by name)')
    if 'createFromParcel' in dst or 'newArray' in dst:
        return ('non_standard', 'Parcel finds the static CREATOR field of the class by reflection')
    if 'FragmentFactory' in ev:
        return ('non_standard', 'FragmentFactory instantiates the fragment by reflection')
    if 'LayoutInflater.java:612' in ev or 'ViewStub' in ev:
        return ('non_standard', 'LayoutInflater builds the view named in the XML layout by reflection')
    if x['kind'] == 'FRAMEWORK' and re.search(r'\.(writeToParcel|describeContents)$', dst):
        return ('standard', 'Parcelable protocol: the framework calls writeToParcel / describeContents of an object the app put into an Intent, a Bundle or the saved state')
    if 'ACRA' in ev:
        return ('non_standard', 'ACRA reads the BuildConfig class by reflection')
    if re.search(r'SmartLocation|RxJava|\bRx\b|RxPermissions', ev):
        return ('non_standard', 'Rx / SmartLocation library delivers the callback')
    if x['kind'] in ('ENTRY', 'SYSTEM', 'INTENT') and re.search(r'(Receiver|Service|Provider|Extension)\.<init>$', dst) and 'AndroidManifest' in ev:
        return ('non_standard', 'manifest component started through an intent action / system event (resolved by name, not by the app)')
    if x['kind'] == 'ENTRY' and x['env'] and dst == 'MainActivity.<init>':
        return ('non_standard', 'implicit intent resolved by its action / data through a manifest intent filter')
    if x['kind'] == 'ENTRY' and dst.endswith('.<clinit>'):
        return ('standard', 'JVM class initialisation')
    if (x['src'], x['dst']) == ('MainActivity.onBackPressed@SKETCH_DRAWN', 'Attachment.<init>(Uri,String)'):
        return ('standard', 'Back saves the sketch and pops the sketch fragment; the editor fragment is resumed by the fragment lifecycle and attaches the saved sketch')
    if x['dst'].startswith('S_'):
        return ('page', None)
    if x['kind'] == 'CALL' and '_ViewBinding' in x['src']:
        return ('explicit', 'call inside the ButterKnife-generated binder')
    return None


STRICT = True
