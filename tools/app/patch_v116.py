#!/usr/bin/env python3
"""v1.16.0: Reading and Writing department. The data comes from tools/app/build_rw.py; this patch teaches the department
page (www/gv, until now Language Usage only) to serve two departments, chosen by ?d=rw, and opens the home card.
Run after tools/app/add_gv.py if that is ever run again."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def one(s, a, b, n=1, where=''):
    assert s.count(a) == n, (where or a[:70], s.count(a)); return s.replace(a, b)
R = lambda *p: os.path.join(ROOT, *p)
rd = lambda p: open(p, encoding='utf-8').read()
def wr(p, s): open(p, 'w', encoding='utf-8', newline='\n').write(s)

# ---- department page: views
p = R('www', 'gv', 'js', 'views.js'); s = rd(p)
s = one(s, "  let strands = null;\n", """  /* one page, two departments: Language Usage (default) and Reading and Writing (?d=rw) */
  const RW = /[?&]d=rw\\b/.test(location.search);
  const DEPT = RW ? { sid: 'reading_writing', name: 'Reading and Writing', line: 'Levels A1 to B2 • 47 units • 235 lessons', line_ar: 'القراءة والكتابة – من المستوى A1 إلى المستوى B2',
    tag: 'Levels A1 → B2', card: '8 levels • 47 units • 235 lessons', hero: 'Word power • close reading • reading strategies • writing skills • writing workshop', placement: false }
    : { sid: 'grammar_vocabulary', name: 'Language Usage', line: 'Levels A1 to C2 • 72 units • 360 lessons', line_ar: 'استخدام اللغة – من المستوى A1 إلى المستوى C2',
      tag: 'Levels A1 → C2', card: '12 levels • 72 units • 360 lessons', hero: 'Language Usage • MAP-style items at every level • SAT-style items from Level 8', placement: true };
  let strands = null;
""")
s = one(s, "if (!strands) strands = await P.load('data/strands.json'); return strands; }", "if (!strands) { strands = await P.load('data/strands.json'); strands.forEach(x => { x.enabled = x.enabled && x.id === DEPT.sid; }); } return strands; }")
s = one(s, "      el('h1', null, 'Language Usage'),\n      el('p', null, 'Levels A1 to C2 • 72 units • 360 lessons'),\n      P.ar('استخدام اللغة – من المستوى A1 إلى المستوى C2')));",
        "      el('h1', null, DEPT.name),\n      el('p', null, DEPT.line),\n      P.ar(DEPT.line_ar)));")
s = one(s, "    view.appendChild(el('section', { class: 'panel intro' }, el('span', { class: 'in-k' }, 'Introduction ',", """    if (RW) view.appendChild(el('section', { class: 'panel intro' }, el('span', { class: 'in-k' }, 'Introduction ', el('span', { class: 'ar', lang: 'ar' }, 'مقدمة')),
      el('p', null, 'This department takes you from short, simple texts to clear writing of your own. Every unit has five lessons: the new words, a close reading of the main text, a reading strategy with a second text, a writing skill, and a writing workshop where you plan, write and improve your own piece. Levels A1 to B2 are open; the higher levels are coming soon.'),
      P.ar('هذا القسم يأخذك من النصوص القصيرة البسيطة إلى كتابة واضحة بقلمك. في كل وحدة خمسة دروس: الكلمات الجديدة، ثم قراءة متأنية للنص الرئيس، ثم استراتيجية قراءة مع نص ثانٍ، ثم مهارة كتابية، ثم ورشة كتابة تخطط فيها وتكتب وتحسّن نصك. المستويات من A1 إلى B2 متاحة، والمستويات الأعلى قريبًا.'),
      el('ul', { class: 'in-pts' }, ['Read and understand', 'Find the evidence', 'Plan, write and improve'].map(x => el('li', null, x)))));
    else view.appendChild(el('section', { class: 'panel intro' }, el('span', { class: 'in-k' }, 'Introduction ',""")
s = one(s, "el('span', { class: 'tag' }, 'Levels A1 → C2'), el('div', { class: 'big' }, 'All levels and units')", "el('span', { class: 'tag' }, DEPT.tag), el('div', { class: 'big' }, 'All levels and units')")
s = one(s, "s.enabled ? '12 levels • 72 units • 360 lessons' :", "s.enabled ? DEPT.card :")
s = one(s, "      el('a', { class: 'card', href: base('grammar_vocabulary') + '/placement' }, el('div', { class: 'big' }, '🧭 Placement Test')", "      !DEPT.placement ? null : el('a', { class: 'card', href: base('grammar_vocabulary') + '/placement' }, el('div', { class: 'big' }, '🧭 Placement Test')")
s = one(s, "el('p', null, 'Language Usage • MAP-style items at every level • SAT-style items from Level 8')", "el('p', null, DEPT.hero)")
s = one(s, "      const d = levelDone(I, L.level);\n      g.appendChild(el('a', { class: 'card', href: base(sid) + '/L' + L.level },",
        "      const d = levelDone(I, L.level);\n      if (!L.units.length) { g.appendChild(el('div', { class: 'card', style: { opacity: '.6' } }, el('span', { class: 'tag' }, 'Soon · قريبًا'), el('div', { class: 'big' }, P.lvs(L.level)), el('div', { class: 'sub' }, 'This level is being prepared.'))); return; }\n      g.appendChild(el('a', { class: 'card', href: base(sid) + '/L' + L.level },")
s = one(s, "bar(d, 30), el('div', { class: 'sub' }, d + ' / 30 lessons')));\n    });\n    view.append(g, el('div', { class: 'row', style: { marginTop: '16px' } }, el('a', { class: 'btn alt', href: base(sid) + '/placement' }, '🧭 Placement Test')));",
        "bar(d, L.units.length * 5), el('div', { class: 'sub' }, d + ' / ' + L.units.length * 5 + ' lessons')));\n    });\n    view.append(g); if (DEPT.placement) view.append(el('div', { class: 'row', style: { marginTop: '16px' } }, el('a', { class: 'btn alt', href: base(sid) + '/placement' }, '🧭 Placement Test')));")
s = one(s, "const I = await getIndex('grammar_vocabulary');\n      const g = el('div', { class: 'grid' });\n      I.levels.forEach(L => { const d = levelDone(I, L.level); g.appendChild(el('a', { class: 'card', href: base('grammar_vocabulary') + '/L' + L.level }",
        "const I = await getIndex(DEPT.sid);\n      const g = el('div', { class: 'grid' });\n      I.levels.filter(L => L.units.length).forEach(L => { const d = levelDone(I, L.level); g.appendChild(el('a', { class: 'card', href: base(DEPT.sid) + '/L' + L.level }")
s = one(s, "view.append(el('h2', null, 'Language Usage'), g);", "view.append(el('h2', null, DEPT.name), g);")
s = one(s, "P.renderQuiz(J.unit_test, { onSubmit:", "P.renderQuiz(J.unit_test, { writing: J.unit_writing, onSubmit:")
wr(p, s)
p = R('www', 'gv', 'js', 'activities.js'); s = rd(p)
s = one(s, "el('h2', null, 'Writing (10 marks)')", "el('h2', null, 'Writing (' + (opts.writing.marks || 10) + ' marks)')"); wr(p, s)
p = R('www', 'gv', 'js', 'rw.js'); s = rd(p)
if "if (RWD)" not in s:
    s = one(s, "  ['open', 'organizer', 'writing'].forEach(t =>", "  const RWD = /[?&]d=rw\\b/.test(location.search);   // 'open' keeps its own behaviour in Language Usage\n  (RWD ? ['open', 'organizer', 'writing'] : ['organizer', 'writing']).forEach(t =>"); wr(p, s)
p = R('www', 'gv', 'index.html'); s = rd(p)
s = one(s, '<script src="js/activities.js"></script>\n', '<script src="js/activities.js"></script>\n<script src="js/rw.js"></script>\n'); wr(p, s)
p = R('www', 'gv', 'host.js'); s = rd(p)
s = one(s, "  document.addEventListener('DOMContentLoaded', function () {\n", """  document.addEventListener('DOMContentLoaded', function () {
    if (/[?&]d=rw\\b/.test(location.search)) {   // the same page serves the Reading and Writing department
      document.title = 'From Zero To Hero – Reading and Writing';
      var b = document.querySelector('.brand b'); if (b) b.textContent = 'Reading and Writing';
      var f = document.querySelector('footer.foot'); if (f) f.textContent = f.textContent.replace('Language Usage', 'Reading and Writing');
    }
"""); wr(p, s)

# ---- offline: unit files of both departments are saved the first time each one is opened
p = R('tools', 'app', 'sw.template.js'); s = rd(p)
s = one(s, "/\\/gv\\/data\\/grammar_vocabulary\\/(units|tests)\\//", "/\\/gv\\/data\\/(grammar_vocabulary|reading_writing)\\/(units|tests)\\//"); wr(p, s)
p = R('tools', 'app', 'build_www.py'); s = rd(p)
s = one(s, "'gv/data/grammar_vocabulary/tests/', 'ph/pg/'))", "'gv/data/grammar_vocabulary/tests/', 'gv/data/reading_writing/units/', 'ph/pg/'))"); wr(p, s)

# ---- main app
p = R('www', 'index.html'); s = rd(p)
s = one(s, "  ['rw', 'Reading and Writing', 'القراءة والكتابة', '', '#F59E0B', '#EA5B0C', 'dept', 1],", "  ['rw', 'Reading and Writing', 'القراءة والكتابة', 'Levels A1 → B2 · 235 lessons', '#F59E0B', '#EA5B0C', 'rwx', 0],")
s = one(s, "    if (d[6] === 'gvx') { AU.stop(); Store.save(); location.href = 'gv/index.html'; return; }", "    if (d[6] === 'gvx' || d[6] === 'rwx') { AU.stop(); Store.save(); location.href = d[6] === 'rwx' ? 'gv/index.html?d=rw' : 'gv/index.html'; return; }")
a = s.index("  rw: ['Reading and Writing will take you"); b = s.index("]],", a) + 3
s = s[:a] + ("  rw: ['Reading and Writing takes you from short, simple texts to clear writing of your own. Every unit has five lessons: new words, close reading, a reading strategy, a writing skill and a writing workshop. Levels A1 to B2 are open; the higher levels are coming soon.',\n"
             "    'قسم القراءة والكتابة يأخذك من النصوص القصيرة البسيطة إلى كتابة واضحة بقلمك. في كل وحدة خمسة دروس: كلمات جديدة، قراءة متأنية، استراتيجية قراءة، مهارة كتابية، وورشة كتابة. المستويات من A1 إلى B2 متاحة، والمستويات الأعلى قريبًا.',\n"
             "    ['Read and understand', 'Find the evidence', 'Plan, write and improve']],") + s[b:]
s = one(s, ".depts.n7 .dept h3{font-size:1.32rem}}", ".depts.n7 .dept h3{font-size:1.32rem}.depts.n8 .dept{grid-column:span 3}.depts.n8 .dept h3{font-size:1.32rem}}")
s = one(s, ".depts-soon{grid-template-columns:repeat(4,1fr)}\n", ".depts-soon{grid-template-columns:repeat(3,1fr)}\n")
s = one(s, "Language Usage (Levels A1 to C2), STEP Preparation (4 Foundation booklets and 30 mock exams)", "Language Usage (Levels A1 to C2), Reading and Writing (Levels A1 to B2; higher levels are marked “Soon”), STEP Preparation (4 Foundation booklets and 30 mock exams)")
s = one(s, "Reading and Writing, IELTS Preparation, SAT Preparation and GAT Preparation are marked “Soon”.", "IELTS Preparation, SAT Preparation and GAT Preparation are marked “Soon”.")
s = one(s, "const APP_VER = '1.15.0';", "const APP_VER = '1.16.0';"); wr(p, s)
for f, n in (('package.json', 1), ('package-lock.json', 2)):
    t = rd(R(f)); assert t.count('"version": "1.15.0"') >= n; wr(R(f), t.replace('"version": "1.15.0"', '"version": "1.16.0"', n))
q = R('tools', 'app', 'changelog.json'); cl = json.load(open(q, encoding='utf-8'))
cl = {'1.16.0': {'en': ['Reading and Writing is open: Levels A1 to B2 (47 units, 235 lessons). Every unit has new words, close reading, a reading strategy, a writing skill and a writing workshop, plus a unit test.',
                         'New activities: find the evidence by tapping the sentence in the text, timed reading with words per minute, put the parts in order, and writing with a word count, a checklist and a model answer.',
                         'The higher levels of Reading and Writing are marked “Soon”.'],
                  'ar': ['قسم القراءة والكتابة متاح الآن: المستويات من A1 إلى B2 (47 وحدة و235 درسًا). في كل وحدة كلمات جديدة وقراءة متأنية واستراتيجية قراءة ومهارة كتابية وورشة كتابة، مع اختبار للوحدة.',
                         'أنشطة جديدة: إيجاد الدليل بالضغط على الجملة في النص، والقراءة الموقوتة مع عدد الكلمات في الدقيقة، وترتيب الأجزاء، والكتابة مع عدّاد كلمات وقائمة تحقق وإجابة نموذجية.',
                         'المستويات الأعلى في القراءة والكتابة عليها علامة «قريبًا».']}, **cl}
wr(q, json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('patched 1.16.0')

# ---- second part: fixes found while testing Reading and Writing on the department page
p = R('www', 'gv', 'js', 'views.js'); s = rd(p)
if 'LS_RW' not in s:
    s = one(s, "      if (U.unit === 3) g.appendChild(testCard('MID'));\n      if (U.unit === 6) g.appendChild(testCard('END'));", "      [[3, 'MID'], [6, 'END']].forEach(([k, kind]) => { const c = U.unit === k && testCard(kind); if (c) g.appendChild(c); });")
    s = one(s, "J.can_do.replace(/^I can /, ''), P.ar(J.can_do_ar)) : null);", "J.can_do.replace(/^I can /, ''), P.ar(J.can_do_ar)) : '');")
    s = one(s, "  const LS_NAMES = { 1: 'Grammar discovery', 2: 'Grammar practice', 3: 'Vocabulary in depth', 4: 'Mechanics & editing', 5: 'Language in use & review' };\n  const LS_AR = { 1: 'اكتشاف القاعدة', 2: 'تدريب على القاعدة', 3: 'المفردات بعمق', 4: 'الترقيم والتحرير', 5: 'استخدام اللغة والمراجعة' };",
            "  const LS_RW = /[?&]d=rw\\b/.test(location.search);   // the five lessons of a unit are named by department\n  const LS_NAMES = LS_RW ? { 1: 'Word power', 2: 'Close reading', 3: 'Reading strategy', 4: 'Writing skill', 5: 'Writing workshop' } : { 1: 'Grammar discovery', 2: 'Grammar practice', 3: 'Vocabulary in depth', 4: 'Mechanics & editing', 5: 'Language in use & review' };\n  const LS_AR = LS_RW ? { 1: 'قوة الكلمات', 2: 'القراءة المتأنية', 3: 'استراتيجية القراءة', 4: 'مهارة كتابية', 5: 'ورشة الكتابة' } : { 1: 'اكتشاف القاعدة', 2: 'تدريب على القاعدة', 3: 'المفردات بعمق', 4: 'الترقيم والتحرير', 5: 'استخدام اللغة والمراجعة' };")
    s = one(s, "el('b', null, P.lv(L.level)), bar(d, 30), el('div', { class: 'sub' }, d + ' / 30 less", "el('b', null, P.lv(L.level)), bar(d, L.units.length * 5), el('div', { class: 'sub' }, d + ' / ' + L.units.length * 5 + ' less")
    wr(p, s)

# ---- third part: the lesson's text is also at hand on the Practice tab (the questions are about it)
p = R('www', 'gv', 'js', 'views.js'); s = rd(p)
if 'Read the text again' not in s:
    s = one(s, "    if (tab === 'practice') {\n      const p = el('div', { class: 'panel' });", "    if (tab === 'practice') {\n      const p = el('div', { class: 'panel' });\n      L.texts.forEach((t, i) => p.appendChild(el('details', { class: 'box sky', open: i === 0 && L.texts.length === 1 ? '' : null, style: { marginBottom: '12px' } }, el('summary', null, el('b', null, '📖 Read the text again: ' + t.title)), el('div', { class: 'pre', style: { fontSize: '1.05rem', marginTop: '8px' } }, t.body))));")
    wr(p, s)
