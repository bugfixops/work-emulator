# Currency v1.58 (billthefarmer/currency@fb95913) trigger graph definition.
# Built by reading all 17 app source files plus manifest/res; framework claims are
# labelled FW-SRC (AOSP android-8.1.0_r1 file:line) where checked and INFERRED where not. Schema 2 (see handoff/SCHEMA_V2.md).
# Executed by tools/build_graph.py.

TITLE = 'Currency v1.58 trigger graph'

ENV_NET = 'network connected and allowed by the Wi-Fi only / Roaming settings'
ENV_NONET = 'network off, or not allowed by the Wi-Fi only / Roaming settings'
ENV_ECB = ('ECB download succeeds (HTTPS to www.ecb.europa.eu over a trusted certificate chain; '
           'the dataset notes a certificate issue on API<=27 images)')
ENV_WIDGET = 'a Currency widget is placed on the home screen through the launcher (another app, a user action outside Currency)'
ENV_ROTATE = 'the device is rotated (orientation change)'
STATE_FRESH = 'no exchange rates saved yet: first launch after install or after clearing the data'
STATE_THEME = 'Change Theme in Settings, then return to Main'
STATE_SELECTION = 'Long-press a row, then rotate or press Home and return (the selection survives in the process)'
STATE_CHART = 'A chart download succeeded earlier in the same process'
ENV_KINDS_OF = {ENV_NET: ['network'], ENV_NONET: ['network'], ENV_ECB: ['network', 'tls_chain'], ENV_WIDGET: ['other_app'], ENV_ROTATE: ['hardware']}
STATE_KINDS_OF = {STATE_FRESH: ['data'], STATE_THEME: ['settings'], STATE_SELECTION: ['session'], STATE_CHART: ['session']}
STRICT = True
AOSP = 'FW-SRC android-8.1.0_r1:'   # Android framework source of the API 27 emulator (file under frameworks/base/core/java/android/ or services/)
NET_GUARD = ('network connected and (pref_wifi off or on Wi-Fi) and (pref_roaming on or not roaming)')
NET_READS = ['pref:pref_wifi', 'pref:pref_roaming', 'env:connectivity']

SCREENS = {
    'S_ENTRY': 'Outside the app: home screen / launcher (app not running, or reopened from the background)',
    'S_EXIT': 'App finished or crashed; the process may survive with Data/Singleton statics kept',
    'S_MAIN_PAUSED': 'Main is paused/stopped: app in the background, or Chart/Help/Settings/picker on top',
    'S_CHART_PAUSED': 'ChartActivity is paused/stopped: Home, currency picker on top, or mid-rotation',
    'S_SETTINGS_PAUSED': 'SettingsActivity is in the background (Home / recents)',
    'S_MAIN_DISPLAY': 'Main, DISPLAY_MODE: action bar menu main.xml (Add, Refresh inline; Update under More options), navigation icon',
    'S_MAIN_SELECT': 'Main, SELECT_MODE: rows highlighted; action bar menu select.xml (Clear, Remove, Chart, Copy)',
    'S_MAIN_EDIT': 'Main, the value field at the top has focus and the soft keyboard is shown',
    'S_NAV_POPUP': 'PopupMenu from the navigation icon (menu navigation.xml: Settings, Help) over Main',
    'S_DLG_UPDATE': 'AlertDialog "Update extra currency" over Main (EditText + OK / Cancel)',
    'S_CHOICE_DISPLAY': 'ChoiceDialog (floating activity), nothing selected: Clear/Select disabled, tapping a row returns immediately',
    'S_CHOICE_SELECT': 'ChoiceDialog in multi-select: Clear/Select enabled',
    'S_CHART_LOADING': 'ChartActivity, histMap == null (downloading / no network): Invert disabled, title tap does nothing',
    'S_CHART_LOADED': 'ChartActivity, histMap != null (line chart drawn): Invert enabled, title tap inverts',
    'S_HELP': 'HelpActivity (help.html text, Up arrow)',
    'S_SETTINGS': 'SettingsActivity + SettingsFragment (preferences.xml)',
    'S_DLG_ENTRY': 'Single-choice dialog of the "Widget entry" ListPreference',
    'S_DLG_DIGITS': 'Single-choice dialog of the "Fraction digits" ListPreference',
    'S_DLG_THEME': 'Single-choice dialog of the "Theme" ListPreference',
    'S_DLG_ABOUT': 'About dialog (AboutPreference: version, build date, links)',
    'S_HOME_WIDGET': 'Home screen with a Currency widget placed (refresh icon, configure icon, values)',
    'S_WIDGET_CONFIG': 'CurrencyWidgetConfigure dialog: pick which list currency the widget shows',
}

UNREACHABLE = {
    'ChartParser.startParser(Context,int)': ('no_trigger_in_app',
        'No call site in the app: Main.java:497 calls Parser.startParser(Context,int), not the ChartParser overload; '
        'no reflection (the only getIdentifier call looks up android:id/action_bar, Main.java:285)', 'ChartParser.java:83', 'SOURCE'),
    'Singleton.getList': ('branch_never_taken',
        'The only call site, ChartActivity.java:176, is the else-branch of "instance == null" (:163); instance is an instance field (:90), '
        'null whenever onCreate starts, so the branch never runs', 'ChartActivity.java:163-177', 'SOURCE'),
    'CurrencyAdapter.getItem': ('framework_never_calls',
        'Returns null. The app never calls getItem and a plain ListView does not: AdapterView calls adapter.getItem only inside the public '
        'getSelectedItem and getItemAtPosition (AdapterView.java:594, 798 in android-8.1.0_r1), which the app never calls', 'CurrencyAdapter.java:75', 'SOURCE'),
    'ChoiceAdapter.getItem': ('framework_never_calls',
        'Returns null. The app never calls getItem and a plain ListView does not: AdapterView calls adapter.getItem only inside the public '
        'getSelectedItem and getItemAtPosition (AdapterView.java:594, 798 in android-8.1.0_r1), which the app never calls', 'ChoiceAdapter.java:66', 'SOURCE'),
    'CurrencyWidgetUpdate.onBind': ('framework_never_calls',
        'Service.onBind runs only for bindService; the app only starts the service (CurrencyWidgetProvider.java:302, CurrencyWidgetRefresh.java:78), '
        'never binds it, and the service is not exported (AndroidManifest.xml:55-56)', 'CurrencyWidgetUpdate.java:135', 'SOURCE'),
}

NOTES = {
    'Main.onOptionsItemSelected': 'Branches action_help / action_settings are unreachable here: those items moved to the navigation popup (navigation.xml)',
    'ChartActivity.onCreate': 'else-branch (instance != null, ChartActivity.java:173-177) is unreachable',
    'ChartActivity.onActivityResult': 'Hazard candidate: NullPointerException at ChartActivity.java:836 when a pair is picked via New chart before any history loaded',
    'CurrencyWidgetRefresh.onCreate': 'Hazard candidate: when the network check fails the NoDisplay activity returns without finish() (crash on API 23+)',
    'SettingsFragment.onPreferenceTreeClick': 'PreferenceScreen branch unreachable: preferences.xml has no nested PreferenceScreen',
    'HelpActivity.onOptionsItemSelected': 'default branch unreachable: the activity has no options menu items besides Up',
}

FW_TEXTWATCH = AOSP + 'widget/TextView.java:5206,5294-5296,5397,5403'
FW_SETADAPTER = AOSP + 'widget/ListView.java:575; ' + AOSP + 'widget/AbsListView.java:2365'
FW_NOTIFY = AOSP + 'widget/AdapterView.java:833-847; ' + AOSP + 'widget/AbsListView.java:2365'
FW_ITEMID_CLICK = AOSP + 'widget/AbsListView.java:3108-3127; ' + AOSP + 'widget/AdapterView.java:314-318'
FW_MENU = (AOSP + 'app/Activity.java:3512-3515,3386-3388,3404-3406; ' + AOSP + 'policy/PhoneWindow.java:983-999,631,659,2697-2704')
FW_RELAUNCH = AOSP + 'app/ActivityThread.java:4553,4675,4699'
FW_SAVESTATE = AOSP + 'app/ActivityThread.java:4022-4026'
FW_BACK = AOSP + 'app/Activity.java:3001-3010'
FW_RESUME = AOSP + 'app/ActivityThread.java:3534-3553'
MPCHART = (AOSP.replace('android-8.1.0_r1:', 'MPAndroidChart-v3.1.0:') + 'renderer/XAxisRenderer.java:78,204; ' + AOSP.replace('android-8.1.0_r1:', 'MPAndroidChart-v3.1.0:')
          + 'components/AxisBase.java:474,488; ' + AOSP.replace('android-8.1.0_r1:', 'MPAndroidChart-v3.1.0:') + 'formatter/ValueFormatter.java:61-62')
FW_FRAGMENT = AOSP + 'app/FragmentManager.java:1141,1237,1322'

# ---------------------------------------------------------------- entry, Main lifecycle
e('S_ENTRY', 'Main.<clinit>', 'ENTRY', 'First use of class Main in a new process: the static CURRENCIES table is built',
  gui=['Home screen: tap the Currency icon'], evidence='SRC Main.java:115-151',
  note='Runs once per process; widget code that reads Main.CURRENCIES can trigger it too')
e('Main.<clinit>', 'Main$Currency.<init>', 'CALL', 'new Currency(...) for each of the 34 table entries', evidence='SRC Main.java:117-150')
e('S_ENTRY', 'Main.<init>', 'ENTRY', 'Tap the Currency icon in the launcher (MAIN/LAUNCHER intent filter)',
  gui=['Home screen: tap the Currency icon'], evidence='SRC AndroidManifest.xml:19-24',
  note='The other external entry is the home-screen widget (CurrencyWidgetConfigure / CurrencyWidgetProvider are exported)')
e('Main.<init>', 'Main.onCreate', 'LIFECYCLE', 'The system instantiates Main, then calls onCreate', evidence='SRC Main.java:242')
e('Main.onCreate', 'Main.onResume', 'LIFECYCLE', 'onStart -> onResume', evidence='SRC Main.java:369')
e('Main.onCreate', 'Data.getInstance', 'CALL', 'data = Data.getInstance(this): Main becomes the result listener',
  writes=['static:Data.instance', 'static:Data.listener'], evidence='SRC Main.java:282')
e('Data.getInstance', 'Data.<init>', 'CALL', 'instance == null -> new Data()', guard='first call in this process', evidence='SRC Data.java:56-57')
e('Main.onCreate', 'Data.getList', 'CALL', 'selectList = data.getList(): a selection kept in the process restores SELECT_MODE',
  reads=['static:Data.instance.list'], writes=['field:Main.selectList', 'field:Main.mode'], evidence='SRC Main.java:343-355')
e('Main.onCreate', 'CurrencyAdapter.<init>', 'CALL', 'adapter = new CurrencyAdapter(...)', evidence='SRC Main.java:358')
e('Main.onCreate', 'CurrencyAdapter.getCount', 'FRAMEWORK', 'listView.setAdapter(adapter) reads getCount', evidence=FW_SETADAPTER)
e('Main.onCreate', 'Main.lambda$onCreate$0', 'REGISTER', 'toolbar.setNavigationOnClickListener(v -> popup menu)', evidence='SRC Main.java:288-295')
e('Main.onCreate', 'Main.onClick', 'REGISTER', 'flag/name/symbol/long_name/edit.setOnClickListener(this)', evidence='SRC Main.java:308-325')
e('Main.onCreate', 'Main.afterTextChanged', 'REGISTER', 'editView.addTextChangedListener(this) (also beforeTextChanged / onTextChanged)', evidence='SRC Main.java:323')
e('Main.onCreate', 'Main.onEditorAction', 'REGISTER', 'editView.setOnEditorActionListener(this)', evidence='SRC Main.java:324')
e('Main.onCreate', 'Main.onItemClick', 'REGISTER', 'listView.setOnItemClickListener(this)', evidence='SRC Main.java:331')
e('Main.onCreate', 'Main.onItemLongClick', 'REGISTER', 'listView.setOnItemLongClickListener(this)', evidence='SRC Main.java:332')
e('Main.lambda$onCreate$0', 'Main.onMenuItemClick', 'REGISTER', 'popup.setOnMenuItemClickListener(this)', evidence='SRC Main.java:293')

e('Main.onResume', 'Main.<init>', 'SYSTEM', 'recreate(): the Theme preference changed since onCreate',
  guard='pref_theme differs from the theme read in onCreate and SDK != 23', reads=['pref:pref_theme'],
  needs_state=STATE_THEME, evidence='SRC Main.java:380-389',
  note='The old instance runs onPause (and onSaveInstanceState) first')
e('Main.onResume', 'Main.currencyIndex', 'CALL', 'currentIndex = prefs.getInt(PREF_INDEX, currencyIndex("EUR")); also once per list row',
  reads=['pref:pref_index'], evidence='SRC Main.java:392-393,633')
for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
    e('Main.onResume', 'Main.' + cb, 'FRAMEWORK', 'editView.setText(value) notifies the TextWatcher', evidence=FW_TEXTWATCH + '; SRC Main.java:451')
e('Main.onResume', 'Data.getInstance', 'CALL', 'data = Data.getInstance(this): reconnect callbacks', evidence='SRC Main.java:454')
e('Main.onResume', 'Data.getMap', 'CALL', 'valueMap = data.getMap(): rates kept in the process', reads=['static:Data.instance.map'], evidence='SRC Main.java:459')
FIRST_RUN = 'Data.map == null and pref_map not saved yet (first launch after install / clear data)'
e('Main.onResume', 'Parser.<init>', 'CALL', 'No rates anywhere: new Parser() for the rates bundled in res/raw',
  guard=FIRST_RUN, reads=['pref:pref_map'], evidence='SRC Main.java:462-494')
e('Main.onResume', 'Parser.startParser(Context,int)', 'CALL', 'parser.startParser(this, R.raw.eurofxref_daily)',
  guard=FIRST_RUN, reads=['res:raw/eurofxref_daily.xml'], evidence='SRC Main.java:497')
e('Main.onResume', 'Parser.getDate', 'CALL', 'latest = parser.getDate()', guard=FIRST_RUN, evidence='SRC Main.java:505')
e('Main.onResume', 'Parser.getMap', 'CALL', 'valueMap = parser.getMap()', guard=FIRST_RUN, evidence='SRC Main.java:529')
e('Main.onResume', 'CurrencyAdapter.getCount', 'FRAMEWORK', 'adapter.notifyDataSetChanged(): the ListView re-lays out', evidence=FW_NOTIFY + '; SRC Main.java:644')
e('Main.onResume', 'CurrencyAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged(): visible rows are drawn', evidence=FW_NOTIFY + '; SRC Main.java:644')
e('Main.onResume', 'CurrencyAdapter.getItemId', 'FRAMEWORK', 'After notifyDataSetChanged the AdapterView observer calls rememberSyncState -> getItemId(firstPosition)',
  guard='list has rows', evidence=AOSP + 'widget/AdapterView.java:833-847,1245-1263')
e('Main.onResume', 'Main.onCreateOptionsMenu', 'FRAMEWORK', 'The options menu is created after the window attaches (main.xml or select.xml by mode)', evidence=FW_MENU)
e('Main.onResume', 'Data.startParse@MAIN', 'CALL', 'No rates kept in the process: check connectivity, then data.startParse(ECB_DAILY_URL)',
  guard='Data.map == null (first resume in this process) and ' + NET_GUARD, reads=NET_READS, env=ENV_NET,
  evidence='SRC Main.java:646-695')
e('Main.onResume', 'S_MAIN_DISPLAY', 'ENTERS', 'Main becomes visible', guard='mode == DISPLAY_MODE (no selection kept)', evidence='SRC Main.java:351-352')
e('Main.onResume', 'S_MAIN_SELECT', 'ENTERS', 'Main becomes visible with a selection kept in Data.list', guard='mode == SELECT_MODE',
  reads=['static:Data.instance.list'], needs_state=STATE_SELECTION,
  evidence='SRC Main.java:343-355,734')

e('Parser.startParser(Context,int)', 'Parser$Handler.<init>', 'CALL', 'new Handler()', evidence='SRC Parser.java:93')
e('Parser.startParser(Context,int)', 'Parser$Handler.startElement', 'FRAMEWORK', 'Xml.parse SAX callback, once per XML element', evidence='SRC Parser.java:94')
e('Parser.startParser(String)', 'Parser$Handler.<init>', 'CALL', 'new Handler() after the HTTPS stream opened', env=ENV_ECB, evidence='SRC Parser.java:65-67')
e('Parser.startParser(String)', 'Parser$Handler.startElement', 'FRAMEWORK', 'Xml.parse SAX callbacks on the downloaded XML', env=ENV_ECB, evidence='SRC Parser.java:68')

# ---------------------------------------------------------------- Main pause / exit
for pg in ('S_MAIN_DISPLAY', 'S_MAIN_SELECT', 'S_MAIN_EDIT'):
    e(pg, 'Main.onPause', 'SYSTEM', 'Main loses the foreground',
      gui=['Press Home / recents / screen off', 'or open Chart / Help / Settings / the currency picker', 'or Back (finish)', 'or rotate the screen'],
      evidence='SRC Main.java:700')
e('Main.onPause', 'Data.setList', 'CALL', 'data.setList(selectList)', writes=['static:Data.instance.list'], evidence='SRC Main.java:734')
e('Main.onPause', 'Data.setMap', 'CALL', 'data.setMap(valueMap)', writes=['static:Data.instance.map'], evidence='SRC Main.java:735')
e('Main.onPause', 'Data.getInstance', 'CALL', 'data = Data.getInstance(null): disconnect callbacks', writes=['static:Data.listener'], evidence='SRC Main.java:739')
e('Main.onPause', 'Main.updateWidgets', 'CALL', 'updateWidgets()', writes=['pref:pref_map', 'pref:pref_names', 'pref:pref_values', 'pref:pref_index', 'pref:pref_value'],
  evidence='SRC Main.java:705-742')
e('Main.updateWidgets', 'CurrencyWidgetProvider.<init>@UPDATE', 'INTENT', 'sendBroadcast(ACTION_APPWIDGET_UPDATE, EXTRA_UPDATE_DONE=true): the manifest receiver is instantiated',
  writes=['intent:EXTRA_UPDATE_DONE'],
  evidence='SRC Main.java:836-851; ' + AOSP + 'am/ActivityManagerService.java:19199-19224 (an APPWIDGET_UPDATE sent by an app is limited to the caller package); ' + AOSP + 'am/BroadcastQueue.java:1267-1279 (the background skip needs component and package both null)',
  note='Implicit by action, but the system sets the caller package on an APPWIDGET_UPDATE sent by an app, so the manifest receiver gets it on API 27 although the app targets SDK 35')
e('Main.onPause', 'S_MAIN_PAUSED', 'ENTERS', 'Main is in the background or under another activity', evidence='SRC Main.java:700')
e('Main.onPause', 'Main.<init>', 'SYSTEM', 'Rotation destroys and recreates Main (no configChanges in the manifest)', gui=['Rotate the screen'],
  guard='orientation change', evidence='SRC AndroidManifest.xml:18-26; ' + FW_RELAUNCH)
e('Main.onPause', 'S_EXIT', 'ENTERS', 'Back on Main finishes the root activity', guard='Back pressed (finishing)', evidence=FW_BACK)
e('S_MAIN_PAUSED', 'Main.onResume', 'SYSTEM', 'Main returns to the foreground',
  gui=['Return via recents or the launcher icon', 'or close the page on top (Back / Up)'], guard='process still alive', evidence='SRC Main.java:369')
e('S_EXIT', 'S_ENTRY', 'SYSTEM', 'Next launch; if the process survived, Data/Singleton statics are kept (not a cold start)',
  evidence='INFERRED the process stays cached after its last activity finishes and its statics survive until the system kills it (process lifetime code not read)')

# ---------------------------------------------------------------- Main menus and navigation popup
e('S_MAIN_DISPLAY', 'Main.onOptionsItemSelected@DISPLAY', 'GUI', 'Tap a menu item in the action bar',
  gui=['Tap the Add or Refresh icon', 'Tap More options (⋮) -> Update'], guard='menu main.xml: action_add / action_refresh / action_update',
  evidence='SRC res/menu/main.xml; Main.java:770')
e('Main.onOptionsItemSelected@DISPLAY', 'Main.onAddClick', 'CALL', 'switch case R.id.action_add', evidence='SRC Main.java:777-778')
e('Main.onOptionsItemSelected@DISPLAY', 'Main.onRefreshClick', 'CALL', 'switch case R.id.action_refresh', evidence='SRC Main.java:781-782')
e('Main.onOptionsItemSelected@DISPLAY', 'Main.onUpdateClick', 'CALL', 'switch case R.id.action_update', evidence='SRC Main.java:785-786')
e('S_MAIN_SELECT', 'Main.onOptionsItemSelected@SELECT', 'GUI', 'Tap a menu item in the action bar',
  gui=['Tap the Clear / Remove / Chart / Copy icon (via More options when folded)'], guard='menu select.xml',
  evidence='SRC res/menu/select.xml; Main.java:770')
e('Main.onOptionsItemSelected@SELECT', 'Main.onClearClick', 'CALL', 'switch case R.id.action_clear', evidence='SRC Main.java:797-798')
e('Main.onOptionsItemSelected@SELECT', 'Main.onRemoveClick', 'CALL', 'switch case R.id.action_remove', evidence='SRC Main.java:801-802')
e('Main.onOptionsItemSelected@SELECT', 'Main.onChartClick', 'CALL', 'switch case R.id.action_chart', evidence='SRC Main.java:805-806')
e('Main.onOptionsItemSelected@SELECT', 'Main.onCopyClick', 'CALL', 'switch case R.id.action_copy', evidence='SRC Main.java:809-810')

for pg in ('S_MAIN_DISPLAY', 'S_MAIN_SELECT'):
    e(pg, 'Main.lambda$onCreate$0', 'GUI', 'Tap the navigation icon at the left of the action bar', gui=['Tap the ☰ icon (top-left)'],
      evidence='SRC Main.java:288-295')
e('Main.lambda$onCreate$0', 'S_NAV_POPUP', 'ENTERS', 'popup.show(): PopupMenu with Settings / Help', evidence='SRC Main.java:291-294')
e('S_NAV_POPUP', 'Main.onMenuItemClick', 'GUI', 'Tap an item in the popup', gui=['Tap Settings', 'or tap Help'],
  evidence='SRC res/menu/navigation.xml; Main.java:818')
e('Main.onMenuItemClick', 'Main.onHelpClick', 'CALL', 'switch case R.id.action_help', evidence='SRC Main.java:825-826')
e('Main.onMenuItemClick', 'Main.onSettingsClick', 'CALL', 'switch case R.id.action_settings', evidence='SRC Main.java:829-830')
e('S_NAV_POPUP', 'S_MAIN_DISPLAY', 'ENTERS', 'Back or a tap outside dismisses the popup (Main stays in the mode it was in)',
  gui=['Press Back or tap outside the popup'], evidence='SRC Main.java:289-295 (no OnDismissListener); INFERRED PopupMenu dismisses on Back or an outside tap (popup code not read)')

# ---------------------------------------------------------------- Main actions
e('Main.onAddClick', 'ChoiceDialog.<init>@MAIN', 'INTENT', 'startActivityForResult(new Intent(this, ChoiceDialog.class), 0)', evidence='SRC Main.java:857-858')
e('Main.onRefreshClick', 'Data.getInstance', 'CALL', 'data = Data.getInstance(this): reconnect callbacks', guard=NET_GUARD, evidence='SRC Main.java:1024')
e('Main.onRefreshClick', 'Data.startParse@MAIN', 'CALL', 'data.startParse(ECB_DAILY_URL); otherwise the status line shows No connection / No Wi-Fi / Roaming',
  guard=NET_GUARD, reads=NET_READS, env=ENV_NET, evidence='SRC Main.java:990-1028')
e('Main.onUpdateClick', 'Main.updateDialog', 'CALL', 'updateDialog(R.string.update_extra, extra, R.string.decimal, listener)', evidence='SRC Main.java:1045')
e('Main.updateDialog', 'S_DLG_UPDATE', 'ENTERS', 'dialog.show(): AlertDialog with an EditText (OK / Cancel)', evidence='SRC Main.java:1098-1115')
e('S_DLG_UPDATE', 'Main.lambda$onUpdateClick$1', 'GUI', 'Tap a dialog button', gui=['Type a rate and tap OK', 'or tap Cancel'],
  evidence='SRC Main.java:1046,1102-1103')
e('Main.lambda$onUpdateClick$1', 'Main.afterTextChanged', 'CALL', 'OK with text: set the EXT rate, then afterTextChanged(editable) recalculates',
  guard='BUTTON_POSITIVE and text not empty', writes=['field:Main.extraValue'], evidence='SRC Main.java:1050-1087')
e('Main.lambda$onUpdateClick$1', 'S_MAIN_DISPLAY', 'ENTERS', 'The dialog closes', evidence='SRC Main.java:1102-1103')
e('S_DLG_UPDATE', 'S_MAIN_DISPLAY', 'ENTERS', 'Back / tap outside cancels the dialog without calling the listener', gui=['Press Back'],
  evidence='SRC Main.java:1098-1115 (no OnCancelListener); INFERRED AlertDialog cancels on Back or an outside tap (dialog code not read)')
e('Main.afterTextChanged', 'CurrencyAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', evidence='SRC Main.java:1224')

for pg in ('S_MAIN_DISPLAY', 'S_MAIN_SELECT'):
    e(pg, 'Main.onClick', 'GUI', 'Tap the current currency (flag, code, symbol, long name) or the value field',
      gui=['Tap the current currency at the top', 'or tap the value field'], evidence='SRC Main.java:1139-1164')
e('S_MAIN_EDIT', 'Main.onClick', 'GUI', 'Tap the value field again', gui=['Tap the value field'], evidence='SRC Main.java:1146-1156')
e('S_MAIN_DISPLAY', 'S_MAIN_EDIT', 'ENTERS', 'Tap the value field: it takes focus and the soft keyboard opens',
  gui=['Tap the value field (number box at the top)'],
  evidence='SRC AndroidManifest.xml:21 (stateHidden only hides the keyboard at start); INFERRED an EditText with focus shows the soft keyboard (IME behaviour, not read)',
  note='The first tap may only take focus without calling onClick (prompt checklist item 11)')
for cb in ('beforeTextChanged', 'onTextChanged', 'afterTextChanged'):
    e('S_MAIN_EDIT', 'Main.' + cb, 'GUI', 'Type or delete a character in the value field', gui=['Type a number on the keyboard'],
      evidence='SRC Main.java:323,1169-1235')
e('S_MAIN_EDIT', 'Main.onEditorAction', 'GUI', 'Press Done on the soft keyboard (IME_ACTION_DONE)', gui=['Tap Done on the keyboard'],
  evidence='SRC Main.java:1239-1310; res/layout/main.xml imeOptions=actionDone',
  note='A hardware Enter key arrives with a different action id and falls through the switch (prompt checklist item 10)')
e('Main.onEditorAction', 'Main.afterTextChanged', 'FRAMEWORK', 'view.setText(s) reformats the field and notifies the watchers', guard='actionId == IME_ACTION_DONE',
  evidence=FW_TEXTWATCH + '; SRC Main.java:1282')
e('Main.onEditorAction', 'CurrencyAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', guard='actionId == IME_ACTION_DONE', evidence='SRC Main.java:1304')
e('Main.onEditorAction', 'S_MAIN_DISPLAY', 'ENTERS', 'Returns false so the keyboard closes', guard='actionId == IME_ACTION_DONE', evidence='SRC Main.java:1306')
e('S_MAIN_EDIT', 'S_MAIN_DISPLAY', 'ENTERS', 'Back hides the keyboard', gui=['Press Back'], evidence='INFERRED Back hides the soft keyboard (IME behaviour, not read)')

e('S_MAIN_DISPLAY', 'Main.onItemClick@DISPLAY', 'GUI', 'Tap a currency row: it becomes the current currency', gui=['Tap any row in the list'],
  evidence='SRC Main.java:1329-1402')
e('S_MAIN_DISPLAY', 'CurrencyAdapter.getItemId', 'FRAMEWORK', 'Tapping a row: adapter.getItemId(position)', evidence=FW_ITEMID_CLICK)
e('Main.onItemClick@DISPLAY', 'Main.currencyIndex', 'CALL', 'currentIndex = currencyIndex(nameList.get(position))', evidence='SRC Main.java:1335')
e('Main.onItemClick@DISPLAY', 'Main.afterTextChanged', 'FRAMEWORK', 'editView.setText(value) notifies the watchers', evidence=FW_TEXTWATCH + '; SRC Main.java:1371')
e('Main.onItemClick@DISPLAY', 'CurrencyAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()',
  writes=['pref:pref_names', 'pref:pref_values', 'pref:pref_index', 'pref:pref_value'], evidence='SRC Main.java:1382-1401')
e('S_MAIN_SELECT', 'Main.onItemClick@SELECT', 'GUI', 'Tap a row to toggle its selection', gui=['Tap a row'], evidence='SRC Main.java:1405-1422')
e('S_MAIN_SELECT', 'CurrencyAdapter.getItemId', 'FRAMEWORK', 'Tapping a row: adapter.getItemId(position)', evidence=FW_ITEMID_CLICK)
e('Main.onItemClick@SELECT', 'CurrencyAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', evidence='SRC Main.java:1421')
e('Main.onItemClick@SELECT', 'Main.onCreateOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu(): main.xml again', guard='selection becomes empty',
  evidence=FW_MENU + '; SRC Main.java:1417')
e('Main.onItemClick@SELECT', 'S_MAIN_DISPLAY', 'ENTERS', 'Last selected row deselected: back to DISPLAY_MODE', guard='selection becomes empty',
  evidence='SRC Main.java:1414-1418')
for pg in ('S_MAIN_DISPLAY', 'S_MAIN_SELECT'):
    e(pg, 'Main.onItemLongClick', 'GUI', 'Long-press a currency row (in SELECT_MODE the selection restarts from it)',
      gui=['Long-press any row in the list'], evidence='SRC Main.java:1428-1442')
e('Main.onItemLongClick', 'Main.onCreateOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu(): select.xml', evidence=FW_MENU + '; SRC Main.java:1433')
e('Main.onItemLongClick', 'CurrencyAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', evidence='SRC Main.java:1440')
e('Main.onItemLongClick', 'S_MAIN_SELECT', 'ENTERS', 'mode = SELECT_MODE, the row is highlighted', evidence='SRC Main.java:1432-1437')

for h, line, what in (('onClearClick', '864-873', 'Selection cleared'),
                      ('onCopyClick', '877-916', 'Value of the selected row copied to the clipboard; selection cleared'),
                      ('onRemoveClick', '920-949', 'Selected rows removed from the list')):
    e('Main.' + h, 'CurrencyAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', evidence='SRC Main.java:' + line)
    e('Main.' + h, 'Main.onCreateOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu(): main.xml again', evidence=FW_MENU + '; SRC Main.java:' + line)
    e('Main.' + h, 'S_MAIN_DISPLAY', 'ENTERS', what, writes=['clipboard'] if h == 'onCopyClick' else [], evidence='SRC Main.java:' + line)
e('Main.onChartClick', 'Main.currencyIndex', 'CALL', 'currencyIndex(name) for each selected row', evidence='SRC Main.java:962-966')
e('Main.onChartClick', 'ChartActivity.<init>', 'INTENT', 'startActivity(ChartActivity, CHART_LIST = [current, selected...])',
  writes=['intent:chart_list'], evidence='SRC Main.java:955-973')
e('Main.onChartClick', 'Main.onCreateOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu(): main.xml again (selection cleared)', evidence=FW_MENU + '; SRC Main.java:976-981')
e('Main.onHelpClick', 'HelpActivity.<init>', 'INTENT', 'startActivity(HelpActivity)', evidence='SRC Main.java:1122-1123')
e('Main.onSettingsClick', 'SettingsActivity.<init>', 'INTENT', 'startActivity(SettingsActivity)', evidence='SRC Main.java:1132-1133')
e('Main.onActivityResult@OK', 'CurrencyAdapter.getView', 'FRAMEWORK', 'Picked currencies appended, adapter.notifyDataSetChanged()',
  guard='resultCode == RESULT_OK', writes=['pref:pref_names', 'pref:pref_values'], evidence='SRC Main.java:1450-1503')
for res in ('OK', 'CANCEL'):
    e('Main.onActivityResult@' + res, 'Main.onResume', 'LIFECYCLE', 'onActivityResult is delivered before the caller resumes', evidence=FW_RESUME)
e('Main.onDataResult', 'CurrencyAdapter.getView', 'FRAMEWORK', 'New rates: values recalculated, adapter.notifyDataSetChanged()', guard='map not empty',
  writes=['pref:pref_map', 'pref:pref_names', 'pref:pref_values', 'pref:pref_date'], evidence='SRC Main.java:1544-1599')

# ---------------------------------------------------------------- Data (daily rates) per listener
DATA_LISTENER = {'MAIN': 'Main', 'WIDGET': 'CurrencyWidgetUpdate'}
for ctx, lst in DATA_LISTENER.items():
    note = 'The result goes to whoever last called Data.getInstance (a static listener shared by Main and the widget service)'
    e('Data.startParse@' + ctx, 'Data.lambda$startParse$2@' + ctx, 'ASYNC', 'executor.execute(...): worker thread',
      guard='parsing == false (no download already running)', reads=['field:Data.parsing'], evidence='SRC Data.java:97-101')
    e('Data.lambda$startParse$2@' + ctx, 'Parser.<init>', 'CALL', 'new Parser()', evidence='SRC Data.java:104')
    e('Data.lambda$startParse$2@' + ctx, 'Parser.startParser(String)', 'CALL', 'parser.startParser(url) downloads eurofxref-daily.xml',
      reads=['net:https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'], evidence='SRC Data.java:107')
    e('Data.lambda$startParse$2@' + ctx, 'Data.lambda$startParse$0@' + ctx, 'ASYNC', 'Download failed: handler.post(() -> listener.onDateResult(null))',
      guard='startParser returned false and listener != null', evidence='SRC Data.java:107-112', note=note)
    e('Data.lambda$startParse$2@' + ctx, 'Data.lambda$startParse$1@' + ctx, 'ASYNC', 'Download parsed: handler.post(...) back to the main thread',
      guard='startParser returned true and listener != null', env=ENV_ECB, evidence='SRC Data.java:115-122', note=note)
    e('Data.lambda$startParse$0@' + ctx, lst + '.onDateResult', 'CALL', 'listener.onDateResult(null): status shows failure', evidence='SRC Data.java:111')
    e('Data.lambda$startParse$1@' + ctx, lst + '.onDateResult', 'CALL', 'listener.onDateResult(parser.getDate())', evidence='SRC Data.java:120')
    e('Data.lambda$startParse$1@' + ctx, 'Parser.getDate', 'CALL', 'parser.getDate()', evidence='SRC Data.java:120')
    e('Data.lambda$startParse$1@' + ctx, 'Parser.getMap', 'CALL', 'parser.getMap()', evidence='SRC Data.java:121')
    e('Data.lambda$startParse$1@' + ctx, lst + '.onDataResult', 'CALL', 'listener.onDataResult(parser.getMap())', evidence='SRC Data.java:121')

# ---------------------------------------------------------------- ChoiceDialog per caller
CHOICE_CALLER = {'MAIN': 'Main', 'CHART': 'ChartActivity'}
for ctx, caller in CHOICE_CALLER.items():
    D, S = 'S_CHOICE_DISPLAY@' + ctx, 'S_CHOICE_SELECT@' + ctx
    cd = lambda m: 'ChoiceDialog.%s@%s' % (m, ctx)
    e(cd('<init>'), cd('onCreate'), 'LIFECYCLE', 'The system instantiates ChoiceDialog (dialog-themed activity), then onCreate',
      evidence='SRC ChoiceDialog.java:59; AndroidManifest.xml:31-33 (DialogTheme)')
    e(cd('onCreate'), 'ChoiceAdapter.<init>', 'CALL', 'new ChoiceAdapter(this, R.layout.choice, CURRENCIES, selectList)', evidence='SRC ChoiceDialog.java:124')
    e(cd('onCreate'), 'ChoiceAdapter.getCount', 'FRAMEWORK', 'listView.setAdapter(adapter)', evidence=FW_SETADAPTER)
    e(cd('onCreate'), 'ChoiceAdapter.getView', 'FRAMEWORK', 'First layout draws the rows', evidence=FW_SETADAPTER)
    e(cd('onCreate'), 'ChoiceDialog.onItemClick', 'REGISTER', 'listView.setOnItemClickListener(this)', evidence='SRC ChoiceDialog.java:108')
    e(cd('onCreate'), 'ChoiceDialog.onItemLongClick', 'REGISTER', 'listView.setOnItemLongClickListener(this)', evidence='SRC ChoiceDialog.java:109')
    e(cd('onCreate'), 'ChoiceDialog.onClick', 'REGISTER', 'cancel/clear/select.setOnClickListener(this)', evidence='SRC ChoiceDialog.java:112-119')
    e(cd('onCreate'), D, 'ENTERS', 'Picker shown, nothing selected (Clear/Select disabled in choose.xml)',
      evidence='SRC ChoiceDialog.java:96-129; res/layout/choose.xml:39,47')
    for pg in (D, S):
        e(pg, 'ChoiceAdapter.getItemId', 'FRAMEWORK', 'Tapping a row: adapter.getItemId(position)', evidence=FW_ITEMID_CLICK)
        e(pg, cd('onSaveInstanceState'), 'SYSTEM', 'Rotation or Home: state saved before onStop (API 27 order)', gui=['Rotate the screen', 'or press Home'],
          evidence=FW_SAVESTATE)
        e(pg, caller + '.onActivityResult@CANCEL', 'RESULT', 'Back closes the picker with the default RESULT_CANCELED', gui=['Press Back'],
          evidence=AOSP + 'app/Activity.java:824,5503; ' + AOSP + 'app/ActivityThread.java:4253-4264')
    e(D, cd('onItemClick'), 'GUI', 'Tap a currency: it is picked and the picker closes', gui=['Tap any currency in the picker'],
      evidence='SRC ChoiceDialog.java:229-237')
    e(cd('onItemClick'), caller + '.onActivityResult@OK', 'RESULT', 'DISPLAY_MODE: setResult(RESULT_OK, CHOICE=[position]); finish()',
      guard='mode == DISPLAY_MODE', writes=['intent:choice'], evidence='SRC ChoiceDialog.java:230-236')
    e(D, cd('onItemLongClick'), 'GUI', 'Long-press a currency: multi-select starts', gui=['Long-press any currency'], evidence='SRC ChoiceDialog.java:263-276')
    e(S, cd('onItemLongClick'), 'GUI', 'Long-press: the selection restarts from this row', gui=['Long-press a currency'], evidence='SRC ChoiceDialog.java:263-276')
    e(cd('onItemLongClick'), 'ChoiceAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', evidence='SRC ChoiceDialog.java:275')
    e(cd('onItemLongClick'), S, 'ENTERS', 'mode = SELECT_MODE; Clear/Select enabled', evidence='SRC ChoiceDialog.java:266-274')
    e(D, cd('onClick'), 'GUI', 'Tap Cancel (Clear and Select are disabled)', gui=['Tap Cancel'], evidence='SRC ChoiceDialog.java:190-193')
    e(S, cd('onItemClick'), 'GUI', 'Tap a currency to toggle it', gui=['Tap a currency'], evidence='SRC ChoiceDialog.java:240-257')
    e(cd('onItemClick'), 'ChoiceAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', guard='mode == SELECT_MODE', evidence='SRC ChoiceDialog.java:256')
    e(cd('onItemClick'), D, 'ENTERS', 'Last selection removed: back to DISPLAY_MODE', guard='mode == SELECT_MODE and the selection becomes empty',
      evidence='SRC ChoiceDialog.java:247-254')
    e(S, cd('onClick'), 'GUI', 'Tap Select, Clear or Cancel', gui=['Tap Select', 'or tap Clear', 'or tap Cancel'], evidence='SRC ChoiceDialog.java:183-217')
    e(cd('onClick'), D, 'ENTERS', 'Clear: selection emptied, buttons disabled', guard='Clear tapped', evidence='SRC ChoiceDialog.java:196-206')
    e(cd('onClick'), 'ChoiceAdapter.getView', 'FRAMEWORK', 'Clear: adapter.notifyDataSetChanged()', guard='Clear tapped', evidence='SRC ChoiceDialog.java:205')
    e(cd('onClick'), caller + '.onActivityResult@OK', 'RESULT', 'Select: setResult(RESULT_OK, CHOICE=selectList); finish()',
      guard='Select tapped (SELECT_MODE)', writes=['intent:choice'], evidence='SRC ChoiceDialog.java:209-215')
    e(cd('onClick'), caller + '.onActivityResult@CANCEL', 'RESULT', 'Cancel: setResult(RESULT_CANCELED); finish()', guard='Cancel tapped',
      evidence='SRC ChoiceDialog.java:190-193')
    e(cd('onSaveInstanceState'), cd('onRestoreInstanceState'), 'SYSTEM',
      'Rotation: the picker is recreated (new instance: onCreate, then onRestoreInstanceState with the saved selection)',
      guard='activity recreated (rotation), not Home', evidence=AOSP + 'app/ActivityThread.java:2747-2751; SRC ChoiceDialog.java:134-179')
    e(cd('onSaveInstanceState'), cd('<init>'), 'SYSTEM', 'Rotation recreates the picker', guard='rotation', evidence=FW_RELAUNCH)
    e(cd('onRestoreInstanceState'), 'ChoiceAdapter.getView', 'FRAMEWORK', 'adapter.notifyDataSetChanged()', evidence='SRC ChoiceDialog.java:166')
    e(cd('onRestoreInstanceState'), D, 'ENTERS', 'No saved selection: DISPLAY_MODE', guard='saved list empty', evidence='SRC ChoiceDialog.java:146-153')
    e(cd('onRestoreInstanceState'), S, 'ENTERS', 'Saved selection restored: SELECT_MODE', guard='saved list not empty', evidence='SRC ChoiceDialog.java:156-163')

# ---------------------------------------------------------------- ChartActivity
e('ChartActivity.<init>', 'ChartActivity.onCreate', 'LIFECYCLE', 'The system instantiates ChartActivity, then onCreate', evidence='SRC ChartActivity.java:116')
e('ChartActivity.onCreate', 'Singleton.getInstance', 'CALL', 'instance = Singleton.getInstance(this) (the instance field is always null in a new activity)',
  reads=['intent:chart_list'], writes=['static:Singleton.listener'], evidence='SRC ChartActivity.java:163-171')
e('Singleton.getInstance', 'Singleton.<init>', 'CALL', 'instance == null -> new Singleton()', guard='first call in this process', evidence='SRC Singleton.java:57-58')
e('ChartActivity.onCreate', 'ChartActivity$DateAxisValueFormatter.<init>', 'CALL', 'xAxis.setValueFormatter(new DateAxisValueFormatter())', evidence='SRC ChartActivity.java:235')
e('ChartActivity.onCreate', 'Singleton.isParsing', 'CALL', 'instance.isParsing(): title shows "Updating" while a download runs', reads=['static:Singleton.parsing'],
  evidence='SRC ChartActivity.java:266')
e('ChartActivity.onCreate', 'ChartActivity.lambda$onCreate$0', 'REGISTER', 'customView.setOnClickListener(v -> invert)', evidence='SRC ChartActivity.java:257-263')
e('ChartActivity.onCreate', 'ChartActivity.onResume', 'LIFECYCLE', 'onStart -> onResume', evidence='SRC ChartActivity.java:285')
e('ChartActivity.onResume', 'Singleton.getInstance', 'CALL', 'instance = Singleton.getInstance(this)', evidence='SRC ChartActivity.java:298')
e('ChartActivity.onResume', 'Singleton.getMap', 'CALL', 'histMap = instance.getMap(): history kept from an earlier chart visit',
  reads=['static:Singleton.instance.map'], evidence='SRC ChartActivity.java:301-302')
e('ChartActivity.onResume', 'ChartActivity.onCreateOptionsMenu', 'FRAMEWORK', 'Menu created after the window attaches', evidence=FW_MENU)
e('ChartActivity.onResume', 'ChartActivity.onPrepareOptionsMenu', 'FRAMEWORK', 'Prepared right after creation (Invert disabled while histMap == null)',
  evidence=FW_MENU + '; SRC ChartActivity.java:479')
e('ChartActivity.onResume', 'ChartActivity.showToast(int,Object[])', 'CALL', 'Network check failed: toast No connection / No Wi-Fi / Roaming',
  guard='histMap == null and not (' + NET_GUARD + ')', reads=NET_READS, env=ENV_NONET, evidence='SRC ChartActivity.java:401-424')
e('ChartActivity.onResume', 'Singleton.startParse', 'CALL', 'instance.startParse(ECB_QUARTER_URL)', guard='histMap == null and ' + NET_GUARD,
  reads=NET_READS, env=ENV_NET, evidence='SRC ChartActivity.java:427-428')
e('ChartActivity.onResume', 'S_CHART_LOADING', 'ENTERS', 'No history yet: "Updating", Invert disabled', guard='histMap == null', evidence='SRC ChartActivity.java:305,479')
e('ChartActivity.onResume', 'S_CHART_LOADED', 'ENTERS', 'History kept from an earlier visit: the chart is drawn at once', guard='histMap != null',
  needs_state=STATE_CHART, env=ENV_ECB, evidence='SRC ChartActivity.java:305-397')
e('ChartActivity.onResume', 'ChartActivity$DateAxisValueFormatter.getFormattedValue', 'FRAMEWORK', 'chart.setData + invalidate: X axis labels are formatted',
  guard='histMap != null', needs_state=STATE_CHART, env=ENV_ECB,
  evidence='SRC ChartActivity.java:235,378-379; ' + MPCHART)

e('Singleton.startParse', 'Singleton.lambda$startParse$1', 'ASYNC', 'executor.execute(...): worker thread', guard='parsing == false',
  reads=['static:Singleton.parsing'], evidence='SRC Singleton.java:104-108')
e('Singleton.lambda$startParse$1', 'ChartParser.<init>', 'CALL', 'new ChartParser()', evidence='SRC Singleton.java:111')
e('Singleton.lambda$startParse$1', 'ChartParser.startParser(String)', 'CALL', 'parser.startParser(url): 90-day or full history XML',
  reads=['net:https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml', 'net:https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml'],
  evidence='SRC Singleton.java:114')
e('Singleton.lambda$startParse$1', 'Singleton.lambda$startParse$0', 'ASYNC', 'Download parsed: handler.post(...) to the main thread (nothing is posted on failure)',
  guard='startParser returned true and listener != null', env=ENV_ECB, evidence='SRC Singleton.java:114-128')
e('Singleton.lambda$startParse$0', 'ChartActivity.onDateResult', 'CALL', 'listener.onDateResult(parser.getDate()) (empty method)', evidence='SRC Singleton.java:125')
e('Singleton.lambda$startParse$0', 'ChartParser.getDate', 'CALL', 'parser.getDate()', evidence='SRC Singleton.java:125')
e('Singleton.lambda$startParse$0', 'ChartParser.getMap', 'CALL', 'parser.getMap()', evidence='SRC Singleton.java:126')
e('Singleton.lambda$startParse$0', 'ChartActivity.onDataResult', 'CALL', 'listener.onDataResult(parser.getMap())', evidence='SRC Singleton.java:126')
e('ChartParser.startParser(String)', 'ChartParser$Handler.<init>', 'CALL', 'new Handler() after the HTTPS stream opened', env=ENV_ECB, evidence='SRC ChartParser.java:68-70')
e('ChartParser.startParser(String)', 'ChartParser$Handler.startElement', 'FRAMEWORK', 'Xml.parse SAX callbacks', env=ENV_ECB, evidence='SRC ChartParser.java:71')

e('ChartActivity.onDataResult', 'S_CHART_LOADED', 'ENTERS', 'Chart drawn; invalidateOptionsMenu enables Invert', guard='map not empty', evidence='SRC ChartActivity.java:915-1007')
e('ChartActivity.onDataResult', 'ChartActivity.onCreateOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu()', guard='map not empty', evidence=FW_MENU + '; SRC ChartActivity.java:1007')
e('ChartActivity.onDataResult', 'ChartActivity.onPrepareOptionsMenu', 'FRAMEWORK', 'invalidateOptionsMenu(): Invert now enabled', guard='map not empty',
  evidence=FW_MENU + '; SRC ChartActivity.java:1007')
e('ChartActivity.onDataResult', 'ChartActivity$DateAxisValueFormatter.getFormattedValue', 'FRAMEWORK', 'chart.setData + invalidate formats the axis labels',
  guard='map not empty', evidence='SRC ChartActivity.java:235,991-992; ' + MPCHART)
e('ChartActivity.onDataResult', 'ChartActivity.showToast(int,Object[])', 'CALL', 'Empty map: toast "Update failed"', guard='map empty', evidence='SRC ChartActivity.java:1010-1014')
e('ChartActivity.showToast(int,Object[])', 'ChartActivity.showToast(String,Object[])', 'CALL', 'showToast(getString(id), args)', evidence='SRC ChartActivity.java:1026-1027')
e('ChartActivity.showToast(String,Object[])', 'ChartActivity.showToast(String)', 'CALL', 'showToast(String.format(format, args))', evidence='SRC ChartActivity.java:1033-1034')

CHART_GUI = {
    'LOADING': (['Tap the Up arrow, New chart, Refresh or History icon', 'Tap More options (⋮) -> Range -> Week / Month / Quarter / Year / Years / Max'],
                'Invert is disabled while loading'),
    'LOADED': (['Tap the Up arrow, Invert, New chart, Refresh or History icon', 'Tap More options (⋮) -> Range -> Week / Month / Quarter / Year / Years / Max'],
               None),
}
RANGE = (('action_week', 'onWeekClick', '542-543'), ('action_month', 'onMonthClick', '546-547'), ('action_quarter', 'onQuarterClick', '550-551'),
         ('action_year', 'onYearClick', '554-555'), ('action_years', 'onYearsClick', '558-559'), ('action_max', 'onMaxClick', '562-563'))
for st, (gui, guard) in CHART_GUI.items():
    pg, ois = 'S_CHART_' + st, 'ChartActivity.onOptionsItemSelected@' + st
    e(pg, ois, 'GUI', 'Tap a menu item', gui=gui, guard=guard, evidence='SRC res/menu/chart.xml; ChartActivity.java:514',
      note='Range owns a submenu: tapping it dispatches action_range to the default branch first (prompt checklist item 3)')
    e(ois, 'Main.onResume', 'SYSTEM', 'case android.R.id.home: finish(); Main resumes', evidence='SRC ChartActivity.java:205,521-523')
    e(ois, 'ChartActivity.onNewClick', 'CALL', 'switch case R.id.action_new_chart', evidence='SRC ChartActivity.java:530-531')
    e(ois, 'ChartActivity.onRefreshClick', 'CALL', 'switch case R.id.action_refresh (90-day history)', evidence='SRC ChartActivity.java:534-535')
    e(ois, 'ChartActivity.onRefreshClick', 'CALL', 'switch case R.id.action_hist (full history)', evidence='SRC ChartActivity.java:538-539')
    for item, h, line in RANGE:
        e(ois, 'ChartActivity.' + h, 'CALL', 'switch case R.id.%s (More options -> Range submenu)' % item, evidence='SRC ChartActivity.java:' + line)
    e(pg, 'ChartActivity.onPrepareOptionsMenu', 'GUI', 'Open the overflow menu: onPrepareOptionsMenu runs again', gui=['Tap More options (⋮)'],
      evidence=AOSP + 'app/Activity.java:3404-3406; ' + AOSP + 'policy/PhoneWindow.java:659,1265')
    e(pg, 'ChartActivity.lambda$onCreate$0@' + st, 'GUI', 'Tap the currency-pair title in the action bar', gui=['Tap the currency-pair title'],
      guard='does nothing while loading (histMap == null)' if st == 'LOADING' else None, evidence='SRC ChartActivity.java:208-212,259-263')
    e(pg, 'ChartActivity.onPause', 'SYSTEM', 'ChartActivity loses the foreground', gui=['Press Home', 'or Back / Up', 'or New chart (picker on top)', 'or rotate'],
      evidence='SRC ChartActivity.java:433')
    e(pg, 'Main.onResume', 'SYSTEM', 'Back finishes ChartActivity; Main resumes', gui=['Press Back'], evidence=FW_BACK)
    e(pg, 'ChartActivity.onSaveInstanceState', 'SYSTEM', 'Home or rotation: state saved (not on Back/Up, not under the floating picker)',
      gui=['Press Home', 'or rotate'], guard='the chart is stopped (Home or rotation); it is only paused, and nothing is saved, while the floating picker is on top', evidence=FW_SAVESTATE)
e('ChartActivity.onOptionsItemSelected@LOADED', 'ChartActivity.onInvertClick', 'CALL', 'switch case R.id.action_invert', guard='Invert enabled (histMap != null)',
  evidence='SRC ChartActivity.java:479,526-527')
e('ChartActivity.lambda$onCreate$0@LOADED', 'ChartActivity.onInvertClick', 'CALL', 'histMap != null -> onInvertClick()', guard='histMap != null (S_CHART_LOADED)',
  evidence='SRC ChartActivity.java:261-262')
e('ChartActivity.onInvertClick', 'ChartActivity$DateAxisValueFormatter.getFormattedValue', 'FRAMEWORK', 'Chart redraw formats the axis labels',
  evidence='SRC ChartActivity.java:235,644-647; ' + MPCHART)
e('ChartActivity.onNewClick', 'ChoiceDialog.<init>@CHART', 'INTENT', 'startActivityForResult(ChoiceDialog, 0)', evidence='SRC ChartActivity.java:673-674')
e('ChartActivity.onRefreshClick', 'ChartActivity.showToast(int,Object[])', 'CALL', 'Toast No connection / No Wi-Fi / Roaming', guard='not (' + NET_GUARD + ')',
  reads=NET_READS, env=ENV_NONET, evidence='SRC ChartActivity.java:684-706')
e('ChartActivity.onRefreshClick', 'Singleton.startParse', 'CALL', 'instance.startParse(url)', guard=NET_GUARD, reads=NET_READS, env=ENV_NET,
  evidence='SRC ChartActivity.java:710-718')
for _, h, _ in RANGE:
    e('ChartActivity.' + h, 'ChartActivity.updateRange', 'CALL', 'range = ...; item.setChecked(true); updateRange()', evidence='SRC ChartActivity.java:724-781')
e('ChartActivity.onPause', 'Singleton.setList', 'CALL', 'instance.setList([firstIndex, secondIndex])', writes=['static:Singleton.instance.list'], evidence='SRC ChartActivity.java:439-444')
e('ChartActivity.onPause', 'Singleton.setMap', 'CALL', 'instance.setMap(histMap)', writes=['static:Singleton.instance.map'], evidence='SRC ChartActivity.java:445')
e('ChartActivity.onPause', 'Singleton.getInstance', 'CALL', 'Singleton.getInstance(null): disconnect callbacks', evidence='SRC ChartActivity.java:449')
e('ChartActivity.onPause', 'S_CHART_PAUSED', 'ENTERS', 'Chart in the background or under the picker', evidence='SRC ChartActivity.java:433')
e('S_CHART_PAUSED', 'ChartActivity.onResume', 'SYSTEM', 'Return to the chart', gui=['Return via recents or the launcher icon'], evidence=FW_RESUME)
e('ChartActivity.onSaveInstanceState', 'ChartActivity.<init>', 'SYSTEM', 'Rotation recreates the chart; onCreate restores invert and range',
  guard='rotation', evidence='SRC ChartActivity.java:155-159; ' + FW_RELAUNCH)
for res in ('OK', 'CANCEL'):
    e('ChartActivity.onActivityResult@' + res, 'ChartActivity.onResume', 'LIFECYCLE', 'onActivityResult is delivered before onResume', evidence=FW_RESUME)
e('ChartActivity.onActivityResult@OK', 'ChartActivity$DateAxisValueFormatter.getFormattedValue', 'FRAMEWORK', 'Redraw for the newly picked pair',
  guard='RESULT_OK and history loaded', env=ENV_ECB, evidence='SRC ChartActivity.java:235,879-886; ' + MPCHART)
e('ChartActivity.onActivityResult@OK', 'S_EXIT', 'ENTERS', 'Crash: RESULT_OK while no history was ever loaded -> entryList.clear() on null (NullPointerException)',
  guard='RESULT_OK and entryList == null (New chart used while offline or before the download finished)',
  evidence='SRC ChartActivity.java:836,312,925 (entryList is only assigned at 312 and 925)', note='Hazard candidate; not checked on a device')

# ---------------------------------------------------------------- Help
e('HelpActivity.<init>', 'HelpActivity.onCreate', 'LIFECYCLE', 'The system instantiates HelpActivity, then onCreate', evidence='SRC HelpActivity.java:49')
e('HelpActivity.onCreate', 'HelpActivity.read', 'CALL', 'read(this, R.raw.help)', reads=['res:raw/help.html'], evidence='SRC HelpActivity.java:89')
e('HelpActivity.onCreate', 'S_HELP', 'ENTERS', 'Help text shown with an Up arrow', evidence='SRC HelpActivity.java:86-99')
e('S_HELP', 'HelpActivity.onOptionsItemSelected', 'GUI', 'Tap the Up arrow', gui=['Tap the Up arrow (top-left)'], evidence='SRC HelpActivity.java:99,104')
e('HelpActivity.onOptionsItemSelected', 'Main.onResume', 'SYSTEM', 'case android.R.id.home: finish(); Main resumes', evidence='SRC HelpActivity.java:111-112')
e('S_HELP', 'Main.onResume', 'SYSTEM', 'Back finishes HelpActivity; Main resumes', gui=['Press Back'], evidence=FW_BACK)

# ---------------------------------------------------------------- Settings
e('SettingsActivity.<init>', 'SettingsActivity.onCreate', 'LIFECYCLE', 'The system instantiates SettingsActivity, then onCreate', evidence='SRC SettingsActivity.java:41')
e('SettingsActivity.onCreate', 'SettingsFragment.<init>', 'CALL', 'replace(android.R.id.content, new SettingsFragment())', evidence='SRC SettingsActivity.java:79-81')
e('SettingsFragment.<init>', 'SettingsFragment.onCreate', 'LIFECYCLE', 'The fragment transaction commits: fragment onCreate', evidence=FW_FRAGMENT)
e('SettingsFragment.onCreate', 'AboutPreference.<init>', 'FRAMEWORK', 'addPreferencesFromResource inflates preferences.xml; the inflater constructs AboutPreference(Context, AttributeSet)',
  evidence='SRC SettingsFragment.java:48; res/xml/preferences.xml (org.billthefarmer.currency.AboutPreference)')
e('SettingsFragment.onCreate', 'SettingsFragment.onResume', 'LIFECYCLE', 'The fragment resumes with the activity', evidence=AOSP + 'app/FragmentManager.java:1322')
e('SettingsFragment.onResume', 'SettingsFragment.onSharedPreferenceChanged', 'REGISTER', 'registerOnSharedPreferenceChangeListener(this)', evidence='SRC SettingsFragment.java:79-80')
e('SettingsFragment.onResume', 'S_SETTINGS', 'ENTERS', 'Settings list shown', evidence='SRC SettingsFragment.java:76-81')
e('S_SETTINGS', 'SettingsFragment.onPreferenceTreeClick', 'GUI', 'Tap any settings row (Preference.performClick -> the fragment tree-click listener)',
  gui=['Tap any row (Wi-Fi only, Roaming, Widget entry, Fraction digits, Chart fill, Theme, About)'],
  evidence=AOSP + 'preference/Preference.java:1129-1146; ' + AOSP + 'preference/PreferenceFragment.java:227,333')
e('S_SETTINGS', 'SettingsFragment.onSharedPreferenceChanged', 'GUI', 'Tap a checkbox row: the value flips and the listener fires',
  gui=['Tap the Wi-Fi only, Roaming or Chart fill row'], writes=['pref:pref_wifi', 'pref:pref_roaming', 'pref:pref_fill'],
  evidence='SRC res/xml/preferences.xml; ' + AOSP + 'preference/TwoStatePreference.java:61-66,81; ' + AOSP + 'preference/Preference.java:1878; ' + AOSP + 'app/SharedPreferencesImpl.java:551-561')
for dlg, row, key in (('ENTRY', 'Widget entry', 'pref_entry'), ('DIGITS', 'Fraction digits', 'pref_digits'), ('THEME', 'Theme', 'pref_theme')):
    e('S_SETTINGS', 'S_DLG_' + dlg, 'ENTERS', 'Tap %s: list dialog opens' % row, gui=['Tap the %s row' % row],
      evidence='SRC res/xml/preferences.xml (ListPreference %s)' % key)
    e('S_DLG_' + dlg, 'SettingsFragment.onSharedPreferenceChanged', 'GUI', 'Pick a different value', gui=['Pick a value different from the current one'],
      guard='new value != old value', writes=['pref:' + key], evidence='SRC SettingsFragment.java:113-137; ' + AOSP + 'preference/ListPreference.java:148,277-282; ' + AOSP + 'app/SharedPreferencesImpl.java:551-561')
    e('S_DLG_' + dlg, 'S_SETTINGS', 'ENTERS', 'The dialog closes (picking the current value changes nothing)', gui=['Pick a value, or tap Cancel / Back'],
      evidence=AOSP + 'preference/DialogPreference.java:386-395')
e('SettingsFragment.onSharedPreferenceChanged', 'SettingsActivity.<init>', 'SYSTEM', 'pref_theme changed: getActivity().recreate()',
  guard='key == pref_theme and SDK != 23', evidence='SRC SettingsFragment.java:132-136')
e('SettingsFragment.onSharedPreferenceChanged', 'S_SETTINGS', 'ENTERS', 'Summary of Widget entry / Fraction digits updated', evidence='SRC SettingsFragment.java:116-130')
e('S_SETTINGS', 'AboutPreference.onBindDialogView', 'GUI', 'Tap About: the dialog view is bound when shown', gui=['Tap the About row'],
  evidence=AOSP + 'preference/DialogPreference.java:274-300')
e('AboutPreference.onBindDialogView', 'S_DLG_ABOUT', 'ENTERS', 'About dialog shown (version, build date, links)', evidence='SRC AboutPreference.java:50-97')
e('S_DLG_ABOUT', 'S_SETTINGS', 'ENTERS', 'Tap OK or Back', gui=['Tap OK or press Back'], evidence=AOSP + 'preference/DialogPreference.java:386-395')
e('S_SETTINGS', 'SettingsActivity.onOptionsItemSelected', 'GUI', 'Tap the Up arrow', gui=['Tap the Up arrow (top-left)'], evidence='SRC SettingsActivity.java:87,94')
e('SettingsActivity.onOptionsItemSelected', 'Main.onResume', 'SYSTEM', 'case android.R.id.home: finish(); Main resumes (and recreates itself if the theme changed)',
  evidence='SRC SettingsActivity.java:100-101')
e('S_SETTINGS', 'SettingsFragment.onPause', 'SYSTEM', 'Settings loses the foreground', gui=['Press Home', 'or Back / Up', 'or change Theme (recreate)'],
  evidence='SRC SettingsFragment.java:85')
e('S_SETTINGS', 'Main.onResume', 'SYSTEM', 'Back finishes SettingsActivity; Main resumes', gui=['Press Back'], evidence=FW_BACK)
e('SettingsFragment.onPause', 'S_SETTINGS_PAUSED', 'ENTERS', 'Settings in the background', evidence='SRC SettingsFragment.java:85-89')
e('S_SETTINGS_PAUSED', 'SettingsFragment.onResume', 'SYSTEM', 'Return to Settings', gui=['Return via recents'], evidence=AOSP + 'app/FragmentManager.java:1322')

# ---------------------------------------------------------------- home-screen widget
ADD_GUI = ['Home screen: add the Currency widget (long-press an empty spot -> Widgets -> drag Currency onto the screen)']
e('S_ENTRY', 'CurrencyWidgetProvider.<init>@UPDATE', 'ENTRY', 'Add the Currency widget: the system binds a widget id and sends APPWIDGET_UPDATE to the provider',
  gui=ADD_GUI, evidence=AOSP + 'appwidget/AppWidgetServiceImpl.java:1132-1139,2277-2290; SRC AndroidManifest.xml:58-66',
  note='Happens outside the app package: tools confined to the app (Monkey -p, APE) cannot do it')
e('S_ENTRY', 'CurrencyWidgetConfigure.<init>@ADD', 'ENTRY', 'After the widget is dropped the launcher starts the configure activity (android:configure)',
  gui=ADD_GUI, evidence='SRC res/xml/widget.xml (android:configure); SRC AndroidManifest.xml:42-48; ' + AOSP + 'appwidget/AppWidgetServiceImpl.java:992; INFERRED the launcher (another app) calls it after the widget id is bound (launcher source not read)')
for b in ('UPDATE', 'DELETED'):
    e('CurrencyWidgetProvider.<init>@' + b, 'CurrencyWidgetProvider.onReceive@' + b, 'LIFECYCLE',
      'The system instantiates the receiver and calls onReceive (APPWIDGET_%s)' % b,
      reads=['intent:EXTRA_UPDATE_DONE'], evidence='SRC CurrencyWidgetProvider.java:67-76')
e('CurrencyWidgetProvider.onReceive@UPDATE', 'CurrencyWidgetProvider.onUpdate', 'FRAMEWORK', 'super.onReceive (AppWidgetProvider): APPWIDGET_UPDATE with a non-empty id list -> onUpdate',
  guard='at least one Currency widget placed',
  evidence=AOSP + 'appwidget/AppWidgetProvider.java:57-66')
e('CurrencyWidgetProvider.onReceive@DELETED', 'CurrencyWidgetProvider.onDeleted', 'FRAMEWORK', 'super.onReceive: APPWIDGET_DELETED -> onDeleted', guard='a widget was removed',
  evidence=AOSP + 'appwidget/AppWidgetProvider.java:69-73')
e('CurrencyWidgetProvider.onUpdate', 'Main.<clinit>', 'CALL', 'First access to Main.CURRENCIES / currencyIndex initialises Main in a widget-only process',
  guard='class Main not loaded yet in this process', evidence='SRC CurrencyWidgetProvider.java:213-215')
e('CurrencyWidgetProvider.onUpdate', 'Main.currencyIndex', 'CALL', 'Main.currencyIndex(entryName) for each widget', evidence='SRC CurrencyWidgetProvider.java:213')
e('CurrencyWidgetProvider.onUpdate', 'CurrencyWidgetUpdate.<init>', 'INTENT', 'context.startService(CurrencyWidgetUpdate)',
  guard='updateDone == false and ' + NET_GUARD + '; on API 26+ the start throws (and is caught) if the app is in the background',
  reads=NET_READS, env=ENV_NET, evidence='SRC CurrencyWidgetProvider.java:275-312; ' + AOSP + 'am/ActiveServices.java:365-392; ' + AOSP + 'am/ActivityManagerService.java:8548-8556,8607-8660; ' + AOSP + 'app/ContextImpl.java:1521-1524')
e('CurrencyWidgetProvider.onUpdate', 'S_HOME_WIDGET', 'ENTERS', 'appWidgetManager.updateAppWidget: the widget shows the current values', guard='a widget is placed',
  evidence='SRC CurrencyWidgetProvider.java:244-271')
e('CurrencyWidgetProvider.onDeleted', 'S_ENTRY', 'ENTERS', 'Widget removed; its stored entry is deleted', writes=['pref:<appWidgetId>'],
  evidence='SRC CurrencyWidgetProvider.java:316-327')

for ctx in ('ADD', 'RECONFIG'):
    wc = lambda m: 'CurrencyWidgetConfigure.%s@%s' % (m, ctx)
    page = 'S_WIDGET_CONFIG@' + ctx
    e(wc('<init>'), wc('onCreate'), 'LIFECYCLE', 'The system instantiates CurrencyWidgetConfigure (dialog theme), then onCreate', evidence='SRC CurrencyWidgetConfigure.java:51')
    e(wc('onCreate'), 'Main.<clinit>', 'CALL', 'Main.CURRENCIES access initialises Main if needed', guard='class Main not loaded yet', evidence='SRC CurrencyWidgetConfigure.java:156-157')
    e(wc('onCreate'), 'Main.currencyIndex', 'CALL', 'Main.currencyIndex(name) for each saved list entry', reads=['pref:pref_names'], evidence='SRC CurrencyWidgetConfigure.java:128-158')
    e(wc('onCreate'), 'ChoiceAdapter.<init>', 'CALL', 'new ChoiceAdapter(this, R.layout.choice, currencyList, selectList)', evidence='SRC CurrencyWidgetConfigure.java:161')
    e(wc('onCreate'), 'ChoiceAdapter.getCount', 'FRAMEWORK', 'listView.setAdapter(adapter)', evidence=FW_SETADAPTER)
    e(wc('onCreate'), 'ChoiceAdapter.getView', 'FRAMEWORK', 'First layout draws the rows', evidence=FW_SETADAPTER)
    e(wc('onCreate'), 'CurrencyWidgetConfigure.lambda$onCreate$0', 'REGISTER', 'listView.setOnItemClickListener(lambda)', evidence='SRC CurrencyWidgetConfigure.java:96')
    e(wc('onCreate'), 'CurrencyWidgetConfigure.lambda$onCreate$1', 'REGISTER', 'cancel.setOnClickListener(lambda)', evidence='SRC CurrencyWidgetConfigure.java:121')
    e(wc('onCreate'), page, 'ENTERS', 'Dialog listing the Main list currencies', evidence='SRC CurrencyWidgetConfigure.java:88-165')
    e(page, wc('lambda$onCreate$0'), 'GUI', 'Tap a currency for the widget', gui=['Tap a currency in the widget setup list'],
      evidence='SRC CurrencyWidgetConfigure.java:96-118')
    e(page, 'ChoiceAdapter.getItemId', 'FRAMEWORK', 'Tapping a row: adapter.getItemId(position)', evidence=FW_ITEMID_CLICK)
    e(wc('lambda$onCreate$0'), 'CurrencyWidgetProvider.<init>@UPDATE', 'INTENT', 'sendBroadcast(APPWIDGET_UPDATE, ids=[this widget]) without EXTRA_UPDATE_DONE',
      writes=['pref:<appWidgetId>'], evidence='SRC CurrencyWidgetConfigure.java:103-112; ' + AOSP + 'am/ActivityManagerService.java:19199-19224 (an APPWIDGET_UPDATE sent by an app is limited to the caller package); ' + AOSP + 'am/BroadcastQueue.java:1267-1279 (the background skip needs component and package both null)',
      note='Implicit by action; limited to the caller package like the broadcast of Main.updateWidgets')
    e(wc('lambda$onCreate$0'), 'S_HOME_WIDGET', 'ENTERS', 'setResult(RESULT_OK); finish(): home screen with the widget', evidence='SRC CurrencyWidgetConfigure.java:114-117')
    e(page, wc('lambda$onCreate$1'), 'GUI', 'Tap Cancel', gui=['Tap Cancel'], evidence='SRC CurrencyWidgetConfigure.java:121-125')
e('CurrencyWidgetConfigure.lambda$onCreate$1@ADD', 'CurrencyWidgetProvider.<init>@DELETED', 'INTENT',
  'RESULT_CANCELED while placing: the launcher deletes the new widget id and APPWIDGET_DELETED reaches the provider',
  evidence=AOSP + 'appwidget/AppWidgetServiceImpl.java:1752-1767; INFERRED the launcher (another app) deletes a widget id whose configuration activity returned RESULT_CANCELED (launcher source not read)')
e('CurrencyWidgetConfigure.lambda$onCreate$1@ADD', 'S_ENTRY', 'ENTERS', 'Widget not added: plain home screen', evidence='INFERRED the launcher (another app) shows the plain home screen after a cancelled widget placement (launcher source not read)')
e('CurrencyWidgetConfigure.lambda$onCreate$1@RECONFIG', 'S_HOME_WIDGET', 'ENTERS', 'finish(): the widget is unchanged', evidence='SRC CurrencyWidgetConfigure.java:123-124')

e('S_HOME_WIDGET', 'Main.<init>', 'GUI', 'Tap the widget body: its PendingIntent opens Main', gui=['Tap the values on the widget'],
  guard='Main not already running (otherwise the existing task comes to the front)', evidence='SRC CurrencyWidgetProvider.java:237-248')
e('S_HOME_WIDGET', 'CurrencyWidgetRefresh.<init>', 'GUI', 'Tap the refresh icon on the widget', gui=['Tap the refresh icon on the widget'],
  evidence='SRC CurrencyWidgetProvider.java:218-223,249')
e('S_HOME_WIDGET', 'CurrencyWidgetConfigure.<init>@RECONFIG', 'GUI', 'Tap the configure icon on the widget', gui=['Tap the configure icon on the widget'],
  evidence='SRC CurrencyWidgetProvider.java:225-235,250')
e('S_HOME_WIDGET', 'CurrencyWidgetProvider.<init>@DELETED', 'GUI', 'Remove the widget: APPWIDGET_DELETED goes to the provider', gui=['Remove the widget (long-press it, drag it to Remove)'],
  evidence=AOSP + 'appwidget/AppWidgetServiceImpl.java:1752-1767,2290-2294')
e('S_HOME_WIDGET', 'CurrencyWidgetProvider.<init>@UPDATE', 'SYSTEM', 'Periodic update every hour (updatePeriodMillis = 3600000)', gui=['Wait up to an hour'],
  evidence='SRC res/xml/widget.xml (updatePeriodMillis); ' + AOSP + 'appwidget/AppWidgetServiceImpl.java:2311-2335')

e('CurrencyWidgetRefresh.<init>', 'CurrencyWidgetRefresh.onCreate', 'LIFECYCLE', 'The system instantiates the invisible activity (Theme.NoDisplay), then onCreate',
  evidence='SRC CurrencyWidgetRefresh.java:45; AndroidManifest.xml:51-53')
e('CurrencyWidgetRefresh.onCreate', 'CurrencyWidgetUpdate.<init>', 'INTENT', 'startService(CurrencyWidgetUpdate) from a foreground activity', guard=NET_GUARD,
  reads=NET_READS, env=ENV_NET, evidence='SRC CurrencyWidgetRefresh.java:56-78')
e('CurrencyWidgetRefresh.onCreate', 'S_HOME_WIDGET', 'ENTERS', 'finish(): the invisible activity closes', guard=NET_GUARD, evidence='SRC CurrencyWidgetRefresh.java:83')
e('CurrencyWidgetRefresh.onCreate', 'S_EXIT', 'ENTERS',
  'Network check fails: onCreate returns without finish(); a Theme.NoDisplay activity not finished by onResume throws IllegalStateException on API 23+',
  guard='not (' + NET_GUARD + ')', env=ENV_NONET, evidence='SRC CurrencyWidgetRefresh.java:65-74; ' + AOSP + 'app/Activity.java:7098-7121',
  note='Hazard candidate (crash); not checked on a device')

e('CurrencyWidgetUpdate.<init>', 'CurrencyWidgetUpdate.onCreate', 'LIFECYCLE', 'The system instantiates the service, then onCreate', evidence='SRC CurrencyWidgetUpdate.java:71')
e('CurrencyWidgetUpdate.onCreate', 'Data.getInstance', 'CALL', 'data = Data.getInstance(this): the service becomes the Data listener',
  writes=['static:Data.listener'], evidence='SRC CurrencyWidgetUpdate.java:74')
e('CurrencyWidgetUpdate.onCreate', 'CurrencyWidgetUpdate.onStartCommand', 'LIFECYCLE', 'startService -> onStartCommand', evidence='SRC CurrencyWidgetUpdate.java:86')
e('CurrencyWidgetUpdate.onStartCommand', 'CurrencyWidgetUpdate.startUpdate', 'CALL', 'startUpdate()', evidence='SRC CurrencyWidgetUpdate.java:91')
e('CurrencyWidgetUpdate.startUpdate', 'Data.startParse@WIDGET', 'CALL', 'data.startParse(ECB_DAILY_URL)', evidence='SRC CurrencyWidgetUpdate.java:100-101')
e('CurrencyWidgetUpdate.startUpdate', 'CurrencyWidgetUpdate.lambda$startUpdate$0', 'ASYNC', 'handler.postDelayed(..., 5000): restore the refresh icon after 5 s',
  evidence='SRC CurrencyWidgetUpdate.java:113-130')
e('CurrencyWidgetUpdate.onDataResult', 'CurrencyWidgetProvider.<init>@UPDATE', 'INTENT', 'sendBroadcast(APPWIDGET_UPDATE, EXTRA_UPDATE_DONE=true) with the new values',
  guard='map not empty', writes=['pref:pref_map', 'pref:pref_values'], evidence='SRC CurrencyWidgetUpdate.java:274-294; ' + AOSP + 'am/ActivityManagerService.java:19199-19224 (an APPWIDGET_UPDATE sent by an app is limited to the caller package); ' + AOSP + 'am/BroadcastQueue.java:1267-1279 (the background skip needs component and package both null)')
e('CurrencyWidgetUpdate.onDataResult', 'CurrencyWidgetUpdate.onDestroy', 'LIFECYCLE', 'stopSelf() -> onDestroy', evidence='SRC CurrencyWidgetUpdate.java:195-199,299')
e('CurrencyWidgetUpdate.onDestroy', 'Data.getInstance', 'CALL', 'Data.getInstance(null)', evidence='SRC CurrencyWidgetUpdate.java:145')


# ---------------------------------------------------------------- schema 2 hooks
import re


def EDIT(x):
    """Gates that the v1 graph kept only as a guard or in prose, now structured as ENV / STATE."""
    src, dst = x['src'].split('@')[0], x['dst'].split('@')[0]
    # a widget has to be placed first, through the launcher (another app)
    if (not x['env']) and ((x['kind'] == 'ENTRY' and dst in ('CurrencyWidgetProvider.<init>', 'CurrencyWidgetConfigure.<init>'))
                           or (src == 'CurrencyWidgetProvider.onReceive' and dst in ('CurrencyWidgetProvider.onUpdate', 'CurrencyWidgetProvider.onDeleted'))
                           or (src == 'CurrencyWidgetProvider.onUpdate' and dst == 'S_HOME_WIDGET')):
        x['env'] = ENV_WIDGET
    # a rotation of the device recreates the activity (Home is a key press and needs no gate)
    if (not x['env']) and re.match(r'Rotation(?! or Home)', x['trigger'] or ''):
        x['env'] = ENV_ROTATE
    # code that reads the bundled rates runs only while nothing was saved yet
    if (not x['needs_state']) and (x['guard'] or '').startswith('Data.map == null and pref_map not saved yet'):
        x['needs_state'] = STATE_FRESH


def CLASSIFY(x):
    """Edge classes that differ from the default of their kind (see SCHEMA_V2.md)."""
    src, dst = x['src'].split('@')[0], x['dst'].split('@')[0]
    if x['kind'] == 'INTENT' and dst == 'CurrencyWidgetProvider.<init>' and not src.startswith('CurrencyWidgetConfigure.lambda$onCreate$1'):
        return ('non_standard', 'implicit broadcast: Intent(ACTION_APPWIDGET_UPDATE) without a component, resolved by action name to the manifest receiver')
    if dst == 'AboutPreference.<init>':
        return ('non_standard', 'class named in res/xml/preferences.xml, constructed by the framework through reflection (GenericInflater.createItem)')
    if dst.startswith('ChartActivity$DateAxisValueFormatter'):
        return ('standard', 'callback registered with the third-party MPAndroidChart library (setValueFormatter); the library calls it')
    if x['kind'] == 'ENTRY' and dst == 'Main.<clinit>':
        return ('standard', 'JVM class initialisation')
    return None
