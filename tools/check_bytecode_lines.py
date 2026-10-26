"""Check that the source line cited by an edge that came from the bytecode scan really contains the call.

Usage (from work/): python3 -I tools/check_bytecode_lines.py <App> [--all] [--emit]
For every edge whose evidence has `SRC File.java:N (bytecode)` it looks for the callee's simple name (method name, or the class name for a
constructor) on line N of the source (flavor-aware, same lookup as show_route.py). The name is searched on the cited line first, then up to
2 lines before and after (javac gives a `new X(...)` that sits inside a chained call the line of the previous call, so the line can be off by one).
For a constructor that is nowhere near, it looks up to 30 lines back for `new Name(` (the start of a multi-line expression).
Listed: the edges whose cited line does not show the callee, with the correct line when one was found.
Skipped and counted: lambdas, <clinit>, anonymous classes, implicit constructor calls (a constructor or static initializer calling another
constructor: super(), this(), enum constants) and the Dagger-generated injector calls (*HelperModule.xxxHelper).
--emit also prints a FIX_LINES literal (edge -> corrected line text) that can be pasted into the EDIT hook of graph_def.py.
Exit status 1 when anything is listed.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import show_route  # noqa: E402

IMPLICIT = 'IMPLICIT'


def callee_token(dst, src=''):
    d = dst.split('@')[0]
    s_ = src.split('@')[0].rpartition('.')[2]
    if '.<init>' in d and s_.startswith(('<init>', '<clinit>')):
        return IMPLICIT                                   # super() / this() / enum constant
    if re.match(r'.*HelperModule\.\w+Helper$', d):
        return IMPLICIT                                   # Dagger-generated injector
    if re.match(r'Dagger\w+\$Builder\.<init>', d):
        return 'builder'
    cls, _, meth = d.rpartition('.')
    if meth.startswith('<clinit>') or 'lambda$' in meth or meth.startswith('access$'):
        return None
    if meth.startswith('<init>'):
        simple = re.sub(r'^\d+', '', cls.split('$')[-1])      # a local class is named Outer$1Name
        return None if not simple else simple
    meth = meth.split('(')[0]
    return meth or None


def main(argv):
    app = argv[1]
    g = json.load(open(glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]))
    flavors = show_route.built_flavors(app)
    idx = show_route.source_index(app)
    cache, bad, checked, skipped, implicit, fixes = {}, [], 0, 0, 0, {}
    for x in g['edges']:
        for m in re.finditer(r'SRC\s+([\w./$-]+\.java):(\d+)\s*\(bytecode\)', x['evidence'] or ''):
            fname, n = m.group(1), int(m.group(2))
            tok = callee_token(x['dst'], x['src'])
            if tok == IMPLICIT:
                implicit += 1
                continue
            if not tok:
                skipped += 1
                continue
            path = show_route.find(idx, fname, flavors)
            if not path:
                bad.append((x['id'], x['src'], x['dst'], fname, n, 'file not found'))
                continue
            if path not in cache:
                cache[path] = open(path, encoding='utf-8', errors='replace').read().split('\n')
            lines = cache[path]
            checked += 1
            rx = re.compile(r'\b%s\b' % re.escape(tok))
            if 1 <= n <= len(lines) and rx.search(lines[n - 1]):
                continue
            near = [k for k in (n - 1, n + 1, n - 2, n + 2) if 1 <= k <= len(lines) and rx.search(lines[k - 1])]
            start = None
            if not near and '<init>' in x['dst']:
                nrx = re.compile(r'\bnew\s+%s\s*\(' % re.escape(tok))
                for k in range(n - 1, max(0, n - 31), -1):
                    if nrx.search(lines[k - 1]):
                        start = k
                        break
            if near:
                what, new = 'name on line %d' % near[0], '%d' % near[0]
            elif start:
                what, new = 'new %s( starts on line %d' % (tok, start), '%d-%d' % (start, n)
            else:
                what, new = 'name not within 2 lines', None
            bad.append((x['id'], x['src'], x['dst'], fname, n, what))
            if new:
                fixes[(x['src'], x['dst'], 'SRC %s:%d (bytecode)' % (fname, n))] = 'SRC %s:%s (bytecode line was %d)' % (fname, new, n)
    print('%s: %d bytecode-cited edges checked, %d skipped (lambda / clinit / anonymous), %d implicit (super / enum / Dagger), '
          '%d where the cited line does not show the callee' % (app, checked, skipped, implicit, len(bad)))
    for b in bad[:(len(bad) if '--all' in argv else 60)]:
        print('  %s %s -> %s  cited %s:%d  (%s)' % b)
    if '--emit' in argv:
        print('FIX_LINES = {')
        for k, v in sorted(fixes.items()):
            print('    %r: %r,' % (k, v))
        print('}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
