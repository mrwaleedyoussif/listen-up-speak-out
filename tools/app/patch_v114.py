#!/usr/bin/env python3
"""v1.14.0: Phonics department (www/ph.js, www/ph/index.js, book pages, narration audio)."""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def one(s, a, b, n=1, where=''):
    assert s.count(a) == n, (where or a[:60], s.count(a)); return s.replace(a, b)
p = os.path.join(ROOT, 'www', 'index.html'); s = open(p, encoding='utf-8').read()
s = one(s, '<script src="hw.js"></script>\n', '<script src="hw.js"></script>\n<script src="ph/index.js"></script>\n<script src="ph.js"></script>\n')
s = one(s, 'if (typeof HWX !== "undefined") HWX.register();', 'if (typeof HWX !== "undefined") HWX.register(); if (typeof PHX !== "undefined") PHX.register();')
s = one(s, "  ['ph', 'Phonics', 'الصوتيات', '', '#F0569C', '#C92671', 'dept', 1],", "  ['ph', 'Phonics', 'الصوتيات', 'Phonics Made Clear · 40 parts · audio', '#F0569C', '#C92671', 'ph', 0],")
a = s.index("  ph: ['Phonics will teach you"); b = s.index("]],", a) + 3
s = s[:a] + ("  ph: ['This department is the book Phonics Made Clear for Grade 3. It teaches the sounds of English letters and letter groups in 40 parts, from the alphabet and short vowels to syllables and long words. In each part, read the pages of the book and listen to the recording. Then do the practice exercises: the app checks your answers and shows the correct ones.',\n"
             "    'هذا القسم هو كتاب Phonics Made Clear للصف الثالث. يعلّمك أصوات الحروف الإنجليزية ومجموعات الحروف في 40 جزءًا، من الحروف الهجائية والحركات القصيرة إلى المقاطع والكلمات الطويلة. في كل جزء اقرأ صفحات الكتاب واستمع إلى التسجيل، ثم حُلّ تمارين التدريب: يصحّح التطبيق إجاباتك ويعرض الإجابات الصحيحة.',\n"
             "    ['Read the book pages', 'Listen to the recording', 'Practise and check']],") + s[b:]
s = one(s, "    if (v === 'hwp') { go('hw'); return true; }", "    if (v === 'hwp') { go('hw'); return true; }\n    if (v === 'phpart') { go('ph'); return true; }\n    if (v === 'ph') { go('home'); return true; }")
s = one(s, "'steplesson', 'hw', 'grade',", "'steplesson', 'hw', 'ph', 'grade',")
s = one(s, "d[0] === 'hw' && typeof HWX !== 'undefined' ? HWX.homeMeta() : '')", "d[0] === 'hw' && typeof HWX !== 'undefined' ? HWX.homeMeta() : d[0] === 'ph' && typeof PHX !== 'undefined' ? PHX.homeMeta() : '')")
s = one(s, ".depts.n6 .dept{grid-column:span 4}}", ".depts.n6 .dept{grid-column:span 4}.depts.n7 .dept{grid-column:span 3}.depts.n7 .dept:nth-child(n+5){grid-column:span 4}.depts.n7 .dept h3{font-size:1.32rem}}")
# the progress line on a department card may be one text or a list (a single text used to stop the home page)
s = one(s, "${meta.map(x => `<span>${x}</span>`).join('')}", "${[].concat(meta).map(x => `<span>${x}</span>`).join('')}")
s = one(s, "const APP_VER = '1.13.0';", "const APP_VER = '1.14.0';")
open(p, 'w', encoding='utf-8').write(s)
# offline: book pages are saved the first time each one is opened (like the Language Usage lessons), not at install
q = os.path.join(ROOT, 'tools', 'app', 'build_www.py'); t = open(q, encoding='utf-8').read()
t = one(t, "'gv/data/grammar_vocabulary/tests/'))", "'gv/data/grammar_vocabulary/tests/', 'ph/pg/'))"); open(q, 'w', encoding='utf-8').write(t)
for f, n in (('package.json', 1), ('package-lock.json', 2)):
    q = os.path.join(ROOT, f); t = open(q, encoding='utf-8').read(); assert t.count('"version": "1.13.0"') >= n; open(q, 'w', encoding='utf-8').write(t.replace('"version": "1.13.0"', '"version": "1.14.0"', n))
q = os.path.join(ROOT, 'tools', 'app', 'changelog.json'); cl = json.load(open(q, encoding='utf-8'))
cl = {'1.14.0': {'en': ['New department: Phonics, with the book Phonics Made Clear (Grade 3): 40 parts in 11 units, each with its book pages and a recorded narration.',
                         'The Practice Book is interactive: 182 exercises (choose the answer, true or false, write the word, sort the words, dictation), checked with the book’s answer key, plus 10 unit reviews.'],
                  'ar': ['قسم جديد: الصوتيات، ويضم كتاب Phonics Made Clear للصف الثالث: 40 جزءًا في 11 وحدة، ولكل جزء صفحات الكتاب وتسجيل صوتي.',
                         'كتاب التدريب تفاعلي: 182 تمرينًا (اختيار الإجابة، صح أو خطأ، كتابة الكلمة، تصنيف الكلمات، الإملاء) تُصحَّح بمفتاح إجابات الكتاب، مع 10 مراجعات للوحدات.']}, **cl}
open(q, 'w', encoding='utf-8').write(json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('patched 1.14.0')
