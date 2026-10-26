import csv, glob, json, re, sys
sys.path.insert(0, 'tools')
import build_graph as b

g = json.load(open(glob.glob('graphs/hash-checker/out/*_trigger_graph.json')[0]))
E = {x['id']: x for x in g['edges']}
rows = {r['method']: r for r in csv.DictReader(open('graphs/hash-checker/out/methods.csv', encoding='utf-8'))}
ANDX = ' Steps that run through the androidx FragmentManager / RecyclerView rest on INFERRED claims (androidx source not read).'
CTX = ('ERROR FOUND: the derived route started with the plain launcher entry but needs data that only a start by another app carries '
       '(MainActivity.create reads the intent, MainActivity.java:72-93; HashCalculatorFragment reads its arguments, 501-504, 539-545). '
       'Fixed: the start by another app is its own context (@XURI, @XTEXT, @XFILE) from the entry edge down to onViewCreated; the best route is now consistent.')

# method -> (result, ref, note)
P = {}
def p(m, res, ref, note): P[m] = (res, ref, note)

# ---- the final sample of 30
p('HistoryItem.<init>()', 'correct', 'HistoryPresenterImpl.java:35-41',
  'steps 1-10 launcher -> calculator read (MainActivity.java:50-53,93-103, BaseActivity.java:17-19); History icon always shown (menu_main.xml, MainActivity.java:126-138); load() runs while !historyPortion.isLoaded() (35-41); STATE: a hash saved to history (default on). ORMLite reflection and the fragment lifecycle are INFERRED.')
p('DatabaseHelperModule.databaseHelper', 'correct', 'HashCalculatorFragment.java:156', 'App.appComponent.inject(this) in onAttach; the generated component calls the module, nothing in app code calls databaseHelper (non-standard, Dagger).' + ANDX)
p('LangHelperModule.langHelper', 'correct', 'MainActivity.java:51', 'App.appComponent.inject(this) in onCreate; the generated component calls the module (non-standard, Dagger).')
p('ThemeHelperModule.themeHelper', 'correct', 'MainActivity.java:51', 'same injection as LangHelperModule.langHelper.')
p('Blake2B.littleEndianToInt', 'fixed', 'Blake2B.java:91-107,152,171',
  'ERROR FOUND: the derived route reached compress through update(byte) -> compress, which only runs when a 128-byte block is already full (Blake2B.java:91-107), so it needs input longer than one block; getValue -> doFinal -> compress always runs (169-173, 146-152). Fixed: the two update -> compress edges now carry the STATE "input longer than one block" and the route goes through getValue / doFinal. Other steps read: HashCalculatorFragment.java:166-189,215-247; HashCalculatorTask.java:70-76; JdkHashCalculator.java:46-47,109-110.' + ANDX)
p('FNV1a.update256(byte[],int,int)', 'fixed', 'FNV1a.java:95-118',
  'ERROR FOUND (two): (1) ' + CTX[len('ERROR FOUND: '):] + ' (2) FNV1a.update -> update256 runs only for type FNV_1A_256 (FNV1a.java:95-118): the edge now carries that STATE (choose the 256-bit type). The route now goes through the file picker (HashCalculatorFragment.java:171-173,191-201,584-612,316-323).' + ANDX)
p('WebFragment.getMenuResId', 'correct', 'BaseFragment.java:69',
  'Settings icon (MainActivity.java:129-131), privacy row (SettingsFragment.java:182-191), link row opens WebFragment (WebLinksListAdapter.java:55-61), setHasOptionsMenu(true) (BaseFragment.java:98), onCreateOptionsMenu inflates getMenuResId (67-69).' + ANDX)
p('JdkHashCalculator.inputStreamsFormFolder', 'correct', 'JdkHashCalculator.java:87',
  'Folder row -> ACTION_OPEN_DOCUMENT_TREE (HashCalculatorFragment.java:174-175,203-212) -> picker (ENV other_app) -> FOLDER_SELECT with RESULT_OK (600-604) -> validateSelectedFolder (325-332) -> generateHash else branch (235-243) -> HashCalculatorTask.java:70-76 -> JdkHashCalculator.java:87.' + ANDX)
p('HistoryFragment.refreshHistory', 'correct', 'HistoryPresenterImpl.java:43-47',
  'History list -> trash icon -> confirm dialog -> OK -> clearHistory -> refreshHistory (HistoryFragment.java:89-105, HistoryPresenterImpl.java:43-47); STATE: history rows.' + ANDX)
p('OrmLiteLocalDataStorage.getDatabaseFileName', 'correct', 'SettingsPresenterImpl.java:44-50',
  'isHistoryItemsListIsEmpty() is misnamed: it returns countOf() > 0 (OrmLiteLocalDataStorage.java:107-109), so the DONE branch (SettingsPresenterImpl.java:44-50) runs when history has rows, as the edge guard says; onActivityResult needs data, FILE_CREATE and RESULT_OK (SettingsFragment.java:119-124); exportDatabase calls getDatabaseFileName (LocalDataExporter.java:26).' + ANDX)
p('HashCalculatorFragment.writeHashToFile', 'correct', 'HashCalculatorFragment.java:266-267,593-599',
  'Text source, Actions -> Export .txt: needs a source and a generated hash (266), then ACTION_CREATE_DOCUMENT (273-286), result FILE_CREATE calls writeHashToFile (593-599); STATE: a hash was generated; ENV: the document picker.' + ANDX)
p('MainActivity.getConfiguredBundleWithDataUri', 'fixed', 'MainActivity.java:82-88', CTX)
p('Clipboard.clear', 'correct', 'Clipboard.java:27-39',
  'copy icon is visible only for a non-empty field (HashCalculatorFragment.java:519-526), copyHashFromEditText copies a non-empty hash (531-537), Clipboard.copy posts clear after 60 s (Clipboard.java:31); ENV time.' + ANDX)
p('Blake2B.update(byte[],int,int)', 'fixed', 'Blake2B.java:109-131', CTX + ' Also the update -> compress edges of Blake2B were missing the "more than one block" guard (Blake2B.java:91-131), now a STATE.')
p('SettingsFragment.copyFile', 'correct', 'SettingsFragment.java:126-137',
  'export needs history rows and the picker result (SettingsFragment.java:119-124); copyUserDataToUserFolder calls copyFile when uri and descriptor are not null (126-137).' + ANDX)
p('HashCalculatorTask.<init>(Context,HashType,Uri,Uri,HashCalculatorTaskTarget)', 'fixed', 'HashCalculatorFragment.java:227-234', CTX)
p('HashCalculatorFragment.folderNameFromUri', 'correct', 'HashCalculatorFragment.java:330,350-352', 'folder route as for JdkHashCalculator.inputStreamsFormFolder, then validateSelectedFolder calls folderNameFromUri (330).' + ANDX)
p('FeedbackFragment.sendEmail', 'correct', 'FeedbackFragment.java:68-77,101-113',
  'Settings -> Feedback row -> type a message (fragment_feedback.xml) -> Send with a non-empty message (FeedbackFragment.java:68-77) -> sendFeedback -> sendEmail (FeedbackPresenterImpl.java:45).' + ANDX)
p('SharedPreferencesSettings.saveTheme', 'fixed', 'SharedPreferencesSettings.java:128-147; ThemeConfigImpl.java:30',
  'ERROR FOUND: the derived route used getTheme -> validateAppTheme -> saveTheme, which runs only for a stored theme that is neither LIGHT nor DARK (SharedPreferencesSettings.java:128-135) while the app only ever stores those two (142-147): that needs a pre-seeded preferences file. Fixed: the edge is removed; the route goes through the theme picker (ThemesListAdapter.java:48-54,62-78, ThemeConfigImpl.java:30).' + ANDX)
p('AppSnackbar.lambda$show$0', 'correct', 'AppSnackbar.java:62-71',
  'Actions -> Generate with no source -> generateHash else branch shows the hint (HashCalculatorFragment.java:244-246) -> AppSnackbar without a custom action sets the OK listener (AppSnackbar.java:62-71).' + ANDX)
p('HashType.getTitle', 'correct', 'BaseListHolder.java:45', 'hash-type sheet (HashCalculatorFragment.java:473, 260-262) -> RecyclerView binds the rows -> BaseListHolder.bind calls getTitle (BaseListHolder.java:45).' + ANDX)
p('Language.getPrimaryIconResId', 'correct', 'BaseListHolder.java:48', 'Settings -> Language row opens the sheet (SettingsFragment.java:158-166); RecyclerView binds rows; BaseListHolder.bind line 48.' + ANDX)
p('Action.getAdditionalIconResId', 'correct', 'BaseListHolder.java:56', 'From button opens the source sheet (HashCalculatorFragment.java:476-479); RecyclerView binds rows; BaseListHolder.bind line 56.' + ANDX)
p('SharedPreferencesSettings.saveStringPreference', 'fixed', 'App.java:152-167',
  'ERROR FOUND (guard missing): App.setLocale -> setLanguage runs only while key_language is not stored, i.e. on the first launch after install (App.java:154). That holds in the standard configuration (fresh install); the guard text is now on the edge.')
p('App.getShortcut', 'fixed', 'App.java:76-93,137-150',
  'ERROR FOUND (guards missing): createShortcuts runs only on the first launch (App.java:76) and only with SDK_INT >= 26 (84-86), both true on a fresh install on API 27; the guards are now on the edges.')
p('SharedPreferencesSettings.getStringPreference', 'correct', 'SharedPreferencesSettings.java:117', 'App.onCreate calls getSelectedTheme unconditionally (App.java:68); getSelectedTheme -> getTheme -> getStringPreference (103, 117).')
p('SharedPreferencesSettings.getLanguage', 'correct', 'BaseActivity.java:17; LanguageConfigImpl.java:51,57', 'BaseActivity.onCreate calls applyLanguage first (BaseActivity.java:17) -> currentLanguage -> getLanguage (LanguageConfigImpl.java:51,57).')
p('SharedPreferencesSettings.containsPreference', 'correct', 'App.java:152-154', 'App.onCreate calls setLocale (80), which calls languageIsInitialized -> containsPreference (SharedPreferencesSettings.java:52-55).')
p('SharedPreferencesSettings$SharedPreferencesSettingsKeyExtractor.<init>', 'correct', 'App.java:58-59', 'App.onCreate builds an anonymous subclass of the abstract class (App.java:58-65; SharedPreferencesSettings.java:246).')
p('SharedPreferencesSettings.getBooleanPreference', 'correct', 'App.java:76; SharedPreferencesSettings.java:159', 'App.onCreate calls isShortcutsIsCreated unconditionally (App.java:76), which calls getBooleanPreference (159).')

# ---- read before the sample was last drawn (the best routes changed while fixing); kept as extra rows
p('LogUtils.e', 'fixed', 'HashCalculatorFragment.java:196-199; SharedPreferencesSettings.java:44-49',
  'ERROR FOUND: the derived route reached LogUtils.e through getLastHashType, whose catch needs a stored last_type_value that is not an enum name; the app stores HashType.toString() only (HashCalculatorFragment.java:432, SharedPreferencesSettings.java:30-35), so that needs a pre-seeded preference. Fixed: edge removed; the route now ends in openSystemFileManager catching ActivityNotFoundException (HashCalculatorFragment.java:191-200), ENV: no app handles ACTION_OPEN_DOCUMENT.')
p('AppTextWatcher.<init>', 'fixed', 'HashCalculatorFragment.java:457-468,516',
  'ERROR FOUND: a hand-written edge HashCalculatorFragment.<init> -> HashCalculatorFragment$1.<init> was wrong: the field initialiser at line 111 builds a lambda (lambda$new$1), and $1 is the TextWatcher built in watcherForInputField (516, called from onViewCreated at 457-468). Fixed: the edge is removed; the route goes onViewCreated -> watcherForInputField -> $1.<init> -> AppTextWatcher.<init>.' + ANDX)
p('ThemeConfigImpl.setCurrentTheme', 'correct', 'ThemesListAdapter.java:62-81', 'Settings -> Theme row -> a theme other than the current -> dialog -> OK -> configureNewTheme -> setCurrentTheme (ThemesListAdapter.java:48-54,62-81).' + ANDX)
p('HashCalculatorFragment.selectFileFromSystemFileManager', 'correct', 'HashCalculatorFragment.java:584-592,609-612', 'File row -> ACTION_OPEN_DOCUMENT (191-201) -> picker (ENV other_app) -> FILE_SELECT with RESULT_OK (588-591).' + ANDX)
for m, cls in (('DatabaseHelperModule.<init>', 71), ('SettingsHelperModule.<init>', 72), ('ThemeHelperModule.<init>', 74)):
    p(m, 'fixed', 'App.java:%d' % cls, 'ERROR FOUND: the route was right but the edge App.onCreate -> %s was classed non-standard (Dagger) although it is a plain new in App.onCreate (App.java:%d, explicit), and its cited line was one too early (javac attributes a new inside a chained call to the previous line). Fixed: explicit, line corrected; only the injector calls to the modules stay non-standard.' % (m, cls))

# ---- UNREACHABLE labels
U = {}
def u(m, res, cb, note): U[m] = (res, cb, note)
GREP = 'call sites grepped once more in the app sources (main, thirdPartyStores, googlePlay), res/ XML and the manifest (no reflection, no android:onClick): '
for m in ('HashConstants.<init>', 'JdkHashUtils.<init>', 'LocalDataExporter.<init>', 'AppUtils.<init>', 'LogUtils.<init>', 'UIUtils.<init>', 'WebUtils.<init>'):
    u(m, 'correct', 'SOURCE', GREP + 'no new %s( anywhere; static-only class, no trigger in app confirmed' % m.split('.')[0])
u('OrmLiteConfigUtil.<init>', 'correct', 'SOURCE', GREP + 'only the class declaration mentions OrmLiteConfigUtil (build-time ORMLite config generator): no trigger in app confirmed')
u('OrmLiteConfigUtil.main', 'correct', 'SOURCE', GREP + 'command-line main of the build-time generator, never called')
u('OrmLiteLocalDataStorage.onUpgrade', 'correct', 'INFERRED', GREP + 'only the definition (OrmLiteLocalDataStorage.java:56, empty body); DATABASE_VERSION is 1 (31-33), so no older database exists; that SQLiteOpenHelper calls onUpgrade only for a lower stored version is INFERRED (android.database.sqlite source not read)')
u('OrmLiteLocalDataStorage.releaseHelper', 'correct', 'SOURCE', GREP + 'only caller is App.onTerminate (App.java:178), which never runs in a normal app process')
u('App.onTerminate', 'correct', 'SOURCE', GREP + 'no explicit caller; framework side read in Android 8.1: only the EXIT_APPLICATION message calls it (ActivityThread.java:1659-1664) and AMS sends it for a process with no real pid or system_server itself (ActivityManagerService.java:6919-6936, 23336-23340)')
u('DbEntity.getId', 'correct', 'INFERRED', GREP + 'no getId() call; the field has @DatabaseField(generatedId = true) without useGetSet (DbEntity.java:7-16); that ORMLite uses the field by reflection is INFERRED (ORMLite source not read)')
u('DbEntity.setId', 'correct', 'INFERRED', GREP + 'no setId( call; same ORMLite reasoning as getId (INFERRED)')
u('HistoryItem.equals', 'correct', 'INFERRED', GREP + 'no equals / contains / indexOf on HistoryItem objects (they are only held in Lists); that ORMLite does not compare row objects without an object cache is INFERRED')
u('HistoryItem.hashCode', 'correct', 'INFERRED', GREP + 'no HashMap / HashSet of HistoryItem; ORMLite part INFERRED as for equals')
u('AppTextWatcher.onTextChanged', 'correct', 'SOURCE', GREP + 'AppTextWatcher has one subclass instantiation, the anonymous class at HashCalculatorFragment.java:516, which overrides onTextChanged (518-527); the base method is empty (AppTextWatcher.java:14-18)')
u('BaseFragment.setAllowBackAction', 'correct', 'SOURCE', GREP + 'the four BaseFragment subclasses (HashCalculatorFragment 665, HistoryFragment 155, FeedbackFragment 136, WebFragment 58) all override it; the base returns false (BaseFragment.java:103-105)')
u('BaseFragment.getBackActionIconResId', 'correct', 'SOURCE', GREP + 'called only when setAllowBackAction() is true (BaseFragment.java:53-60); the three fragments that return true override it (WebFragment 63, FeedbackFragment 141, HistoryFragment 160) and HashCalculatorFragment returns false')
u('SettingsFragment.lambda$initRate$7', 'correct', 'SOURCE', GREP + 'registered only when BuildConfig.FLAVOR equals "googlePlay" (SettingsFragment.java:247-257); the dataset APK is the thirdPartyStores flavor (DATASET.txt provenance, BuildConfig.class FLAVOR in build/intermediates/javac/thirdPartyStoresDebug)')
u('SharedPreferencesSettings.setRefreshSelectedFileStatus', 'fixed', 'SOURCE', 'was REACHABLE (after setup) in the first graph; ' + GREP + 'the only caller is HashCalculatorFragment.java:580 inside if (settings.refreshSelectedFile()) and the only value ever written is false, so the branch is open only with a pre-seeded preferences file: closed_by_configuration')
u('SharedPreferencesSettings.getThemeAnalogue', 'fixed', 'SOURCE', 'was REACHABLE (after setup) in the first graph; ' + GREP + 'the only caller is the else branch of getTheme (SharedPreferencesSettings.java:117-125) for a stored theme that is neither LIGHT nor DARK, and the app only stores those two (142-147): closed_by_configuration')

out = [['type', 'item', 'result', 'confirmed_by', 'ref', 'edges', 'note']]
for m, (res, ref, note) in P.items():
    out.append(['path', m, res, 'SOURCE', ref, rows[m]['route_edge_ids'], note])
unre = {m for m, l in g['labels'].items() if l.get('unreachable')}
assert set(U) == unre, (sorted(unre - set(U)), sorted(set(U) - unre))
for m, (res, cb, note) in U.items():
    out.append(['label', m, res, cb, g['labels'][m]['source_ref'], '', note])
# reachable labels of the final sample
sample = [l.split()[-1] for l in open('<scratchpad>/sample_final.txt') if l.startswith(('NONSTD', 'INFERRED', 'STATE', 'ENV', 'LONG', 'PLAIN'))]
for m in sample:
    _cb = 'SOURCE' if all(b.edge_sourced(E[i]) for i in rows[m]['route_edge_ids'].split()) else 'INFERRED'   # INFERRED while an edge of the route rests on a claim that was not read
    out.append(['label', m, 'correct', _cb, P[m][1].split(';')[0], '', 'REACHABLE confirmed: the route to it was read step by step (path row); ENV / STATE gates on it read: env=%s state=%s' % (rows[m]['env_kinds'] or '-', rows[m]['state_kinds'] or '-')])

# ---- edge rows
def eid(src, dst, contains=None):
    c = [x for x in g['edges'] if x['src'] == src and x['dst'] == dst and (contains is None or contains in (x['evidence'] or ''))]
    assert c, (src, dst, contains)
    return c[0]['id']
seen = set()
def edge(i, res, ref, note):
    if i in seen:
        return
    seen.add(i)
    out.append(['edge', i, res, 'SOURCE', ref, '', note])
for x in g['edges']:
    if 'bytecode line was' in (x['evidence'] or ''):
        m = re.search(r'SRC ([\w.$]+):([\d-]+) \(bytecode line was (\d+)\)', x['evidence'])
        edge(x['id'], 'fixed', '%s:%s' % (m.group(1), m.group(2)), 'ERROR FOUND: the line table of the bytecode put the call on line %s; the call %s -> %s is on %s (javac gives a new inside a chained call, or the last line of a multi-line expression, the line before / after)' % (m.group(3), x['src'], x['dst'], m.group(2)))
for m in ('Dagger',):
    pass
for dst in ('DatabaseHelperModule.<init>', 'SettingsHelperModule.<init>', 'ThemeHelperModule.<init>', 'LangHelperModule.<init>'):
    edge(eid('App.onCreate', dst), 'fixed', 'App.java:71-74', 'edge class corrected: a plain new in app code is explicit, not Dagger non-standard')
edge(eid('Blake2B.update(byte)', 'Blake2B.compress'), 'fixed', 'Blake2B.java:91-107', 'guard missing: compress only when the 128-byte buffer is full; now a STATE')
edge(eid('Blake2B.update(byte[],int,int)', 'Blake2B.compress'), 'fixed', 'Blake2B.java:109-131', 'guard missing: compress only when more input than one block arrives; now a STATE')
edge(eid('FNV1a.update(byte[],int,int)', 'FNV1a.update256(byte[],int,int)'), 'fixed', 'FNV1a.java:95-118', 'guard missing: only for type FNV_1A_256; now a STATE (the other sizes the same)')
edge(eid('App.setLocale', 'LanguageConfigImpl.setLanguage(Language)'), 'fixed', 'App.java:152-167', 'guard missing: first launch after install (key_language not stored)')
edge(eid('App.onCreate', 'App.createShortcuts'), 'fixed', 'App.java:76-79', 'guard missing: first launch after install')
edge(eid('App.createShortcuts', 'App.getShortcutForFolderType'), 'fixed', 'App.java:84-93', 'guard missing: SDK_INT >= 26 (true on API 27) and a ShortcutManager')
edge(eid('S_ENTRY', 'MainActivity.<init>@XURI'), 'fixed', 'MainActivity.java:72-93', 'the VIEW / SEND start was an extra entry into the plain startup chain, which carries no URI; it now starts its own context @XURI (likewise @XTEXT, @XFILE for the two launcher shortcuts)')
pe = [x for x in g['edges'] if x['src'] == 'P' or ('A device-wide configuration change' in x['trigger'])]
for x in pe:
    edge(x['id'], 'fixed', 'AndroidManifest.xml:19-24', 'text corrected: the trigger said the portrait lock means no activity recreate, but the lock only stops rotation; MainActivity has no android:configChanges, so a locale / font change relaunches it too')
# framework claims that were read (FW-SRC), one row per distinct citation
cites = {}
for x in g['edges']:
    for seg in (x['evidence'] or '').split(';'):
        seg = seg.strip()
        if seg.startswith('FW-SRC'):
            cites.setdefault(seg.split('(')[0].strip(), x['id'])
for c, i in cites.items():
    edge(i, 'correct', c.replace('FW-SRC ', '').split(' and ')[0], 'lines printed from the Android 8.1.0_r1 source and read: ' + c.replace('FW-SRC ', ''))

with open('graphs/hash-checker/verification.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
import collections
print(collections.Counter((r[0], r[2]) for r in out[1:]))
