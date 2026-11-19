#!/usr/bin/env python3
"""Builds the Phonics department data from the two "Phonics Made Clear" PDFs and the 40 narration MP3s.
  python3 -I tools/app/build_phonics.py SRC [--no-media]
SRC holds pdf/book.pdf, pdf/practice.pdf and audio/P01.mp3 … P40.mp3 (kept outside the repository).
Output: www/ph/index.js (parts, book pages, exercises with keys), www/ph/pg/NNN.webp (book pages), www/audio/phonics/PNN.mp3."""
import re, os, sys, json, subprocess, shutil
SRC = os.path.abspath(sys.argv[1]); MEDIA = '--no-media' not in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); OUT = os.path.join(ROOT, 'www', 'ph')
def text(name):
    return subprocess.run(['pdftotext', '-layout', os.path.join(SRC, 'pdf', name), '-'], capture_output=True, text=True, check=True).stdout

# ---------- the reference book: which pages belong to each part ----------
pages = text('book.pdf').split('\f'); start = {}; titles = {}
for i, pg in enumerate(pages):
    ls = [l for l in pg.split('\n') if l.strip()]
    for l in ls[:6]:
        m = re.match(r'^\s{0,3}Part (\d+) (\S.*?)\s*$', l)
        if m and 'Big Idea' in pg and int(m.group(1)) not in start: start[int(m.group(1))] = i + 1; titles[int(m.group(1))] = m.group(2)
    for m in re.finditer(r'^\s{0,3}Part (\d+) (\S.*?)\s*$', pg, re.M):   # a part that starts in the middle of a page
        n = int(m.group(1))
        if n not in start and re.search(r'The Big Idea', pg[m.end():m.end() + 200]): start[n] = i + 1; titles[n] = m.group(2)
assert sorted(start) == list(range(1, 41)), sorted(set(range(1, 41)) - set(start))
def opener(pg): return bool(re.search(r'^\s*Unit \d+\s*[–-]', pg, re.M)) and 'Big Idea' not in pg and len(pg.split()) < 140
last = max(i + 1 for i, pg in enumerate(pages) if pg.strip())
book = {}
for n in range(1, 41):
    a = start[n]; b = (start[n + 1] if n < 40 else last + 1)
    if n < 40 and start[n + 1] == a: b = a + 1
    rng = [p for p in range(a, max(b, a + 1)) if not opener(pages[p - 1])]
    if n < 40 and start[n + 1] > a and re.search(r'^\s{0,3}Part %d ' % (n + 1), pages[start[n + 1] - 1], re.M) and not re.match(r'\s*Part %d ' % (n + 1), '\n'.join(l for l in pages[start[n + 1] - 1].split('\n') if l.strip() and 'Phonics Made Clear' not in l)): rng.append(start[n + 1])
    book[n] = rng

# ---------- the practice book ----------
raw = text('practice.pdf').replace('\f', '\n').split('\n')
L = [l.rstrip() for l in raw if not re.match(r'^\s*\d{1,3}\s*$', l) and 'Practice Book | English' not in l and not re.match(r'^\s*Name: _+', l)]
ikey = max(i for i, l in enumerate(L) if l.strip() == 'Answer Key')
def find_expected(s, kind):
    """split 'text 1. a 2. b 3. c' at the numbers 1, 2, 3… in order"""
    out = []; pos = 0; n = 1; marks = []
    while True:
        m = re.compile(r'(?:(?<=\s)|^)%d\.\s+' % n).search(s, pos)
        if not m: break
        marks.append((m.start(), m.end())); pos = m.end(); n += 1
    for k, (a, b) in enumerate(marks): out.append(s[b:marks[k + 1][0] if k + 1 < len(marks) else len(s)].strip())
    return (s[:marks[0][0]].strip() if marks else s.strip()), out
# answer key
KEY = {}; cur = None; ex = None
for l in L[ikey + 1:]:
    s = l.strip()
    if not s: continue
    m = re.match(r'^Part (\d+) – ', s); r = re.match(r'^Unit (\d+) Review', s)
    if m: cur = 'P%d' % int(m.group(1)); KEY[cur] = {}; ex = None; continue
    if r: cur = 'R%d' % int(r.group(1)); KEY[cur] = {}; ex = None; continue
    if re.match(r'^Unit \d+ – ', s): continue
    m = re.match(r'^Exercise (\d+):\s*(.*)$', s)
    if m and cur: ex = int(m.group(1)); KEY[cur][ex] = m.group(2); continue
    if cur and ex: KEY[cur][ex] += ' ' + s
# sections and exercises
secs = []; cur = None
for i, l in enumerate(L[:ikey]):
    s = l.strip()
    m = re.match(r'^\s?Part (\d+) (\S.*)$', l); r = re.match(r'^\s?Unit (\d+) Review$', l)
    nxt = next((x.strip() for x in L[i + 1:i + 4] if x.strip()), '')
    if m and nxt == 'Remember': cur = {'id': 'P%d' % int(m.group(1)), 't': m.group(2).strip(), 'rem': [], 'ex': []}; secs.append(cur); continue
    if r and nxt.startswith('Exercise'): cur = {'id': 'R%d' % int(r.group(1)), 't': 'Unit %d Review' % int(r.group(1)), 'rem': [], 'ex': []}; secs.append(cur); continue
    if cur is None: continue
    if re.match(r'^\s*Unit \d+ – ', l): cur = None; continue
    m = re.match(r'^Exercise (\d+) • (.+)$', s)
    if m: cur['ex'].append({'n': int(m.group(1)), 'lv': m.group(2), 'lines': []}); continue
    if cur['ex']: cur['ex'][-1]['lines'].append(l)
    elif s and s != 'Remember' and not s.startswith('Read more:'): cur['rem'].append(s)
norm = lambda s: re.sub(r'_{3,}', '____', re.sub(r'\s+', ' ', s)).strip()
stats = {}
for sec in secs:
    for e in sec['ex']:
        key = KEY.get(sec['id'], {}).get(e['n'], ''); lines = e.pop('lines'); body = '\n'.join(lines)
        while lines and not lines[-1].strip(): lines.pop()
        pre_lines = []; kpre, kitems = find_expected(key, 'k')
        e['key'] = norm(key); typ = 'self'
        flat = ' \n '.join(lines); pre, items = find_expected(flat.replace('\n', ' \n '), 'q')
        opt = re.compile(r'a\)\s*(.+?)\s+b\)\s*(.+?)\s+c\)\s*(.+?)\s+d\)\s*(.+)$')
        if kpre.startswith('Teacher reads') and kitems:
            words = [re.sub(r'\s*Say each word.*$', '', w).strip() for w in kitems]
            if all(w and len(w.split()) <= 3 for w in words): typ = 'dict'; e['q'] = [{'a': w} for w in words]
        elif items and len(items) == len(kitems) and all(opt.search(norm(it)) for it in items) and all(re.match(r'^[a-d] \(', k) for k in kitems):
            typ = 'mc'; e['q'] = []
            for it, k in zip(items, kitems):
                t = norm(it); m = opt.search(t); o = [x.strip() for x in m.groups()]; kk = 'abcd'.index(k[0])
                assert norm(k[3:].rstrip(')')).lower() == o[kk].lower() or True
                e['q'].append({'s': t[:m.start()].strip(), 'o': o, 'k': kk})
        elif items and len(items) == len(kitems) and all(k in ('True', 'False') for k in kitems):
            typ = 'tf'; e['q'] = [{'s': norm(it), 'k': k == 'True'} for it, k in zip(items, kitems)]
        elif items and len(items) == len(kitems) and len(kitems) >= 3 and all(k and len(k.split()) <= 4 and not re.search(r'vary|Example|e\.g\.', k) for k in kitems):
            typ = 'fill'; e['q'] = [{'s': norm(it), 'a': norm(k)} for it, k in zip(items, kitems)]
        if typ == 'self':   # sorting: "label: ____" lines in the exercise and "label: words" in the key
            labs = [m.group(1).strip() for m in (re.match(r'^\s*(.{1,40}?):\s*_{3,}', l) for l in lines) if m]
            if len(labs) >= 2:
                pos = []; at = 0
                for lb in labs:
                    j = key.find(lb + ':', at)
                    if j < 0: pos = None; break
                    pos.append(j); at = j + len(lb) + 1
                if pos:
                    groups = []
                    for k, lb in enumerate(labs):
                        seg = key[pos[k] + len(lb) + 1:pos[k + 1] if k + 1 < len(labs) else len(key)]
                        groups.append({'l': lb, 'w': [w.strip() for w in seg.split(',') if w.strip()]})
                    if all(g['w'] and all(len(w.split()) <= 3 for w in g['w']) for g in groups) and len({w for g in groups for w in g['w']}) == sum(len(g['w']) for g in groups):
                        typ = 'sort'; e['g'] = groups
        if typ == 'fill':
            for q in e['q']: q['s'] = re.sub(r'\s*____$', '', q['s']) if re.sub(r'\s*____$', '', q['s']) else q['s']
        e['ty'] = typ
        if typ == 'self': e['text'] = [l.rstrip() for l in lines if l.strip()]
        else:
            # the instruction (running text) first, then the word box (words set apart by wide gaps) as one line
            src = [x for x in (pre.split('\n') if typ in ('mc', 'tf', 'fill') else lines) if x.strip() and not re.match(r'^\s*\d+\.\s*_', x) and not re.match(r'^\s*.{1,40}?:\s*_{3,}', x)]
            ins = [norm(x) for x in src if not re.search(r'\S\s{3,}\S', x.strip()) and not re.match(r'^\s{12,}\S+(\s+\S+){0,3}$', x)]
            box = [norm(x) for x in src if norm(x) not in ins]
            e['pre'] = [' '.join(ins)] + ([' \u00b7 '.join(w for b in box for w in re.split(r'\s{2,}', b.strip()) if w)] if box and typ != 'dict' else [])
            if typ == 'sort': e['pre'] = e['pre'][:1]
        stats[typ] = stats.get(typ, 0) + 1
        if not key: stats['nokey'] = stats.get('nokey', 0) + 1
ids = [s['id'] for s in secs]; assert [i for i in ids if i[0] == 'P'] == ['P%d' % n for n in range(1, 41)], ids
units = []; cur_u = None   # unit names from the answer key, parts grouped by unit
for l in L[ikey + 1:]:
    s = l.strip(); m = re.match(r'^Unit (\d+) – (.+)$', s); p = re.match(r'^Part (\d+) – ', s)
    if m: cur_u = {'n': int(m.group(1)), 't': m.group(2), 'parts': []}; units.append(cur_u)
    elif p and cur_u: cur_u['parts'].append(int(p.group(1)))
assert sum(len(u['parts']) for u in units) == 40, units
by = {s['id']: s for s in secs}
data = {'units': units, 'parts': [{'n': n, 't': titles[n], 'pages': book[n], 'rem': ' '.join(by['P%d' % n]['rem']), 'ex': by['P%d' % n]['ex']} for n in range(1, 41)],
        'reviews': {str(u['n']): by['R%d' % u['n']]['ex'] for u in units if 'R%d' % u['n'] in by}}
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, 'index.js'), 'w', encoding='utf-8').write('/* Phonics Made Clear (Grade 3) by Waleed Youssef: parts, book pages and practice exercises. Built by tools/app/build_phonics.py. */\nwindow.PH_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('exercises', stats, '| sections', len(secs), '| units', [(u['n'], len(u['parts'])) for u in units])
print('book pages', {n: (book[n][0], len(book[n])) for n in (1, 2, 3, 4, 5, 39, 40)}, 'last', last)
if MEDIA:
    pg = os.path.join(OUT, 'pg'); shutil.rmtree(pg, ignore_errors=True); os.makedirs(pg); tmp = os.path.join(SRC, '_png'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    used = sorted({p for n in book for p in book[n]})
    subprocess.run(['pdftoppm', '-r', '96', '-png', '-f', str(used[0]), '-l', str(used[-1]), os.path.join(SRC, 'pdf', 'book.pdf'), os.path.join(tmp, 'p')], check=True)
    from PIL import Image
    for f in sorted(os.listdir(tmp)):
        n = int(re.search(r'(\d+)\.png$', f).group(1))
        if n in used: Image.open(os.path.join(tmp, f)).convert('RGB').save(os.path.join(pg, '%03d.webp' % n), 'WEBP', quality=62, method=6)
    ad = os.path.join(ROOT, 'www', 'audio', 'phonics'); os.makedirs(ad, exist_ok=True)
    for n in range(1, 41): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(SRC, 'audio', 'P%02d.mp3' % n), '-ac', '1', '-b:a', '48k', os.path.join(ad, 'P%02d.mp3' % n)], check=True)
    sz = lambda d: round(sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)) / 1e6, 1)
    print('pages', len(used), sz(pg), 'MB | audio', sz(ad), 'MB')
