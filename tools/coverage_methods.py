"""Per-method JaCoCo hit status for an app's APE and Monkey runs.

Usage: python3 -I coverage_methods.py <app_dir> [--json OUT] [--grep SUBSTRING]
Prints Class.method(desc) with M (Monkey) / A (APE) hit flags.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET


def load(path):
    res = {}
    for cls in ET.parse(path).getroot().iter('class'):
        cn = cls.get('name')
        if 'JacocoInstrument' in cn:
            continue
        for m in cls.findall('method'):
            c = {x.get('type'): int(x.get('covered')) for x in m.findall('counter')}
            res[(cn, m.get('name'), m.get('desc'))] = c.get('METHOD', 0) > 0
    return res


def main(argv):
    app = argv[1]
    out_json = argv[argv.index('--json') + 1] if '--json' in argv else None
    pat = argv[argv.index('--grep') + 1] if '--grep' in argv else ''
    mk = load(os.path.join(app, 'monkey/report/report.xml'))
    ap = load(os.path.join(app, 'ape/report/report.xml'))
    rows = []
    for k in sorted(set(mk) | set(ap)):
        cn, name, desc = k
        rows.append({'class': cn, 'short': cn.rsplit('/', 1)[-1] + '.' + name, 'desc': desc,
                     'monkey': bool(mk.get(k)), 'ape': bool(ap.get(k))})
    for r in rows:
        if pat in r['short']:
            print('%s %s  %s%s' % ('M' if r['monkey'] else '-', 'A' if r['ape'] else '-', r['short'], r['desc']))
    if out_json:
        with open(out_json, 'w') as f:
            json.dump(rows, f, indent=1)


if __name__ == '__main__':
    main(sys.argv)
