#!/usr/bin/env python3
"""Builds www/hw/data.js for the Cursive Handwriting department.
Letter shapes: Hershey Script (single-stroke), from tools/app/hw/HersheyScript1.svg. The Hershey Fonts were originally
created by Dr. A. V. Hershey while working at the U.S. National Bureau of Standards. Each letter is kept as pen strokes
in writing order, so the app can show the direction, animate the writing and measure a student's tracing.
Practice lists follow the school's cursive booklet: letters A-Z, joined letters, and words for each letter."""
import re, html, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
svg = open(os.path.join(HERE, 'hw', 'HersheyScript1.svg'), encoding='utf-8').read()

def strokes(d):
    toks = re.findall(r'[MLC]|-?\d+\.?\d*(?:e-?\d+)?', d); out = []; cur = None; i = 0; cmd = None
    def num(): nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if toks[i] in 'MLC': cmd = toks[i]; i += 1
        if cmd == 'M': cur = [(num(), num())]; out.append(cur); cmd = 'L'
        elif cmd == 'L': cur.append((num(), num()))
        else:
            p0 = cur[-1]; p1 = (num(), num()); p2 = (num(), num()); p3 = (num(), num())
            for k in range(1, 9):
                t = k / 8; a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; e = t ** 3
                cur.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return [[round(v) for p in s for v in p] for s in out if len(s) > 1]

G = {}
for m in re.finditer(r'<glyph\b([^>]*)/?>', svg):
    a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1))); u = html.unescape(a.get('unicode', ''))
    if len(u) == 1 and u.isascii() and u.isalpha(): G[u] = [round(float(a['horiz-adv-x'])), strokes(a.get('d', ''))]
assert len(G) == 52, len(G)

JOINS = ['as ea', 'ed igh', 'ing ng', 'squ ss', 'ai ar', 'au aw ay', 'ck ch', 'er ew', 'ff ll', 'ir kn', 'qu ur', 'sh th', 'ae be', 'de ee', 'fe ge',
         'ie pe', 'se ue', 'ere ure', 'oe re', 've we', 'oa oh', 'oi on', 'oo op', 'or ou', 'ov ow']
WORDS = {'a': 'apple ant arm also', 'b': 'ball bird book blue', 'c': 'cat cake car cloud', 'd': 'dog door duck day', 'e': 'egg ear eat eight',
         'f': 'fish farm food five', 'g': 'goat game girl green', 'h': 'hat hand home horse', 'i': 'ink ice idea into', 'j': 'jam jump juice job',
         'k': 'king kite key kind', 'l': 'lion leaf lamp light', 'm': 'moon milk map mother', 'n': 'nest nose name night', 'o': 'orange owl open one',
         'p': 'pen park play paper', 'q': 'queen quick quiet quiz', 'r': 'rain red road river', 's': 'sun star school seven', 't': 'tree time table two',
         'u': 'umbrella under uncle use', 'v': 'van vase visit very', 'w': 'water wind window week', 'x': 'box fox six taxi', 'y': 'yellow year young you',
         'z': 'zoo zebra zero zip'}
assert len(WORDS) == 26 and all(len(v.split()) == 4 for v in WORDS.values())
data = {'xh': 284, 'asc': 662, 'desc': -378, 'g': G, 'joins': [j.split() for j in JOINS], 'words': {k: v.split() for k, v in WORDS.items()}}
os.makedirs(os.path.join(ROOT, 'www', 'hw'), exist_ok=True)
p = os.path.join(ROOT, 'www', 'hw', 'data.js')
open(p, 'w', encoding='utf-8').write('/* Cursive Handwriting data. Letter strokes: Hershey Script (the Hershey Fonts were originally created by Dr. A. V. Hershey\n   while working at the U.S. National Bureau of Standards). Built by tools/app/build_hw.py. */\nwindow.HW_DATA=' + json.dumps(data, separators=(',', ':')) + ';\n')
print('letters', len(G), 'joins', sum(len(j.split()) for j in JOINS), 'in', len(JOINS), 'pages; words', 104, '|', round(os.path.getsize(p) / 1024), 'KB')
