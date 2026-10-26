"""List, for every UNREACHABLE method of a schema 2 build, where it is declared and where its name is still used in the app sources.

Usage (from work/): python3 -I tools/scan_unreachable.py <App> [--all] [--refs] [--callers]
Reads graphs/<App>/out/*_trigger_graph.json. Searches the .java and .xml files of final_java_only/<App>/app/*/ (generated and build folders skipped).
For a method: the name (a constructor is searched as `new Class(` / `Class(`), the declaring file and line (printed as the reference), and every other line
that mentions the name, comments skipped. Methods with no other mention are printed in one line at the end ("no other mention"): those are the
no-caller cases; the others are listed with up to 4 hits so a person can decide if the hit is a real caller (a call, an XML android:onClick,
a reflection string) or only another method of the same name. --refs prints a python dict {method: 'File.java:line'} for use as source_ref.
--callers instead prints the UNREACHABLE methods that still have a bytecode call edge from a method outside the unreachable set (the callers a SUPPRESS may have hidden); each one must be explained in its reason.
It is a triage tool: a hit is not proof of a caller, and no hit does not rule out reflection by a string built at run time.
"""
import glob
import json
import os
import re
import sys

SRC_ROOT = 'final_java_only'


def sources(app):
    out = {}
    for root in glob.glob('%s/%s/app/*/' % (SRC_ROOT, app)):
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in ('build', 'androidTest', 'test', '.git', 'JacocoInstrument')]
            for f in fn:
                if f.endswith(('.java', '.xml', '.kt')):
                    p = os.path.join(dp, f)
                    try:
                        out[p] = open(p, encoding='utf-8', errors='replace').read().split('\n')
                    except OSError:
                        pass
    return out


def simple(m):
    base = m.split('@')[0]
    cls, _, meth = base.rpartition('.')
    meth = meth.split('(')[0]
    outer = cls.split('$')[0]
    return cls, outer, meth


def is_comment(line):
    s = line.strip()
    return s.startswith(('//', '*', '/*', '<!--'))


def main(argv):
    app = argv[1]
    if '--callers' in argv:
        g = json.load(open(glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]))
        unre = {m for m, l in g['labels'].items() if l.get('unreachable')}
        if not os.path.exists('graphs/%s/auto_calls.json' % app):
            print('graphs/%s/auto_calls.json does not exist: no bytecode edges to compare' % app)
            return
        auto = json.load(open('graphs/%s/auto_calls.json' % app))
        live = {}
        for c in auto['calls']:
            if c['dst'] in unre and c['src'] not in unre:
                live.setdefault(c['dst'], []).append('%s (%s:%s)' % (c['src'], c['file'], c['line']))
        for m in sorted(live):
            print('%s [%s] <- %s' % (m, g['labels'][m]['unreachable']['kind'], '; '.join(live[m][:3])))
        print('%d of %d unreachable methods have a bytecode caller outside the set' % (len(live), len(unre)))
        return
    g = json.load(open(glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]))
    files = sources(app)
    by_name = {}
    for p in files:
        by_name.setdefault(os.path.basename(p), []).append(p)
    refs, quiet, shown = {}, [], 0
    for m, l in sorted(g['labels'].items()):
        u = l.get('unreachable')
        if not u:
            continue
        cls, outer, meth = simple(m)
        inner = cls.split('$')[-1]
        ctor = meth == '<init>'
        name = inner if ctor else meth
        if meth == '<clinit>':
            name = inner
        decl_files = by_name.get(outer + '.java', []) + by_name.get(outer + '.kt', [])
        rx = re.compile(r'\bnew\s+%s\s*\(|\b%s\s*\(' % (re.escape(inner), re.escape(inner))) if ctor else re.compile(r'\b%s\b' % re.escape(name))
        decl = None
        hits = []
        for p, lines in files.items():
            for i, line in enumerate(lines, 1):
                if is_comment(line) or not rx.search(line):
                    continue
                is_decl = p in decl_files and decl is None and (
                    re.search(r'(public|private|protected|static|void|int|boolean|String|class)\b.*\b%s\b' % re.escape(name), line) and '(' in line and not re.search(r'\bnew\b|return |=\s*[\w.]*%s\(' % re.escape(name), line)) if not ctor else None
                if ctor and p in decl_files and decl is None and re.search(r'\b(class|enum)\s+%s\b|\b%s\s*\([^)]*\)\s*(throws [\w, ]+)?\s*\{' % (re.escape(inner), re.escape(inner)), line):
                    is_decl = True
                if is_decl:
                    decl = '%s:%d' % (os.path.basename(p), i)
                    continue
                hits.append('%s:%d %s' % (os.path.relpath(p, '%s/%s/app' % (SRC_ROOT, app)).split('/src/')[-1] if '--full' in argv else os.path.basename(p), i, line.strip()[:70]))
        refs[m] = decl or (decl_files and os.path.basename(decl_files[0]) or '?')
        if not hits and '--all' not in argv:
            quiet.append(m)
            continue
        shown += 1
        print('%s [%s] %s: %s' % (m, u['kind'], refs[m], 'no other mention' if not hits else '%d other mentions' % len(hits)))
        for h in hits[:4]:
            print('      ' + h)
    print('\n%d methods with other mentions shown; %d with no other mention: %s' % (shown, len(quiet), ', '.join(quiet)[:3000]))
    if '--refs' in argv:
        print('REFS = {')
        for m, r in sorted(refs.items()):
            print('    %r: %r,' % (m, r))
        print('}')


if __name__ == '__main__':
    main(sys.argv)
