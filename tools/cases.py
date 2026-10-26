"""Source helpers for graph_def.py of hand-written graphs: split a big switch / if-chain method into its branches, find who sends a Handler message.

    import sys; sys.path.insert(0, TOOLS); import cases
    CS = cases.Cases('Vanilla-Music')                       # indexes the app sources once (flavor aware, like show_route.py)
    CS.branches('LibraryActivity.java', 'onFancyItemSelected')
        -> [('CTX_MENU_EXPAND', 746, 752), ('CTX_MENU_ENQUEUE', 753, 755), ...]   labels of the first switch (case X: / default:) or of the
           first if / else-if chain of the method body, with the first and last source line of each branch (fall-through labels share a range)
    CS.method_lines('LibraryActivity.java', 'onFancyItemSelected')  -> (first_line, last_line) of the method (declaration to closing brace)
    CS.enclosing('LibraryActivity.java', 775)                -> 'onFancyItemSelected' (name of the method that contains the line, or None)
    CS.uses(r'\\bMSG_DELETE\\b')                              -> [(file, line, method)] every use in the app sources (comments / strings skipped)
    CS.calls_in(src_node, a, b, AUTO)                        -> the bytecode call edges of src_node whose line is in [a, b]

The parser blanks comments, strings and char literals, then matches braces; it understands `switch (x) { case A: case B: ... default: ... }`,
`case A: { ... }` and `if (c) {...} else if (c) {...} else {...}` (also braceless single statements). It does not understand a switch inside a
lambda body or a ternary chain; for those the caller gets an empty list and writes the branches by hand.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import show_route  # noqa: E402


def blank(text):
    """Replace comments, string and char literals by spaces (newlines kept) so braces and keywords can be searched."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        two = text[i:i + 2]
        if two == '//':
            j = text.find('\n', i)
            j = n if j < 0 else j
            out.append(' ' * (j - i)); i = j
        elif two == '/*':
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r'[^\n]', ' ', text[i:j])); i = j
        elif c in '"\'':
            q, j = c, i + 1
            while j < n and text[j] != q:
                j += 2 if text[j] == '\\' else 1
            j = min(j + 1, n)
            out.append(re.sub(r'[^\n]', ' ', text[i:j])); i = j
        else:
            out.append(c); i += 1
    return ''.join(out)


class Cases:
    def __init__(self, app):
        self.app = app
        self.idx = show_route.source_index(app)
        self.fl = show_route.built_flavors(app)
        self._src = {}

    def _load(self, fname):
        p = show_route.find(self.idx, fname, self.fl)
        if not p:
            raise KeyError(fname)
        if p not in self._src:
            raw = open(p, encoding='utf-8', errors='replace').read()
            self._src[p] = (raw.split('\n'), blank(raw))
        return self._src[p]

    # ---- positions
    @staticmethod
    def _offsets(text):
        starts, pos = [0], 0
        for line in text.split('\n'):
            pos += len(line) + 1
            starts.append(pos)
        return starts

    @staticmethod
    def _line_of(starts, off):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= off:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    @staticmethod
    def _match(text, i, op='{', cl='}'):
        depth = 0
        for j in range(i, len(text)):
            if text[j] == op:
                depth += 1
            elif text[j] == cl:
                depth -= 1
                if depth == 0:
                    return j
        return -1

    def method_lines(self, fname, name, nth=0, params=None, any_depth=False):
        """(first_line, last_line) of the nth declaration of `name` whose parameter list matches the regex `params` (default any); declarations
        nested deeper than the shallowest one (methods of inner / anonymous classes) are skipped unless any_depth."""
        lines, text = self._load(fname)
        starts = self._offsets(text)
        pat = re.compile(r'(?:(?:public|private|protected|static|final|synchronized|abstract|native)\s+)*[\w<>\[\],.? ]+\s+%s\s*\(([^)]*)\)\s*(?:throws[\w\s,.]+)?\{' % re.escape(name))
        pat2 = re.compile(r'\b%s\s*\(([^)]*)\)\s*(?:throws[\w\s,.]+)?\{' % re.escape(name))   # constructors
        hits = []
        for m in list(pat.finditer(text)) + [m for m in pat2.finditer(text) if m.start() not in {x.start() for x in pat.finditer(text)}]:
            head = text[max(0, m.start() - 40):m.start()]
            if re.search(r'\b(new|return|else)\s*$', head) or re.search(r'[=.]\s*$', head):
                continue
            if params is not None and not re.search(params, m.group(1)):
                continue
            hits.append(m)
        hits.sort(key=lambda m: m.start())
        if not any_depth and hits:
            def depth_at(off):
                d = 0
                for ch in text[:off]:
                    if ch == '{':
                        d += 1
                    elif ch == '}':
                        d -= 1
                return d
            ds = [depth_at(m.start()) for m in hits]
            lo = min(ds)
            hits = [m for m, d in zip(hits, ds) if d == lo]
        if nth >= len(hits):
            raise KeyError('%s.%s #%d' % (fname, name, nth))
        m = hits[nth]
        ob = m.end() - 1
        cb = self._match(text, ob)
        return self._line_of(starts, m.start()), self._line_of(starts, cb)

    def enclosing(self, fname, line):
        lines, text = self._load(fname)
        starts = self._offsets(text)
        best = None
        for m in re.finditer(r'\b([A-Za-z_]\w*)\s*\(([^;{}]*)\)\s*(?:throws[\w\s,.]+)?\{', text):
            if m.group(1) in ('if', 'for', 'while', 'switch', 'catch', 'synchronized', 'return', 'new', 'else'):
                continue
            ob = m.end() - 1
            cb = self._match(text, ob)
            a, b = self._line_of(starts, m.start()), self._line_of(starts, cb)
            if a <= line <= b and (best is None or a >= best[1]):
                best = (m.group(1), a)
        return best[0] if best else None

    def uses(self, regex):
        out = []
        rx = re.compile(regex)
        for fname, paths in sorted(self.idx.items()):
            if not fname.endswith('.java'):
                continue
            try:
                lines, text = self._load(fname)
            except KeyError:
                continue
            for i, ln in enumerate(text.split('\n'), 1):
                if rx.search(ln):
                    out.append((fname, i, self.enclosing(fname, i)))
        return out

    def calls_in(self, src, a, b, AUTO):
        return [c for c in AUTO['calls'] if c['src'] == src and a <= c['line'] <= b]


    # ---- the conditions around a line
    def guard_of(self, fname, line, depth=3):
        """The source conditions that enclose `line`, outermost first, as a list of short strings: `cond` of an if, `not (cond)` of the matching else,
        `case X`, `for (...)` / `while (...)`, `catch (E)`, `finally`, `synchronized`. Lambdas and anonymous classes end the search (their body runs
        when the library calls it, not where it is written). Returns [] when the line is not inside any condition."""
        lines, text = self._load(fname)
        raw = '\n'.join(lines)
        starts = self._offsets(text)
        a, b = None, None
        try:
            name = self.enclosing(fname, line)
        except KeyError:
            return []
        # method body start: the nearest method declaration that contains the line
        best = None
        for m in re.finditer(r'\b([A-Za-z_]\w*)\s*\(([^;{}]*)\)\s*(?:throws[\w\s,.]+)?\{', text):
            if m.group(1) in ('if', 'for', 'while', 'switch', 'catch', 'synchronized', 'return', 'new', 'else'):
                continue
            ob = m.end() - 1
            cb = self._match(text, ob)
            la, lb = self._line_of(starts, m.start()), self._line_of(starts, cb)
            if la <= line <= lb and (best is None or la >= best[0]):
                best = (la, lb, ob)
        if not best:
            return []
        target = starts[line - 1] + len(lines[line - 1]) - len(lines[line - 1].lstrip())
        body = text[best[2]:target]
        stack = []                 # (header, kind, cond)
        closed = {}                # depth -> (kind, cond) of the last block closed at that depth
        last = best[2] + 1
        i = best[2]
        n = len(text)
        j = best[2] + 1
        seg_start = j
        depth = 0
        labels = {}                # depth -> last case label seen at that depth (switch body)
        def classify(header):
            h = re.sub(r'\s+', ' ', header).strip()
            m = re.search(r'(?:^|\})\s*else\s+if\s*\((.*)\)$', h)
            if m:
                return ('elseif', m.group(1))
            m = re.search(r'^(?:.*?[;{}:]\s*)?if\s*\((.*)\)$', h)
            if m:
                return ('if', m.group(1))
            if re.search(r'(?:^|\})\s*else$', h):
                return ('else', None)
            m = re.search(r'(for|while)\s*\((.*)\)$', h)
            if m:
                return (m.group(1), m.group(2))
            m = re.search(r'catch\s*\(([^)]*)\)$', h)
            if m:
                return ('catch', m.group(1))
            if re.search(r'(^|[;{}])\s*finally$', h):
                return ('finally', None)
            if re.search(r'synchronized\s*\(.*\)$', h):
                return ('sync', None)
            if re.search(r'switch\s*\(.*\)$', h):
                return ('switch', None)
            if re.search(r'->\s*$', h) or re.search(r'\bnew\s+[\w.<>]+\s*\([^)]*\)$', h) or re.search(r'\)\s*->$', h):
                return ('lambda', None)
            if re.search(r'(?:class|interface|enum)\s+\w+.*$', h):
                return ('lambda', None)
            return ('block', None)
        pos = best[2] + 1
        while pos < target:
            ch = text[pos]
            if ch == '{':
                header = text[seg_start:pos]
                kind, cond = classify(header)
                if kind in ('if', 'elseif', 'for', 'while', 'catch'):
                    rk, rc = classify(raw[seg_start:pos])
                    if rk == kind and rc:
                        cond = rc
                if kind == 'else':
                    prev = closed.get(len(stack))
                    cond = prev[1] if prev and prev[0] in ('if', 'elseif') else None
                    kind = 'else'
                stack.append((kind, cond))
                seg_start = pos + 1
            elif ch == '}':
                if stack:
                    k, c = stack.pop()
                    closed[len(stack)] = (k, c)
                    for d_ in [d for d in labels if d > len(stack)]:
                        del labels[d_]
                seg_start = pos + 1
            elif ch == ';':
                seg_start = pos + 1
            else:
                mm = re.match(r'(case\s+[^:;{}]+?|default)\s*:(?!:)', text[pos:pos + 200])
                if mm and (text[pos - 1].isspace() or text[pos - 1] in '{};') and stack and stack[-1][0] == 'switch':
                    rl = re.match(r'(case\s+[^:;{}]+?|default)\s*:(?!:)', raw[pos:pos + 200])
                    labels[len(stack)] = re.sub(r'^case\s+', 'case ', re.sub(r'\s+', ' ', (rl or mm).group(1)).strip())
                    pos += mm.end()
                    seg_start = pos
                    continue
            pos += 1
        out = []
        for d, (k, c) in enumerate(stack):
            if k == 'lambda':
                out = []
                continue
            if k == 'if' or k == 'elseif':
                out.append(re.sub(r'\s+', ' ', c).strip())
            elif k == 'else':
                out.append('not (%s)' % re.sub(r'\s+', ' ', c).strip() if c else 'else')
            elif k in ('for', 'while'):
                out.append('%s (%s)' % (k, re.sub(r'\s+', ' ', c).strip()))
            elif k == 'catch':
                out.append('catch (%s)' % c.strip())
            elif k == 'finally':
                out.append('finally')
            elif k == 'sync':
                pass
            if k == 'switch' and (d + 1) in labels:
                out.append(labels[d + 1])
        # a braceless if right before the call
        tail = re.sub(r'\s+', ' ', raw[seg_start:target]).strip()
        mm = re.match(r'(?:else )?if\s*\((.*)\)\s*\S?.*$', tail)
        if mm and tail.count('(') >= 1:
            out.append(mm.group(1)[:200])
        return out[-depth:]

    # ---- branches of a method
    def branches(self, fname, name, nth=0, params=None, any_depth=False):
        lines, text = self._load(fname)
        starts = self._offsets(text)
        a, b = self.method_lines(fname, name, nth, params, any_depth)
        o0 = starts[a - 1]
        o1 = starts[b]
        body_open = text.index('{', o0)
        body_close = self._match(text, body_open)
        body = text[body_open + 1:body_close]
        base = body_open + 1
        # top-level statements: depth 0 of the body
        m = None
        depth = 0
        i = 0
        while i < len(body):
            c = body[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            elif depth == 0 and body.startswith('switch', i) and re.match(r'switch\s*\(', body[i:]) and (i == 0 or not (body[i - 1].isalnum() or body[i - 1] == '_')):
                m = ('switch', i)
                break
            elif depth == 0 and body.startswith('if', i) and re.match(r'if\s*\(', body[i:]) and (i == 0 or not (body[i - 1].isalnum() or body[i - 1] == '_')) and not re.search(r'else\s*$', body[:i]):
                m = ('if', i)
                break
            i += 1
        if not m:
            return []
        kind, i = m
        if kind == 'switch':
            p = body.index('(', i)
            pe = self._match(body, p, '(', ')')
            ob = body.index('{', pe)
            cb = self._match(body, ob)
            inner = body[ob + 1:cb]
            ibase = base + ob + 1
            labels = []      # (label text, offset of label start, offset of colon end)
            d = 0
            j = 0
            while j < len(inner):
                c = inner[j]
                if c == '{':
                    d += 1
                elif c == '}':
                    d -= 1
                elif d == 0:
                    mm = re.match(r'(case\s+[^:]+?|default)\s*:(?!:)', inner[j:])
                    if mm and (j == 0 or not (inner[j - 1].isalnum() or inner[j - 1] == '_')):
                        labels.append((re.sub(r'^case\s+', '', mm.group(1)).strip(), j, j + mm.end()))
                        j += mm.end()
                        continue
                j += 1
            out = []
            pending = []
            for k, (lab, s0, s1) in enumerate(labels):
                nxt = labels[k + 1][1] if k + 1 < len(labels) else len(inner)
                stmt = inner[s1:nxt]
                pending.append(lab)
                if stmt.strip() == '':
                    continue          # fall-through label: shares the next range
                la = self._line_of(starts, ibase + s0)
                lb = self._line_of(starts, ibase + nxt - 1)
                last = inner[:nxt].rstrip()
                lb = self._line_of(starts, ibase + len(last) - 1)
                for l_ in pending:
                    out.append((l_, la, lb))
                pending = []
            return out
        # if / else-if chain
        out = []
        j = i
        while True:
            mm = re.match(r'if\s*\(', body[j:])
            if not mm:
                break
            p = j + body[j:].index('(')
            pe = self._match(body, p, '(', ')')
            cond = re.sub(r'\s+', ' ', body[p + 1:pe]).strip()
            k = pe + 1
            while body[k] in ' \n\t\r':
                k += 1
            if body[k] == '{':
                ke = self._match(body, k)
            else:
                ke = body.index(';', k)
            out.append((cond, self._line_of(starts, base + j), self._line_of(starts, base + ke)))
            t = ke + 1
            while t < len(body) and body[t] in ' \n\t\r':
                t += 1
            if body.startswith('else', t):
                t += 4
                while t < len(body) and body[t] in ' \n\t\r':
                    t += 1
                if re.match(r'if\s*\(', body[t:]):
                    j = t
                    continue
                if body[t] == '{':
                    te = self._match(body, t)
                else:
                    te = body.index(';', t)
                out.append(('else', self._line_of(starts, base + t), self._line_of(starts, base + te)))
            break
        return out


if __name__ == '__main__':
    app, fname, meth = sys.argv[1:4]
    CS = Cases(app)
    print(CS.method_lines(fname, meth))
    for b in CS.branches(fname, meth):
        print(b)
