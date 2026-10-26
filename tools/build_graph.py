"""Build, validate and export a trigger graph from an app's graph_def.py (output schema 2, see handoff/SCHEMA_V2.md).

Usage: python3 -I build_graph.py <graph_dir> <file_prefix>

<graph_dir> must contain:
  graph_def.py          edge definitions (see below)
  method_list.json      output of list_methods.py --json (the method universe)
  verification.csv      optional audit log: type,item,result,confirmed_by,ref,edges,note (see SCHEMA_V2.md)
  coverage_baseline.json  optional; used only for the one-way sanity check (a method a tool ran cannot be UNREACHABLE)

graph_def.py is executed with these names predefined:
  e(src, dst, kind, trigger, gui=(), guard=None, reads=(), writes=(), note=None, needs_state=None, evidence=None,
    env=None, cls=None, via=None, env_kinds=(), state_kinds=())      -> appends one edge
  SCREENS = {}  TITLE = ''  NOTES = {}
  UNREACHABLE = {method: (kind, reason[, source_ref[, confirmed_by]])}   kind in UNREACHABLE_KINDS
  DEAD = {}  FRAMEWORK_ONLY = {}     legacy: {method: reason}; read as UNREACHABLE with kind 'unclassified'
  ENV_KINDS_OF = {env text: [kinds]}  STATE_KINDS_OF = {needs_state text: [kinds]}   kinds of the gates, by exact text
  CLASSIFY = None       optional callable(edge) -> edge class or (edge class, via); applied to edges without cls
  EDIT = None           optional callable(edge): may change any field of every edge (e.g. add an ENV gate) before ids are made
  STRICT = False        True: anything still unclassified is an error (set it once an app is converted)
  HTML = True           write the viewer page if the template exists
  PREFER_SETUP_OVER_ENV = False   # True: a method that needs in-app state but no environment gate is preferred
                                  # over a route that needs the environment
`env` marks an edge that needs the device or the outside world; `needs_state` an edge that needs earlier in-app actions.
NOTES maps a base method name to a free-text note for methods.csv.
USE_AUTO = True adds the call edges from <graph_dir>/auto_calls.json (tools/extract_calls.py) for every
caller/callee pair that no hand-written edge already covers; SUPPRESS = {(src, dst), ...} or {src, ...}
drops auto edges (e.g. calls inside branches that can never run). Lambda creations become REGISTER edges.

Writes into <graph_dir>/out/:
  <prefix>_trigger_graph.json, methods.csv, <prefix>_trigger_graph.html (if the template exists),
  sanity_check.csv (tool coverage vs labels, never used to set a label), build_report.txt.
methods.csv has route_edge_ids: the edge ids of the derived best route (what a verification.csv path row must repeat).
"""
import collections
import csv
import hashlib
import json
import os
import re
import sys

KINDS = {'ENTRY', 'LIFECYCLE', 'GUI', 'REGISTER', 'CALL', 'INTENT', 'RESULT', 'ASYNC',
         'FRAMEWORK', 'SYSTEM', 'ENTERS'}
EVIDENCE = ('SRC', 'FW-SRC', 'DYN', 'FW-MEMORY', 'INFERRED', 'UNVERIFIED')
JVM = {'I': 'int', 'J': 'long', 'Z': 'boolean', 'F': 'float', 'D': 'double', 'B': 'byte',
       'C': 'char', 'S': 'short', 'V': 'void'}
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'viewer_template.html')

# schema 2 vocabularies
EDGE_CLASSES = ('explicit', 'standard', 'non_standard', 'page')
DEFAULT_CLASS = {'CALL': 'explicit', 'ENTRY': 'standard', 'LIFECYCLE': 'standard', 'GUI': 'standard', 'REGISTER': 'standard',
                 'INTENT': 'standard', 'RESULT': 'standard', 'ASYNC': 'standard', 'FRAMEWORK': 'standard', 'SYSTEM': 'standard'}
ENV_KINDS = ('network', 'tls_chain', 'permission', 'hardware', 'other_app', 'system_event', 'time', 'other')
STATE_KINDS = ('data', 'settings', 'account', 'file', 'session')
UNREACHABLE_KINDS = ('no_trigger_in_app', 'branch_never_taken', 'framework_never_calls', 'closed_by_configuration', 'closed_by_api_level')
CONFIRMED = ('DEVICE', 'SOURCE', 'INFERRED')
RESULTS = ('correct', 'fixed', 'wrong', 'unclear')
VERIFY_TYPES = ('label', 'edge', 'path')
# words that suggest a non-standard implicit edge (library or reflection makes the link); only used to print a review list
NONSTD_HINT = re.compile(r'EventBus|ButterKnife|@OnClick|@BindView|Dagger|@Inject|RxJava|android:onClick|reflect|getIdentifier|'
                         r'Class\.forName|data ?binding|ViewBinding|implicit (?:intent|broadcast)|by action|setAction\(|'
                         r'Intent\((?:\w+\.)?ACTION_', re.I)


def base(n):
    return n.split('@')[0]


def is_screen(n):
    return n.startswith('S_')


def param_names(desc):
    """'(Landroid/content/Context;I)Z' -> 'Context,int'"""
    args, i, out = desc[1:desc.index(')')], 0, []
    while i < len(args):
        dims = 0
        while args[i] == '[':
            dims += 1
            i += 1
        if args[i] == 'L':
            j = args.index(';', i)
            name = args[i + 1:j].rsplit('/', 1)[-1].split('$')[-1]
            i = j + 1
        else:
            name = JVM[args[i]]
            i += 1
        out.append(name + '[]' * dims)
    return ','.join(out)


def class_prefixes(rows):
    """{outer class: 'pkgtail.'} for outer classes whose simple name is shared by another class (e.g. two TagsAdapter)."""
    simple = collections.defaultdict(set)
    for r in rows:
        outer = r['class'].split('$')[0]
        simple[outer.rsplit('/', 1)[-1]].add(outer)
    pre = {}
    for sn, fulls in simple.items():
        if len(fulls) < 2:
            continue
        for k in range(1, 8):
            tails = {f: '.'.join(f.split('/')[-1 - k:-1]) for f in fulls}
            if len(set(tails.values())) == len(fulls):
                break
        for f in fulls:
            pre[f] = tails[f] + '.'
    return pre


def method_names(rows):
    """Base node name per method; overloads get '(params)'; classes that share a simple name get a package prefix."""
    pre = class_prefixes(rows)
    shorts = [pre.get(r['class'].split('$')[0], '') + r['short'] for r in rows]
    count = collections.Counter(shorts)
    names, by_name = [], {}
    for r, sh in zip(rows, shorts):
        n = sh if count[sh] == 1 else '%s(%s)' % (sh, param_names(r['desc']))
        k = 2
        while n in by_name:   # same class, overloads whose parameter simple names coincide
            n = '%s#%d' % (n.split('#')[0], k)
            k += 1
        names.append(n)
        by_name[n] = r
    return names, by_name


def bfs(out, allow_setup, allow_env=True, classes=None):
    """Breadth-first reachability from S_ENTRY; classes: only follow edges of these edge classes."""
    prev, q = {'S_ENTRY': None}, ['S_ENTRY']
    for n in q:
        for x in out.get(n, []):
            if x['kind'] == 'REGISTER' or x['src'] == x['dst'] or x['dst'] in prev:
                continue
            if x['needs_state'] and not allow_setup:
                continue
            if x.get('env') and not allow_env:
                continue
            if classes is not None and x['edge_class'] not in classes:
                continue
            prev[x['dst']] = x
            q.append(x['dst'])
    return prev


def cheapest(out, allow_setup):
    """Like bfs, but each reachable node keeps the path with the fewest environment-gated edges, then the fewest
    earlier-setup (needs_state) edges, then the fewest steps.
    The returned dict is in settlement order (cheapest first), so the first variant found for a method is its best one."""
    import heapq
    best = {'S_ENTRY': (0, 0, 0)}
    via = {'S_ENTRY': None}
    done, prev = set(), {}
    heap, tick = [(0, 0, 0, 0, 'S_ENTRY')], 0
    while heap:
        env, setup, steps, _t, n = heapq.heappop(heap)
        if n in done:
            continue
        done.add(n)
        prev[n] = via[n]
        for x in out.get(n, []):
            if x['kind'] == 'REGISTER' or x['src'] == x['dst'] or x['dst'] in done:
                continue
            if x['needs_state'] and not allow_setup:
                continue
            cost = (env + (1 if x.get('env') else 0), setup + (1 if x['needs_state'] else 0), steps + 1)
            if x['dst'] not in best or cost < best[x['dst']]:
                best[x['dst']] = cost
                via[x['dst']] = x
                tick += 1
                heapq.heappush(heap, (cost[0], cost[1], cost[2], tick, x['dst']))
    return prev


def path_to(n, prev):
    p = []
    while prev.get(n):
        p.append(prev[n])
        n = prev[n]['src']
    return p[::-1]


def menu_label(trigger):
    m = re.search(r'(android\.R\.id\.home)|R\.id\.(\w+)', trigger or '')
    if not m:
        return None
    return 'Up arrow (top-left)' if m.group(1) else re.sub(r'^(action|menu|item)_', '', m.group(2)).replace('_', ' ')


def gui_steps(path):
    steps = []
    for i, x in enumerate(path):
        if not x['gui']:
            continue
        if i + 1 < len(path) and re.search(r'case (android\.)?R\.id\.', path[i + 1]['trigger'] or ''):
            lab = menu_label(path[i + 1]['trigger'])
            if lab:
                steps.append('Tap menu item: ' + lab)
                continue
        steps.append(x['gui'][0])
    return steps


def add_auto_edges(gdir, edges, e, suppress):
    auto = json.load(open(os.path.join(gdir, 'auto_calls.json')))
    manual = {(base(x['src']), base(x['dst'])) for x in edges if x['kind'] != 'REGISTER'}
    manual_reg = {(base(x['src']), base(x['dst'])) for x in edges if x['kind'] == 'REGISTER'}
    receiver = set(auto.get('receiver_variants', ()))
    variants = collections.defaultdict(set)  # hand-written context variants (not receiver variants)
    for x in edges:
        for n in (x['src'], x['dst']):
            if '@' in n and not is_screen(n) and n not in receiver:
                variants[base(n)].add(n)
    manual_nodes = {(x['src'], base(x['dst'])) for x in edges if x['kind'] != 'REGISTER'}
    for c in auto['calls']:
        p = (c['src'], c['dst'])
        if p in suppress or c['src'] in suppress or c['dst'] in suppress:
            continue
        if c['src'] in receiver:  # receiver variants: skip only if that exact node already has a hand edge
            if (c['src'], base(c['dst'])) in manual_nodes:
                continue
        elif (c['src'], base(c['dst'])) in manual or (base(c['src']), base(c['dst'])) in manual:
            continue
        trig = 'Direct call' if c['dispatch'] == 'exact' else 'Virtual/interface call that can dispatch to this implementation'
        if c['via']:
            trig += ' (through ' + ', '.join(c['via']) + ')'
        for s in [c['src']] + sorted(variants.get(c['src'], ())):
            e(s, c['dst'], 'CALL', trig, evidence='SRC %s:%s (bytecode)' % (c['file'], c['line']), auto=True)
    for l in auto['lambdas']:
        p = (l['src'], l['dst'])
        if p in manual or p in manual_reg or p in suppress or l['src'] in suppress:
            continue
        e(l['src'], l['dst'], 'REGISTER', 'Creates the lambda / method reference (its body runs when invoked)',
          evidence='SRC %s:%s (bytecode)' % (l['file'], l['line']), auto=True)


def assign_ids(edges):
    """Stable edge ids: a hash of the edge's content, so adding or removing other edges never renumbers an edge
    (stored paths and the audit log refer to these ids); an edge whose own text changes gets a new id."""
    seen = collections.Counter()
    for x in edges:
        key = '|'.join(str(x.get(k) or '') for k in ('src', 'dst', 'kind', 'trigger', 'guard', 'evidence', 'env', 'needs_state'))
        h = 'E' + hashlib.sha1(key.encode('utf-8')).hexdigest()[:8]
        seen[h] += 1
        x['id'] = h if seen[h] == 1 else '%s-%d' % (h, seen[h])


def evidence_labels(ev):
    """'SRC A.java:1; B.java:2; FW-MEMORY x' -> ['SRC', 'FW-MEMORY'] (a segment without a label continues the previous one)"""
    return [seg.split()[0] for seg in (ev or '').split(';') if seg.strip() and seg.split()[0] in EVIDENCE]


def edge_sourced(x):
    """True when every claim of the edge's evidence cites a source line (app source or AOSP source)."""
    labs = evidence_labels(x['evidence'])
    return bool(labs) and all(l in ('SRC', 'FW-SRC') for l in labs)


def evidence_ref(ev):
    """'SRC Main.java:646-695; FW-MEMORY ...' -> 'Main.java:646-695' (first source reference), else None."""
    m = re.search(r'(?:^|;\s*)(?:FW-)?SRC\s+([^\s;]+)', ev or '')
    return m.group(1) if m else None


def gate_items(path, key, kinds_key):
    """Distinct gates (text + kinds) on a path, in path order."""
    seen, res = set(), []
    for x in path:
        t = x.get(key)
        if t and t not in seen:
            seen.add(t)
            res.append({'kinds': x[kinds_key], 'text': t})
    return res


def norm_unreachable(m, v, legacy=None):
    """UNREACHABLE entry -> {'kind', 'text', 'ref', 'confirmed_by', 'legacy'}"""
    if isinstance(v, str):
        v = ('unclassified', v)
    kind, text = v[0], v[1]
    ref = v[2] if len(v) > 2 else None
    cb = v[3] if len(v) > 3 else ('SOURCE' if ref else 'INFERRED')
    return {'kind': kind, 'text': text, 'ref': ref, 'confirmed_by': cb, 'legacy': legacy}


def load_verification(gdir):
    path = os.path.join(gdir, 'verification.csv')
    if not os.path.isfile(path):
        return []
    with open(path, encoding='utf-8', newline='') as f:
        return [r for r in csv.DictReader(f) if (r.get('type') or '').strip() and not r['type'].strip().startswith('#')]


def main(argv):
    gdir, prefix = argv[1], argv[2]
    outdir = os.path.join(gdir, 'out')
    os.makedirs(outdir, exist_ok=True)
    rows = json.load(open(os.path.join(gdir, 'method_list.json')))
    methods, by_name = method_names(rows)

    edges = []

    def e(src, dst, kind, trigger, gui=(), guard=None, reads=(), writes=(), note=None,
          needs_state=None, evidence=None, env=None, auto=False, cls=None, via=None, env_kinds=(), state_kinds=()):
        x = {'src': src, 'dst': dst, 'kind': kind, 'trigger': trigger, 'gui': list(gui),
             'guard': guard, 'reads': list(reads), 'writes': list(writes), 'note': note,
             'needs_state': needs_state, 'evidence': evidence, 'env': env,
             'edge_class': cls, 'via': via, 'env_kinds': list(env_kinds), 'state_kinds': list(state_kinds)}
        if auto:
            x['auto'] = True
        edges.append(x)

    auto_path = os.path.join(gdir, 'auto_calls.json')
    auto_data = json.load(open(auto_path)) if os.path.isfile(auto_path) else None

    def impl(cls, name, desc=None):
        """Node that runs when method `name` is invoked on an instance of class `cls` (short name)."""
        tbl = (auto_data or {}).get('impl', {}).get(cls, {}).get(name)
        if not tbl:
            raise KeyError('impl: %s has no method %s' % (cls, name))
        if desc:
            return tbl[desc]
        if len(set(tbl.values())) != 1:
            raise KeyError('impl: %s.%s is overloaded, pass desc: %s' % (cls, name, sorted(tbl)))
        return next(iter(tbl.values()))

    ns = {'e': e, 'SCREENS': {}, 'DEAD': {}, 'FRAMEWORK_ONLY': {}, 'UNREACHABLE': {}, 'TITLE': '', 'NOTES': {},
          'USE_AUTO': False, 'SUPPRESS': set(), 'AUTO': auto_data, 'impl': impl, 'METHODS': list(methods),
          'GDIR': os.path.abspath(gdir), 'TOOLS': os.path.dirname(os.path.abspath(__file__)),
          'AUTO_DEAD': None, 'COVERAGE': None, 'CLASSIFY': None, 'EDIT': None, 'ENV_KINDS_OF': {}, 'STATE_KINDS_OF': {},
          'STRICT': False, 'HTML': True}
    src_path = os.path.join(gdir, 'graph_def.py')
    exec(compile(open(src_path, encoding='utf-8').read(), src_path, 'exec'), ns)
    screens, dead, fwo, notes = ns['SCREENS'], ns['DEAD'], ns['FRAMEWORK_ONLY'], ns['NOTES']
    strict = bool(ns['STRICT'])
    if ns['USE_AUTO']:
        add_auto_edges(gdir, edges, e, set(ns['SUPPRESS']))
    if ns['EDIT']:
        for x in edges:
            ns['EDIT'](x)
    assign_ids(edges)

    errors, warnings = [], []
    todo = []     # things still to classify (warnings, or errors in strict mode)
    known = set(methods) | set(screens)
    for x in edges:
        for end in ('src', 'dst'):
            if base(x[end]) not in known:
                errors.append('%s: unknown %s node %s' % (x['id'], end, x[end]))
        if x['kind'] not in KINDS:
            errors.append('%s: bad kind %s' % (x['id'], x['kind']))
        if x['kind'] == 'GUI' and (not is_screen(x['src']) or is_screen(x['dst'])):
            errors.append('%s: GUI edge must go page -> method' % x['id'])
        if x['kind'] == 'ENTERS' and not is_screen(x['dst']):
            errors.append('%s: ENTERS edge must end on a page' % x['id'])
        if not x['evidence'] or x['evidence'].split()[0] not in EVIDENCE:
            errors.append('%s: missing/invalid evidence label' % x['id'])

    # reachability labels that are decided by hand: UNREACHABLE (new) plus the legacy DEAD / FRAMEWORK_ONLY lists
    unreach = {m: norm_unreachable(m, v) for m, v in ns['UNREACHABLE'].items()}
    for m, t in dead.items():
        unreach.setdefault(m, norm_unreachable(m, t, 'DEAD'))
    for m, t in fwo.items():
        unreach.setdefault(m, norm_unreachable(m, t, 'FRAMEWORK_ONLY'))
    for m, u in unreach.items():
        if m not in methods:
            errors.append('UNREACHABLE entry for unknown method ' + m)
        if u['kind'] not in UNREACHABLE_KINDS:
            if u['kind'] == 'unclassified':
                todo.append('%s: unreachable reason has no kind (legacy DEAD / FRAMEWORK_ONLY entry): classify it' % m)
            else:
                errors.append('%s: bad unreachable kind %s' % (m, u['kind']))
        if u['confirmed_by'] not in CONFIRMED:
            errors.append('%s: bad confirmed_by %s' % (m, u['confirmed_by']))

    if ns.get('AUTO_DEAD'):   # drop pages (and their edges) that nothing reaches
        o0 = collections.defaultdict(list)
        for x in edges:
            o0[x['src']].append(x)
        reach = bfs(o0, allow_setup=True)
        gone = {s_ for s_ in screens if s_ != 'S_ENTRY' and not any(base(n) == s_ for n in reach)}
        if gone:
            edges[:] = [x for x in edges if base(x['src']) not in gone and base(x['dst']) not in gone]
            for s_ in gone:
                del screens[s_]
            assign_ids(edges)

    # edge classes (explicit / standard / non_standard / page) and the kinds of the ENV / STATE gates
    classify = ns.get('CLASSIFY')
    env_of, state_of = ns['ENV_KINDS_OF'], ns['STATE_KINDS_OF']
    hint_review = []
    for x in edges:
        x['class_basis'] = 'authored'
        if not x['edge_class'] and classify:
            r = classify(x)
            if r:
                x['edge_class'], x['via'] = r if isinstance(r, tuple) else (r, x['via'])
        if not x['edge_class']:
            x['edge_class'] = 'page' if is_screen(x['dst']) else DEFAULT_CLASS.get(x['kind'], 'standard')
            x['class_basis'] = 'default'
            if x['class_basis'] == 'default' and NONSTD_HINT.search(' '.join(str(x.get(k) or '') for k in ('trigger', 'note', 'guard', 'evidence'))):
                hint_review.append(x['id'])
        if x['edge_class'] not in EDGE_CLASSES:
            errors.append('%s: bad edge class %s' % (x['id'], x['edge_class']))
        if x['edge_class'] == 'non_standard' and not x['via']:
            todo.append('%s: non_standard edge without via (name the library or mechanism)' % x['id'])
        for key, kinds_key, table, vocab, what in (('env', 'env_kinds', env_of, ENV_KINDS, 'ENV'),
                                                   ('needs_state', 'state_kinds', state_of, STATE_KINDS, 'STATE')):
            if not x[key]:
                if x[kinds_key]:
                    errors.append('%s: %s kinds without a %s gate text' % (x['id'], what, key))
                continue
            kinds = list(x[kinds_key]) or list(table.get(x[key], ()))
            if not kinds:
                x[kinds_key] = ['unclassified']
                todo.append('%s: %s gate has no kinds: %s' % (x['id'], what, x[key][:80]))
                continue
            bad = [k for k in kinds if k not in vocab]
            if bad:
                errors.append('%s: bad %s kind %s' % (x['id'], what, ', '.join(bad)))
            x[kinds_key] = kinds
    if strict and ns.get('AUTO_DEAD'):
        errors.append('STRICT: AUTO_DEAD is not allowed (every UNREACHABLE needs an authored reason)')

    out, inn = collections.defaultdict(list), collections.defaultdict(list)
    for x in edges:
        out[x['src']].append(x)
        inn[base(x['dst'])].append(x)

    prev = bfs(out, allow_setup=False)
    prev_setup = bfs(out, allow_setup=True)
    prev_noenv = bfs(out, allow_setup=True, allow_env=False)
    prev_expl = bfs(out, allow_setup=True, classes={'explicit', 'standard', 'page'})
    prefer = bool(ns.get('PREFER_SETUP_OVER_ENV'))
    prev_clean = bfs(out, allow_setup=False, allow_env=False) if prefer else None
    best_first = cheapest(out, allow_setup=False)     # path choice: fewest environment gates, then fewest steps
    best_setup = cheapest(out, allow_setup=True)

    def first_variant(m, pv):
        for n in pv:  # dict keeps BFS discovery order, so the first hit is the shortest
            if base(n) == m:
                return n
        return None

    verdict, info = {}, {}
    auto_dead = set()
    for m in methods:
        mode = None     # 'clean': a route without any needs_state edge; 'setup': a route that needs earlier in-app actions
        if m in unreach:
            verdict[m] = 'UNREACHABLE'
        elif prefer and first_variant(m, prev_clean):
            verdict[m], mode = 'REACHABLE', 'clean'
        elif prefer and first_variant(m, prev_noenv):
            verdict[m], mode = 'REACHABLE', 'setup'   # in-app setup only: better than a route that needs the environment
        elif first_variant(m, prev):
            verdict[m], mode = 'REACHABLE', 'clean'
        elif first_variant(m, prev_setup):
            verdict[m], mode = 'REACHABLE', 'setup'
        elif ns.get('AUTO_DEAD'):
            verdict[m] = 'UNREACHABLE'
            auto_dead.add(m)
            unreach[m] = norm_unreachable(m, ns['AUTO_DEAD'] if isinstance(ns['AUTO_DEAD'], str) else 'No route found from the entry points', 'AUTO_DEAD')
            todo.append('%s: no route found, labelled UNREACHABLE by AUTO_DEAD: read the source and give a reason' % m)
        else:
            verdict[m] = 'UNRESOLVED'
            errors.append('method has no path and no UNREACHABLE entry: ' + m)
        if verdict[m] == 'UNREACHABLE' and m not in auto_dead:
            live = [x['id'] for x in inn.get(m, []) if x['kind'] != 'REGISTER']
            if live:
                warnings.append('%s is UNREACHABLE but has incoming edges %s' % (m, live))
        # best route. Converted graphs (STRICT): of the cheapest route without any needs_state edge and the cheapest route over all edges, take
        # the one with the fewest ENV kinds, then the fewest STATE kinds, then the fewest steps. Schema-1 graphs: a route without any
        # needs_state edge first.
        v, pv, p = None, None, []
        if mode and strict:
            cands = []
            for cand in (best_first, best_setup):
                v = first_variant(m, cand)
                if v:
                    cands.append(path_to(v, cand))
            p = min(cands, key=lambda q: (len({k for x in q for k in x['env_kinds']}), len({k for x in q for k in x['state_kinds']}), len(q)))
        elif mode:
            for cand in ([best_first] if mode == 'clean' else [best_setup]):
                v = first_variant(m, cand)
                if v:
                    pv = cand
                    break
            p = path_to(v, pv) if v else []
        info[m] = {'path': p, 'env_gated': any(x.get('env') for x in p)}

    pages = set(screens)
    for s in pages:
        if s not in ('S_ENTRY',) and not any(base(n) == s for n in prev_setup):
            errors.append('page not reachable from S_ENTRY: ' + s)

    # per-method labels
    labels = {}
    for m in methods:
        p = info[m]['path']
        if verdict[m] == 'UNREACHABLE':
            u = unreach[m]
            lab = {'unreachable': {'kind': u['kind'], 'text': u['text']}, 'confirmed_by': u['confirmed_by'], 'source_ref': u['ref'],
                   'path_status': None}
        else:
            lab = {'env': gate_items(p, 'env', 'env_kinds'), 'state': gate_items(p, 'needs_state', 'state_kinds'),
                   'route_edge_classes': sorted({x['edge_class'] for x in p} - {'page'}),
                   'explicit_standard_route': bool(first_variant(m, prev_expl)),
                   'confirmed_by': 'SOURCE' if p and all(edge_sourced(x) for x in p) else 'INFERRED',
                   'source_ref': evidence_ref(p[-1]['evidence']) if p else None,
                   'path_status': 'UNCHECKED'}
        labels[m] = lab

    # audit log (verification.csv): confirmations, path status, stored paths, error rates
    vrows = load_verification(gdir)
    edge_ids = {x['id'] for x in edges}
    counts = {t: collections.Counter() for t in VERIFY_TYPES}
    stored_paths = []
    for r in vrows:
        t, item, res = r['type'].strip(), (r.get('item') or '').strip(), (r.get('result') or '').strip()
        cb = (r.get('confirmed_by') or 'INFERRED').strip()
        if t not in VERIFY_TYPES or res not in RESULTS or cb not in CONFIRMED:
            errors.append('verification.csv: bad row %s' % dict(r))
            continue
        if t == 'edge':
            if item not in edge_ids:
                warnings.append('verification.csv: edge %s no longer exists (the edge text changed): re-verify it' % item)
                continue
        elif item not in labels:
            errors.append('verification.csv: unknown method %s' % item)
            continue
        counts[t][res] += 1
        if t == 'label' and res in ('correct', 'fixed'):
            labels[item]['confirmed_by'] = cb
            if r.get('ref'):
                labels[item]['source_ref'] = r['ref'].strip()
        elif t == 'path' and verdict[item] == 'REACHABLE':
            ids = (r.get('edges') or '').split()
            current = [x['id'] for x in info[item]['path']]
            if res == 'wrong':
                labels[item]['path_status'] = 'WRONG'
            elif res == 'unclear':
                labels[item]['path_status'] = 'UNCHECKED'
            elif ids != current:
                labels[item]['path_status'] = 'STALE'
                warnings.append('verification.csv: the verified path of %s is no longer the best route: re-verify' % item)
            else:
                labels[item]['path_status'] = {'DEVICE': 'DEVICE_OK', 'SOURCE': 'SOURCE_OK'}.get(cb, 'UNCHECKED')
                if cb in ('DEVICE', 'SOURCE'):
                    p = info[item]['path']
                    cls = sorted({x['edge_class'] for x in p} - {'page'})
                    stored_paths.append({'method': item, 'edges': current, 'edge_classes': cls,
                                         'explicit_standard_only': 'non_standard' not in cls,
                                         'env': labels[item]['env'], 'state': labels[item]['state'],
                                         'verified_by': cb, 'ref': (r.get('ref') or '').strip() or None})
    verification = None
    if vrows:
        verification = {}
        for t in VERIFY_TYPES:
            c = counts[t]
            checked = c['correct'] + c['fixed'] + c['wrong']
            verification[t] = {'checked': checked, 'correct': c['correct'], 'errors_found': c['fixed'] + c['wrong'], 'unclear': c['unclear'],
                               'error_rate': round((c['fixed'] + c['wrong']) / checked, 3) if checked else None}
        verification['reachable_methods'] = sum(1 for m in methods if verdict[m] == 'REACHABLE')

    if todo:
        (errors if strict else warnings).extend(['TO CLASSIFY ' + s for s in todo[:200]] + (['TO CLASSIFY ... %d more' % (len(todo) - 200)] if len(todo) > 200 else []))
    if hint_review:
        warnings.append('REVIEW %d edges on the default class mention a library/reflection hint (EventBus, ButterKnife, android:onClick, ...): '
                        'check they are not non_standard: %s' % (len(hint_review), ' '.join(hint_review[:40]) + (' ...' if len(hint_review) > 40 else '')))

    graph = {'schema': 2, 'title': ns['TITLE'], 'screens': screens, 'methods': methods, 'verdict': verdict, 'labels': labels,
             'edges': edges, 'paths': stored_paths, 'verification': verification}
    jpath = os.path.join(outdir, prefix + '_trigger_graph.json')
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=1, ensure_ascii=False)

    cov = {}
    cpath = os.path.join(gdir, 'coverage_baseline.json')
    if os.path.isfile(cpath):
        for r in json.load(open(cpath)):
            cov[(r.get('class'), r['short'], r['desc'])] = r

    def tool_hit(m):
        c = cov.get((by_name[m]['class'], by_name[m]['short'], by_name[m]['desc']), {})
        return bool(c.get('monkey') or c.get('ape'))

    # optional: frontier of the baseline coverage (where the nearest tool-run method leads into code no tool ran).
    # Not a label and off by default: it uses tool coverage, so it never goes into methods.csv.
    frontier = {}
    if cov and ns.get('FRONTIER', False):
        hit_set = {m for m in methods if tool_hit(m)}
        nodes_all = {x['src'] for x in edges} | {x['dst'] for x in edges}
        prevf = {}
        dq = collections.deque()
        for n in sorted(nodes_all):
            if not is_screen(n) and base(n) in hit_set:
                prevf[n] = None
                dq.append(n)
        while dq:
            n = dq.popleft()
            for x in out.get(n, []):
                if x['kind'] == 'REGISTER' or x['dst'] in prevf:
                    continue
                prevf[x['dst']] = x
                dq.append(x['dst'])
        first = {}
        for n in prevf:
            first.setdefault(base(n), n)
        for m in methods:
            if m in hit_set or verdict[m] != 'REACHABLE' or m not in first:
                continue
            chain, n = [], first[m]
            while prevf.get(n):
                chain.append(prevf[n])
                n = prevf[n]['src']
            chain.reverse()      # edges from the hit method (n) to the target
            k = None
            for i, x in enumerate(chain):
                if not is_screen(x['dst']) and base(x['dst']) not in hit_set:
                    k = i
                    break
            if k is None:
                continue
            fx = chain[k]
            ev = [t.strip() for t in (fx['evidence'] or '').split(';')]
            frontier[m] = (base(fx['src']), fx['dst'], fx['kind'], next((t for t in ev if t.startswith('SRC')), ev[0]), len(chain) - k)
    if frontier:
        with open(os.path.join(outdir, 'frontier.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['method', 'frontier_from', 'frontier_first_unrun', 'frontier_edge_kind', 'frontier_edge_evidence', 'steps_after_frontier'])
            for m in methods:
                if m in frontier:
                    w.writerow([m] + list(frontier[m]))

    def kinds_of(items):
        return ';'.join(sorted({k for it in items for k in it['kinds']}))

    with open(os.path.join(outdir, 'methods.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['method', 'verdict', 'unreachable_kind', 'unreachable_reason', 'env_kinds', 'env', 'state_kinds', 'state',
                    'route_edge_classes', 'explicit_standard_route', 'confirmed_by', 'source_ref', 'path_status',
                    'steps_from_launch', 'gui_steps_on_shortest_path', 'shortest_path', 'route_edge_ids', 'incoming_edges', 'note', 'jvm_descriptor'])
        for m in methods:
            p, lab = info[m]['path'], labels[m]
            un = lab.get('unreachable') or {}
            r = by_name[m]
            w.writerow([m, verdict[m], un.get('kind', ''), un.get('text', ''),
                        kinds_of(lab.get('env', [])), ' | '.join(it['text'] for it in lab.get('env', [])),
                        kinds_of(lab.get('state', [])), ' | '.join(it['text'] for it in lab.get('state', [])),
                        ';'.join(lab.get('route_edge_classes', [])),
                        '' if 'explicit_standard_route' not in lab else ('yes' if lab['explicit_standard_route'] else 'no'),
                        lab['confirmed_by'], lab['source_ref'] or '', lab['path_status'] or '',
                        len(p) if p else '', ' ; '.join(gui_steps(p)),
                        ' > '.join([p[0]['src']] + [x['dst'] for x in p]) if p else '', ' '.join(x['id'] for x in p),
                        sum(1 for x in inn.get(m, []) if x['kind'] != 'REGISTER'),
                        notes.get(m) or '', r['desc']])

    if cov:    # one-way sanity check: a method a tool ran cannot be UNREACHABLE; never used to set a label
        with open(os.path.join(outdir, 'sanity_check.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['method', 'verdict', 'monkey_hit', 'ape_hit', 'flag'])
            for m in methods:
                c = cov.get((by_name[m]['class'], by_name[m]['short'], by_name[m]['desc']), {})
                flag = ''
                if tool_hit(m) and verdict[m] == 'UNREACHABLE':
                    flag = 'CONTRADICTION'
                elif tool_hit(m) and info[m]['env_gated']:
                    flag = 'ENV_GATED_BUT_HIT'
                w.writerow([m, verdict[m], int(bool(c.get('monkey'))) if c else '', int(bool(c.get('ape'))) if c else '', flag])

    if ns.get('HTML', True) and os.path.isfile(TEMPLATE):
        data = json.dumps(graph, ensure_ascii=False).replace('</', '<\\/')
        html = open(TEMPLATE, encoding='utf-8').read().replace('/*DATA*/', data)
        with open(os.path.join(outdir, prefix + '_trigger_graph.html'), 'w', encoding='utf-8') as f:
            f.write(html)

    # report
    rep = []
    vc = collections.Counter(verdict.values())
    rep.append('methods %d, pages %d, edges %d' % (len(methods), len(screens), len(edges)))
    rep.append('verdicts: ' + ', '.join('%s %d' % kv for kv in sorted(vc.items())))
    rep.append('unreachable by kind: ' + (', '.join('%s %d' % kv for kv in sorted(collections.Counter(u['kind'] for m, u in unreach.items() if m in methods).items())) or 'none'))
    rep.append('edge kinds: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(x['kind'] for x in edges).items())))
    rep.append('edge classes: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(x['edge_class'] for x in edges).items()))
               + '; class set by hand: %d of %d' % (sum(1 for x in edges if x['class_basis'] == 'authored'), len(edges)))
    rep.append('auto edges (from bytecode): %d of %d' % (sum(1 for x in edges if x.get('auto')), len(edges)))
    rep.append('evidence: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(x['evidence'].split()[0] for x in edges).items())))
    rep.append('edges with a claim that cites no source line (FW-MEMORY, INFERRED, DYN, UNVERIFIED): %d of %d' % (sum(1 for x in edges if not edge_sourced(x)), len(edges)))
    rep.append('needs_state edges: %d; env edges: %d; methods with ENV: %d, with STATE: %d' % (
        sum(1 for x in edges if x['needs_state']), sum(1 for x in edges if x.get('env')),
        sum(1 for m in methods if labels[m].get('env')), sum(1 for m in methods if labels[m].get('state'))))
    reach = [m for m in methods if verdict[m] == 'REACHABLE']
    rep.append('reachable methods whose best route has a non-standard edge: %d; with no explicit/standard-only route at all: %d' % (
        sum(1 for m in reach if 'non_standard' in labels[m]['route_edge_classes']),
        sum(1 for m in reach if not labels[m]['explicit_standard_route'])))
    rep.append('labels confirmed by: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(l['confirmed_by'] for l in labels.values()).items())))
    rep.append('path status: ' + ', '.join('%s %d' % kv for kv in sorted(collections.Counter(l['path_status'] for l in labels.values() if l['path_status']).items())))
    if verification:
        for t in VERIFY_TYPES:
            v = verification[t]
            rep.append('verification %s: checked %d, errors found %d (rate %s), unclear %d' % (t, v['checked'], v['errors_found'], v['error_rate'], v['unclear']))
    if cov:
        contra = [m for m in methods if verdict[m] == 'UNREACHABLE' and tool_hit(m)]
        gated_hit = [m for m in methods if verdict[m] == 'REACHABLE' and tool_hit(m) and info[m]['env_gated']]
        unreported = [m for m in methods if (by_name[m]['class'], by_name[m]['short'], by_name[m]['desc']) not in cov]
        rep.append('sanity check (tool coverage; never used to set a label): %d methods ran in a tool run; %d UNREACHABLE but ran (contradictions); '
                   '%d ENV-gated on the best route but ran' % (sum(1 for m in methods if tool_hit(m)), len(contra), len(gated_hit)))
        for m in contra:
            rep.append('  CONTRADICTION: %s is UNREACHABLE but ran in a tool run: read the source, do not just flip the label' % m)
        for m in gated_hit:
            rep.append('  ENV-GATED BUT RAN: %s' % m)
        rep.append('not in the JaCoCo report (filtered trivial methods): %s' % (', '.join(unreported) or 'none'))
    rep.append('errors: %d' % len(errors))
    rep += ['  ERROR ' + s for s in errors]
    rep.append('warnings: %d' % len(warnings))
    rep += ['  WARN ' + s for s in warnings]
    text = '\n'.join(rep)
    with open(os.path.join(outdir, 'build_report.txt'), 'w', encoding='utf-8') as f:
        f.write(text + '\n')
    print(text)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
