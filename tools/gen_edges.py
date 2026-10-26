"""Generate the framework-driven edges of a trigger graph from bytecode, AndroidManifest.xml and res/ XML.

Used by the graph_def.py of "generated" apps:

    import gen_edges
    gen_edges.apply(globals(), GDIR, '<App folder name in final_java_only>', cfg)

Everything the bytecode call graph (tools/extract_calls.py -> auto_calls.json) cannot see is added here as edges:
  entry points (manifest: application, launcher, exported components), lifecycle of components, pages (activities,
  fragments), UI / system callbacks of instantiated classes, lambdas, class-literal / action-string starts,
  XML-instantiated classes, activity results, permission results, static initialisers.
The model is deliberately an over-approximation: a callback is reachable once an instance of its class exists, an
instance exists once some reachable method constructs it. Methods that nothing reaches stay unreachable; build_graph.py
(AUTO_DEAD) reports them as DEAD.

cfg (per app, optional keys):
  GROUPS: [(regex on node name, 'needs'|'env'|'guard', text)]   gate every edge into a method of the group that the baseline never ran
  EDGES:  [(regex on source node, regex on target node, 'needs'|'env'|'guard', text)]   gate the edges between two nodes (a branch condition)
  STATIC_ADAPTERS: [regex on class name]                        adapters whose rows exist without user data (no row gate)
  NO_EXPORT_ENV: [class simple names]                           exported components reached from the app itself
  EXTRA_ENTRY: [(class simple name, kind, text, env)]           extra entry points
  ADJUST: callable(src, dst, kind, kw) that may edit an edge's keyword arguments before it is added
"""
import collections
import json
import os
import re
import xml.etree.ElementTree as ET

from build_graph import base, method_names
from extract_calls import parse_class

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
APPS = os.path.join(os.path.dirname(WORK), 'final_java_only')

ANDROID_NS = '{http://schemas.android.com/apk/res/android}'

ENV_EXT = 'outside package: another app, the system or adb sends the intent / broadcast / content call'
ENV_BOOT = 'outside package: the device reboots (BOOT_COMPLETED) or another system broadcast arrives'
ENV_LAUNCHER = 'outside package: the notification shade, an alarm, a launcher widget or shortcut starts it'
ENV_SYSTEM = 'outside package: a system condition (low memory, new intent from another app, system broadcast) triggers the callback'
NEED_ROWS = 'The list / adapter shows at least one row (some user data exists: add an item first)'
NEED_PREF_CHANGE = 'A preference value was changed while the app was running'
NEED_RESULT = 'The activity that was started for a result returned (or the permission dialog was answered)'

FW_LIFE = 'FW-MEMORY the framework creates the component and calls its lifecycle callbacks'
FW_CB = 'FW-MEMORY the framework / library calls this callback on an instance created by the app'
FW_LAMBDA = 'FW-MEMORY a lambda / method reference is invoked by the library that received it'
FW_INFLATE = 'FW-MEMORY LayoutInflater / setContentView / addPreferencesFromResource instantiates the classes named in the XML'
FW_CLINIT = 'FW-MEMORY the JVM runs a static initialiser before the first use of the class'
FW_RESULT = 'FW-MEMORY the system delivers the result of startActivityForResult / requestPermissions to the caller'
FW_INTENT = 'FW-MEMORY the system starts the component named by the intent'

# ------------------------------------------------------------------ callback catalogue
USER_NAMES = {
    'onClick', 'onLongClick', 'onTouch', 'onItemClick', 'onItemLongClick', 'onItemSelected', 'onNothingSelected',
    'onCheckedChanged', 'onProgressChanged', 'onStartTrackingTouch', 'onStopTrackingTouch', 'onKey', 'onEditorAction',
    'onFocusChange', 'onQueryTextSubmit', 'onQueryTextChange', 'onMenuItemClick', 'onMenuItemActionExpand',
    'onMenuItemActionCollapse', 'onNavigationItemSelected', 'onTabSelected', 'onTabUnselected', 'onTabReselected',
    'onPreferenceClick', 'onPreferenceChange', 'onPreferenceTreeClick', 'onOptionsItemSelected',
    'onContextItemSelected', 'onCreateContextMenu', 'onBackPressed', 'onKeyDown', 'onKeyUp', 'onKeyLongPress',
    'onTouchEvent', 'onInterceptTouchEvent', 'dispatchTouchEvent', 'onGenericMotionEvent', 'onSupportNavigateUp',
    'onNavigateUp', 'onMenuItemSelected', 'onSearchRequested', 'onScroll', 'onScrollStateChanged', 'onFling',
    'onSingleTapUp', 'onSingleTapConfirmed', 'onDoubleTap', 'onLongPress', 'onDown', 'onShowPress', 'onDrag',
    'onTextChanged', 'beforeTextChanged', 'afterTextChanged', 'onDateSet', 'onTimeSet', 'onPageSelected',
    'onPageScrolled', 'onPageScrollStateChanged', 'onSwiped', 'onMove', 'onRefresh', 'onSelectionChanged',
    'onCheckedChange', 'onValueChange', 'onStopTrackingTouch', 'onItemSwipe', 'onItemMove', 'onActionItemClicked',
    'onCreateActionMode', 'onPrepareActionMode', 'onDestroyActionMode', 'onItemCheckedStateChanged',
    'onItemDismiss', 'onDismiss', 'onCancel', 'onShow', 'onPositive', 'onNegative', 'onNeutral', 'onSelection',
    'onClose', 'onSwipe', 'onSelectionDone', 'onColorSelected', 'onFileSelection', 'onFolderSelection',
    'onItemClicked', 'onMenuItemSelected', 'onOptionsMenuClosed', 'onContextMenuClosed', 'doClick',
    'onRowClick', 'onItemTouch', 'onTouchItem', 'onDragStarted', 'onItemDrop',
}
OBJECT_NAMES = {'toString', 'equals', 'hashCode', 'clone', 'finalize', 'compareTo', 'compare', 'readObject',
                'writeObject', 'readResolve', 'writeReplace', 'close', 'iterator', 'hasNext', 'next',
                'describeContents', 'writeToParcel', 'createFromParcel', 'newArray'}
ALWAYS_NAMES = {'run', 'call', 'doInBackground', 'onPostExecute', 'onPreExecute', 'onProgressUpdate', 'onCancelled',
                'handleMessage', 'onHandleIntent', 'onReceive', 'onSharedPreferenceChanged'}
ASYNC_NAMES = {'run', 'call', 'doInBackground', 'onPostExecute', 'onPreExecute', 'onProgressUpdate', 'onCancelled',
               'handleMessage', 'onHandleIntent', 'onReceive', 'onLoadFinished', 'onCreateLoader', 'onLoaderReset',
               'loadInBackground', 'doWork', 'onStartJob', 'onStopJob', 'onResult', 'onResponse', 'onFailure',
               'onSuccess', 'onError', 'onNext', 'onCompleted', 'accept', 'apply', 'test', 'get', 'subscribe',
               'onChanged', 'onChange', 'update', 'uncaughtException', 'onSharedPreferenceChanged'}
SYSTEM_PAGE = {   # callbacks of an activity / fragment that the system calls later: name -> (gui text, env)
    'onPause': ('Press Home or open another app', None),
    'onStop': ('Press Home or open another app', None),
    'onDestroy': ('Press Back or rotate the device', None),
    'onDestroyView': ('Press Back or rotate the device', None),
    'onDetach': ('Press Back or rotate the device', None),
    'onRestart': ('Return to the app from the recent apps list', None),
    'onSaveInstanceState': ('Rotate the device or press Home', None),
    'onRestoreInstanceState': ('Rotate the device', None),
    'onConfigurationChanged': ('Rotate the device', None),
    'onUserLeaveHint': ('Press Home', None),
    'onTrimMemory': (None, ENV_SYSTEM),
    'onLowMemory': (None, ENV_SYSTEM),
    'onNewIntent': (None, ENV_SYSTEM),
    'onMultiWindowModeChanged': (None, ENV_SYSTEM),
    'onPictureInPictureModeChanged': (None, ENV_SYSTEM),
}
LIFE_ALWAYS = {
    'attachBaseContext', 'onCreate', 'onPostCreate', 'onStart', 'onResume', 'onPostResume', 'onCreateOptionsMenu',
    'onPrepareOptionsMenu', 'onAttachedToWindow', 'onWindowFocusChanged', 'onContentChanged', 'onAttachFragment',
    'onAttach', 'onCreateView', 'onViewCreated', 'onActivityCreated', 'onViewStateRestored', 'onCreateDialog',
    'onCreatePreferences', 'onStartCommand', 'onBind', 'onUnbind', 'onHandleIntent', 'onReceive',
    'onSupportContentChanged', 'onApplyThemeResource', 'onTitleChanged', 'onStateNotSaved', 'onCreateLoader',
    'onLoadFinished', 'onStartJob',
}
ROW_NAMES = {'getView', 'onBindViewHolder', 'onCreateViewHolder', 'bindView', 'newView', 'instantiateItem',
             'getDropDownView', 'getItem', 'getItemId', 'getItemViewType', 'getChildView', 'getGroupView'}
LIFETIME_NAMES = {'<clinit>', '<init>'}
PROVIDER_OPS = {'query', 'insert', 'update', 'delete', 'getType', 'call', 'openFile', 'bulkInsert', 'openAssetFile', 'applyBatch', 'openTypedAssetFile'}
STARTERS = {   # only receivers: a ComponentName for a receiver is often used to query or enable it, not to start it
    'RECEIVER': {'sendBroadcast', 'sendOrderedBroadcast', 'getBroadcast', 'sendStickyBroadcast', 'sendBroadcastAsUser', 'set', 'setExact',
                 'setRepeating', 'setInexactRepeating', 'setAndAllowWhileIdle', 'setExactAndAllowWhileIdle', 'setAlarmClock', 'setWindow'},
}
TOUCH_NAMES = {'onTouchEvent', 'onInterceptTouchEvent', 'dispatchTouchEvent', 'onGenericMotionEvent', 'onKeyDown', 'onKeyUp',
               'onTouch', 'onFling', 'onScroll', 'onLongPress', 'onDoubleTap', 'onSingleTapUp', 'onSingleTapConfirmed', 'onDown'}
LIST_VIEW_BASES = ('ListView', 'GridView', 'AbsListView', 'AdapterView', 'RecyclerView', 'ExpandableListView', 'StaggeredGridView')
SYSTEM_EVENTS = {   # callbacks that hardware or another app triggers: name -> condition
    'onAudioFocusChange': 'another app takes or gives back audio focus',
    'onSensorChanged': 'a sensor reports a new value',
    'onAccuracyChanged': 'a sensor changes its accuracy',
    'onLocationChanged': 'a location fix arrives',
    'onProviderEnabled': 'the location provider is switched on',
    'onProviderDisabled': 'the location provider is switched off',
    'onCallStateChanged': 'a phone call starts or ends',
    'onBatteryLow': 'the battery runs low',
    'onTaskRemoved': 'the user swipes the app away from the recent apps list',
}
ROW_USER = {'onItemClick', 'onItemLongClick', 'onActionItemClicked', 'onCreateActionMode', 'onPrepareActionMode',
            'onDestroyActionMode', 'onItemCheckedStateChanged', 'onChildClick', 'onGroupClick', 'onItemClicked',
            'onItemSwipe', 'onSwiped', 'onItemDismiss', 'onItemMove', 'onRowClick', 'onSelectedChanged'}


def short(c):
    return c.rsplit('/', 1)[-1]


def cat_of(name):
    if name in USER_NAMES:
        return 'USER'
    return 'ASYNC' if name in ASYNC_NAMES else 'FW'


class Gen:
    def __init__(self, ns, gdir, app, cfg):
        self.ns, self.gdir, self.app, self.cfg = ns, gdir, app, cfg or {}
        self.e0 = ns['e']
        self.emitted = set()
        self.stats = collections.Counter()
        self.notes = []
        # a pattern starting with 'class:' is matched against the internal class name (package path) instead of the node name
        self.gate_res = [(re.compile(rx[6:] if rx.startswith('class:') else rx), k, t, rx.startswith('class:'))
                         for rx, k, t in self.cfg.get('GROUPS', [])]
        # EDGES: [(regex on source node, regex on target node, 'needs'|'env'|'guard', text)]: a branch-specific gate on direct calls
        self.edge_gates = [(re.compile(a), re.compile(b), k, t) for a, b, k, t in self.cfg.get('EDGES', [])]
        self.load()

    # ------------------------------------------------------------------ inputs
    def load(self):
        gdir = self.gdir
        rows = json.load(open(os.path.join(gdir, 'method_list.json')))
        self.names, self.by_name = method_names(rows)
        self.node = {}
        self.key = {}
        for n in self.names:
            r = self.by_name[n]
            self.node[(r['class'], r['name'], r['desc'])] = n
            self.key[n] = (r['class'], r['name'], r['desc'])
        self.auto = json.load(open(os.path.join(gdir, 'auto_calls.json')))
        self.hit = set()      # nodes that APE or Monkey ran: an environment gate in front of them is refuted
        cpath = os.path.join(gdir, 'coverage_baseline.json')
        if os.path.isfile(cpath):
            for r in json.load(open(cpath)):
                if r.get('monkey') or r.get('ape'):
                    n = self.node.get((r['class'], r['short'].split('.', 1)[1], r['desc']))
                    if n:
                        self.hit.add(n)
        self.rv = set(self.auto.get('receiver_variants', ()))
        appdir = os.path.join(APPS, self.app, 'app')
        cf = json.load(open(os.path.join(appdir, 'class_files.json')))
        (_apk, d), = cf.items()
        self.classdirs = [os.path.join(appdir, p) for p in d['classfiles']]
        self.srcdirs = [os.path.join(appdir, p) for p in d['sourcefiles'] if not re.search(r'/src/(androidTest|test)/', p)]
        self.resroots = sorted({os.path.dirname(s.rstrip('/')) for s in self.srcdirs})
        excl = tuple(self.cfg.get('EXCLUDE_CLASS', ())) + ('JacocoInstrument', 'SMSInstrumentedReceiver', 'EmmaInstrument')
        self.classes = {}
        for cdir in self.classdirs:
            for dp, _ds, fs in os.walk(cdir):
                for f in fs:
                    if f.endswith('.class'):
                        ci = parse_class(os.path.join(dp, f))
                        if not any(x in ci.name for x in excl):
                            self.classes[ci.name] = ci
        # hierarchy
        self.fw = {}
        for c in self.classes:
            self.fw[c] = self.fw_supers(c)
        self.subs = collections.defaultdict(set)
        for c in self.classes.values():
            for s_ in [c.super] + c.interfaces:
                if s_ in self.classes:
                    self.subs[s_].add(c.name)
        # in-edges of the bytecode call graph
        self.inn = collections.Counter()
        self.out_calls = collections.defaultdict(list)
        for c in self.auto['calls']:
            if c['src'] != c['dst']:
                self.inn[base(c['dst'])] += 1
            self.out_calls[c['src']].append(c)
        self.lam_dst = collections.Counter()
        self.lam_by = {}
        for l in self.auto['lambdas']:
            self.lam_dst[l['dst']] += 1
        for cname, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                src = self.node.get((cname, mn, md))
                if not src:
                    continue
                for (impl, line), meta in zip(m['lambdas'], m['lam_meta']):
                    dst = self.node.get(impl)
                    if dst:
                        self.lam_by.setdefault((src, dst), (meta[1], meta[2], line, ci.source))
        self.bus_subscribers = collections.defaultdict(set)   # declaring class -> {(name, desc)} of EventBus subscribers
        for cname, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                if any(a.endswith('eventbus/Subscribe;') for a in m['annos']) or \
                        (mn in ('onEvent', 'onEventMainThread', 'onEventAsync', 'onEventBackgroundThread') and re.fullmatch(r'\(L[^;]+;\)V', md)):
                    self.bus_subscribers[cname].add((mn, md))
        self.has_bus_posts = any(x in ('EventBus.post', 'EventBus.postSticky') for calls in self.auto['framework_calls'].values() for x in calls)
        self.resolver_ops = set()   # ContentResolver operations that app code itself calls
        for calls in self.auto['framework_calls'].values():
            for x in calls:
                if x.startswith('ContentResolver.') or x.startswith('ContentProviderClient.'):
                    self.resolver_ops.add(x.split('.', 1)[1])
        self.sources = {}
        self.manifest_text = ''
        self.parse_manifest()
        self.parse_xml()
        # classes that something can construct: a `new` outside a subclass constructor, a class literal, a name string
        self.real_ctor = collections.Counter()
        for c in self.auto['calls']:
            dk = self.key.get(base(c['dst']))
            sk = self.key.get(base(c['src']))
            if not dk or dk[1] != '<init>' or not sk:
                continue
            if sk[1] == '<init>' and (dk[0] == sk[0] or dk[0] in self.all_supers(sk[0])):
                continue   # this(...) / super(...)
            self.real_ctor[dk[0]] += 1
        self.new_sites = collections.defaultdict(list)   # class -> [(method node, line)] of every `new class`
        for cname, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                src = self.node.get((cname, mn, md))
                if src:
                    for (tc, ln) in m['new_refs']:
                        if tc != cname or mn not in ('<init>',):
                            self.new_sites[tc].append((src, ln, cname))
        for tc, lst in self.new_sites.items():
            if tc in self.classes and not self.inits_of(tc):
                self.real_ctor[tc] += len(lst)
        self.lit_refs = set()
        self.str_refs = set()
        self.generated_impl = set()   # concrete subclasses of an abstract class whose class literal is used (Room, ...)
        for cname, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                for (tc, _l) in m['ldc_classes']:
                    if tc != cname or (m['access'] & 0x0008 and mn != '<clinit>'):
                        self.lit_refs.add(tc)
                for (sv, _l) in m['ldc_strings']:
                    if '.' in sv and ' ' not in sv and len(sv) < 120:
                        self.str_refs.add(sv.replace('.', '/'))
        for tc in list(self.lit_refs):
            ti = self.classes.get(tc)
            if ti and ti.access & 0x0600:
                for sub in self.all_subs(tc):
                    if self.is_concrete(sub) and self.real_ctor.get(sub, 0) == 0 and self.generated_like(sub):
                        self.generated_impl.add(sub)

    def fw_supers(self, c):
        seen, stack, res = set(), [c], set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            ci = self.classes.get(x)
            if not ci:
                if x != 'java/lang/Object':
                    res.add(x)
                continue
            for s_ in [ci.super] + ci.interfaces:
                if s_:
                    stack.append(s_)
        res.discard(c)
        return res

    def inits_of(self, cls):
        return [n for (c, nm, ds), n in self.node.items() if c == cls and nm == '<init>']

    def anchors(self, cls):
        """Nodes standing for 'an instance of cls is constructed': its constructors, or a pseudo page when JaCoCo hides its
        (empty, default) constructor from the method universe."""
        d = self.comps.get(cls)
        if d and d['kind'] in ('SERVICE', 'RECEIVER', 'PROVIDER', 'APPLICATION', 'BACKUP'):
            # the system creates the instance that gets the lifecycle callbacks; an instance the app constructs itself does not
            pn = 'S_SYS_' + short(cls).replace('$', '_')
            S = self.ns['SCREENS']
            if pn not in S:
                S[pn] = 'The system creates the %s %s and calls its callbacks' % (d['kind'].lower(), short(cls))
                for i in self.inits_of(cls):
                    self.emit(pn, i, 'LIFECYCLE', 'The system constructs the instance', evidence=FW_LIFE)
            return [pn]
        ins = self.inits_of(cls)
        if ins:
            return ins
        pn = 'S_NEW_' + short(cls).replace('$', '_')
        S = self.ns['SCREENS']
        if pn not in S:
            S[pn] = 'An instance of %s is constructed (its default constructor is not in the JaCoCo method universe)' % short(cls)
        return [pn]

    def is_concrete(self, c):
        return c in self.classes and not self.classes[c].access & 0x0600

    def kind_of_class(self, c):
        """component kind from the framework ancestors: ACTIVITY, FRAGMENT, SERVICE, RECEIVER, PROVIDER, APPLICATION"""
        names = {short(x) for x in self.fw.get(c, ())}
        # app classes between c and the framework count too (fw already walks through them)
        def ends(suffix):
            return any(n.endswith(suffix) for n in names)
        if ends('Activity'):
            return 'ACTIVITY'
        if ends('Fragment') or ends('FragmentCompat'):
            return 'FRAGMENT'
        if ends('Service'):
            return 'SERVICE'
        if ends('BroadcastReceiver') or 'AppWidgetProvider' in names:
            return 'RECEIVER'
        if 'ContentProvider' in names:
            return 'PROVIDER'
        if ends('Application'):
            return 'APPLICATION'
        return None

    def declared_up(self, c, name, desc):
        x = c
        while x in self.classes:
            m = self.classes[x].methods.get((name, desc))
            if m is not None and not m['access'] & 0x0400:
                return x
            x = self.classes[x].super
        for s_ in self.all_supers(c):
            if s_ in self.classes:
                m = self.classes[s_].methods.get((name, desc))
                if m is not None and not m['access'] & 0x0400:
                    return s_
        return None

    def all_subs(self, c):
        seen, stack = set(), [c]
        while stack:
            for s_ in self.subs.get(stack.pop(), ()):
                if s_ not in seen:
                    seen.add(s_)
                    stack.append(s_)
        return seen

    def all_supers(self, c):
        seen, stack = [], [c]
        while stack:
            x = stack.pop()
            if x not in self.classes:
                continue
            for s_ in [self.classes[x].super] + self.classes[x].interfaces:
                if s_ and s_ not in seen:
                    seen.append(s_)
                    stack.append(s_)
        return seen

    def impl_nodes(self, c):
        """{(name, desc): node} that run for an instance of concrete class c (declared or inherited)."""
        res = {}
        for anc in [c] + self.all_supers(c):
            if anc not in self.classes:
                continue
            for (mn, md) in self.classes[anc].methods:
                if mn in LIFETIME_NAMES or (mn, md) in res:
                    continue
                d = self.declared_up(c, mn, md)
                if not d:
                    continue
                n = self.node.get((d, mn, md))
                if not n:
                    continue
                v = '%s@%s' % (n, short(c))
                res[(mn, md)] = v if v in self.rv else n
        return res

    # ------------------------------------------------------------------ sources
    def src_lines(self, cls):
        ci = self.classes.get(cls)
        if not ci or not ci.source:
            return None
        key = (os.path.dirname(cls), ci.source)
        if key not in self.sources:
            lines = None
            for sd in self.srcdirs:
                p = os.path.join(sd, key[0], key[1])
                if os.path.isfile(p):
                    lines = open(p, encoding='utf-8', errors='replace').read().split('\n')
                    break
            self.sources[key] = lines
        return self.sources[key]

    def line_text(self, cls, line):
        ls = self.src_lines(cls)
        if not ls or not line or line > len(ls):
            return ''
        return ' '.join(ls[max(0, line - 3):line + 1])

    def label(self, cls, line, kind='Tap'):
        """Human label of the control a listener is attached to, read from the source around the registration."""
        txt = self.line_text(cls, line)
        ci = self.classes.get(cls)
        where = '%s:%s' % (ci.source if ci else short(cls), line)
        if not txt:
            return None if kind == 'quiet' else '%s the control registered at %s' % (kind, where)
        m = re.findall(r'R\.id\.(\w+)', txt)
        if m:
            return '%s the control R.id.%s' % ('Tap' if kind == 'quiet' else kind, m[-1])
        m = re.findall(r'(\b[A-Za-z_]\w*)\s*(?:\([^()]*\))?\s*\.\s*(?:setOn\w*Listener|add\w*Listener|setOnItem\w*|setOnCheckedChangeListener)\s*\(', txt)
        if m:
            return '%s %s' % ('Tap' if kind == 'quiet' else kind, m[-1])
        return None if kind == 'quiet' else '%s the control registered at %s' % (kind, where)

    def site_text(self, cls, line):
        ci = self.classes.get(cls)
        return 'SRC %s:%s (bytecode)' % (ci.source if ci else '?', line)

    # ------------------------------------------------------------------ manifest / xml
    def parse_manifest(self):
        self.pkg = None
        self.comps = {}      # internal class -> dict(kind, exported, filters[[actions],[categories]], alias_of, line)
        self.manifest_lines = []
        self.perms = set()
        found = False
        for r in self.resroots:
            p = os.path.join(r, 'AndroidManifest.xml')
            if not os.path.isfile(p):
                continue
            found = True
            text = open(p, encoding='utf-8', errors='replace').read()
            self.manifest_lines.append((p, text.split('\n')))
            try:
                root = ET.fromstring(text)
            except ET.ParseError:
                continue
            if root.get('package') and not self.pkg:
                self.pkg = root.get('package')
            for up in root.iter('uses-permission'):
                self.perms.add(up.get(ANDROID_NS + 'name'))
            appn = root.find('application')
            if appn is None:
                continue
            if appn.get(ANDROID_NS + 'name'):
                self.add_comp(appn.get(ANDROID_NS + 'name'), 'APPLICATION', appn, p)
            if appn.get(ANDROID_NS + 'backupAgent'):
                self.add_comp(appn.get(ANDROID_NS + 'backupAgent'), 'BACKUP', appn, p)
            for tag, kind in (('activity', 'ACTIVITY'), ('activity-alias', 'ACTIVITY'), ('service', 'SERVICE'),
                              ('receiver', 'RECEIVER'), ('provider', 'PROVIDER')):
                for el in appn.iter(tag):
                    nm = el.get(ANDROID_NS + 'name')
                    if tag == 'activity-alias':
                        nm = el.get(ANDROID_NS + 'targetActivity') or nm
                    self.add_comp(nm, kind, el, p)
        if not self.pkg:
            gp = [os.path.join(os.path.dirname(r), 'build.gradle') for r in self.resroots]
            for g in gp:
                if os.path.isfile(g):
                    m = re.search(r'namespace\s*[=\s]\s*[\'"]([\w.]+)[\'"]', open(g).read())
                    if m:
                        self.pkg = m.group(1)
        if not found:
            self.notes.append('no AndroidManifest.xml found')

    def resolve(self, name):
        if not name:
            return None
        orig = name
        if name.startswith('.'):
            name = (self.pkg or '') + name
        elif '.' not in name and self.pkg:
            name = self.pkg + '.' + name
        cand = name.replace('.', '/')
        if cand in self.classes:
            return cand
        # nested classes written with dots
        parts = name.split('.')
        for i in range(len(parts) - 1, 0, -1):
            c2 = '/'.join(parts[:i]) + '/' + '$'.join(parts[i:])
            if c2 in self.classes:
                return c2
        tail = '/' + cand.rsplit('/', 1)[-1]
        hits = [c for c in self.classes if c.endswith(tail) or c.endswith(tail.replace('.', '$'))]
        if len(hits) == 1 and (not self.pkg or orig.startswith('.') or '.' not in orig):
            return hits[0]
        return None

    def add_comp(self, name, kind, el, path):
        cls = self.resolve(name)
        if not cls:
            return
        actions, cats = [], []
        has_filter = False
        for f in (el.iter('intent-filter') if kind not in ('APPLICATION', 'BACKUP') else ()):
            has_filter = True
            acts = [a.get(ANDROID_NS + 'name') for a in f.iter('action')]
            cs = [c.get(ANDROID_NS + 'name') for c in f.iter('category')]
            actions += acts
            cats += cs
        exp = el.get(ANDROID_NS + 'exported')
        exported = (exp == 'true') if exp is not None else has_filter
        launcher = any(c == 'android.intent.category.LAUNCHER' for c in cats) and \
            any(a == 'android.intent.action.MAIN' for a in actions)
        line = None
        for p, ls in self.manifest_lines:
            if p == path:
                short_n = name.split('.')[-1]
                for i, t in enumerate(ls, 1):
                    if 'android:name="%s"' % name in t or ('"%s"' % name in t) or ('.' + short_n + '"') in t:
                        line = i
                        break
        d = self.comps.setdefault(cls, {'kind': kind, 'exported': False, 'actions': [], 'launcher': False,
                                        'filter': False, 'line': line})
        d['exported'] = d['exported'] or exported
        d['actions'] += [a for a in actions if a]
        d['launcher'] = d['launcher'] or launcher
        d['filter'] = d['filter'] or has_filter
        d['path'] = path

    def parse_xml(self):
        """layout / xml / menu / navigation files: classes they instantiate, includes, android:onClick handlers."""
        self.strings = {}
        for r in self.resroots:
            vd = os.path.join(r, 'res', 'values')
            if os.path.isdir(vd):
                for f in os.listdir(vd):
                    if f.endswith('.xml'):
                        t = open(os.path.join(vd, f), encoding='utf-8', errors='replace').read()
                        for sm in re.finditer(r'<string\s+name="(\w+)"[^>]*>([^<]*)</string>', t):
                            self.strings.setdefault(sm.group(1), sm.group(2).strip())
        self.xml_refs = collections.defaultdict(list)    # class -> [(res type, name, file, line)]
        self.includes = collections.defaultdict(set)     # layout -> layouts it includes
        self.onclick = collections.defaultdict(list)     # method name -> [(layout, view id, line)]
        self.layout_files = {}
        for r in self.resroots:
            res = os.path.join(r, 'res')
            if not os.path.isdir(res):
                continue
            for dp, _ds, fs in os.walk(res):
                typ = os.path.basename(dp).split('-')[0]
                if typ not in ('layout', 'xml', 'menu', 'navigation', 'values', 'drawable', 'animator', 'anim'):
                    continue
                for f in fs:
                    if not f.endswith('.xml'):
                        continue
                    name = f[:-4]
                    path = os.path.join(dp, f)
                    try:
                        text = open(path, encoding='utf-8', errors='replace').read()
                    except OSError:
                        continue
                    self.layout_files[(typ, name)] = path
                    for m in re.finditer(r'@(layout|xml|navigation)/([\w.]+)', text):
                        if typ in ('layout', 'xml', 'navigation'):
                            self.includes[(typ, name)].add((m.group(1), m.group(2)))
                    if typ == 'values':   # resource aliases: <item name="activity_main" type="layout">@layout/activity_main_drawer</item>
                        for am in re.finditer(r'<item\s+name="([\w.]+)"\s+type="(layout|xml|navigation)"[^>]*>\s*@(layout|xml|navigation)/([\w.]+)\s*</item>', text):
                            self.includes[(am.group(2), am.group(1))].add((am.group(3), am.group(4)))
                    for lm in re.finditer(r'android:onClick="(\w+)"', text):
                        line = text.count('\n', 0, lm.start()) + 1
                        idm = re.findall(r'android:id="@\+?id/(\w+)"', text[max(0, lm.start() - 400):lm.start() + 400])
                        self.onclick[lm.group(1)].append((name, idm[-1] if idm else None, line))
                    # class names: tags with dots, android:name / class / android:fragment / app:... Class attributes
                    cands = set(re.findall(r'<([A-Za-z_][\w.$]*\.[\w.$]+)[\s>/]', text))
                    cands |= set(re.findall(r'(?:\b\w+:)?(?:name|fragment|class|actionViewClass|actionProviderClass|'
                                            r'layout_behavior|targetClass|destination)\s*=\s*"([\w.$]+)"', text))
                    for sm in re.finditer(r'(?:\b\w+:)?(?:name|fragment|class|actionViewClass|actionProviderClass|layout_behavior)\s*=\s*"@string/(\w+)"', text):
                        sv = self.strings.get(sm.group(1))
                        if sv and re.fullmatch(r'[\w.$]+', sv):
                            cands.add(sv)
                    for cn in cands:
                        if '.' not in cn:
                            continue
                        c = self.resolve(cn)
                        if c:
                            ln = text.count(cn, 0, 10 ** 9) and text[:text.find(cn)].count('\n') + 1
                            self.xml_refs[c].append((typ, name, path, ln))

    # ------------------------------------------------------------------ emit helpers
    def variants_of(self, node):
        """Receiver variants Base.m@Sub of a base node whose class Sub is constructed somewhere."""
        if not hasattr(self, '_okv'):
            var_of = collections.defaultdict(list)
            for v in self.rv:
                var_of[base(v)].append(v)
            by_short = collections.defaultdict(list)
            for c in self.classes:
                by_short[short(c)].append(c)
            self._okv = {}
            for b, vs in var_of.items():
                self._okv[b] = [v for v in vs if any(self.instantiated(c) for c in by_short.get(v.split('@', 1)[1], ()))]
        return self._okv.get(node, ())

    def emit(self, src, dst, kind, trigger, fan=False, **kw):
        if fan and '@' not in dst:   # the receiver class is unknown here: the call can run in every constructed subclass
            for v in self.variants_of(dst):
                self.emit(src, v, kind, trigger, **dict(kw))
        if src == dst:
            return
        k = (src, dst, kind)
        if k in self.emitted:
            return
        if src not in self.ns['SCREENS'] and base(src) not in self.names_set():
            return
        if dst not in self.ns['SCREENS'] and base(dst) not in self.names_set():
            return
        self.emitted.add(k)
        if kw.get('env') and base(dst) in self.hit and kind != 'ENTRY':
            kw['env'] = None      # the baseline ran the target, so the outside condition was not needed on the baseline setup
            self.stats['env_refuted'] += 1
        for rx, gk, text, on_class in self.gate_res:
            if base(dst) in self.hit:
                break                      # a configured gate never applies to a method the baseline ran
            if self.group_match(rx, on_class, dst):
                if gk == 'needs' and not kw.get('needs_state'):
                    kw['needs_state'] = text
                elif gk == 'env' and not kw.get('env'):
                    kw['env'] = text
                elif gk == 'guard' and not kw.get('guard'):
                    kw['guard'] = text
        for ra, rb, gk, text in self.edge_gates:
            if ra.search(base(src)) and rb.search(base(dst)):
                if gk == 'needs' and not kw.get('needs_state'):
                    kw['needs_state'] = text
                elif gk == 'env' and not kw.get('env'):
                    kw['env'] = text
                elif gk == 'guard' and not kw.get('guard'):
                    kw['guard'] = text
        adj = self.cfg.get('ADJUST')
        if adj:
            adj(src, dst, kind, kw)
        gui = kw.pop('gui', ())
        self.e0(src, dst, kind, trigger, gui=gui, **kw)
        self.stats[kind] += 1

    def group_match(self, rx, on_class, node):
        b = base(node)
        if on_class:
            k = self.key.get(b)
            return bool(k and rx.search(k[0]))
        return bool(rx.search(b))

    def names_set(self):
        if not hasattr(self, '_ns'):
            self._ns = set(self.names)
        return self._ns

    def page(self, cls):
        pn = 'S_' + short(cls).replace('$', '_')
        return pn

    # ------------------------------------------------------------------ the generator
    def run(self):
        self.pages = {}
        self.handlers = []
        self.entry_edges()
        self.callback_edges()
        self.lambda_edges()
        self.abstract_ref_edges()
        self.intent_edges()
        self.xml_edges()
        self.result_edges()
        self.new_edges()
        self.handler_edges()
        self.databinding_edges()
        self.generated_edges()
        self.reflection_edges()
        self.di_edges()
        self.library_edges()
        self.variant_edges()
        self.clinit_edges()
        self.case_label_edges()
        self.group_gate_edges()
        return self

    def group_gate_edges(self):
        """cfg GROUPS: copy every bytecode call edge that enters a group from outside, with the gate on it (the copy replaces the plain auto edge)."""
        if not self.gate_res and not self.edge_gates:
            return
        n = 0
        for c in self.auto['calls']:
            d, sr = c['dst'], c['src']
            if any(ra.search(base(sr)) and rb.search(base(d)) for ra, rb, _k, _t in self.edge_gates) or \
                    (any(self.group_match(rx, oc, d) for rx, _k, _t, oc in self.gate_res) and base(d) not in self.hit):
                before = len(self.emitted)
                trig = 'Direct call' if c['dispatch'] == 'exact' else 'Virtual/interface call that can dispatch to this implementation'
                self.emit(sr, d, 'CALL', trig, evidence='SRC %s:%s (bytecode)' % (c['file'], c['line']))
                n += len(self.emitted) - before
        self.stats['group_gated_calls'] = n

    # ---- entry points
    def entry_edges(self):
        S = self.ns['SCREENS']
        S['S_ENTRY'] = 'Outside the app: launcher, another app, the system or adb'
        for cls, d in sorted(self.comps.items()):
            init = self.anchors(cls)[0]
            ev = 'SRC AndroidManifest.xml:%s' % (d.get('line') or '?')
            kind = d['kind']
            if kind == 'APPLICATION':
                self.emit('S_ENTRY', init, 'ENTRY', 'The process starts: the system creates the Application object', gui=['Start the app'], evidence=ev)
            elif kind == 'PROVIDER':
                self.emit('S_ENTRY', init, 'ENTRY', 'The process starts: the system creates the ContentProvider before Application.onCreate', evidence=ev)
            elif d['launcher']:
                self.emit('S_ENTRY', init, 'ENTRY', 'MAIN / LAUNCHER intent starts %s' % short(cls), gui=['Tap the app icon in the launcher'], evidence=ev)
            elif kind == 'BACKUP':
                self.emit('S_ENTRY', init, 'ENTRY', 'The Android Backup Manager creates the backup agent %s (backup or restore)' % short(cls),
                          env='outside package: the system Backup Manager runs a backup or restore for the app (bmgr)', evidence=ev + '; FW-MEMORY android:backupAgent')
            elif d['exported'] or d['filter'] or kind == 'RECEIVER':
                acts = sorted({a.rsplit('.', 1)[-1] for a in d['actions']})[:4]
                env = ENV_BOOT if kind == 'RECEIVER' else ENV_EXT
                txt = 'Another app or the system starts %s (%s)' % (short(cls), ', '.join(acts) or 'exported component')
                self.emit('S_ENTRY', init, 'ENTRY', txt, env=env, evidence=ev + '; ' + FW_INTENT)

    # ---- lifecycle, pages, callbacks of every concrete class with a framework ancestor
    def component_kind(self, cls):
        d = self.comps.get(cls)
        return (d['kind'] if d else None) or self.kind_of_class(cls)

    def callback_edges(self):
        S = self.ns['SCREENS']
        static_ad = [re.compile(x) for x in self.cfg.get('STATIC_ADAPTERS', [])]
        self.unrouted = []
        for cls in sorted(self.classes):
            if not self.is_concrete(cls):
                continue
            kind = self.component_kind(cls)
            if not self.instantiated(cls):
                continue   # abstract-like base class: its callbacks run through the subclasses' impl tables
            fw = self.fw.get(cls, ())
            has_fw = bool(fw)
            impl = self.impl_nodes(cls)
            if not has_fw and not kind:
                impl = {k: v for k, v in impl.items() if k[0] in OBJECT_NAMES}
                if not impl:
                    continue
            # one <init> per class is enough as the source: pick the first; every <init> is a possible construction
            inits = self.anchors(cls)
            page = None
            if kind in ('ACTIVITY', 'FRAGMENT'):
                page = self.page(cls)
                S[page] = '%s %s (%s)' % ('Activity' if kind == 'ACTIVITY' else 'Fragment', short(cls), cls.replace('/', '.'))
                self.pages[cls] = page
            fw_names = {short(x) for x in fw}
            is_adapter = any(n.endswith('Adapter') or n.endswith('ViewHolder') for n in fw_names) and not any(r.search(cls) for r in static_ad) \
                and not any('Pager' in n or n == 'FragmentStateAdapter' for n in fw_names)
            entered = None
            for (mn, md), n in sorted(impl.items()):
                m_decl = self.declared_up(cls, mn, md)
                mm = self.classes[m_decl].methods[(mn, md)]
                if mm['access'] & 0x0008 or mn.startswith('lambda$'):
                    continue
                orphan = self.inn.get(base(n), 0) == 0 and self.lam_dst.get(base(n), 0) == 0
                always = mn in LIFE_ALWAYS
                known = always or mn in USER_NAMES or mn in SYSTEM_PAGE or mn in ALWAYS_NAMES or (mn in OBJECT_NAMES and orphan)
                if not (orphan or known):
                    continue
                cat = cat_of(mn)
                ev = FW_LIFE if kind else FW_CB
                if kind in ('ACTIVITY', 'FRAGMENT') and mn in ('onActivityResult', 'onRequestPermissionsResult'):
                    continue   # reached from the request sites only (result_edges)
                if (mn, md) in self.bus_subscribers.get(m_decl, ()) and self.has_bus_posts:
                    continue   # EventBus subscriber: reached from the post sites only (library_edges)
                if kind in ('ACTIVITY', 'FRAGMENT') and mn in SYSTEM_PAGE:
                    txt, env = SYSTEM_PAGE[mn]
                    self.emit(page, n, 'SYSTEM', 'The system calls %s' % mn, gui=[txt] if txt else (), env=env, evidence=ev)
                    continue
                if kind in ('ACTIVITY', 'FRAGMENT') and cat == 'USER':
                    self.emit(page, n, 'GUI', self.user_text(mn), gui=[self.user_gui(mn, cls)], evidence=ev)
                    continue
                if kind in ('ACTIVITY', 'FRAGMENT') and md == '(Landroid/view/View;)V' and not always and mn not in ASYNC_NAMES:
                    oc = self.onclick.get(mn)
                    where = ('android:onClick="%s" in layout %s' % (mn, oc[0][0])) if oc else 'a click handler with a View parameter'
                    gtext = 'Tap the control %s' % (('R.id.' + oc[0][1]) if oc and oc[0][1] else '(%s)' % where)
                    self.emit(page, n, 'GUI', 'Tap: %s' % where, gui=[gtext], evidence=ev + ('; SRC res/layout/%s.xml:%s' % (oc[0][0], oc[0][2]) if oc else ''))
                    continue
                if mn == 'handleMessage' and md in ('(Landroid/os/Message;)V', '(Landroid/os/Message;)Z'):
                    self.handlers.append(n)   # reached from the code that sends messages (handler_edges)
                    continue
                src = inits
                if mn in ROW_NAMES and is_adapter:
                    need = NEED_ROWS
                else:
                    need = None
                if mn in ('onSharedPreferenceChanged',):
                    need = NEED_PREF_CHANGE
                if mn in ROW_USER:
                    need = NEED_ROWS
                knd = 'LIFECYCLE' if (kind and always) else ('ASYNC' if cat == 'ASYNC' else ('SYSTEM' if mn in SYSTEM_PAGE else 'FRAMEWORK'))
                sys_env = None
                if mn in SYSTEM_EVENTS:
                    knd = 'SYSTEM'
                    sys_env = 'outside package: ' + SYSTEM_EVENTS[mn]
                if kind == 'PROVIDER' and mn in PROVIDER_OPS and mn not in self.resolver_ops:
                    sys_env = 'outside package: another app (or adb content) calls the provider; the app itself never calls ContentResolver.%s' % mn
                gui = ()
                if cat == 'USER':
                    gui = [self.creation_label(cls, mn)]
                    if mn in TOUCH_NAMES and not kind:
                        gui = ['Touch or drag on a %s' % short(cls)]
                        if any(n.endswith(LIST_VIEW_BASES) for n in fw_names):
                            need = NEED_ROWS
                for s_ in src:
                    self.emit(s_, n, knd, ('Lifecycle callback %s' % mn) if knd == 'LIFECYCLE' else
                              ('The framework calls %s on an instance created by %s' % (mn, s_.split('.', 1)[-1])),
                              gui=gui, needs_state=need, env=sys_env, evidence=ev)
            if page:
                # ENTERS: after the first lifecycle callback that shows the screen
                order = ['onResume', 'onStart', 'onViewCreated', 'onCreateView', 'onActivityCreated', 'onCreate'] if kind == 'FRAGMENT' else \
                    ['onResume', 'onStart', 'onCreate']
                src = None
                for nm in order:
                    cands = [v for (mn, md), v in impl.items() if mn == nm and self.key[base(v)][0] == cls]
                    if cands:
                        src = cands[0]   # declared in this very class, so the node is not shared with sibling screens
                        break
                if src is None:
                    src = inits[0]
                self.emit(src, page, 'ENTERS', 'The screen %s is shown' % short(cls), evidence=FW_LIFE)

    def user_text(self, mn):
        return {
            'onOptionsItemSelected': 'The user taps an item of the toolbar / overflow menu',
            'onContextItemSelected': 'The user taps an item of the context menu',
            'onBackPressed': 'The user presses Back',
            'onKeyDown': 'The user presses a hardware key',
            'onKeyUp': 'The user releases a hardware key',
            'onSupportNavigateUp': 'The user taps the Up arrow',
            'onNavigateUp': 'The user taps the Up arrow',
            'onTouchEvent': 'The user touches the screen',
            'dispatchTouchEvent': 'The user touches the screen',
        }.get(mn, 'The user interacts with the screen (%s)' % mn)

    def user_gui(self, mn, cls):
        return {
            'onOptionsItemSelected': 'Open the toolbar / overflow menu and tap an item',
            'onContextItemSelected': 'Long-press an item and tap an entry of the context menu',
            'onCreateContextMenu': 'Long-press an item to open the context menu',
            'onBackPressed': 'Press Back',
            'onKeyDown': 'Press a hardware key (volume, menu, search ...)',
            'onKeyUp': 'Press a hardware key (volume, menu, search ...)',
            'onSupportNavigateUp': 'Tap the Up arrow (top-left)',
            'onNavigateUp': 'Tap the Up arrow (top-left)',
            'onTouchEvent': 'Touch the screen',
            'dispatchTouchEvent': 'Touch the screen',
            'onNavigationItemSelected': 'Open the navigation drawer and tap an entry',
            'onQueryTextSubmit': 'Type in the search box and submit',
            'onQueryTextChange': 'Type in the search box',
        }.get(mn, 'Interact with the screen (%s in %s)' % (mn, short(cls)))

    def creation_label(self, cls, mn):
        """gui text for a user callback of a listener class: look at where the class is instantiated."""
        sites = self.ctor_sites(cls)
        if sites:
            scls, line = sites[0]
            return self.label(scls, line, 'Use') if mn not in ('onClick', 'onItemClick') else self.label(scls, line, 'Tap')
        return 'Interact with the control handled by %s.%s' % (short(cls), mn)

    def ctor_sites(self, cls):
        if not hasattr(self, '_ctor_sites'):
            idx = collections.defaultdict(list)
            for c in self.auto['calls']:
                dk = self.key.get(base(c['dst']))
                if dk and dk[1] == '<init>':
                    sk = self.key.get(base(c['src']))
                    if sk:
                        idx[dk[0]].append((sk[0], c['line']))
            self._ctor_sites = idx
        return self._ctor_sites.get(cls, [])

    # ---- lambdas: the creating method makes the body reachable
    def lambda_edges(self):
        for (src, dst), (sam, iface, line, srcfile) in sorted(self.lam_by.items()):
            scls = self.key[src][0]
            cat = cat_of(sam)
            ev = FW_LAMBDA + '; ' + self.site_text(scls, line)
            if cat == 'USER' or re.search(r'(Click|Listener|Callback)$', iface.split('$')[-1].rstrip(';')) and sam in USER_NAMES:
                self.emit(src, dst, 'FRAMEWORK', 'Lambda for %s.%s: the user triggers it' % (short(iface.strip('L;')).split('$')[-1], sam),
                          gui=[self.label(scls, line, 'Tap')], evidence=ev, fan=True)
            elif sam in ('run', 'call') or 'Runnable' in iface or 'Callable' in iface:
                self.emit(src, dst, 'ASYNC', 'Runnable / Callable lambda runs later on a handler or worker thread', evidence=ev, fan=True)
            else:
                self.emit(src, dst, 'FRAMEWORK', 'The library invokes the lambda (%s.%s)' % (short(iface.strip('L;')).split('$')[-1], sam), evidence=ev, fan=True)

    # ---- method references to abstract / interface methods: the library calls every implementation
    def abstract_ref_edges(self):
        n = 0
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                src = self.node.get((cls, mn, md))
                if not src:
                    continue
                for (impl, line), meta in zip(m['lambdas'], m['lam_meta']):
                    if impl[0] not in self.classes or impl[1].startswith('lambda$'):
                        continue
                    owner, name, desc = impl
                    targets = set()
                    for sub in [owner] + sorted(self.all_subs(owner)):
                        if self.is_concrete(sub):
                            d = self.declared_up(sub, name, desc)
                            if d and (d, name, desc) in self.node:
                                targets.add(self.node[(d, name, desc)])
                    cat = cat_of(meta[1])
                    for t in sorted(targets):
                        self.emit(src, t, 'FRAMEWORK', 'Method reference %s::%s: the library calls it on every implementation' % (short(owner), name),
                                  evidence=FW_LAMBDA + '; ' + self.site_text(cls, line), fan=True)
                        n += 1
        self.stats['abstract_method_ref'] = n

    def generated_like(self, cls):
        sn = short(cls)
        return bool(re.search(r'(_Impl|Impl|_Factory|\$\$\w+|^Generated\w*|^Dagger\w*)(\$\d+)?$', sn)) or '_Impl' in sn

    def starts(self, src, kind):
        """Does method `src` (or one of its direct callers) call a framework API that starts / schedules a component of this kind?"""
        if not hasattr(self, '_callers'):
            cm = collections.defaultdict(set)
            for c in self.auto['calls']:
                cm[base(c['dst'])].add(base(c['src']))
            self._callers = cm
        fw = self.auto['framework_calls']
        names = STARTERS[kind]
        for n in [src] + sorted(self._callers.get(base(src), ())):
            if any(x.rsplit('.', 1)[-1] in names for x in fw.get(n, ())):
                return True
        return False

    # ---- startActivity(new Intent(ctx, X.class)), class literals, custom action strings
    def intent_edges(self):
        orphan_init = {}
        for (c, nm, ds), n in self.node.items():
            if nm == '<init>':
                orphan_init.setdefault(c, []).append(n)
        for c in self.classes:
            if self.comps.get(c, {}).get('kind') in ('SERVICE', 'RECEIVER', 'PROVIDER', 'APPLICATION', 'BACKUP'):
                orphan_init[c] = self.anchors(c)
            elif c not in orphan_init and self.is_concrete(c):
                orphan_init[c] = self.anchors(c) if (c in self.comps or c in self.lit_refs or c in self.str_refs or c in self.xml_refs) else []
        actions = collections.defaultdict(list)
        std_actions = collections.defaultdict(list)   # standard actions an own exported activity declares (VIEW, EDIT, SEND, ...)
        for cls, d in self.comps.items():
            for a in set(d['actions']):
                if not a.startswith('android.'):
                    actions[a].append(cls)
                elif d['kind'] == 'ACTIVITY' and a.rsplit('.', 1)[-1] in ('VIEW', 'EDIT', 'SEND', 'SEND_MULTIPLE', 'SENDTO', 'PICK',
                                                                           'GET_CONTENT', 'OPEN_DOCUMENT', 'INSERT', 'SEARCH', 'CREATE_DOCUMENT'):
                    std_actions[a].append(cls)
        fwcalls = self.auto['framework_calls']
        implicit = []
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                src = self.node.get((cls, mn, md))
                if not src:
                    continue
                pend = any(x.startswith('PendingIntent.') or x.startswith('AlarmManager.') for x in fwcalls.get(src, ()))
                for (tc, line) in m['ldc_classes']:
                    if tc not in self.classes or (tc == cls and (not m['access'] & 0x0008 or mn == '<clinit>')):
                        continue
                    inits = orphan_init.get(tc, [])
                    if not inits:
                        continue
                    kind = self.component_kind(tc)
                    comp = tc in self.comps
                    if comp and kind in STARTERS and not self.starts(src, kind):
                        continue    # e.g. ComponentName for setComponentEnabledSetting / AppWidgetManager: not a start
                    if self.classes[tc].access & 0x0600:   # abstract / interface literal: generated implementations (Room, ...)
                        for sub in sorted(self.all_subs(tc)):
                            if self.is_concrete(sub) and self.real_ctor.get(sub, 0) == 0 and self.generated_like(sub) and not self.component_kind(tc):
                                for i in orphan_init.get(sub, []):
                                    self.emit(src, i, 'FRAMEWORK', 'Class literal %s.class: the library instantiates the generated implementation %s reflectively' % (short(tc), short(sub)),
                                              evidence=FW_CB + '; ' + self.site_text(cls, line))
                        continue
                    if not comp:  # a class literal handed to a library: it may call any constructor nobody in the app calls
                        inits = [i for i in inits if self.inn.get(base(i), 0) == 0]
                    for i in inits:
                        if comp:
                            env = ENV_LAUNCHER if pend else None
                            lab = self.label(cls, line, 'quiet') if kind == 'ACTIVITY' and not pend else None
                            gui = [lab] if lab else ()
                            self.emit(src, i, 'INTENT', 'Intent with the class literal %s.class starts the %s' % (short(tc), (kind or 'component').lower()),
                                      gui=gui, env=env, evidence=FW_INTENT + '; ' + self.site_text(cls, line))
                        else:
                            self.emit(src, i, 'FRAMEWORK', 'Class literal %s.class: the class is instantiated by the framework or by reflection' % short(tc),
                                      evidence=FW_CB + '; ' + self.site_text(cls, line))
                for (sv, line) in m['ldc_strings']:
                    if sv in std_actions and any(x in ('Intent.<init>', 'Intent.setAction', 'Intent.setDataAndType', 'Intent.setType',
                                                       'Intent.createChooser') for x in fwcalls.get(src, ())):
                        for tc in std_actions[sv]:
                            if tc != cls:
                                implicit.append((src, tc, sv, cls, line))
                    if sv in actions:
                        for tc in actions[sv]:
                            for i in orphan_init.get(tc, []):
                                self.emit(src, i, 'INTENT', 'Intent with the action "%s" starts %s' % (sv.rsplit('.', 1)[-1], short(tc)),
                                          env=ENV_LAUNCHER if pend else None, evidence=FW_INTENT + '; ' + self.site_text(cls, line))
                    elif '.' in sv and ' ' not in sv and len(sv) < 120:
                        tc = sv.replace('.', '/')
                        if tc in self.classes and tc != cls:
                            for i in orphan_init.get(tc, []):
                                if self.inn.get(base(i), 0) == 0:
                                    self.emit(src, i, 'FRAMEWORK', 'Class name string "%s": instantiated by name (reflection / Fragment.instantiate)' % short(tc),
                                              evidence=FW_CB + '; ' + self.site_text(cls, line))

        # implicit standard actions only for components the app does not start explicitly anywhere (otherwise too many false routes)
        explicit_targets = {d for (_s, d, k) in self.emitted if k == 'INTENT'}
        for (src, tc, sv, cls, line) in implicit:
            targets = orphan_init.get(tc, [])
            if any(d in explicit_targets for d in targets):
                continue
            for i_ in targets:
                self.emit(src, i_, 'INTENT', 'Implicit intent with the action %s may resolve to the app\'s own exported %s' % (sv.rsplit('.', 1)[-1], short(tc)),
                          evidence='INFERRED ' + FW_INTENT + '; ' + self.site_text(cls, line))

    # ---- classes named in layout / xml files are created where the file is inflated
    def xml_edges(self):
        # usage sites of R.<type>.<name> in the Java sources
        sites = collections.defaultdict(list)    # (type, name) -> [(class, method node, line)]
        self.all_sites = collections.defaultdict(list)
        by_file = collections.defaultdict(list)  # (pkgdir, SourceFile) -> [(cls, mn, md, node, lo, hi, linenos)]
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                n = self.node.get((cls, mn, md))
                if n and m['lines']:
                    by_file[(os.path.dirname(cls), ci.source)].append((cls, n, m['lines'][0], m['lines'][1], set(m['linenos'])))
        used_types = {(t, n) for refs in self.xml_refs.values() for (t, n, _p, _l) in refs}
        needed = set(used_types)
        # layouts that include a layout that declares a class
        changed = True
        incl_rev = collections.defaultdict(set)
        for (typ, name), inc in self.includes.items():
            for (t2, n2) in inc:
                incl_rev[(t2, n2)].add((typ, name))
        while changed:
            changed = False
            for k in list(needed):
                for up in incl_rev.get(k, ()):
                    if up not in needed:
                        needed.add(up)
                        changed = True
        bind = {}
        for cls in self.classes:
            m = re.match(r'(.+)Binding$', short(cls))
            if m and ('/databinding/' in cls or '/viewbinding/' in cls):
                lay = re.sub(r'(?<!^)(?=[A-Z])', '_', m.group(1)).lower()
                bind[cls] = lay
        for sd in self.srcdirs:
            for dp, _ds, fs in os.walk(sd):
                for f in fs:
                    if not f.endswith('.java'):
                        continue
                    p = os.path.join(dp, f)
                    text = open(p, encoding='utf-8', errors='replace').read()
                    pk = os.path.relpath(dp, sd)
                    for mm in re.finditer(r'R\.(layout|xml|navigation)\.(\w+)', text):
                        key = (mm.group(1), mm.group(2))
                        line = text.count('\n', 0, mm.start()) + 1
                        hit = self.method_at(by_file.get((pk, f), ()), line)
                        if hit:
                            self.all_sites[key].append((hit[0], hit[1], line))
                            if key in needed:
                                sites[key].append((hit[0], hit[1], line))
        # view binding: callers of XBinding.inflate / bind
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                n = self.node.get((cls, mn, md))
                if not n:
                    continue
                for kind_, (owner, name, desc), line in m['calls']:
                    if owner in bind:
                        sites[('layout', bind[owner])].append((cls, n, line))
        done = 0
        for c, refs in sorted(self.xml_refs.items()):
            inits = [(n, ds) for (k, nm, ds), n in self.node.items() if k == c and nm == '<init>']
            if not inits:
                inits = [(a, '()V') for a in self.anchors(c)]
            if self.component_kind(c) not in ('FRAGMENT', 'ACTIVITY'):  # views / preferences: inflated with an AttributeSet
                attr = [(n, ds) for n, ds in inits if 'AttributeSet' in ds]
                inits = attr or inits
            else:
                noarg = [(n, ds) for n, ds in inits if ds == '()V']
                inits = noarg or inits
            inits = [n for n, ds in inits]
            for (typ, name, path, ln) in refs:
                stack, seen = [(typ, name)], set()
                while stack:
                    k = stack.pop()
                    if k in seen:
                        continue
                    seen.add(k)
                    for (scls, snode, sline) in sites.get(k, ()):
                        for i in inits:
                            rel = os.path.relpath(path, os.path.dirname(os.path.dirname(os.path.dirname(path))))
                            self.emit(snode, i, 'FRAMEWORK', 'Inflating %s %s.xml instantiates %s' % (k[0], k[1], short(c)),
                                      evidence=FW_INFLATE + '; SRC %s:%s; %s' % (rel, ln, self.site_text(scls, sline)))
                            done += 1
                    for up in incl_rev.get(k, ()):
                        stack.append(up)
        self.stats['xml_inflate'] = done
        self.layout_sites = sites

    def method_at(self, entries, line):
        best = None
        for cls, n, lo, hi, linenos in entries:
            if line in linenos:
                return cls, n
            if lo <= line <= hi and (best is None or hi - lo < best[2]):
                best = (cls, n, hi - lo)
        return (best[0], best[1]) if best else None

    # ---- onActivityResult / onRequestPermissionsResult: the result goes back to the class that made the request
    def family_reach(self, cls, depth=6):
        """Nodes reachable by direct calls from the methods of cls and its nested classes (the code that runs on behalf of cls)."""
        if not hasattr(self, '_fr_adj'):
            adj = collections.defaultdict(set)
            for n, lst in self.out_calls.items():
                for c in lst:
                    adj[n].add(c['dst'])
            for l in self.auto['lambdas']:           # a lambda created here runs here
                adj[l['src']].add(l['dst'])
            by_cls = collections.defaultdict(list)
            for (c, nm, ds), n in self.node.items():
                by_cls[c].append((nm, n))
            for (c, nm, ds), n in self.node.items():  # a constructed object's own methods can run (listeners, tasks)
                if nm == '<init>':
                    for (nm2, n2) in by_cls[c]:
                        if nm2 != '<init>':
                            adj[n].add(n2)
            self._fr_adj = adj
        outer = cls.split('$')[0]
        start = [n for (c, nm, ds), n in self.node.items() if c.split('$')[0] == outer]
        seen = set(start)
        frontier = list(start)
        for _ in range(depth):
            nxt = []
            for n in frontier:
                for d in self._fr_adj.get(n, ()):
                    if d not in seen:
                        seen.add(d)
                        nxt.append(d)
            frontier = nxt
        return seen

    def result_edges(self):
        fwcalls = self.auto['framework_calls']
        def names(src):
            return {x.rsplit('.', 1)[-1] for x in fwcalls.get(src, ())}
        act_sites = {src for src in fwcalls if any(n.endswith('ForResult') or n in ('launch', 'startActivityFromFragment') for n in names(src))}
        perm_sites = {src for src in fwcalls if 'requestPermissions' in names(src)}
        n_res = 0
        for cls in sorted(self.classes):
            if not self.is_concrete(cls) or self.component_kind(cls) not in ('ACTIVITY', 'FRAGMENT'):
                continue
            impl = self.impl_nodes(cls)
            wanted = [(mn, n) for (mn, md), n in impl.items() if mn in ('onActivityResult', 'onRequestPermissionsResult')]
            if not wanted:
                continue
            reach = None
            for mn, n in wanted:
                pool = act_sites if mn == 'onActivityResult' else perm_sites
                if reach is None:
                    reach = {base(x) for x in self.family_reach(cls)}
                srcs = pool & reach
                note = ''
                if not srcs:   # the request is made from code the call graph does not tie to this class (static references, helpers)
                    srcs = pool
                    note = '; INFERRED: no request site in the class family, every request site assumed'
                for s_ in sorted(srcs):
                    self.emit(s_, n, 'RESULT', 'The system delivers the result to %s' % mn, evidence=FW_RESULT + note)
                    n_res += 1
        self.stats['result_sites'] = n_res

    # ---- `new C` where C's constructor is not a node: the creating method reaches the pseudo anchor
    def new_edges(self):
        n = 0
        for tc, lst in sorted(self.new_sites.items()):
            if tc not in self.classes or self.inits_of(tc) or not self.is_concrete(tc):
                continue
            a = self.anchors(tc)[0]
            for (src, ln, scls) in lst:
                self.emit(src, a, 'CALL', 'new %s (default constructor)' % short(tc), evidence=self.site_text(scls, ln).replace('SRC', 'SRC', 1))
                n += 1
        self.stats['new_default_ctor'] = n

    # ---- Handler.handleMessage runs after somebody sends a message
    def handler_edges(self):
        send = {'sendMessage', 'sendEmptyMessage', 'sendMessageDelayed', 'sendEmptyMessageDelayed', 'sendMessageAtTime',
                'sendMessageAtFrontOfQueue', 'sendToTarget', 'dispatchMessage'}
        posters = [src for src, calls in self.auto['framework_calls'].items() if any(x.rsplit('.', 1)[-1] in send for x in calls)]
        n = 0
        for h in sorted(set(self.handlers)):
            hc = self.key[base(h)][0]
            hout = hc.split('$')[0]
            # posters of the same class family, or that mention the handler class; else every poster (INFERRED)
            near = [src for src in posters if self.key[src][0].split('$')[0] == hout or
                    hc in self.classes[self.key[src][0]].methods[(self.key[src][1], self.key[src][2])]['class_refs']]
            for src in sorted(near or posters):
                self.emit(src, h, 'ASYNC', 'Handler.send...Message delivers the message to handleMessage on the main thread',
                          evidence='FW-MEMORY Handler: sendMessage queues the message, the looper calls handleMessage; INFERRED (poster matched by class, not by instance)' +
                                   ('' if near else '; no poster in the same class family: every send site assumed'))
                n += 1
        self.stats['handler'] = n

    # ---- data binding: XBinding.inflate / bind make DataBindingUtil construct the generated XBindingImpl
    def databinding_edges(self):
        n = 0
        for cls in sorted(self.classes):
            if not self.is_concrete(cls) or 'ViewDataBinding' not in {short(x) for x in self.fw.get(cls, ())}:
                continue
            inits = [(nm, n_) for (c, nm, ds), n_ in self.node.items() if c == cls and nm == '<init>']
            if not inits:
                continue
            parents = [p for p in self.all_supers(cls) if p in self.classes]
            for p in parents:
                for (c, nm, ds), src in sorted(self.node.items()):
                    if c == p and (nm.startswith('inflate') or nm.startswith('bind') or nm == '<init>') and src not in [i for _, i in inits]:
                        for _nm, i in inits:
                            self.emit(src, i, 'FRAMEWORK', 'DataBindingUtil (DataBinderMapperImpl) constructs the generated %s' % short(cls),
                                      evidence='FW-MEMORY androidx.databinding: inflate / bind look up the generated Impl class for the layout')
                            n += 1
        # layouts: XBindingImpl <-> res/layout/x_y.xml; the method that mentions R.layout.x_y (DataBindingUtil.inflate / setContentView) creates it
        for cls in sorted(self.classes):
            mm = re.match(r'^(.*?)Binding\w*Impl$', short(cls))
            if not mm or not self.is_concrete(cls) or 'ViewDataBinding' not in {short(x) for x in self.fw.get(cls, ())}:
                continue
            lay = re.sub(r'(?<!^)(?=[A-Z])', '_', mm.group(1)).lower()
            for (scls, snode, sline) in self.all_sites.get(('layout', lay), ()):
                for (c, nm, ds), i in self.node.items():
                    if c == cls and nm == '<init>':
                        self.emit(snode, i, 'FRAMEWORK', 'DataBindingUtil binds layout %s: the generated %s is constructed' % (lay, short(cls)),
                                  evidence='FW-MEMORY androidx.databinding; ' + self.site_text(scls, sline))
                        n += 1
        # the aggregated mapper that DataBindingUtil loads by class name
        factories = [src for (c, nm, ds), src in self.node.items()
                     if 'ViewDataBinding' in {short(x) for x in self.fw.get(c, ())} and (nm.startswith('inflate') or nm.startswith('bind'))]
        for src, calls in self.auto['framework_calls'].items():
            if any(x.startswith('DataBindingUtil.') for x in calls):
                factories.append(src)
        for cls in sorted(self.classes):
            if short(cls) == 'DataBinderMapperImpl':
                for (c, nm, ds), t in sorted(self.node.items()):
                    if c == cls and nm != '<clinit>':
                        for src in sorted(factories):
                            self.emit(src, t, 'FRAMEWORK', 'DataBindingUtil loads DataBinderMapperImpl by name and asks it for the binding of the layout',
                                      evidence='FW-MEMORY androidx.databinding: DataBindingUtil.inflate / bind -> MergedDataBinderMapper -> generated mapper')
                            n += 1
        self.stats['databinding'] = n

    # ---- generated classes that a library loads by name (Icepick, Parceler, Glide)
    def generated_edges(self):
        fwc = self.auto['framework_calls']
        n = 0
        # Icepick: T$$Icepick.restore / save
        for cls in sorted(self.classes):
            if not short(cls).endswith('$$Icepick'):
                continue
            t = cls[:-len('$$Icepick')]
            for src, calls in fwc.items():
                sc = self.key[src][0]
                outer = sc
                while outer != t and '$' in outer:
                    outer = outer.rsplit('$', 1)[0]
                if outer != t and sc != t and sc not in self.all_supers(t):
                    continue
                for (c, nm, ds), tn in self.node.items():
                    if c != cls:
                        continue
                    if (nm == 'restore' and 'Icepick.restoreInstanceState' in calls) or (nm == 'save' and 'Icepick.saveInstanceState' in calls) or \
                            (nm in ('<init>', '<clinit>') and any(x.startswith('Icepick.') for x in calls)):
                        self.emit(src, tn, 'FRAMEWORK', 'Icepick.%s reflectively calls the generated %s' % ('restoreInstanceState' if nm == 'restore' else 'saveInstanceState', short(cls)),
                                  evidence='FW-MEMORY Icepick loads T$$Icepick by name')
                        n += 1
        # Parceler: X$$Parcelable constructed by Parcels.wrap / unwrap
        pw = [src for src, calls in fwc.items() if any(x in ('Parcels.wrap', 'Parcels.unwrap') for x in calls)]
        for cls in sorted(self.classes):
            if short(cls).endswith('$$Parcelable'):
                for a in self.anchors(cls):
                    for src in pw:
                        self.emit(src, a, 'FRAMEWORK', 'Parcels.wrap / unwrap constructs the generated %s' % short(cls),
                                  evidence='FW-MEMORY Parceler loads X$$Parcelable by name; INFERRED (class of the wrapped object not matched)')
                        n += 1
        # Glide: generated module, request classes
        gl = [src for src, calls in fwc.items() if any(x.split('.')[0] in ('Glide', 'GlideApp') for x in calls)]
        for cls in sorted(self.classes):
            sn = short(cls)
            if sn in ('GeneratedAppGlideModuleImpl',) or 'AppGlideModule' in {short(x) for x in self.fw.get(cls, ())}:
                for a in self.anchors(cls):
                    for src in gl:
                        self.emit(src, a, 'FRAMEWORK', 'Glide.get(...) loads the generated module %s by name' % sn,
                                  evidence='FW-MEMORY Glide: GeneratedAppGlideModule is loaded reflectively when Glide initialises')
                        n += 1
        # ORMLite: DaoManager.createDao instantiates the DAO class named in @DatabaseTable(daoClass = ...)
        dm = [src for src, calls in fwc.items() if any(x.startswith('DaoManager.') for x in calls)]
        for cls in sorted(self.classes):
            if 'BaseDaoImpl' in {short(x) for x in self.fw.get(cls, ())} and self.is_concrete(cls):
                for a in self.anchors(cls):
                    for src in dm:
                        self.emit(src, a, 'FRAMEWORK', 'DaoManager.createDao instantiates the DAO class %s reflectively' % short(cls),
                                  evidence='FW-MEMORY ORMLite: @DatabaseTable(daoClass) names the DAO class; INFERRED (table not matched)')
                        n += 1
        # Glide's generated subclasses of RequestOptions / RequestBuilder / RequestManager: the library calls any overridden method
        for cls in sorted(self.classes):
            sup = {short(x) for x in self.fw.get(cls, ())}
            if sup & {'RequestOptions', 'BaseRequestOptions', 'RequestBuilder', 'RequestManager'} and self.is_concrete(cls):
                for a in self.anchors(cls):
                    for (c, nm, ds), t in self.node.items():
                        if c == cls and nm not in ('<init>', '<clinit>'):
                            self.emit(a, t, 'FRAMEWORK', 'Glide calls the generated override %s' % nm, evidence='FW-MEMORY Glide generated request classes')
                            n += 1
        self.stats['generated_by_name'] = n

    # ---- reflection by method name: getDeclaredMethod("name") / getMethod("name")
    def reflection_edges(self):
        fwc = self.auto['framework_calls']
        by_name = collections.defaultdict(list)
        for (c, nm, ds), n in self.node.items():
            if nm not in ('<init>', '<clinit>') and not nm.startswith('lambda$') and self.inn.get(base(n), 0) == 0:
                by_name[nm].append((c, n))
        k = 0
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                src = self.node.get((cls, mn, md))
                if not src or not any(x in ('Class.getDeclaredMethod', 'Class.getMethod', 'Class.getDeclaredMethods', 'Class.getMethods') for x in fwc.get(src, ())):
                    continue
                for (sv, line) in m['ldc_strings']:
                    for (c, n) in by_name.get(sv, ()):
                        if c == cls or c in {x for x, _l in m['ldc_classes']}:
                            self.emit(src, n, 'FRAMEWORK', 'Reflection: getDeclaredMethod("%s") makes the method callable' % sv,
                                      evidence='FW-MEMORY java.lang.reflect.Method; ' + self.site_text(cls, line), fan=True)
                            k += 1
                    if len(sv) >= 5 and re.fullmatch(r'[A-Za-z_]\w*', sv):   # "onUpgradeTo" + version: a name prefix
                        for nm, lst in by_name.items():
                            if nm.startswith(sv) and nm != sv:
                                for (c, n) in lst:
                                    if c == cls:
                                        self.emit(src, n, 'FRAMEWORK', 'Reflection: getDeclaredMethod("%s" + suffix) makes the method callable' % sv,
                                                  evidence='FW-MEMORY java.lang.reflect.Method; ' + self.site_text(cls, line), fan=True)
                                        k += 1
        self.stats['reflection'] = k

    # ---- Dagger / Hilt: generated factories call @Provides methods and @Inject constructors when the object graph is built
    def di_edges(self):
        provs, injs, inj_methods = [], [], []
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                n = self.node.get((cls, mn, md))
                if not n:
                    continue
                an = m['annos']
                if any(a.endswith('dagger/Provides;') or a.endswith('dagger/producers/Produces;') for a in an):
                    provs.append(n)
                elif any(a.endswith('inject/Inject;') for a in an):
                    (injs if mn == '<init>' else inj_methods).append((cls, n))
        if not (provs or injs or inj_methods):
            return
        root = None
        for cls, d in self.comps.items():
            if d['kind'] == 'APPLICATION':
                for (mn, md), n in self.impl_nodes(cls).items():
                    if mn == 'onCreate':
                        root = n
                if root is None:
                    root = self.anchors(cls)[0]
        root = root or 'S_ENTRY'
        ev = 'FW-MEMORY Dagger / Hilt: the generated component and factories call @Provides methods and @Inject constructors when the graph is built; INFERRED root (application start)'
        n = 0
        for p_ in provs:
            self.emit(root, p_, 'FRAMEWORK', 'Dagger factory calls the @Provides method', evidence=ev)
            n += 1
        for cls, i in injs:
            self.emit(root, i, 'FRAMEWORK', 'Dagger factory calls the @Inject constructor', evidence=ev)
            n += 1
        for cls, mnode in inj_methods:
            for a in self.anchors(cls):
                self.emit(a, mnode, 'FRAMEWORK', 'Dagger calls the @Inject method after construction', evidence=ev)
                n += 1
        self.stats['dagger'] = n

    # ---- libraries: ButterKnife binders, EventBus 3 subscribers
    def library_edges(self):
        fwc = self.auto['framework_calls']
        binders = collections.defaultdict(list)
        for c in self.classes:
            s_ = short(c)
            if s_.endswith('_ViewBinding'):
                binders[c[:-len('_ViewBinding')]].append(c)
            elif s_.endswith('$$ViewBinder'):
                binders[c[:-len('$$ViewBinder')]].append(c)
        n_bk = 0
        for src, calls in sorted(fwc.items()):
            sc = self.key[src][0]
            bind = any(x in ('ButterKnife.bind', 'ButterKnife.inject') for x in calls)
            unb = any(x == 'Unbinder.unbind' for x in calls)
            if not (bind or unb):
                continue
            t = sc
            while t not in binders and '$' in t:
                t = t.rsplit('$', 1)[0]
            for bc in binders.get(t, ()):
                inits = [(n, ds) for (c, nm, ds), n in self.node.items() if c == bc and nm == '<init>']
                two = [(n, ds) for n, ds in inits if ds.count(';') >= 2 or 'View' in ds]
                if bind:
                    for n, ds in (two or inits):
                        self.emit(src, n, 'FRAMEWORK', 'ButterKnife.bind(...) reflectively calls the generated %s constructor' % short(bc),
                                  evidence='FW-MEMORY ButterKnife.bind finds and calls the generated binder class')
                        n_bk += 1
                if unb:
                    u = self.node.get((bc, 'unbind', '()V'))
                    if u:
                        self.emit(src, u, 'FRAMEWORK', 'Unbinder.unbind() calls the generated unbind',
                                  evidence='FW-MEMORY Unbinder.unbind')
        self.stats['butterknife'] = n_bk
        # EventBus 3
        subs, posts = [], []
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                n = self.node.get((cls, mn, md))
                if not n:
                    continue
                if any(a.endswith('eventbus/Subscribe;') for a in m['annos']) or \
                        (mn in ('onEvent', 'onEventMainThread', 'onEventAsync', 'onEventBackgroundThread') and re.fullmatch(r'\(L[^;]+;\)V', md)):
                    pm = re.match(r'\(L([^;]+);', md)
                    if pm:
                        subs.append((n, pm.group(1)))
        for src, calls in fwc.items():
            if any(x in ('EventBus.post', 'EventBus.postSticky') for x in calls):
                posts.append(src)
        n_eb = 0
        for sn, ev in subs:
            cand = []
            for src in posts:
                sc = self.key[src][0]
                m = self.classes[sc].methods.get((self.key[src][1], self.key[src][2]))
                if ev in m['class_refs'] or sc == ev or ('L%s;' % ev) in self.key[src][2]:
                    cand.append(src)
            hard = bool(cand)
            for src in (cand or posts):
                self.emit(src, sn, 'FRAMEWORK', 'EventBus.post(%s) calls the subscriber' % short(ev), fan=True,
                          guard=None if hard else 'poster not identified: every EventBus.post site is assumed',
                          evidence=('FW-MEMORY greenrobot EventBus 3: post() calls the @Subscribe methods registered for the event class' +
                                    ('' if hard else '; INFERRED')))
                n_eb += 1
        self.stats['eventbus'] = n_eb

    # ---- inherited template methods: a call into Base.m can run Base.m for any constructed subclass
    def instantiated(self, cls):
        return cls in self.comps or cls in self.xml_refs or self.real_ctor.get(cls, 0) > 0 or \
            cls in self.lit_refs or cls in self.str_refs or short(cls).endswith(('_ViewBinding', '$$ViewBinder')) or \
            short(cls) == 'DataBinderMapperImpl' or short(cls) in ('GeneratedAppGlideModuleImpl',) or short(cls).endswith(('$$Icepick', '$$Parcelable')) or 'BaseDaoImpl' in {short(x) for x in self.fw.get(cls, ())} or (short(cls).endswith('Impl') and 'ViewDataBinding' in {short(x) for x in self.fw.get(cls, ())}) or \
            (cls in self.generated_impl)

    def variant_edges(self):
        okv = {b: self.variants_of(b) for b in {base(v) for v in self.rv}}
        n = 0
        for c in self.auto['calls']:
            if c['src'] in self.rv or c['dst'] not in okv or not okv[c['dst']]:
                continue
            ev = 'SRC %s:%s (bytecode)' % (c['file'], c['line'])
            self.emit(c['src'], c['dst'], 'CALL', 'Direct call', evidence=ev)
            for v in okv[c['dst']]:
                self.emit(c['src'], v, 'CALL', 'Call on an instance of %s (inherited method that dispatches differently there)' % v.split('@', 1)[1], evidence=ev)
                n += 1
        self.stats['variant_calls'] = n

    # ---- static initialisers: first use of a class runs <clinit>
    def clinit_edges(self):
        refs = collections.defaultdict(set)
        for cls, ci in self.classes.items():
            for (mn, md), m in ci.methods.items():
                src = self.node.get((cls, mn, md))
                if not src:
                    continue
                for rc in set(m['class_refs']):
                    if rc != cls:
                        refs[rc].add(src)
        for cls, ci in self.classes.items():
            targets = [cls] + [s_ for s_ in self.all_supers(cls) if s_ in self.classes]
            for t in targets:
                cl = self.node.get((t, '<clinit>', '()V'))
                if not cl:
                    continue
                for src in sorted(refs.get(cls, ())):
                    self.emit(src, cl, 'LIFECYCLE', 'First use of %s runs its static initialiser' % short(t), evidence=FW_CLINIT)
        # a class's own methods can only run after its static initialiser
        by_cls = collections.defaultdict(list)
        for (c, nm, ds), n in self.node.items():
            by_cls[c].append((nm, n))
        for c, lst in by_cls.items():
            cl = self.node.get((c, '<clinit>', '()V'))
            if not cl:
                continue
            for nm, n in lst:
                if nm != '<clinit>':
                    self.emit(n, cl, 'LIFECYCLE', 'A method of %s runs, so its static initialiser has run' % short(c), evidence=FW_CLINIT)

    # ---- menu / switch handlers: label the call edges with the case they belong to
    def case_label_edges(self):
        handlers = {'onOptionsItemSelected', 'onMenuItemClick', 'onNavigationItemSelected', 'onContextItemSelected',
                    'onMenuItemSelected', 'onClick', 'onItemSelected', 'onActionItemClicked'}
        for (cls, mn, md), n in sorted(self.node.items()):
            if mn not in handlers:
                continue
            m = self.classes[cls].methods.get((mn, md))
            if not m or not m['lines']:
                continue
            lo, hi = m['lines']
            ls = self.src_lines(cls)
            if not ls:
                continue
            marks = []
            for i in range(max(0, lo - 2), min(len(ls), hi + 1)):
                for mm in re.finditer(r'(?:case\s+(android\.)?R\.id\.(\w+)\s*:|(?:==|!=)\s*(android\.)?R\.id\.(\w+)|(android\.)?R\.id\.(\w+)\s*(?:==|!=))', ls[i]):
                    lab = mm.group(2) or mm.group(4) or mm.group(6)
                    marks.append((i + 1, lab, 'android.' if (mm.group(1) or mm.group(3) or mm.group(5)) else ''))
            if not marks:
                continue
            seen = set()
            for c in self.out_calls.get(n, ()):
                if c['dst'] in seen:
                    continue
                prev = [mk for mk in marks if mk[0] <= (c['line'] or 0) and (c['line'] or 0) - mk[0] <= 40]
                if not prev:
                    continue
                seen.add(c['dst'])
                ln, lab, pfx = prev[-1]
                menu_like = mn in ('onOptionsItemSelected', 'onMenuItemClick', 'onNavigationItemSelected', 'onContextItemSelected',
                                   'onMenuItemSelected', 'onActionItemClicked')
                if menu_like:
                    self.emit(c['src'], c['dst'], 'CALL', 'case %sR.id.%s: call' % (pfx, lab), evidence='INFERRED SRC %s:%s (bytecode)' % (c['file'], c['line']))
                else:
                    self.emit(c['src'], c['dst'], 'CALL', 'branch for view R.id.%s' % lab,
                              gui=['Tap the control R.id.%s' % lab], evidence='INFERRED SRC %s:%s (bytecode)' % (c['file'], c['line']))


def apply(ns, gdir, app, cfg=None):
    g = Gen(ns, gdir, app, cfg).run()
    rep = ['generator: %s' % ', '.join('%s %d' % kv for kv in sorted(g.stats.items())),
           'pages: %d' % len(g.pages)] + g.notes
    ns['GEN_REPORT'] = rep
    print('\n'.join(rep))
    return g
