"""Combine the per-app artifacts of one workflow run into one folder with a summary table (stdlib only).

Usage: python3 -I ci/collect.py <downloaded_dir> <out_dir> <expected apps, comma separated>
<downloaded_dir>/results-<App>/ holds what ci/run_app.sh wrote; apps that left nothing are listed as no_artifact.
Writes <out_dir>/<App>/..., SUMMARY.md and summary.csv.
"""
import csv
import json
import os
import shutil
import sys

MAX_FILE = 40 * 1024 * 1024
COLS = ['app', 'status', 'tool', 'minutes', 'segments_valid', 'segments_total', 'methods_hit', 'methods_total', 'events_injected',
        'crashes', 'anrs', 'tool_exit', 'app_alive_at_end']


def main():
    src, dst = sys.argv[1], sys.argv[2]
    expected = [a for a in (sys.argv[3] if len(sys.argv) > 3 else '').split(',') if a]
    os.makedirs(dst, exist_ok=True)
    seen = set()
    rows = []
    if os.path.isdir(src):
        for name in sorted(os.listdir(src)):
            folder = os.path.join(src, name)
            if not (name.startswith('results-') and os.path.isdir(folder)):
                continue
            app = name[len('results-'):]
            seen.add(app)
            shutil.copytree(folder, os.path.join(dst, app), dirs_exist_ok=True)
            for root, _, files in os.walk(os.path.join(dst, app)):
                for f in files:
                    path = os.path.join(root, f)
                    if os.path.getsize(path) > MAX_FILE:
                        os.remove(path)
            try:
                with open(os.path.join(folder, 'meta.json'), encoding='utf-8') as f:
                    meta = json.load(f)
            except (OSError, ValueError):
                meta = {'status': 'no_meta'}
            meta['app'] = app
            rows.append(meta)
    for app in expected:
        if app not in seen:
            rows.append({'app': app, 'status': 'no_artifact'})
    rows.sort(key=lambda r: r['app'].lower())
    with open(os.path.join(dst, 'summary.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in rows:
            w.writerow([r.get(c, '') for c in COLS])
    lines = ['# Run %s' % os.environ.get('GITHUB_RUN_ID', ''), '',
             '| App | Status | Tool | Min | Segments ok/all | Methods hit/all | Events | Crashes | ANRs |', '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append('| %s | %s | %s | %s | %s/%s | %s/%s | %s | %s | %s |' % (
            r['app'], r.get('status', ''), r.get('tool', ''), r.get('minutes', ''), r.get('segments_valid', ''), r.get('segments_total', ''),
            r.get('methods_hit', ''), r.get('methods_total', ''), r.get('events_injected', ''), r.get('crashes', ''), r.get('anrs', '')))
    text = '\n'.join(lines) + '\n'
    with open(os.path.join(dst, 'SUMMARY.md'), 'w', encoding='utf-8') as f:
        f.write(text)
    sys.stdout.write(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write(text)


if __name__ == '__main__':
    main()
