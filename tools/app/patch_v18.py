"""v1.8.0: school identity, a departments hub after sign-in, motion, and Levels 2–5 in Listening and Speaking.
Run once:  python3 tools/app/patch_v18.py"""
import os, re
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)


def patch(path, pairs, regex=()):
    s = open(path, encoding='utf-8').read()
    for a, b, *n in pairs:
        n = n[0] if n else 1
        c = s.count(a)
        assert c == n, f'{path}: expected {n} x {a[:80]!r}, found {c}'
        s = s.replace(a, b)
    for pat, rep, n in regex:
        s, c = re.subn(pat, rep, s)
        assert c == n, f'{path}: regex {pat!r} matched {c}, expected {n}'
    open(path, 'w', encoding='utf-8').write(s)


CSS = r"""
/* ===== v1.8: school identity, departments hub, motion ===== */
.top::before{content:"";display:block;height:4px;background:linear-gradient(90deg,#2E3074 0 25%,#E16378 25% 50%,#F2B330 50% 75%,#278FC2 75% 100%)}
.brand img.b-sch{width:40px;height:40px;flex:none;border-radius:10px;background:#fff;object-fit:contain}
.auth-head img.b-sch{width:64px;height:64px;flex:none;border-radius:14px;background:#fff;object-fit:contain;box-shadow:var(--sh2)}
.sch-line{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px;font-weight:800;color:#2E3074;margin:14px 0 0;font-size:.92rem}
.sch-line img{width:26px;height:26px;border-radius:6px}
.hub{margin-top:18px;border-radius:28px;padding:26px 28px;color:#fff;position:relative;overflow:hidden;background:linear-gradient(120deg,#2E3074 0%,#3A3D9C 40%,#278FC2 100%);background-size:200% 200%;animation:hubBg 14s ease-in-out infinite alternate;box-shadow:0 14px 34px rgba(46,48,116,.28)}
@keyframes hubBg{to{background-position:100% 50%}}
.hub-shapes{position:absolute;inset:0;pointer-events:none}
.hub-shapes i{position:absolute;width:var(--s,34px);height:var(--s,34px);background:var(--k,#F2B330);border-radius:7px;opacity:.5;animation:shp var(--t,9s) ease-in-out infinite alternate;animation-delay:var(--d,0s)}
@keyframes shp{from{transform:translate(0,0) rotate(var(--r0,0deg))}to{transform:translate(var(--x,18px),var(--y,-24px)) rotate(calc(var(--r0,0deg) + 50deg))}}
.hub-in{position:relative;z-index:1;display:flex;gap:22px;align-items:center;flex-wrap:wrap}
.hub-logo{flex:none;background:#fff;border-radius:22px;padding:10px 16px;box-shadow:0 12px 30px rgba(10,12,50,.35);animation:breathe 4.5s ease-in-out infinite}
.hub-logo img{display:block;height:132px;width:auto}
@keyframes breathe{50%{transform:translateY(-6px)}}
.hub-tx{flex:1 1 300px;min-width:0}
.hub-tx .pill{background:rgba(255,255,255,.2);color:#fff}
.hub-tx h1{font-size:clamp(1.55rem,3.1vw,2.15rem);font-weight:800;margin-top:8px}
.hub .by-ph{width:80px;height:80px}.hub .by-tx{min-width:0}.hub .by-tx b{font-size:1.2rem}.hub .by-ar{margin-top:5px}
.hub-hi{font-size:1.12rem;font-weight:800;margin:.35rem 0 0}
.hub-tx .ar{color:#fff;text-align:left}
.hub .ctrls{justify-content:flex-start;margin-top:12px}
.hub .ctrls .btn{background:rgba(255,255,255,.16);color:#fff;border:1px solid rgba(255,255,255,.4);box-shadow:none}
.hub .ctrls .btn:hover{background:rgba(255,255,255,.28)}
.depts{display:grid;gap:16px;grid-template-columns:repeat(12,1fr)}
.dept{grid-column:span 4;position:relative;overflow:hidden;border-radius:24px;padding:20px;min-height:216px;color:#fff;text-align:left;display:flex;flex-direction:column;gap:2px;background:linear-gradient(135deg,var(--a),var(--b));box-shadow:0 10px 24px rgba(29,36,51,.18);text-shadow:0 1px 2px rgba(0,0,0,.16);animation:dIn .6s cubic-bezier(.2,.9,.25,1.15) backwards;animation-delay:calc(var(--i)*80ms);transition:transform .2s,box-shadow .2s}
.dept.soon{grid-column:span 3;min-height:158px}
@keyframes dIn{from{opacity:0;transform:translateY(28px) scale(.93)}}
.dept::before{content:"";position:absolute;right:-44px;top:-44px;width:176px;height:176px;border-radius:50%;background:rgba(255,255,255,.17);animation:blob 6s ease-in-out infinite alternate;animation-delay:calc(var(--i)*-.7s)}
.dept::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,.3) 50%,transparent 60%);transform:translateX(-120%);animation:shine 6s ease-in-out infinite;animation-delay:calc(var(--i)*.55s);pointer-events:none}
@keyframes shine{0%,72%{transform:translateX(-120%)}100%{transform:translateX(120%)}}
@keyframes blob{to{transform:scale(1.28) translate(-14px,12px)}}
.dept:hover{transform:translateY(-7px) scale(1.02);box-shadow:0 18px 34px rgba(29,36,51,.26)}
.dept:active{transform:scale(.97)}
.dept>*{position:relative;z-index:1}
.d-ic{width:64px;height:64px;border-radius:20px;background:rgba(255,255,255,.24);display:grid;place-items:center;margin-bottom:10px;animation:dFloat 3.4s ease-in-out infinite;animation-delay:calc(var(--i)*-.5s)}
.d-ic svg{width:34px;height:34px;stroke:#fff;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.d-ic svg text{fill:#fff;stroke:none;font-family:var(--fh);font-weight:800}
@keyframes dFloat{50%{transform:translateY(-7px) rotate(-6deg)}}
.d-k{font-weight:800;font-size:.78rem;letter-spacing:.04em;text-transform:uppercase;opacity:.95}
.dept h3{font-size:1.5rem;line-height:1.15;color:#fff}
.dept .ar{color:#fff;text-align:left;font-weight:700}
.d-meta{margin-top:auto;padding-top:10px;display:flex;gap:6px;flex-wrap:wrap;padding-right:48px}
.d-meta span{background:rgba(255,255,255,.24);border-radius:999px;padding:4px 10px;font-weight:800;font-size:.8rem;text-shadow:none}
.d-go{position:absolute!important;right:16px;bottom:16px;width:42px;height:42px;border-radius:50%;background:#fff;color:var(--b);display:grid;place-items:center;font-weight:900;font-size:1.25rem;text-shadow:none;transition:transform .2s}
.dept:hover .d-go{transform:translateX(5px)}
.d-soon{position:absolute!important;right:12px;top:12px;background:#fff;color:var(--b);border-radius:999px;padding:4px 12px;font-weight:900;font-size:.8rem;display:inline-flex;gap:6px;align-items:center;text-shadow:none}
.d-soon i{width:8px;height:8px;border-radius:50%;background:var(--b);animation:pulse 1.2s infinite}
.dept.soon h3{font-size:1.18rem}
.dept.soon .d-ic{width:54px;height:54px;border-radius:17px}.dept.soon .d-ic svg{width:28px;height:28px}
.dept.nudge{animation:rshake .4s ease-in-out}
.soonmsg{min-height:1.6em;text-align:center;font-weight:800;color:#2E3074;margin:12px 0 0}
.lhead.dhead{display:flex;gap:16px;align-items:center;background:linear-gradient(135deg,var(--a),var(--b))}
.lhead.dhead .d-ic{margin:0;flex:none}
.gcard{transition:transform .18s,box-shadow .18s}
.gcard:hover{transform:translateY(-5px);box-shadow:0 14px 28px rgba(29,36,51,.2)}
.gcard:active{transform:scale(.98)}
.gcard .em{animation:dFloat 3.6s ease-in-out infinite}
.ucard,.studio-card,.lrow{transition:transform .18s,box-shadow .18s,border-color .18s}
.ucard:hover,.studio-card:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(29,36,51,.14)}
.vin>*{animation:vIn .45s cubic-bezier(.2,.8,.2,1) backwards}
.vin>*:nth-child(2){animation-delay:.06s}.vin>*:nth-child(3){animation-delay:.12s}.vin>*:nth-child(4){animation-delay:.18s}.vin>*:nth-child(5){animation-delay:.24s}.vin>*:nth-child(n+6){animation-delay:.3s}
@keyframes vIn{from{opacity:0;transform:translateY(16px)}}
.vin .gcard,.vin .ucard{animation:dIn .55s cubic-bezier(.2,.9,.25,1.15) backwards}
.vin .gcard:nth-child(2),.vin .ucard:nth-child(2){animation-delay:.07s}.vin .gcard:nth-child(3),.vin .ucard:nth-child(3){animation-delay:.14s}.vin .gcard:nth-child(4),.vin .ucard:nth-child(4){animation-delay:.21s}.vin .ucard:nth-child(5){animation-delay:.28s}.vin .ucard:nth-child(6){animation-delay:.35s}
@media (max-width:900px){.dept{grid-column:span 12;min-height:0}.dept.soon{grid-column:span 6;min-height:168px}.hub .byline{flex:1 1 100%}}
@media (max-width:640px){.lhead.dhead{flex-direction:column;align-items:flex-start;gap:10px}.hub{padding:20px}.hub-logo img{height:96px}.hub-in{gap:14px}.d-soon{font-size:.72rem;padding:3px 9px}}
@media (prefers-reduced-motion:reduce){.hub,.hub-shapes i,.hub-logo,.dept,.dept::before,.dept::after,.d-ic,.d-soon i,.gcard .em,.vin>*,.vin .gcard,.vin .ucard{animation:none!important}.dept,.gcard,.ucard,.studio-card,.d-go{transition:none!important}}
"""

JS_HEAD = r"""
/* ---------- Departments (v1.8) ---------- */
const lv = g => 'Level ' + (g - 1);                  // Listening and Speaking levels: the four sets are Level 2 … Level 5
const SCH = '<img class="b-sch" src="img/andalus-shield.png" alt="Andalus International Schools" width="40" height="40">';
const DIC = {
  ls: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg>',
  sh: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/></svg>',
  map: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
  rw: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  gv: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 16 6-12 6 12"/><path d="M8 12h8"/><path d="m16 20 2 2 4-4"/></svg>',
  step: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/><path d="M22 10v6"/></svg>',
  ph: '<svg viewBox="0 0 24 24" aria-hidden="true"><text x="12" y="16.5" text-anchor="middle" font-size="11.5">abc</text></svg>'
};
/* id, English name, Arabic name, line above the name, gradient from → to, view to open (none = coming soon) */
const DEPTS = [
  ['ls', 'Listening and Speaking', 'الاستماع والتحدث', 'Levels 2–5 · CEFR A1 → A2+', '#2F9BF0', '#1D5FD6', 'ls'],
  ['sh', 'Shadowing', 'التظليل (المحاكاة)', 'Listen and speak with the speaker', '#FF7A59', '#E23E78', 'studio'],
  ['map', 'MAP Test', 'اختبار MAP', 'Reading · Language Usage · Grades 3–9', '#22B573', '#0B8A5A', 'map'],
  ['rw', 'Reading and Writing', 'القراءة والكتابة', '', '#F59E0B', '#EA5B0C', ''],
  ['gv', 'Grammar and Vocabulary', 'القواعد والمفردات', '', '#9B6CF6', '#6D3BE0', ''],
  ['step', 'STEP Preparation', 'التحضير لاختبار STEP', '', '#12B5CB', '#0A7C96', ''],
  ['ph', 'Phonics', 'الصوتيات', '', '#F0569C', '#C92671', '']
];
"""

HOME = r"""VIEWS.home = m => {
  const me = Store.me(), T = me.id === 'teacher';
  const lsS = D.grades.reduce((a, gr) => { const s = gradeStats(gr.grade); a.done += s.done; a.total += s.total; a.stars += s.stars; return a; }, { done: 0, total: 0, stars: 0 });
  const sh = shStats(), mapDone = typeof MAPX !== 'undefined' && MAPX.doneCount ? MAPX.doneCount() : 0;
  const meta = { ls: [`${lsS.done}/${lsS.total} lessons`, `★ ${lsS.stars}`], sh: [`⏱️ ${sh.min} min`, `⭐ ${sh.mastered}`, `🔥 ${sh.streak}`], map: ['2 subjects · 7 grades', `✅ ${mapDone}`] };
  const shapes = [['8%', '12%', 30, '#F2B330', 20, -22, 9, 0, 45], ['37%', '5%', 22, '#E16378', -16, 14, 11, -2, 0], ['52%', '8%', 18, '#fff', 14, 20, 8, -1, 45], ['68%', '70%', 40, '#278FC2', -22, -26, 12, -3, 0],
    ['82%', '14%', 34, '#E16378', 18, 24, 10, -4, 45], ['93%', '58%', 26, '#F2B330', -14, -30, 9, -5, 0], ['60%', '86%', 16, '#fff', 20, -10, 7, -2, 45], ['1.5%', '70%', 20, '#278FC2', 10, 14, 13, -6, 45]];
  m.innerHTML = `
  <section class="hub">
    <div class="hub-shapes" aria-hidden="true">${shapes.map(([l, t, s, k, x, y, d, dl, r]) => `<i style="left:${l};top:${t};--s:${s}px;--k:${k};--x:${x}px;--y:${y}px;--t:${d}s;--d:${dl}s;--r0:${r}deg"></i>`).join('')}</div>
    <div class="hub-in">
      <div class="hub-logo"><img src="img/andalus-logo.png" alt="Andalus International Schools" width="107" height="132"></div>
      <div class="hub-tx">
        <span class="pill">Andalus International Schools · Taif</span>
        <h1><span class="hero-logo">${LOGO}</span>Listen Up! Speak Out!</h1>
        <p class="hub-hi">Hello, ${esc(me.name)}! 👋 Choose a department to start.</p>
        <p class="ar" style="margin:0">مرحبًا! اختر القسم لتبدأ التعلّم.</p>
        <div class="ctrls">${T ? '<button class="btn sm" id="wDash">📊 Dashboard</button>' : ''}<button class="btn sm" id="wSet">⚙️ Settings</button><button class="btn sm" id="wOut">🔁 Switch user</button></div>
      </div>
      <div class="byline"><img class="by-ph" src="img/waleed-youssef.jpg" alt="Mr. Waleed Youssef" width="96" height="96"><div class="by-tx"><span class="by-k">Designed by</span><b>Mr. Waleed Youssef</b><span class="by-t">English Teacher & Curriculum Designer</span><span class="by-ar" lang="ar" dir="rtl">تصميم وإعداد: أ. وليد يوسف</span></div></div>
    </div>
  </section>
  <div class="section-title"><h2>Departments</h2><span class="ar" style="font-size:1.1rem;font-weight:800">الأقسام</span></div>
  <section class="depts">${DEPTS.map(([id, en, ar, k, a, b, view], i) => `
    <button class="dept${view ? '' : ' soon'}" style="--a:${a};--b:${b};--i:${i}" data-dept="${id}">
      ${view ? '' : '<span class="d-soon"><i></i>Soon · قريبًا</span>'}
      <span class="d-ic">${DIC[id]}</span>
      ${k ? `<span class="d-k">${esc(k)}</span>` : ''}
      <h3>${esc(en)}</h3>
      <span class="ar">${esc(ar)}</span>
      ${view ? `<span class="d-meta">${meta[id].map(x => `<span>${x}</span>`).join('')}</span><span class="d-go" aria-hidden="true">→</span>` : ''}
    </button>`).join('')}
  </section>
  <p class="soonmsg" id="soonMsg" role="status" aria-live="polite"></p>
  <div id="appBox"></div>
  <section class="card about">
    <img class="ab-ph" src="img/waleed-youssef.jpg" alt="Mr. Waleed Youssef" width="128" height="128">
    <div class="ab-tx"><span class="by-k" style="color:var(--muted)">About the designer</span><h3>Mr. Waleed Youssef</h3>
      <p>Mr. Waleed Youssef is an English language teacher, a trainer of STEP and IELTS candidates, and a curriculum and materials designer. He created <b>Listen Up! Speak Out!</b> so that young learners listen with confidence and speak with joy.</p>
      <p class="ar ar-block">الأستاذ وليد يوسف معلّم لغة إنجليزية، ومدرّب لاختبارَي STEP وIELTS، ومصمّم مناهج ومواد تعليمية. صمّم هذا البرنامج ليستمع المتعلّمون الصغار بثقة ويتحدّثوا بمتعة.</p></div>
    <img class="ab-seal" src="img/seal.svg" alt="Mr. Waleed Youssef seal" width="112" height="112">
  </section>
  <p class="sch-line"><img src="img/andalus-shield.png" alt="" width="26" height="26">Andalus International Schools · Taif <span class="ar" style="color:inherit">مدارس الأندلس العالمية</span></p>
  <p class="foot" style="margin-top:10px"><img src="img/seal.svg" alt="" width="22" height="22" style="vertical-align:-6px;margin-right:6px">Listen Up! Speak Out! · Designed by Mr. Waleed Youssef · Listening and Speaking Levels 2–5 · Shadowing · MAP practice for Grades 3–9 · v${APP_VER}<br><span style="font-size:.75rem">Pictures: Fluent Emoji © Microsoft (MIT licence)</span></p>`;
  if (window.LSP_PWA) LSP_PWA.box($('#appBox', m));
  if ($('#wDash', m)) $('#wDash', m).onclick = () => go('teacher');
  $('#wSet', m).onclick = () => go('settings'); $('#wOut', m).onclick = () => Auth.signOut();
  $$('[data-dept]', m).forEach(b => b.onclick = () => {
    const d = DEPTS.find(x => x[0] === b.dataset.dept);
    if (d[6]) return go(d[6]);
    b.classList.remove('nudge'); void b.offsetWidth; b.classList.add('nudge');
    $('#soonMsg', m).innerHTML = `${esc(d[1])} is coming soon. <span class="ar" style="color:inherit">${esc(d[2])}: قريبًا</span>`;
  });
};

/* --- Listening and Speaking department: choose a level --- */
VIEWS.ls = m => {
  const parts = [['Home', () => go('home')], ['Listening and Speaking']], d = DEPTS[0];
  m.innerHTML = crumbs(parts) + `
  <section class="lhead dhead" style="--a:${d[4]};--b:${d[5]}"><span class="d-ic">${DIC.ls}</span><div><span class="k">Department · Levels 2–5 · CEFR A1 → A2+</span><h1>Listening and Speaking</h1>
    <p style="margin:.3rem 0 0;opacity:.95;max-width:720px">Real audio, smart listening tasks, pronunciation games and role-plays. Each level has 6 units; each unit has 3 listening lessons, 2 speaking lessons, 3 games and a Unit Check.</p>
    <p class="ar" style="color:#fff;margin:0">الاستماع والتحدث: تسجيلات حقيقية ومهام استماع وألعاب نطق ولعب أدوار، في أربعة مستويات.</p></div></section>
  <div class="section-title"><h2>Choose your level</h2><span class="ar" style="font-size:1.05rem;font-weight:800">اختر مستواك</span></div>
  <section class="grid g2">
    ${D.grades.map(gr => { const b = BANDS[gr.grade], s = gradeStats(gr.grade); return `
      <button class="gcard" style="background:${b.grad}" data-grade="${gr.grade}">
        <span class="em">${b.em}</span>
        <span class="lv">${esc(b.name)} · CEFR ${esc(gr.level)}</span>
        <h3>${lv(gr.grade)}</h3>
        <span style="font-weight:700;opacity:.95;margin:.2rem 0 .8rem">${gr.units.map(u => u.emoji).join(' ')}</span>
        <span class="bar"><i style="width:${Math.round(100 * s.done / s.total)}%"></i></span>
        <span class="meta">${s.done}/${s.total} lessons · ★ ${s.stars}</span>
      </button>`; }).join('')}
  </section>`;
  bindCrumbs(m, parts);
  $$('[data-grade]', m).forEach(b => b.onclick = () => go('grade', { g: +b.dataset.grade }));
};
"""

p = P('www', 'index.html')
s = open(p, encoding='utf-8').read()
i, j = s.index('VIEWS.home = m => {'), s.index('VIEWS.grade = m => {')
s = s[:i] + HOME + '\n' + s[j:]
assert s.count('</style>') >= 1
k = s.index('</style>')
s = s[:k] + CSS + s[k:]
a = '/* =============== VIEWS =============== */'
assert s.count(a) == 1
s = s.replace(a, JS_HEAD + '\n' + a)
open(p, 'w', encoding='utf-8').write(s)

L = "['Listening and Speaking', () => go('ls')], "
patch(p, [
    ("const APP_VER = '1.7.0';", "const APP_VER = '1.8.0';"),
    ('<meta name="theme-color" content="#2F7BEA">', '<meta name="theme-color" content="#2E3074">'),
    ('content="Listening and speaking program for Grades 3–6 (CEFR A1 → A2+): real audio, listening tasks, pronunciation games, shadowing and role-plays, with Arabic support. Designed by Mr. Waleed Youssef."',
     'content="Listen Up! Speak Out! — Andalus International Schools, Taif: Listening and Speaking (Levels 2–5), Shadowing and MAP test practice (Grades 3–9), with Arabic support. Designed by Mr. Waleed Youssef."'),
    # school colours as the default accent
    ("--coral:#FF6B4A; --coral-d:#E0502F; --sun:#FFC233;", "--coral:#E0566F; --coral-d:#BE3F58; --sun:#F2B330;"),
    ("--c:#2F7BEA; --cl:#E3EEFF; --cd:#1B4FA3;", "--c:#2E3074; --cl:#E8E9F7; --cd:#1F2052;"),
    ("r.setProperty('--c', b ? b.c : '#2F7BEA'); r.setProperty('--cl', b ? b.l : '#E3EEFF'); r.setProperty('--cd', b ? b.d : '#1B4FA3');",
     "r.setProperty('--c', b ? b.c : '#2E3074'); r.setProperty('--cl', b ? b.l : '#E8E9F7'); r.setProperty('--cd', b ? b.d : '#1F2052');"),
    # header: school shield and name
    ("""aria-label="Home">${LOGO}<span>Listen Up! Speak Out!<small>by Mr. Waleed Youssef · Grades 3–9</small></span></button>""",
     """aria-label="Home">${SCH}<span>Listen Up! Speak Out!<small>Andalus International Schools · Taif</small></span></button>"""),
    # view-enter motion
    ("""  $$('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));""",
     """  { const vk = [S.view, S.step, S.g, S.u, S.mg, S.subj].join('|'); if (render.vk !== vk) $('#main').classList.add('vin'); render.vk = vk; }
  $$('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));"""),
    # navigation
    ("    if (v === 'grade' || v === 'teacher' || v === 'studio') go('home');", "    if (v === 'grade') go('ls');\n    else if (v === 'ls' || v === 'teacher' || v === 'studio') go('home');"),
    ("safe() { return ['home', 'grade',", "safe() { return ['home', 'ls', 'grade',"),
    # sign-in and first-run screens
    ("""<div class="auth-head">${LOGO}<div><h1>Welcome to Listen Up! Speak Out!</h1>""", """<div class="auth-head">${SCH}${LOGO}<div><h1>Welcome to Listen Up! Speak Out!</h1>"""),
    ("""<div class="auth-head">${LOGO}<div><h1>Who is learning today?</h1>""", """<div class="auth-head">${SCH}${LOGO}<div><h1>Who is learning today?</h1>"""),
    ("""<p class="foot">Listen Up! Speak Out! · Designed by Mr. Waleed Youssef · v${APP_VER} · 🔒 accounts stay on this device</p>""",
     """<p class="foot">Andalus International Schools · Taif · Listen Up! Speak Out! · Designed by Mr. Waleed Youssef · v${APP_VER} · 🔒 accounts stay on this device</p>"""),
    # Levels instead of grades in Listening and Speaking and in Shadowing
    ("""  const parts = [['Home', () => go('home')], [`Grade ${S.g}`]];""", """  const parts = [['Home', () => go('home')], """ + L + """[lv(S.g)]];"""),
    ("""<span class="k">${esc(b.name)} Level · CEFR ${esc(gr.level)}</span><h1>Grade ${S.g}: 6 units</h1>""", """<span class="k">${esc(b.name)} · CEFR ${esc(gr.level)}</span><h1>${lv(S.g)}: 6 units</h1>"""),
    ("""[['Home', () => go('home')], [`Grade ${S.g}`, () => go('grade', { g: S.g })],""", """[['Home', () => go('home')], """ + L + """[lv(S.g), () => go('grade', { g: S.g })],""", 4),
    ("""<span class="k">Grade ${S.g} · Unit ${u.n}</span>""", """<span class="k">${lv(S.g)} · Unit ${u.n}</span>"""),
    ("""<b style="font-size:1.25rem">Grade ${S.g} · Unit ${u.n}: ${esc(u.title)}</b><br>in <b>Listen Up! Speak Out!</b> (${esc(b.name)} Level, CEFR ${esc(G(S.g).level)})</p>""",
     """<b style="font-size:1.25rem">${lv(S.g)} · Unit ${u.n}: ${esc(u.title)}</b><br>in <b>Listen Up! Speak Out!</b> (Listening and Speaking, ${esc(b.name)}, CEFR ${esc(G(S.g).level)})</p>"""),
    ("""<span><b>Grade ${x.g}</b> · ${x.done}/${x.total} lessons</span>""", """<span><b>${lv(x.g)}</b> · ${x.done}/${x.total} lessons</span>"""),
    ("""<h2>Choose your grade</h2></div>""", """<h2>Choose your level</h2></div>"""),
    ("""class="${x.grade === S.g ? 'on' : ''}">Grade ${x.grade}</button>""", """class="${x.grade === S.g ? 'on' : ''}">${lv(x.grade)}</button>"""),
    ("""<span class="k">🎙️ Shadowing Studio · Grade ${S.g} · Unit ${u0.n}</span>""", """<span class="k">🎙️ Shadowing Studio · ${lv(S.g)} · Unit ${u0.n}</span>"""),
    ("""<li><b>Arabic support (ع):</b> on by default in Grades 3–4 and off in Grades 5–6. Students can switch it for their grade.</li>""",
     """<li><b>Departments:</b> after sign-in, students choose a department: Listening and Speaking (Levels 2–5), Shadowing or MAP Test. Reading and Writing, Grammar and Vocabulary, STEP Preparation and Phonics are marked “Soon”.</li>
    <li><b>Arabic support (ع):</b> in Listening and Speaking it is on by default in Levels 2–3 and off in Levels 4–5. Students can switch it for their level.</li>"""),
    ("""const L = ['Student,Class,Grade,Lessons done,""", """const L = ['Student,Class,Listening and Speaking level,Lessons done,"""),
    ("""per.forEach(x => L.push([p.name, p.cls || '', x.g, x.done,""", """per.forEach(x => L.push([p.name, p.cls || '', x.g - 1, x.done,"""),
])
left = [ln for ln in open(p, encoding='utf-8').read().split('\n') if 'Grade ${' in ln]
assert not left, left[:3]

patch(P('www', 'map.js'), [
    ("  return { register, band, load, dashRows, csv, homeCard, GRADES };",
     "  const doneCount = () => { const me = Store.me(); return ['reading', 'language'].reduce((t, subj) => t + GRADES.reduce((a, g) => { const s = gradeSummary(me, subj, g); return a + s.sets + s.mocks; }, 0), 0); };\n  return { register, band, load, dashRows, csv, homeCard, doneCount, GRADES };"),
])
patch(P('www', 'manifest.webmanifest'), [
    ('"description": "Listening and speaking program for Grades 3–6 (CEFR A1 → A2+): real audio, listening tasks, pronunciation games, shadowing and role-plays, with Arabic support. Designed by Mr. Waleed Youssef."',
     '"description": "Andalus International Schools, Taif: Listening and Speaking (Levels 2–5), Shadowing and MAP test practice (Grades 3–9), with Arabic support. Designed by Mr. Waleed Youssef."'),
    ('"theme_color": "#2F7BEA"', '"theme_color": "#2E3074"'),
])
print('v1.8.0 patched')

# offline audio box (pwa.js): levels instead of grades
patch(P('www', 'pwa.js'), [
    ("Save the audio of a grade on this device so lessons play without internet.", "Save the audio of a Listening and Speaking level on this device so lessons play without internet."),
    ("<b>Grade ${g}</b>", "<b>Level ${g - 1}</b>"),
    ("<h3>Remove Grade ${b.dataset.dlr} audio?</h3><p>Lessons will need the internet again for this grade.</p>", "<h3>Remove Level ${b.dataset.dlr - 1} audio?</h3><p>Lessons will need the internet again for this level.</p>"),
])
print('pwa.js patched')
