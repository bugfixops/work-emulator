import csv, glob, json, re, sys, collections
sys.path.insert(0, 'tools')
import build_graph as b

SCR = '<scratchpad>'
g = json.load(open(glob.glob('graphs/Omni-Notes/out/*_trigger_graph.json')[0]))
E = {x['id']: x for x in g['edges']}
rows = {r['method']: r for r in csv.DictReader(open('graphs/Omni-Notes/out/methods.csv', encoding='utf-8'))}
old = json.load(open(SCR + '/omni_old/out/omni-old_trigger_graph.json'))
oldrows = {r['method']: r for r in csv.DictReader(open(SCR + '/omni_old/out/methods.csv', encoding='utf-8'))}
OE = {x['id']: x for x in old['edges']}

LIBS = ' Steps that run through androidx / MaterialDialogs / ButterKnife / EventBus / RxJava / SmartLocation rest on INFERRED claims (library source not read).'
SC = ('ERROR FOUND: the first-graph route reached the list through the shortcut edges "MainActivity.onResume -> ListFragment.onResume / MainActivity.init / the list page", taken right after the process starts. '
      'On a cold start isPasswordAccepted is false, so onResume calls checkPassword, which calls init(), which adds the ListFragment once (MainActivity.java:111-118, 138-156, 178-182); the shortcuts skip those steps and are only valid after an earlier resume. '
      'Fixed: the shortcut edges now carry the STATE "MainActivity was resumed before in this process" and the best route uses the explicit chain onResume -> checkPassword -> init -> ListFragment.')


def route_edges(m, graph_rows, graph_edges):
    return [graph_edges[i] for i in graph_rows[m]['route_edge_ids'].split() if i in graph_edges]


SCPAIRS = {('MainActivity.onResume', 'ListFragment.onResume'), ('MainActivity.onResume', 'MainActivity.init')}


def had_shortcut(m):
    for x in route_edges(m, oldrows, OE):
        if (x['src'], x['dst']) in SCPAIRS or (x['src'] == 'MainActivity.onResume' and x['dst'].startswith('S_')):
            return True
    return False


def has_edge(src, dst, **kw):
    """assert the final graph carries a gate that a note below talks about"""
    for x in g['edges']:
        if x['src'] == src and x['dst'] == dst:
            for k, v in kw.items():
                if v not in (x.get(k) or ''):
                    break
            else:
                return x['id']
    raise AssertionError((src, dst, kw))


P = {}
def p(m, res, ref, note, sc=True):
    if sc:
        assert had_shortcut(m), m
        note = SC + ' ' + note
    P[m] = (res, ref, note)


# ---- the sample of 30 (seed 20261025), same order as the sample list
has_edge('GeocodeHelper.lambda$getCoordinatesFromAddress$1', 'DetailFragment.onCoordinatesResolved', guard='at least one result')
p('DetailFragment.onCoordinatesResolved', 'fixed', 'GeocodeHelper.java:164-170; DetailFragment.java:2195-2228',
  'ERROR FOUND (also): the geocoder callback calls onCoordinatesResolved only when the result list is not empty (GeocodeHelper.java:166-168), and the location dialog that leads there opens only when internet is available (DetailFragment.java:2204-2209), after a location fix (GeocodeHelper.java:86-95) and with the location permission (DetailFragment.java:733-737). '
  'Fixed: guard on the callback edge, ENV network / hardware / permission on the route. Steps read: FAB long-press (Fab.java:69-76) -> new note -> Attachment -> Location (DetailFragment.java:2267-2320) -> displayLocationDialog -> getLocation -> dialog -> typed address (2220-2228) -> getCoordinatesFromAddress.' + LIBS)
has_edge('SettingsFragment.onActivityResult@SPRINGPAD', 'DataBackupIntentService.onHandleIntent@SPRINGPAD', evidence='IntentService.java')
p('SpringImportHelper.lambda$importDataFromSpringpad$0', 'fixed', 'SettingsFragment.java:240-255,683-691; DataBackupIntentService.java:75-87',
  'ERROR FOUND (also): the edge into DataBackupIntentService.onHandleIntent cited AsyncTask.java, but the service is an IntentService (IntentService.java:70-78, 112-132: onStart queues a message, the ServiceHandler on a HandlerThread calls onHandleIntent). Fixed: the citation is the IntentService source. '
  'Steps read: Settings > Data > Sync > Import from Springpad (SettingsFragment.java:240-255, picker ENV other_app) -> onActivityResult (683-691) -> startService -> action switch (DataBackupIntentService.java:75-87). That importDataFromSpringpad calls the lambda is INFERRED (stream / Rx library source not read).' + LIBS)
has_edge('SettingsFragment.onActivityResult@SPRINGPAD', 'FileHelper.getPath')
has_edge('FileHelper.getPath', 'FileHelper.isMediaDocument', env='picker app')
p('FileHelper.isMediaDocument', 'fixed', 'SettingsFragment.java:684-685; FileHelper.java:55-75',
  'ERROR FOUND (also): the first route went merge -> NotesHelper.addAttachments -> StorageHelper.createAttachmentFromUri -> createExternalStoragePrivateFile -> catch -> FileHelper.getPath, but a merged note holds file:// URIs of its own copies (StorageHelper.java:479-481; NotesHelper.java:70-78), which are not document URIs, so getPath never reaches isMediaDocument that way. '
  'Only a content URI picked in another app does: the Springpad zip (SettingsFragment.java:684-685) or, after an I/O failure, an attachment picked in AttachmentTask (StorageHelper.java:118-124). '
  'Fixed: the AttachmentTask path got its own context (@PICK) for the catch fallback, the merge path no longer leads to getPath; getPath -> isMediaDocument needs a picker app that returns a document URI of another provider (ENV other_app). The new route is Settings > Data > Sync > Import from Springpad -> picker -> onActivityResult -> getPath (FileHelper.java:55-75).' + LIBS)
has_edge('GeocodeHelper$1.onError@AUTO', 'DetailFragment.onLocationUnavailable')
p('DetailFragment.onLocationUnavailable', 'fixed', 'DetailFragment.java:699-702,733-736; GeocodeHelper.java:91,104-107',
  'ERROR FOUND (also): the location callbacks had no gates. onError arrives when no fix comes within the 2 s timeout (GeocodeHelper.java:91, 104-107), the callback runs only with the location permission (DetailFragment.java:733-736), and the automatic location needs the "auto location" preference (default off) and a new note (699-702). Fixed: ENV hardware + permission and STATE settings on the route. '
  'The route builds the editor fragment again with the edge swipe (DetailFragment.java:1903-1953) -> onActivityCreated -> init -> initViews -> initViewLocation (629); the FAB path through editNote -> switchToDetail reaches the same constructor (ListFragment.java:930-950, MainActivity.java:439-450).' + LIBS)
p('DbHelper.deleteNote(long,boolean)', 'wrong', 'DetailFragment.java:1583-1587,1612-1616; ListFragment.java:847-880',
  'ERROR FOUND, NOT FIXED: after the shortcut is removed the route is: FAB-created editor -> change the note -> Back -> saveNote -> onNoteSaved -> deleteMergedNotes (DetailFragment.java:1616) -> NoteProcessorDelete -> DbHelper.deleteNote, with the STATE "the open note is the result of Merge". '
  'deleteMergedNotes does something only when the editor was opened by the Merge action of the list (mergedNotesIds is set from the intent), which the page node of a FAB-created editor cannot express: a STATE cannot say how an editor was opened. The label REACHABLE is right (Merge is a real path); the route is not consistent. '
  'Modelling limit: it would need its own editor context (@MERGE) with its own Back / save chain.' + LIBS)
p('Attachment.<init>(BaseAttachment)', 'fixed', 'DataBackupIntentService.java:75-87,121-137; BackupHelper.java:145-176; Note.java:152-159',
  'ERROR FOUND (also): the first route took the legacy import (onHandleIntent@LEGACY) and then importData -> BackupHelper.importNotes, but importData calls importNotes only when the action is the normal import and importDB when it is the legacy one (DataBackupIntentService.java:123, 131-135). '
  'Fixed: importData now runs per action (@IMPORT / @LEGACY) with the matching guards; the route is Settings > Data > Sync > Import -> backup list -> Confirm (SettingsFragment.java:159-166, 573-591) -> importData@IMPORT -> importNotes -> importNote -> getImportNote -> Note.buildFromJson -> Attachment (Note.java:152-159), '
  'STATE a backup folder with attachments (file), ENV storage permission. importNotes needs a file named <13 digits>.json (BackupHelper.java:147) and getImportNote a non-empty file (175): both guards added.' + LIBS)
has_edge('SnoozeActivity.setNextRecurrentReminder', 'RecurrenceHelper.nextReminderFromRecurrenceRule(long,String)', guard='recurrence rule')
p('RecurrenceHelper.nextReminderFromRecurrenceRule(long,long,String)', 'fixed', 'SnoozeActivity.java:55-60,138-150; ListFragment.java:893-899',
  'ERROR FOUND (also): setNextRecurrentReminder calls nextReminderFromRecurrenceRule only for a note with a recurrence rule (SnoozeActivity.java:55-60): guard and STATE "a recurrence rule was chosen in the reminder picker" added. '
  'Steps read: select a note -> Add reminder in the action bar (ListFragment.java:451-465, 893-899) -> SnoozeActivity from the list (82-93, 116-119) -> picker -> OK -> onRecurrenceReminderPicked (138-150). This route passes the postpone branch of SnoozeActivity, which may crash on API 27 (hazard in the notes); the method is also reached without it: the alarm fires -> AlarmReceiver.onReceive -> SnoozeActivity.setNextRecurrentReminder (AlarmReceiver.java:59; ENV time, a note with a recurrence rule), so the label does not depend on that branch.' + LIBS)
has_edge('BackupHelper.exportAttachments(NotificationsHelper,File,List,List)', 'LogDelegate.w(String)', guard='missing')
p('LogDelegate.w(String)', 'fixed', 'BackupHelper.java:112-121',
  'ERROR FOUND (also): LogDelegate.w(String) is called in the catch block for a missing attachment file (BackupHelper.java:117-118); the edge had no gate. Fixed: guard, ENV exception (openInputStream throws FileNotFoundException) and STATE "a note has an attachment". '
  'Steps read: Settings > Data > Sync > Export (SettingsFragment.java:141-157, 625-669) -> backup name -> Confirm -> startBackupService -> DataBackupIntentService (75-83, 93-110) -> exportAttachments (96-99, 104-121).' + LIBS)
p('Tag$1.<init>', 'fixed', 'DbHelper.java:685-706; Tag.java:65-70',
  'Steps read: search icon (ListFragment.java:688-735) -> tags icon visible while the search view has focus (775) -> filterByTags (805-845, 1803) -> TagsHelper.getAllTags -> DbHelper.getTags -> new Tag per #tag found in a note (DbHelper.java:696-706; STATE: a note contains a #tag) -> Tag class initialiser builds the CREATOR (Tag.java:65). The class initialiser step is INFERRED (JVM rule).' + LIBS)
p('ListFragment.lambda$null$11', 'fixed', 'ListFragment.java:1352-1364; BaseActivity.java:115-134',
  'Steps read: drawer -> Trash entry (shown when a trashed note exists, MainMenuTask.java:73-84) -> long-press a note -> Delete in the action bar -> confirmation OK (ListFragment.java:1352-1361) -> requestPassword: no locked note and no password-on-access preference means the validator runs at once with SUCCEED (BaseActivity.java:115-134) -> lambda$null$11.' + LIBS)
p('CategoryBaseAdapter.isSelected', 'fixed', 'CategoryBaseAdapter.java:100-103',
  'Steps read: list load (ListFragment.initNotesList -> NoteLoaderTask) -> NotesLoadedEvent -> drawer refreshMenus (NavigationDrawerFragment.java:120-131, 205) -> CategoryMenuTask -> the category list binds its rows -> getView calls isSelected for every row (CategoryBaseAdapter.java:103); STATE at least one category.' + LIBS)
has_edge('CountFactory.getCounterInstanceByLocale', 'IdeogramsWordCounter.<init>', env='ja_JP')
p('IdeogramsWordCounter.<init>', 'fixed', 'CountFactory.java:28-44; LanguageHelper.java:94-104',
  'ERROR FOUND (also): the edge said the ideogram counter is used for "Chinese, Japanese or Korean"; the code picks it only for the locales ja_JP, zh_CN and zh_TW (CountFactory.java:33-40) and reads the locale from the Application context (LanguageHelper.java:94-104), i.e. the device locale. Fixed: the ENV text names the three locales. '
  'Steps read: new note -> Info in the toolbar (DetailFragment.java:1074-1141) -> NoteInfosActivity.populateViews -> getNoteInfos -> getChars -> CountFactory.getWordCounter.' + LIBS)
has_edge('ONDashClockExtension.onUpdateData', 'ONDashClockExtension.getNoteTitle', guard='reminder')
has_edge('DetailFragment.onNoteSaved', 'BaseActivity.notifyAppWidgets')
p('TextHelper.getAlternativeTitle', 'fixed', 'ONDashClockExtension.java:65-113,122-132; DetailFragment.java:1612-1613',
  'ERROR FOUND (also, two): (1) getNoteTitle is called only for notes that have a reminder due today or within 24 hours (ONDashClockExtension.java:79-96, 122-132); the edge had no gate, now a guard and the STATE "a note has a reminder due today or within 24 hours". '
  '(2) the first route went through Discard changes -> BaseActivity.notifyAppWidgets, which runs only for a note that already exists (DetailFragment.java:1490-1492), but the route used a new editor. Fixed: Discard changes is split into a new-note chain and an existing-note chain (@EXIST); the new route uses the save path, whose onNoteSaved calls notifyAppWidgets unconditionally (DetailFragment.java:1613). '
  'The broadcast reaches the DashClock receiver only when the extension is active (ENV other_app; LocalBroadcastManager is INFERRED).' + LIBS)
p('DataBackupIntentService.deleteData', 'fixed', 'SettingsFragment.java:159-166,595-615; DataBackupIntentService.java:75-83',
  'Steps read: Settings > Data > Sync > Import (SettingsFragment.java:159-166, 539-622: the list of backup folders) -> long-press a backup (595) -> confirm delete (601-615) -> startService -> action switch (DataBackupIntentService.java:81-82); ENV storage permission, STATE a backup folder exists.' + LIBS)
p('DetailFragment.removeAttachment(Attachment)', 'fixed', 'DetailFragment.java:1956-1962; AttachmentTask.java:62-68',
  'ERROR FOUND (also): the first graph had a route to removeAttachment(Attachment) through onAttachingFileErrorOccurred. That method calls it only inside `if (noteTmp.getAttachmentsList().contains(mAttachment))` (DetailFragment.java:1956-1962), and its only caller, AttachmentTask.onPostExecute, passes null (AttachmentTask.java:62-68), which no attachment list contains. '
  'Fixed: the method is UNREACHABLE (branch_never_taken); the other overload removeAttachment(int) is the one the attachment popup uses (DetailFragment.java:849). No route remains.', sc=True)
has_edge('AlarmReceiver.createNotification', 'BitmapHelper.getBitmapFromAttachment', guard='attachment')
p('BitmapHelper.getImageBitmap', 'fixed', 'AlarmReceiver.java:120-125; BitmapHelper.java:52-57',
  'ERROR FOUND (also): AlarmReceiver.createNotification calls getBitmapFromAttachment only when the reminded note has an attachment and the first one is not a file attachment (AlarmReceiver.java:120-125), and getBitmapFromAttachment calls getImageBitmap only for a video, image or sketch (BitmapHelper.java:56-57); the first edge had no gate, the second only partly. Fixed: guards and STATE. '
  'Steps read: save a note with a reminder (SaveNoteTask.java:58-65) -> the alarm fires (ENV time) -> AlarmReceiver.onReceive -> createNotification.' + LIBS)
p('UpgradeProcessor.<init>', 'fixed', 'DbHelper.java:191-214; SQLiteOpenHelper.java:326-351',
  'Steps read: list load -> NoteLoaderTask -> DbHelper.getAllNotes -> getNotesActive -> getNotes -> getDatabase -> SQLiteOpenHelper calls onUpgrade when the stored database version is lower (FW-SRC SQLiteOpenHelper.java:326-351; ENV other: an older database is on disk) -> DbHelper.onUpgrade -> UpgradeProcessor.process (DbHelper.java:191-214) -> getInstance -> constructor. '
  'ERROR FOUND (also): the first graph sent getAllNotes with the wrong branch (arguments are not distinguished by the call edge); the loader edge is now getAllNotes@NAV with the Notes-navigation guard (DbHelper.java:333-335).' + LIBS)
has_edge('DateHelper.getFormattedDate', 'DateUtils.prettyTime(Long)', guard='prettified')
p('DateUtils.prettyTime(Long,Locale)', 'fixed', 'DetailFragment.java:638-654; DateHelper.java:112-118; DateUtils.java:186-191',
  'ERROR FOUND (also, two): (1) DateHelper.getFormattedDate calls prettyTime only while the prettified-dates preference is on (DateHelper.java:112-115; default on): guard added. (2) the first route reached getFormattedDate through Trash on a checklist editor opened with the FAB, i.e. a new note, but Trash is visible only for a note that already exists (DetailFragment.java:1019, 1033-1035); Fixed: that edge from the checklist page needs the STATE "the open note already exists". '
  'Steps read: new editor -> edge swipe opens a new editor fragment (DetailFragment.java:1903-1953) -> initViews -> initViewFooter formats the creation and modification dates (638-654; a null timestamp still enters prettyTime, DateUtils.java:191).' + LIBS)
has_edge('CategoryActivity.saveCategory@NEW_DETAIL', 'DbHelper.updateCategory', guard='name field')
p('Category.<init>(Parcel)', 'fixed', 'CategoryActivity.java:135-159; DetailFragment.java:1438-1443',
  'ERROR FOUND (also): saveCategory returns early for an empty name (CategoryActivity.java:138-141), so the result edges need a typed name; they had no gate. Fixed: guard on every edge leaving saveCategory. '
  'Steps read: new note -> Category in the toolbar -> categorize dialog -> "Add category" (DetailFragment.java:1242-1276) -> CategoryActivity -> Save -> setResult (CategoryActivity.java:156-157) -> DetailFragment.onActivityResult reads the Parcelable "category" (1438-1443; Parcel.createFromParcel reads the CREATOR by reflection, Parcel.java:2867-2900).' + LIBS)
p('DbHelper.deleteCategory', 'fixed', 'CategoryActivity.java:162-188; CategoryMenuTask.java:144-157',
  'Steps read: long-press a category in the drawer (CategoryMenuTask.java:144-157; STATE a category exists) -> MainActivity.editTag -> ListFragment.editCategory (1463-1467) -> CategoryActivity -> Delete -> confirmation -> onPositive calls deleteCategory (CategoryActivity.java:170-180).' + LIBS)
has_edge('MainActivity.onBackPressed@SKETCH_DRAWN', 'Attachment.<init>(Uri,String)', evidence='INFERRED')
p('Attachment$1.<init>', 'fixed', 'SketchFragment.java:208-226; DetailFragment.java:385-388',
  'ERROR FOUND (also): the edge from onBackPressed (sketch) to the new Attachment was a compressed step classed explicit; it crosses a fragment transaction, so it is now class standard and cites the INFERRED fragment lifecycle (androidx FragmentManager) next to the source lines. '
  'Steps read: Attachment -> Sketch (DetailFragment.java:2267-2320, 1360-1384) -> draw on the canvas (SketchView.java:165-185) -> Back saves the sketch (MainActivity.java:255-269; guard: at least one stroke, SketchView.java:204-207) -> editor attaches it (385-388) -> Attachment class initialiser builds the CREATOR (Attachment.java:85).' + LIBS)
p('Stats.getCharsMax', 'fixed', 'StatsActivity.java:35-84; settings.xml:111-117',
  'Steps read: drawer -> Settings -> Statistics (res/xml/settings.xml:111-117) -> StatsActivity.onCreate -> initData -> StatsTask (AsyncTask, FW-SRC AsyncTask.java) -> onPostExecute -> populateViews calls getCharsMax (StatsActivity.java:84).' + LIBS)
p('NoteProcessor.afterProcess', 'fixed', 'ListFragment.java:572-575,1688-1715; NoteProcessor.java:40-68',
  'Steps read: trash a note (the undo bar shows, STATE session) -> touch the list: onViewTouchOccurred -> commitPending -> trashNote (ListFragment.java:572-575, 1688-1715) -> NoteProcessorTrash.process -> AsyncTask -> onPostExecute -> afterProcess (NoteProcessor.java:40-68).' + LIBS)

# the seven that never used the shortcut
has_edge('NotificationsHelper.initNotificationChannels', 'NotificationChannels.getChannels', guard='SDK_INT')
has_edge('OmniNotes.onCreate', 'NotificationsHelper.initNotificationChannels', guard='LeakCanary')
p('NotificationChannels.getChannels', 'fixed', 'OmniNotes.java:80-93,104-110; NotificationsHelper.java:55-57',
  'ERROR FOUND: the call in initNotificationChannels is inside `if (SDK_INT > O)` (NotificationsHelper.java:56), true on API 27, and onCreate continues only in the app\'s own process, not in the LeakCanary analyzer process where initLeakCanary() returns true (OmniNotes.java:83-85, 104-110); both guards were missing. Fixed: guards on the edges (the NotificationChannels class initialiser edge also carries the SDK guard).', sc=False)
has_edge('LogDelegate.isFileLoggingEnabled', 'OmniNotes.getSharedPreferences', guard='first logging call')
p('OmniNotes.getSharedPreferences', 'fixed', 'BaseActivity.java:96-100; LogDelegate.java:48-49,92-94',
  'ERROR FOUND (guard missing): isFileLoggingEnabled reads the preference only while the static fileLoggingEnabled is null (LogDelegate.java:93-94), i.e. on the first logging call of the process; the edge had no guard. The route is right (launcher -> MainActivity.onResume -> BaseActivity.onResume -> LogDelegate.d, BaseActivity.java:96-100). '
  'Also fixed on the same method: the edges that follow in the same `if (fileLoggingEnabled)` block (getAppContext, getExternalStoragePublicDir, LogDelegate.java:95-99) now need the file-logging switch turned on in an earlier run (SettingsFragment.java:506-517).', sc=False)
has_edge('LanguageHelper.updateLanguage', 'LanguageHelper.getLocale', needs_state='language preference')
p('LanguageHelper.getLocale', 'fixed', 'LanguageHelper.java:45-60; BaseActivity.java:72-75',
  'ERROR FOUND (guard / state missing): updateLanguage reaches getLocale only when a language is passed in or the language preference is already stored (LanguageHelper.java:50-58); on the first start the first branch runs and getLocale is not called. Fixed: guard and STATE settings ("the language preference is already stored", written by the first start itself).', sc=False)
p('OmniNotes.getAppContext', 'fixed', 'OmniNotes.java:80-93; NotificationChannels.java:34-45; IntroActivity.java:48-51',
  'ERROR FOUND: the first route went MainActivity.onCreate -> IntroActivity.mustRun -> getAppContext, but mustRun is `!OmniNotes.isDebugBuild() && !OmniNotes.getAppContext()...` (IntroActivity.java:48-51) and the standard configuration is the debug build (BuildConfig.BUILD_TYPE "debug", OmniNotes.java:55-57), where the && stops at the first operand. '
  'Fixed: the edge is removed; the route is now onCreate -> initNotificationChannels (SDK guard) -> NotificationChannels class initialiser -> its static list builds NotificationChannel objects with getAppContext (NotificationChannels.java:34-45). The class initialiser step is INFERRED (JVM rule).', sc=False)
p('BaseActivity.onCreate', 'correct', 'MainActivity.java:93-94', 'Launcher -> MainActivity.<init> -> onCreate, whose first statement is super.onCreate (MainActivity.java:94).', sc=False)
p('MainActivity.initUI', 'correct', 'MainActivity.java:101', 'onCreate calls initUI unconditionally (MainActivity.java:101).', sc=False)
p('LanguageHelper.setLocale', 'correct', 'LanguageHelper.java:60; BaseActivity.java:73', 'attachBaseContext calls updateLanguage (BaseActivity.java:73), which ends in setLocale on every branch (LanguageHelper.java:60).', sc=False)

# ---- extra paths read while sampling
p('MediaStoreFactory.<init>', 'fixed', 'FileHelper.java:75-86; SettingsFragment.java:684-685',
  'ERROR FOUND (also): same wrong merge route as FileHelper.isMediaDocument (a merged note holds file:// URIs). Fixed: the route is Springpad import -> picker -> getPath -> `new MediaStoreFactory()` for a document URI of the media provider (FileHelper.java:75-86; ENV other_app: the picker app returns such a URI).' + LIBS)
p('DynamicNavigationLookupTable.<init>', 'fixed', 'MainMenuTask.java:109-126; DynamicNavigationLookupTable.java:47',
  'Steps read: ListFragment.initNotesList -> NoteLoaderTask -> NotesLoadedEvent -> NavigationDrawerFragment.refreshMenus (120-131, 203) -> buildMainMenu -> MainMenuTask -> checkSkippableItem inside the loop over the navigation entries (MainMenuTask.java:109-126) -> getInstance -> constructor.' + LIBS)
p('ListFragment.initNotesList', 'fixed', 'ListFragment.java:246-261,396',
  'Steps read: onActivityCreated -> init -> initNotesList (ListFragment.java:246-261) after the explicit onResume -> checkPassword -> init -> ListFragment chain.' + LIBS)

# ---- UNREACHABLE labels
FIXED_LABELS = {
    'DetailFragment.removeAttachment(Attachment)': 'was REACHABLE in the first graph through onAttachingFileErrorOccurred; that method calls it only for an attachment contained in the list, and its only caller passes null',
    'SettingsFragment.lambda$onResume$16': 'was REACHABLE in the first graph through a GUI edge for the widget-colours preference; the preference "settings_colors_widget" is in no preference XML, so the listener is never registered',
    'BackupHelper.lambda$exportAttachments$0': 'was REACHABLE in the first graph; the only main-code caller of the four-argument exportAttachments passes null, which line 109 turns into an empty list (BackupHelper.java:99, 109, 132-136)',
    'BackupHelper.lambda$exportAttachments$1': 'was REACHABLE in the first graph; same empty listOld as lambda$exportAttachments$0',
    'SystemHelper.closeCloseable': 'was REACHABLE in the first graph; its callers are the dead updater and GeocodeHelper.autocomplete, which returns early because MAPS_API_KEY is empty in the built APK',
}
unre = {m for m, l in g['labels'].items() if l.get('unreachable')}
for m in FIXED_LABELS:
    assert m in unre and oldrows[m]['verdict'] == 'REACHABLE', m
out = [['type', 'item', 'result', 'confirmed_by', 'ref', 'edges', 'note']]
for m, (res, ref, note) in P.items():
    if rows[m]['verdict'] == 'REACHABLE':
        out.append(['path', m, res, 'SOURCE', ref, rows[m]['route_edge_ids'], note])
    else:
        out.append(['path', m, res, 'SOURCE', ref, '', note])
for m in sorted(unre):
    l = g['labels'][m]
    u = l['unreachable']
    base = 'call sites of the method name searched in the app sources, layouts / menus / manifest XML and reflection; bytecode callers outside the unreachable set checked (only five have one, each explained in its reason). Reason: '
    if m in FIXED_LABELS:
        out.append(['label', m, 'fixed', l['confirmed_by'], l['source_ref'], '', 'ERROR FOUND: ' + FIXED_LABELS[m] + '. Fixed: UNREACHABLE (' + u['kind'] + '). ' + u['text']])
    else:
        out.append(['label', m, 'correct', l['confirmed_by'], l['source_ref'], '', base + u['text']])
# reachable labels that changed
out.append(['label', 'BuildConfig.<clinit>', 'fixed', 'INFERRED', 'OmniNotes.java:45,75', '',
            'ERROR FOUND: the first graph called BuildConfig.<clinit> unreachable (nothing in the app calls it). @AcraCore(buildConfigClass = BuildConfig.class) (OmniNotes.java:45) and ACRA.init(this) in attachBaseContext (75) make the ACRA collector read the BuildConfig fields by reflection when a crash report is built, which initialises the class. Fixed: REACHABLE through a non-standard edge with ENV other (a crash). The ACRA claim is INFERRED (ACRA source not read).'])
out.append(['label', 'DetailFragment.lambda$initViewTitle$12', 'fixed', 'SOURCE', 'DetailFragment.java:874', '',
            'ERROR FOUND: the first graph called the title OnDragListener dead because the test tools never drag onto the title; reachability does not depend on the tools. It is registered on the title field and runs when a drag reaches it (a note text or an item dragged onto the title). Fixed: REACHABLE, with the edge from the title view.'])
# reachable labels of the sample
for m in P:
    if m not in rows or rows[m]['verdict'] != 'REACHABLE':
        continue
    sourced = all(b.edge_sourced(E[i]) for i in rows[m]['route_edge_ids'].split())
    cb = 'SOURCE' if sourced else 'INFERRED'
    out.append(['label', m, 'correct', cb, P[m][1].split(';')[0], '', 'REACHABLE confirmed: the route to it was read step by step (path row); ENV / STATE gates on it: env=%s state=%s' % (rows[m]['env_kinds'] or '-', rows[m]['state_kinds'] or '-')])

# ---- edge rows
seen = set()
def edge(i, res, ref, note):
    if i in seen:
        return
    seen.add(i)
    out.append(['edge', i, res, 'SOURCE', ref, '', note])
def eid(src, dst, **kw):
    return has_edge(src, dst, **kw)

for x in g['edges']:
    if 'bytecode line was' in (x['evidence'] or ''):
        m = re.search(r'SRC ([\w./$-]+):([\d-]+) \(bytecode line was (\d+)\)', x['evidence'])
        edge(x['id'], 'fixed', '%s:%s' % (m.group(1), m.group(2)), 'ERROR FOUND: the line table of the bytecode put the call on line %s; the call %s -> %s is on %s (javac gives a call inside a chained call, or after a multi-line expression, a neighbouring line)' % (m.group(3), x['src'], x['dst'], m.group(2)))
edge(eid('MainActivity.onResume', 'ListFragment.onResume'), 'fixed', 'MainActivity.java:111-118', 'guard missing: the edge is valid only after an earlier resume (isPasswordAccepted already true); now a STATE')
edge(eid('MainActivity.onResume', 'MainActivity.init'), 'fixed', 'MainActivity.java:111-118', 'guard missing: init() runs from onResume only when isPasswordAccepted is true; the first start goes through checkPassword; now a STATE')
edge(eid('LogDelegate.isFileLoggingEnabled', 'OmniNotes.getSharedPreferences'), 'fixed', 'LogDelegate.java:93-94', 'guard missing: first logging call of the process (static still null)')
edge(eid('LogDelegate.isFileLoggingEnabled', 'OmniNotes.getAppContext'), 'fixed', 'LogDelegate.java:93-99', 'guard missing: only when the file-logging preference is on; now a STATE settings')
edge(eid('OmniNotes.onCreate', 'NotificationsHelper.initNotificationChannels'), 'fixed', 'OmniNotes.java:83-85,104-110', 'guard missing: not in the LeakCanary analyzer process')
edge(eid('NotificationsHelper.initNotificationChannels', 'NotificationChannels.<clinit>'), 'fixed', 'NotificationsHelper.java:56-57', 'guard missing: SDK_INT > 26 (true on API 27)')
edge(eid('DataBackupIntentService.importData@IMPORT', 'BackupHelper.importNotes'), 'fixed', 'DataBackupIntentService.java:123,131-135', 'context missing: importNotes runs only for the normal import action; the legacy action calls importDB')
edge(eid('DataBackupIntentService.importData@LEGACY', 'BackupHelper.importDB'), 'fixed', 'DataBackupIntentService.java:123,131-133', 'context missing: importDB only for the legacy import action')
edge(eid('BackupHelper.importNotes', 'BackupHelper.importNote'), 'fixed', 'BackupHelper.java:147', 'guard missing: a note file named <13 digits>.json in the folder')
edge(eid('BackupHelper.getImportNote', 'Note.buildFromJson'), 'fixed', 'BackupHelper.java:175', 'guard missing: the note file is not empty')
edge(eid('DetailFragment.lambda$discard$18@EXIST', 'BaseActivity.notifyAppWidgets'), 'fixed', 'DetailFragment.java:1490-1492', 'context missing: the widget refresh runs only for a note that already exists')
edge(eid('ONDashClockExtension.onUpdateData', 'ONDashClockExtension.getNoteTitle'), 'fixed', 'ONDashClockExtension.java:79-96,122-132', 'guard missing: a note with a reminder due today or within 24 hours')
edge(eid('CategoryActivity.saveCategory@NEW_DETAIL', 'DbHelper.updateCategory'), 'fixed', 'CategoryActivity.java:138-141', 'guard missing: the name field is not empty')
edge(eid('AlarmReceiver.createNotification', 'BitmapHelper.getBitmapFromAttachment'), 'fixed', 'AlarmReceiver.java:120-125', 'guard missing: the note has an attachment and the first one is not a file attachment')
edge(eid('CountFactory.getCounterInstanceByLocale', 'IdeogramsWordCounter.<init>'), 'fixed', 'CountFactory.java:33-40', 'ENV text wrong: the locales are ja_JP, zh_CN and zh_TW, not "Chinese, Japanese or Korean"')
edge(eid('GeocodeHelper.lambda$getCoordinatesFromAddress$1', 'DetailFragment.onCoordinatesResolved'), 'fixed', 'GeocodeHelper.java:166-168', 'guard missing: the geocoder returned at least one result')
edge(eid('StorageHelper.createExternalStoragePrivateFile@PICK', 'FileHelper.getPath'), 'fixed', 'StorageHelper.java:118-124; AttachmentTask.java:55', 'context missing: a merged note holds file:// URIs; only a URI picked in another app (AttachmentTask) reaches getPath through the catch fallback')
edge(eid('FileHelper.getPath', 'FileHelper.isMediaDocument'), 'fixed', 'FileHelper.java:55-75', 'state text wrong: the URI is not an attachment of a note but the URI a picker app returned; now ENV other_app')
edge(eid('DateHelper.getFormattedDate', 'DateUtils.prettyTime(Long)'), 'fixed', 'DateHelper.java:112-115', 'guard missing: the prettified-dates preference is on (default on)')
edge(eid('SnoozeActivity.setNextRecurrentReminder', 'RecurrenceHelper.nextReminderFromRecurrenceRule(long,String)'), 'fixed', 'SnoozeActivity.java:55-60', 'guard missing: the note has a recurrence rule')
edge(eid('LanguageHelper.updateLanguage', 'LanguageHelper.getLocale'), 'fixed', 'LanguageHelper.java:50-58', 'guard missing: a language is passed in or the preference is already stored')
edge(eid('BackupHelper.exportAttachments(NotificationsHelper,File,List,List)', 'LogDelegate.w(String)'), 'fixed', 'BackupHelper.java:112-121', 'guard missing: the catch block for a missing attachment file')
edge(eid('MainActivity.onBackPressed@SKETCH_DRAWN', 'Attachment.<init>(Uri,String)'), 'fixed', 'SketchFragment.java:208-226', 'class wrong: a compressed step across a fragment transaction was classed explicit; now standard with the INFERRED lifecycle claim named')
# framework claims that were read (FW-SRC), one row per distinct citation
cites = collections.OrderedDict()
for x in g['edges']:
    for seg in (x['evidence'] or '').split(';'):
        seg = seg.strip()
        if seg.startswith('FW-SRC'):
            cites.setdefault(seg.split('(')[0].strip(), x['id'])
for c, i in cites.items():
    edge(i, 'correct', c.replace('FW-SRC ', '').split(' and ')[0], 'lines read in the Android 8.1.0_r1 source: ' + c.replace('FW-SRC ', ''))

with open('graphs/Omni-Notes/verification.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(collections.Counter((r[0], r[2]) for r in out[1:]))
