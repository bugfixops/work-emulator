"""Small, diff-friendly summaries of one app run (stdlib only).

Usage: python3 -I ci/report.py <outdir> key=value [key=value ...]
Reads  report.xml (JaCoCo XML), segments.csv and tool.log in <outdir>, whichever exist.
Writes methods_hit.csv (class,method,desc,hit with JaCoCo's class names, instrumentation classes left out) and meta.json.
"""
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET


def main():
    out = sys.argv[1]
    meta = dict(a.split('=', 1) for a in sys.argv[2:] if '=' in a)
    rows = []
    xml_path = os.path.join(out, 'report.xml')
    if os.path.exists(xml_path):
        for cls in ET.parse(xml_path).getroot().iter('class'):
            name = cls.get('name')
            if 'JacocoInstrument' in name:
                continue
            for m in cls.findall('method'):
                counters = {c.get('type'): int(c.get('covered')) for c in m.findall('counter')}
                rows.append((name, m.get('name'), m.get('desc'), 1 if counters.get('METHOD', 0) > 0 else 0))
        rows.sort()
        with open(os.path.join(out, 'methods_hit.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['class', 'method', 'desc', 'hit'])
            w.writerows(rows)
    meta['methods_total'] = len(rows)
    meta['methods_hit'] = sum(r[3] for r in rows)
    seg = os.path.join(out, 'segments.csv')
    if os.path.exists(seg):
        parts = [line.split(',', 4) for line in open(seg, encoding='utf-8') if line.strip()]
        meta['segments_total'] = len(parts)
        meta['segments_valid'] = sum(1 for p in parts if len(p) > 3 and p[3] == 'true')
    log = os.path.join(out, 'tool.log')
    if os.path.exists(log):
        text = open(log, encoding='utf-8', errors='replace').read()
        events = re.findall(r'Events injected: (\d+)', text)
        meta['events_injected'] = int(events[-1]) if events else None
        # Monkey prints no summary when `timeout` stops it; every event is followed by one throttle sleep line
        meta['events_estimated'] = len(re.findall(r'^Sleeping for \d+ milliseconds', text, re.M))
        meta['crashes'] = text.count('// CRASH:')
        meta['anrs'] = text.count('// NOT RESPONDING:')
    with open(os.path.join(out, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=1, sort_keys=True)
        f.write('\n')


if __name__ == '__main__':
    main()
