"""Check that every framework citation (FW-SRC) of a schema 2 graph points at a source file we hold, at lines inside that file.

Usage (from work/): python3 -I tools/check_citations.py <App> [--show]
Reads the evidence of every edge and the UNREACHABLE reasons in graphs/<App>/out/*_trigger_graph.json. Two citation styles exist:
  core/java/android/app/Activity.java:3001-3010, 3386-3388      path from the Android source root (Diary style)
  android-8.1.0_r1:app/Activity.java:3001-3010                  path tail after the version tag (Currency style)
Files are looked up in work/fw_src/android-8.1.0_r1/ and graphs/<App>/.plan/fw_src/android-8.1.0_r1/ (the tails are matched).
Library citations (lib ..., MPAndroidChart-...) are counted but not checked. It also counts the evidence claims that no source backs
(FW-MEMORY, DYN, UNVERIFIED), which a converted graph must not have. --show prints the first cited line of every distinct citation, to be read.
It checks that the file exists and the lines exist; that a line says what the edge claims is for a person to read.
Exit status 1 when a file is missing or a line is out of range.
"""
import glob
import json
import os
import re
import sys

LINES = r'\d+(?:-\d+)?(?:\s*,\s*\d+(?:-\d+)?)*'
ROOT_STYLE = re.compile(r'((?:core|services|data|libcore|packages)/[\w./\-]+\.(?:java|xml)):(' + LINES + ')')
TAG_STYLE = re.compile(r'android-8\.1\.0_r1:([\w./\-]+\.(?:java|xml)):(' + LINES + ')')
LIB_STYLE = re.compile(r'FW-SRC lib |MPAndroidChart-v[\d.]+:')
UNBACKED = re.compile(r'(?:^|;\s*)(FW-MEMORY|DYN|UNVERIFIED)\b')


def caches(app):
    out = []
    for c in ('fw_src/android-8.1.0_r1', 'graphs/%s/.plan/fw_src/android-8.1.0_r1' % app):
        if os.path.isdir(c):
            out.append(c)
    return out


def files_in(cache):
    res = {}
    for dp, _, fn in os.walk(cache):
        for f in fn:
            full = os.path.join(dp, f)
            res[os.path.relpath(full, cache)] = full
    return res


def resolve(path, style, index):
    if style == 'root':
        for cache, files in index:
            if path in files:
                return files[path]
        return None
    for cache, files in index:
        for rel, full in files.items():
            if rel == path or rel.endswith('/' + path):
                return full
    return None


def line_ranges(spec):
    for part in spec.split(','):
        a, _, b = part.strip().partition('-')
        yield int(a), int(b or a)


def main(argv):
    app = argv[1]
    g = json.load(open(glob.glob('graphs/%s/out/*_trigger_graph.json' % app)[0]))
    index = [(c, files_in(c)) for c in caches(app)]
    texts = [(x['id'], x['evidence'] or '') for x in g['edges']]
    texts += [(m, l['unreachable']['text']) for m, l in g['labels'].items() if l.get('unreachable')]
    seen, problems, libs, unbacked = {}, [], 0, []
    line_cache = {}
    for owner, ev in texts:
        if LIB_STYLE.search(ev):
            libs += 1
        if UNBACKED.search(ev):
            unbacked.append(owner)
        for style, rx in (('root', ROOT_STYLE), ('tag', TAG_STYLE)):
            for m in rx.finditer(ev):
                path, spec = m.group(1), re.sub(r'\s+', '', m.group(2))
                key = (path, spec)
                if key in seen:
                    continue
                full = resolve(path, style, index)
                if not full:
                    seen[key] = None
                    problems.append('%s: file not held: %s' % (owner, path))
                    continue
                if full not in line_cache:
                    line_cache[full] = open(full, encoding='utf-8', errors='replace').read().split('\n')
                lines = line_cache[full]
                bad = [r for r in line_ranges(spec) if not 1 <= r[0] <= r[1] <= len(lines)]
                seen[key] = (full, lines, spec)
                if bad:
                    problems.append('%s: %s has %d lines, cited %s' % (owner, path, len(lines), spec))
    print('citations: %d distinct, %d problems; library citations (not checked): %d; evidence with FW-MEMORY / DYN / UNVERIFIED: %d' % (
        len(seen), len(problems), libs, len(unbacked)))
    for p in problems[:40]:
        print('  PROBLEM ' + p)
    if unbacked:
        print('  unbacked evidence on: ' + ', '.join(unbacked[:12]) + (' ...' if len(unbacked) > 12 else ''))
    if '--show' in argv:
        for (path, spec), val in sorted(seen.items()):
            if val:
                first = next(iter(line_ranges(spec)))[0]
                print('%s:%s\n      %s' % (path, spec, val[1][first - 1].strip()[:150]))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
