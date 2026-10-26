"""Compare the verdicts of two trigger graphs of the same app (hand-written vs generated).

Usage: python3 -I compare_graphs.py <hand.json> <gen.json> [--list N]
Prints a confusion table of verdicts and the first N methods of each disagreement class.
"""
import collections
import json
import sys


def main(argv):
    a = json.load(open(argv[1]))
    b = json.load(open(argv[2]))
    n = int(argv[argv.index('--list') + 1]) if '--list' in argv else 12
    va, vb = a['verdict'], b['verdict']
    common = [m for m in va if m in vb]
    tab = collections.Counter((va[m], vb[m]) for m in common)
    kinds = sorted({k for p in tab for k in p})
    print('methods in both: %d (hand %d, generated %d)' % (len(common), len(va), len(vb)))
    print('%-24s' % 'hand \\ generated' + ''.join('%-24s' % k for k in kinds))
    for ka in kinds:
        print('%-24s' % ka + ''.join('%-24d' % tab.get((ka, kb), 0) for kb in kinds))
    agree = sum(v for (x, y), v in tab.items() if x == y)
    print('exact agreement: %.1f%%' % (100.0 * agree / len(common)))
    dead = lambda v: v in ('DEAD', 'FRAMEWORK_ONLY')
    both_alive = sum(v for (x, y), v in tab.items() if not dead(x) and not dead(y))
    print('agreement on dead-vs-alive: %.1f%%' % (100.0 * sum(v for (x, y), v in tab.items() if dead(x) == dead(y)) / len(common)))
    groups = collections.defaultdict(list)
    for m in common:
        if va[m] != vb[m]:
            groups[(va[m], vb[m])].append(m)
    for (x, y), ms in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print('\n%s -> %s: %d' % (x, y, len(ms)))
        for m in ms[:n]:
            print('   ', m)


main(sys.argv)
