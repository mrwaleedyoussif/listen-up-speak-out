"""v1.11.0
  * Grammar and Vocabulary department opens (www/gv, added by tools/app/add_gv.py).
  * Level names A1, A1+, A2, A2+, B1, B1+, B2, B2+, C1, C2 in the whole app; levels without lessons show "Soon".
  * MAP Test: practice is grouped in RIT units inside each grade (data regrouped by tools/app/build_map_data.py).
  * Animated reactions for right and wrong answers (www/fx.js) with a brighter right sound and a kinder wrong sound.
Run once:  python3 tools/app/patch_v111.py"""
import os, json
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda p: open(p, encoding='utf-8').read()
wr = lambda p, s: open(p, 'w', encoding='utf-8').write(s)


def one(s, a, b, n=1, where=''):
    c = s.count(a)
    assert c == n, f'{where}: expected {n} x {a[:90]!r}, found {c}'
    return s.replace(a, b)


# ======================================================================= index.html
W = 'index.html'; p = P('www', 'index.html'); s = rd(p)

# --- shared reactions script
s = one(s, '<script src="sfx/reactions.js"></script>\n', '<script src="sfx/reactions.js"></script>\n<script src="fx.js"></script>\n', 1, W)

# --- reactions: animation with every right / wrong answer, brighter right sound, kinder wrong sound
s = one(s, "    if (kind === 'right') { this.bell(1046.5, 0, 0.32, 0.15); this.bell(1568, 0.1, 0.55, 0.15); }\n    else if (kind === 'wrong') { this.tone(330, 0, 0.2, { type: 'triangle', v: 0.17, to: 290 }); this.tone(247, 0.18, 0.34, { type: 'triangle', v: 0.17, to: 208 }); }",
        "    if (kind === 'right') {           // a bright rising chime with a sparkle\n      [1046.5, 1318.5, 1568].forEach((f, i) => this.bell(f, i * 0.08, 0.42, 0.14));\n      for (let i = 0; i < 6; i++) this.tone(2000 + Math.random() * 2200, 0.3 + i * 0.06, 0.13, { v: 0.04 });\n    }\n    else if (kind === 'wrong') {      // soft and kind: two gentle notes, then one that rises (\"try again\")\n      this.tone(349.23, 0, 0.18, { type: 'triangle', v: 0.15 }); this.tone(293.66, 0.16, 0.2, { type: 'triangle', v: 0.15 }); this.tone(440, 0.38, 0.42, { type: 'triangle', v: 0.14 });\n    }", 1, W)
s = one(s, "  async answer(ok) { if (!this.on()) return; AU.stop(); this.sfx(ok ? 'right' : 'wrong'); await sleep(ok ? 280 : 420); await this.say(ok ? 'right' : 'wrong'); },\n  async praise() { if (!this.on()) return; this.sfx('right'); await sleep(280); await this.say('right'); },\n  async encourage() { if (!this.on()) return; this.sfx('try'); await sleep(450); await this.say('try'); },",
        "  // the animated reaction (fx.js) shows the same words that are spoken\n  show(ok, kind, i) { const L = window.LSP_RX && window.LSP_RX[kind]; if (window.Cheer) Cheer.show(ok, L && i >= 0 && L[i] ? L[i].t : null); },\n  async answer(ok) { const k = ok ? 'right' : 'wrong', i = this.pick(k); this.show(ok, k, i); if (!this.on()) return; AU.stop(); this.sfx(k); await sleep(ok ? 280 : 420); await this.say(k, i); },\n  async praise() { const i = this.pick('right'); this.show(true, 'right', i); if (!this.on()) return; this.sfx('right'); await sleep(280); await this.say('right', i); },\n  async encourage() { const i = this.pick('try'); this.show(false, 'try', i); if (!this.on()) return; this.sfx('try'); await sleep(450); await this.say('try', i); },", 1, W)

# --- level names
s = one(s, "const lv = g => 'Level ' + (g - 1);                  // Listening and Speaking levels: the four sets are Level 2 … Level 5",
        "const lvs = g => G(g).level;                          // level names: A1, A1+, A2, A2+ (the four sets of Listening and Speaking)\nconst lv = g => 'Level ' + lvs(g);\nconst SOON_LV = ['B1', 'B1+', 'B2', 'B2+', 'C1', 'C2'];   // levels of the scale that have no lessons yet", 1, W)
s = one(s, "'Levels 2–5 · CEFR A1 → A2+', '#2F9BF0'", "'Levels A1 → A2+ · B1 → C2 soon', '#2F9BF0'", 1, W)
s = one(s, "Start with Level 2 and move up one level at a time.", "Start with Level A1 and move up one level at a time.", 1, W)
s = one(s, "ابدأ بالمستوى 2 ثم انتقل مستوى بعد مستوى.", "ابدأ بالمستوى A1 ثم انتقل مستوى بعد مستوى.", 1, W)
s = one(s, "['5 steps', 'Levels 2–5', 'Daily 5: five lines for today']", "['5 steps', 'Levels A1 → A2+', 'Daily 5: five lines for today']", 1, W)
s = one(s, '<span class="k">Department · Levels 2–5 · CEFR A1 → A2+</span>', '<span class="k">Department · Levels A1 → C2</span>', 1, W)
s = one(s, """        <span class="lv">${esc(b.name)} · CEFR ${esc(gr.level)}</span>
        <h3>${lv(gr.grade)}</h3>""", """        <span class="lv">${esc(b.name)}</span>
        <h3>${lv(gr.grade)}</h3>""", 1, W)
s = one(s, """        <span class="meta">${s.done}/${s.total} lessons · ★ ${s.stars}</span>
      </button>`; }).join('')}
  </section>`;""", """        <span class="meta">${s.done}/${s.total} lessons · ★ ${s.stars}</span>
      </button>`; }).join('')}
    ${SOON_LV.map(n => `<div class="gcard soonlv"><span class="d-soon"><i></i>Soon · قريبًا</span><span class="em">🔒</span><span class="lv">Coming soon</span><h3>Level ${n}</h3><span class="meta">Lessons for this level are being prepared. <span class="ar" style="color:inherit">دروس هذا المستوى قيد الإعداد.</span></span></div>`).join('')}
  </section>`;""", 1, W)
s = one(s, '<span class="k">${esc(b.name)} · CEFR ${esc(gr.level)}</span><h1>${lv(S.g)}: 6 units</h1>', '<span class="k">${esc(b.name)}</span><h1>${lv(S.g)}: 6 units</h1>', 1, W)
s = one(s, "(Listening and Speaking, ${esc(b.name)}, CEFR ${esc(G(S.g).level)})", "(Listening and Speaking, ${esc(b.name)})", 1, W)
s = one(s, "on by default in Levels 2–3 and off in Levels 4–5.", "on by default in Levels A1 and A1+ and off in Levels A2 and A2+.", 1, W)
s = one(s, "Listening and Speaking (Levels 2–5), Shadowing or MAP Test. Reading and Writing, Grammar and Vocabulary, STEP Preparation,",
        "Listening and Speaking (Levels A1 to A2+; B1 to C2 are marked “Soon”), Shadowing, MAP Test or Grammar and Vocabulary (Levels A1 to C2). Reading and Writing, STEP Preparation,", 1, W)
s = one(s, "Listening and Speaking (Levels 2–5), Shadowing and MAP test practice (Grades 3–9)", "Listening and Speaking, Shadowing, Grammar and Vocabulary (Levels A1 to C2) and MAP test practice (Grades 3–9)", 1, W)
s = one(s, """>${lv(x.grade)}</button>`).join('')}</div>""", """>${lvs(x.grade)}</button>`).join('')}</div> <span class="pill soonnote" title="These levels have no lessons yet">B1 · B1+ · B2 · B2+ · C1 · C2: Soon · قريبًا</span>""", 1, W)

# --- Grammar and Vocabulary is open: its card leaves the Soon row and opens the department
s = one(s, "['gv', 'Grammar and Vocabulary', 'القواعد والمفردات', '', '#9B6CF6', '#6D3BE0', 'dept', 1],", "['gv', 'Grammar and Vocabulary', 'القواعد والمفردات', 'Levels A1 → C2 · 360 lessons', '#9B6CF6', '#6D3BE0', 'gvx', 0],", 1, W)
s = one(s, "    go(d[6], d[6] === 'dept' ? { dp: d[0] } : {});", "    if (d[6] === 'gvx') { AU.stop(); Store.save(); location.href = 'gv/index.html'; return; }   // Grammar and Vocabulary has its own page\n    go(d[6], d[6] === 'dept' ? { dp: d[0] } : {});", 1, W)
s = one(s, '<section class="depts">${open.map(', '<section class="depts n${open.length}">${open.map(', 1, W)

CSS = """
/* ===== v1.11: four open departments, Soon levels ===== */
@media (min-width:1001px){.depts.n4 .dept{grid-column:span 3}.depts.n4 .dept h3{font-size:1.32rem}}
.depts-soon{grid-template-columns:repeat(4,1fr)}
@media (max-width:1000px){.depts-soon{grid-template-columns:repeat(2,1fr)}}
.gcard.soonlv{background:linear-gradient(135deg,#8D97B4,#5C6787);cursor:default;min-height:150px;--b:#5C6787}
.gcard.soonlv .em{display:none}
.gcard.soonlv .meta{font-size:.86rem;opacity:.95}
.soonnote{margin-left:8px;background:#EEF0F7;color:#4B5574;font-weight:800}
"""
anchor = "@media (prefers-reduced-motion:reduce){.lg,.lg-f,.lg-f::before,.lg-sheen,.bye img{animation:none!important}.brand .b-lg{transition:none}}\n"
s = one(s, anchor, anchor + CSS.lstrip('\n'), 1, W)
s = one(s, "work through the practice units, then sit a full mock exam", "work through the RIT units that match your score, then sit a full mock exam", 1, W)
s = one(s, "['Reading and Language Usage', 'Grades 3–9', 'Practice units and full mock exams']", "['Reading and Language Usage', 'Grades 3–9', 'RIT units and full mock exams']", 1, W)
s = one(s, "const APP_VER = '1.10.2';", "const APP_VER = '1.11.0';", 1, W)
wr(p, s)

# ======================================================================= map.js: RIT units
W = 'map.js'; p = P('www', 'map.js'); s = rd(p)
s = one(s, "  const prog = (p, id) => ((p || Store.me()).progress || {})[id] || null;",
        "  const prog = (p, id) => ((p || Store.me()).progress || {})[id] || null;\n  /* RIT units, practices and questions in a grade (from map/index.js) */\n  const CNT = (subj, g) => (window.MAP_COUNTS || {})[subj + '_' + g] || { u: 0, s: 12, q: 78 };\n  const gname = k => (GOALS[k] || [''])[0];", 1, W)
s = one(s, "const setRow = (u, s) => { const id = u.id + s.set,", "const setRow = (u, s) => { const id = u.id + '-' + s.set,", 1, W)
s = one(s, """<span class="ic">${s.set === 'A' ? '📝' : '🧠'}</span><span class="tx"><small>Practice ${s.set} · ${s.items.length} questions</small>""",
        """<span class="ic">${(GOALS[s.goal] || [])[2] || '📝'}</span><span class="tx"><small>Practice ${s.set} · ${s.items.length} question${s.items.length > 1 ? 's' : ''}${gname(s.goal) ? ' · ' + esc(gname(s.goal)) : ''}</small>""", 1, W)
s = one(s, """<p style="margin:.3rem 0 0;opacity:.95">6 practice units (78 questions) and 5 full mock exams (43 questions each), ordered from easier to harder.</p>
      <span class="ar ar-block">6 وحدات تدريب و5 اختبارات تجريبية كاملة، مرتبة من الأسهل إلى الأصعب.</span></section>""",
        """<p style="margin:.3rem 0 0;opacity:.95">${d.units.length} RIT units (${CNT(subj, g).q} practice questions) and 5 full mock exams (43 questions each). Every RIT unit covers 10 RIT points: RIT 1 is 151–160, RIT 2 is 161–170, and so on. Start with the unit that holds your own RIT score, then move up.</p>
      <span class="ar ar-block">${d.units.length} وحدات RIT للتدريب و5 اختبارات تجريبية كاملة. كل وحدة تغطي 10 نقاط: RIT 1 من 151 إلى 160، و RIT 2 من 161 إلى 170، وهكذا. ابدأ بالوحدة التي تضم درجتك ثم انتقل إلى الأعلى.</span></section>""", 1, W)
s = one(s, '<h2>📘 Practice units</h2>', '<h2>📈 RIT units</h2>', 1, W)
s = one(s, """<span class="pill">${esc(u.id.replace('U', 'Unit '))} · ${esc(G[0] || u.goal)}</span><h3>${esc(u.title)}</h3><span class="muted" style="font-size:.85rem">RIT ${esc(u.band)}</span>""",
        """<span class="pill">RIT ${u.n}</span><h3>From ${esc(u.band.replace('–', ' to '))}</h3><span class="muted" style="font-size:.85rem">${(n => n + ' question' + (n > 1 ? 's' : ''))(u.sets.reduce((a, x) => a + x.items.length, 0))} in ${u.sets.length} practice${u.sets.length > 1 ? 's' : ''}</span>""", 1, W)
s = one(s, "const G = GOALS[u.goal] || ['', '', '📘'];", "const G = GOALS[u.goal] || ['', '', '📈'];", 1, W)
s = one(s, "const id = pkey(subj, g, u.id + set.set), items = set.items, G = GOALS[u.goal] || ['', '', ''];", "const id = pkey(subj, g, u.id + '-' + set.set), items = set.items, G = GOALS[set.goal] || ['', '', ''];", 1, W)
s = one(s, "const parts = crumbsTo(g, `${u.id.replace('U', 'Unit ')} · Practice ${set.set}`);", "const parts = crumbsTo(g, `RIT ${u.n} · Practice ${set.set}`);", 1, W)
s = one(s, """<span class="k">Grade ${g} · ${esc(u.id.replace('U', 'Unit '))} · Practice ${set.set} · ${esc(G[0])}</span><h1>${esc(u.title)}</h1>
      <p style="margin:.3rem 0 0;opacity:.95">${esc(u.skills.join(' · '))}</p></section>""",
        """<span class="k">Grade ${g} · Practice ${set.set}${G[0] ? ' · ' + esc(G[0]) : ''}</span><h1>RIT ${u.n} <span style="font-size:.7em;opacity:.92">· ${esc(u.band)}</span></h1>
      <p style="margin:.3rem 0 0;opacity:.95">${esc([...new Set(items.map(x => x.sk))].join(' · '))}</p></section>""", 1, W)
s = one(s, "if (/^U\\d[AB]$/.test(id) && v.done) { sets++;", "if (/^R\\d+-\\d+$/.test(id) && v.done) { sets++;", 1, W)
s = one(s, "6 units · 5 mock exams</span>", "${CNT(subj, g).u} RIT units · 5 mock exams</span>", 1, W)
s = one(s, "Math.round(100 * (s.sets + s.mocks) / 17)", "Math.round(100 * (s.sets + s.mocks) / (CNT(subj, g).s + 5))", 1, W)
s = one(s, "`${s.sets}/12 practice sets · ${s.mocks}/5 mocks", "`${s.sets}/${CNT(subj, g).s} practices · ${s.mocks}/5 mocks", 1, W)
s = one(s, "· ${s.sets}/12 sets${s.setAvg", "· ${s.sets}/${CNT(subj, g).s} practices${s.setAvg", 1, W)
s = one(s, "Practice sets done (of 12),", "Practices done,", 1, W)
wr(p, s)

# ======================================================================= service worker and build list
W = 'sw.template.js'; p = P('tools', 'app', 'sw.template.js'); s = rd(p)
s = one(s, "const SHELL = 'lsp-shell-' + V, AUDIO = 'lsp-audio-' + AV;", "const SHELL = 'lsp-shell-' + V, AUDIO = 'lsp-audio-' + AV, GVDATA = 'lsp-gvdata-1';   // Grammar and Vocabulary lessons: saved the first time each one is opened", 1, W)
s = one(s, "if (k.startsWith('lsp-') && k !== SHELL && k !== AUDIO) await caches.delete(k);", "if (k.startsWith('lsp-') && k !== SHELL && k !== AUDIO && k !== GVDATA) await caches.delete(k);", 1, W)
s = one(s, "  if (u.pathname.endsWith('.mp3')) { e.respondWith(audio(r)); return; }", "  if (u.pathname.endsWith('.mp3')) { e.respondWith(audio(r)); return; }\n  if (/\\/gv\\/data\\/grammar_vocabulary\\/(units|tests)\\//.test(u.pathname)) { e.respondWith(lazy(r)); return; }", 1, W)
s = one(s, "    const page = await c.match('index.html');", "    const page = await c.match(/\\/gv\\//.test(new URL(r.url).pathname) ? 'gv/index.html' : 'index.html');   // the Grammar and Vocabulary department has its own page", 1, W)
s = one(s, "/* Audio: cache first.", "/* Grammar and Vocabulary unit and test files: cache first, saved on first use. */\nasync function lazy(r) {\n  const c = await caches.open(GVDATA);\n  const hit = await c.match(r.url);\n  if (hit) return hit;\n  try { const res = await fetch(r.url); if (res.status === 200) { try { await c.put(r.url, res.clone()); } catch (e) {} } return res; } catch (e) { return Response.error(); }\n}\n\n/* Audio: cache first.", 1, W)
wr(p, s)
W = 'build_www.py'; p = P('tools', 'app', 'build_www.py'); s = rd(p)
s = one(s, "r.startswith(('icons/shots/', 'print/'))", "r.startswith(('icons/shots/', 'print/', 'gv/data/grammar_vocabulary/units/', 'gv/data/grammar_vocabulary/tests/'))", 1, W)
wr(p, s)

# ======================================================================= texts, version, changelog
t = rd(P('www', 'manifest.webmanifest'))
wr(P('www', 'manifest.webmanifest'), one(t, "Listening and Speaking (Levels 2–5), Shadowing and MAP test practice", "Listening and Speaking, Shadowing, Grammar and Vocabulary (Levels A1 to C2) and MAP test practice", 1, 'manifest'))
t = rd(P('package.json')); wr(P('package.json'), one(t, '"version": "1.10.2"', '"version": "1.11.0"', 1, 'package.json'))
t = rd(P('package-lock.json')); assert t.count('"version": "1.10.2"') >= 2
wr(P('package-lock.json'), t.replace('"version": "1.10.2"', '"version": "1.11.0"', 2))
cl = json.loads(rd(P('tools', 'app', 'changelog.json'))); assert '1.11.0' not in cl
cl = {'1.11.0': {
    'en': ['New department: Grammar and Vocabulary is open, with 12 steps from A1 to C2 (72 units, 360 lessons), games, exit quizzes, unit and level tests, a placement test and Word Cards.',
           'Levels are now named A1, A1+, A2, A2+, B1, B1+, B2, B2+, C1 and C2 in the whole app. Levels that have no lessons yet are marked “Soon”.',
           'MAP Test: practice is now grouped in RIT units inside each grade (RIT 1 is 151–160, RIT 2 is 161–170, and so on). Mock exams are unchanged. Practice results saved under the old units start again.',
           'Right answers get an animated cheer with a bright sound; wrong answers get a kind “try again” with a gentle sound.'],
    'ar': ['قسم جديد: القواعد والمفردات مفتوح الآن، في 12 مرحلة من A1 إلى C2 (72 وحدة و360 درسًا) مع ألعاب واختبارات قصيرة واختبارات للوحدات والمستويات واختبار تحديد المستوى وبطاقات الكلمات.',
           'أسماء المستويات أصبحت A1 و A1+ و A2 و A2+ و B1 و B1+ و B2 و B2+ و C1 و C2 في كل البرنامج، والمستويات التي لم تُضف دروسها بعد عليها علامة «قريبًا».',
           'اختبار MAP: التدريب أصبح في وحدات RIT داخل كل صف (RIT 1 من 151 إلى 160، و RIT 2 من 161 إلى 170، وهكذا). الاختبارات التجريبية كما هي، ونتائج التدريب المحفوظة في الوحدات القديمة تبدأ من جديد.',
           'الإجابة الصحيحة تحصل على احتفال متحرك مع صوت مبهج، والإجابة الخاطئة على تشجيع لطيف «حاول مرة أخرى» مع صوت هادئ.']}, **cl}
wr(P('tools', 'app', 'changelog.json'), json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('v1.11.0 patched')
