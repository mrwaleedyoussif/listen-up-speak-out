"""STEP Preparation department: the four "STEP Foundation" booklets (Grammar, Reading, Listening, Composition).

    python3 -I tools/app/build_step_books.py <folder with b1.html … b4.html>

bN.html is `pandoc -t html --wrap=none` of the booklet's MASTER document (b1 Grammar, b2 Reading, b3 Listening,
b4 Composition). For every unit it writes www/step/bk/<G|R|L|C><unit>.js with each lesson (its teaching pages as
HTML and its 30-question quiz with the key, explanations and Arabic hints) and the unit review, and it writes
www/step/books.js with the outline. The Classroom Corner (teacher activity) and review games are left out of the
student pages. Every quiz is checked: numbering, four options, a key and an explanation for every question."""
import html as H, json, os, re, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = sys.argv[1]
OUT = os.path.join(ROOT, 'www', 'step', 'bk'); os.makedirs(OUT, exist_ok=True)
BOOKS = [('G', 'b1', 'Grammar', 'القواعد', 'Sentence Structure', '🧩', '#2F9BF0', '#1D5FD6'), ('R', 'b2', 'Reading', 'القراءة', 'Reading Comprehension', '📖', '#22B573', '#0B8A5A'),
         ('L', 'b3', 'Listening', 'الاستماع', 'Listening Comprehension', '🎧', '#F59E0B', '#C2570C'), ('C', 'b4', 'Composition', 'تحليل الكتابة', 'Composition Analysis', '✍️', '#9B6CF6', '#6D3BE0')]
AR = re.compile(r'[؀-ۿ]')
txt = lambda x: H.unescape(re.sub(r'<[^>]+>', '', x)).replace('\xa0', ' ').strip()
tag = lambda x: (re.match(r'<(h\d|p|blockquote|/blockquote|ul|ol|li|table)', x) or [None, ''])[1]


def options(lines):
    text = ' ' + ' '.join(lines) + ' '
    pos, at = [], 0
    for k in 'ABCD':
        m = re.search(r'\s' + k + r'\.\s+', text[at:])
        if not m: return None
        pos.append((at + m.start(), at + m.end())); at += m.end()
    if pos[0][0] != 0: return None
    return [text[pos[i][1]:(pos[i + 1][0] if i < 3 else len(text))].strip() for i in range(4)]


def parse_quiz(lines, where):
    """lines: plain text lines of a quiz. Returns groups: lead lines (text, recording, part heading) + questions."""
    groups, g, q, nextn = [], None, None, 1

    def close():
        nonlocal q
        if q is None: return
        ctx, opt = [], []
        for ln in q.pop('_l'): (opt if (opt or re.match(r'^A\.\s', ln)) else ctx).append(ln)
        q['o'] = options(opt); assert q['o'], (where, q['n'], opt[:2])
        if ctx: q['x'] = ctx
        g['q'].append(q); q = None

    def full(): return q is not None and options([x for x in q['_l'] if re.match(r'^[A-D]\.\s', x) or (q['_l'].index(x) > 0 and any(re.match(r'^A\.\s', y) for y in q['_l'][:q['_l'].index(x)]))]) is not None

    for s in lines:
        if not s: continue
        m = re.match(r'^(\d+)\. (.+)$', s)
        if m and int(m.group(1)) == nextn:
            close()
            if g is None: g = {'l': [], 'q': []}; groups.append(g)
            q = {'n': nextn, 's': m.group(2), '_l': []}; nextn += 1; continue
        if q is not None and not full(): q['_l'].append(s); continue
        close()
        if g is None or g['q']: g = {'l': [], 'q': []}; groups.append(g)
        m = re.search(r'\bTrack (L-[A-Z0-9+]+-\w+-\w+)\s*$', s)
        if m: g['a'] = m.group(1); s = s[:m.start()].strip()
        g['l'].append(s)
    close()
    groups = [x for x in groups if x['q']]
    return groups, nextn - 1


def parse_key(lines):
    ans, wu = {}, ''
    for i, s in enumerate(lines):
        m = re.match(r'^(\d+)\. ([A-D]) — (.+)$', s)
        if m:
            nx = next((x for x in lines[i + 1:i + 3] if x), '')
            ans[int(m.group(1))] = ['ABCD'.index(m.group(2)), m.group(3), re.sub(r'^تلميح:\s*', '', nx) if nx.startswith('تلميح') else '']
        elif not ans and re.match(r'^(Warm-up|Worked|Example)', s): wu = s
    return ans, wu


def clean(block_lines, scripts):
    """teaching pages as light HTML: no ids, no Classroom Corner, Arabic paragraphs marked for right-to-left."""
    out, skip = [], False
    for x in block_lines:
        t = tag(x)
        if t in ('h3', 'h4'):
            skip = txt(x).startswith('Classroom Corner')
            if skip: continue
        if skip: continue
        x = re.sub(r'\s(id|class|style)="[^"]*"', '', x)
        x = re.sub(r'<(/?)h3>', r'<\1h3>', x)
        x = re.sub(r'<h(\d)><strong>(.*?)</strong></h\1>', r'<h\1>\2</h\1>', x)
        if AR.search(txt(x)) and not re.search(r'[A-Za-z]{4,}.*[A-Za-z]{4,}.*[A-Za-z]{4,}', re.sub(r'<span dir="rtl">.*?</span>', '', txt(x) if False else x)): x = re.sub(r'^<(p|h\d)>', r'<\1 class="ar" dir="rtl">', x)
        x = x.replace('<span dir="rtl">', '<span dir="rtl" lang="ar">')
        m = re.search(r'\[(L-[A-Z0-9+]+-\d+-\w+)\]', x)
        if m and m.group(1) in scripts: x = x.replace(m.group(0), f'<button class="btn sm st-say" data-tr="{m.group(1)}">▶ Listen</button>')
        out.append(x)
    return '\n'.join(out)


outline, totals = [], {'lessons': 0, 'q': 0}
for code, f, name, ar, link, ic, ca, cb in BOOKS:
    L = open(os.path.join(SRC, f + '.html'), encoding='utf-8').read().split('\n')
    T = [txt(x) for x in L]
    heads = [(i, tag(L[i]), T[i]) for i in range(len(L)) if tag(L[i]) in ('h1', 'h2', 'h3')]
    def find(pat, start=0):
        return [(i, t) for i, h, t in heads if i >= start and re.match(pat, t)]
    ikey = find(r'^Answer Key$')[0][0]
    # listening scripts by track code
    scripts = {}
    if code == 'L':
        s0 = find(r'^Teacher Section — Audio Scripts')[0][0]; cur = None
        for i in range(s0, ikey):
            s = T[i]; m = re.search(r'\[(L-[A-Z0-9+]+-\w+-\w+)\]\s*$', s)
            if m: cur = scripts[m.group(1)] = []; continue
            if tag(L[i]) in ('h1', 'h2'): cur = None; continue
            if cur is not None and s and not AR.search(s) and not re.match(r'^\(?\d+ words\)?$', s): cur.append(s)
    # answer keys by title
    keys = {}; kh = [(i, t) for i, h, t in heads if i > ikey and t.endswith('— Answer Key')] + [(len(L), '')]
    for (i, t), (j, _) in zip(kh, kh[1:]): keys[t[:-len(' — Answer Key')]] = parse_key(T[i + 1:j])
    units = find(r'^Unit \d — ')
    units = [(i, t) for i, t in units if i < ikey and any(h == 'h1' for k, h, tt in heads if k == i)]
    stops = sorted(i for i, h, t in heads if h in ('h1', 'h2') or re.match(r'^(Lesson \d\.\d+ Quiz|Unit \d Review)', t))
    nxt = lambda i: next(k for k in stops + [len(L)] if k > i)
    book = {'id': code, 'name': name, 'ar': ar, 'link': link, 'ic': ic, 'a': ca, 'b': cb, 'units': []}
    for ui, (u0, ut) in enumerate(units):
        u1 = units[ui + 1][0] if ui + 1 < len(units) else min(i for i, h, t in heads if i > u0 and h == 'h1')
        m = re.match(r'^Unit (\d) — ([A-Z0-9+]+): (.+)$', ut); un = int(m.group(1))
        unit = {'n': un, 'level': m.group(2), 't': m.group(3), 'lessons': [], 'sc': {}}
        used = set()
        for li, lt in [(i, t) for i, h, t in heads if u0 < i < u1 and re.match(r'^Lesson \d\.\d+ — ', t)]:
            m = re.match(r'^Lesson (\d\.\d+) — (.+)$', lt); lid = m.group(1)
            qi = next(i for i, h, t in heads if i > li and t.startswith(f'Lesson {lid} Quiz'))
            groups, n = parse_quiz(T[qi + 1:nxt(qi)], f'{code} {lid}')
            ans, wu = keys[f'Lesson {lid} Quiz']
            assert n == len(ans) and n >= 20, (code, lid, n, len(ans))
            for g in groups:
                for q in g['q']: q['k'], q['e'], q['h'] = ans[q['n']]
                if g.get('a'): assert g['a'] in scripts, (code, lid, g['a']); used.add(g['a'])
            page = clean(L[li + 1:qi], scripts)
            used.update(re.findall(r'data-tr="([^"]+)"', page))
            unit['lessons'].append({'id': lid, 't': m.group(2), 'html': page, 'wu': wu, 'quiz': groups, 'n': n}); totals['lessons'] += 1; totals['q'] += n
        ri = [(i, t) for i, h, t in heads if u0 < i < u1 and re.match(rf'^Unit {un} Review — \d+ Questions', t)]
        if ri:
            groups, n = parse_quiz(T[ri[0][0] + 1:nxt(ri[0][0])], f'{code} review {un}')
            ans, _ = keys[f'Unit {un} Review']
            assert n == len(ans), (code, 'review', un, n, len(ans))
            for g in groups:
                for q in g['q']: q['k'], q['e'], q['h'] = ans[q['n']]
                if g.get('a'): assert g['a'] in scripts, g['a']; used.add(g['a'])
            unit['review'] = {'quiz': groups, 'n': n}; totals['q'] += n
        unit['sc'] = {k: scripts[k] for k in sorted(used)}
        open(os.path.join(OUT, f'{code}{un}.js'), 'w', encoding='utf-8', newline='\n').write(
            f'/* STEP Foundation — {name}, Unit {un} (original material by Waleed Youssef) */\n(window.STEP_BOOK = window.STEP_BOOK || {{}})["{code}{un}"] = '
            + json.dumps(unit, ensure_ascii=False, separators=(',', ':')) + ';\n')
        book['units'].append({'n': un, 'level': unit['level'], 't': unit['t'], 'review': unit.get('review', {}).get('n', 0), 'lessons': [[x['id'], x['t'], x['n']] for x in unit['lessons']]})
    outline.append(book)
    print(name, [(u['level'], len(u['lessons']), u['review']) for u in book['units']])
open(os.path.join(ROOT, 'www', 'step', 'books.js'), 'w', encoding='utf-8', newline='\n').write('/* generated by tools/app/build_step_books.py */\nwindow.STEP_BOOKS = ' + json.dumps(outline, ensure_ascii=False, separators=(',', ':')) + ';\n')
size = sum(os.path.getsize(os.path.join(OUT, x)) for x in os.listdir(OUT))
print(totals, f'{size / 1048576:.1f} MB')
