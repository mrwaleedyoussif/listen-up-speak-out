"""Grammar and Vocabulary department: brings the "English Pathway App" module (Strand D) into www/gv
and fits it to From Zero To Hero.

    python3 -I tools/app/add_gv.py "<folder that holds the unpacked English Pathway App>"

What it changes on the way in:
  * only the .js data mirrors are kept (they load everywhere, also from file:// in the Windows app);
  * progress is kept per signed-in user of the main app (no separate name box, no teacher PIN);
  * level names follow the app's scale (A1, A1+, A2, A2+, B1, B1+, B2, B2+, C1, C2);
  * right and wrong answers use the shared reactions (www/fx.js);
  * the page header, colours of the school and the credit line match the main app.
The module's own sw.js, manifest, icons and empty media folders are not copied."""
import json, os, re, shutil, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = sys.argv[1]
OUT = os.path.join(ROOT, 'www', 'gv')
rd = lambda p: open(p, encoding='utf-8').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8', newline='\n').write(s)


def one(s, a, b, n=1, where=''):
    c = s.count(a)
    assert c == n, f'{where}: expected {n} x {a[:80]!r}, found {c}'
    return s.replace(a, b)


# the 12 levels of the module on the app's level scale
LV = {1: 'A1', 2: 'A1+', 3: 'A2', 4: 'A2+', 5: 'B1 · Part 1', 6: 'B1 · Part 2', 7: 'B1+', 8: 'B2 · Part 1', 9: 'B2 · Part 2', 10: 'B2+', 11: 'C1', 12: 'C2'}
if os.path.isdir(OUT): shutil.rmtree(OUT)

# ---------------------------------------------------------------- data (the .js mirrors only)
n_data = 0
for dp, dn, fn in os.walk(os.path.join(SRC, 'data')):
    for f in sorted(fn):
        if not f.endswith('.js'): continue
        p = os.path.join(dp, f); rel = os.path.relpath(p, SRC).replace(os.sep, '/')
        s = rd(p)
        assert s.startswith('PathwayData.put("' + rel[:-3] + '.json"'), rel
        s = re.sub(r'Level (\d+) \([A-C][12][ab+]?\)', lambda m: 'Level ' + LV[int(m.group(1))], s)
        if rel in ('data/strands.js', 'data/grammar_vocabulary/index.js'):
            s = s.replace('"title":"Grammar & Vocabulary"', '"title":"Grammar and Vocabulary"')
        wr(os.path.join(OUT, rel), s); n_data += 1
assert not re.search(r'Level \d+ \(', rd(os.path.join(OUT, 'data/grammar_vocabulary/index.js')))

# ---------------------------------------------------------------- core.js
W = 'core.js'; s = rd(os.path.join(SRC, 'js', 'core.js'))
s = one(s, '   © Mr. Waleed Yussuf. Shared by all four strand modules. */', '   Part of From Zero To Hero (Grammar and Vocabulary department). Designed by Waleed Youssef. */', 1, W)
s = one(s, """    if (location.protocol === 'file:') return viaScript();
    return fetch(path).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(j => (P._data[path] = j)).catch(viaScript);""", """    return viaScript();   // the .js mirrors load everywhere (web, Android, iPhone and the Windows app)""", 1, W)
s = one(s, "  const KEY = 'pathway.progress.v1';", """  const HOST = window.GV_HOST || {};          // who is signed in to the main app (see host.js)
  const KEY = 'fzh.gv.v1.' + (HOST.uid || 'guest');   // each user of the device keeps their own progress
  P.host = HOST;
  /* level names on the app's scale */
  P.LV = """ + json.dumps({str(k): v for k, v in LV.items()}, ensure_ascii=False) + """;
  P.lvs = n => P.LV[n] || String(n);
  P.lv = n => 'Level ' + P.lvs(n);""", 1, W)
s = one(s, "      this.mem.profile = Object.assign(b.profile, (s && s.profile) || {});", """      this.mem.profile = Object.assign(b.profile, (s && s.profile) || {});
      if (HOST.name) { this.mem.profile.name = HOST.name; this.mem.profile.cls = HOST.cls || ''; }
      if (HOST.role !== 'teacher') { this.mem.settings.teacher = false; this.mem.settings.showAnswers = false; }""", 1, W)
s = one(s, """    if (!audioId) return P.speak(text);
    const a = new Audio('media/audio/' + audioId + '.mp3');
    a.play().catch(() => P.speak(text));""", """    if (!audioId || !P.recorded) return P.speak(text);   // no recorded files yet: the device voice reads the text
    const a = new Audio('media/audio/' + audioId + '.mp3');
    a.play().catch(() => P.speak(text));""", 1, W)
i = s.index("  /* ---------------------------------------------------------- service worker (offline use) */"); j = s.index('})();', i)
s = s[:i] + s[j:]
wr(os.path.join(OUT, 'js', 'core.js'), s)

# ---------------------------------------------------------------- activities.js / games.js: shared reactions
W = 'activities.js'; s = rd(os.path.join(SRC, 'js', 'activities.js'))
s = one(s, """  P.feedback = function (ok, item, extra) {
    const S = P.store.get();""", """  P.feedback = function (ok, item, extra) {
    if (window.Cheer) Cheer.react(ok);
    const S = P.store.get();""", 1, W)
s = one(s, "ctx.result(ok); P.toast(ok ? 'Great work!'", "ctx.result(ok); if (window.Cheer) Cheer.react(ok); P.toast(ok ? 'Great work!'", 1, W)
wr(os.path.join(OUT, 'js', 'activities.js'), s)

W = 'games.js'; s = rd(os.path.join(SRC, 'js', 'games.js'))
s = one(s, "sel.disabled = b.disabled = true; sel = null; found++;", "sel.disabled = b.disabled = true; sel = null; found++; if (window.Cheer) Cheer.react(true, { lite: true });", 1, W)
s = one(s, "} else { b.classList.add('bad'); setTimeout(() => b.classList.remove('bad'), 600); }", "} else { b.classList.add('bad'); setTimeout(() => b.classList.remove('bad'), 600); if (window.Cheer) Cheer.react(false, { lite: true }); }", 1, W)
s = one(s, "        msg.appendChild(el('div', { class: 'fb ' + (won ? 'ok' : 'bad') }", "        if (window.Cheer) Cheer.react(won);\n        msg.appendChild(el('div', { class: 'fb ' + (won ? 'ok' : 'bad') }", 1, W)
s = one(s, "const ok = op === it.answer; e.currentTarget.classList.add(ok ? 'ok' : 'bad'); if (ok) score++;", "const ok = op === it.answer; e.currentTarget.classList.add(ok ? 'ok' : 'bad'); if (ok) score++; if (window.Cheer) Cheer.react(ok, { lite: true });", 1, W)
wr(os.path.join(OUT, 'js', 'games.js'), s)

# ---------------------------------------------------------------- views.js
W = 'views.js'; s = rd(os.path.join(SRC, 'js', 'views.js'))
s = one(s, "el('span', { class: 'tag' }, L.cefr), el('div', { class: 'big' }, 'Level ' + L.level),", "el('span', { class: 'tag' }, 'Level'), el('div', { class: 'big' }, P.lvs(L.level)),", 1, W)
s = one(s, "'Level ' + lv + ' (' + L.cefr + ')'", "P.lv(lv)", 1, W)
s = one(s, "'Level ' + L.level + ' (' + L.cefr + ')'", "P.lv(L.level)", 1, W)
for a, b in (("'Level ' + lv", "P.lv(lv)"), ("'Level ' + T.level", "P.lv(T.level)"), ("'Level ' + S.placement.level", "P.lv(S.placement.level)"),
             ("'Level ' + d.placement.level", "P.lv(d.placement.level)")):
    assert a in s, a; s = s.replace(a, b)
s = one(s, "'Placement: Level ' + S.placement.level", "'Placement: ' + P.lv(S.placement.level)", 1, W)
left = re.findall(r".{30}'Level '.{30}", s)
assert not left, left
# home: this department only, with a short introduction
s = one(s, """      el('h1', null, 'English Pathway Programme'),
      el('p', null, 'Levels 1–12 (A1 to C2) • Four strands • Andalus International Schools – Taif'),
      P.ar('برنامج المسار الإنجليزي – اثنا عشر مستوى في أربعة مسارات')));""", """      el('h1', null, 'Grammar and Vocabulary'),
      el('p', null, 'Levels A1 to C2 • 72 units • 360 lessons'),
      P.ar('القواعد والمفردات – من المستوى A1 إلى المستوى C2')));
    view.appendChild(el('section', { class: 'panel intro' }, el('span', { class: 'in-k' }, 'Introduction ', el('span', { class: 'ar', lang: 'ar' }, 'مقدمة')),
      el('p', null, 'This department gives you the rules and the words that every skill needs. Each lesson explains one point with clear examples in English and Arabic, then you practise it in activities and a game and finish with a short exit quiz. Take the Placement Test to find your level, or start at Level A1.'),
      P.ar('هذا القسم يعطيك القواعد والكلمات التي تحتاجها كل مهارة. كل درس يشرح نقطة واحدة بأمثلة واضحة بالإنجليزية والعربية، ثم تتدرّب عليها في أنشطة ولعبة وتنهي الدرس باختبار قصير. أدِّ اختبار تحديد المستوى لتعرف مستواك، أو ابدأ من المستوى A1.'),
      el('ul', { class: 'in-pts' }, ['12 steps from A1 to C2', '5 lessons in each unit', 'Word Cards for review'].map(x => el('li', null, x)))));""", 1, W)
s = one(s, "const S = P.store.get(), list = await getStrands();", "const S = P.store.get(), list = (await getStrands()).filter(x => x.enabled);", 1, W)
s = one(s, "    view.appendChild(el('h2', null, 'Strands'));", "    view.appendChild(el('h2', null, 'Start here'));", 1, W)
s = one(s, "const inner = [el('span', { class: 'tag' }, 'Strand ' + s.letter), el('div', { class: 'big' }, s.title), P.ar(s.title_ar),", "const inner = [el('span', { class: 'tag' }, 'Levels A1 → C2'), el('div', { class: 'big' }, 'All levels and units'), P.ar(s.title_ar),", 1, W)
s = one(s, "el('div', { class: 'sub' }, 'Grammar & Vocabulary • 60 questions • find your level')", "el('div', { class: 'sub' }, 'Grammar and Vocabulary • 60 questions • find your level')", 1, W)
s = one(s, "el('h1', null, 'Strand ' + I._strand.letter + ': ' + I.title)", "el('h1', null, I.title)", 1, W)
# teacher tools: for the teacher who is signed in to the main app (no separate PIN)
s = one(s, """    view.append(crumbs(['Home', '#/'], ['Teacher']), el('h1', null, '👩‍🏫 Teacher Dashboard'), P.ar('لوحة المعلم'));
    if (!unlocked) {""", """    view.append(crumbs(['Home', '#/'], ['Teacher']), el('h1', null, '👩‍🏫 Teacher Dashboard'), P.ar('لوحة المعلم'));
    if (P.host.role === 'teacher') unlocked = true;
    else if (P.host.locked) { view.appendChild(el('div', { class: 'panel' }, el('p', null, 'This page is for the teacher. Sign in to the app with the teacher account to open it.'), P.ar('هذه الصفحة للمعلم. سجّل الدخول بحساب المعلم لفتحها.'))); return view; }
    if (!unlocked) {""", 1, W)
wr(os.path.join(OUT, 'js', 'views.js'), s)

# ---------------------------------------------------------------- styles
css = rd(os.path.join(SRC, 'css', 'app.css')) + """
/* ===== From Zero To Hero: header, credit line, introduction ===== */
:root{--en:'Nunito',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;--ar:'Tajawal','Segoe UI','Tahoma',Arial,sans-serif}
body.upper{--en:'Nunito',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
h1,h2,h3,.brand b,.big{font-family:'Baloo 2','Nunito',system-ui,sans-serif}
.topbar{border-bottom:0;box-shadow:0 2px 14px rgba(46,48,116,.12);gap:10px}
.topnav a{padding-left:9px;padding-right:9px}
.topbar::before{content:"";position:absolute;left:0;right:0;top:0;height:4px;background:linear-gradient(90deg,#2E3074 0 25%,#E0566F 25% 50%,#F2B330 50% 75%,#278FC2 75%)}
.topbar .back{display:inline-flex;align-items:center;gap:6px;padding:7px 13px;border-radius:999px;background:#2E3074;color:#fff;font-weight:800;text-decoration:none;white-space:nowrap}
.topbar .back:hover{background:#1F2052}
.brand img{height:42px;width:auto;border-radius:0}
.brand small{display:block;font-weight:700;color:var(--muted);font-size:.72rem;line-height:1.2}
.who{font-weight:800;font-size:.86rem;color:var(--navy);background:#E8E9F7;border-radius:999px;padding:5px 11px;white-space:nowrap;max-width:170px;overflow:hidden;text-overflow:ellipsis}
.topbar .back{font-size:.92rem}
@media (max-width:1180px){.brand small{display:none}}
@media (max-width:900px){.who{display:none}.topbar .back span{display:none}}
.intro{position:relative;overflow:hidden;padding-left:26px}
.intro::before{content:"";position:absolute;left:0;top:0;bottom:0;width:8px;background:linear-gradient(#9B6CF6,#6D3BE0)}
.in-k{display:flex;gap:8px;align-items:baseline;font-weight:800;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;color:#6D3BE0}
.in-k .ar{font-size:1rem;letter-spacing:0;color:inherit}
.intro p{margin:.35rem 0 0;line-height:1.65}
.in-pts{display:flex;flex-wrap:wrap;gap:8px;margin:.8rem 0 0;padding:0;list-style:none}
.in-pts li{background:#EFE9FF;color:#4630A8;border-radius:999px;padding:5px 13px;font-weight:700;font-size:.9rem}
@media (max-width:640px){.brand small,.brand span{display:none}.who{display:none}.topbar{flex-wrap:wrap;row-gap:6px}.topbar .back{font-size:.85rem;padding:6px 11px}
  #arToggle{margin-left:auto}.topnav{order:5;width:100%;flex-wrap:nowrap;justify-content:center;gap:2px}.topnav a{white-space:nowrap}}
"""
wr(os.path.join(OUT, 'css', 'app.css'), css)

# ---------------------------------------------------------------- page and bridge to the main app
wr(os.path.join(OUT, 'host.js'), r"""/* Bridge between the Grammar and Vocabulary department and the main app (same device, same sign-in).
   It reads who is signed in (the main app keeps that in localStorage), keeps the session awake while
   the student works here, and sends the visitor back to the sign-in page when nobody is signed in. */
(function () {
  'use strict';
  var d = {}; try { d = JSON.parse(localStorage.getItem('lsp_v1') || '{}') || {}; } catch (e) { d = {}; }
  var auth = d.auth || {}, ses = auth.session || null, ready = !!(auth.teacher && auth.teacher.pw);
  var prof = (d.profiles || {})[ses ? ses.id : (d.current || 'guest')] || { id: 'guest', name: 'Guest', cls: '' };
  if (!ses) { location.replace('../index.html'); return; }       // nobody is signed in: back to the sign-in page
  window.GV_HOST = { uid: prof.id || 'guest', name: prof.name || '', cls: prof.cls || '', role: ses.role, locked: true };
  /* keep the main app's idle timer fresh while someone is working here */
  var last = 0;
  function touch() {
    var now = Date.now(); if (now - last < 30000) return; last = now;
    try { var x = JSON.parse(localStorage.getItem('lsp_v1') || '{}'); if (x.auth && x.auth.session) { x.auth.session.last = now; localStorage.setItem('lsp_v1', JSON.stringify(x)); } } catch (e) {}
  }
  ['pointerdown', 'keydown'].forEach(function (ev) { document.addEventListener(ev, touch, { capture: true, passive: true }); });
  document.addEventListener('DOMContentLoaded', function () {
    var w = document.getElementById('who'); if (w) { if (prof.name) w.textContent = '👤 ' + prof.name; else w.remove(); }
    if (window.GV_HOST.role !== 'teacher') { var t = document.querySelector('[data-nav="teacher"]'); if (t) t.remove(); }
  });
})();
""")
wr(os.path.join(OUT, 'index.html'), """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>From Zero To Hero – Grammar and Vocabulary</title>
<meta name="description" content="From Zero To Hero (English Language) – Grammar and Vocabulary, Levels A1 to C2. Andalus International Schools, Taif Boys. Designed by Waleed Youssef.">
<meta name="theme-color" content="#2E3074">
<link rel="icon" href="../icons/icon-192.png">
<link rel="stylesheet" href="../fonts.css">
<link rel="stylesheet" href="css/app.css">
</head>
<body>
<header class="topbar">
  <a class="back" href="../index.html" title="Back to the departments">← Departments <span lang="ar" dir="rtl">الأقسام</span></a>
  <a class="brand" href="#/"><img src="../img/andalus-shield.png" alt="Andalus International Schools"><span><b>Grammar and Vocabulary</b><small>From Zero To Hero · Andalus International Schools · Taif Boys</small></span></a>
  <nav class="topnav" aria-label="Main">
    <a href="#/" data-nav="home">Home</a>
    <a href="#/cards" data-nav="cards">Word Cards <span id="dueBadge" class="badge" hidden></span></a>
    <a href="#/progress" data-nav="progress">My Progress</a>
    <a href="#/teacher" data-nav="teacher">Teacher</a>
  </nav>
  <span class="who" id="who"></span>
  <button id="arToggle" class="chip" type="button" title="Show or hide Arabic support">عربي</button>
</header>
<main id="app" tabindex="-1"><p class="loading">Loading…</p></main>
<footer class="foot">From Zero To Hero (English Language) · Grammar and Vocabulary · Designed by Waleed Youssef · Andalus International Schools · Taif Boys</footer>
<div id="toast" role="status" aria-live="polite"></div>
<script src="host.js"></script>
<script src="../sfx/reactions.js"></script>
<script src="../fx.js"></script>
<script src="js/core.js"></script>
<script src="js/activities.js"></script>
<script src="js/games.js"></script>
<script src="js/views.js"></script>
</body>
</html>
""")
size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(OUT) for f in fn)
print(f'www/gv: {n_data} data files, {size / 1048576:.1f} MB in all')
