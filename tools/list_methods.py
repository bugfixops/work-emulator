"""List every method with a body in a directory of .class files (a javap -p substitute).

Usage: python3 -I list_methods.py <classes_dir> [<classes_dir> ...] [--exclude SUBSTRING ...] [--json OUT]
                                   [--jacoco report.xml]

--jacoco keeps only methods that the JaCoCo report lists, plus private no-arg constructors (JaCoCo
filters the empty ones), so the universe matches the coverage data (drops @Generated code such as
Dagger, enum values/valueOf, synthetic switch maps). Dropped methods are listed on stderr.

Drops: abstract/native methods, synthetic or bridge methods (access$NNN, bridges),
and synthetic inner-class constructors. Keeps lambdas (lambda$m$0), constructors,
static initialisers and inner/anonymous class methods.
Prints one line per method: Class.method<TAB>descriptor<TAB>flags.
"""
import json
import os
import struct
import sys

ACC_STATIC, ACC_BRIDGE, ACC_NATIVE = 0x0008, 0x0040, 0x0100
ACC_ABSTRACT, ACC_SYNTHETIC = 0x0400, 0x1000


def parse_class(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('not a class file: ' + path)
    pos = 10
    (count,) = struct.unpack_from('>H', data, 8)
    pool = [None] * count
    i = 1
    while i < count:
        tag = data[pos]
        pos += 1
        if tag == 1:  # Utf8
            (n,) = struct.unpack_from('>H', data, pos)
            pool[i] = data[pos + 2:pos + 2 + n].decode('utf-8', 'replace')
            pos += 2 + n
        elif tag in (3, 4):
            pos += 4
        elif tag in (5, 6):  # long/double take two slots
            pos += 8
            i += 1
        elif tag == 7:  # Class
            pool[i] = ('class', struct.unpack_from('>H', data, pos)[0])
            pos += 2
        elif tag in (8, 16, 19, 20):
            pos += 2
        elif tag in (9, 10, 11, 12, 17, 18):
            pos += 4
        elif tag == 15:
            pos += 3
        else:
            raise ValueError('bad constant tag %d in %s' % (tag, path))
        i += 1
    _access, this_idx = struct.unpack_from('>HH', data, pos)
    pos += 6
    (n_ifaces,) = struct.unpack_from('>H', data, pos)
    pos += 2 + 2 * n_ifaces

    def skip_members(p):
        (n,) = struct.unpack_from('>H', data, p)
        p += 2
        out = []
        for _ in range(n):
            acc, name_i, desc_i, n_attr = struct.unpack_from('>HHHH', data, p)
            p += 8
            for _ in range(n_attr):
                (alen,) = struct.unpack_from('>I', data, p + 2)
                p += 6 + alen
            out.append((acc, pool[name_i], pool[desc_i]))
        return p, out

    pos, _fields = skip_members(pos)
    pos, methods = skip_members(pos)
    cls = pool[pool[this_idx][1]]
    return cls, methods


def short_name(internal):
    return internal.rsplit('/', 1)[-1]


def main(argv):
    roots, excludes, out_json, jacoco = [], [], None, None
    rest = argv[1:]
    while rest:
        a = rest.pop(0)
        if a == '--exclude':
            excludes.append(rest.pop(0))
        elif a == '--json':
            out_json = rest.pop(0)
        elif a == '--jacoco':
            jacoco = rest.pop(0)
        else:
            roots.append(a)
    rows = []
    for root in roots:
      for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.endswith('.class'):
                continue
            path = os.path.join(dirpath, fn)
            if any(x in path for x in excludes):
                continue
            cls, methods = parse_class(path)
            if any(x in cls for x in excludes):
                continue
            for acc, name, desc in methods:
                if acc & (ACC_ABSTRACT | ACC_NATIVE):
                    continue
                if acc & ACC_BRIDGE or name.startswith('access$'):
                    continue
                if acc & ACC_SYNTHETIC and not name.startswith('lambda$'):
                    continue
                flags = []
                if acc & ACC_STATIC:
                    flags.append('static')
                if acc & ACC_SYNTHETIC:
                    flags.append('synthetic')
                if acc & 0x0002:
                    flags.append('private')
                rows.append({'class': cls, 'short': short_name(cls) + '.' + name,
                             'name': name, 'desc': desc, 'flags': flags})
    if jacoco:
        import xml.etree.ElementTree as ET
        rep, rep_classes = set(), set()
        for c in ET.parse(jacoco).getroot().iter('class'):
            rep_classes.add(c.get('name'))
            for m in c.findall('method'):
                rep.add((c.get('name'), m.get('name'), m.get('desc')))
        keep, dropped = [], []
        for r in rows:
            k = (r['class'], r['name'], r['desc'])
            if k in rep or (r['name'] == '<init>' and r['desc'] == '()V' and 'private' in r['flags']
                            and r['class'] in rep_classes):
                keep.append(r)
            else:
                dropped.append(r)
        print('# --jacoco: kept %d, dropped %d not in the report' % (len(keep), len(dropped)), file=sys.stderr)
        for r in dropped:
            print('#   dropped %s%s' % (r['short'], r['desc']), file=sys.stderr)
        rows = keep
    rows.sort(key=lambda r: (r['class'], r['name'], r['desc']))
    for r in rows:
        print('%s\t%s\t%s' % (r['short'], r['desc'], ','.join(r['flags'])))
    print('# %d methods' % len(rows), file=sys.stderr)
    if out_json:
        with open(out_json, 'w') as f:
            json.dump(rows, f, indent=1)


if __name__ == '__main__':
    main(sys.argv)
