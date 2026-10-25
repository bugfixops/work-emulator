"""Decide what one workflow run does and publish it as step outputs.

Manual runs ("Run workflow") pass their options in IN_* variables; a push of ci/run.conf is read from the file.
Outputs: matrix (JSON for the job matrix), count, minutes, seed, tool.
"""
import csv
import json
import os
import sys


def read_conf(path):
    conf = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()
            if '=' in line:
                key, value = line.split('=', 1)
                conf[key.strip().upper()] = value.strip()
    return conf


def fail(msg):
    print('::error title=plan::%s' % msg)
    sys.exit(1)


def main():
    if os.environ.get('EVENT') == 'workflow_dispatch':
        conf = {'APPS': os.environ.get('IN_APPS', ''), 'MINUTES': os.environ.get('IN_MINUTES', ''),
                'TOOL': os.environ.get('IN_TOOL', ''), 'SEED': os.environ.get('IN_SEED', '')}
    else:
        conf = read_conf('ci/run.conf')
    known = [r['app'] for r in csv.DictReader(open('ci/apps.csv', encoding='utf-8'))]
    apps = (conf.get('APPS') or 'all').strip()
    want = known if apps.lower() == 'all' else [a.strip() for a in apps.split(',') if a.strip()]
    unknown = [a for a in want if a not in known]
    if unknown:
        fail('unknown app(s) %s; known: %s' % (', '.join(unknown), ', '.join(known)))
    tool = (conf.get('TOOL') or 'monkey').strip().lower()
    if tool not in ('monkey', 'ape'):
        fail('TOOL must be monkey or ape, got %r' % tool)
    if tool == 'ape' and not os.path.exists('ci/ape.jar'):
        fail('TOOL=ape needs ci/ape.jar (build it from the APE sources and commit it); it is not in this repo')
    try:
        minutes = int(conf.get('MINUTES') or 60)
        seed = int(conf.get('SEED') or 20261016)
    except ValueError:
        fail('MINUTES and SEED must be integers')
    if not 1 <= minutes <= 300:
        fail('MINUTES must be between 1 and 300 (a hosted job is limited to 6 hours)')
    out = {'matrix': json.dumps({'app': want}), 'apps': ','.join(want), 'count': str(len(want)), 'minutes': str(minutes),
           'seed': str(seed), 'tool': tool}
    text = ''.join('%s=%s\n' % kv for kv in out.items())
    sys.stdout.write(text)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write('**Plan:** %s for %d min each (seed %d) on %d app(s): %s\n' % (tool, minutes, seed, len(want), ', '.join(want)))


if __name__ == '__main__':
    main()
