# Diary v1.105 (billthefarmer/diary@07bb05c3b7a8ea90db5efdc8f574b9f334402a71) trigger graph definition.
# Built by hand from all 11 app source files (Diary, FileUtils, Editor, DiaryWidgetProvider, DiaryWidgetUpdate,
# SettingsFragment, QueryHandler, Settings, DatePickerPreference, AboutPreference and the vendored
# android/support/v4/content/FileProvider, which is treated as app code), AndroidManifest.xml, res/menu/main.xml,
# res/layout/*, res/xml/{preferences,widget,filepaths}.xml and assets/help.md. Executed by tools/build_graph.py.
#
# Evidence labels (schema 2, see handoff/SCHEMA_V2.md): SRC <file>:<line> (app source/resources); FW-SRC <path under
# .plan/fw_src/android-8.1.0_r1>:<line> for framework source that was opened (the target API level of the baseline is 27);
# FW-SRC lib <library@version>/<file> for the two libraries pinned in build.gradle (CustomCalendarView v1.06, MarkdownView
# v1.11); INFERRED for a claim whose code was not read (another app, WebView, libcore, ...); the segment says what was not read.
#
# Conventions (see .plan/plan.md section 4):
# - Menus: one GUI edge page -> Diary.onOptionsItemSelected@<CTX>, then one CALL edge per item whose trigger contains
#   'switch case R.id.<id>'. The ids lack the action_ prefix the CSV builder looks for, so each item CALL edge carries
#   its own gui step ('Tap More options (⋮) -> Share…'); android.R.id.home has no gui (the builder labels it).
# - Preference-dependent behaviour is reached through Settings (@CONTEXT page variants); the same behaviour on a later
#   start (preference already persisted) is kept as a needs_state edge so first-path searches go through Settings.
# - S_DIARY_PLAIN (markdown off) is entered only from the Settings path; shared handlers keep their ENTERS edges into
#   markdown pages (accepted approximation, README "Limits").

TITLE = 'Diary v1.105 trigger graph'

# ---------------------------------------------------------------- environment conditions (edge field env)
ENV_NOPERM = 'storage/calendar runtime permissions not granted yet (a fresh install without auto-grant, or the permissions revoked)'
ENV_PERM = 'storage permission granted'
ENV_24H = ('device locale whose SHORT time format is 24-hour without AM/PM (e.g. en-GB, de-DE); in en-US "10:30" '
           'fails to parse')
ENV_CAL_ACCOUNT = 'at least one calendar exists in the Calendar provider (an account with a calendar)'
ENV_CAL_EVENT = 'the Calendar provider has an event on the shown diary date'
ENV_IO_ERROR = 'writing the target file fails with an I/O error (e.g. storage full or read-only location)'
ENV_NO_PATH = ('the picked document has no readable local file path (e.g. a cloud provider), so the URI stays '
               'content://')

# ---------------------------------------------------------------- needs_state texts (state built by an earlier visit)
NS_INDEX = 'Use index was ticked in Settings on an earlier visit (persisted) and Diary is started again from the launcher'
NS_THEME = 'Theme was changed in Settings while this Diary instance stayed in the back stack'
NS_DATEPREF = 'Index page or Template page was set with OK on an earlier Settings visit (the key is now persisted)'
NS_WIDGET = 'a Diary widget is already on the home screen'
NS_TASK = 'a Diary task is alive in the background (Diary opened earlier and left with Home)'
NS_SAMENAME = "an image with the same file name was already copied into this month's folder"
NS_EDITMODE = ('Diary was left (Home, rotation, Settings, Editor, picker, ...) while the text editor was shown '
               '(shown == false survives in the instance or the saved state)')
NS_PLAIN = 'Use markdown was unticked in Settings on an earlier visit (persisted)'
NS_CUSTOM_OFF = 'Use custom calendar was unticked in Settings on an earlier visit (persisted)'
NS_TEMPLATE = 'Use template was ticked in Settings on an earlier visit (persisted)'
NS_TEMPLATE_PLAIN = 'Use template ticked and Use markdown unticked in Settings on an earlier visit (persisted)'
NS_COPY = 'Copy images was ticked in Settings on an earlier visit (persisted)'
NS_INDEX_PAGE = 'Use index was ticked in Settings on an earlier visit (persisted)'
NS_BAD_INDEX_TEMPLATE = 'an invalid date pattern (e.g. <<date q>>) was saved as Index template in Settings earlier'
NS_BAD_TEMPLATE_PAGE = 'the Template page entry contains an invalid <<date ...>> pattern (written earlier)'
NS_HAVEMEDIA = ('media was received from another app earlier and its date dialog was cancelled, so haveMedia is '
                'still true in this Diary instance')

# ---------------------------------------------------------------- framework evidence (checked in .plan/fw_src)
FWS = 'FW-SRC '
F_MENU_FIRST = (FWS + 'core/java/com/android/internal/policy/PhoneWindow.java:2696-2704 (installDecor posts the first '
                'panel invalidation instead of building the menu inside onCreate), 999-1027 (doInvalidatePanelMenu -> '
                'preparePanel), 612-659 (onCreatePanelMenu, onPreparePanel); core/java/android/app/Activity.java:'
                '3386-3388, 3404-3406')
F_INVALIDATE = (FWS + 'core/java/android/app/Activity.java:3512-3516 (invalidateOptionsMenu) -> core/java/com/android/'
                'internal/policy/PhoneWindow.java:983-988 (posted), 999-1027 (menu cleared and prepared again), 612-659;'
                ' Activity.java:3386-3388, 3404-3406')
F_OVERFLOW = (FWS + 'core/java/android/widget/ActionMenuPresenter.java:997-1006 (OpenOverflowRunnable -> changeMenuMode)'
              ' -> core/java/com/android/internal/view/menu/MenuBuilder.java:767-769 -> core/java/com/android/internal/'
              'policy/PhoneWindow.java:1246-1265 (reopenMenu calls onPreparePanel again) -> core/java/android/app/'
              'Activity.java:3404-3406')
F_SEARCH_EXPAND = (FWS + 'core/java/com/android/internal/view/menu/MenuBuilder.java:907-913 (the item is dispatched to '
                   'onOptionsItemSelected first, then expandActionView); core/java/android/widget/SearchView.java:'
                   '1358-1365 (onActionViewExpanded sets the text to ""), 1249-1252 (onQueryTextChange when the text '
                   'differs from mOldQueryText, which starts null)')
F_SEARCH_COLLAPSE = (FWS + 'core/java/android/widget/SearchView.java:1346-1347 (onActionViewCollapsed -> setQuery("")), '
                     '559-560, 1249-1252')
F_SEARCH_SUBMIT = (FWS + 'core/java/android/widget/SearchView.java:1230-1236 (IME action), 972-973 (submit button), '
                   '1255-1259 (onQueryTextSubmit only for a non-empty query)')
F_SEARCH_BACK = (FWS + 'core/java/android/widget/SearchView.java:1992-2014 (Back while the search field has focus only '
                 'clears focus and hides the keyboard)')
F_SETTEXT = (FWS + 'core/java/android/widget/TextView.java:5290-5296, 5398-5403 (setText notifies beforeTextChanged, '
             'onTextChanged, afterTextChanged)')
F_EDITABLE = (FWS + 'core/java/android/widget/TextView.java:11912-11939 (ChangeWatcher forwards Editable insert/append/'
              'replace to the TextWatchers); 4920-4924 (append edits the Editable)')
F_BACK = (FWS + 'core/java/android/app/Activity.java:3001-3010 (onBackPressed: collapse an expanded action view, '
          'otherwise finish)')
F_SAVESTATE = (FWS + 'core/java/android/app/ActivityThread.java:4021-4032 (performStopActivityInner: onSaveInstanceState '
               'before onStop, skipped when the activity is finishing)')
F_RELAUNCH = (FWS + 'core/java/android/app/ActivityThread.java:4667-4673 (relaunch on a configuration change or '
              'recreate: pause, save state, destroy, new instance); core/java/android/app/Activity.java:5472-5481 '
              '(recreate -> requestActivityRelaunch); SRC AndroidManifest.xml:52-83, 85-98, 100-102 (the Diary, Editor and '
              'Settings activities declare no android:configChanges)')
F_RESTORE = (FWS + 'core/java/android/app/ActivityThread.java:2741-2751 (performStart, then onRestoreInstanceState when '
             'saved state exists)')
F_RESULT = (FWS + 'core/java/android/app/ActivityThread.java:4294-4316 (handleSendResult: onActivityResult is delivered '
            'before performResume)')
F_PERMRESULT = (FWS + 'core/java/android/app/Activity.java:4370-4382 (requestPermissions starts the system grant '
                'activity for result), 7259-7270, 7412-7419 (the result calls onRequestPermissionsResult); '
                'ActivityThread.java:4294-4316')
F_GESTURE_DOWN = FWS + 'core/java/android/view/GestureDetector.java:593 (onDown for every ACTION_DOWN)'
F_GESTURE_DOUBLE = (FWS + 'core/java/android/view/GestureDetector.java:385-386 (SimpleOnGestureListener is also the '
                    'double-tap listener), 556-565 (onDoubleTap on the second ACTION_DOWN)')
F_GESTURE_FLING = (FWS + 'core/java/android/view/GestureDetector.java:630-656 (onFling on ACTION_UP above the minimum '
                   'fling velocity)')
F_ASYNC_PRE = FWS + 'core/java/android/os/AsyncTask.java:648 (execute -> onPreExecute on the calling thread)'
F_ASYNC_BG = FWS + 'core/java/android/os/AsyncTask.java:333 (doInBackground on a worker thread)'
F_ASYNC_POST = FWS + 'core/java/android/os/AsyncTask.java:691-695 (onPostExecute on the main thread)'
F_AQH = (FWS + 'core/java/android/content/AsyncQueryHandler.java:340-348 (onQueryComplete / onInsertComplete on the '
         'handler thread)')
F_PROVIDER_START = (FWS + 'core/java/android/app/ActivityThread.java:5720-5722 (installContentProviders when the process '
                    'binds, before any activity or receiver), 6236-6239 (localProvider.attachInfo)')
F_PROVIDER_ONCREATE = FWS + 'core/java/android/content/ContentProvider.java:1912-1917 (attachInfo -> onCreate)'
F_DATEPICKER_OK = FWS + 'core/java/android/app/DatePickerDialog.java:164-171 (OK -> OnDateSetListener.onDateSet)'
F_CCD_OK = (FWS + 'lib CustomCalendarView@v1.06/CustomCalendarDialog.java:107-120 (OK -> listener.onDateSet; Cancel '
            'does nothing)')
F_DECORATE = (FWS + 'lib CustomCalendarView@v1.06/CustomCalendarView.java:404, 440 (each day cell calls DayView.decorate '
              'when the month is drawn), 245-249 (month arrows redraw); DayView.java:51-60 (decorate -> '
              'DayDecorator.decorate)')
F_MD_LOAD = (FWS + 'lib MarkdownView@v1.11/MarkdownView.java:270-280 (loadMarkdown -> loadDataWithBaseURL); '
             'INFERRED the WebView engine (Chromium, native code outside the Java sources) then calls WebViewClient.onPageFinished')
F_WVC_URL = (FWS + 'core/java/android/webkit/WebViewClient.java:76-77 (the WebResourceRequest overload delegates to the '
             'String overload); INFERRED the WebView engine (Chromium, native code outside the Java sources) asks shouldOverrideUrlLoading for a tapped link')
F_PREF_CLICK = (FWS + 'core/java/android/preference/Preference.java:1129-1146 (performClick: onClick, then the '
                'fragment\'s onPreferenceTreeClick)')
F_PREF_INIT = (FWS + 'core/java/android/preference/Preference.java:1323-1328 (onAttachedToHierarchy -> '
               'dispatchSetInitialValue), 1547-1561 (onSetInitialValue(true, null) only when the key is persisted; '
               'never without android:defaultValue otherwise)')
F_SPI = (FWS + 'core/java/android/app/SharedPreferencesImpl.java:499-508, 551-561 (only keys whose value changed are '
         'reported to OnSharedPreferenceChangeListener)')
F_CHECKBOX = FWS + 'core/java/android/preference/TwoStatePreference.java:61-81 (onClick -> setChecked -> persistBoolean); ' + F_SPI[len(FWS):]
F_DLGPREF_SHOW = (FWS + 'core/java/android/preference/DialogPreference.java:274-300 (onClick -> showDialog -> '
                  'onCreateDialogView, onBindDialogView)')
F_DLGPREF_CLOSE = FWS + 'core/java/android/preference/DialogPreference.java:395 (dismiss -> onDialogClosed(OK pressed))'
F_EDITTEXT_PREF = FWS + 'core/java/android/preference/EditTextPreference.java:142-148 (OK -> setText -> persist); ' + F_SPI[len(FWS):]
F_LIST_PREF = FWS + 'core/java/android/preference/ListPreference.java:277-283 (a picked entry -> setValue -> persist); ' + F_SPI[len(FWS):]
F_WIDGET_UPDATE = (FWS + 'core/java/android/appwidget/AppWidgetProvider.java:61-67 (APPWIDGET_UPDATE -> onUpdate only '
                   'for a non-empty id list)')
F_WIDGET_OPTIONS = FWS + 'core/java/android/appwidget/AppWidgetProvider.java:74-81 (APPWIDGET_OPTIONS_CHANGED -> onAppWidgetOptionsChanged)'
F_WIDGET_BIND = (FWS + 'services/appwidget/java/com/android/server/appwidget/AppWidgetServiceImpl.java:1129-1139 '
                 '(bindAppWidgetId sends APPWIDGET_ENABLED and APPWIDGET_UPDATE), 2277-2288 (explicit component)')
F_WIDGET_PERIODIC = (FWS + 'services/appwidget/java/com/android/server/appwidget/AppWidgetServiceImpl.java:2311-2335 '
                     '(an inexact repeating alarm every updatePeriodMillis sends APPWIDGET_UPDATE)')
F_WIDGET_DELETE = (FWS + 'services/appwidget/java/com/android/server/appwidget/AppWidgetServiceImpl.java:1752-1767, '
                   '2290-2295 (APPWIDGET_DELETED, explicit component)')
F_WIDGET_OPTS_SVC = (FWS + 'services/appwidget/java/com/android/server/appwidget/AppWidgetServiceImpl.java:1448-1474, '
                     '2299-2305 (updateAppWidgetOptions -> APPWIDGET_OPTIONS_CHANGED, explicit component)')
F_APPWIDGET_PKG = (FWS + 'services/core/java/com/android/server/am/ActivityManagerService.java:19198-19224 '
                   '(APPWIDGET_UPDATE sent by an app is limited to the caller\'s package) + services/core/java/com/'
                   'android/server/am/BroadcastQueue.java:1267-1279 (the background-receiver skip needs component and '
                   'package both null)')
F_SHARE_GRANT = (FWS + 'core/java/android/content/Intent.java:9998-10012 (migrateExtraStreamToClipData: the SEND stream '
                 'gets FLAG_GRANT_READ_URI_PERMISSION only)')
F_LISTFILES = 'INFERRED java.io / java.util library behaviour (libcore source not read): File.listFiles(FilenameFilter) calls accept(dir, name) for every directory entry'
F_SORT = 'INFERRED java.io / java.util library behaviour (libcore source not read): Arrays.sort(T[], Comparator) calls compare for arrays with at least 2 elements'

PREF_READS = ['pref:pref_theme', 'pref:pref_copy_media', 'pref:pref_custom', 'pref:pref_extended', 'pref:pref_external',
              'pref:pref_markdown', 'pref:pref_use_index', 'pref:pref_use_template', 'pref:pref_index_page',
              'pref:pref_template_page', 'pref:pref_folder', 'pref:pref_index_template']

SCREENS = {
    'S_ENTRY': 'Outside the app: launcher, home screen, another app (search root)',
    'S_EXIT': 'Diary/Editor finished (Back on the root) or crashed; the process may survive (static QueryHandler, FileProvider.sCache kept)',
    'S_DIARY_PAUSED': 'Diary paused/stopped: Home, another activity on top (Settings, Editor, picker, chooser, print, permission dialog, browser), or mid-rotation',
    'S_EDITOR_PAUSED': 'Editor in the background (Home / recents)',
    'S_SETTINGS_PAUSED': 'Settings in the background (Home / recents)',
    'S_DIARY_VIEW': 'Diary, MarkdownView shown (shown == true), Edit (pencil) button, no unsaved changes; menu main.xml without Cancel; Index/Add link hidden',
    'S_DIARY_VIEW_CHANGED': 'Diary, MarkdownView shown with unsaved changes (changed == true): Cancel (✕) visible. First start (help text) and after Add time/events/media/link',
    'S_DIARY_EDIT': 'Diary, EditText shown (shown == false), Accept (✓) button, no unsaved changes',
    'S_DIARY_EDIT_CHANGED': 'Diary, EditText after typing: Cancel (✕) visible, Accept saves',
    'S_DIARY_SEARCH': 'Diary with the SearchView expanded in the action bar; Find all appears when the overflow is opened. @VIEW: the query searches the MarkdownView; @EDIT: it highlights in the EditText',
    'S_DIARY_BROWSE': 'Diary, MarkdownView navigated away from the entry by a link (entry == false): Up arrow shown, Back goes back in the WebView history',
    'S_DIARY_PLAIN': 'Diary with Use markdown off: EditText only, no Accept/Edit buttons; Cancel appears after typing (entered through Settings)',
    'S_DLG_CALENDAR': 'CustomCalendarDialog (Use custom calendar on): month view with entry days marked, OK / Cancel. @GOTO from the menu, @SEND_* / @GEO for received media',
    'S_DLG_DATE_PICKER': 'Framework DatePickerDialog (Use custom calendar off), OK / Cancel',
    'S_DLG_SAVE_CHANGES': 'Alert "Save changes?" Save / Discard over Diary (Cancel item)',
    'S_DLG_BACKUP': 'Backup dialog: path EditText, Save / Cancel / Storage',
    'S_DLG_ADD_LINK': 'Add link dialog: title EditText, Add link / Cancel',
    'S_DLG_FIND_ALL': 'Find all result list (empty when nothing matches) with Cancel',
    'S_DLG_ERROR': 'Alert with an exception message and OK over Diary',
    'S_CHOOSER_SHARE': 'System share sheet for Share… @IMAGE (shown: PNG of the MarkdownView) / @TEXT (editing: the entry file)',
    'S_MEDIA_PICKER': 'System chooser + picker app for Add media… (GET_CONTENT */*); @PLAIN or @COPY (Copy images on)',
    'S_DOC_CREATE': 'DocumentsUI "save as" for Backup -> Storage (ACTION_CREATE_DOCUMENT application/zip)',
    'S_PRINT': 'System print preview (PrintManager.print)',
    'S_PERMISSION': 'Runtime permission dialog (GrantPermissionsActivity) over @DIARY or the Editor (@EDITOR_STYLES / @EDITOR_EXTERNAL)',
    'S_EDITOR': 'Editor activity (EditText, Accept ✓, Up arrow), no unsaved changes; @STYLES (Edit styles…/Edit script… for result) or @EXTERNAL (opened by another app)',
    'S_EDITOR_CHANGED': 'Editor after typing (Back asks Save / Discard); @STYLES / @EXTERNAL',
    'S_DLG_EDITOR_SAVE': 'Alert "Save changes?" Save / Discard in the Editor; @STYLES / @EXTERNAL',
    'S_SETTINGS': 'Settings activity + SettingsFragment (preferences.xml); Index page / Index template / Template page disabled until their checkbox is ticked. @<KEY>: right after that key changed',
    'S_DLG_FOLDER': 'EditTextPreference dialog "Folder"',
    'S_DLG_INDEX_TEMPLATE': 'EditTextPreference dialog "Index template" (only with Use index ticked)',
    'S_DLG_DATE_PREF': 'DatePickerPreference dialog; @INDEX (Index page) or @TEMPLATE (Template page)',
    'S_DLG_THEME': 'ListPreference dialog Theme: Light / Dark / System',
    'S_DLG_ABOUT': 'About dialog (AboutPreference, layout about.xml) with OK',
    'S_HOME_WIDGET': 'Home screen with a Diary widget (header date, ◀ / ▶ / ⌄ today icons, entry text; layout widget.xml)',
}

SCOPE = ('Search scope: all 11 app source files (text search for the symbol), the invoke/invokedynamic scan of every '
         'compiled app class (.plan/app_callers.txt, 23 classes), res/ XML (no android:onClick; the only app class '
         'names are AboutPreference/DatePickerPreference in preferences.xml), AndroidManifest.xml, and reflection or '
         'string dispatch (no forName/getMethod/getDeclared*/newInstance/getIdentifier/addJavascriptInterface in the '
         'app); the 3 JacocoInstrument classes reference no app class.')

DEAD = {
    'Diary.getEntries()': 'No call site: the only occurrences are its declaration and its own body (Diary.java:2152-2156). ' + SCOPE,
    'Diary.getEntries(Calendar)': 'Only call site is Diary.java:2155, inside the dead Diary.getEntries(). ' + SCOPE,
    'DiaryWidgetProvider.getFile()': 'No call site (declaration DiaryWidgetProvider.java:265-269; getText calls getFile(Calendar) at 193). ' + SCOPE,
    'FileUtils.<init>': ('Private constructor (FileUtils.java:102-104) and no "new FileUtils" anywhere; every FileUtils member '
                         'is static. JaCoCo does not report it (filtered trivial constructor). ' + SCOPE),
    'FileUtils.copyFile(Context,Uri,Uri)': ('No call site (declaration FileUtils.java:651-655); Diary.addMedia(Uri,boolean) calls '
                                            'copyFile(File,File) at Diary.java:2783. ' + SCOPE),
    'FileUtils.createGetContentIntent': ('No call site (FileUtils.java:814-822); Diary.addMedia() builds its own GET_CONTENT intent '
                                         '(Diary.java:1880-1885). ' + SCOPE),
    'FileUtils.getPathWithoutFilename': 'No call site (FileUtils.java:184-209). ' + SCOPE,
    'FileUtils.getReadableFileSize': 'No call site (FileUtils.java:691-718). ' + SCOPE,
    'FileUtils.getSize': 'No call site (FileUtils.java:394-420). ' + SCOPE,
    'FileUtils.getThumbnail(Context,Uri)': ('No call site (FileUtils.java:744-747); the getThumbnail calls at FileUtils.java:784 and '
                                            '792 are MediaStore.*.Thumbnails.getThumbnail. ' + SCOPE),
    'FileUtils.getThumbnail(Context,File)': 'No call site (FileUtils.java:730-733). ' + SCOPE,
    'FileUtils.getThumbnail(Context,Uri,String)': ('Only call sites are FileUtils.java:732 and 746, inside the two dead getThumbnail '
                                                   'overloads. ' + SCOPE),
    'FileUtils.getUri': 'Only call site is FileUtils.java:732, inside the dead getThumbnail(Context,File). ' + SCOPE,
    'FileUtils.isMediaUri': 'Only call site is FileUtils.java:765, inside the dead getThumbnail(Context,Uri,String). ' + SCOPE,
    'FileUtils.lambda$static$0': ('Body of the comparator stored in the static field sComparator (FileUtils.java:65-70): <clinit> '
                                  'only creates the function object (invokedynamic, no call), and sComparator is never read '
                                  '(text search finds only its declaration), so compare never runs. ' + SCOPE),
    'FileUtils.lambda$static$1': ('Body of the FileFilter stored in sFileFilter (FileUtils.java:84-89): created in <clinit>, the '
                                  'field is never read (only its declaration matches), so accept never runs. ' + SCOPE),
    'FileUtils.lambda$static$2': ('Body of the FileFilter stored in sDirFilter (FileUtils.java:95-100): created in <clinit>, the '
                                  'field is never read (only its declaration matches), so accept never runs. ' + SCOPE),
}

FRAMEWORK_ONLY = {
    'DatePickerPreference.onGetDefaultValue': (
        'Framework callback whose only call site in the framework files searched is Preference.java:292-294 (the '
        'constructor, only for an android:defaultValue attribute; FW-SRC core/java/android/preference/Preference.java; '
        'TwoStatePreference/EditTextPreference/ListPreference.java only override it). Neither DatePickerPreference '
        'element (preferences.xml:92-97, 121-126) has android:defaultValue, and no app code calls it (text search '
        'finds only its declaration, DatePickerPreference.java:72). Framework scope: the downloaded android-8.1.0_r1 '
        'preference/*.java files (Preference, DialogPreference, PreferenceFragment, PreferenceScreen, TwoStatePreference, '
        'EditTextPreference, ListPreference). App code: ' + SCOPE),
    'FileProvider.insert': (
        'ContentProvider callback reached only through ContentProvider.Transport.insert after enforceWritePermission '
        '(FW-SRC core/java/android/content/ContentProvider.java:254-266). The provider is not exported '
        '(AndroidManifest.xml:119-123), Diary grants only READ when sharing (FW-SRC Intent.java:9998-10012), and the '
        'app never inserts into its own authority: the only ContentResolver writes in the 11 sources are '
        'QueryHandler.startInsert on Calendar URIs (QueryHandler.java:143, 182). It would throw anyway (FileProvider.java:497). '
        'App code: ' + SCOPE + ' Framework scope: ContentProvider.java and Intent.java of android-8.1.0_r1.'),
    'FileProvider.update': (
        'ContentProvider callback reached only through ContentProvider.Transport.update after enforceWritePermission '
        '(FW-SRC ContentProvider.java:348-357). Not exported, read-only grants (Intent.java:9998-10012), no update call '
        'anywhere in the 11 sources (text search for ".update(" / startUpdate finds none). It would throw anyway '
        '(FileProvider.java:506). App code: ' + SCOPE + ' Framework scope: ContentProvider.java and Intent.java of android-8.1.0_r1.'),
    'FileProvider.delete': (
        'ContentProvider callback reached only through ContentProvider.Transport.delete after enforceWritePermission '
        '(FW-SRC ContentProvider.java:333-341). Not exported, read-only grants (Intent.java:9998-10012); the only '
        '".delete(" calls in the 11 sources are File.delete (Diary.java:2293, 2297, 2301; FileProvider.java:524 inside '
        'this method) and there is no startDelete, so nothing deletes through a content URI. App code: ' + SCOPE +
        ' Framework scope: ContentProvider.java and Intent.java of android-8.1.0_r1.'),
}

NOTES = {
    'Diary.cancel': ('else branch load() (Diary.java:1227-1228) is unreachable from the menu: Cancel is visible only while '
                     'changed (632) and every place that clears changed also rebuilds the menu'),
    'Diary.onOptionsItemSelected': ('Contexts: @VIEW, @VIEW_CHANGED, @EDIT, @EDIT_CHANGED, @PLAIN, @SEARCH, @BROWSE, @INDEX, '
                                    '@NOCUSTOM, @COPY. R.id.search falls to default (super), then the SearchView '
                                    'expands; the collapse at 722-724 skips Find all'),
    'Diary.addMap': 'else branch after if (true) (Diary.java:2882-2886) is dead code',
    'Diary.mediaCheck(CharSequence)': 'non-geo "type == null" branch and the image branch do nothing (Diary.java:1426-1433)',
    'Diary.onResume': ('Hazard candidate: on the first start the help text sets changed (2387), so onPause saves it as '
                       "today's entry (598-600). S_DIARY_PLAIN is entered through Settings (Use markdown unticked) or, "
                       'on a later start, by a needs_state edge'),
    'Diary.eventCheck': ('Hazard candidate: "@ 10:30 Dentist" (help.md:220) parses only when the SHORT time format is '
                         '24-hour (ENV_24H); in en-US the line is skipped silently and no event is added'),
    'QueryHandler.insertEvent': 'Needs ENV_24H (see Diary.eventCheck)',
    'DatePickerPreference.onSetInitialValue': ('Runs only when Index page or Template page was set with OK on an earlier '
                                               'Settings visit (key persisted), hence REACHABLE_AFTER_SETUP. The '
                                               'restorePersistedValue == false branch (87-91) is unreachable: without '
                                               'android:defaultValue dispatchSetInitialValue never passes false '
                                               '(Preference.java:1555-1557)'),
    'SettingsFragment.onPreferenceTreeClick': 'PreferenceScreen branch (133-138) is unreachable: preferences.xml has no nested PreferenceScreen',
    'Settings.onOptionsItemSelected': 'return false (116) is unreachable: no menu items besides Up',
    'Editor.onOptionsItemSelected': 'super branch (236-238) is unreachable: no menu items besides Up',
    'QueryHandler.onInsertComplete': 'EVENT_DONE case does nothing (185-186); EVENT_REMIND adds a 10-minute reminder',
    'QueryHandler.onQueryComplete': 'Hazard candidate: the cursor is never closed (leak); empty or null cursor returns at once (124-125)',
    'DiaryWidgetProvider.onUpdate': 'Line 164 sets the data of intent instead of today (typo); no visible effect',
    'Diary$GestureListener.onFling': ('Returns at once unless a touch with 2+ pointers came first (multi, Diary.java:842-843, '
                                      '3440-3441); multi is reset after each fling (3484). @MULTI is the swipe case'),
    'Diary.addMedia(Intent)': ('Hazard candidate: SEND of image/audio/video without EXTRA_STREAM dereferences media at 1615 '
                               'before the null check at 1618 (NullPointerException); SEND_MULTIPLE without a list NPE at 1643'),
    'Diary.share': ('Hazard candidate (INFERRED): shown == true while the MarkdownView was never laid out (Use markdown off '
                    'from the start) makes getDrawingCache() null -> Bitmap.createBitmap(null) at 1817'),
    'Editor.write': ('Hazard candidate: without storage permission Accept/Save request it and finish at once '
                     '(Editor.java:197-198, 261-262), so the text is not written; file == null (unmapped content URI) '
                     'also drops the text silently (411)'),
    'Editor.onCreate': ('Hazard candidate: a content URI that FileUtils.getPath cannot map keeps file == null; Accept/Save '
                        'then drop the edits silently and still return RESULT_OK (125-126, 411)'),
    'FileUtils.getPath': ('Hazard candidate: an ExternalStorageProvider document id without ":" would throw '
                          'ArrayIndexOutOfBounds at split[1] (502)'),
    'Diary.onDateSet(CustomCalendarView,int,int,int)': ('Hazard candidate: haveMedia stays true when the date dialog for '
                                                        'received media is cancelled; the next Go to date + OK inserts '
                                                        'the media again (823-824, 1655)'),
    'Diary.onDateSet(DatePicker,int,int,int)': 'Same haveMedia hazard as the custom calendar overload (823-824)',
    'DiaryWidgetUpdate.onCreate': ('Hazard candidate 11 (ActivityStarter read, the affinity match INFERRED): the NoDisplay '
                                   'activity started with NEW_TASK from the widget joins an existing Diary task, so ◀/▶ '
                                   'while Diary is in the background may bring Diary to the front'),
    'Diary.today': 'template() runs here only with Use template on and Use markdown off (2620-2621)',
    'Diary.template': ('Returns at once unless the shown entry is empty (2696-2697); a later Settings visit is needed for '
                       'Use template (Edit tap on S_DIARY_VIEW@TEMPLATE)'),
    'Diary.onBackPressed': ('Contexts: base (entry pages), @CHANGED, @EDIT, @EDIT_CHANGED, @BROWSE (WebView history), '
                            '@SEARCH_VIEW/@SEARCH_EDIT (super collapses the SearchView first, Activity.java:3001-3004)'),
    'Diary.alertDialog(int,String,int)': ('The shortest path shown needs ENV_IO_ERROR (a failed save) although this column does '
                                          'not say so (see TOOL_ISSUES.md); without it: Backup… -> a path in a missing folder '
                                          '-> Save (Diary$ZipTask.lambda$doInBackground$0), 13 steps'),
    'Diary$ZipTask.lambda$doInBackground$0': ('The shortest path shown (plain Save) needs ENV_IO_ERROR although this column '
                                              'does not say so (TOOL_ISSUES.md); without it: Backup… -> replace the path with '
                                              'one in a missing folder (e.g. nofolder/backup.zip) -> Save (@BADPATH), same length'),
    'FileUtils.getPathWithoutExtension': ('Needs an image with the same name already copied into the month folder: with Copy '
                                          'images on, add the same image twice (rename loop Diary.java:2771-2779)'),
    'Diary.changeDate(Calendar)': ('Contexts: @START (inside onCreate), base (MarkdownView shown), @EDIT (EditText shown: '
                                   'animateAccept switches back)'),
}

# ---------------------------------------------------------------- helpers
def at(node, ctx):
    return node + '@' + ctx if ctx else node


def menu_rebuild(src, guard=None, line=None, ns=None, env=None):
    """invalidateOptionsMenu() -> onCreateOptionsMenu + onPrepareOptionsMenu (FRAMEWORK)."""
    ev = F_INVALIDATE + ('; SRC Diary.java:' + line if line else '')
    e(src, 'Diary.onCreateOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu(): the menu is rebuilt on the next frame (main.xml inflated)',
      guard=guard, needs_state=ns, env=env, evidence=ev)
    e(src, 'Diary.onPrepareOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu(): the rebuilt menu is prepared (Cancel/Previous/Next/Today/Index state)',
      guard=guard, needs_state=ns, env=env, evidence=ev)


def watchers(src, how, line, guard=None, ctx=None, env=None, ev=F_EDITABLE, needs_state=None):
    """An edit of the EditText notifies Diary's TextWatcher (anonymous Diary$2)."""
    for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
        e(src, at('Diary$2.' + cb, ctx), 'FRAMEWORK', how + ' notifies the TextWatcher (%s)' % cb, guard=guard, env=env,
          needs_state=needs_state, evidence=ev + '; SRC Diary.java:' + line)


def changed_pages(src, trig, line, guard=None, env=None):
    """Text inserted by a handler: the user is left on a _CHANGED page (README approximation 4.6)."""
    g = (guard + ' and ') if guard else ''
    e(src, 'S_DIARY_VIEW_CHANGED', 'ENTERS', trig + '; MarkdownView shown, Cancel visible', guard=g + 'shown (markdown on)', env=env,
      evidence='SRC Diary.java:' + line + ', 1084-1085 (watcher sets changed)')
    e(src, 'S_DIARY_EDIT_CHANGED', 'ENTERS', trig + '; EditText shown, Cancel visible', guard=g + 'not shown (editing)', env=env,
      evidence='SRC Diary.java:' + line + ', 1084-1085 (watcher sets changed)')


# ---------------------------------------------------------------- process start: vendored FileProvider (app code)
START_GUI = ['Start Diary in any way (launcher icon, home-screen widget, Share to Diary, open a text file with Diary)']
e('S_ENTRY', 'FileProvider.<clinit>', 'ENTRY', 'Any start of the app process: the provider class is loaded when the process installs its manifest providers',
  gui=START_GUI, evidence=F_PROVIDER_START + '; SRC FileProvider.java:325-344 (static COLUMNS, DEVICE_ROOT, sCache)')
e('S_ENTRY', 'FileProvider.<init>', 'ENTRY', 'Any start of the app process: ActivityThread instantiates the non-exported FileProvider before any activity or receiver runs',
  gui=START_GUI, evidence=F_PROVIDER_START + '; SRC AndroidManifest.xml:119-127',
  note='Runs once per process; launcher, widget broadcast, share target and Editor starts all create the process')
e('FileProvider.<init>', 'FileProvider.attachInfo', 'LIFECYCLE', 'localProvider.attachInfo(context, info)', evidence=F_PROVIDER_START)
e('FileProvider.attachInfo', 'FileProvider.onCreate', 'FRAMEWORK', 'super.attachInfo -> ContentProvider.attachInfo calls onCreate() (returns true)',
  evidence=F_PROVIDER_ONCREATE + '; SRC FileProvider.java:353-355, 366')
e('FileProvider.attachInfo', 'FileProvider.getPathStrategy', 'CALL', 'mStrategy = getPathStrategy(context, info.authority) after the export/grant sanity checks',
  writes=['field:FileProvider.mStrategy'], evidence='SRC FileProvider.java:369-376')
e('FileProvider.getPathStrategy', 'FileProvider.parsePathStrategy', 'CALL', 'sCache miss: parse the FILE_PROVIDER_PATHS meta-data',
  guard='authority not yet in the static sCache (first call in this process)', reads=['static:FileProvider.sCache', 'res:xml/filepaths.xml'],
  writes=['static:FileProvider.sCache'], evidence='SRC FileProvider.java:556-568')
e('FileProvider.parsePathStrategy', 'FileProvider$SimplePathStrategy.<init>', 'CALL', 'strat = new SimplePathStrategy(authority)', evidence='SRC FileProvider.java:582')
e('FileProvider.parsePathStrategy', 'FileProvider.buildPath', 'CALL', 'buildPath(target, path) for each root of filepaths.xml (external-path, cache-path, root-path)',
  evidence='SRC FileProvider.java:594-617; res/xml/filepaths.xml:3-5')
e('FileProvider.parsePathStrategy', 'FileProvider$SimplePathStrategy.addRoot', 'CALL', 'strat.addRoot(name, buildPath(...)) for each of the 3 roots',
  evidence='SRC FileProvider.java:616-617')

# ---------------------------------------------------------------- Diary: entries and onCreate per launch context
LAUNCH_GUI = ['Home screen: tap the Diary icon']
e('S_ENTRY', 'Diary.<clinit>', 'ENTRY', 'First use of class Diary in a new process: the static Pattern constants are compiled',
  gui=LAUNCH_GUI, evidence='SRC Diary.java:157-179', note='A widget-only process initialises it through Diary.read / Diary.listDays (CALL edges from the widget code)')
e('S_ENTRY', 'Diary.<init>', 'ENTRY', 'Tap the Diary icon in the launcher (MAIN/LAUNCHER intent filter)', gui=LAUNCH_GUI,
  evidence='SRC AndroidManifest.xml:52-59',
  note='Other entries: Share to Diary (SEND / SEND_MULTIPLE), geo: links, the home-screen widget body; text files open in Editor')
OUTSIDE = 'Happens in another app: tools confined to the Diary package (APE, Monkey -p) cannot do it'
RECV_CTX = ('SEND_TEXT', 'SEND_IMAGE', 'SEND_MULTI', 'GEO', 'SELF_TEXT', 'SELF_IMAGE')   # SELF_*: Share… -> Diary itself
ENTRY_CTX = {
    'SEND_TEXT': ('Another app shares text/plain to Diary: text, a link, or a text file in EXTRA_STREAM',
                  ['In another app share text, a link or a .txt file (e.g. Files -> Download/todo.txt -> Share), then pick Diary'],
                  'SRC AndroidManifest.xml:60-67 (SEND text/plain)'),
    'SEND_IMAGE': ('Another app shares one image, audio or video file to Diary (SEND with EXTRA_STREAM)',
                   ['In Files or Gallery share an image (or an audio/video file), then pick Diary'],
                   'SRC AndroidManifest.xml:60-74 (SEND audio/* video/* and image/*)'),
    'SEND_MULTI': ('Another app shares several images to Diary (SEND_MULTIPLE image/*)',
                   ['In Files select several images, tap Share, then pick Diary'], 'SRC AndroidManifest.xml:68-74 (SEND_MULTIPLE image/*)'),
    'GEO': ('Another app opens a geo: URI with Diary (VIEW geo, BROWSABLE)',
            ['Open a geo: link (e.g. geo:51.5,-0.12 on a web page or from a maps app) and pick Diary'], 'SRC AndroidManifest.xml:75-82 (VIEW geo)'),
}
for ctx, (trig, gui, ev) in ENTRY_CTX.items():
    e('S_ENTRY', 'Diary.<init>@' + ctx, 'ENTRY', trig, gui=gui, evidence=ev, note=OUTSIDE)

for ctx in ('', 'WIDGET', 'RECREATE') + RECV_CTX:
    ini, oc = at('Diary.<init>', ctx), at('Diary.onCreate', ctx)
    e(ini, oc, 'LIFECYCLE', 'The system instantiates Diary, then onCreate' + (' with the saved instance state' if ctx == 'RECREATE' else ''),
      evidence='SRC Diary.java:441-443')
    if ctx == 'RECREATE':
        e(oc, 'Diary.onRestoreInstanceState', 'LIFECYCLE', 'Recreated with saved state: onStart, then onRestoreInstanceState (the intent branch 497-516 is skipped)',
          guard='savedInstanceState != null', evidence=F_RESTORE + '; SRC Diary.java:497, 523-533')
    else:
        e(oc, 'Diary.onResume', 'LIFECYCLE', 'onStart -> onResume', evidence='SRC Diary.java:539-541')
    e(oc, 'Diary.getPreferences', 'CALL', 'getPreferences(): theme, calendar, markdown, selection, browser, index, template, copy media, folder',
      reads=PREF_READS, evidence='SRC Diary.java:444, 1259-1287')
    e(oc, 'Diary.setListeners', 'CALL', 'setListeners() after setContentView(main.xml)', evidence='SRC Diary.java:473-490')
    e(oc, 'Diary$GestureListener.<init>', 'CALL', 'gestureDetector = new GestureDetector(this, new GestureListener())', evidence='SRC Diary.java:492-493')
    e(oc, 'Diary.onCreateOptionsMenu', 'FRAMEWORK', 'setContentView installs the window decor, which posts the first menu build; it runs on the next frame (after onResume) and inflates menu/main.xml',
      evidence=F_MENU_FIRST + '; SRC Diary.java:473, 612-615')
    e(oc, 'Diary.onPrepareOptionsMenu', 'FRAMEWORK', 'The first menu build prepares the menu right after creating it',
      evidence=F_MENU_FIRST + '; SRC Diary.java:622-654')

# @START: the date is set inside onCreate of a new instance, where changed == false and shown == true, so
# changeDate neither saves nor switches views (the menu handlers use the base nodes)
e('Diary.onCreate', 'Diary.today@START', 'CALL', 'Started from the launcher (no widget extra): today()', guard='savedInstanceState == null and not (useIndex and ACTION_MAIN)',
  evidence='SRC Diary.java:497-512')
e('Diary.onCreate', 'Diary.index@START', 'CALL', 'Use index on and started from the launcher: index() opens the index page', guard='savedInstanceState == null and useIndex and ACTION_MAIN',
  reads=['pref:pref_use_index', 'pref:pref_index_page'], needs_state=NS_INDEX, evidence='SRC Diary.java:502-504')
e('Diary.onCreate', 'Diary.mediaCheck(Intent)', 'CALL', 'mediaCheck(getIntent()): MAIN is not SEND/VIEW, so nothing happens', guard='savedInstanceState == null',
  evidence='SRC Diary.java:515, 1293-1300')
e('Diary.onCreate@WIDGET', 'Diary.changeDate(long)', 'CALL', 'Started from the widget body: changeDate(intent ENTRY extra = the widget date)',
  guard='savedInstanceState == null and intent has org.billthefarmer.diary.ENTRY', reads=['intent:org.billthefarmer.diary.ENTRY'],
  evidence='SRC Diary.java:506-509; DiaryWidgetProvider.java:129-141')
e('Diary.onCreate@WIDGET', 'Diary.mediaCheck(Intent)', 'CALL', 'mediaCheck(intent): the widget intent has no action, nothing happens', evidence='SRC Diary.java:515')
e('Diary.changeDate(long)', 'Diary.changeDate(Calendar)@START', 'CALL', 'Midnight GregorianCalendar of the given time -> changeDate(date)', evidence='SRC Diary.java:2587-2593')
e('Diary.today@START', 'Diary.changeDate(Calendar)@START', 'CALL', "entryStack.clear(); changeDate(today's date)", evidence='SRC Diary.java:2610-2617')
e('Diary.today@START', 'Diary.template', 'CALL', 'useTemplate and not markdown: template() for the empty new entry', guard='pref_use_template on and pref_markdown off',
  needs_state=NS_TEMPLATE_PLAIN, evidence='SRC Diary.java:2619-2621')
e('Diary.index@START', 'Diary.changeDate(Calendar)@START', 'CALL', 'entryStack.clear(); changeDate(index page date)', reads=['pref:pref_index_page'], evidence='SRC Diary.java:2625-2631')
e('Diary.changeDate(Calendar)@START', 'Diary.setDate', 'CALL', 'setDate(date) (no save: changed is false in a new instance)', evidence='SRC Diary.java:2565-2572')
e('Diary.changeDate(Calendar)@START', 'Diary.load', 'CALL', 'load() the entry of the start date; shown is already true', evidence='SRC Diary.java:2573-2581')
for ctx in RECV_CTX:
    e('Diary.onCreate@' + ctx, 'Diary.today@START', 'CALL', 'No widget extra: today() first', guard='savedInstanceState == null', evidence='SRC Diary.java:510-512')
    e('Diary.onCreate@' + ctx, 'Diary.mediaCheck(Intent)@' + ctx, 'CALL', 'mediaCheck(intent) for the received intent', guard='savedInstanceState == null',
      evidence='SRC Diary.java:515')
    e('Diary.mediaCheck(Intent)@' + ctx, 'Diary.goToDate@' + ctx, 'CALL', 'SEND / SEND_MULTIPLE / VIEW: haveMedia = true; goToDate(currEntry) asks where to put it',
      writes=['field:Diary.haveMedia'], evidence='SRC Diary.java:1293-1300')
# ---------------------------------------------------------------- Diary.setListeners: registrations (round B)
e('Diary.setListeners', 'Diary$1.<init>', 'CALL', 'markdownView.setWebViewClient(new WebViewClient() {...})', evidence='SRC Diary.java:852-855')
for cb, ln in (('onPageFinished', '861-890'), ('shouldOverrideUrlLoading', '896-924')):
    e('Diary.setListeners', 'Diary$1.' + cb, 'REGISTER', 'WebViewClient of the MarkdownView (%s)' % cb, evidence='SRC Diary.java:854, ' + ln)
REG = (('Diary.lambda$setListeners$4', 'showEdit = () -> fade the Edit button in (posted by the MarkdownView scroll listener)', '928-935'),
       ('Diary.lambda$setListeners$5', 'markdownView.setOnScrollChangeListener (API >= 23; the baseline ran API 27)', '928, 938-974'),
       ('Diary.lambda$setListeners$6', 'markdownView.setOnLongClickListener', '978-985'),
       ('Diary.lambda$setListeners$7', 'accept.setOnClickListener (✓ button)', '992-1017'),
       ('Diary.lambda$setListeners$8', 'accept.setOnLongClickListener', '1020-1026'),
       ('Diary.lambda$setListeners$10', 'edit.setOnClickListener (pencil button)', '1033-1062'),
       ('Diary.lambda$setListeners$11', 'edit.setOnLongClickListener', '1065-1071'),
       ('Diary.lambda$setListeners$12', 'textView.setOnFocusChangeListener', '1104-1111'),
       ('Diary.lambda$setListeners$13', 'textView.setOnClickListener (task-list box toggle)', '1114-1142'),
       ('Diary.lambda$setListeners$14', 'textView.setOnLongClickListener', '1145-1152'),
       ('Diary.lambda$setListeners$15', 'showAccept = () -> fade the Accept button in (posted by the editor scroll listener)', '1157-1163'),
       ('Diary.lambda$setListeners$16', 'scrollView.setOnScrollChangeListener (API >= 23)', '1157, 1166-1203'))
for dst, trig, ln in REG:
    e('Diary.setListeners', dst, 'REGISTER', trig, evidence='SRC Diary.java:' + ln)
e('Diary.setListeners', 'Diary$2.<init>', 'CALL', 'textView.addTextChangedListener(new TextWatcher() {...})', evidence='SRC Diary.java:1077-1078')
for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
    e('Diary.setListeners', 'Diary$2.' + cb, 'REGISTER', 'TextWatcher of the EditText (%s)' % cb, evidence='SRC Diary.java:1077-1101')

# ---------------------------------------------------------------- Diary lifecycle: resume, pause, state, back (round D)
e('Diary.onRestoreInstanceState', 'Diary.setDate', 'CALL', 'setDate(saved year/month/day); shown, entry, saved restored',
  reads=['bundle:year', 'bundle:month', 'bundle:day', 'bundle:shown', 'bundle:entry', 'bundle:saved'], evidence='SRC Diary.java:523-533')
e('Diary.onRestoreInstanceState', 'Diary.onResume', 'LIFECYCLE', 'onPostCreate -> onResume', evidence=F_RESTORE + '; SRC Diary.java:539')
e('Diary.onResume', 'Diary.getPreferences', 'CALL', 'getPreferences() again (Settings may have changed them)', reads=PREF_READS, evidence='SRC Diary.java:542-544')
e('Diary.onResume', 'Diary.<init>@RECREATE', 'SYSTEM', 'recreate(): pref_theme differs from the theme this instance started with',
  guard='theme changed and SDK != 23', reads=['pref:pref_theme'], needs_state=NS_THEME, evidence=F_RELAUNCH + '; SRC Diary.java:546-548')
e('Diary.onResume', 'Diary.setDate', 'CALL', 'setDate(currEntry)', evidence='SRC Diary.java:551')
e('Diary.onResume', 'Diary.getFile()', 'CALL', 'getFile().lastModified() compared with saved', evidence='SRC Diary.java:554')
e('Diary.onResume', 'Diary.load', 'CALL', 'Reload: the entry file changed on disk since onPause (or exists and saved == 0 on the first resume)',
  guard='getFile().lastModified() > saved', reads=['file:<folder>/YYYY/MM/DD.(txt|md)', 'field:Diary.saved'], evidence='SRC Diary.java:553-555')
HELP_GUARD = 'storage permission granted, no entry before or after the shown date and an empty text (first start)'
e('Diary.onResume', 'Diary.readAssetFile', 'CALL', 'Copy the help text to the empty page: textView.setText(readAssetFile("help.md")) (sets changed)',
  guard=HELP_GUARD, reads=['res:assets/help.md'], writes=['field:Diary.changed'], env=ENV_PERM, evidence='SRC Diary.java:560-565, 2376-2394')
watchers('Diary.onResume', 'textView.setText(help text)', '565', guard=HELP_GUARD, env=ENV_PERM, ev=F_SETTEXT)
e('Diary.onResume', 'Diary.loadMarkdown()', 'CALL', 'markdown && changed: render the (help) text', guard='markdown on and changed', evidence='SRC Diary.java:567-568')
e('Diary.onResume', 'Diary.setVisibility', 'CALL', 'setVisibility(): markdown/editor switchers by shown and pref_markdown', evidence='SRC Diary.java:570')
e('Diary.onResume', 'S_DIARY_VIEW', 'ENTERS', 'Diary visible with the MarkdownView', guard='markdown on and shown (the default)', evidence='SRC Diary.java:570, 1696-1709')
e('Diary.onResume', 'S_DIARY_VIEW_CHANGED', 'ENTERS', 'First start: the help text was copied into the empty page (changed = true, Cancel visible)',
  guard=HELP_GUARD, env=ENV_PERM, evidence='SRC Diary.java:560-570, 2387')
e('Diary.onResume', 'S_DIARY_EDIT', 'ENTERS', 'Back in edit mode: the EditText and Accept button are shown again', guard='markdown on and not shown',
  needs_state=NS_EDITMODE, evidence='SRC Diary.java:1704-1708')
e('Diary.onResume', 'S_DIARY_PLAIN', 'ENTERS', 'Use markdown is off: EditText only, buttons gone', guard='pref_markdown off', needs_state=NS_PLAIN,
  evidence='SRC Diary.java:1712-1717')
for pg, ns in (('S_DIARY_VIEW@INDEX', NS_INDEX_PAGE), ('S_DIARY_VIEW@NOCUSTOM', NS_CUSTOM_OFF), ('S_DIARY_VIEW@TEMPLATE', NS_TEMPLATE),
               ('S_DIARY_VIEW@COPY', NS_COPY)):
    e('Diary.onResume', pg, 'ENTERS', 'Diary visible with a preference that an earlier Settings visit changed', needs_state=ns,
      evidence='SRC Diary.java:1259-1287 (preferences read on every resume)')

DIARY_PAGES = ('S_DIARY_VIEW', 'S_DIARY_VIEW_CHANGED', 'S_DIARY_EDIT', 'S_DIARY_EDIT_CHANGED', 'S_DIARY_PLAIN',
               'S_DIARY_SEARCH@VIEW', 'S_DIARY_SEARCH@EDIT', 'S_DIARY_BROWSE')
CHANGED_PAGES = ('S_DIARY_VIEW_CHANGED', 'S_DIARY_EDIT_CHANGED', 'S_DIARY_PLAIN')   # pages where changed can be true
PAUSE_GUI = ['Press Home / recents / screen off', 'or open Settings, Editor, a picker, the share sheet, print', 'or Back on the root page', 'or rotate the screen']
for pg in DIARY_PAGES:
    e(pg, 'Diary.onPause@CHANGED' if pg in CHANGED_PAGES else 'Diary.onPause', 'SYSTEM',
      'Diary loses the foreground' + (' with unsaved changes' if pg in CHANGED_PAGES else ''), gui=PAUSE_GUI,
      guard='changed' if pg == 'S_DIARY_PLAIN' else None, evidence='SRC Diary.java:596-606')
    e(pg, 'Diary.onSaveInstanceState', 'SYSTEM', 'Home or another activity on top: state saved before onStop (not on Back, not under a dialog)',
      gui=['Press Home (or open Settings / Editor / a picker)'], evidence=F_SAVESTATE + '; SRC Diary.java:577-590')
    e(pg, 'Diary.onSaveInstanceState@ROTATE', 'SYSTEM', 'Rotation: state saved before the activity is destroyed and recreated',
      gui=['Rotate the screen'], guard='orientation change (no android:configChanges)', evidence=F_RELAUNCH + '; SRC Diary.java:577-590')
for op in ('Diary.onPause', 'Diary.onPause@CHANGED'):
    if op.endswith('CHANGED'):
        e(op, 'Diary.save()', 'CALL', 'Unsaved changes are saved when Diary leaves the foreground', guard='changed', writes=['field:Diary.changed'],
          evidence='SRC Diary.java:598-603')
    e(op, 'Diary.getFile()', 'CALL', 'saved = getFile().lastModified()', writes=['field:Diary.saved'], evidence='SRC Diary.java:605')
    e(op, 'S_DIARY_PAUSED', 'ENTERS', 'Diary is in the background or under another activity', guard='not finishing', evidence='SRC Diary.java:596')
    e(op, 'S_EXIT', 'ENTERS', 'Back on the root page finished Diary', guard='finishing (Back with an empty entry stack)', evidence=F_BACK + '; SRC Diary.java:740, 755')
e('S_DIARY_PAUSED', 'Diary.onResume', 'SYSTEM', 'Diary returns to the foreground',
  gui=['Return via recents or the launcher icon', 'or close the page on top (Back / Up / finish)'], guard='process and activity still alive',
  evidence='SRC Diary.java:539')
e('Diary.onSaveInstanceState@ROTATE', 'Diary.<init>@RECREATE', 'SYSTEM', 'Rotation destroys Diary and creates a new instance with the saved state',
  guard='orientation change', writes=['bundle:year', 'bundle:month', 'bundle:day', 'bundle:shown', 'bundle:entry', 'bundle:saved'],
  evidence=F_RELAUNCH + '; SRC AndroidManifest.xml:52-55, Diary.java:577-590')
e('S_EXIT', 'S_ENTRY', 'SYSTEM', 'Next start; if the process survived, static state (QueryHandler, FileProvider.sCache, loaded classes) is kept',
  gui=['Start Diary again (launcher icon, widget, share)'], evidence='INFERRED Back finishes the root activity but the process may stay alive after the last activity finishes (process lifetime is not in the sources read)')

# Back key per page context
BACK_CTX = {'S_DIARY_VIEW': '', 'S_DIARY_VIEW_CHANGED': 'CHANGED', 'S_DIARY_PLAIN': 'CHANGED', 'S_DIARY_EDIT': 'EDIT', 'S_DIARY_EDIT_CHANGED': 'EDIT_CHANGED'}
for pg, ctx in BACK_CTX.items():
    e(pg, at('Diary.onBackPressed', ctx), 'SYSTEM', 'Back key on an entry page', gui=['Press Back'], evidence='SRC Diary.java:731-757')
for ctx in ('', 'CHANGED', 'EDIT', 'EDIT_CHANGED'):
    ob, op = at('Diary.onBackPressed', ctx), 'Diary.onPause@CHANGED' if 'CHANGED' in ctx else 'Diary.onPause'
    cd = 'Diary.changeDate(Calendar)@EDIT' if ctx.startswith('EDIT') else 'Diary.changeDate(Calendar)'
    e(ob, cd, 'CALL', 'entry and the entry stack is not empty: changeDate(entryStack.pop()) goes back to the previous entry' +
      (' (saving the changes first)' if 'CHANGED' in ctx else ''), guard='entry and entryStack not empty', evidence='SRC Diary.java:734-737, 2565-2570')
    e(ob, 'S_DIARY_VIEW', 'ENTERS', 'Previous entry shown', guard='entryStack not empty (markdown on)', evidence='SRC Diary.java:737, 2575-2581')
    e(ob, op, 'SYSTEM', 'Empty entry stack: super.onBackPressed() finishes Diary', guard='entryStack empty', evidence=F_BACK + '; SRC Diary.java:739-740')
e('S_DIARY_BROWSE', 'Diary.onBackPressed@BROWSE', 'SYSTEM', 'Back key while a linked page is shown', gui=['Press Back'], evidence='SRC Diary.java:743-756')
e('Diary.onBackPressed@BROWSE', 'Diary$1.onPageFinished', 'FRAMEWORK', 'markdownView.goBack(): the previous page finishes loading',
  guard='markdownView.canGoBack()', evidence='INFERRED the WebView engine (Chromium, native code outside the Java sources) reloads the previous history entry on goBack and calls onPageFinished; SRC Diary.java:746-748')
e('Diary.onBackPressed@BROWSE', 'Diary.changeDate(Calendar)', 'CALL', 'History now empty: changeDate(currEntry) re-renders the entry (entry = true)',
  guard='canGoBack() before and not after goBack()', evidence='SRC Diary.java:746-751')
e('Diary.onBackPressed@BROWSE', 'S_DIARY_VIEW', 'ENTERS', 'Back at the diary entry', guard='history empty after goBack()', evidence='SRC Diary.java:750-751')
e('Diary.onBackPressed@BROWSE', 'S_DIARY_BROWSE', 'ENTERS', 'An earlier linked page is shown', guard='more history left after goBack()', evidence='SRC Diary.java:746-748')
e('Diary.onBackPressed@BROWSE', 'Diary.onPause', 'SYSTEM', 'No WebView history: super.onBackPressed() finishes Diary', guard='not canGoBack()',
  evidence=F_BACK + '; SRC Diary.java:754-755')
for v, base_pg in (('VIEW', 'S_DIARY_VIEW'), ('EDIT', 'S_DIARY_EDIT')):
    bp = 'Diary.onBackPressed@SEARCH_' + v
    e('S_DIARY_SEARCH@' + v, bp, 'SYSTEM', 'Back key while the SearchView is expanded', gui=['Press Back (a first Back only closes the keyboard while the search field has focus)'],
      evidence=F_SEARCH_BACK + '; SRC Diary.java:731-740')
    e(bp, 'Diary.changeDate(Calendar)', 'CALL', 'Entry stack not empty: changeDate(entryStack.pop()); the SearchView stays expanded',
      guard='entry and entryStack not empty', evidence='SRC Diary.java:734-737')
    e(bp, 'S_DIARY_SEARCH@VIEW', 'ENTERS', 'Previous entry shown, still searching', guard='entryStack not empty', evidence='SRC Diary.java:737, 2575-2581')
    e(bp, base_pg, 'ENTERS', 'Empty stack: super.onBackPressed() collapses the expanded SearchView instead of finishing', guard='entryStack empty',
      evidence=F_BACK + ' + ' + F_SEARCH_COLLAPSE[len(FWS):] + '; SRC Diary.java:739-740')
    e(bp, 'Diary$QueryTextListener.onQueryTextChange', 'FRAMEWORK', 'Collapsing clears the query: onQueryTextChange("")', guard='entryStack empty and the query was not empty',
      evidence=F_SEARCH_COLLAPSE)

# ---------------------------------------------------------------- date navigation helpers (round A)
e('Diary.setDate', 'Diary.setTitleDate', 'CALL', 'setTitleDate(date.getTime())', evidence='SRC Diary.java:2507')
e('Diary.setDate', 'Diary.getPrevEntry', 'CALL', 'prevEntry = getPrevEntry(y, m, d) (today if the date is in the future)', writes=['field:Diary.prevEntry'],
  evidence='SRC Diary.java:2516-2519')
e('Diary.setDate', 'Diary.getNextEntry', 'CALL', 'nextEntry = getNextEntry(y, m, d) (today if the date is in the past)', writes=['field:Diary.currEntry', 'field:Diary.nextEntry'],
  evidence='SRC Diary.java:2520-2524')
menu_rebuild('Diary.setDate', line='2526')
for side, lines in (('Prev', ('2082-2092', '2068-2075', '2055-2062', '2042-2049')), ('Next', ('2138-2148', '2124-2131', '2111-2118', '2098-2105'))):
    lo = side.lower()
    e('Diary.get%sEntry' % side, 'Diary.%sDay' % lo, 'CALL', '%sDay(year, month, day): nearest day file in the month folder' % lo, evidence='SRC Diary.java:' + lines[0])
    e('Diary.get%sEntry' % side, 'Diary.%sMonth' % lo, 'CALL', 'No day found: %sMonth(year, month), then recursion into that month' % lo,
      guard='no %s day file in this month' % ('earlier' if side == 'Prev' else 'later'), evidence='SRC Diary.java:' + lines[0])
    e('Diary.get%sEntry' % side, 'Diary.%sYear' % lo, 'CALL', 'No month found: %sYear(year), then recursion into that year' % lo,
      guard='no %s month folder in this year' % ('earlier' if side == 'Prev' else 'later'), evidence='SRC Diary.java:' + lines[0])
    e('Diary.%sDay' % lo, 'Diary.getMonth', 'CALL', 'getMonth(year, month) folder', evidence='SRC Diary.java:' + lines[1])
    e('Diary.%sDay' % lo, 'Diary.listDays', 'CALL', 'listDays(monthDir)', evidence='SRC Diary.java:' + lines[1])
    e('Diary.%sDay' % lo, 'Diary.dayValue', 'CALL', 'dayValue(file) for each day file', guard='the month folder has day files', evidence='SRC Diary.java:' + lines[1])
    e('Diary.%sMonth' % lo, 'Diary.getYear', 'CALL', 'getYear(year) folder', evidence='SRC Diary.java:' + lines[2])
    e('Diary.%sMonth' % lo, 'Diary.listMonths', 'CALL', 'listMonths(yearDir)', evidence='SRC Diary.java:' + lines[2])
    e('Diary.%sMonth' % lo, 'Diary.monthValue', 'CALL', 'monthValue(dir) for each month folder', guard='the year folder has month folders', evidence='SRC Diary.java:' + lines[2])
    e('Diary.%sYear' % lo, 'Diary.getHome', 'CALL', 'getHome() diary folder', evidence='SRC Diary.java:' + lines[3])
    e('Diary.%sYear' % lo, 'Diary.listYears', 'CALL', 'listYears(home)', evidence='SRC Diary.java:' + lines[3])
    e('Diary.%sYear' % lo, 'Diary.yearValue', 'CALL', 'yearValue(dir) for each year folder', guard='the diary folder has year folders', evidence='SRC Diary.java:' + lines[3])
for lst, lam, ln in (('listYears', 'lambda$listYears$1', '312-315'), ('listMonths', 'lambda$listMonths$2', '320-323'), ('listDays', 'lambda$listDays$3', '328-331')):
    e('Diary.' + lst, 'Diary.sortFiles', 'CALL', 'sortFiles(dir.listFiles(filter))', evidence='SRC Diary.java:' + ln)
    e('Diary.' + lst, 'Diary.' + lam, 'FRAMEWORK', 'File.listFiles(FilenameFilter) calls the filter lambda for each directory entry',
      guard='the folder exists and is not empty', evidence=F_LISTFILES + '; SRC Diary.java:' + ln)
e('Diary.sortFiles', 'Diary.lambda$sortFiles$0', 'FRAMEWORK', 'Arrays.sort(files, comparator): reverse name order', guard='at least 2 files',
  evidence=F_SORT + '; SRC Diary.java:300-307')
e('Diary.getFile()', 'Diary.getFile(Calendar)', 'CALL', 'getFile(currEntry)', evidence='SRC Diary.java:2026-2028')
e('Diary.getFile(Calendar)', 'Diary.getDay', 'CALL', 'getDay(y, m, d)', evidence='SRC Diary.java:2032-2036')
e('Diary.getDay', 'Diary.getMonth', 'CALL', 'getMonth(y, m) then DD.txt (or DD.md when markdown and no .txt exists)', reads=['pref:pref_markdown'],
  evidence='SRC Diary.java:2008-2022')
e('Diary.getMonth', 'Diary.getYear', 'CALL', 'new File(getYear(y), MM)', evidence='SRC Diary.java:2000-2004')
e('Diary.getYear', 'Diary.getHome', 'CALL', 'new File(getHome(), YYYY)', evidence='SRC Diary.java:1992-1996')

# ---------------------------------------------------------------- changeDate, load, save, markdown rendering (round A)
# base: called from a page with the MarkdownView shown; @EDIT: called while the EditText is shown (here: Back from an
# edit page with a non-empty entry stack; menu, swipe and Go to date from edit pages run the same code)
for cd in ('Diary.changeDate(Calendar)', 'Diary.changeDate(Calendar)@EDIT'):
    e(cd, 'Diary.save()', 'CALL', 'Unsaved text is saved before moving to another date', guard='changed', evidence='SRC Diary.java:2565-2570')
    e(cd, 'Diary.setDate', 'CALL', 'setDate(date)', evidence='SRC Diary.java:2572')
    e(cd, 'Diary.load', 'CALL', 'load() the entry of the new date; entry = true', writes=['field:Diary.entry'], evidence='SRC Diary.java:2573, 2581')
e('Diary.changeDate(Calendar)@EDIT', 'Diary.animateAccept', 'CALL', 'markdown and not shown: switch back to the MarkdownView (shown = true)',
  guard='markdown on and not shown', writes=['field:Diary.shown'], evidence='SRC Diary.java:2575-2579')
e('Diary.load', 'S_PERMISSION@DIARY_READ', 'ENTERS', 'No READ_EXTERNAL_STORAGE: requestPermissions(..., REQUEST_READ) and return',
  guard='SDK >= 23 and storage permission not granted', env=ENV_NOPERM, evidence=F_PERMRESULT + '; SRC Diary.java:2400-2412')
e('Diary.load', 'Diary.getFile()', 'CALL', 'read(getFile())', evidence='SRC Diary.java:2415')
e('Diary.load', 'Diary.read', 'CALL', 'text = read(getFile()) (empty for a missing file)', reads=['file:<folder>/YYYY/MM/DD.(txt|md)'], evidence='SRC Diary.java:2415, 355-370')
watchers('Diary.load', 'textView.setText(text)', '2416 (changed is reset right after, 2417)', ev=F_SETTEXT)
menu_rebuild('Diary.load', line='2418')
e('Diary.load', 'Diary.loadMarkdown()', 'CALL', 'Render the entry', guard='markdown on', evidence='SRC Diary.java:2419-2420')
e('Diary.load', 'Diary.checkPosition', 'CALL', 'checkPosition(text): cursor from a [<] / [>] / [#] marker', evidence='SRC Diary.java:2422-2423')
e('Diary.checkPosition', 'Diary.lambda$checkPosition$20', 'ASYNC', 'textView.postDelayed(scroll to the cursor line, 128 ms)', evidence='SRC Diary.java:2465-2477')
e('Diary.loadMarkdown()', 'Diary.loadMarkdown(CharSequence)', 'CALL', 'loadMarkdown(textView.getText())', evidence='SRC Diary.java:1353-1357')
e('Diary.loadMarkdown(CharSequence)', 'Diary.getBaseUrl', 'CALL', 'base URL = month folder', evidence='SRC Diary.java:1362')
e('Diary.loadMarkdown(CharSequence)', 'Diary.markdownCheck', 'CALL', 'markdownCheck(text)', evidence='SRC Diary.java:1362')
e('Diary.loadMarkdown(CharSequence)', 'Diary.getStyles', 'CALL', 'styles: <folder>/css/styles.css or the asset', evidence='SRC Diary.java:1363')
e('Diary.loadMarkdown(CharSequence)', 'Diary.getScript', 'CALL', 'script: <folder>/js/script.js or none', evidence='SRC Diary.java:1363')
e('Diary.loadMarkdown(CharSequence)', 'Diary$1.onPageFinished', 'FRAMEWORK', 'markdownView.loadMarkdown -> loadDataWithBaseURL; the WebView reports onPageFinished',
  evidence=F_MD_LOAD + '; SRC Diary.java:1362-1364')
e('Diary.markdownCheck', 'Diary.dateCheck(CharSequence)', 'CALL', '[text](date:dd/mm/yyyy) links -> file URIs', evidence='SRC Diary.java:1370')
e('Diary.markdownCheck', 'Diary.mapCheck', 'CALL', '[lat,lng] -> ![osm](geo:...)', evidence='SRC Diary.java:1373')
e('Diary.markdownCheck', 'Diary.mediaCheck(CharSequence)', 'CALL', '![..](geo:/audio/video) -> iframe/audio/video HTML', evidence='SRC Diary.java:1376')
e('Diary.dateCheck(CharSequence)', 'Diary.getDay', 'CALL', 'getDay(...) for each date: link that parses in the SHORT date format', guard='the text has a [x](date:...) link outside backticks',
  evidence='SRC Diary.java:1503-1532')
e('Diary.mediaCheck(CharSequence)', 'FileUtils.getMimeType(File)', 'CALL', 'FileUtils.getMimeType(new File(path)) for each ![title](path)', guard='the text has a ![..](..) element (the help text has three)',
  evidence='SRC Diary.java:1382-1390; assets/help.md:173-187')
e('Diary.mediaCheck(CharSequence)', 'FileUtils.<clinit>', 'CALL', 'First use of class FileUtils in this process', guard='FileUtils not initialised yet',
  evidence='SRC Diary.java:1390; FileUtils.java:65-100')
e('FileUtils.getMimeType(File)', 'FileUtils.getExtension', 'CALL', 'getExtension(file.getName())', evidence='SRC FileUtils.java:216-225')
e('Diary.getBaseUrl', 'Diary.getCurrent', 'CALL', 'Uri.fromFile(getCurrent()) + "/"', evidence='SRC Diary.java:1659-1661')
e('Diary.getCurrent', 'Diary.getMonth', 'CALL', 'getMonth(currEntry year, month)', evidence='SRC Diary.java:1665-1668')
e('Diary.getStyles', 'Diary.getHome', 'CALL', 'new File(getHome(), "css/styles.css")', evidence='SRC Diary.java:1672-1679')
e('Diary.getScript', 'Diary.getHome', 'CALL', 'new File(getHome(), "js/script.js")', evidence='SRC Diary.java:1683-1690')
e('Diary$1.onPageFinished', 'Diary.setTitleDate', 'CALL', 'Entry page (or no history): title = date; Up arrow shown iff the entry stack / history is not empty',
  guard='entry, or not canGoBack()', evidence='SRC Diary.java:861-889')

e('Diary.save()', 'S_PERMISSION@DIARY_WRITE', 'ENTERS', 'No WRITE_EXTERNAL_STORAGE: requestPermissions(..., REQUEST_WRITE) and return',
  guard='SDK >= 23 and storage permission not granted', env=ENV_NOPERM, evidence=F_PERMRESULT + '; SRC Diary.java:2250-2264')
e('Diary.save()', 'Diary.eventCheck', 'CALL', 'eventCheck(text): "@ HH:MM title" lines become calendar events', guard='currEntry != null', evidence='SRC Diary.java:2266-2270')
e('Diary.save()', 'Diary.mapCheck', 'CALL', 'mapCheck(text)', evidence='SRC Diary.java:2273')
e('Diary.save()', 'Diary.positionCheck', 'CALL', 'positionCheck(text): store the cursor in a [#]: # (n) marker', evidence='SRC Diary.java:2276')
e('Diary.save()', 'Diary.save(CharSequence)', 'CALL', 'save(text) writes the entry file', evidence='SRC Diary.java:2279')
e('Diary.save()', 'Diary.updateWidgets', 'CALL', 'updateWidgets(text)', evidence='SRC Diary.java:2282')
EVENT_GUARD = 'a line matches ^@ *H:MM +title$ and the time parses with DateFormat.SHORT'
NS_EVENT_LINE = ('the entry holds an unsaved "@ HH:MM title" line that was pasted, received or written outside Diary '
                 '(the help text has none at a line start; saving turns it into "@:")')
e('Diary.eventCheck', 'QueryHandler.insertEvent', 'CALL', 'QueryHandler.insertEvent(start, start + 1 h, title) for each parsed "@ HH:MM title" line',
  guard=EVENT_GUARD, env=ENV_24H, needs_state=NS_EVENT_LINE, writes=['db:CalendarContract.Events'], evidence='SRC Diary.java:1305-1349; assets/help.md:217-224')
# @EVENT: an event line was typed in this visit, so the next save runs insertEvent
for pg in ('S_DIARY_EDIT', 'S_DIARY_EDIT_CHANGED'):
    e(pg, 'Diary$2.afterTextChanged@TYPED_EVENT', 'GUI', 'Typing an event line notifies the TextWatcher',
      gui=['Type a new line "@ 10:30 Dentist" (at sign, time, title) in the entry'], evidence='SRC Diary.java:1077-1086, 1305-1349; assets/help.md:217-224')
e('Diary$2.afterTextChanged@TYPED_EVENT', 'S_DIARY_EDIT_CHANGED@EVENT', 'ENTERS', 'changed = true with an event line in the text', writes=['field:Diary.changed'],
  evidence='SRC Diary.java:1084-1086')
menu_rebuild('Diary$2.afterTextChanged@TYPED_EVENT', line='1085')
e('S_DIARY_EDIT_CHANGED@EVENT', 'Diary.lambda$setListeners$7@EVENT', 'GUI', 'Tap the Accept (✓) button: the entry is saved', gui=['Tap the Accept (✓) button'],
  evidence='SRC Diary.java:992-1017')
e('S_DIARY_EDIT_CHANGED@EVENT', 'Diary.onPause@EVENT', 'SYSTEM', 'Diary loses the foreground with the unsaved event line', gui=PAUSE_GUI, evidence='SRC Diary.java:596-606')
e('Diary.lambda$setListeners$7@EVENT', 'Diary.save()@EVENT', 'CALL', 'changed: save()', guard='changed', evidence='SRC Diary.java:995-998')
e('Diary.lambda$setListeners$7@EVENT', 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown(); changed = false', evidence='SRC Diary.java:999-1004')
e('Diary.lambda$setListeners$7@EVENT', 'Diary.animateAccept', 'CALL', 'animateAccept(); shown = true', evidence='SRC Diary.java:1009-1016')
e('Diary.lambda$setListeners$7@EVENT', 'S_DIARY_VIEW', 'ENTERS', 'Rendered entry shown; the event line now reads "@:10:30 Dentist"', evidence='SRC Diary.java:1009-1016, 1348')
e('Diary.onPause@EVENT', 'Diary.save()@EVENT', 'CALL', 'changed: save()', guard='changed', evidence='SRC Diary.java:598-603')
e('Diary.onPause@EVENT', 'S_DIARY_PAUSED', 'ENTERS', 'Diary in the background', evidence='SRC Diary.java:596')
for dst, trig, ln in (('Diary.eventCheck@EVENT', 'eventCheck(text)', '2270'), ('Diary.mapCheck', 'mapCheck(text)', '2273'), ('Diary.positionCheck', 'positionCheck(text)', '2276'),
                      ('Diary.save(CharSequence)', 'save(text)', '2279'), ('Diary.updateWidgets', 'updateWidgets(text)', '2282')):
    e('Diary.save()@EVENT', dst, 'CALL', trig + ' (storage permission granted)', guard='currEntry != null', evidence='SRC Diary.java:' + ln)
e('Diary.eventCheck@EVENT', 'QueryHandler.insertEvent', 'CALL', 'QueryHandler.insertEvent(start, start + 1 h, title) for the typed "@ HH:MM title" line',
  guard=EVENT_GUARD, env=ENV_24H, writes=['db:CalendarContract.Events'], evidence='SRC Diary.java:1305-1349')
e('Diary.save(CharSequence)', 'Diary.getFile()', 'CALL', 'file = getFile()', evidence='SRC Diary.java:2289')
e('Diary.save(CharSequence)', 'Diary.alertDialog(int,String,int)', 'CALL', 'FileWriter failed: alertDialog(appName, e.getMessage(), OK)',
  guard='non-empty text and the write throws', env=ENV_IO_ERROR, writes=['file:<folder>/YYYY/MM/DD.(txt|md)'], evidence='SRC Diary.java:2304-2318')
e('Diary.alertDialog(int,String,int)', 'S_DLG_ERROR', 'ENTERS', 'builder.show(): message + OK', evidence='SRC Diary.java:2340-2352')
e('S_DLG_ERROR', 'S_DIARY_VIEW', 'ENTERS', 'OK or Back closes the alert (back on the page below)', gui=['Tap OK (or press Back)'],
  evidence=FWS + 'core/java/com/android/internal/app/AlertController.java:344-349 (setButton keeps no message for a null listener), 125-146 (a button click sends its message only when one is set, '
  'then posts MSG_DISMISS_DIALOG), 169-170 (it calls dismiss()), 995-998 (AlertParams starts with mCancelable = true); core/java/android/app/Dialog.java:650-654 (Back calls cancel() '
  'while the dialog is cancelable), 1231-1238 (cancel() sends the cancel message only when one is set, then dismisses); '
  'SRC Diary.java:2348-2351 (setNeutralButton with a null listener, no OnCancelListener, builder.show())')
e('Diary.updateWidgets', 'DiaryWidgetProvider.<init>@APP', 'INTENT', 'sendBroadcast(APPWIDGET_UPDATE, EXTRA_APPWIDGET_IDS = placed ids): the manifest receiver is started',
  writes=['intent:appWidgetIds'],
  evidence=(F_APPWIDGET_PKG + '; SRC Diary.java:2357-2368'),
  note='Implicit broadcast, but AMS sets the caller package for APPWIDGET_UPDATE, so it is not skipped as a background broadcast')
# ---------------------------------------------------------------- Diary page gestures (rounds B, F)
VIEW_PAGES = ('S_DIARY_VIEW', 'S_DIARY_VIEW_CHANGED', 'S_DIARY_BROWSE', 'S_DIARY_SEARCH@VIEW')
EDIT_PAGES = ('S_DIARY_EDIT', 'S_DIARY_EDIT_CHANGED', 'S_DIARY_SEARCH@EDIT')
TEXT_PAGES = EDIT_PAGES + ('S_DIARY_PLAIN',)

# any touch goes through dispatchTouchEvent -> GestureDetector
for pg in DIARY_PAGES:
    e(pg, 'Diary.dispatchTouchEvent', 'GUI', 'Any touch on the Diary window is fed to the GestureDetector (2+ pointers set multi)',
      gui=['Touch the screen (tap, scroll, pinch or fling)'], writes=['field:Diary.multi'], evidence='SRC Diary.java:840-846')
    e(pg, 'Diary$GestureListener.onFling', 'GUI', 'One-finger fling: onFling returns at once because multi is false',
      gui=['Fling quickly with one finger'], guard='multi == false', evidence=F_GESTURE_FLING + '; SRC Diary.java:3436-3441')
    e(pg, 'Diary$GestureListener.onFling@MULTI', 'GUI', 'A fling right after a touch with 2+ pointers (multi == true): swipe navigation',
      gui=['Swipe with two fingers (or pinch, then fling with one finger) left / right / up / down by more than 256 px'],
      guard='multi == true (a multi-pointer touch came first)', evidence=F_GESTURE_FLING + '; SRC Diary.java:840-846, 3436-3486')
e('Diary.dispatchTouchEvent', 'Diary$GestureListener.onDown', 'FRAMEWORK', 'gestureDetector.onTouchEvent(ACTION_DOWN) -> onDown (returns true)',
  evidence=F_GESTURE_DOWN + '; SRC Diary.java:845, 3428-3430')
e('Diary$GestureListener.onFling@MULTI', 'Diary.onSwipeRight', 'CALL', 'Horizontal fling to the right: previous day', guard='|dx| > |dy|, dx > 256 px, |vx| > 256 px/s, dx > 0',
  evidence='SRC Diary.java:3445-3455 (access$1900)')
e('Diary$GestureListener.onFling@MULTI', 'Diary.onSwipeLeft', 'CALL', 'Horizontal fling to the left: next day', guard='|dx| > |dy|, |dx| > 256 px, |vx| > 256 px/s, dx < 0',
  evidence='SRC Diary.java:3445-3459 (access$2000)')
e('Diary$GestureListener.onFling@MULTI', 'Diary.onSwipeDown', 'CALL', 'Vertical fling down: previous month', guard='|dy| >= |dx|, dy > 256 px, |vy| > 256 px/s, dy > 0',
  evidence='SRC Diary.java:3463-3474 (access$2100)')
e('Diary$GestureListener.onFling@MULTI', 'Diary.onSwipeUp', 'CALL', 'Vertical fling up: next month', guard='|dy| >= |dx|, |dy| > 256 px, |vy| > 256 px/s, dy < 0',
  evidence='SRC Diary.java:3463-3478 (access$2200)')
for sw, cal, anim, ln in (('onSwipeLeft', 'getNextCalendarDay', 'animateSwipeLeft', '2995-3003'), ('onSwipeRight', 'getPrevCalendarDay', 'animateSwipeRight', '3006-3014'),
                          ('onSwipeDown', 'getPrevCalendarMonth', 'animateSwipeRight', '3017-3025'), ('onSwipeUp', 'getNextCalendarMonth', 'animateSwipeLeft', '3028-3036')):
    e('Diary.' + sw, 'Diary.' + cal, 'CALL', cal + '() from currEntry', evidence='SRC Diary.java:' + ln)
    e('Diary.' + sw, 'Diary.changeDate(Calendar)', 'CALL', 'entryStack.push(currEntry); changeDate(new date)', writes=['field:Diary.entryStack'], evidence='SRC Diary.java:' + ln)
    e('Diary.' + sw, 'Diary.' + anim, 'CALL', 'Slide-in animation of the MarkdownView', guard='markdown on and shown', evidence='SRC Diary.java:' + ln)
    e('Diary.' + sw, 'S_DIARY_VIEW', 'ENTERS', 'The new date is shown in the MarkdownView', guard='markdown on', evidence='SRC Diary.java:' + ln + ', 2575-2581')

# double tap: switch to the editor at the tapped position
DT = {'': ('S_DIARY_EDIT', ('S_DIARY_VIEW', 'S_DIARY_BROWSE', 'S_DIARY_SEARCH@VIEW')), 'CHANGED': ('S_DIARY_EDIT_CHANGED', ('S_DIARY_VIEW_CHANGED',)),
      'PLAIN': (None, ('S_DIARY_PLAIN',))}
for ctx, (dst, pages) in DT.items():
    dtn = at('Diary$GestureListener.onDoubleTap', ctx)
    for pg in pages:
        e(pg, dtn, 'GUI', 'Double-tap the text: the editor opens at that position' if dst else
          'Double-tap the text: shown is still true with markdown off, so onDoubleTap switches to "editing" (shown = false)',
          gui=['Double-tap the entry'], guard='shown', evidence=F_GESTURE_DOUBLE + '; SRC Diary.java:3491-3497')
    e(dtn, 'Diary.animateEdit', 'CALL', 'animateEdit() (access$2400); the SearchView collapses if expanded', evidence='SRC Diary.java:3511-3518')
    e(dtn, 'Diary$GestureListener.lambda$onDoubleTap$0', 'ASYNC', 'textView.postDelayed(select the tapped line and scroll to it, 128 ms)',
      evidence='SRC Diary.java:3521-3538')
    if dst:
        e(dtn, dst, 'ENTERS', 'EditText and Accept button shown (shown = false)', writes=['field:Diary.shown'], evidence='SRC Diary.java:1241-1245, 3540')
for pg in EDIT_PAGES:
    e(pg, 'Diary$GestureListener.onDoubleTap@EDIT', 'GUI', 'Double-tap while editing: onDoubleTap returns false (not shown)', gui=['Double-tap the text'],
      guard='not shown', evidence=F_GESTURE_DOUBLE + '; SRC Diary.java:3493, 3544')

# MarkdownView pages: Edit button, scroll, long-press, links
EDIT_TAP = {'': ('S_DIARY_EDIT', ('S_DIARY_VIEW', 'S_DIARY_BROWSE', 'S_DIARY_VIEW@INDEX', 'S_DIARY_VIEW@NOCUSTOM', 'S_DIARY_VIEW@COPY')),
            'CHANGED': ('S_DIARY_EDIT_CHANGED', ('S_DIARY_VIEW_CHANGED',)),
            'SEARCH': ('S_DIARY_EDIT', ('S_DIARY_SEARCH@VIEW',)),
            'TEMPLATE': ('S_DIARY_EDIT', ('S_DIARY_VIEW@TEMPLATE',))}
for ctx, (dst, pages) in EDIT_TAP.items():
    et = at('Diary.lambda$setListeners$10', ctx)
    for pg in pages:
        gui = ['Tap the Edit (pencil) button']
        if ctx == 'TEMPLATE':
            gui = ['On an empty day (e.g. Go to date… -> a day without an entry), tap the Edit (pencil) button']
        e(pg, et, 'GUI', 'Tap the Edit button: switch to the EditText', gui=gui, evidence='SRC Diary.java:1033-1062; res/layout/main.xml:78-86')
    e(et, 'Diary.animateEdit', 'CALL', 'animateEdit(); the SearchView collapses if expanded', evidence='SRC Diary.java:1036-1040')
    e(et, 'Diary.lambda$setListeners$9', 'ASYNC', 'edit.postDelayed(scroll to the cursor line, 128 ms)', evidence='SRC Diary.java:1047-1059')
    if ctx == 'TEMPLATE':
        e(et, 'Diary.template', 'CALL', 'useTemplate: template() fills an empty entry from the template page', guard='useTemplate',
          reads=['pref:pref_use_template'], evidence='SRC Diary.java:1042-1044')
        e(et, 'S_DIARY_EDIT_CHANGED', 'ENTERS', 'Empty entry filled from the template (watcher sets changed)', guard='the entry was empty and the template page is readable',
          evidence='SRC Diary.java:2693-2719')
    else:
        e(et, 'Diary.template', 'CALL', 'useTemplate: template() for an empty entry', guard='useTemplate', reads=['pref:pref_use_template'],
          needs_state=NS_TEMPLATE, evidence='SRC Diary.java:1042-1044')
    e(et, dst, 'ENTERS', 'EditText and Accept button shown (shown = false)', writes=['field:Diary.shown'], evidence='SRC Diary.java:1241-1245, 1061')
e('Diary.lambda$setListeners$10@SEARCH', 'Diary$QueryTextListener.onQueryTextChange', 'FRAMEWORK', 'Tapping Edit while searching collapses the SearchView: onQueryTextChange("")',
  guard='the query was not empty', evidence=F_SEARCH_COLLAPSE + '; SRC Diary.java:1039-1040')
for pg in VIEW_PAGES:
    e(pg, 'Diary.lambda$setListeners$11', 'GUI', 'Long-press the Edit button: it hides', gui=['Long-press the Edit (pencil) button'], evidence='SRC Diary.java:1065-1071')
    e(pg, 'Diary.lambda$setListeners$5', 'GUI', 'Scroll the MarkdownView: the Edit button fades out (content scrolled down) or back in',
      gui=['Scroll the rendered entry up or down'], evidence='SRC Diary.java:938-974')
    e(pg, 'Diary.lambda$setListeners$6', 'GUI', 'Long-press the MarkdownView: show the Edit button; returns false so the WebView starts text selection',
      gui=['Long-press a word in the rendered entry'], evidence='SRC Diary.java:978-985')
    e(pg, 'Diary$1.shouldOverrideUrlLoading', 'GUI', 'Tap a link in the rendered entry (the help text has https and file:///android_asset links)',
      gui=['Tap a link in the rendered entry (e.g. "OpenStreetMap" or "help file" in the help text)'],
      guard='the shown text contains a link', evidence=F_WVC_URL + '; SRC Diary.java:896-924; assets/help.md:15, 203-204')
e('Diary.lambda$setListeners$5', 'Diary.startAnimation', 'CALL', 'startAnimation(edit, fade_out / fade_in)', guard='direction changed', evidence='SRC Diary.java:941-972')
e('Diary.lambda$setListeners$5', 'Diary.lambda$setListeners$4', 'ASYNC', 'markdownView.postDelayed(showEdit, 2048 ms) while scrolling down', guard='y > oldY',
  evidence='SRC Diary.java:941-957 (957: markdownView.postDelayed(showEdit, VISIBLE_DELAY); the showEdit lambda is at 930-935)')
e('Diary.lambda$setListeners$4', 'Diary.startAnimation', 'CALL', 'startAnimation(edit, fade_in, VISIBLE)', evidence='SRC Diary.java:932-934')
e('Diary.lambda$setListeners$6', 'Diary.startAnimation', 'CALL', 'startAnimation(edit, fade_in) when hidden', guard='Edit button not visible', evidence='SRC Diary.java:981-982')
e('Diary.lambda$setListeners$6', 'Diary.onActionModeStarted', 'FRAMEWORK', 'The listener returns false: the WebView selects the word and starts a selection ActionMode',
  evidence='INFERRED the WebView engine (Chromium, native code outside the Java sources) starts a selection ActionMode on a long press and the Activity is told about it; SRC Diary.java:985, 3040-3044')
e('Diary$1.shouldOverrideUrlLoading', 'Diary.diaryEntry', 'CALL', 'diaryEntry(url): is it an existing entry file under the diary folder?', evidence='SRC Diary.java:898 (access$600), 2177-2207')
e('Diary$1.shouldOverrideUrlLoading', 'Diary.changeDate(Calendar)', 'CALL', 'Diary entry link: entryStack.push(currEntry); changeDate(calendar); return true',
  guard='diaryEntry(url) != null (a relative link like 25.txt or a date: link to an existing entry)', writes=['field:Diary.entryStack'], evidence='SRC Diary.java:899-905 (access$700)')
e('Diary$1.shouldOverrideUrlLoading', 'S_DIARY_VIEW', 'ENTERS', 'The linked diary entry is shown (Up arrow appears)', guard='diaryEntry(url) != null', evidence='SRC Diary.java:899-905, 861-868')
e('Diary$1.shouldOverrideUrlLoading', 'Diary$1.onPageFinished', 'FRAMEWORK', 'Returns false: the WebView loads the URL itself and reports onPageFinished',
  guard='file:// / file:///android_asset link that is not an entry, or http(s) with Browser off', evidence='INFERRED the WebView engine (Chromium, native code outside the Java sources) loads the URL itself and reports onPageFinished; SRC Diary.java:907-924')
e('Diary$1.shouldOverrideUrlLoading', 'S_DIARY_BROWSE', 'ENTERS', 'entry = false; the linked page is shown in the MarkdownView',
  guard='file/asset link that is not an existing entry, or http(s) link with pref_external off', reads=['pref:pref_external'], writes=['field:Diary.entry'],
  evidence='SRC Diary.java:907-924')
e('Diary$1.shouldOverrideUrlLoading', 'S_DIARY_PAUSED', 'ENTERS', 'Browser on (or a mailto: link): startActivity(VIEW url) opens another app',
  guard='pref_external on or mailto: scheme, and an activity resolves the intent', reads=['pref:pref_external'], evidence='SRC Diary.java:913-921')
e('Diary.diaryEntry', 'Diary.getHome', 'CALL', 'Uri.fromFile(getHome()) prefix check', evidence='SRC Diary.java:2177-2183')

# preference-variant pages share the gestures of S_DIARY_VIEW (their own menu and Edit tap are defined with the menus)
for pg in ('S_DIARY_VIEW@INDEX', 'S_DIARY_VIEW@NOCUSTOM', 'S_DIARY_VIEW@TEMPLATE', 'S_DIARY_VIEW@COPY'):
    e(pg, 'Diary.onPause', 'SYSTEM', 'Diary loses the foreground', gui=PAUSE_GUI, evidence='SRC Diary.java:596-606')
    e(pg, 'Diary.onBackPressed', 'SYSTEM', 'Back key on an entry page', gui=['Press Back'], evidence='SRC Diary.java:731-757')
    e(pg, 'Diary.dispatchTouchEvent', 'GUI', 'Any touch on the Diary window is fed to the GestureDetector', gui=['Touch the screen (tap, scroll, pinch or fling)'],
      writes=['field:Diary.multi'], evidence='SRC Diary.java:840-846')
    e(pg, 'Diary$GestureListener.onDoubleTap', 'GUI', 'Double-tap the text: the editor opens at that position', gui=['Double-tap the entry'], guard='shown',
      evidence=F_GESTURE_DOUBLE + '; SRC Diary.java:3491-3497')
    e(pg, 'Diary$1.shouldOverrideUrlLoading', 'GUI', 'Tap a link in the rendered entry', gui=['Tap a link in the rendered entry'], guard='the shown text contains a link',
      evidence=F_WVC_URL + '; SRC Diary.java:896-924')

# EditText pages: typing, task boxes, focus, long-press, scroll, Accept button
TYPE_GUI = ['Type or delete text in the entry']
for pg in EDIT_PAGES:
    for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
        e(pg, 'Diary$2.%s@TYPED' % cb, 'GUI', 'Typing in the EditText notifies the TextWatcher (%s)' % cb, gui=TYPE_GUI, evidence='SRC Diary.java:1077-1101')
for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
    e('S_DIARY_PLAIN', 'Diary$2.%s@TYPED_PLAIN' % cb, 'GUI', 'Typing on the plain page notifies the TextWatcher (%s)' % cb, gui=TYPE_GUI, evidence='SRC Diary.java:1077-1101')
e('Diary$2.afterTextChanged@TYPED', 'S_DIARY_EDIT_CHANGED', 'ENTERS', 'changed = true: Cancel appears, Accept will save', writes=['field:Diary.changed'], evidence='SRC Diary.java:1084-1086')
menu_rebuild('Diary$2.afterTextChanged@TYPED', line='1085')
menu_rebuild('Diary$2.afterTextChanged@TYPED_PLAIN', line='1085')
menu_rebuild('Diary$2.afterTextChanged', line='1085')
TASK_GUARD = 'the tapped line is a task-list item "- [ ] x" / "- [x] x" and the cursor is in its box'
for ctx, pages in (('', EDIT_PAGES), ('PLAIN', ('S_DIARY_PLAIN',))):
    t13 = at('Diary.lambda$setListeners$13', ctx)
    for pg in pages:
        e(pg, t13, 'GUI', 'Tap the text (a tap on a task-list box toggles it)', gui=['Tap a "[ ]" / "[x]" box in a task-list line (or anywhere in the text)'],
          evidence='SRC Diary.java:1114-1142; assets/help.md:160-166',
          note='The first tap on an unfocused EditText may only take focus without calling onClick (prompt checklist item 11)')
    watchers(t13, 'editable.replace(box, "x" or " ")', '1126-1137', guard=TASK_GUARD)
e('Diary.lambda$setListeners$13', 'S_DIARY_EDIT_CHANGED', 'ENTERS', 'Box toggled: the watcher sets changed', guard=TASK_GUARD, evidence='SRC Diary.java:1126-1137, 1084')
for pg in TEXT_PAGES:
    e(pg, 'Diary.lambda$setListeners$12', 'GUI', 'The EditText gains focus (tap into it) or loses it (e.g. the search field takes focus): hide the keyboard on loss',
      gui=['Tap into the text, or tap the search field'], evidence='SRC Diary.java:1104-1111')
    e(pg, 'Diary.lambda$setListeners$14', 'GUI', 'Long-press the text: show the Accept button; returns false so the EditText starts selection',
      gui=['Long-press a word in the text'], evidence='SRC Diary.java:1145-1152')
    e(pg, 'Diary.lambda$setListeners$16', 'GUI', 'Scroll the editor: the Accept button fades out (content scrolled down) or back in',
      gui=['Scroll the text up or down'], guard='the text is taller than the screen', evidence='SRC Diary.java:1166-1203')
e('Diary.lambda$setListeners$14', 'Diary.startAnimation', 'CALL', 'startAnimation(accept, fade_in) when hidden', guard='Accept not visible', evidence='SRC Diary.java:1148-1149')
e('Diary.lambda$setListeners$14', 'Diary.onActionModeStarted', 'FRAMEWORK', 'The listener returns false: the EditText selects the word and starts the text-selection ActionMode',
  evidence=FWS + 'core/java/android/widget/TextView.java:10877-10893 (performLongClick hands the long press to the Editor), core/java/com/android/internal/policy/DecorView.java:849-852, '
  '864-870, 901-903 (startActionMode asks the window callback, then reports onActionModeStarted), core/java/android/app/Activity.java:6694 (Activity.onActionModeStarted); '
  'INFERRED the text-selection Editor (android.widget.Editor, source not held) starts the selection ActionMode on a long press; SRC Diary.java:1152, 3040-3100',
  note='With pref_extended on and not shown, the selection is extended to the enclosing brackets/quotes (3045-3098)')
e('Diary.lambda$setListeners$16', 'Diary.startAnimation', 'CALL', 'startAnimation(accept, fade_out / fade_in)', guard='direction changed', evidence='SRC Diary.java:1169-1200')
e('Diary.lambda$setListeners$16', 'Diary.lambda$setListeners$15', 'ASYNC', 'scrollView.postDelayed(showAccept, 2048 ms) while scrolling down', guard='y > oldY',
  evidence='SRC Diary.java:1169-1185')
e('Diary.lambda$setListeners$15', 'Diary.startAnimation', 'CALL', 'startAnimation(accept, fade_in, VISIBLE)', evidence='SRC Diary.java:1161-1162')
for pg in EDIT_PAGES:
    e(pg, 'Diary.lambda$setListeners$7@SEARCH' if pg == 'S_DIARY_SEARCH@EDIT' else 'Diary.lambda$setListeners$7', 'GUI',
      'Tap the Accept (✓) button: save if changed, render, back to the MarkdownView', gui=['Tap the Accept (✓) button'],
      evidence='SRC Diary.java:992-1017; res/layout/main.xml:67-75')
    e(pg, 'Diary.lambda$setListeners$8', 'GUI', 'Long-press the Accept button: it hides', gui=['Long-press the Accept (✓) button'], evidence='SRC Diary.java:1020-1026')
for acc in ('Diary.lambda$setListeners$7', 'Diary.lambda$setListeners$7@SEARCH'):
    e(acc, 'Diary.save()', 'CALL', 'Text changed: save()', guard='changed', evidence='SRC Diary.java:995-998')
    e(acc, 'Diary.loadMarkdown()', 'CALL', 'Text changed: loadMarkdown(); changed = false; entry = true', guard='changed',
      writes=['field:Diary.changed', 'field:Diary.entry'], evidence='SRC Diary.java:999-1004')
    menu_rebuild(acc, guard='changed', line='1006')
    e(acc, 'Diary.animateAccept', 'CALL', 'animateAccept(); the SearchView collapses if expanded; shown = true', writes=['field:Diary.shown'],
      evidence='SRC Diary.java:1009-1016')
    e(acc, 'S_DIARY_VIEW', 'ENTERS', 'Rendered entry shown again, no unsaved changes', evidence='SRC Diary.java:1009-1016, 1233-1237')
e('Diary.lambda$setListeners$7@SEARCH', 'Diary$QueryTextListener.onQueryTextChange', 'FRAMEWORK', 'Accept while searching collapses the SearchView: onQueryTextChange("")',
  guard='the query was not empty', evidence=F_SEARCH_COLLAPSE + '; SRC Diary.java:1013-1014')
# ---------------------------------------------------------------- options menu main.xml (round C)
MENU_GUI0 = 'Open the action bar menu (icons or More options ⋮)'
ITEM = {
    'cancel': ('Diary.cancel', 'Tap the ✕ (Cancel) icon', '666-667', 'visible only while changed (632)'),
    'prevEntry': ('Diary.prevEntry', 'Tap ◀ Previous (icon, or More options ⋮ -> Previous when it does not fit)', '669-670',
                  'enabled only if an earlier entry exists or the shown date is after today (630, 2516-2519)'),
    'nextEntry': ('Diary.nextEntry', 'Tap ▶ Next (icon, or More options ⋮ -> Next when it does not fit)', '672-673',
                  'enabled only if a later entry exists or the shown date is before today (629, 2521-2524)'),
    'today': ('Diary.today', 'Tap Today (icon, or More options ⋮ -> Today when it does not fit)', '675-676',
              'enabled only when the shown date is not today (622-628)'),
    'goToDate': ('Diary.goToDate', 'Tap Go to date… (icon, or More options ⋮ -> Go to date… when it does not fit)', '678-679', None),
    'index': ('Diary.index', 'Tap Index (icon, or More options ⋮ -> Index when it does not fit)', '681-682', 'visible only with Use index (633)'),
    'link': ('Diary.addIndexLink', 'Tap More options (⋮) -> Add link', '684-685', 'visible only with Use index (634)'),
    'findAll': ('Diary.findAll', 'Tap More options (⋮) -> Find all…', '687-688',
                'visible only while the SearchView is expanded; opening the overflow re-prepares the menu (648-652)'),
    'print': ('Diary.print', 'Tap More options (⋮) -> Print…', '690-691', None),
    'share': ('Diary.share', 'Tap More options (⋮) -> Share…', '693-694', None),
    'addTime': ('Diary.addTime', 'Tap More options (⋮) -> Add time', '696-697', None),
    'addEvents': ('Diary.addEvents', 'Tap More options (⋮) -> Add events', '699-700', None),
    'addMedia': ('Diary.addMedia()', 'Tap More options (⋮) -> Add media…', '702-703', None),
    'editStyles': ('Diary.editStyles', 'Tap More options (⋮) -> Edit styles…', '705-706', None),
    'editScript': ('Diary.editScript', 'Tap More options (⋮) -> Edit script…', '708-709', None),
    'backup': ('Diary.backup', 'Tap More options (⋮) -> Backup…', '711-712', None),
    'settings': ('Diary.settings', 'Tap More options (⋮) -> Settings', '714-715', None),
}
HEAD_ITEMS = ['prevEntry', 'nextEntry', 'today', 'goToDate']
TAIL_ITEMS = ['print', 'share', 'addTime', 'addEvents', 'addMedia', 'editStyles', 'editScript', 'backup', 'settings']
UP_ENTRY = 'Up arrow shown: entry and the entry stack is not empty (onPageFinished 862-868)'
MENU_CTX = {
    # ctx: (pages, extra items, page entered by Search, Up target, handler overrides)
    'VIEW': (('S_DIARY_VIEW', 'S_DIARY_VIEW@TEMPLATE'), [], 'S_DIARY_SEARCH@VIEW', ('Diary.onBackPressed', UP_ENTRY), {}),
    'VIEW_CHANGED': (('S_DIARY_VIEW_CHANGED',), ['cancel'], 'S_DIARY_SEARCH@VIEW', ('Diary.onBackPressed', UP_ENTRY), {}),
    'EDIT': (('S_DIARY_EDIT',), [], 'S_DIARY_SEARCH@EDIT', ('Diary.onBackPressed', UP_ENTRY), {}),
    'EDIT_CHANGED': (('S_DIARY_EDIT_CHANGED',), ['cancel'], 'S_DIARY_SEARCH@EDIT', ('Diary.onBackPressed', UP_ENTRY), {}),
    'PLAIN': (('S_DIARY_PLAIN',), ['cancel'], 'S_DIARY_SEARCH@VIEW', ('Diary.onBackPressed', UP_ENTRY), {}),
    'SEARCH': (('S_DIARY_SEARCH@VIEW', 'S_DIARY_SEARCH@EDIT'), ['cancel', 'findAll'], None, None, {}),
    'BROWSE': (('S_DIARY_BROWSE',), [], 'S_DIARY_SEARCH@VIEW',
               ('Diary.onBackPressed@BROWSE', 'Up arrow shown: the WebView can go back (onPageFinished 873-877)'), {}),
    'INDEX': (('S_DIARY_VIEW@INDEX',), ['index', 'link'], 'S_DIARY_SEARCH@VIEW', ('Diary.onBackPressed', UP_ENTRY), {}),
    'NOCUSTOM': (('S_DIARY_VIEW@NOCUSTOM',), [], 'S_DIARY_SEARCH@VIEW', ('Diary.onBackPressed', UP_ENTRY),
                 {'goToDate': 'Diary.goToDate@NOCUSTOM'}),
    'COPY': (('S_DIARY_VIEW@COPY',), [], 'S_DIARY_SEARCH@VIEW', ('Diary.onBackPressed', UP_ENTRY), {'addMedia': 'Diary.addMedia()@COPY'}),
}
for ctx, (pages, extra, spage, home, ov) in MENU_CTX.items():
    ois = 'Diary.onOptionsItemSelected@' + ctx
    for pg in pages:
        e(pg, ois, 'GUI', 'Tap an action bar icon or an item under More options (⋮)', gui=[MENU_GUI0],
          guard='menu/main.xml; visible and enabled items as set by onPrepareOptionsMenu (622-654)', evidence='SRC res/menu/main.xml:22-118; Diary.java:659-726')
        e(pg, 'Diary.onPrepareOptionsMenu', 'GUI', 'Open More options (⋮): onPrepareOptionsMenu runs again before the overflow shows',
          gui=['Tap More options (⋮)'], evidence=F_OVERFLOW)
    items = [i for i in ('cancel',) if i in extra] + HEAD_ITEMS + [i for i in ('index', 'link', 'findAll') if i in extra] + TAIL_ITEMS
    for it in items:
        h, g, ln, guard = ITEM[it]
        e(ois, ov.get(it, h), 'CALL', 'switch case R.id.' + it, gui=[g], guard=guard, evidence='SRC Diary.java:' + ln + '; res/menu/main.xml')
    if ctx == 'SEARCH':
        e(ois, 'Diary$QueryTextListener.onQueryTextChange', 'FRAMEWORK', 'Any item other than Find all collapses the SearchView: onQueryTextChange("")',
          guard='item != findAll and the query was not empty', evidence=F_SEARCH_COLLAPSE + '; SRC Diary.java:721-724')
    else:
        e(ois, spage, 'ENTERS', 'R.id.search falls to default (super returns false); the menu then expands the SearchView in the action bar',
          gui=['Tap the Search (magnifier) icon, or More options (⋮) -> Search…'], evidence=F_SEARCH_EXPAND + '; SRC Diary.java:716-718; res/menu/main.xml:63-67')
        e(ois, 'Diary$QueryTextListener.onQueryTextChange', 'FRAMEWORK', 'Expanding the SearchView sets its text to "" and reports onQueryTextChange("") once',
          gui=['Tap the Search (magnifier) icon, or More options (⋮) -> Search…'], guard='Search tapped', evidence=F_SEARCH_EXPAND)
    if home:
        e(ois, home[0], 'CALL', 'switch case android.R.id.home: onBackPressed()', guard=home[1], evidence='SRC Diary.java:663-664, 861-889')

e('Diary.onPrepareOptionsMenu', 'Diary$QueryTextListener.<init>', 'CALL', 'searchView.setOnQueryTextListener(new QueryTextListener())',
  guard='searchView != null (actionViewClass SearchView)', evidence='SRC Diary.java:636-646 (Diary$QueryTextListener.<init> 3320-3323)')
for cb in ('onQueryTextChange', 'onQueryTextSubmit'):
    e('Diary.onPrepareOptionsMenu', 'Diary$QueryTextListener.' + cb, 'REGISTER', 'SearchView query listener (%s)' % cb, evidence='SRC Diary.java:641-645')
for v, base_pg in (('VIEW', 'S_DIARY_VIEW'), ('EDIT', 'S_DIARY_EDIT')):
    pg = 'S_DIARY_SEARCH@' + v
    e(pg, 'Diary$QueryTextListener.onQueryTextChange', 'GUI', 'Type in the search field: each change searches again ' +
      ('(markdownView.findAll)' if v == 'VIEW' else '(regex search, yellow highlight, scroll in the EditText)'),
      gui=['Type a word in the search field'], evidence=FWS + 'core/java/android/widget/SearchView.java:1249-1252; SRC Diary.java:3335-3378')
    e(pg, 'Diary$QueryTextListener.onQueryTextSubmit', 'GUI', 'Submit the query: find the next match', gui=['Type a word, then tap the submit arrow (or Go on the keyboard)'],
      guard='query not empty', evidence=F_SEARCH_SUBMIT + '; SRC Diary.java:3384-3415')
    e(pg, base_pg, 'ENTERS', 'The collapse arrow closes the SearchView', gui=['Tap the ← arrow at the left of the search field'],
      evidence=FWS + 'core/java/android/widget/Toolbar.java:1381-1395 (the collapse button calls collapseActionView on click), 717-723 (collapseActionView collapses the expanded item), '
      '2340-2346 (expandItemActionView adds the collapse button and records the expanded item)')

# ---------------------------------------------------------------- menu handlers: Cancel, navigation, Go to date
e('Diary.cancel', 'Diary.alertDialog(int,int,int,int,OnClickListener)', 'CALL', 'changed: alertDialog("Save changes?", Save, Discard, listener)', guard='changed',
  evidence='SRC Diary.java:1208-1225')
e('Diary.cancel', 'Diary.lambda$cancel$17', 'REGISTER', 'Save / Discard listener of the dialog', evidence='SRC Diary.java:1211-1225')
e('Diary.alertDialog(int,int,int,int,OnClickListener)', 'S_DLG_SAVE_CHANGES', 'ENTERS', 'builder.show(): title, message, Save / Discard', evidence='SRC Diary.java:2325-2337')
e('S_DLG_SAVE_CHANGES', 'Diary.lambda$cancel$17', 'GUI', 'Tap Save or Discard', gui=['Tap Save', 'or tap Discard'], evidence='SRC Diary.java:1214-1225')
e('S_DLG_SAVE_CHANGES', 'S_DIARY_VIEW_CHANGED', 'ENTERS', 'Back or a tap outside dismisses the dialog; nothing changes', gui=['Press Back'],
  guard='opened from the rendered entry', evidence=FWS + 'core/java/com/android/internal/app/AlertController.java:995-998 (AlertParams starts with mCancelable = true), core/java/android/app/Dialog.java:650-654 (Back calls cancel() '
  'while the dialog is cancelable), 680-684 (a touch outside calls cancel()), 1231-1238 (cancel() sends the cancel message only when one is set, then dismisses); '
  'SRC Diary.java:2327-2336 (the builder gets buttons only, no OnCancelListener)')
e('S_DLG_SAVE_CHANGES', 'S_DIARY_EDIT_CHANGED', 'ENTERS', 'Back or a tap outside dismisses the dialog; nothing changes', gui=['Press Back'],
  guard='opened while editing', evidence=FWS + 'core/java/com/android/internal/app/AlertController.java:995-998 (AlertParams starts with mCancelable = true), core/java/android/app/Dialog.java:650-654 (Back calls cancel() '
  'while the dialog is cancelable), 680-684 (a touch outside calls cancel()), 1231-1238 (cancel() sends the cancel message only when one is set, then dismisses); '
  'SRC Diary.java:2327-2336 (the builder gets buttons only, no OnCancelListener)')
e('Diary.lambda$cancel$17', 'Diary.save()', 'CALL', 'Save: save()', guard='BUTTON_POSITIVE', evidence='SRC Diary.java:1216-1218')
e('Diary.lambda$cancel$17', 'Diary.load', 'CALL', 'Save: save() then load(); Discard: load() re-reads the saved file', evidence='SRC Diary.java:1216-1223')
e('Diary.lambda$cancel$17', 'S_DIARY_VIEW', 'ENTERS', 'Text reloaded, changed = false', guard='shown', evidence='SRC Diary.java:1214-1225, 2416-2417')
e('Diary.lambda$cancel$17', 'S_DIARY_EDIT', 'ENTERS', 'Text reloaded in the editor, changed = false', guard='not shown', evidence='SRC Diary.java:1214-1225, 2416-2417')
for h, ln in (('prevEntry', '2596-2600'), ('nextEntry', '2603-2607')):
    e('Diary.' + h, 'Diary.changeDate(Calendar)', 'CALL', 'entryStack.push(currEntry); changeDate(%s)' % h, writes=['field:Diary.entryStack'], evidence='SRC Diary.java:' + ln)
    e('Diary.' + h, 'S_DIARY_VIEW', 'ENTERS', 'That entry is shown (Up arrow appears)', guard='markdown on', evidence='SRC Diary.java:' + ln + ', 2575-2581')
e('Diary.today', 'Diary.changeDate(Calendar)', 'CALL', "entryStack.clear(); changeDate(today's date)", writes=['field:Diary.entryStack'], evidence='SRC Diary.java:2610-2617')
e('Diary.today', 'Diary.template', 'CALL', 'useTemplate and not markdown: template() for an empty entry', guard='pref_use_template on and pref_markdown off',
  needs_state=NS_TEMPLATE_PLAIN, evidence='SRC Diary.java:2619-2621')
e('Diary.today', 'S_DIARY_VIEW', 'ENTERS', "Today's entry shown, entry stack cleared", guard='markdown on', evidence='SRC Diary.java:2610-2618')
e('Diary.goToDate', 'Diary.showCustomCalendarDialog', 'CALL', 'custom (default): showCustomCalendarDialog(currEntry)', guard='pref_custom on',
  reads=['pref:pref_custom'], evidence='SRC Diary.java:1721-1725')
e('Diary.goToDate', 'Diary.showDatePickerDialog', 'CALL', 'not custom: showDatePickerDialog(currEntry)', guard='pref_custom off', reads=['pref:pref_custom'],
  needs_state=NS_CUSTOM_OFF, evidence='SRC Diary.java:1726-1727')
e('Diary.goToDate@NOCUSTOM', 'Diary.showDatePickerDialog', 'CALL', 'Use custom calendar unticked: showDatePickerDialog(currEntry)', guard='pref_custom off',
  reads=['pref:pref_custom'], evidence='SRC Diary.java:1726-1727')
for ctx in RECV_CTX:
    e('Diary.goToDate@' + ctx, 'Diary.showCustomCalendarDialog@' + ctx, 'CALL', 'custom (default): showCustomCalendarDialog(currEntry)', guard='pref_custom on',
      reads=['pref:pref_custom'], evidence='SRC Diary.java:1721-1725')
    e('Diary.goToDate@' + ctx, 'Diary.showDatePickerDialog@' + ctx, 'CALL', 'not custom: showDatePickerDialog(currEntry)', guard='pref_custom off',
      reads=['pref:pref_custom'], needs_state=NS_CUSTOM_OFF, evidence='SRC Diary.java:1726-1727')
for ctx in ('',) + RECV_CTX:
    sc, pg = at('Diary.showCustomCalendarDialog', ctx), 'S_DLG_CALENDAR@' + (ctx or 'GOTO')
    e(sc, 'Diary$EntryDecorator.<init>', 'CALL', 'decorators.add(new EntryDecorator())', evidence='SRC Diary.java:1741-1743')
    e(sc, 'Diary$EntryDecorator.decorate', 'FRAMEWORK', 'calendarView.refreshCalendar(...) draws the month: decorate(dayView) for each day cell (entry days get a background)',
      evidence=F_DECORATE + '; SRC Diary.java:1746-1757, 3560-3569')
    e(sc, pg, 'ENTERS', 'dialog.show(): CustomCalendarDialog over Diary', evidence='SRC Diary.java:1731-1739')
    od = at('Diary.onDateSet(CustomCalendarView,int,int,int)', ctx)
    e(pg, od, 'GUI', 'Pick a day and tap OK', gui=['Tap a day, then OK'], evidence=F_CCD_OK + '; SRC Diary.java:827-836')
    e(pg, 'Diary$EntryDecorator.decorate', 'GUI', 'Change the month or tap a day: the calendar redraws and decorates every day cell',
      gui=['Tap ‹ or › to change the month (or tap a day)'], evidence=F_DECORATE)
    e(pg, 'S_DIARY_VIEW', 'ENTERS', 'Cancel or Back: nothing happens' + ('; haveMedia stays true (hazard candidate)' if ctx else ''),
      gui=['Tap Cancel (or press Back)'], evidence=F_CCD_OK)
    sd, pd = at('Diary.showDatePickerDialog', ctx), at('S_DLG_DATE_PICKER', ctx)
    e(sd, pd, 'ENTERS', 'dialog.show(): framework DatePickerDialog', evidence='SRC Diary.java:1761-1769')
    odp = at('Diary.onDateSet(DatePicker,int,int,int)', ctx)
    e(pd, odp, 'GUI', 'Set the date and tap OK', gui=['Set the date, then OK'], evidence=F_DATEPICKER_OK + '; SRC Diary.java:818-825')
    e(pd, 'S_DIARY_VIEW', 'ENTERS', 'Cancel or Back: nothing happens', gui=['Tap Cancel (or press Back)'],
      evidence=FWS + 'core/java/android/app/DatePickerDialog.java:122-123 (both buttons use the dialog itself as the listener), 175-177 (BUTTON_NEGATIVE only calls cancel()); '
      'core/java/android/app/Dialog.java:650-654 (Back calls cancel()), 1231-1238 (cancel() sends the cancel message only when one is set, then dismisses); '
      'core/java/com/android/internal/app/AlertController.java:125-146 (a button click sends the button message, then posts MSG_DISMISS_DIALOG), 169-170 (it calls dismiss()); '
      'SRC Diary.java:1763-1769 (the dialog is created and shown with no cancel listener); ' + F_DATEPICKER_OK)
    for o, ln in ((od, '829-836'), (odp, '818-825')):
        e(o, 'Diary.changeDate(Calendar)', 'CALL', 'entryStack.push(currEntry); changeDate(picked date)', writes=['field:Diary.entryStack'], evidence='SRC Diary.java:' + ln)
        if ctx:
            e(o, 'Diary.addMedia(Intent)@' + ctx, 'CALL', 'haveMedia (set by mediaCheck): addMedia(getIntent()) inserts the received item', guard='haveMedia',
              reads=['field:Diary.haveMedia'], evidence='SRC Diary.java:' + ln)
            e(o, 'S_DIARY_VIEW', 'ENTERS', 'The picked date is shown (when the received item adds nothing)', guard='markdown on', evidence='SRC Diary.java:' + ln)
        else:
            e(o, 'Diary.addMedia(Intent)', 'CALL', 'haveMedia still true: addMedia(getIntent()) inserts the earlier received item again', guard='haveMedia',
              reads=['field:Diary.haveMedia'], needs_state=NS_HAVEMEDIA, evidence='SRC Diary.java:' + ln + ', 1293-1300, 1654-1655')
            e(o, 'S_DIARY_VIEW', 'ENTERS', 'The picked date is shown', guard='markdown on', evidence='SRC Diary.java:' + ln + ', 2575-2581')

# ---------------------------------------------------------------- Find all (FindTask) and Print
e('Diary.findAll', 'Diary$FindTask.<init>', 'CALL', 'new FindTask(this).execute(searchView.getQuery())', evidence='SRC Diary.java:1774-1780')
e('Diary.findAll', 'Diary$FindTask.doInBackground', 'ASYNC', 'execute -> doInBackground(query) on a worker thread', evidence=F_ASYNC_BG + '; SRC Diary.java:1780')
e('Diary$FindTask.doInBackground', 'Diary.listEntries', 'CALL', 'listEntries(diary.getHome(), entries): every day file, newest first', evidence='SRC Diary.java:3232-3234')
e('Diary$FindTask.doInBackground', 'Diary.getHome', 'CALL', 'diary.getHome() (access$1100)', evidence='SRC Diary.java:3234')
e('Diary$FindTask.doInBackground', 'Diary.read', 'CALL', 'read(file) for each entry', guard='at least one entry file', evidence='SRC Diary.java:3239-3242')
e('Diary$FindTask.doInBackground', 'Diary.parseTime', 'CALL', 'parseTime(file) for the date of each match', guard='an entry contains the query', evidence='SRC Diary.java:3243-3265')
e('Diary$FindTask.doInBackground', 'Diary$FindTask.onPostExecute', 'ASYNC', 'onPostExecute(matches) on the main thread', evidence=F_ASYNC_POST + '; SRC Diary.java:3268')
e('Diary$FindTask.onPostExecute', 'Diary$FindTask.lambda$onPostExecute$1', 'REGISTER', 'builder.setItems(matches, listener)', guard='matches not empty', evidence='SRC Diary.java:3284-3311')
e('Diary$FindTask.onPostExecute', 'S_DLG_FIND_ALL', 'ENTERS', 'builder.show(): result list (or an empty list) with Cancel', evidence='SRC Diary.java:3274-3316')
e('S_DLG_FIND_ALL', 'Diary$FindTask.lambda$onPostExecute$1', 'GUI', 'Tap a result: go to that entry', gui=['Tap a result in the list'], guard='at least one match',
  evidence='SRC Diary.java:3288-3311')
e('S_DLG_FIND_ALL', 'S_DIARY_SEARCH@VIEW', 'ENTERS', 'Cancel or Back: back to the search', gui=['Tap Cancel (or press Back)'], guard='started from the rendered entry',
  evidence='SRC Diary.java:3313-3315')
e('S_DLG_FIND_ALL', 'S_DIARY_SEARCH@EDIT', 'ENTERS', 'Cancel or Back: back to the search', gui=['Tap Cancel (or press Back)'], guard='started while editing',
  evidence='SRC Diary.java:3313-3315')
e('Diary$FindTask.lambda$onPostExecute$1', 'Diary.changeDate(Calendar)', 'CALL', 'Parse the date of the chosen line, diary.changeDate(entry) (access$700)',
  guard='the date prefix parses', evidence='SRC Diary.java:3290-3301')
e('Diary$FindTask.lambda$onPostExecute$1', 'Diary$FindTask.lambda$onPostExecute$0', 'ASYNC', 'searchView.postDelayed(setQuery(search), 256 ms)',
  evidence='SRC Diary.java:3302-3306')
e('Diary$FindTask.lambda$onPostExecute$1', 'S_DIARY_SEARCH@VIEW', 'ENTERS', 'The entry is shown; the SearchView is still expanded (Find all does not collapse it)',
  guard='markdown on', evidence='SRC Diary.java:721-724, 3290-3306')
e('Diary$FindTask.lambda$onPostExecute$0', 'Diary$QueryTextListener.onQueryTextChange', 'FRAMEWORK', 'searchView.setQuery(search, false) puts the query back: onQueryTextChange(search)',
  evidence=FWS + 'core/java/android/widget/SearchView.java:559-560, 1249-1252; SRC Diary.java:3305-3306')
e('Diary.print', 'S_PRINT', 'ENTERS', 'printManager.print(job, markdownView.createPrintDocumentAdapter(job), A4): the print preview opens',
  evidence='SRC Diary.java:1785-1801')
e('S_PRINT', 'Diary.onResume', 'SYSTEM', 'Back, Cancel or after printing: Diary resumes', gui=['Press Back (or print / save as PDF)'],
  evidence='INFERRED the print preview is an activity of the print spooler on top of Diary (another app, its source was not read)')

# ---------------------------------------------------------------- Share… and the FileProvider read path
e('Diary.share', 'FileProvider.getUriForFile', 'CALL', 'shown: Diary.png from the MarkdownView drawing cache in the cache dir; else the entry file -> content:// URI',
  evidence='SRC Diary.java:1813-1838')
e('Diary.share', 'Diary.getFile()', 'CALL', 'not shown: FileProvider.getUriForFile(this, FILE_PROVIDER, getFile())', guard='not shown', evidence='SRC Diary.java:1834-1838')
e('Diary.share', 'S_CHOOSER_SHARE@IMAGE', 'ENTERS', 'startActivity(createChooser(SEND image/png, EXTRA_STREAM = Diary.png, EXTRA_TEXT = entry text))', guard='shown',
  writes=['file:<cache>/Diary.png'], evidence='SRC Diary.java:1807-1831, 1843; ' + F_SHARE_GRANT)
e('Diary.share', 'S_CHOOSER_SHARE@TEXT', 'ENTERS', 'startActivity(createChooser(SEND text/plain, EXTRA_STREAM = entry file, EXTRA_TEXT = entry text))', guard='not shown',
  evidence='SRC Diary.java:1832-1843; ' + F_SHARE_GRANT)
e('Diary.share', 'S_EXIT', 'ENTERS', 'Crash: getDrawingCache() returns null for a MarkdownView that was never laid out -> NullPointerException in Bitmap.createBitmap',
  guard='shown and the MarkdownView was never displayed in this instance (Use markdown off since the start)',
  evidence='SRC Diary.java:1812-1817 (share() with shown == true builds the bitmap from markdownView.getDrawingCache()), 1696, 1713-1717 (markdown off: only the EditText is displayed), '
           '254 (shown starts true); INFERRED View.getDrawingCache() returns null for a view that was never laid out (the View source is not held)',
  note='Hazard candidate; not checked on a device')
e('FileProvider.getUriForFile', 'FileProvider.getPathStrategy', 'CALL', 'getPathStrategy(context, authority) (cached in sCache)', evidence='SRC FileProvider.java:399-400')
e('FileProvider.getUriForFile', 'FileProvider$SimplePathStrategy.getUriForFile', 'CALL', 'strategy.getUriForFile(file): most specific root -> content://authority/<root>/<path>',
  evidence='SRC FileProvider.java:401, 688-724')
RECEIVER_GUI = ['Pick another app in the share sheet that reads the file (e.g. Messaging or Gmail)']
for v, me in (('IMAGE', 'SELF_IMAGE'), ('TEXT', 'SELF_TEXT')):
    pg = 'S_CHOOSER_SHARE@' + v
    e(pg, 'Diary.<init>@' + me, 'GUI', 'Pick Diary in the share sheet: a new Diary instance receives the SEND intent', gui=['Pick Diary in the share sheet'],
      evidence='SRC AndroidManifest.xml:60-74; INFERRED ChooserActivity (the share sheet, another app) starts the picked activity with the read grant (its source was not read)',
      note='The help text describes this self-share for selected text (help.md:205-209)')
    e(pg, 'FileProvider.query', 'GUI', 'The receiving app queries the display name / size of the shared URI', gui=RECEIVER_GUI,
      evidence='INFERRED receiving apps query OpenableColumns of EXTRA_STREAM (another app, its source was not read); ' + F_SHARE_GRANT)
    e(pg, 'FileProvider.getType', 'GUI', 'The receiving app asks the MIME type of the shared URI', gui=RECEIVER_GUI,
      evidence='INFERRED the receiving app calls ContentResolver.getType (another app, its source was not read); ' + F_SHARE_GRANT)
    e(pg, 'FileProvider.openFile', 'GUI', 'The receiving app opens the shared URI for reading', gui=RECEIVER_GUI,
      evidence=FWS + 'core/java/android/content/ContentResolver.java:967 (openInputStream -> openAssetFileDescriptor(uri, "r")), 1246-1247 (mode "r" -> openTypedAssetFileDescriptor), '
      '1410 (provider.openTypedAssetFile); core/java/android/content/ContentProvider.java:423 (the provider transport calls openTypedAssetFile), '
      '1721-1723 (type */* -> openAssetFile(uri, "r")), 1543 (openAssetFile -> openFile(uri, mode)); ' + F_SHARE_GRANT)
    e(pg, 'Diary.onResume', 'SYSTEM', 'Back from the share sheet or from the receiving app', gui=['Press Back'],
      evidence='INFERRED the chooser (the share sheet) is an activity on top of Diary (another app, its source was not read)')
e('FileProvider.query', 'FileProvider$SimplePathStrategy.getFileForUri', 'CALL', 'file = mStrategy.getFileForUri(uri)', evidence='SRC FileProvider.java:436, 727-751')
e('FileProvider.query', 'FileProvider.copyOf(String[],int)', 'CALL', 'cols = copyOf(cols, i) (DISPLAY_NAME / SIZE columns asked for)', evidence='SRC FileProvider.java:442-455')
e('FileProvider.query', 'FileProvider.copyOf(Object[],int)', 'CALL', 'values = copyOf(values, i)', evidence='SRC FileProvider.java:456')
e('FileProvider.getType', 'FileProvider$SimplePathStrategy.getFileForUri', 'CALL', 'file = mStrategy.getFileForUri(uri); MIME type from the extension', evidence='SRC FileProvider.java:474-489')
e('FileProvider.openFile', 'FileProvider$SimplePathStrategy.getFileForUri', 'CALL', 'file = mStrategy.getFileForUri(uri)', evidence='SRC FileProvider.java:543-545')
e('FileProvider.openFile', 'FileProvider.modeToMode', 'CALL', 'ParcelFileDescriptor.open(file, modeToMode(mode))', evidence='SRC FileProvider.java:546-547, 757-780')

# ---------------------------------------------------------------- Add time, Add events (QueryHandler)
watchers('Diary.addTime', 'editable.insert(cursor, time)', '1847-1853')
e('Diary.addTime', 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown()', evidence='SRC Diary.java:1854')
changed_pages('Diary.addTime', 'Current time (SHORT format) inserted at the cursor', '1847-1855')
e('Diary.addEvents', 'QueryHandler.queryEvents', 'CALL', 'QueryHandler.queryEvents(this, day start, day end, listener)', reads=['db:CalendarContract.Instances'],
  evidence='SRC Diary.java:1858-1866')
e('Diary.addEvents', 'Diary.lambda$addEvents$18', 'REGISTER', 'EventListener lambda: insert "@:time title" for each event', evidence='SRC Diary.java:1866-1876')
for q, ln, tok in (('queryEvents', '76-96', 'LISTEN'), ('insertEvent', '99-117', 'INSERT')):
    e('QueryHandler.' + q, 'QueryHandler.<clinit>', 'CALL', 'First use of class QueryHandler in this process', guard='class not initialised yet',
      evidence='SRC QueryHandler.java:44-49')
    e('QueryHandler.' + q, 'QueryHandler.<init>', 'CALL', 'queryHandler == null: new QueryHandler(resolver) (kept in a static field)', guard='first call in this process',
      writes=['static:QueryHandler.queryHandler'], evidence='SRC QueryHandler.java:' + ln)
e('QueryHandler.queryEvents', 'QueryHandler.onQueryComplete@LISTEN', 'ASYNC', 'startQuery(INSTANCE_LISTEN, Instances/<start>/<end>): the worker queries, the handler delivers onQueryComplete',
  writes=['static:QueryHandler.listener'], evidence=F_AQH + '; SRC QueryHandler.java:84-95')
e('QueryHandler.insertEvent', 'QueryHandler.onQueryComplete@INSERT', 'ASYNC', 'startQuery(EVENT_INSERT, values, Calendars.CONTENT_URI): find a calendar id',
  evidence=F_AQH + '; SRC QueryHandler.java:107-116')
e('QueryHandler.onQueryComplete@LISTEN', 'Diary.lambda$addEvents$18', 'CALL', 'INSTANCE_LISTEN: listener.onEvent(begin, title) for each event row',
  guard='the cursor has rows', env=ENV_CAL_EVENT, evidence='SRC QueryHandler.java:122-125, 146-162')
e('QueryHandler.onQueryComplete@INSERT', 'QueryHandler.onInsertComplete', 'ASYNC', 'EVENT_INSERT: first calendar id; startInsert(EVENT_REMIND, Events) -> onInsertComplete',
  guard='at least one calendar row', env=ENV_CAL_ACCOUNT, writes=['db:CalendarContract.Events'], evidence=F_AQH + '; SRC QueryHandler.java:131-144')
watchers('Diary.lambda$addEvents$18', 'editable.insert(cursor, "@:time title")', '1869-1874')
e('Diary.lambda$addEvents$18', 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown()', evidence='SRC Diary.java:1875')
changed_pages('Diary.lambda$addEvents$18', 'Calendar events inserted at the cursor', '1869-1876')
# ---------------------------------------------------------------- Add media…: picker, result, FileUtils path resolution
for ctx, pick in (('', 'PLAIN'), ('COPY', 'COPY')):
    e(at('Diary.addMedia()', ctx), 'S_MEDIA_PICKER@' + pick, 'ENTERS', 'startActivityForResult(createChooser(GET_CONTENT */* OPENABLE), ADD_MEDIA)',
      evidence='SRC Diary.java:1880-1885')
# result contexts: @ADD_MEDIA(_COPY) an image/audio/video was picked, @ADD_FILE another kind of file, @CANCELED Back
PICK_MEDIA_GUI = ['Pick an image (e.g. Pictures/...), audio or video file']
PICK_FILE_GUI = ['Pick a file that is not an image, audio or video (e.g. Download/*.pdf or *.txt)']
for pick, res, am in (('PLAIN', 'ADD_MEDIA', 'Diary.addMedia(Uri,boolean)'), ('COPY', 'ADD_MEDIA_COPY', 'Diary.addMedia(Uri,boolean)@COPY')):
    pg = 'S_MEDIA_PICKER@' + pick
    e(pg, 'Diary.onActivityResult@' + res, 'RESULT', 'An image, audio or video file is picked: RESULT_OK with its URI', gui=PICK_MEDIA_GUI,
      evidence='SRC Diary.java:763-798; INFERRED the picker (another app) returns a content:// URI with a read grant (its source was not read)')
    e(pg, 'Diary.onActivityResult@ADD_FILE', 'RESULT', 'Another kind of file is picked: RESULT_OK with its URI', gui=PICK_FILE_GUI,
      evidence='SRC Diary.java:763-798; INFERRED the picker (another app) returns a content:// URI with a read grant (its source was not read)')
    e(pg, 'Diary.onActivityResult@CANCELED', 'RESULT', 'Back closes the picker: RESULT_CANCELED', gui=['Press Back'], evidence='SRC Diary.java:764-766')
for res, last in (('ADD_MEDIA', ('Diary.addMedia(Uri,boolean)', 'image / audio / video: addMedia(uri, false) inserts ![name](uri) at the cursor',
                                 'type starts with image, audio or video', '791-794')),
                  ('ADD_MEDIA_COPY', ('Diary.addMedia(Uri,boolean)@COPY', 'image (Copy images on): addMedia(uri, false) copies it into the month folder first',
                                      'type starts with image', '791-794')),
                  ('ADD_FILE', ('Diary.addLink', 'Other or unknown type: addLink(uri, title, false) opens the Add link dialog', 'type null, or not image/audio/video',
                                '788-797'))):
    oar = 'Diary.onActivityResult@' + res
    e(oar, 'Diary.resolveContent', 'CALL', 'content:// URI: uri = resolveContent(uri) (file:// if a readable local path is found)', guard='RESULT_OK and scheme content',
      evidence='SRC Diary.java:770-778')
    e(oar, 'FileUtils.getDisplayName', 'CALL', 'Still content:// after resolving: title = FileUtils.getDisplayName(...)', guard='no readable local path',
      env=ENV_NO_PATH, evidence='SRC Diary.java:780-782')
    e(oar, 'FileUtils.getMimeType(Context,Uri)', 'CALL', 'file:// URI: type = FileUtils.getMimeType(this, uri)', guard='the URI was resolved to a file',
      evidence='SRC Diary.java:784-786')
    e(oar, last[0], 'CALL', last[1], guard=last[2], evidence='SRC Diary.java:' + last[3])
    e(oar, 'Diary.onResume', 'LIFECYCLE', 'onActivityResult is delivered before onResume', evidence=F_RESULT)
e('Diary.onActivityResult@CANCELED', 'Diary.onResume', 'LIFECYCLE', 'resultCode != RESULT_OK: return at once; Diary resumes', evidence=F_RESULT + '; SRC Diary.java:764-766')
e('Diary.resolveContent', 'FileUtils.getPath', 'CALL', 'path = FileUtils.getPath(this, uri); a readable file becomes Uri.fromFile', evidence='SRC Diary.java:2892-2903')
e('Diary.resolveContent', 'FileUtils.<clinit>', 'CALL', 'First use of class FileUtils in this process', guard='FileUtils not initialised yet', evidence='SRC Diary.java:2894')
e('FileUtils.getPath', 'FileUtils.isExternalStorageDocument', 'CALL', 'DocumentsContract document URI: ExternalStorageProvider? (primary:<path> -> /sdcard/<path>)',
  guard='document URI (picked through the DocumentsUI picker)', evidence='SRC FileUtils.java:494-535')
e('FileUtils.getPath', 'FileUtils.isDownloadsDocument', 'CALL', 'Not external storage: DownloadsProvider?', guard='document URI, not ExternalStorageProvider',
  evidence='SRC FileUtils.java:537-539')
e('FileUtils.getPath', 'FileUtils.isMediaDocument', 'CALL', 'Not Downloads: MediaProvider (image:/video:/audio: ids)?', guard='document URI, neither external storage nor Downloads',
  evidence='SRC FileUtils.java:559-561')
e('FileUtils.getPath', 'FileUtils.getDataColumn', 'CALL', 'Downloads id -> content://downloads/public_downloads/<id>; Media -> MediaStore _id=?; plain content URI -> its _data column',
  guard='Downloads or Media document, or a plain content:// URI (not Google Photos)', evidence='SRC FileUtils.java:539-603')
e('FileUtils.getPath', 'FileUtils.isGooglePhotosUri', 'CALL', 'Plain content:// URI: Google Photos returns its last path segment', guard='content URI that is not a document URI',
  evidence='SRC FileUtils.java:595-600')
e('FileUtils.getPath', 'FileUtils.fileProviderPath', 'CALL', 'No _data column: rebuild a path from FileProvider-style segments', guard="plain content URI without a _data column (e.g. Diary's own FileProvider URI)",
  evidence='SRC FileUtils.java:602-608, 290-338')
# @SELF: the URI is Diary's own content://org.billthefarmer.diary.fileprovider/<root>/<path> (Share… -> Diary)
e('Diary.resolveContent@SELF', 'FileUtils.getPath@SELF', 'CALL', 'path = FileUtils.getPath(this, own FileProvider URI)', evidence='SRC Diary.java:2892-2903')
e('Diary.resolveContent@SELF', 'FileUtils.<clinit>', 'CALL', 'First use of class FileUtils in this process', guard='FileUtils not initialised yet', evidence='SRC Diary.java:2894')
e('FileUtils.getPath@SELF', 'FileUtils.isGooglePhotosUri', 'CALL', 'Not a document URI, scheme content: Google Photos? (no)', evidence='SRC FileUtils.java:595-600')
e('FileUtils.getPath@SELF', 'FileUtils.getDataColumn@SELF', 'CALL', 'getDataColumn(uri): query the _data column', evidence='SRC FileUtils.java:602-605')
e('FileUtils.getPath@SELF', 'FileUtils.fileProviderPath', 'CALL', 'No _data column: fileProviderPath(uri) rebuilds /sdcard/<path> for the external root (the cache root gives null)',
  evidence='SRC FileUtils.java:607-608, 290-338; res/xml/filepaths.xml:3-5')
e('FileUtils.getDataColumn@SELF', 'FileProvider.query', 'FRAMEWORK', 'resolver.query(own FileProvider URI, [_data]) is answered in-process by FileProvider.query (no _data column, empty row)',
  evidence=FWS + 'core/java/android/content/ContentResolver.java:734-738 (query calls acquireUnstableProvider(uri)), 1774-1781 (it resolves the authority of a content: URI), 538 (the provider lookup is '
  'delegated to a subclass); core/java/android/app/ActivityThread.java:5821-5826, 5921-5927 (acquireProvider first looks the authority up in mProviderMap), '
  '6260-6277, 6157-6165 (a provider installed in this process is registered in mProviderMap under its authorities); INFERRED the subclass of ContentResolver (ContextImpl, source not held) '
  'forwards the lookup to ActivityThread.acquireProvider; SRC FileUtils.java:440-462, FileProvider.java:433-461')
e('FileUtils.getMimeType(Context,Uri)', 'FileUtils.getPath', 'CALL', 'getPath(context, uri) (twice)', evidence='SRC FileUtils.java:231-236')
e('FileUtils.getMimeType(Context,Uri)', 'FileUtils.getMimeType(File)', 'CALL', 'getMimeType(new File(path))', guard='path != null', evidence='SRC FileUtils.java:236-237')
e('FileUtils.getFile', 'FileUtils.getPath', 'CALL', 'path = getPath(context, uri)', evidence='SRC FileUtils.java:628-632')
e('FileUtils.getFile', 'FileUtils.isLocal', 'CALL', 'isLocal(path): not http(s)', evidence='SRC FileUtils.java:633')
e('FileUtils.getPathWithoutExtension', 'FileUtils.getExtension', 'CALL', 'path minus getExtension(path)', evidence='SRC FileUtils.java:139-146')
for ctx in ('', 'COPY'):
    am = at('Diary.addMedia(Uri,boolean)', ctx)
    ns = None if ctx else NS_COPY
    img = 'pref_copy_media on and the media type is image/*'
    e(am, 'FileUtils.getMimeType(Context,Uri)', 'CALL', 'copyMedia: type = FileUtils.getMimeType(this, media)', guard='pref_copy_media on', reads=['pref:pref_copy_media'],
      needs_state=ns, evidence='SRC Diary.java:2759-2766')
    e(am, 'FileUtils.getFile', 'CALL', 'oldMedia = FileUtils.getFile(this, media)', guard=img, needs_state=ns, evidence='SRC Diary.java:2767-2769')
    e(am, 'Diary.getCurrent', 'CALL', "newMedia = new File(getCurrent(), name) in the entry's month folder", guard=img, needs_state=ns, evidence='SRC Diary.java:2770, 2778')
    for fu in ('FileUtils.getPathWithoutExtension', 'FileUtils.getExtension'):
        e(am, fu, 'CALL', 'Name already taken: try name_1.ext, name_2.ext, ...', guard=img + ' and the name exists in the month folder',
          needs_state=(NS_COPY + ', and ' + NS_SAMENAME) if not ctx else NS_SAMENAME, evidence='SRC Diary.java:2771-2779')
    e(am, 'FileUtils.copyFile(File,File)', 'CALL', 'FileUtils.copyFile(oldMedia, newMedia); the entry then links the copy by its name', guard=img, needs_state=ns,
      writes=['file:<folder>/YYYY/MM/<name>'], evidence='SRC Diary.java:2781-2790')
    watchers(am, 'textView.append / editable.insert("![name](uri)")', '2793-2805')
    e(am, 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown()', evidence='SRC Diary.java:2807')
    changed_pages(am, '![name](uri) added to the entry', '2793-2807')
e('Diary.addLink', 'Diary.addLinkDialog', 'CALL', 'addLinkDialog(url, title or last segment, listener)', evidence='SRC Diary.java:2811-2817')
e('Diary.addLink', 'Diary.lambda$addLink$21', 'REGISTER', 'Add link / Cancel listener', evidence='SRC Diary.java:2817-2844')
e('Diary.addLinkDialog', 'S_DLG_ADD_LINK', 'ENTERS', 'builder.show(): URL as message, title in the EditText', evidence='SRC Diary.java:2849-2870')
e('S_DLG_ADD_LINK', 'Diary.lambda$addLink$21', 'GUI', 'Keep or edit the title, tap Add link (or Cancel)', gui=['Tap Add link', 'or tap Cancel'], evidence='SRC Diary.java:2819-2844')
e('S_DLG_ADD_LINK', 'S_DIARY_VIEW', 'ENTERS', 'Back dismisses the dialog', gui=['Press Back'],
  evidence=FWS + 'core/java/com/android/internal/app/AlertController.java:995-998 (AlertParams starts with mCancelable = true), core/java/android/app/Dialog.java:650-654 (Back calls cancel() '
  'while the dialog is cancelable), 1231-1238 (cancel() sends the cancel message only when one is set, then dismisses); '
  'SRC Diary.java:2851-2870 (the builder gets buttons and a view, no OnCancelListener)')
watchers('Diary.lambda$addLink$21', 'textView.append / editable.insert("[title](url)")', '2830-2839', guard='Add link with a non-empty title')
e('Diary.lambda$addLink$21', 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown()', guard='Add link with a non-empty title', evidence='SRC Diary.java:2841')
changed_pages('Diary.lambda$addLink$21', '[title](url) added to the entry', '2821-2842', guard='Add link with a non-empty title')
e('Diary.lambda$addLink$21', 'S_DIARY_VIEW', 'ENTERS', 'Cancel (or an empty title): the dialog closes, nothing added', guard='BUTTON_NEGATIVE or empty title',
  evidence='SRC Diary.java:2819-2828')

# ---------------------------------------------------------------- Edit styles… / Edit script… (Editor for result)
for h, ln, f in (('editStyles', '1889-1895', 'css/styles.css'), ('editScript', '1898-1904', 'js/script.js')):
    e('Diary.' + h, 'Diary.getHome', 'CALL', 'new File(getHome(), "%s")' % f, evidence='SRC Diary.java:' + ln)
    e('Diary.' + h, 'Editor.<init>@STYLES', 'INTENT', 'startActivityForResult(ACTION_EDIT file://<folder>/%s, Editor.class), EDIT_STYLES' % f, writes=['intent:data'],
      evidence='SRC Diary.java:' + ln)
e('Diary.onActivityResult@EDIT_STYLES', 'Diary$1.onPageFinished', 'FRAMEWORK', 'RESULT_OK: markdownView.reload() re-renders with the edited styles/script',
  guard='resultCode == RESULT_OK (Accept or Save in the Editor)', evidence='INFERRED the WebView engine (Chromium, native code outside the Java sources) reports onPageFinished after reload(); SRC Diary.java:764-766, 800-802')
e('Diary.onActivityResult@EDIT_STYLES', 'Diary.onResume', 'LIFECYCLE', 'Then Diary resumes', evidence=F_RESULT)

# ---------------------------------------------------------------- Backup… (ZipTask)
e('Diary.backup', 'Diary.getHome', 'CALL', 'Default name = <home>.zip relative to external storage', evidence='SRC Diary.java:1908-1912')
e('Diary.backup', 'Diary.saveAsDialog', 'CALL', 'saveAsDialog(name, Backup, "Choose a file name", listener)', evidence='SRC Diary.java:1914')
e('Diary.backup', 'Diary.lambda$backup$19', 'REGISTER', 'Save / Cancel / Storage listener', evidence='SRC Diary.java:1914-1947')
e('Diary.saveAsDialog', 'S_DLG_BACKUP', 'ENTERS', 'builder.show() with the path EditText prefilled', evidence='SRC Diary.java:1952-1973; res/layout/save_path.xml')
e('S_DLG_BACKUP', 'Diary.lambda$backup$19', 'GUI', 'Tap Save (keep or edit the path), Storage, or Cancel', gui=['Tap Save', 'or tap Storage', 'or tap Cancel'],
  evidence='SRC Diary.java:1916-1947')
# @BADPATH: the user types a path whose folder does not exist, so the zip stream cannot be opened
e('S_DLG_BACKUP', 'Diary.lambda$backup$19@BADPATH', 'GUI', 'Save to a path in a folder that does not exist',
  gui=['Replace the path with one in a missing folder (e.g. nofolder/backup.zip) and tap Save'], evidence='SRC Diary.java:1916-1936, 3131-3133')
e('Diary.lambda$backup$19@BADPATH', 'Diary$ZipTask.<init>', 'CALL', 'new ZipTask(this).execute(Uri.fromFile(external storage/nofolder/backup.zip))', evidence='SRC Diary.java:1918-1936')
e('Diary.lambda$backup$19@BADPATH', 'Diary$ZipTask.onPreExecute', 'FRAMEWORK', 'zipTask.execute(uri) -> onPreExecute on the main thread', evidence=F_ASYNC_PRE + '; SRC Diary.java:1936')
e('Diary.lambda$backup$19@BADPATH', 'Diary$ZipTask.doInBackground@BADPATH', 'ASYNC', 'execute -> doInBackground(uri) on a worker thread', evidence=F_ASYNC_BG + '; SRC Diary.java:1936')
e('Diary.lambda$backup$19@BADPATH', 'S_DIARY_VIEW', 'ENTERS', 'The dialog closes', evidence='SRC Diary.java:1916-1947')
e('Diary$ZipTask.doInBackground@BADPATH', 'Diary.getHome', 'CALL', 'home = diary.getHome() (access$1100)', evidence='SRC Diary.java:3128-3135')
e('Diary$ZipTask.doInBackground@BADPATH', 'Diary$ZipTask.lambda$doInBackground$0', 'ASYNC', 'openOutputStream(file URI in a missing folder) throws FileNotFoundException: runOnUiThread(alert)',
  evidence=FWS + 'core/java/android/content/ContentResolver.java:981-983, 1005-1012 (openOutputStream(uri) = openOutputStream(uri, "w") -> openAssetFileDescriptor), '
  '1241-1244 (a file: URI is opened with ParcelFileDescriptor.open(new File(path), mode)); INFERRED java.io library behaviour (libcore source not read): '
  'the open fails for a missing parent folder; SRC Diary.java:3131-3133, 3183-3188')
e('Diary$ZipTask.doInBackground@BADPATH', 'Diary$ZipTask.onPostExecute', 'ASYNC', 'onPostExecute: "Backup complete" toast even after the error', evidence=F_ASYNC_POST + '; SRC Diary.java:3191, 3197-3202')
e('S_DLG_BACKUP', 'S_DIARY_VIEW', 'ENTERS', 'Back dismisses the dialog', gui=['Press Back'],
  evidence=FWS + 'core/java/com/android/internal/app/AlertController.java:995-998 (AlertParams starts with mCancelable = true), core/java/android/app/Dialog.java:650-654 (Back calls cancel() '
  'while the dialog is cancelable), 1231-1238 (cancel() sends the cancel message only when one is set, then dismisses); '
  'SRC Diary.java:1954-1973 (the builder gets buttons and a view, no OnCancelListener)')
ZIP_GUARD = 'BUTTON_POSITIVE and a non-empty path'
e('Diary.lambda$backup$19', 'Diary$ZipTask.<init>', 'CALL', 'Save: new ZipTask(this).execute(Uri.fromFile(path)) (a relative path is under external storage)', guard=ZIP_GUARD,
  evidence='SRC Diary.java:1918-1936')
e('Diary.lambda$backup$19', 'Diary$ZipTask.onPreExecute', 'FRAMEWORK', 'zipTask.execute(uri) -> onPreExecute on the main thread', guard=ZIP_GUARD,
  evidence=F_ASYNC_PRE + '; SRC Diary.java:1936')
e('Diary.lambda$backup$19', 'Diary$ZipTask.doInBackground', 'ASYNC', 'execute -> doInBackground(uri) on a worker thread', guard=ZIP_GUARD,
  evidence=F_ASYNC_BG + '; SRC Diary.java:1936')
e('Diary.lambda$backup$19', 'S_DOC_CREATE', 'ENTERS', 'Storage: startActivityForResult(ACTION_CREATE_DOCUMENT application/zip, CREATE_BACKUP)', guard='BUTTON_NEUTRAL',
  evidence='SRC Diary.java:1938-1945')
e('Diary.lambda$backup$19', 'S_DIARY_VIEW', 'ENTERS', 'Save or Cancel closes the dialog', guard='BUTTON_POSITIVE or BUTTON_NEGATIVE', evidence='SRC Diary.java:1916-1947')
e('S_DOC_CREATE', 'Diary.onActivityResult@CREATE_BACKUP', 'RESULT', 'A target document is created: RESULT_OK with its URI', gui=['Choose a folder and a name, tap Save'],
  evidence='SRC Diary.java:804-812; INFERRED DocumentsUI returns the created document URI (another app, its source was not read)')
e('S_DOC_CREATE', 'Diary.onActivityResult@CREATE_BACKUP', 'RESULT', 'Back: RESULT_CANCELED, onActivityResult returns at once', gui=['Press Back'], evidence='SRC Diary.java:764-766')
e('Diary.onActivityResult@CREATE_BACKUP', 'Diary$ZipTask.<init>', 'CALL', 'new ZipTask(this).execute(data.getData())', guard='RESULT_OK with a data URI',
  evidence='SRC Diary.java:804-811')
e('Diary.onActivityResult@CREATE_BACKUP', 'Diary$ZipTask.onPreExecute', 'FRAMEWORK', 'execute -> onPreExecute', guard='RESULT_OK with a data URI', evidence=F_ASYNC_PRE + '; SRC Diary.java:811')
e('Diary.onActivityResult@CREATE_BACKUP', 'Diary$ZipTask.doInBackground', 'ASYNC', 'execute -> doInBackground(uri)', guard='RESULT_OK with a data URI',
  evidence=F_ASYNC_BG + '; SRC Diary.java:811')
e('Diary.onActivityResult@CREATE_BACKUP', 'Diary.onResume', 'LIFECYCLE', 'onActivityResult is delivered before onResume', evidence=F_RESULT)
e('Diary$ZipTask.onPreExecute', 'Diary.showToast(int)', 'CALL', 'showToast(R.string.start) "Start backup"', guard='the Diary is still referenced', evidence='SRC Diary.java:3117-3122')
e('Diary.showToast(int)', 'Diary.showToast(String)', 'CALL', 'showToast(getString(id))', evidence='SRC Diary.java:2953-2957')
e('Diary$ZipTask.doInBackground', 'Diary.getHome', 'CALL', 'home = diary.getHome() (access$1100)', evidence='SRC Diary.java:3128-3135')
e('Diary$ZipTask.doInBackground', 'Diary.listFiles', 'CALL', 'listFiles(home, files): every file and folder', evidence='SRC Diary.java:3139-3142')
e('Diary$ZipTask.doInBackground', 'Diary$ZipTask.lambda$doInBackground$0', 'ASYNC', 'Exception while zipping: diary.runOnUiThread(alert with e.getMessage())',
  guard='openOutputStream or a write throws for a valid path', env=ENV_IO_ERROR, evidence='SRC Diary.java:3183-3188')
e('Diary$ZipTask.doInBackground', 'Diary$ZipTask.onPostExecute', 'ASYNC', 'The task finishes: onPostExecute on the main thread', evidence=F_ASYNC_POST + '; SRC Diary.java:3191')
e('Diary$ZipTask.lambda$doInBackground$0', 'Diary.alertDialog(int,String,int)', 'CALL', 'alertDialog(appName, e.getMessage(), OK) (access$1200)', evidence='SRC Diary.java:3186-3188')
e('Diary$ZipTask.onPostExecute', 'Diary.showToast(int)', 'CALL', 'showToast(R.string.complete) "Backup complete" (also after an error)', evidence='SRC Diary.java:3197-3202')

# ---------------------------------------------------------------- Settings…, Index, Add link (index), template
e('Diary.settings', 'Settings.<init>', 'INTENT', 'startActivity(new Intent(this, Settings.class))', evidence='SRC Diary.java:1976-1979')
e('Diary.index', 'Diary.changeDate(Calendar)', 'CALL', 'entryStack.clear(); changeDate(index page date)', reads=['pref:pref_index_page'], evidence='SRC Diary.java:2625-2631')
e('Diary.index', 'S_DIARY_VIEW@INDEX', 'ENTERS', 'The index page is shown (Index / Add link stay visible)', guard='markdown on', evidence='SRC Diary.java:2625-2631, 633-634')
e('Diary.addIndexLink', 'Diary.index', 'CALL', 'useIndex: remember the shown date, then index()', guard='useIndex', evidence='SRC Diary.java:2634-2640')
e('Diary.addIndexLink', 'Diary.dateCheck(CharSequence,String,Date)', 'CALL', 'title = dateCheck(pref_index_template, "EEEE d MMMM yyyy", linkDate)', reads=['pref:pref_index_template'],
  evidence='SRC Diary.java:2642-2644')
watchers('Diary.addIndexLink', 'textView.append("[title](date:...)")', '2645-2648')
e('Diary.addIndexLink', 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown()', guard='markdown on', evidence='SRC Diary.java:2650-2651')
e('Diary.addIndexLink', 'S_DIARY_VIEW_CHANGED', 'ENTERS', 'Index page shown with the new link appended (unsaved)', guard='markdown on', evidence='SRC Diary.java:2636-2652')
e('Diary.dateCheck(CharSequence,String,Date)', 'Diary.alertDialog(int,String,int)', 'CALL', 'Invalid SimpleDateFormat pattern in <<date ...>>: alertDialog(e.getMessage())',
  guard='the index template holds an invalid pattern', needs_state=NS_BAD_INDEX_TEMPLATE, evidence='SRC Diary.java:2655-2680')
e('Diary.template', 'S_PERMISSION@DIARY_TEMPLATE', 'ENTERS', 'No READ_EXTERNAL_STORAGE: requestPermissions(..., REQUEST_TEMPLATE) and return',
  guard='the entry is empty, SDK >= 23 and storage permission not granted', env=ENV_NOPERM, evidence=F_PERMRESULT + '; SRC Diary.java:2699-2711')
TPL_GUARD = 'the shown entry is empty (2696-2697)'
e('Diary.template', 'Diary.getFile(Calendar)', 'CALL', 'getFile(template page date)', guard=TPL_GUARD, reads=['pref:pref_template_page'], evidence='SRC Diary.java:2711-2713')
e('Diary.template', 'Diary.read', 'CALL', 'text = read(template page file)', guard=TPL_GUARD, evidence='SRC Diary.java:2713')
e('Diary.template', 'Diary.dateCheck(CharSequence,String)', 'CALL', 'text = dateCheck(text, "EEEE d MMMM yyyy HH:mm"): <<date>> patterns become now', guard=TPL_GUARD,
  evidence='SRC Diary.java:2714')
watchers('Diary.template', 'textView.setText(template text)', '2715', guard=TPL_GUARD, ev=F_SETTEXT)
e('Diary.template', 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown()', guard=TPL_GUARD + ' and markdown on', evidence='SRC Diary.java:2717-2718')
e('Diary.dateCheck(CharSequence,String)', 'Diary.alertDialog(int,String,int)', 'CALL', 'Invalid <<date pattern>> in the template page: alertDialog(e.getMessage())',
  guard='the template text holds an invalid pattern', needs_state=NS_BAD_TEMPLATE_PAGE, evidence='SRC Diary.java:2722-2747')

# ---------------------------------------------------------------- runtime permission dialog over Diary (env ENV_NOPERM)
# one context per request code, so a grant is never followed by another request code's branch
for rc, dst, ln in (('READ', 'Diary.load', '2227-2234'), ('WRITE', 'Diary.save()', '2218-2225'), ('TEMPLATE', 'Diary.template', '2236-2243')):
    orp = 'Diary.onRequestPermissionsResult@' + rc
    e('S_PERMISSION@DIARY_' + rc, orp, 'GUI', 'Tap Allow (or Deny) in the permission dialog (REQUEST_%s)' % rc, gui=['Tap Allow (or Deny)'],
      evidence=F_PERMRESULT + '; SRC Diary.java:2212-2245')
    e(orp, dst, 'CALL', 'REQUEST_%s granted: %s()' % (rc, dst.split('.')[1].replace('()', '')),
      guard='requestCode REQUEST_%s and the storage permission granted' % rc, evidence='SRC Diary.java:' + ln)
    e(orp, 'Diary.onResume', 'LIFECYCLE', 'The permission activity closes; Diary resumes', evidence=F_RESULT)

# ---------------------------------------------------------------- received media (SEND / SEND_MULTIPLE / VIEW geo) after the date dialog
e('Diary.addMedia(Intent)@SEND_TEXT', 'Diary.addLink', 'CALL', 'EXTRA_TEXT is an http(s) URL: addLink(uri, EXTRA_TITLE or EXTRA_SUBJECT, true)',
  guard='type text/plain and the text parses as an http/https URI', evidence='SRC Diary.java:1561-1577')
watchers('Diary.addMedia(Intent)@SEND_TEXT', 'textView.append(EXTRA_TEXT)', '1579-1583', guard='type text/plain and the text is not an http(s) URL')
e('Diary.addMedia(Intent)@SEND_TEXT', 'Diary.loadMarkdown()', 'CALL', 'Plain text appended: loadMarkdown()', guard='the text is not an http(s) URL', evidence='SRC Diary.java:1579-1583')
e('Diary.addMedia(Intent)@SEND_TEXT', 'S_DIARY_VIEW_CHANGED', 'ENTERS', 'Shared text appended to the chosen entry (unsaved)', guard='EXTRA_TEXT present and not a URL',
  evidence='SRC Diary.java:1579-1583, 1084-1085')
e('Diary.addMedia(Intent)@SEND_TEXT', 'Diary.resolveContent', 'CALL', 'EXTRA_STREAM content:// (e.g. a shared .txt file): resolveContent(uri)', guard='EXTRA_STREAM with scheme content',
  evidence='SRC Diary.java:1586-1595')
e('Diary.addMedia(Intent)@SEND_TEXT', 'Diary.addLink', 'CALL', 'EXTRA_STREAM: addLink(uri, title, true)', guard='EXTRA_STREAM present', evidence='SRC Diary.java:1586-1600')
e('Diary.addMedia(Intent)@SEND_IMAGE', 'Diary.resolveContent', 'CALL', 'SEND: media = EXTRA_STREAM; content:// -> resolveContent(media)', guard='ACTION_SEND and a content:// stream',
  evidence='SRC Diary.java:1603-1616')
e('Diary.addMedia(Intent)@SEND_IMAGE', 'Diary.addMedia(Uri,boolean)', 'CALL', 'addMedia(media, true) appends ![name](uri) (or an http(s) URL from EXTRA_TEXT)',
  guard='ACTION_SEND with an image/audio/video type', evidence='SRC Diary.java:1618-1634')
e('Diary.addMedia(Intent)@SEND_IMAGE', 'S_EXIT', 'ENTERS', 'Crash: SEND without EXTRA_STREAM dereferences media (NullPointerException at 1615)',
  guard='an app sends image/audio/video without EXTRA_STREAM',
  evidence=FWS + 'core/java/android/content/Intent.java:7166-7168 (getParcelableExtra returns null when the extra is missing); '
  'SRC Diary.java:1610-1618 (media is read at 1611-1612 and dereferenced by media.getScheme() at 1615 before the null check at 1618)',
  note='Hazard candidate; not checked on a device')
e('Diary.addMedia(Intent)@SEND_MULTI', 'Diary.resolveContent', 'CALL', 'SEND_MULTIPLE: resolveContent(uri) for each content:// stream', guard='content:// streams',
  evidence='SRC Diary.java:1638-1647')
e('Diary.addMedia(Intent)@SEND_MULTI', 'Diary.addMedia(Uri,boolean)', 'CALL', 'addMedia(uri, true) for each shared image', guard='EXTRA_STREAM list present', evidence='SRC Diary.java:1638-1650')
e('Diary.addMedia(Intent)@SEND_MULTI', 'S_EXIT', 'ENTERS', 'Crash: SEND_MULTIPLE without an EXTRA_STREAM list (NullPointerException at 1643)',
  guard='an app sends SEND_MULTIPLE without streams',
  evidence=FWS + 'core/java/android/content/Intent.java:7194-7196 (getParcelableArrayListExtra returns null when the extra is missing); '
  'SRC Diary.java:1638-1643 (the list is read at 1641-1642 and iterated at 1643 without a null check)',
  note='Hazard candidate; not checked on a device')
e('Diary.addMedia(Intent)@GEO', 'Diary.addMap', 'CALL', 'type == null and scheme geo: addMap(uri)', guard='VIEW geo: URI', evidence='SRC Diary.java:1551-1558')
# Share… -> Diary (self-share): text/plain with the entry file as EXTRA_STREAM, or image/png Diary.png from the cache root
watchers('Diary.addMedia(Intent)@SELF_TEXT', 'textView.append(EXTRA_TEXT = the shared entry text)', '1579-1583', guard='the entry text is not an http(s) URL')
e('Diary.addMedia(Intent)@SELF_TEXT', 'Diary.loadMarkdown()', 'CALL', 'Shared entry text appended: loadMarkdown()', guard='the text is not an http(s) URL', evidence='SRC Diary.java:1579-1583')
e('Diary.addMedia(Intent)@SELF_TEXT', 'Diary.addLink', 'CALL', 'The text itself is an http(s) URL: addLink(uri, title, true)', guard='the shared text parses as an http/https URI',
  evidence='SRC Diary.java:1561-1577')
e('Diary.addMedia(Intent)@SELF_TEXT', 'Diary.resolveContent@SELF', 'CALL', 'EXTRA_STREAM = content://org.billthefarmer.diary.fileprovider/external/<folder>/YYYY/MM/DD.md: resolveContent',
  evidence='SRC Diary.java:1586-1595, 1834-1838')
e('Diary.addMedia(Intent)@SELF_TEXT', 'Diary.addLink', 'CALL', 'addLink(file URI of the shared entry, title, true): the Add link dialog opens', evidence='SRC Diary.java:1596-1600')
e('Diary.addMedia(Intent)@SELF_IMAGE', 'Diary.resolveContent@SELF', 'CALL', 'media = EXTRA_STREAM content://.../cache/Diary.png: resolveContent(media) (stays content://)',
  evidence='SRC Diary.java:1610-1616, 1813-1829')
e('Diary.addMedia(Intent)@SELF_IMAGE', 'Diary.addMedia(Uri,boolean)', 'CALL', 'addMedia(media, true) appends ![Diary.png](content://...)', evidence='SRC Diary.java:1618-1619')
e('Diary.addMedia(Intent)@SELF_IMAGE', 'FileProvider.openFile', 'FRAMEWORK', 'Rendering ![Diary.png](content://...) makes the WebView read the image through the provider',
  guard='the stream stayed content:// (the cache root has no /sdcard path)', evidence='SRC Diary.java:2807, 1430-1433 (images left to the MarkdownView); INFERRED the WebView engine (Chromium, native code outside the Java sources) loads content:// URLs through the ContentResolver')
e('Diary.addMedia(Intent)', 'Diary.addLink', 'CALL', 'The earlier received text/plain link or stream is added again', guard='text/plain intent with a URL or EXTRA_STREAM',
  needs_state=NS_HAVEMEDIA, evidence='SRC Diary.java:1561-1600')
e('Diary.addMedia(Intent)', 'Diary.addMedia(Uri,boolean)', 'CALL', 'The earlier received image/audio/video is added again', guard='media intent',
  needs_state=NS_HAVEMEDIA, evidence='SRC Diary.java:1603-1650')
e('Diary.addMedia(Intent)', 'Diary.addMap', 'CALL', 'The earlier received geo: URI is added again', guard='geo intent', needs_state=NS_HAVEMEDIA, evidence='SRC Diary.java:1551-1558')
watchers('Diary.addMap', 'textView.append("![osm](geo:...)")', '2875-2880')
e('Diary.addMap', 'Diary.loadMarkdown()', 'CALL', 'loadMarkdown(): mediaCheck turns ![osm](geo:lat,lng) into an OpenStreetMap iframe', evidence='SRC Diary.java:2888, 1393-1424')
e('Diary.addMap', 'S_DIARY_VIEW_CHANGED', 'ENTERS', 'Map added to the chosen entry (unsaved)', evidence='SRC Diary.java:2875-2889')
# ---------------------------------------------------------------- Settings (rounds B, C, D)
e('Settings.<init>', 'Settings.onCreate', 'LIFECYCLE', 'The system instantiates Settings, then onCreate (theme from pref_theme, Up arrow enabled)',
  reads=['pref:pref_theme'], evidence='SRC Settings.java:53-104')
e('Settings.onCreate', 'SettingsFragment.<init>', 'CALL', 'replace(android.R.id.content, new SettingsFragment()).commit()', evidence='SRC Settings.java:91-94')
e('SettingsFragment.<init>', 'SettingsFragment.onCreate', 'LIFECYCLE', 'The fragment transaction commits: fragment onCreate',
  evidence=FWS + 'core/java/android/app/FragmentManager.java:1879-1895, 1905-1912 (a committed transaction is queued and posted), 2036-2048 (execPendingActions runs it), '
  '1141, 1237 (moveToState -> Fragment.performCreate); core/java/android/app/Activity.java:1014 (onCreate: mFragments.dispatchCreate), '
  '7018 (performStart: mFragments.execPendingActions before onStart)')
e('SettingsFragment.onCreate', 'AboutPreference.<init>', 'FRAMEWORK', 'addPreferencesFromResource(preferences.xml) inflates AboutPreference(Context, AttributeSet)',
  evidence=FWS + 'core/java/android/preference/GenericInflater.java:56-57 (constructor signature Context, AttributeSet), 368-385 (createItem: getConstructor, newInstance); SRC SettingsFragment.java:52-53; res/xml/preferences.xml:172-179')
e('SettingsFragment.onCreate', 'DatePickerPreference.<init>', 'FRAMEWORK', 'addPreferencesFromResource inflates the two DatePickerPreference rows (Index page, Template page)',
  evidence=FWS + 'core/java/android/preference/GenericInflater.java:56-57 (constructor signature Context, AttributeSet), 368-385 (createItem: getConstructor, newInstance); SRC SettingsFragment.java:52-53; res/xml/preferences.xml:92-97, 121-126')
e('SettingsFragment.onCreate', 'DatePickerPreference.onSetInitialValue', 'FRAMEWORK', 'The inflated row is attached: dispatchSetInitialValue -> onSetInitialValue(true, null) restores the persisted date',
  guard='pref_index_page or pref_template_page already persisted', reads=['pref:pref_index_page', 'pref:pref_template_page'], needs_state=NS_DATEPREF,
  evidence=F_PREF_INIT + '; SRC DatePickerPreference.java:79-93')
e('SettingsFragment.onCreate', 'DatePickerPreference.getValue', 'CALL', 'Index page and Template page summaries = formatted getValue()', evidence='SRC SettingsFragment.java:66-93')
e('SettingsFragment.onCreate', 'SettingsFragment.onResume', 'LIFECYCLE', 'The fragment resumes with the activity',
  evidence=FWS + 'core/java/android/app/FragmentManager.java:1141, 1322 (moveToState -> Fragment.performResume), 2987-2989 (dispatchResume moves the fragments to RESUMED); '
  'core/java/android/app/Activity.java:7128 (performResume: mFragments.dispatchResume)')
e('SettingsFragment.onResume', 'SettingsFragment.onSharedPreferenceChanged', 'REGISTER', 'registerOnSharedPreferenceChangeListener(this)', evidence='SRC SettingsFragment.java:107-113')
e('SettingsFragment.onResume', 'S_SETTINGS', 'ENTERS', 'Settings list shown', evidence='SRC SettingsFragment.java:107-113')
e('S_SETTINGS', 'SettingsFragment.onPreferenceTreeClick', 'GUI', 'Tap any enabled row: Preference.performClick reports it to the fragment',
  gui=['Tap any enabled settings row'], evidence=F_PREF_CLICK + '; SRC SettingsFragment.java:125-140')
CHECK_KEYS = {  # ctx: (row title, key)
    'CUSTOM': ('Use custom calendar', 'pref_custom'), 'MARKDOWN': ('Use markdown', 'pref_markdown'), 'EXTENDED': ('Use extended selection', 'pref_extended'),
    'USE_INDEX': ('Use index', 'pref_use_index'), 'USE_TEMPLATE': ('Use template', 'pref_use_template'), 'EXTERNAL': ('Browser', 'pref_external'),
    'COPY_MEDIA': ('Copy images', 'pref_copy_media'),
}
for ctx, (row, key) in CHECK_KEYS.items():
    e('S_SETTINGS', 'SettingsFragment.onSharedPreferenceChanged@' + ctx, 'GUI', 'Tap the %s checkbox row: the value flips and the listener fires' % row,
      gui=['Tap the %s row' % row], writes=['pref:' + key], evidence=F_CHECKBOX + '; SRC res/xml/preferences.xml')
SETTINGS_KEY_PAGE = {'CUSTOM': 'S_SETTINGS@CUSTOM', 'MARKDOWN': 'S_SETTINGS@MARKDOWN', 'USE_INDEX': 'S_SETTINGS@USE_INDEX',
                     'USE_TEMPLATE': 'S_SETTINGS@USE_TEMPLATE', 'COPY_MEDIA': 'S_SETTINGS@COPY_MEDIA', 'THEME': 'S_SETTINGS@THEME',
                     'EXTENDED': 'S_SETTINGS', 'EXTERNAL': 'S_SETTINGS', 'FOLDER': 'S_SETTINGS', 'INDEX_TEMPLATE': 'S_SETTINGS@USE_INDEX',
                     'INDEX_PAGE': 'S_SETTINGS@USE_INDEX', 'TEMPLATE_PAGE': 'S_SETTINGS@USE_TEMPLATE'}
for ctx, pg in SETTINGS_KEY_PAGE.items():
    e('SettingsFragment.onSharedPreferenceChanged@' + ctx, pg, 'ENTERS', 'Settings stays shown with the new value' +
      (' (Index page / Index template rows enabled)' if ctx == 'USE_INDEX' else ' (Template page row enabled)' if ctx == 'USE_TEMPLATE' else ''),
      evidence='SRC SettingsFragment.java:146-208' + ('; res/xml/preferences.xml:93, 100' if ctx == 'USE_INDEX' else '; res/xml/preferences.xml:122' if ctx == 'USE_TEMPLATE' else ''))
e('SettingsFragment.onSharedPreferenceChanged@INDEX_PAGE', 'DatePickerPreference.getValue', 'CALL', 'key pref_index_page: summary = formatted getValue()', evidence='SRC SettingsFragment.java:161-172')
e('SettingsFragment.onSharedPreferenceChanged@TEMPLATE_PAGE', 'DatePickerPreference.getValue', 'CALL', 'key pref_template_page: summary = formatted getValue()', evidence='SRC SettingsFragment.java:183-196')
e('SettingsFragment.onSharedPreferenceChanged@THEME', 'Settings.<init>', 'SYSTEM', 'key pref_theme: getActivity().recreate() (Settings restarts in the new theme)',
  guard='SDK != 23', evidence=F_RELAUNCH + '; SRC SettingsFragment.java:198-207')
for dlg, row, ctx, ev, pg in (('S_DLG_FOLDER', 'Folder', 'FOLDER', F_EDITTEXT_PREF, 'S_SETTINGS'), ('S_DLG_THEME', 'Theme', 'THEME', F_LIST_PREF, 'S_SETTINGS'),
                              ('S_DLG_INDEX_TEMPLATE', 'Index template', 'INDEX_TEMPLATE', F_EDITTEXT_PREF, 'S_SETTINGS@USE_INDEX')):
    e(pg, dlg, 'ENTERS', 'Tap the %s row: its dialog opens' % row, gui=['Tap the %s row' % row], evidence=F_DLGPREF_SHOW + '; SRC res/xml/preferences.xml')
    e(dlg, 'SettingsFragment.onSharedPreferenceChanged@' + ctx, 'GUI', 'Enter or pick a different value and confirm',
      gui=['Pick a different theme (Light / Dark / System)'] if ctx == 'THEME' else ['Type a different value and tap OK'], guard='new value != old value',
      writes=['pref:pref_' + ctx.lower()], evidence=ev)
    e(dlg, pg, 'ENTERS', 'Cancel / Back, or the same value: nothing is reported', gui=['Tap Cancel (or press Back)'], evidence=ev)
e('S_SETTINGS', 'AboutPreference.onBindDialogView', 'GUI', 'Tap About: the dialog view is bound when the dialog is shown', gui=['Tap the About row'],
  evidence=F_DLGPREF_SHOW + '; SRC AboutPreference.java:50-98')
e('AboutPreference.onBindDialogView', 'S_DLG_ABOUT', 'ENTERS', 'About dialog: version, build date, copyright and licence links', evidence='SRC AboutPreference.java:50-98; res/layout/about.xml')
e('S_DLG_ABOUT', 'S_SETTINGS', 'ENTERS', 'OK or Back closes the dialog', gui=['Tap OK (or press Back)'],
  evidence=FWS + 'core/java/android/preference/DialogPreference.java:318-319 (the dialog is shown with the preference as its dismiss listener), 386-388 (onClick records the clicked button), '
  '390-395 (onDismiss calls onDialogClosed); core/java/android/app/Dialog.java:650-654 (Back calls cancel() while the dialog is cancelable), 1231-1238 (cancel() dismisses); '
  'SRC res/xml/preferences.xml:177 (no negative button)')
for ctx, pg_from in (('INDEX', 'S_SETTINGS@USE_INDEX'), ('TEMPLATE', 'S_SETTINGS@USE_TEMPLATE')):
    row = 'Index page' if ctx == 'INDEX' else 'Template page'
    ocd, odc, dpg = 'DatePickerPreference.onCreateDialogView@' + ctx, 'DatePickerPreference.onDialogClosed@' + ctx, 'S_DLG_DATE_PREF@' + ctx
    e(pg_from, ocd, 'GUI', 'Tap the %s row: DialogPreference.showDialog asks for the dialog view' % row, gui=['Tap the %s row' % row],
      evidence=F_DLGPREF_SHOW + '; SRC DatePickerPreference.java:50-67')
    e(pg_from, 'SettingsFragment.onPreferenceTreeClick', 'GUI', 'The same tap is reported to the fragment', gui=['Tap the %s row' % row], evidence=F_PREF_CLICK)
    e(ocd, 'DatePickerPreference.lambda$onCreateDialogView$0', 'REGISTER', 'picker.init(y, m, d, OnDateChangedListener)', evidence='SRC DatePickerPreference.java:55-66')
    e(ocd, dpg, 'ENTERS', 'Dialog with a DatePicker at the stored date', evidence='SRC DatePickerPreference.java:50-67')
    lam, dpc, odcc = 'DatePickerPreference.lambda$onCreateDialogView$0@' + ctx, dpg + '_CHANGED', odc + '_CHANGED'
    for p in (dpg, dpc):
        e(p, lam, 'GUI', 'Change the date in the picker: value = the new date', gui=['Change the day, month or year'],
          writes=['field:DatePickerPreference.value'], evidence='INFERRED DatePicker calls OnDateChangedListener on each change (core/java/android/widget/DatePicker.java:122-133 declares the callback and 226-228 passes it to '
          'the delegate, but the delegate classes that call it are not held, so that call was not read); SRC DatePickerPreference.java:59-66')
    e(lam, dpc, 'ENTERS', 'The dialog now holds a different date', evidence='SRC DatePickerPreference.java:62-66')
    e(dpg, odc, 'GUI', 'Tap OK or Cancel without changing the date: the dialog closes', gui=['Tap OK (or Cancel)'], evidence=F_DLGPREF_CLOSE + '; SRC DatePickerPreference.java:97-104')
    e(dpc, odcc, 'GUI', 'Tap OK (or Cancel) after changing the date', gui=['Tap OK'], evidence=F_DLGPREF_CLOSE + '; SRC DatePickerPreference.java:97-104')
    e(odcc, 'SettingsFragment.onSharedPreferenceChanged@' + ctx + '_PAGE', 'FRAMEWORK', 'OK: persistLong(new value); the listener fires because the value changed',
      guard='OK pressed', writes=['pref:pref_%s_page' % ctx.lower()], evidence=F_SPI + '; SRC DatePickerPreference.java:100-103')
    e(odcc, pg_from, 'ENTERS', 'Cancel: nothing persisted', guard='Cancel pressed', evidence='SRC DatePickerPreference.java:97-104')
    e(odc, pg_from, 'ENTERS', 'Cancel, or OK with the same date: nothing reported', evidence='SRC DatePickerPreference.java:97-104; ' + F_SPI)
for ctx in [None] + list(SETTINGS_KEY_PAGE):
    pg = SETTINGS_KEY_PAGE.get(ctx, 'S_SETTINGS') if ctx else 'S_SETTINGS'
    if ctx and pg != 'S_SETTINGS@' + ctx:
        continue
    oi, dr = at('Settings.onOptionsItemSelected', ctx), at('Diary.onResume', ctx)
    e(pg, oi, 'GUI', 'Tap the Up arrow', gui=['Tap the Up arrow (top-left)'], evidence='SRC Settings.java:96-102, 109-117')
    e(oi, dr, 'SYSTEM', 'android.R.id.home: finish(); Diary resumes', guard='item id == android.R.id.home', evidence='SRC Settings.java:111-115')
    e(pg, dr, 'SYSTEM', 'Back finishes Settings; Diary resumes', gui=['Press Back'],
      evidence=F_BACK + '; SRC Settings.java:36-119 (no onBackPressed override in the class), 93-95 (the fragment transaction does not call addToBackStack)')
    e(pg, 'SettingsFragment.onPause', 'SYSTEM', 'Settings loses the foreground', gui=['Press Home', 'or Back / Up', 'or change Theme (recreate)'],
      evidence='SRC SettingsFragment.java:117-122')
e('S_SETTINGS', 'Settings.<init>', 'SYSTEM', 'Rotation recreates Settings (the FragmentManager restores the fragment and a new one is added)', gui=['Rotate the screen'],
  guard='orientation change', evidence=F_RELAUNCH)
e('SettingsFragment.onPause', 'S_SETTINGS_PAUSED', 'ENTERS', 'Settings in the background (listener unregistered)', guard='not finishing', evidence='SRC SettingsFragment.java:117-122')
e('S_SETTINGS_PAUSED', 'SettingsFragment.onResume', 'SYSTEM', 'Return to Settings', gui=['Return via recents'],
  evidence=FWS + 'core/java/android/app/FragmentManager.java:1141, 1322 (moveToState -> Fragment.performResume), 2987-2989 (dispatchResume moves the fragments to RESUMED); '
  'core/java/android/app/Activity.java:7128 (performResume: mFragments.dispatchResume)')
DIARY_KEY_PAGE = {'CUSTOM': 'S_DIARY_VIEW@NOCUSTOM', 'USE_INDEX': 'S_DIARY_VIEW@INDEX', 'USE_TEMPLATE': 'S_DIARY_VIEW@TEMPLATE', 'COPY_MEDIA': 'S_DIARY_VIEW@COPY'}
for ctx, pg in DIARY_KEY_PAGE.items():
    e('Diary.onResume@' + ctx, pg, 'ENTERS', 'Back in Diary with the changed preference (getPreferences in onResume); other calls as Diary.onResume',
      reads=['pref:' + CHECK_KEYS[ctx][1]], evidence='SRC Diary.java:539-571, 1259-1287')
e('Diary.onResume@MARKDOWN', 'Diary.setVisibility', 'CALL', 'markdown off: setVisibility() hides the MarkdownView and both buttons', reads=['pref:pref_markdown'],
  evidence='SRC Diary.java:570, 1712-1717')
e('Diary.onResume@MARKDOWN', 'S_DIARY_PLAIN', 'ENTERS', 'Back in Diary with Use markdown off: EditText only', evidence='SRC Diary.java:1712-1717')
e('Diary.onResume@THEME', 'Diary.<init>@RECREATE', 'SYSTEM', 'pref_theme differs from the theme read in onCreate: recreate()', guard='SDK != 23',
  reads=['pref:pref_theme'], evidence=F_RELAUNCH + '; SRC Diary.java:542-548')

# ---------------------------------------------------------------- Editor (Edit styles…/Edit script… for result, or opened by another app)
e('S_ENTRY', 'Editor.<init>@EXTERNAL', 'ENTRY', 'Another app opens a text file with Diary\'s Editor (VIEW/EDIT text/*)',
  gui=['In Files open a text file with "Open with" -> Diary (e.g. Downloads -> todo.txt; the root it is opened from decides which FileUtils.getPath branch runs)'],
  evidence='SRC AndroidManifest.xml:85-98', note=OUTSIDE)
for x in ('STYLES', 'EXTERNAL'):
    oc = 'Editor.onCreate@' + x
    e('Editor.<init>@' + x, oc, 'LIFECYCLE', 'The system instantiates Editor, then onCreate (theme from pref_theme, Up arrow on)', reads=['pref:pref_theme'],
      evidence='SRC Editor.java:72-110')
    e(oc, 'Editor.setListeners', 'CALL', 'setListeners()', evidence='SRC Editor.java:135')
    if x == 'EXTERNAL':
        e(oc, 'Editor.resolveContent', 'CALL', 'content:// URI: uri = resolveContent(uri); file stays null if it cannot be mapped', guard='intent data has scheme content',
          evidence='SRC Editor.java:114-126')
    e(oc, 'Editor.read@' + x, 'CALL', 'text = read(uri); textView.setText(text) before the watcher is registered (no watcher call)',
      guard='intent data != null and savedInstanceState == null', reads=['file:intent data'], evidence='SRC Editor.java:128-132')
    e(oc, 'S_EDITOR@' + x, 'ENTERS', 'Editor shows the file with the Accept button and the Up arrow', evidence='SRC Editor.java:72-136; res/layout/editor.xml')
    # one permission page / result context per request code (a REQUEST_READ grant never runs the REQUEST_WRITE branch)
    pr, pw = 'S_PERMISSION@EDITOR_%s_READ' % x, 'S_PERMISSION@EDITOR_%s_WRITE' % x
    orr, orw = 'Editor.onRequestPermissionsResult@%s_READ' % x, 'Editor.onRequestPermissionsResult@%s_WRITE' % x
    e('Editor.read@' + x, pr, 'ENTERS', 'No READ_EXTERNAL_STORAGE: requestPermissions(..., REQUEST_READ); empty text',
      guard='SDK >= 23 and storage permission not granted', env=ENV_NOPERM, evidence=F_PERMRESULT + '; SRC Editor.java:363-376')
    e('Editor.write@' + x, pw, 'ENTERS', 'No WRITE_EXTERNAL_STORAGE: requestPermissions(..., REQUEST_WRITE) and return',
      guard='SDK >= 23 and storage permission not granted', env=ENV_NOPERM, evidence=F_PERMRESULT + '; SRC Editor.java:398-409',
      note='The caller finishes right after (Editor.java:197-198, 261-262), so this grant result is probably dropped (hazard candidate)')
    e('Editor.write@' + x, 'Editor.alertDialog(int,String,int)', 'CALL', 'FileWriter failed: alertDialog(appName, e.getMessage(), OK)', guard='file != null and the write throws',
      env=ENV_IO_ERROR, writes=['file:edited file'], evidence='SRC Editor.java:411-425')
    e(pr, orr, 'GUI', 'Tap Allow (or Deny) in the permission dialog (REQUEST_READ)', gui=['Tap Allow (or Deny)'], evidence=F_PERMRESULT + '; SRC Editor.java:282-312')
    e(pw, orw, 'GUI', 'Tap Allow (or Deny) in the permission dialog (REQUEST_WRITE)', gui=['Tap Allow (or Deny)'],
      evidence=F_PERMRESULT + '; SRC Editor.java:282-312; INFERRED the permission result still arrives after the Editor finished (not checked)')
    e(orr, 'Editor.read@' + x, 'CALL', 'REQUEST_READ granted: text = read(uri)', guard='READ_EXTERNAL_STORAGE granted', evidence='SRC Editor.java:300-308')
    for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
        e(orr, 'Editor$1.' + cb, 'FRAMEWORK', 'textView.setText(text) after the watcher was registered (%s; changed = true)' % cb, guard='READ_EXTERNAL_STORAGE granted',
          evidence=F_SETTEXT + '; SRC Editor.java:308, 146-168')
    e(orr, 'S_EDITOR_CHANGED@' + x, 'ENTERS', 'File text loaded after the grant; the watcher marked it changed', guard='READ_EXTERNAL_STORAGE granted',
      evidence='SRC Editor.java:300-308, 150-154')
    e(orw, 'Editor.write@' + x, 'CALL', 'REQUEST_WRITE granted: write(text, file)', guard='WRITE_EXTERNAL_STORAGE granted while the Editor is still alive',
      evidence='SRC Editor.java:288-297; INFERRED the permission result still arrives after finish() (not checked)')
    for k, pg in ((x, 'S_EDITOR@' + x), (x + '_CHANGED', 'S_EDITOR_CHANGED@' + x)):
        ch = k.endswith('_CHANGED')
        acc, oi, ob, ss = ('Editor.lambda$setListeners$1@' + k, 'Editor.onOptionsItemSelected@' + k, 'Editor.onBackPressed@' + k, 'Editor.onSaveInstanceState@' + k)
        for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
            e(pg, 'Editor$1.%s@TYPED_%s' % (cb, x), 'GUI', 'Typing notifies the TextWatcher (%s)' % cb, gui=['Type or delete text'], evidence='SRC Editor.java:146-168')
        e(pg, 'Editor.lambda$setListeners$0', 'GUI', 'Long-press the text: the Accept button reappears; returns false (text selection)', gui=['Long-press a word in the text'],
          evidence='SRC Editor.java:172-177')
        e(pg, acc, 'GUI', 'Tap the Accept (✓) button: write if changed, return RESULT_OK', gui=['Tap the Accept (✓) button'], evidence='SRC Editor.java:183-199')
        e(pg, 'Editor.lambda$setListeners$2', 'GUI', 'Long-press the Accept button: it hides', gui=['Long-press the Accept (✓) button'], evidence='SRC Editor.java:202-207')
        e(pg, oi, 'GUI', 'Tap the Up arrow', gui=['Tap the Up arrow (top-left)'], evidence='SRC Editor.java:110, 229-239')
        e(oi, ob, 'CALL', 'item id == android.R.id.home: onBackPressed()', evidence='SRC Editor.java:231-234')
        e(pg, ob, 'SYSTEM', 'Back key', gui=['Press Back'], evidence='SRC Editor.java:244-278')
        ssr = 'Editor.onSaveInstanceState@ROTATE_' + k
        e(pg, ss, 'SYSTEM', 'Home: state (changed) saved before onStop', gui=['Press Home'], evidence=F_SAVESTATE + '; SRC Editor.java:221-225')
        e(pg, ssr, 'SYSTEM', 'Rotation: state (changed) saved before the Editor is destroyed and recreated', gui=['Rotate the screen'], guard='orientation change',
          evidence=F_RELAUNCH + '; SRC Editor.java:221-225')
        e(ssr, 'Editor.<init>@ROT_' + k, 'SYSTEM', 'A new Editor instance is created with the saved state', guard='orientation change',
          writes=['bundle:changed'], evidence=F_RELAUNCH)
        e(ss, 'S_EDITOR_PAUSED@' + k, 'ENTERS', 'Editor in the background', evidence=F_SAVESTATE)
        e('S_EDITOR_PAUSED@' + k, pg, 'ENTERS', 'Return to the Editor', gui=['Return via recents'],
          evidence=FWS + 'core/java/android/app/ActivityThread.java:3556 (performResumeActivity calls activity.performResume on the same instance), 4123-4128 (a stopped record is restarted with activity.performRestart); '
          'core/java/android/app/Activity.java:7056-7095 (performRestart: onRestart, then performStart), 7098-7099 (performResume calls performRestart first)')
        rini, roc, rres = 'Editor.<init>@ROT_' + k, 'Editor.onCreate@ROT_' + k, 'Editor.onRestoreInstanceState@ROT_' + k
        e(rini, roc, 'LIFECYCLE', 'The new Editor instance runs onCreate with saved state (no read: savedInstanceState != null)', evidence='SRC Editor.java:72-136')
        e(roc, 'Editor.setListeners', 'CALL', 'setListeners()', evidence='SRC Editor.java:135')
        if x == 'EXTERNAL':
            e(roc, 'Editor.resolveContent', 'CALL', 'content:// URI resolved again', guard='intent data has scheme content', evidence='SRC Editor.java:118-121')
        e(roc, rres, 'LIFECYCLE', 'onStart, then onRestoreInstanceState(saved)', evidence=F_RESTORE + '; SRC Editor.java:213-217')
        for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
            e(rres, 'Editor$1.' + cb, 'FRAMEWORK', 'super.onRestoreInstanceState restores the EditText text and notifies the watcher registered in onCreate (%s)' % cb,
              evidence=FWS + 'core/java/android/widget/TextView.java:5019-5031 (onSaveInstanceState freezes the text into the SavedState), '
              '5081-5083 (onRestoreInstanceState calls setText(ss.text)); SRC Editor.java:215')
        e(rres, pg, 'ENTERS', 'changed restored from the bundle: back on the same Editor page', reads=['bundle:changed'], evidence='SRC Editor.java:213-217')
        if ch:
            e(acc, 'Editor.write@' + x, 'CALL', 'changed: write(textView.getText(), file)', guard='changed', evidence='SRC Editor.java:185-189')
            e(ob, 'Editor.alertDialog(int,int,int,int,OnClickListener)@' + x, 'CALL', 'changed: alertDialog("Save changes?", Save, Discard, listener)', evidence='SRC Editor.java:250-253')
            e(ob, 'Editor.lambda$onBackPressed$3@' + x, 'REGISTER', 'Save / Discard listener', evidence='SRC Editor.java:253-271')
        if x == 'STYLES':
            e(acc, 'Diary.onActivityResult@EDIT_STYLES', 'RESULT', 'setResult(RESULT_OK); finish(): Diary reloads the MarkdownView', writes=['result:RESULT_OK'],
              evidence='SRC Editor.java:191-198; Diary.java:800-802')
            if not ch:
                e(ob, 'Diary.onActivityResult@EDIT_STYLES', 'RESULT', 'Unchanged: setResult(RESULT_CANCELED); finish(): onActivityResult returns at once',
                  writes=['result:RESULT_CANCELED'], evidence='SRC Editor.java:273-276; Diary.java:764-766')
        else:
            e(acc, 'S_EXIT', 'ENTERS', 'setResult(RESULT_OK); finish(): back in the app that opened the file', evidence='SRC Editor.java:191-198')
            if not ch:
                e(ob, 'S_EXIT', 'ENTERS', 'Unchanged: setResult(RESULT_CANCELED); finish()', evidence='SRC Editor.java:273-276')
    e('Editor$1.afterTextChanged@TYPED_' + x, 'S_EDITOR_CHANGED@' + x, 'ENTERS', 'changed = true (Back now asks Save / Discard)', writes=['field:Editor.changed'],
      evidence='SRC Editor.java:150-154')
    ad, dlg, lob = 'Editor.alertDialog(int,int,int,int,OnClickListener)@' + x, 'S_DLG_EDITOR_SAVE@' + x, 'Editor.lambda$onBackPressed$3@' + x
    e(ad, dlg, 'ENTERS', 'builder.show(): "Save changes?" Save / Discard', evidence='SRC Editor.java:331-343')
    e(dlg, lob, 'GUI', 'Tap Save or Discard', gui=['Tap Save', 'or tap Discard'], evidence='SRC Editor.java:256-271')
    e(dlg, 'S_EDITOR_CHANGED@' + x, 'ENTERS', 'Back dismisses the dialog', gui=['Press Back'],
      evidence=FWS + 'core/java/com/android/internal/app/AlertController.java:995-998 (AlertParams starts with mCancelable = true), core/java/android/app/Dialog.java:650-654 (Back calls cancel() '
      'while the dialog is cancelable), 1231-1238 (cancel() sends the cancel message only when one is set, then dismisses); '
      'SRC Editor.java:333-342 (the builder gets buttons only, no OnCancelListener)')
    e(lob, 'Editor.write@' + x, 'CALL', 'Save: write(text, file)', guard='BUTTON_POSITIVE', evidence='SRC Editor.java:258-260')
    if x == 'STYLES':
        e(lob, 'Diary.onActivityResult@EDIT_STYLES', 'RESULT', 'Save: RESULT_OK; Discard: RESULT_CANCELED; finish()', evidence='SRC Editor.java:258-268; Diary.java:764-766, 800-802')
    else:
        e(lob, 'S_EXIT', 'ENTERS', 'finish(): back in the app that opened the file', evidence='SRC Editor.java:258-268')
e('Editor.resolveContent', 'FileUtils.getPath', 'CALL', 'path = FileUtils.getPath(this, uri); file:// URI from the path', evidence='SRC Editor.java:315-325')
e('Editor.resolveContent', 'FileUtils.<clinit>', 'CALL', 'First use of class FileUtils in this process', guard='FileUtils not initialised yet', evidence='SRC Editor.java:317')
e('Editor.setListeners', 'Editor$1.<init>', 'CALL', 'textView.addTextChangedListener(new TextWatcher() {...})', evidence='SRC Editor.java:141-147')
for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
    e('Editor.setListeners', 'Editor$1.' + cb, 'REGISTER', 'TextWatcher (%s)' % cb, evidence='SRC Editor.java:146-168')
for lam, trig, ln in (('lambda$setListeners$0', 'textView.setOnLongClickListener', '172-177'), ('lambda$setListeners$1', 'accept.setOnClickListener', '183-199'),
                      ('lambda$setListeners$2', 'accept.setOnLongClickListener', '202-207')):
    e('Editor.setListeners', 'Editor.' + lam, 'REGISTER', trig, evidence='SRC Editor.java:' + ln)

# ---------------------------------------------------------------- home-screen widget (DiaryWidgetProvider, DiaryWidgetUpdate)
W_ADD_GUI = ['Home screen: long-press an empty spot -> Widgets -> drag the Diary widget onto the screen']
e('S_ENTRY', 'DiaryWidgetProvider.<init>@ADD', 'ENTRY', 'A Diary widget is placed: AppWidgetService sends APPWIDGET_ENABLED and APPWIDGET_UPDATE (explicit component) for the new id',
  gui=W_ADD_GUI, evidence=F_WIDGET_BIND + '; INFERRED Launcher3 binds the id when the widget is dropped (another app, its source was not read); SRC AndroidManifest.xml:108-117; res/xml/widget.xml',
  note='Outside the app package: tools confined to the package cannot place a widget. Launcher3 also sets the size right after (OPTIONS_CHANGED, see @RESIZE)')
WIDGET_CTX = {'ADD': 'APPWIDGET_UPDATE for the new widget', 'APP': "Diary's own APPWIDGET_UPDATE after a save", 'BUTTON': 'APPWIDGET_UPDATE from DiaryWidgetUpdate (◀ / ▶ / ⌄)',
              'PERIODIC': 'periodic APPWIDGET_UPDATE (updatePeriodMillis 3600000)', 'RESIZE': 'APPWIDGET_OPTIONS_CHANGED after a resize', 'DELETED': 'APPWIDGET_DELETED after removal'}
for c, what in WIDGET_CTX.items():
    e('DiaryWidgetProvider.<init>@' + c, 'DiaryWidgetProvider.onReceive@' + c, 'LIFECYCLE', 'The system instantiates the manifest receiver and calls onReceive (%s)' % what,
      reads=['pref:pref_folder', 'pref:pref_markdown', 'intent:org.billthefarmer.diary.ENTRY'], writes=['pref:pref_widget_entry'], evidence='SRC DiaryWidgetProvider.java:75-96')
for c in ('ADD', 'BUTTON', 'PERIODIC'):
    e('DiaryWidgetProvider.onReceive@' + c, 'DiaryWidgetProvider.onUpdate', 'FRAMEWORK', 'super.onReceive: APPWIDGET_UPDATE with a non-empty id list -> onUpdate',
      guard='at least one Diary widget placed', evidence=F_WIDGET_UPDATE + '; SRC DiaryWidgetProvider.java:95')
e('DiaryWidgetProvider.onReceive@APP', 'DiaryWidgetProvider.onUpdate', 'FRAMEWORK', 'super.onReceive: the ids sent by Diary.updateWidgets are non-empty only with a placed widget',
  guard='at least one Diary widget placed', needs_state=NS_WIDGET,
  evidence=F_WIDGET_UPDATE + '; SRC Diary.java:2361-2367')
e('DiaryWidgetProvider.onReceive@RESIZE', 'DiaryWidgetProvider.onAppWidgetOptionsChanged', 'FRAMEWORK', 'super.onReceive: APPWIDGET_OPTIONS_CHANGED -> onAppWidgetOptionsChanged',
  evidence=F_WIDGET_OPTIONS + '; ' + F_WIDGET_OPTS_SVC[len(FWS):])
e('DiaryWidgetProvider.onReceive@DELETED', 'S_ENTRY', 'ENTERS', 'super.onReceive: APPWIDGET_DELETED -> onDeleted (not overridden): the widget is gone',
  evidence=F_WIDGET_DELETE + '; FW-SRC core/java/android/appwidget/AppWidgetProvider.java:68-73')
e('DiaryWidgetProvider.onAppWidgetOptionsChanged', 'DiaryWidgetProvider.onUpdate', 'CALL', 'onUpdate(context, manager, {appWidgetId}) (options ignored)', evidence='SRC DiaryWidgetProvider.java:100-108')
e('DiaryWidgetProvider.onUpdate', 'DiaryWidgetProvider.getText', 'CALL', 'text = getText(context): the entry of the widget date (commonmark to HTML when markdown)', evidence='SRC DiaryWidgetProvider.java:117-121')
for dst, ln in (('Diary.<init>@WIDGET', '129-141, 176'), ('DiaryWidgetUpdate.<init>@PREV', '143-153, 177'), ('DiaryWidgetUpdate.<init>@NEXT', '154-164, 178'),
                ('DiaryWidgetUpdate.<init>@TODAY', '165-173, 179')):
    e('DiaryWidgetProvider.onUpdate', dst, 'REGISTER', 'views.setOnClickPendingIntent(...) for this part of the widget', evidence='SRC DiaryWidgetProvider.java:' + ln)
e('DiaryWidgetProvider.onUpdate', 'S_HOME_WIDGET', 'ENTERS', 'appWidgetManager.updateAppWidget(ids, views): date header and entry text shown', evidence='SRC DiaryWidgetProvider.java:181-185')
e('DiaryWidgetProvider.getText', 'Diary.read', 'CALL', 'Diary.read(getFile(entry))', reads=['file:<folder>/YYYY/MM/DD.(txt|md)'], evidence='SRC DiaryWidgetProvider.java:190-193')
e('DiaryWidgetProvider.getText', 'Diary.<clinit>', 'CALL', 'First use of class Diary in a widget-only process', guard='class Diary not initialised yet', evidence='SRC DiaryWidgetProvider.java:193')
e('DiaryWidgetProvider.getText', 'DiaryWidgetProvider.getFile(Calendar)', 'CALL', 'getFile(entry)', evidence='SRC DiaryWidgetProvider.java:193')
e('DiaryWidgetProvider.getFile(Calendar)', 'DiaryWidgetProvider.getDay', 'CALL', 'getDay(y, m, d)', evidence='SRC DiaryWidgetProvider.java:257-261')
e('DiaryWidgetProvider.getDay', 'DiaryWidgetProvider.getMonth', 'CALL', 'getMonth(y, m); DD.txt or DD.md', evidence='SRC DiaryWidgetProvider.java:239-253')
e('DiaryWidgetProvider.getMonth', 'DiaryWidgetProvider.getYear', 'CALL', 'new File(getYear(y), MM)', evidence='SRC DiaryWidgetProvider.java:231-235')
e('DiaryWidgetProvider.getYear', 'DiaryWidgetProvider.getHome', 'CALL', 'new File(getHome(), YYYY)', evidence='SRC DiaryWidgetProvider.java:223-227')
e('S_HOME_WIDGET', 'Diary.<init>@WIDGET', 'GUI', 'Tap the widget body: Diary opens at the widget date',
  gui=['Tap the entry text (or the date) on the widget'], evidence='SRC DiaryWidgetProvider.java:129-141, 176; INFERRED a PendingIntent started from the launcher gets NEW_TASK (another app, its source was not read); with Diary already running a new Diary instance is put on top of its task (different intent)')
for c, icon, ln in (('PREV', '◀', '143-153, 177'), ('NEXT', '▶', '154-164, 178'), ('TODAY', '⌄ (today)', '165-173, 179')):
    e('S_HOME_WIDGET', 'DiaryWidgetUpdate.<init>@' + c, 'GUI', 'Tap the %s icon on the widget: the invisible DiaryWidgetUpdate activity starts' % icon,
      gui=['Tap the %s icon on the widget' % icon], evidence='SRC DiaryWidgetProvider.java:' + ln + '; AndroidManifest.xml:104-106 (Theme.NoDisplay)')
e('S_HOME_WIDGET', 'DiaryWidgetProvider.<init>@RESIZE', 'GUI', 'Resize the widget: the launcher updates its options', gui=['Long-press the widget and drag a resize handle'],
  evidence=F_WIDGET_OPTS_SVC + '; INFERRED Launcher3 calls updateAppWidgetOptions after a resize (another app, its source was not read); SRC res/xml/widget.xml:27-29 (resizeMode)')
e('S_HOME_WIDGET', 'DiaryWidgetProvider.<init>@DELETED', 'GUI', 'Remove the widget', gui=['Long-press the widget and drag it to Remove'],
  evidence=F_WIDGET_DELETE + '; INFERRED Launcher3 deletes the widget id (another app, its source was not read)')
e('S_HOME_WIDGET', 'DiaryWidgetProvider.<init>@PERIODIC', 'SYSTEM', 'Periodic update (updatePeriodMillis = 3600000)', gui=['Wait up to an hour'],
  evidence=F_WIDGET_PERIODIC + '; SRC res/xml/widget.xml:27')
for c in ('PREV', 'NEXT', 'TODAY'):
    u = 'DiaryWidgetUpdate.onCreate@' + c
    e('DiaryWidgetUpdate.<init>@' + c, u, 'LIFECYCLE', 'The system instantiates DiaryWidgetUpdate (Theme.NoDisplay), then onCreate', reads=['pref:pref_folder', 'pref:pref_widget_entry'],
      evidence='SRC DiaryWidgetUpdate.java:50-75')
    e(u, 'DiaryWidgetProvider.<init>@BUTTON', 'INTENT', 'sendBroadcast(APPWIDGET_UPDATE, ids, ENTRY = new date): the provider redraws the widget', writes=['intent:org.billthefarmer.diary.ENTRY'],
      evidence=F_APPWIDGET_PKG + '; SRC DiaryWidgetUpdate.java:107-118')
    e(u, 'S_HOME_WIDGET', 'ENTERS', 'finish(): the invisible activity closes', evidence='SRC DiaryWidgetUpdate.java:123')
    e(u, 'Diary.onResume', 'SYSTEM', 'The NEW_TASK start joins the existing Diary task, which comes to the front when DiaryWidgetUpdate finishes',
      needs_state=NS_TASK,
      evidence=FWS + 'services/core/java/com/android/server/am/ActivityStarter.java:1496-1520 (a NEW_TASK start without MULTIPLE_TASK looks for an existing task with findTaskLocked), '
      '1036-1050 (a found task becomes the task of the new activity), 1754-1760 (started into an existing task without RESET_TASK_IF_NEEDED, the activity is placed on top of it), '
      '1565-1580, 1603-1605 (a found task that is not in front is brought to the front); INFERRED that findTaskLocked picks the Diary task by its affinity '
      '(the matching code is in ActivityStackSupervisor, not held) and that Diary then resumes when DiaryWidgetUpdate finishes (not checked)',
      note='Hazard candidate 11 (README)')
e('DiaryWidgetUpdate.onCreate@PREV', 'DiaryWidgetUpdate.getPrevEntry', 'CALL', 'PREV: getPrevEntry(stored widget date); none -> keep the date', evidence='SRC DiaryWidgetUpdate.java:82-92')
e('DiaryWidgetUpdate.onCreate@NEXT', 'DiaryWidgetUpdate.getNextEntry', 'CALL', 'NEXT: getNextEntry(stored widget date); none -> today', evidence='SRC DiaryWidgetUpdate.java:93-103')
for side, lines in (('Prev', ('195-205', '181-188', '168-175', '155-162')), ('Next', ('251-261', '237-244', '224-231', '211-218'))):
    lo = side.lower()
    W = 'DiaryWidgetUpdate.'
    e(W + 'get%sEntry' % side, W + lo + 'Day', 'CALL', '%sDay(year, month, day)' % lo, evidence='SRC DiaryWidgetUpdate.java:' + lines[0])
    e(W + 'get%sEntry' % side, W + lo + 'Month', 'CALL', 'No day found: %sMonth(year, month), then recursion' % lo, guard='no matching day in this month',
      evidence='SRC DiaryWidgetUpdate.java:' + lines[0])
    e(W + 'get%sEntry' % side, W + lo + 'Year', 'CALL', 'No month found: %sYear(year), then recursion' % lo, guard='no matching month in this year',
      evidence='SRC DiaryWidgetUpdate.java:' + lines[0])
    e(W + lo + 'Day', W + 'getMonth', 'CALL', 'getMonth(year, month)', evidence='SRC DiaryWidgetUpdate.java:' + lines[1])
    e(W + lo + 'Day', 'Diary.listDays', 'CALL', 'Diary.listDays(monthDir)', evidence='SRC DiaryWidgetUpdate.java:' + lines[1])
    e(W + lo + 'Day', 'Diary.dayValue', 'CALL', 'Diary.dayValue(file) for each day file', guard='the month folder has day files', evidence='SRC DiaryWidgetUpdate.java:' + lines[1])
    e(W + lo + 'Day', 'Diary.<clinit>', 'CALL', 'First use of class Diary in a widget-only process', guard='class Diary not initialised yet', evidence='SRC DiaryWidgetUpdate.java:' + lines[1])
    e(W + lo + 'Month', W + 'getYear', 'CALL', 'getYear(year)', evidence='SRC DiaryWidgetUpdate.java:' + lines[2])
    e(W + lo + 'Month', 'Diary.listMonths', 'CALL', 'Diary.listMonths(yearDir)', evidence='SRC DiaryWidgetUpdate.java:' + lines[2])
    e(W + lo + 'Month', 'Diary.monthValue', 'CALL', 'Diary.monthValue(dir) for each month folder', guard='the year folder has month folders', evidence='SRC DiaryWidgetUpdate.java:' + lines[2])
    e(W + lo + 'Year', W + 'getHome', 'CALL', 'getHome()', evidence='SRC DiaryWidgetUpdate.java:' + lines[3])
    e(W + lo + 'Year', 'Diary.listYears', 'CALL', 'Diary.listYears(home)', evidence='SRC DiaryWidgetUpdate.java:' + lines[3])
    e(W + lo + 'Year', 'Diary.yearValue', 'CALL', 'Diary.yearValue(dir) for each year folder', guard='the diary folder has year folders', evidence='SRC DiaryWidgetUpdate.java:' + lines[3])
e('DiaryWidgetUpdate.getMonth', 'DiaryWidgetUpdate.getYear', 'CALL', 'new File(getYear(year), MM)', evidence='SRC DiaryWidgetUpdate.java:145-149')
e('DiaryWidgetUpdate.getYear', 'DiaryWidgetUpdate.getHome', 'CALL', 'new File(getHome(), YYYY)', evidence='SRC DiaryWidgetUpdate.java:137-141')


# ---------------------------------------------------------------- schema 2 (see handoff/SCHEMA_V2.md)
import re

# DEAD and FRAMEWORK_ONLY become UNREACHABLE: (kind, reason, first app source reference, how confirmed). The reasons are Kiro's
# (each lists every call site and the search scope); the kind and the reference were added.
_APP_FILES = ('Diary.java', 'FileUtils.java', 'Editor.java', 'DiaryWidgetProvider.java', 'DiaryWidgetUpdate.java', 'SettingsFragment.java',
              'QueryHandler.java', 'Settings.java', 'DatePickerPreference.java', 'AboutPreference.java', 'FileProvider.java')
_FW_NEVER_CALLS = {'FileProvider.delete': 'FileProvider.java:521', 'FileProvider.insert': 'FileProvider.java:496',
                   'FileProvider.update': 'FileProvider.java:505', 'DatePickerPreference.onGetDefaultValue': 'DatePickerPreference.java:72'}


def _first_app_ref(text):
    for m in re.finditer(r'\b([A-Z][A-Za-z]+\.java:\d+(?:-\d+)?)', text):
        if m.group(1).split(':')[0] in _APP_FILES:
            return m.group(1)
    return None


UNREACHABLE = {}
for _m, _t in list(DEAD.items()) + list(FRAMEWORK_ONLY.items()):
    if _m in _FW_NEVER_CALLS:
        UNREACHABLE[_m] = ('framework_never_calls', _t, _FW_NEVER_CALLS[_m], 'SOURCE')
    else:
        UNREACHABLE[_m] = ('no_trigger_in_app', _t, _first_app_ref(_t), 'SOURCE')
DEAD, FRAMEWORK_ONLY = {}, {}

ENV_WIDGET = 'a Diary widget is placed on the home screen through the launcher (another app, a user action outside Diary)'
ENV_ROTATE = 'the device is rotated (orientation change)'
ENV_OTHER_APP = 'another app takes part: it sends the intent, or it is the share sheet, document picker or creator, or print service'

ENV_KINDS_OF = {ENV_NOPERM: ['permission'], ENV_PERM: ['permission'], ENV_24H: ['other'], ENV_CAL_ACCOUNT: ['other_app'],
                ENV_CAL_EVENT: ['other_app'], ENV_IO_ERROR: ['other'], ENV_NO_PATH: ['other_app'], ENV_WIDGET: ['other_app'],
                ENV_ROTATE: ['hardware'], ENV_OTHER_APP: ['other_app']}
STATE_KINDS_OF = {NS_INDEX: ['settings'], NS_THEME: ['settings', 'session'], NS_DATEPREF: ['settings'], NS_TASK: ['session'],
                  NS_SAMENAME: ['file'], NS_EDITMODE: ['session'], NS_PLAIN: ['settings'], NS_CUSTOM_OFF: ['settings'],
                  NS_TEMPLATE: ['settings'], NS_TEMPLATE_PLAIN: ['settings'], NS_COPY: ['settings'], NS_INDEX_PAGE: ['settings'],
                  NS_BAD_INDEX_TEMPLATE: ['settings'], NS_BAD_TEMPLATE_PAGE: ['data'], NS_HAVEMEDIA: ['session']}

STATE_KINDS_OF['the entry holds an unsaved "@ HH:MM title" line that was pasted, received or written outside Diary (the help text has none at a line start; saving turns it into "@:")'] = ['data']
STATE_KINDS_OF["Copy images was ticked in Settings on an earlier visit (persisted), and an image with the same file name was already copied into this month's folder"] = ['settings', 'file']

# Path reading (step 4): guards that need state which the derived route does not build itself, now structured as STATE
NS_ENTRYSTACK = ('an earlier navigation in this Diary instance left a previous entry on the entry stack (Go to date and OK, a diary link, '
                 'Previous or Next entry, or a swipe; Today and the index clear it)')
NS_CHANGED = ('the entry has unsaved changes (text typed or inserted earlier in this Diary instance, or the help text copied into the '
              'empty page on the first start)')
NS_ENTRIES = 'the diary folder already holds entry files (entries saved on earlier visits)'
NS_MATCH = 'a saved entry contains the text that is searched for'
NS_EMPTYDAY = 'the shown day has no entry text yet (a day without an entry; the help text of the first start is not empty)'
STATE_KINDS_OF[NS_ENTRYSTACK] = ['session']
STATE_KINDS_OF[NS_CHANGED] = ['session']
STATE_KINDS_OF[NS_ENTRIES] = ['data']
STATE_KINDS_OF[NS_MATCH] = ['data']
STATE_KINDS_OF[NS_EMPTYDAY] = ['data']
_STATE_BY_GUARD = {
    'entry and entryStack not empty': NS_ENTRYSTACK, 'entryStack not empty': NS_ENTRYSTACK, 'entryStack not empty (markdown on)': NS_ENTRYSTACK,
    'Up arrow shown: entry and the entry stack is not empty (onPageFinished 862-868)': NS_ENTRYSTACK,
    'at least 2 files': NS_ENTRIES, 'getFile().lastModified() > saved': NS_ENTRIES, 'the month folder has day files': NS_ENTRIES,
    'the year folder has month folders': NS_ENTRIES, 'the diary folder has year folders': NS_ENTRIES,
    'the folder exists and is not empty': NS_ENTRIES, 'at least one entry file': NS_ENTRIES,
    'an entry contains the query': NS_MATCH, 'matches not empty': NS_MATCH, 'at least one match': NS_MATCH,
    'the shown entry is empty (2696-2697)': NS_EMPTYDAY, 'the shown entry is empty (2696-2697) and markdown on': NS_EMPTYDAY,
    'the entry was empty and the template page is readable': NS_EMPTYDAY}

_OTHER_PAGES = ('S_CHOOSER_SHARE', 'S_MEDIA_PICKER', 'S_DOC_CREATE', 'S_PRINT')
_SENT_BY_OTHER_APP = ('Diary.<init>@SEND_TEXT', 'Diary.<init>@SEND_IMAGE', 'Diary.<init>@SEND_MULTI', 'Diary.<init>@GEO', 'Editor.<init>@EXTERNAL')


def EDIT(x):
    """Gates that v1 kept as a STATE text or only as a guard, as structured ENV."""
    src, dst = x['src'].split('@')[0], x['dst'].split('@')[0]
    if not x['needs_state']:                    # path reading: state that the derived route does not build itself
        x['needs_state'] = _STATE_BY_GUARD.get(x['guard'] or '')
    if not x['needs_state'] and (x['guard'] or '') in ('changed', 'visible only while changed (632)') and \
            not any(k in x['src'] for k in ('CHANGED', '@EVENT', '@PLAIN', 'S_DIARY_PLAIN', 'Diary.cancel')):
        x['needs_state'] = NS_CHANGED           # the page or node of the edge does not itself mean that the text was changed
    if x['needs_state'] == NS_HAVEMEDIA and not x['env']:   # haveMedia is set only in an instance that another app started
        x['env'] = ENV_OTHER_APP
    if x['needs_state'] == NS_WIDGET:           # a widget is placed by the launcher: another app, so ENV, not STATE
        x['needs_state'], x['env'] = None, ENV_WIDGET
    if x['env']:
        return
    if (x['kind'] == 'ENTRY' and x['dst'].startswith('DiaryWidgetProvider.<init>@ADD')) or \
            (src == 'DiaryWidgetProvider.onReceive' and dst == 'DiaryWidgetProvider.onUpdate'):
        x['env'] = ENV_WIDGET
    elif 'orientation change' in (x['guard'] or ''):
        x['env'] = ENV_ROTATE
    elif (x['kind'] == 'ENTRY' and x['dst'] in _SENT_BY_OTHER_APP) or src in _OTHER_PAGES:
        x['env'] = ENV_OTHER_APP


def CLASSIFY(x):
    """Edge classes that differ from the default of their kind (see SCHEMA_V2.md)."""
    src, dst = x['src'].split('@')[0], x['dst'].split('@')[0]
    if x['kind'] == 'INTENT' and dst == 'DiaryWidgetProvider.<init>':
        return ('non_standard', 'implicit broadcast: Intent(ACTION_APPWIDGET_UPDATE) without a component, resolved by action name to the manifest receiver')
    if dst in ('AboutPreference.<init>', 'DatePickerPreference.<init>'):
        return ('non_standard', 'class named in res/xml/preferences.xml, constructed by the framework through reflection (GenericInflater.createItem)')
    if dst.startswith('FileProvider.') and dst not in ('FileProvider.<clinit>', 'FileProvider.<init>', 'FileProvider.attachInfo', 'FileProvider.onCreate') \
            and (src in _OTHER_PAGES or src.startswith('FileUtils.getDataColumn') or src == 'Diary.addMedia(Intent)'):
        return ('non_standard', 'content URI resolved to the provider by its authority (ContentResolver); nothing in the app calls the provider method')
    if x['kind'] == 'ENTRY' and dst.endswith('.<clinit>'):
        return ('standard', 'JVM class initialisation')
    return None


STRICT = True
