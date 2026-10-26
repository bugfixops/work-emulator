"""Extract direct call edges between app methods from compiled .class files.

Usage: python3 -I extract_calls.py <graph_dir> <classes_dir> [<classes_dir> ...]

Reads <graph_dir>/method_list.json (the method universe) and writes
<graph_dir>/auto_calls.json:
  calls:   [{src, dst, line, file, via, dispatch}]  app method -> app method
  lambdas: [{src, dst, line, file}]                 a lambda / method reference is created in src
                                                    (dst is its body; usually a REGISTER candidate)
  framework_calls: {src: [owner.name, ...]}         framework methods each app method calls (for modelling)

Resolution:
- invokestatic / invokespecial: the declared method, or the nearest app superclass that declares it.
- invokevirtual / invokeinterface on an app type: the resolved method plus every override in app
  subclasses / implementors (class hierarchy analysis); edges added only by CHA have dispatch='cha'.
- Self-calls inside an inherited method (base-class "template methods": this.x() where x is overridden)
  get receiver-class variants: Base.m@Sub calls Sub's overrides only. impl[Sub][name][desc] gives the node
  that runs for a Sub instance (Sub.m, Base.m@Sub or Base.m); graph_def.py can use impl(Sub, name).
- Calls through methods outside the universe (synthetic accessors, generated code such as Dagger,
  bridges) are collapsed: the edge goes from the universe caller to the universe callee, and `via`
  names the skipped methods.
Line numbers come from the LineNumberTable, file names from the SourceFile attribute.
"""
import collections
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_graph import method_names  # noqa: E402

INVOKES = {0xb6: 'virtual', 0xb7: 'special', 0xb8: 'static', 0xb9: 'interface', 0xba: 'dynamic'}
# opcode -> operand byte count (fixed-size instructions); tableswitch/lookupswitch/wide handled apart
OPLEN = {}
for op in list(range(0x00, 0x10)) + list(range(0x1a, 0x36)) + list(range(0x3b, 0x84)) + list(range(0x85, 0x99)) + \
        list(range(0xac, 0xb2)) + [0xbe, 0xbf, 0xc2, 0xc3]:
    OPLEN[op] = 0
for op in [0x10, 0x12, 0x15, 0x16, 0x17, 0x18, 0x19, 0x36, 0x37, 0x38, 0x39, 0x3a, 0xa9, 0xbc]:
    OPLEN[op] = 1
for op in [0x11, 0x13, 0x14, 0x84, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xbb, 0xbd, 0xc0, 0xc1, 0xc6, 0xc7] + \
        list(range(0x99, 0xa9)):
    OPLEN[op] = 2
OPLEN[0xc5] = 3
for op in [0xb9, 0xba, 0xc8, 0xc9]:
    OPLEN[op] = 4


class ClassInfo:
    pass


def _skip_value(d, p):
    tag = chr(d[p])
    p += 1
    if tag in 'BCDFIJSZsc':
        return p + 2
    if tag == 'e':
        return p + 4
    if tag == '@':
        return _skip_annotation(d, p)[1]
    if tag == '[':
        (n,) = struct.unpack_from('>H', d, p)
        p += 2
        for _ in range(n):
            p = _skip_value(d, p)
        return p
    raise ValueError('bad annotation element tag ' + tag)


def _skip_annotation(d, p):
    ti, npairs = struct.unpack_from('>HH', d, p)
    p += 4
    for _ in range(npairs):
        p = _skip_value(d, p + 2)
    return ti, p


def parse_annos(d, ap, utf):
    """Type descriptors of a RuntimeVisibleAnnotations attribute, e.g. 'Lorg/greenrobot/eventbus/Subscribe;'."""
    (n,) = struct.unpack_from('>H', d, ap)
    p, out = ap + 2, []
    for _ in range(n):
        ti, p = _skip_annotation(d, p)
        out.append(utf(ti))
    return out


def parse_class(path):
    d = open(path, 'rb').read()
    (count,) = struct.unpack_from('>H', d, 8)
    pool, pos, i = [None] * count, 10, 1
    while i < count:
        tag = d[pos]
        pos += 1
        if tag == 1:
            (n,) = struct.unpack_from('>H', d, pos)
            pool[i] = ('utf', d[pos + 2:pos + 2 + n].decode('utf-8', 'replace'))
            pos += 2 + n
        elif tag in (3, 4):
            pos += 4
        elif tag in (5, 6):
            pos += 8
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            pool[i] = (tag, struct.unpack_from('>H', d, pos)[0])
            pos += 2
        elif tag in (9, 10, 11, 12, 17, 18):
            pool[i] = (tag,) + struct.unpack_from('>HH', d, pos)
            pos += 4
        elif tag == 15:
            pool[i] = (15, d[pos]) + struct.unpack_from('>H', d, pos + 1)
            pos += 3
        else:
            raise ValueError('bad tag %d in %s' % (tag, path))
        i += 1
    utf = lambda k: pool[k][1]
    cname = lambda k: utf(pool[k][1])

    def ref(k):  # Methodref / InterfaceMethodref -> (owner, name, desc)
        _, ci, nti = pool[k]
        _, ni, di = pool[nti]
        return cname(ci), utf(ni), utf(di)

    ci = ClassInfo()
    ci.access, this_i, super_i = struct.unpack_from('>HHH', d, pos)
    pos += 6
    ci.name = cname(this_i)
    ci.super = cname(super_i) if super_i else None
    (ni,) = struct.unpack_from('>H', d, pos)
    ci.interfaces = [cname(struct.unpack_from('>H', d, pos + 2 + 2 * j)[0]) for j in range(ni)]
    pos += 2 + 2 * ni

    def attrs(p):
        (n,) = struct.unpack_from('>H', d, p)
        p += 2
        out = []
        for _ in range(n):
            ai, alen = struct.unpack_from('>HI', d, p)
            out.append((utf(ai), p + 6, alen))
            p += 6 + alen
        return p, out

    (nf,) = struct.unpack_from('>H', d, pos)
    pos += 2
    for _ in range(nf):
        pos, _a = attrs(pos + 6)
    (nm,) = struct.unpack_from('>H', d, pos)
    pos += 2
    raw_methods = []
    for _ in range(nm):
        acc, mni, mdi = struct.unpack_from('>HHH', d, pos)
        pos, ma = attrs(pos + 6)
        raw_methods.append((acc, utf(mni), utf(mdi), ma))
    pos, ca = attrs(pos)
    ci.source = None
    bootstrap = []
    for an, ap, alen in ca:
        if an == 'SourceFile':
            ci.source = utf(struct.unpack_from('>H', d, ap)[0])
        elif an == 'BootstrapMethods':
            (nb,) = struct.unpack_from('>H', d, ap)
            p = ap + 2
            for _ in range(nb):
                mh, na = struct.unpack_from('>HH', d, p)
                args = [struct.unpack_from('>H', d, p + 4 + 2 * j)[0] for j in range(na)]
                bootstrap.append((mh, args))
                p += 4 + 2 * na

    def lambda_impl(bsm_index):
        """For a LambdaMetafactory bootstrap, return the (owner, name, desc) of the implementation."""
        mh, args = bootstrap[bsm_index]
        _, _kind, r = pool[mh]
        if ref(r)[1] not in ('metafactory', 'altMetafactory'):
            return None
        for a in args:
            if pool[a] and pool[a][0] == 15:
                return ref(pool[a][2])
        return None

    ci.methods = {}
    for acc, name, desc, ma in raw_methods:
        m = {'access': acc, 'name': name, 'desc': desc, 'calls': [], 'lambdas': [], 'lam_meta': [], 'annos': [],
             'ldc_classes': [], 'ldc_strings': [], 'class_refs': [], 'new_refs': [], 'ref_lines': {}, 'lines': None, 'linenos': ()}
        for an, ap, alen in ma:
            if an == 'RuntimeVisibleAnnotations':
                m['annos'] = parse_annos(d, ap, utf)
                continue
            if an != 'Code':
                continue
            (clen,) = struct.unpack_from('>I', d, ap + 4)
            code = d[ap + 8:ap + 8 + clen]
            lines = []
            p2 = ap + 8 + clen
            (exl,) = struct.unpack_from('>H', d, p2)
            p2 += 2 + 8 * exl
            _p, cattrs = attrs(p2)
            for can, cap, calen in cattrs:
                if can == 'LineNumberTable':
                    (nl,) = struct.unpack_from('>H', d, cap)
                    lines += [struct.unpack_from('>HH', d, cap + 2 + 4 * j) for j in range(nl)]
            lines.sort()
            if lines:
                m['lines'] = (lines[0][1], max(l for _s, l in lines))
                m['linenos'] = tuple(sorted({l for _s, l in lines}))

            def line_at(off):
                ln = None
                for start, l in lines:
                    if start > off:
                        break
                    ln = l
                return ln

            pc = 0
            while pc < len(code):
                op = code[pc]
                if op in INVOKES:
                    (k,) = struct.unpack_from('>H', code, pc + 1)
                    if op == 0xba:
                        _, bsi, nti = pool[k]
                        impl = lambda_impl(bsi)
                        if impl:
                            m['lambdas'].append((impl, line_at(pc)))
                            _, sni, sdi = pool[nti]  # NameAndType: SAM name, (captures)Liface;
                            m['lam_meta'].append((impl, utf(sni), utf(sdi).split(')')[-1]))
                    else:
                        m['calls'].append((INVOKES[op], ref(k), line_at(pc)))
                        if op == 0xb8:
                            m['class_refs'].append(ref(k)[0])
                            m['ref_lines'].setdefault(ref(k)[0], line_at(pc))
                elif op in (0x12, 0x13):  # ldc / ldc_w
                    k = code[pc + 1] if op == 0x12 else struct.unpack_from('>H', code, pc + 1)[0]
                    ent = pool[k]
                    if ent and ent[0] == 7:
                        m['ldc_classes'].append((cname(k), line_at(pc)))
                    elif ent and ent[0] == 8:
                        m['ldc_strings'].append((utf(ent[1]), line_at(pc)))
                elif op in (0xb2, 0xb3):  # getstatic / putstatic
                    (k,) = struct.unpack_from('>H', code, pc + 1)
                    m['class_refs'].append(cname(pool[k][1]))
                    m['ref_lines'].setdefault(cname(pool[k][1]), line_at(pc))
                elif op == 0xbb:  # new
                    (k,) = struct.unpack_from('>H', code, pc + 1)
                    m['class_refs'].append(cname(k))
                    m['ref_lines'].setdefault(cname(k), line_at(pc))
                    m['new_refs'].append((cname(k), line_at(pc)))
                if op == 0xaa:  # tableswitch
                    p = pc + 1 + (3 - pc % 4)
                    low, high = struct.unpack_from('>ii', code, p + 4)
                    pc = p + 12 + 4 * (high - low + 1)
                elif op == 0xab:  # lookupswitch
                    p = pc + 1 + (3 - pc % 4)
                    (npairs,) = struct.unpack_from('>i', code, p + 4)
                    pc = p + 8 + 8 * npairs
                elif op == 0xc4:  # wide
                    pc += 6 if code[pc + 1] == 0x84 else 4
                else:
                    if op not in OPLEN:
                        raise ValueError('unknown opcode 0x%02x in %s.%s' % (op, ci.name, name))
                    pc += 1 + OPLEN[op]
        ci.methods[(name, desc)] = m
    return ci


def main(argv):
    gdir, cdirs = argv[1], argv[2:]
    classes = {}
    for cdir in cdirs:
        for dp, _ds, fs in os.walk(cdir):
            for f in fs:
                if f.endswith('.class'):
                    ci = parse_class(os.path.join(dp, f))
                    classes[ci.name] = ci
    rows = json.load(open(os.path.join(gdir, 'method_list.json')))
    names, by_name = method_names(rows)
    uname = {}  # (class, name, desc) -> universe node name
    for n in names:
        r = by_name[n]
        uname[(r['class'], r['name'], r['desc'])] = n

    subs = collections.defaultdict(set)  # class -> direct app subtypes
    for c in classes.values():
        for s_ in [c.super] + c.interfaces:
            if s_ in classes:
                subs[s_].add(c.name)
    is_iface = lambda c: c in classes and classes[c].access & 0x0200
    is_concrete = lambda c: c in classes and not classes[c].access & 0x0600

    def all_supers(c):
        seen, stack = [], [c]
        while stack:
            x = stack.pop()
            if x not in classes:
                continue
            for s_ in [classes[x].super] + classes[x].interfaces:
                if s_ and s_ not in seen:
                    seen.append(s_)
                    stack.append(s_)
        return seen

    def all_subs(c):
        seen, stack = set(), [c]
        while stack:
            for s_ in subs.get(stack.pop(), ()):
                if s_ not in seen:
                    seen.add(s_)
                    stack.append(s_)
        return seen

    def declared_up(owner, name, desc):
        c = owner
        while c in classes:
            if (name, desc) in classes[c].methods:
                return c
            c = classes[c].super
        for c2 in all_supers(owner):  # default methods
            if c2 in classes and (name, desc) in classes[c2].methods:
                return c2
        return None

    def has_body(c, name, desc):
        return not classes[c].methods[(name, desc)]['access'] & 0x0400

    # ---- receiver-class contexts for inherited methods ("template method" self-calls)
    def is_self(cur, kind, owner):
        return kind in ('virtual', 'special') and owner in classes and not is_iface(owner) and \
            (owner == cur or owner in all_supers(cur) or cur in all_supers(owner))

    def resolve_self(rt, name, desc):
        d = declared_up(rt, name, desc)
        return d if d and has_body(d, name, desc) else None

    # needs_variant[(decl, name, desc, rt)]: method declared in decl, running with receiver class rt (rt != decl,
    # rt does not override it), whose self-calls resolve differently than for decl itself.
    needs = set()
    changed = True
    concrete_subs = {c: [s_ for s_ in all_subs(c) if is_concrete(s_)] for c in classes}
    while changed:
        changed = False
        for c in classes.values():
            for (mn, md), m in c.methods.items():
                if m['access'] & 0x0008 or mn in ('<init>', '<clinit>'):
                    continue
                for rt in concrete_subs[c.name]:
                    # rt may override this method and still reach it through super.m()
                    if (c.name, mn, md, rt) in needs:
                        continue
                    for kind, (owner, name, desc), line in m['calls']:
                        if not is_self(c.name, kind, owner):
                            continue
                        if kind == 'special':  # super.x() / private: fixed target, but it may itself need rt
                            t = declared_up(owner, name, desc)
                        else:
                            t = resolve_self(rt, name, desc)
                        t_base = declared_up(owner, name, desc) if kind == 'special' else resolve_self(c.name, name, desc)
                        if t != t_base or (t and t != rt and (t, name, desc, rt) in needs):
                            needs.add((c.name, mn, md, rt))
                            changed = True
                            break

    def node(decl, name, desc, rt=None):
        """Universe node for method (decl, name, desc) running with receiver class rt."""
        if (decl, name, desc) not in uname:
            return None
        n = uname[(decl, name, desc)]
        if rt and rt != decl and (decl, name, desc, rt) in needs:
            return n + '@' + rt.rsplit('/', 1)[-1]
        return n

    def targets(cur, rt, kind, owner, name, desc):
        """[(class, dispatch, receiver_ctx)] for one invoke inside a method of class cur running with receiver rt."""
        if owner not in classes:
            return []
        if is_self(cur, kind, owner) and name != '<init>':
            if kind == 'special':
                t = declared_up(owner, name, desc)
                return [(t, 'exact', rt)] if t and has_body(t, name, desc) else []
            t = resolve_self(rt or cur, name, desc)
            if t:
                return [(t, 'exact', rt or cur)]
            if rt is None:  # abstract here and no receiver context: every concrete implementation
                return [(s_, 'cha', s_) for s_ in concrete_subs[cur] if declared_up(s_, name, desc) == s_]
            return []
        out = []
        decl = declared_up(owner, name, desc)
        if decl and has_body(decl, name, desc):
            out.append((decl, 'exact', None))
        if kind in ('virtual', 'interface') and name != '<init>':
            for s_ in all_subs(owner):
                if (name, desc) in classes[s_].methods and has_body(s_, name, desc):
                    out.append((s_, 'cha', None))
        return out

    # raw edges: (node_key) -> [(callee key, line, dispatch, callee_rt)]
    def raw_calls(c, mn, md, rt):
        m = c.methods[(mn, md)]
        res = []
        eff = rt or (c.name if is_concrete(c.name) else None)  # a concrete class's own code runs on itself
        for kind, (owner, name, desc), line in m['calls']:
            for tc, disp, crt in targets(c.name, eff, kind, owner, name, desc):
                res.append(((tc, name, desc), line, disp, crt))
        for rc in set(m['class_refs']):   # first use of a class (new, getstatic, putstatic, invokestatic) runs its <clinit>
            if rc == c.name:
                continue
            for k_ in [rc] + [x for x in all_supers(rc) if x in classes]:
                if k_ in classes and ('<clinit>', '()V') in classes[k_].methods:
                    res.append(((k_, '<clinit>', '()V'), m['ref_lines'].get(rc), 'exact', None))
        return res

    fw = collections.defaultdict(set)
    lambdas = []
    for c in classes.values():
        for (mn, md), m in c.methods.items():
            for kind, (owner, name, desc), line in m['calls']:
                if owner not in classes:
                    fw[(c.name, mn, md)].add('%s.%s' % (owner.rsplit('/', 1)[-1], name))
                elif name != '<init>' and not declared_up(owner, name, desc):   # inherited framework method called on an app-typed receiver
                    fw[(c.name, mn, md)].add('%s.%s' % (owner.rsplit('/', 1)[-1], name))
            for (owner, name, desc), line in m['lambdas']:
                lambdas.append(((c.name, mn, md), (owner, name, desc), line, c.source))

    def short_key(k):
        return '%s.%s' % (k[0].rsplit('/', 1)[-1], k[1])

    calls, seen = [], set()
    sources = [(c, mn, md, None) for c in classes.values() for (mn, md) in c.methods]
    sources += [(classes[d], mn, md, rt) for (d, mn, md, rt) in sorted(needs)]
    for c, mn, md, rt in sources:
        src = node(c.name, mn, md, rt)
        if not src:
            continue
        stack = [(t, line, disp, crt, []) for t, line, disp, crt in raw_calls(c, mn, md, rt)]
        visited = set()
        while stack:
            t, line, disp, crt, via = stack.pop()
            if t in uname:
                dst = node(t[0], t[1], t[2], crt)
                sig = (src, dst)
                if sig not in seen:
                    seen.add(sig)
                    calls.append({'src': src, 'dst': dst, 'file': c.source, 'line': line, 'dispatch': disp,
                                  'via': [short_key(v) for v in via]})
                continue
            if t in visited or len(via) > 6 or t[0] not in classes or (t[1], t[2]) not in classes[t[0]].methods:
                continue
            visited.add(t)
            for t2, _l2, d2, crt2 in raw_calls(classes[t[0]], t[1], t[2], crt):
                stack.append((t2, line, 'cha' if 'cha' in (disp, d2) else 'exact', crt2, via + [t]))

    # impl map: for each concrete class, which node runs for each method name it inherits or declares
    impl = {}
    for c in classes:
        if not is_concrete(c):
            continue
        tbl = {}
        for anc in [c] + all_supers(c):
            if anc not in classes:
                continue
            for (mn, md) in classes[anc].methods:
                if mn in ('<clinit>',) or (mn == '<init>' and anc != c):
                    continue
                d = declared_up(c, mn, md)
                if d and has_body(d, mn, md):
                    n = node(d, mn, md, c)
                    if n:
                        tbl.setdefault(mn, {})[md] = n
        impl[c.rsplit('/', 1)[-1]] = tbl

    lam_out = []
    for src, impl_m, line, srcfile in lambdas:
        if src in uname and impl_m in uname:
            lam_out.append({'src': uname[src], 'dst': uname[impl_m], 'file': srcfile, 'line': line})
    fw_out = {uname[k]: sorted(v) for k, v in fw.items() if k in uname}
    variants = sorted({node(d, mn, md, rt) for (d, mn, md, rt) in needs if node(d, mn, md, rt)})
    out = {'calls': calls, 'lambdas': lam_out, 'framework_calls': fw_out, 'receiver_variants': variants, 'impl': impl}
    with open(os.path.join(gdir, 'auto_calls.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('classes %d | universe methods %d | call edges %d (exact %d, cha-only %d, via skipped code %d) | '
          'receiver variants %d | lambda creations %d'
          % (len(classes), len(names), len(calls), sum(1 for x in calls if x['dispatch'] == 'exact'),
             sum(1 for x in calls if x['dispatch'] == 'cha'), sum(1 for x in calls if x['via']), len(variants), len(lam_out)))


if __name__ == '__main__':
    main(sys.argv)
