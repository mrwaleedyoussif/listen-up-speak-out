#!/usr/bin/env python3
"""v1.13.0: Cursive Handwriting department (www/hw.js, www/hw/data.js); Ghars Arabic name corrected to غرس."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def one(s, a, b, n=1, where=''):
    assert s.count(a) == n, (where or a[:60], s.count(a)); return s.replace(a, b)
p = os.path.join(ROOT, 'www', 'index.html'); s = open(p, encoding='utf-8').read()
s = one(s, 'غراس', 'غرس', 3, 'ghars name')
s = one(s, '<script src="step.js"></script>\n', '<script src="step.js"></script>\n<script src="hw/data.js"></script>\n<script src="hw.js"></script>\n')
s = one(s, 'if (typeof STEPX !== "undefined") STEPX.register();', 'if (typeof STEPX !== "undefined") STEPX.register(); if (typeof HWX !== "undefined") HWX.register();')
s = one(s, "  ['ph', 'Phonics', 'الصوتيات', '', '#F0569C', '#C92671', 'dept', 1],",
        "  ['hw', 'Cursive Handwriting', 'الخط المتصل', 'Watch · Trace · Write · 77 pages', '#F2994A', '#D9480F', 'hw', 0],\n  ['ph', 'Phonics', 'الصوتيات', '', '#F0569C', '#C92671', 'dept', 1],")
s = one(s, "  ph: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><text",
        "  hw: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M3 17c3-6 5-9 6.5-9S11 10 9 13s-1 5 1 4 3-4 4.5-4 0 4 1.5 4S19 15 21 13\"/><path d=\"M3 21h18\"/></svg>',\n  ph: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><text")
s = one(s, "  ph: ['Phonics will teach you",
        "  hw: ['This department teaches you joined (cursive) handwriting, following the school cursive booklet: every capital and small letter, the common letter joins, and words for each letter. Each item has three steps. First watch the app write it, with a green dot where you start and arrows for the direction. Then trace over the model. Then write it alone on the lines. After each try the app shows your score, the parts you wrote correctly in green and the parts to fix in red.',\n"
        "    'هذا القسم يعلّمك الخط المتصل وفق كتيّب الخط المتصل في المدرسة: كل الحروف الكبيرة والصغيرة، ووصلات الحروف الشائعة، وكلمات لكل حرف. لكل عنصر ثلاث خطوات: شاهد التطبيق وهو يكتب، مع نقطة خضراء لمكان البداية وأسهم للاتجاه، ثم تتبّع النموذج، ثم اكتبه وحدك على السطور. وبعد كل محاولة يعرض التطبيق درجتك، والأجزاء الصحيحة باللون الأخضر، والأجزاء التي تحتاج إلى تصحيح باللون الأحمر.',\n"
        "    ['1 · Watch', '2 · Trace', '3 · Write', 'Score and feedback']],\n  ph: ['Phonics will teach you")
s = one(s, "    if (v === 'stepmock' || v === 'stepbook') { go('step'); return true; }", "    if (v === 'stepmock' || v === 'stepbook') { go('step'); return true; }\n    if (v === 'hwp') { go('hw'); return true; }\n    if (v === 'hw') { go('home'); return true; }")
s = one(s, "'stepbook', 'steplesson', 'grade',", "'stepbook', 'steplesson', 'hw', 'grade',")
s = one(s, "(d[0] === 'step' && typeof STEPX !== 'undefined' ? STEPX.homeMeta() : '')", "(d[0] === 'step' && typeof STEPX !== 'undefined' ? STEPX.homeMeta() : d[0] === 'hw' && typeof HWX !== 'undefined' ? HWX.homeMeta() : '')")
s = one(s, ".depts.n5 .dept:nth-child(n+4){grid-column:span 6}}", ".depts.n5 .dept:nth-child(n+4){grid-column:span 6}.depts.n6 .dept{grid-column:span 4}}")
s = one(s, "const APP_VER = '1.12.2';", "const APP_VER = '1.13.0';")
open(p, 'w', encoding='utf-8').write(s)
for f, n in (('package.json', 1), ('package-lock.json', 2)):
    q = os.path.join(ROOT, f); t = open(q, encoding='utf-8').read(); assert t.count('"version": "1.12.2"') >= n; open(q, 'w', encoding='utf-8').write(t.replace('"version": "1.12.2"', '"version": "1.13.0"', n))
q = os.path.join(ROOT, 'tools', 'app', 'changelog.json'); cl = json.load(open(q, encoding='utf-8'))
cl = {'1.13.0': {'en': ['New department: Cursive Handwriting. 77 practice pages (letters A to Z, joined letters and words), each with three steps: Watch, Trace and Write.',
                         'The app shows where each letter starts and which way to go, then scores your tracing and your writing and marks correct parts in green and parts to fix in red.',
                         'The Arabic name of the Ghars department is corrected to «غرس».'],
                  'ar': ['قسم جديد: الخط المتصل. 77 صفحة تدريب (الحروف من A إلى Z والحروف الموصولة والكلمات)، ولكل عنصر ثلاث خطوات: شاهد، تتبّع، اكتب.',
                         'يوضّح التطبيق مكان بداية كل حرف واتجاه الكتابة، ثم يقيّم التتبّع والكتابة ويلوّن الأجزاء الصحيحة بالأخضر والأجزاء التي تحتاج إلى تصحيح بالأحمر.',
                         'تصحيح الاسم العربي لقسم Ghars إلى «غرس».']}, **cl}
open(q, 'w', encoding='utf-8').write(json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('patched 1.13.0')
