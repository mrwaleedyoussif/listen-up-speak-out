"""v1.12.0: STEP Preparation department opens with 30 STEP-style mock exams (www/step.js, data from tools/app/build_step.py).
Run once:  python3 tools/app/patch_v112.py"""
import os, json, re
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda p: open(p, encoding='utf-8').read()
wr = lambda p, s: open(p, 'w', encoding='utf-8').write(s)


def one(s, a, b, n=1, where=''):
    c = s.count(a)
    assert c == n, f'{where}: expected {n} x {a[:90]!r}, found {c}'
    return s.replace(a, b)


W = 'index.html'; p = P('www', 'index.html'); s = rd(p)
s = one(s, '<script src="map.js"></script>\n', '<script src="map.js"></script>\n<script src="step/index.js"></script>\n<script src="step.js"></script>\n', 1, W)
s = one(s, 'else { if (typeof MAPX !== "undefined") MAPX.register();', 'else { if (typeof MAPX !== "undefined") MAPX.register(); if (typeof STEPX !== "undefined") STEPX.register();', 1, W)
s = one(s, "['step', 'STEP Preparation', 'التحضير لاختبار STEP', '', '#12B5CB', '#0A7C96', 'dept', 1],", "['step', 'STEP Preparation', 'التحضير لاختبار STEP', '30 mock exams · 3,000 questions', '#12B5CB', '#0A7C96', 'step', 0],", 1, W)
# introduction of the department (now open)
i = s.index("  step: ['STEP Preparation will train you"); j = s.index("  ph: [", i)
s = s[:i] + """  step: ['This department prepares you for the Standardized Test of English Proficiency (STEP) with 30 full practice exams in three sets: Foundation, Intermediate and Exam Standard. Every exam has the four STEP sections and 100 questions. Take a section with its timer, then review each answer with its question type, an explanation and an Arabic hint.',
    'هذا القسم يجهّزك لاختبار كفايات اللغة الإنجليزية (STEP) بثلاثين اختبارًا تدريبيًا كاملًا في ثلاث مجموعات: تأسيسي ومتوسط ومستوى الاختبار. في كل اختبار أقسام STEP الأربعة ومئة سؤال. أدِّ القسم مع المؤقّت، ثم راجع كل إجابة مع نوع السؤال وشرح وتلميح بالعربية.',
    ['Reading comprehension · 40', 'Sentence structure · 30', 'Listening comprehension · 20', 'Composition analysis · 10']],
""" + s[j:]
s = one(s, "    if (v === 'map') { go('home'); return true; }", "    if (v === 'map' || v === 'step') { go('home'); return true; }\n    if (v === 'stepmock') { go('step'); return true; }\n    if (v === 'stepsec') { go('stepmock', { sm: S.sm }); return true; }", 1, W)
s = one(s, "safe() { return ['home', 'ls', 'ghars', 'dept', 'grade',", "safe() { return ['home', 'ls', 'ghars', 'dept', 'step', 'stepmock', 'grade',", 1, W)
s = one(s, "Shadowing, MAP Test or Grammar and Vocabulary (Levels A1 to C2). Reading and Writing, STEP Preparation,", "Shadowing, MAP Test, Grammar and Vocabulary (Levels A1 to C2) or STEP Preparation (30 mock exams). Reading and Writing,", 1, W)
s = one(s, "@media (min-width:1001px){.depts.n4 .dept{grid-column:span 3}.depts.n4 .dept h3{font-size:1.32rem}}\n.depts-soon{grid-template-columns:repeat(4,1fr)}",
        "@media (min-width:1001px){.depts.n4 .dept{grid-column:span 3}.depts.n4 .dept h3{font-size:1.32rem}.depts.n5 .dept{grid-column:span 4}.depts.n5 .dept:nth-child(n+4){grid-column:span 6}}\n.depts-soon{grid-template-columns:repeat(3,1fr)}", 1, W)
# progress line on the STEP card
m = re.search(r"\n(\s*)<section class=\"depts n\$\{open\.length\}\">", s); assert m
s = one(s, "<section class=\"depts n${open.length}\">${open.map((d, i) => deptCard(d, i, meta[d[0]])).join('')}</section>", "<section class=\"depts n${open.length}\">${open.map((d, i) => deptCard(d, i, meta[d[0]] || (d[0] === 'step' && typeof STEPX !== 'undefined' ? STEPX.homeMeta() : ''))).join('')}</section>", 1, W)
s = one(s, "const APP_VER = '1.11.1';", "const APP_VER = '1.12.0';", 1, W)
wr(p, s)

t = rd(P('README.md'))
t = one(t, "are open; Reading and Writing, STEP Preparation,", "and **STEP Preparation** (30 mock exams in `www/step`, built by `tools/app/build_step.py`) are open; Reading and Writing,", 1, 'README')
wr(P('README.md'), t)
t = rd(P('package.json')); wr(P('package.json'), one(t, '"version": "1.11.1"', '"version": "1.12.0"', 1, 'package.json'))
t = rd(P('package-lock.json')); assert t.count('"version": "1.11.1"') >= 2
wr(P('package-lock.json'), t.replace('"version": "1.11.1"', '"version": "1.12.0"', 2))
cl = json.loads(rd(P('tools', 'app', 'changelog.json'))); assert '1.12.0' not in cl
cl = {'1.12.0': {
    'en': ['New department: STEP Preparation is open with 30 STEP-style mock exams in three sets (Foundation, Intermediate, Exam Standard), 3,000 questions and 390 listening recordings.',
           'Each exam has the four STEP sections with a timer. After a section you see your score, the question types you missed, and every answer with an explanation and an Arabic hint; listening scripts appear in the review.'],
    'ar': ['قسم جديد: التحضير لاختبار STEP مفتوح الآن بثلاثين اختبارًا تدريبيًا في ثلاث مجموعات (تأسيسي، متوسط، مستوى الاختبار) و3000 سؤال و390 تسجيلًا للاستماع.',
           'في كل اختبار أقسام STEP الأربعة مع مؤقّت. بعد كل قسم ترى درجتك وأنواع الأسئلة التي أخطأت فيها وكل إجابة مع شرح وتلميح بالعربية، وتظهر نصوص الاستماع في المراجعة.']}, **cl}
wr(P('tools', 'app', 'changelog.json'), json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('v1.12.0 patched')
