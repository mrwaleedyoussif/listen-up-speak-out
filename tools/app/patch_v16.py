"""v1.6.0: Language Usage material in the MAP Growth department — connects it in www/index.html.
Run once:  python3 tools/app/patch_v16.py   (www/map.js is patched by patch_v16_map.py)"""
import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = os.path.join(ROOT, 'www', 'index.html')
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, f'expected {n} x {a[:70]!r}, found {c}'
    s = s.replace(a, b)

rep("const APP_VER = '1.5.0';", "const APP_VER = '1.6.0';")
# Back / Up keeps the subject (Reading or Language Usage)
rep("    if (v === 'mapset' || v === 'mapmock') { if (v === 'mapmock' && (S.run || S.res)) go('mapmock', { mg: S.mg, mk: S.mk }); else go('mapgrade', { mg: S.mg }); return true; }",
    "    if (v === 'mapset' || v === 'mapmock') { if (v === 'mapmock' && (S.run || S.res)) go('mapmock', { mg: S.mg, mk: S.mk, subj: S.subj }); else go('mapgrade', { mg: S.mg, subj: S.subj }); return true; }")
rep("Reading for Grades 3–9 — 6 practice units (78 questions) and 5 full mock exams of 43 questions per grade, scored by goal area (Literary Text, Informational Text, Vocabulary). Mock answers are saved as students go. Language Usage is coming soon.</li>",
    "Reading and Language Usage for Grades 3–9 — per subject and grade, 6 practice units (78 questions) and 5 full mock exams of 43 questions, scored by goal area (Reading: Literary Text, Informational Text, Vocabulary; Language Usage: Writing, Grammar and Usage, Mechanics). Mock answers are saved as students go.</li>")
open(P, 'w', encoding='utf-8').write(s)
print('index.html patched for v1.6.0')
