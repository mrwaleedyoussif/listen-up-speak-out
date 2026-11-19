#!/usr/bin/env python3
"""v1.15.0: three new "Soon" departments (IELTS, SAT, GAT Preparation), on top of the Ghars > Wordline move."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def one(s, a, b, n=1, where=''):
    assert s.count(a) == n, (where or a[:60], s.count(a)); return s.replace(a, b)
p = os.path.join(ROOT, 'www', 'index.html'); s = open(p, encoding='utf-8').read()
s = one(s, "  ['ghars', 'Ghars', 'غرس', 'Wordline · Cursive Handwriting', '#7CB518', '#3D7A0A', 'ghars', 0]\n];",
        "  ['ghars', 'Ghars', 'غرس', 'Wordline · Cursive Handwriting', '#7CB518', '#3D7A0A', 'ghars', 0],\n"
        "  ['ielts', 'IELTS Preparation', 'التحضير لاختبار IELTS', '', '#E0445C', '#A8233B', 'dept', 1],\n"
        "  ['sat', 'SAT Preparation', 'التحضير لاختبار SAT', '', '#3B82F6', '#1E40AF', 'dept', 1],\n"
        "  ['gat', 'GAT Preparation', 'التحضير لاختبار القدرات العامة', '', '#14B8A6', '#0F766E', 'dept', 1]\n];")
s = one(s, "  ghars: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M12 21v-9\"/>",
        "  ielts: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M3 12h18\"/><path d=\"M12 3c3 3 3 15 0 18\"/><path d=\"M12 3c-3 3-3 15 0 18\"/></svg>',\n"
        "  sat: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M6 3h9l4 4v14H6z\"/><path d=\"M15 3v4h4\"/><path d=\"m9 14 2 2 4-4\"/></svg>',\n"
        "  gat: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M9 18h6\"/><path d=\"M10 21h4\"/><path d=\"M12 3a6 6 0 0 0-4 10.500c.700.800 1 1.500 1 2.500h6c0-1 .300-1.700 1-2.500A6 6 0 0 0 12 3Z\"/></svg>',\n"
        "  ghars: '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M12 21v-9\"/>".replace('10.500c.700.800 1 1.500 1 2.500', '10.5c.7.8 1 1.5 1 2.5').replace('1 .300-1.700 1-2.500A6', '1 .3-1.700 1-2.5A6').replace('-1.700', '-1.7'))
s = one(s, "  ghars: ['Ghars brings two programmes together",
        "  ielts: ['IELTS Preparation will help you get ready for the IELTS test in its four skills: Listening, Reading, Writing and Speaking. Its lessons and practice tests will be added here.',\n"
        "    'قسم التحضير لاختبار IELTS سيساعدك على الاستعداد للاختبار في مهاراته الأربع: الاستماع والقراءة والكتابة والتحدث. وستُضاف دروسه واختباراته التدريبية هنا.', ['Listening', 'Reading', 'Writing', 'Speaking']],\n"
        "  sat: ['SAT Preparation will help you get ready for the Reading and Writing section of the SAT. Its lessons and practice questions will be added here.',\n"
        "    'قسم التحضير لاختبار SAT سيساعدك على الاستعداد لقسم القراءة والكتابة في الاختبار. وستُضاف دروسه وأسئلته التدريبية هنا.', []],\n"
        "  gat: ['GAT Preparation will help you get ready for the General Aptitude Test (GAT). Its lessons and practice questions will be added here.',\n"
        "    'قسم التحضير لاختبار القدرات العامة سيساعدك على الاستعداد للاختبار. وستُضاف دروسه وأسئلته التدريبية هنا.', []],\n"
        "  ghars: ['Ghars brings two programmes together")
s = one(s, ".depts-soon{grid-template-columns:repeat(3,1fr)}\n", ".depts-soon{grid-template-columns:repeat(4,1fr)}\n")
s = one(s, "Reading and Writing is marked “Soon”. Every department", "Reading and Writing, IELTS Preparation, SAT Preparation and GAT Preparation are marked “Soon”. Every department")
s = one(s, "const APP_VER = '1.14.1';", "const APP_VER = '1.15.0';")
open(p, 'w', encoding='utf-8').write(s)
for f, n in (('package.json', 1), ('package-lock.json', 2)):
    q = os.path.join(ROOT, f); t = open(q, encoding='utf-8').read(); assert t.count('"version": "1.14.1"') >= n; open(q, 'w', encoding='utf-8').write(t.replace('"version": "1.14.1"', '"version": "1.15.0"', n))
q = os.path.join(ROOT, 'tools', 'app', 'changelog.json'); cl = json.load(open(q, encoding='utf-8')); old = cl.pop('1.14.1')
cl = {'1.15.0': {'en': ['Three new departments marked “Soon”: IELTS Preparation, SAT Preparation and GAT Preparation.'] + old['en'],
                  'ar': ['ثلاثة أقسام جديدة بعلامة «قريبًا»: التحضير لاختبار IELTS، والتحضير لاختبار SAT، والتحضير لاختبار القدرات العامة.'] + old['ar']}, **cl}
open(q, 'w', encoding='utf-8').write(json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('patched 1.15.0')

# stale level names: the offline-audio list and the footer still said "Level 2–5" instead of A1, A1+, A2, A2+
q = os.path.join(ROOT, 'www', 'pwa.js'); t = open(q, encoding='utf-8').read()
if 'const LVN' not in t:
    t = one(t, "<b>Level ${g - 1}</b>", "<b>Level ${LVN(g)}</b>")
    t = one(t, "<h3>Remove Level ${b.dataset.dlr - 1} audio?</h3>", "<h3>Remove Level ${LVN(b.dataset.dlr)} audio?</h3>")
    t = "const LVN = g => { try { return lvs(+g); } catch (e) { return ({ 3: 'A1', 4: 'A1+', 5: 'A2', 6: 'A2+' })[+g] || (+g - 1); } };   // the level's name, as in the rest of the app\n" + t
    open(q, 'w', encoding='utf-8').write(t)
s = open(p, encoding='utf-8').read()
if 'Listening and Speaking Levels 2–5' in s:
    s = one(s, "Listening and Speaking Levels 2–5 · Shadowing · MAP", "Listening and Speaking Levels A1–A2+ · Shadowing · MAP"); open(p, 'w', encoding='utf-8').write(s)
