"""STEP Preparation department: turns the 30 "STEP Foundation" mock exams into app data.

    python3 -I tools/app/build_step.py <folder with docx/mNN.txt and audio/MNN-L-XX.mp3>

docx/mNN.txt is the plain text of STEP_F_Mock_NN.docx (pandoc -t plain --wrap=none).
Output: www/step/mNN.js (one exam each), www/step/index.js (the list), www/audio/step/*.mp3 (speech, 48 kbit/s mono).
Every exam is checked: 100 questions, four options each, the key agrees with the compact key, 13 recordings with audio."""
import json, os, re, subprocess, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = sys.argv[1]
OUT = os.path.join(ROOT, 'www', 'step'); AUD = os.path.join(ROOT, 'www', 'audio', 'step')
os.makedirs(OUT, exist_ok=True); os.makedirs(AUD, exist_ok=True)
SEC = {1: ('R', 'Reading Comprehension', 'فهم المقروء', 70), 2: ('S', 'Sentence Structure', 'تركيب الجمل', 35),
       3: ('L', 'Listening Comprehension', 'فهم المسموع', 30), 4: ('C', 'Composition Analysis', 'التحليل الإنشائي', 20)}
OPT = re.compile(r'(?:^|\s)([A-D])\.\s+')


def options(lines):
    """Option lines are either one per line ("A. …") or packed ("A. … B. …"). Letters are looked for in order,
    so a name such as "Group B." inside an option is not taken for a new option."""
    text = ' ' + ' '.join(x.strip() for x in lines) + ' '
    pos, at = [], 0
    for k in 'ABCD':
        m = re.search(r'\s' + k + r'\.\s+', text[at:])
        assert m, (k, text[:140])
        pos.append((at + m.start(), at + m.end())); at += m.end()
    assert pos[0][0] == 0, text[:140]
    return [text[pos[i][1]:(pos[i + 1][0] if i < 3 else len(text))].strip() for i in range(4)]


def parse(n):
    raw = open(os.path.join(SRC, 'docx', f'm{n:02d}.txt'), encoding='utf-8').read().split('\n')
    L = [x.rstrip() for x in raw]
    head = '\n'.join(L[:40])
    setline = re.search(r'^(Set [A-C]) — (.+?) · 100 questions', head, re.M)
    band = re.search(r'Difficulty band: (.+)$', head, re.M)
    i0 = next(i for i, x in enumerate(L) if re.match(r'^Section 1 — Reading Comprehension \(Questions', x))
    ik = next(i for i, x in enumerate(L) if x == 'Answer Key')
    isc = next(i for i, x in enumerate(L) if x == 'Listening Scripts')
    body, key, scr = L[i0:ik], L[ik:isc], L[isc:]
    secs, cur, grp, q, nextn = [], None, None, None, 1

    def close_q():
        nonlocal q
        if q is None: return
        ctx, opt = [], []
        for ln in q.pop('_l'):
            (opt if (opt or re.match(r'^A\.\s', ln)) else ctx).append(ln)
        q['o'] = options(opt)
        if ctx: q['x'] = ctx
        grp['q'].append(q); q = None

    def new_grp(**kw):
        nonlocal grp
        close_q(); grp = dict(kw, q=[]); cur['g'].append(grp)

    for ln in body:
        s = ln.strip()
        if not s: continue
        m = re.match(r'^Section (\d) — (.+?) \(Questions (\d+)–(\d+)\)$', s)
        if m:
            close_q(); k = int(m.group(1))
            cur = {'id': SEC[k][0], 'name': SEC[k][1], 'ar': SEC[k][2], 'min': SEC[k][3], 'from': int(m.group(3)), 'to': int(m.group(4)), 'g': []}
            secs.append(cur); grp = None; new_grp(); continue
        m = re.match(r'^Passage (\d+): (.+)$', s)
        if m and cur['id'] == 'R': new_grp(t=m.group(2), p=[]); continue
        m = re.match(r'^Recording (\d+) \(Questions? [\d–]+\) Track (M\d\d-L-\d\d)$', s)
        if m: new_grp(rec=int(m.group(1)), a=m.group(2)); continue
        m = re.match(r'^Questions (\d+)–(\d+): (.+)$', s)
        if m and cur['id'] == 'S': new_grp(i=m.group(3)[0].upper() + m.group(3)[1:], err='underlined' in m.group(3)); continue
        m = re.match(r'^(\d+)\. (.+)$', s)
        if m and int(m.group(1)) == nextn:
            close_q(); q = {'n': nextn, 's': m.group(2), '_l': []}; nextn += 1; continue
        if q is not None: q['_l'].append(s); continue
        if grp is not None and 'p' in grp and re.match(r'^\[\d+\] ', s): grp['p'].append(re.sub(r'^\[\d+\] ', '', s)); continue
        if re.search(r'[؀-ۿ]', s): cur.setdefault('iar', s) if not any(g['q'] for g in cur['g']) else None; continue
        if s in ('Short conversations', 'Longer conversations', 'Talks', 'Talks and lectures', 'Short talks') or re.match(r'^(Short|Longer|Talks?|Lectures?)\b.{0,40}$', s): continue
        if not any(g['q'] for g in cur['g']) and 'i' not in cur and len(cur['g']) == 1 and not cur['g'][0].get('t'): cur['i'] = s; continue
        raise SystemExit(f'mock {n}: unplaced line in section {cur["id"]}: {s[:90]}')
    close_q()
    for sc in secs: sc['g'] = [g for g in sc['g'] if g['q']]
    # ---- answer key: letter, question type, explanation, Arabic hint
    ans = {}
    for i, ln in enumerate(key):
        m = re.match(r'^(\d+)\. ([A-D]) — \[(.+?)\] ?(.*)$', ln.strip())
        if m:
            nx = next((x.strip() for x in key[i + 1:i + 4] if x.strip()), '')
            ans[int(m.group(1))] = [m.group(2), m.group(3).split(' · ')[0], m.group(4), re.sub(r'^تلميح:\s*', '', nx) if nx.startswith('تلميح') else '']
    compact = {int(a): b for a, b in re.findall(r'\b(\d+)-([A-D])\b', '\n'.join(x for x in key if re.match(r'^Section \d — .+: \d+-[A-D]', x)))}
    # ---- listening scripts (shown only in the review after the exam)
    scripts, curs = {}, None
    for ln in scr:
        s = ln.strip()
        m = re.match(r'^Recording \d+ \(Q[\d–]+\): (.+) \[(M\d\d-L-\d\d)\]$', s)
        if m: curs = scripts[m.group(2)] = {'t': m.group(1), 'l': []}; continue
        if curs is not None and s and not re.search(r'[؀-ۿ]', s): curs['l'].append(s)
    # ---- checks
    qs = [x for sc in secs for g in sc['g'] for x in g['q']]
    assert [x['n'] for x in qs] == list(range(1, 101)), (n, len(qs))
    assert [(sc['from'], sc['to']) for sc in secs] == [(1, 40), (41, 70), (71, 90), (91, 100)], n
    assert len(ans) == 100 and len(compact) == 100 and all(ans[k][0] == compact[k] for k in ans), (n, 'key')
    recs = [g for g in secs[2]['g']]
    assert len(recs) == 13 and all(g['a'] in scripts for g in recs), (n, 'recordings')
    for x in qs: x['k'] = 'ABCD'.index(ans[x['n']][0]); x['ty'], x['e'], x['h'] = ans[x['n']][1:]
    for g in recs:
        assert os.path.exists(os.path.join(SRC, 'audio', g['a'] + '.mp3')), g['a']
        g['t'] = scripts[g['a']]['t']; g['sc'] = scripts[g['a']]['l']
    return {'n': n, 'set': setline.group(1)[-1], 'level': setline.group(2), 'band': band.group(1) if band else '', 'sec': secs}


index, bal = [], [0, 0, 0, 0]
for n in range(1, 31):
    d = parse(n)
    for sc in d['sec']:
        for g in sc['g']:
            for x in g['q']: bal[x['k']] += 1
    open(os.path.join(OUT, f'm{n:02d}.js'), 'w', encoding='utf-8', newline='\n').write(
        f'/* STEP-style mock exam {n} (original material by Waleed Youssef; not an official STEP paper) */\n(window.STEP_DATA = window.STEP_DATA || {{}})[{n}] = '
        + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ';\n')
    index.append({'n': n, 'set': d['set'], 'level': d['level'], 'band': d['band'], 'pass': [g['t'] for g in d['sec'][0]['g']]})
open(os.path.join(OUT, 'index.js'), 'w', encoding='utf-8', newline='\n').write('/* generated by tools/app/build_step.py */\nwindow.STEP_INDEX = ' + json.dumps(index, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('30 exams, 3000 questions; key balance A–D:', bal)
if '--no-audio' not in sys.argv:
    names = sorted(x for x in os.listdir(os.path.join(SRC, 'audio')) if x.endswith('.mp3'))
    for x in names:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(SRC, 'audio', x), '-ac', '1', '-ar', '24000', '-codec:a', 'libmp3lame', '-b:a', '48k', os.path.join(AUD, x)], check=True)
    print(len(names), 'recordings,', sum(os.path.getsize(os.path.join(AUD, x)) for x in names) // 1048576, 'MB')
