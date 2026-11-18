"""v1.9.0: new name (From Zero To Hero), transparent animated school logo, animated welcome and sign-out,
entrance sound, Ghars department, smaller designer card, Google sign-in (Gmail or school e-mail).
Run once:  python3 tools/app/patch_v19.py"""
import os, re
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda p: open(p, encoding='utf-8').read()
wr = lambda p, s: open(p, 'w', encoding='utf-8').write(s)


def one(s, a, b, n=1, where=''):
    c = s.count(a)
    assert c == n, f'{where}: expected {n} x {a[:90]!r}, found {c}'
    return s.replace(a, b)


def cut(s, start, end, new, where=''):
    assert s.count(start) == 1 and s.count(end) >= 1, f'{where}: anchors {start[:50]!r} / {end[:50]!r}'
    i = s.index(start); j = s.index(end, i)
    return s[:i] + new + s[j:]


CSS = r"""
/* ===== v1.9: new name, animated transparent logo, welcome page, sign-out, Ghars, small designer card ===== */
.brand img.b-sch{background:none;border-radius:0;width:36px;height:42px;animation:logoSway 5s ease-in-out infinite}
@keyframes logoSway{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg) scale(1.06)}}
.nm b{color:#E0566F}.nm i{font-style:normal;color:#E8A317}
.hub .nm b,.authhero .nm b,.bye .nm b{color:#FF8FA3}.hub .nm i,.authhero .nm i,.bye .nm i{color:#FFC94A}
.nm .ch{display:inline-block;animation:chWave 2.8s ease-in-out infinite;animation-delay:calc(var(--n)*70ms)}
@keyframes chWave{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-9px)}}
.nm-sub{display:block;font-family:var(--fb);font-weight:800;font-size:.42em;letter-spacing:.14em;text-transform:uppercase;opacity:.92;margin-top:2px}
.hub-logo{background:none;box-shadow:none;padding:0;border-radius:0;animation:logoFloat 4.6s ease-in-out infinite}
.hub-logo img{height:150px;filter:drop-shadow(0 10px 18px rgba(8,10,50,.45))}
@keyframes logoFloat{0%,100%{transform:translateY(0) rotate(-2.5deg)}50%{transform:translateY(-10px) rotate(2.5deg)}}
.logo-ring{position:relative;display:inline-block}
.logo-ring::before{content:"";position:absolute;inset:-14px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.28),transparent 68%);animation:ringPulse 3s ease-in-out infinite}
@keyframes ringPulse{0%,100%{transform:scale(.86);opacity:.55}50%{transform:scale(1.12);opacity:1}}
.logo-ring img{position:relative}
.hub .byline.mini{flex:none;padding:6px 14px 6px 6px;gap:9px;border-radius:999px;align-self:flex-end;backdrop-filter:none;box-shadow:none;background:rgba(255,255,255,.13)}
.hub .byline.mini .by-ph{width:38px;height:38px;border-width:2px;box-shadow:none}
.hub .byline.mini .by-k{font-size:.58rem;letter-spacing:.1em}
.hub .byline.mini .by-tx b{font-size:.9rem;line-height:1.1}
.depts-soon{display:grid;gap:14px;grid-template-columns:repeat(5,1fr);margin-top:16px}
.depts-soon .dept.soon{grid-column:auto}
.dept.soon .d-go{width:34px;height:34px;font-size:1.05rem;right:12px;bottom:12px}
.sub2{display:grid;gap:16px;grid-template-columns:repeat(2,1fr);margin-top:16px}
.sub2 .dept.soon{grid-column:auto;min-height:190px}
/* welcome (first run and sign-in) */
body.onauth{background:#2E3074;min-height:100vh}
body.onauth::before{content:"";position:fixed;inset:0;z-index:0;background:linear-gradient(125deg,#2E3074,#3B3FA6 30%,#278FC2 62%,#E0566F 105%);background-size:240% 240%;animation:hubBg 16s ease-in-out infinite alternate}
body.onauth #app{position:relative;z-index:1}
.auth>.card,.authhero,.auth>.foot{position:relative;z-index:1}
body.onauth .top{background:rgba(255,255,255,.9)}
.authfx{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:0}
.authfx i{position:absolute;bottom:-70px;width:var(--s);height:var(--s);background:var(--k);border-radius:8px;opacity:.5;transform:rotate(45deg);animation:rise var(--t) linear infinite;animation-delay:var(--d)}
@keyframes rise{to{transform:translateY(-118vh) rotate(405deg);opacity:0}}
.auth{position:relative;z-index:1}
.authhero{text-align:center;color:#fff;margin:6px 0 16px}
.authhero .logo-ring img{height:128px;width:auto;animation:logoFloat 4.6s ease-in-out infinite;filter:drop-shadow(0 10px 18px rgba(8,10,50,.45))}
.authhero h1{font-size:clamp(2rem,6.4vw,3.3rem);font-weight:800;margin-top:10px;text-shadow:0 3px 0 rgba(0,0,0,.14)}
.authhero .tag{font-weight:800;font-size:1.08rem;margin:.5rem 0 0}
.authhero .ar{color:#fff;text-align:center;display:block;font-weight:700}
body.onauth .auth>.card{background:rgba(255,255,255,.96);border-radius:26px;box-shadow:0 22px 50px rgba(10,12,60,.34);animation:cardUp .7s cubic-bezier(.2,.9,.25,1.12) backwards .12s}
@keyframes cardUp{from{opacity:0;transform:translateY(40px) scale(.95)}}
body.onauth .foot{color:#fff;opacity:.92}
.wave{display:inline-block;transform-origin:70% 80%;animation:waveH 1.9s ease-in-out infinite}
@keyframes waveH{0%,55%,100%{transform:rotate(0)}10%,30%{transform:rotate(18deg)}20%,40%{transform:rotate(-10deg)}}
body.onauth .ptile{animation:dIn .5s cubic-bezier(.2,.9,.25,1.15) backwards;animation-delay:calc(var(--i,0)*55ms + .3s);transition:transform .16s,box-shadow .16s,border-color .16s}
body.onauth .ptile:hover{transform:translateY(-4px) scale(1.03);box-shadow:0 10px 22px rgba(46,48,116,.22)}
.ptile small{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:118px}
.btn.pulse{animation:btnPulse 2.2s ease-in-out infinite}
@keyframes btnPulse{0%,100%{box-shadow:0 4px 0 var(--coral-d),0 0 0 0 rgba(224,86,111,.5)}50%{box-shadow:0 4px 0 var(--coral-d),0 0 0 12px rgba(224,86,111,0)}}
.gbtn{background:#fff!important;color:#1F1F1F!important;border:2px solid #DADCE0;box-shadow:0 4px 0 #C6C9CE!important;gap:10px}
.gbtn svg{width:20px;height:20px;flex:none}
.gbox{min-height:48px;display:flex;justify-content:center;margin:14px 0 6px}
/* sign-out */
.bye{position:fixed;inset:0;z-index:200;display:grid;place-items:center;text-align:center;color:#fff;background:linear-gradient(125deg,#2E3074,#278FC2 60%,#E0566F 120%);animation:byeAll 1.9s ease-in-out forwards}
@keyframes byeAll{0%{opacity:0}14%,72%{opacity:1}100%{opacity:0;visibility:hidden}}
.bye img{height:150px;width:auto;animation:byeLogo 1.9s ease-in-out forwards;filter:drop-shadow(0 10px 18px rgba(8,10,50,.45))}
@keyframes byeLogo{0%{transform:scale(.4) rotate(-25deg)}22%{transform:scale(1.08) rotate(4deg)}34%,70%{transform:scale(1) rotate(0)}100%{transform:scale(.6) translateY(-80px)}}
.bye h2{font-size:clamp(1.7rem,5vw,2.6rem);color:#fff;margin-top:14px}
.bye .ar{color:#fff;text-align:center;display:block;font-size:1.25rem;font-weight:800}
.bye .wave{font-size:2.6rem;margin-top:6px}
@media (max-width:1000px){.depts-soon{grid-template-columns:repeat(3,1fr)}}
@media (max-width:640px){.depts-soon{grid-template-columns:repeat(2,1fr)}.sub2{grid-template-columns:1fr}.hub-logo img{height:104px}.authhero .logo-ring img{height:100px}.hub .byline.mini{align-self:flex-start;flex:none}}
@media (prefers-reduced-motion:reduce){body.onauth::before,.authfx i,.brand img.b-sch,.hub-logo,.logo-ring::before,.authhero .logo-ring img,.nm .ch,.wave,.btn.pulse,body.onauth .ptile,body.onauth .auth>.card,.bye img{animation:none!important}.authfx{display:none}.bye{animation:byeAll .9s linear forwards}}
"""

JS_HEAD = r"""
/* ---------- Departments (v1.9) ---------- */
const lv = g => 'Level ' + (g - 1);                  // Listening and Speaking levels: the four sets are Level 2 … Level 5
const APP = 'From Zero To Hero';
const SCH = '<img class="b-sch" src="img/andalus-shield.png" alt="Andalus International Schools" width="36" height="42">';
/* the app name with coloured, waving letters */
const nameFX = (wave) => { let n = 0; const w = (t, tag) => { const s = wave ? [...t].map(c => `<span class="ch" style="--n:${n++}">${c}</span>`).join('') : t; return tag ? `<${tag}>${s}</${tag}>` : s; };
  return `<span class="nm" aria-label="${APP}">${w('From')} ${w('Zero', 'b')} ${w('To')} ${w('Hero', 'i')}</span>`; };
const fxShapes = n => `<div class="authfx" aria-hidden="true">${Array.from({ length: n }, (_, i) => `<i style="left:${(i * 37 + 5) % 97}%;--s:${14 + (i * 13) % 30}px;--k:${['#F2B330', '#E16378', '#fff', '#7FD0F5'][i % 4]};--t:${9 + (i * 5) % 9}s;--d:-${(i * 3) % 14}s"></i>`).join('')}</div>`;
const AUTH_HERO = () => `${fxShapes(14)}<div class="authhero"><span class="logo-ring"><img src="img/andalus-logo-light.png" alt="Andalus International Schools" width="104" height="128"></span>
  <h1>${nameFX(true)}<span class="nm-sub">English Language · اللغة الإنجليزية</span></h1>
  <p class="tag">Start from zero. Become a hero! 🚀</p><span class="ar">ابدأ من الصفر وكن بطلًا!</span></div>`;
const DIC = {
  ls: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg>',
  sh: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/></svg>',
  map: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
  rw: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  gv: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 16 6-12 6 12"/><path d="M8 12h8"/><path d="m16 20 2 2 4-4"/></svg>',
  step: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/><path d="M22 10v6"/></svg>',
  ph: '<svg viewBox="0 0 24 24" aria-hidden="true"><text x="12" y="16.5" text-anchor="middle" font-size="11.5">abc</text></svg>',
  ghars: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21v-9"/><path d="M12 12C12 8 9 5 4 5c0 5 3 7 8 7Z"/><path d="M12 14c0-3 3-6 8-6 0 4-3 6-8 6Z"/><path d="M7 21h10"/></svg>',
  wl: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16"/><path d="M4 12h10"/><path d="M4 18h13"/><circle cx="19" cy="12" r="2"/></svg>',
  pa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h14v7a7 7 0 0 1-14 0Z"/><path d="M9 9h.01"/><path d="M15 9h.01"/><path d="M9 13c1.6 1.6 4.4 1.6 6 0"/></svg>'
};
/* id, English name, Arabic name, line above the name, gradient from → to, view to open, coming soon? */
const DEPTS = [
  ['ls', 'Listening and Speaking', 'الاستماع والتحدث', 'Levels 2–5 · CEFR A1 → A2+', '#2F9BF0', '#1D5FD6', 'ls', 0],
  ['sh', 'Shadowing', 'المحاكاة', 'Listen and speak with the speaker', '#FF7A59', '#E23E78', 'studio', 0],
  ['map', 'MAP Test', 'اختبار MAP', 'Reading · Language Usage · Grades 3–9', '#22B573', '#0B8A5A', 'map', 0],
  ['rw', 'Reading and Writing', 'القراءة والكتابة', '', '#F59E0B', '#EA5B0C', '', 1],
  ['gv', 'Grammar and Vocabulary', 'القواعد والمفردات', '', '#9B6CF6', '#6D3BE0', '', 1],
  ['step', 'STEP Preparation', 'التحضير لاختبار STEP', '', '#12B5CB', '#0A7C96', '', 1],
  ['ph', 'Phonics', 'الصوتيات', '', '#F0569C', '#C92671', '', 1],
  ['ghars', 'Ghars', 'غراس', '', '#7CB518', '#3D7A0A', 'ghars', 1]
];
const GHARS = [['wl', 'Wordline', '', '#12B5CB', '#0A7C96'], ['pa', 'Performing Art', 'الفنون الأدائية', '#F0569C', '#C92671']];
const deptCard = ([id, en, ar, k, a, b, view, soon], i, meta) => `
    <button class="dept${soon ? ' soon' : ''}" style="--a:${a};--b:${b};--i:${i}" data-dept="${id}">
      ${soon ? '<span class="d-soon"><i></i>Soon · قريبًا</span>' : ''}
      <span class="d-ic">${DIC[id]}</span>
      ${k ? `<span class="d-k">${esc(k)}</span>` : ''}
      <h3>${esc(en)}</h3>
      ${ar ? `<span class="ar">${esc(ar)}</span>` : ''}
      ${meta ? `<span class="d-meta">${meta.map(x => `<span>${x}</span>`).join('')}</span>` : ''}${view ? '<span class="d-go" aria-hidden="true">→</span>' : ''}
    </button>`;
let ENTER = false;   // set at sign-in: the home page then plays the entrance sound once
"""

HOME = r"""VIEWS.home = m => {
  const me = Store.me(), T = me.id === 'teacher';
  const lsS = D.grades.reduce((a, gr) => { const s = gradeStats(gr.grade); a.done += s.done; a.total += s.total; a.stars += s.stars; return a; }, { done: 0, total: 0, stars: 0 });
  const sh = shStats(), mapDone = typeof MAPX !== 'undefined' && MAPX.doneCount ? MAPX.doneCount() : 0;
  const meta = { ls: [`${lsS.done}/${lsS.total} lessons`, `★ ${lsS.stars}`], sh: [`⏱️ ${sh.min} min`, `⭐ ${sh.mastered}`, `🔥 ${sh.streak}`], map: ['2 subjects · 7 grades', `✅ ${mapDone}`] };
  const shapes = [['8%', '12%', 30, '#F2B330', 20, -22, 9, 0, 45], ['37%', '5%', 22, '#E16378', -16, 14, 11, -2, 0], ['52%', '8%', 18, '#fff', 14, 20, 8, -1, 45], ['68%', '70%', 40, '#278FC2', -22, -26, 12, -3, 0],
    ['82%', '14%', 34, '#E16378', 18, 24, 10, -4, 45], ['93%', '58%', 26, '#F2B330', -14, -30, 9, -5, 0], ['60%', '86%', 16, '#fff', 20, -10, 7, -2, 45], ['1.5%', '70%', 20, '#278FC2', 10, 14, 13, -6, 45]];
  const open = DEPTS.filter(d => !d[7]), soon = DEPTS.filter(d => d[7]);
  m.innerHTML = `
  <section class="hub">
    <div class="hub-shapes" aria-hidden="true">${shapes.map(([l, t, s, k, x, y, d, dl, r]) => `<i style="left:${l};top:${t};--s:${s}px;--k:${k};--x:${x}px;--y:${y}px;--t:${d}s;--d:${dl}s;--r0:${r}deg"></i>`).join('')}</div>
    <div class="hub-in">
      <div class="hub-logo logo-ring"><img src="img/andalus-logo-light.png" alt="Andalus International Schools" width="121" height="150"></div>
      <div class="hub-tx">
        <span class="pill">Andalus International Schools · Taif</span>
        <h1>${nameFX(true)}<span class="nm-sub">English Language · اللغة الإنجليزية</span></h1>
        <p class="hub-hi">Hello, ${esc(me.name)}! <span class="wave">👋</span> Choose a department to start.</p>
        <p class="ar" style="margin:0">مرحبًا! اختر القسم لتبدأ التعلّم.</p>
        <div class="ctrls">${T ? '<button class="btn sm" id="wDash">📊 Dashboard</button>' : ''}<button class="btn sm" id="wSet">⚙️ Settings</button><button class="btn sm" id="wOut">🔁 Switch user</button></div>
      </div>
      <div class="byline mini" title="تصميم وإعداد: وليد يوسف"><img class="by-ph" src="img/waleed-youssef.jpg" alt="Waleed Youssef" width="38" height="38"><div class="by-tx"><span class="by-k">Designed by</span><b>Waleed Youssef</b></div></div>
    </div>
  </section>
  <div class="section-title"><h2>Departments</h2><span class="ar" style="font-size:1.1rem;font-weight:800">الأقسام</span></div>
  <section class="depts">${open.map((d, i) => deptCard(d, i, meta[d[0]])).join('')}</section>
  <section class="depts-soon">${soon.map((d, i) => deptCard(d, i + open.length)).join('')}</section>
  <p class="soonmsg" id="soonMsg" role="status" aria-live="polite"></p>
  <div id="appBox"></div>
  <section class="card about">
    <img class="ab-ph" src="img/waleed-youssef.jpg" alt="Waleed Youssef" width="128" height="128">
    <div class="ab-tx"><span class="by-k" style="color:var(--muted)">About the designer</span><h3>Waleed Youssef</h3>
      <p>Waleed Youssef is an English language teacher, a trainer of STEP and IELTS candidates, and a curriculum and materials designer. He created <b>${APP}</b> to take learners of English from their first words to confident use of the language.</p>
      <p class="ar ar-block">وليد يوسف معلّم لغة إنجليزية، ومدرّب لاختبارَي STEP وIELTS، ومصمّم مناهج ومواد تعليمية. صمّم هذا البرنامج ليأخذ متعلّمي الإنجليزية من كلماتهم الأولى إلى استخدام اللغة بثقة.</p></div>
    <img class="ab-seal" src="img/seal.svg" alt="Waleed Youssef seal" width="112" height="112">
  </section>
  <p class="sch-line"><img src="img/andalus-shield.png" alt="" width="23" height="26">Andalus International Schools · Taif <span class="ar" style="color:inherit">مدارس الأندلس العالمية</span></p>
  <p class="foot" style="margin-top:10px"><img src="img/seal.svg" alt="" width="22" height="22" style="vertical-align:-6px;margin-right:6px">${APP} (English Language) · Designed by Waleed Youssef · Listening and Speaking Levels 2–5 · Shadowing · MAP practice for Grades 3–9 · v${APP_VER}<br><span style="font-size:.75rem">Pictures: Fluent Emoji © Microsoft (MIT licence)</span></p>`;
  if (window.LSP_PWA) LSP_PWA.box($('#appBox', m));
  if ($('#wDash', m)) $('#wDash', m).onclick = () => go('teacher');
  $('#wSet', m).onclick = () => go('settings'); $('#wOut', m).onclick = () => Auth.signOut();
  $$('[data-dept]', m).forEach(b => b.onclick = () => {
    const d = DEPTS.find(x => x[0] === b.dataset.dept);
    if (d[6]) return go(d[6]);
    b.classList.remove('nudge'); void b.offsetWidth; b.classList.add('nudge');
    $('#soonMsg', m).innerHTML = `${esc(d[1])} is coming soon. <span class="ar" style="color:inherit">${esc(d[2])}: قريبًا</span>`;
  });
  if (ENTER) { ENTER = false; setTimeout(() => RX.sfx('enter'), 180); }
};

/* --- Ghars department (coming soon): Wordline and Performing Art --- */
VIEWS.ghars = m => {
  const parts = [['Home', () => go('home')], ['Ghars']], d = DEPTS.find(x => x[0] === 'ghars');
  m.innerHTML = crumbs(parts) + `
  <section class="lhead dhead" style="--a:${d[4]};--b:${d[5]}"><span class="d-ic">${DIC.ghars}</span><div><span class="k">Department · coming soon</span><h1>Ghars <span class="ar" style="color:#fff;font-size:.8em">غراس</span></h1>
    <p style="margin:.3rem 0 0;opacity:.95">Two programmes will open here: Wordline and Performing Art.</p>
    <p class="ar" style="color:#fff;margin:0">برنامجان قريبًا في هذا القسم.</p></div></section>
  <section class="sub2">${GHARS.map(([id, en, ar, a, b], i) => deptCard([id, en, ar, '', a, b, '', 1], i)).join('')}</section>
  <p class="soonmsg" id="soonMsg" role="status" aria-live="polite"></p>`;
  bindCrumbs(m, parts);
  $$('[data-dept]', m).forEach(b => b.onclick = () => { const g = GHARS.find(x => x[0] === b.dataset.dept); b.classList.remove('nudge'); void b.offsetWidth; b.classList.add('nudge'); $('#soonMsg', m).textContent = g[1] + ' is coming soon.'; });
};

"""

SIGNIN = r"""VIEWS.signin = m => {
  const sec = Cfg.sec(), list = Auth.students(), classes = [...new Set(list.map(p => p.cls || ''))].filter(Boolean).sort();
  const f = S.cls != null && classes.includes(S.cls) ? S.cls : '';
  const shown = f ? list.filter(p => (p.cls || '') === f) : list;
  m.innerHTML = `<section class="auth wide">${AUTH_HERO()}<div class="card">
    <div class="auth-head"><span class="big wave">👋</span><div><h1>Who is learning today?</h1><span class="ar">من يتعلّم اليوم؟</span></div></div>
    ${S.signedOut ? `<p class="note">🔒 ${esc(S.signedOut)} <span class="ar">تم تسجيل خروجك تلقائيًا.</span></p>` : ''}
    <p class="muted" style="margin:.2rem 0 0">Tap your name, then type your PIN. <span class="ar">اضغط على اسمك ثم اكتب رمزك.</span></p>
    ${classes.length > 1 ? `<div class="seg" id="clsF" style="margin-top:12px"><button data-c="" class="${f ? '' : 'on'}">All</button>${classes.map(c => `<button data-c="${esc(c)}" class="${f === c ? 'on' : ''}">${esc(c)}</button>`).join('')}</div>` : ''}
    <div class="ptiles">${shown.map((p, i) => `<button class="ptile" style="--i:${i}" data-sid="${esc(p.id)}">${avHTML(p)}<span>${esc(p.name)}<small>${p.g ? 'Google · ' + esc(p.email) : esc(p.cls || '') + (p.pin ? '' : (p.cls ? ' · ' : '') + 'new PIN')}</small></span></button>`).join('')}
      ${sec.guest ? `<button class="ptile" style="--i:${shown.length}" data-sid="guest">${avHTML({ id: 'guest', name: 'Guest' })}<span>Guest<small>practice only</small></span></button>` : ''}</div>
    ${list.length ? '' : '<p class="muted" style="margin-top:12px">No students yet. Press “New student” to sign up. <span class="ar">لا يوجد طلاب بعد. اضغط «طالب جديد» للتسجيل.</span></p>'}
    <div class="ctrls" style="justify-content:flex-start;margin-top:16px">
      ${sec.selfSignup ? '<button class="btn pulse" id="suB">➕ New student — sign up <span class="ar" style="color:#fff">تسجيل طالب جديد</span></button>' : '<span class="muted">New student? Ask your teacher to add you. <span class="ar">اطلب من معلمك إضافتك.</span></span>'}
      ${GSI.can() ? `<button class="btn gbtn" id="gB">${GSI.ICON} Sign in with Google <span class="ar">Gmail أو بريد الأندلس</span></button>` : ''}
      <button class="btn sec" id="tB">🔑 Teacher sign in <span class="ar">دخول المعلم</span></button>
    </div></div>
    <p class="foot">Andalus International Schools · Taif · ${APP} · Designed by Waleed Youssef · v${APP_VER} · 🔒 accounts stay on this device</p></section>`;
  $$('#clsF [data-c]', m).forEach(b => b.onclick = () => { S.cls = b.dataset.c; VIEWS.signin(m); });
  $$('[data-sid]', m).forEach(b => b.onclick = () => studentSignIn(b.dataset.sid));
  const su = $('#suB', m); if (su) su.onclick = signUpFlow;
  const gb = $('#gB', m); if (gb) gb.onclick = () => GSI.open();
  $('#tB', m).onclick = () => teacherSignIn();
};

/* ---------- Sign in with Google (Gmail or the school's Google e-mail) ----------
   The app has no server. Google's own sign-in button (Google Identity Services) confirms who the user is and
   hands the page a signed ID token; the app reads the name and e-mail from it and opens (or creates) the
   matching account on this device. Only the browser version can use it: Google blocks sign-in inside app web views.
   The teacher pastes the Google "client ID" in Settings. */
const GSI = {
  ICON: '<svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.2C12.4 13.6 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.6 24.6c0-1.6-.1-3.1-.4-4.6H24v9.1h12.7c-.6 3-2.2 5.5-4.7 7.2l7.6 5.9c4.5-4.1 7-10.2 7-17.6z"/><path fill="#FBBC05" d="M10.5 28.6c-.5-1.5-.8-3-.8-4.6s.3-3.2.8-4.6l-7.9-6.2C1 16.500 0 20.100 0 24s1 7.500 2.600 10.800l7.900-6.200z"/><path fill="#34A853" d="M24 48c6.300 0 11.700-2.100 15.600-5.700l-7.600-5.900c-2.100 1.400-4.800 2.300-8 2.300-6.300 0-11.600-4.100-13.500-9.900l-7.900 6.200C6.500 42.600 14.600 48 24 48z"/></svg>',
  cfg() { return Object.assign({ cid: '', domains: 'gmail.com' }, Store.data.settings.gsi || {}); },
  put(k, v) { const s = Store.data.settings.gsi = Store.data.settings.gsi || {}; s[k] = v; Store.save(); },
  can() { return PLAT === 'web' && /^https?:$/.test(location.protocol); },
  domains() { return this.cfg().domains.toLowerCase().split(/[\s,;]+/).map(d => d.replace(/^@/, '')).filter(Boolean); },
  load() { return this.lib || (this.lib = new Promise((ok, no) => { if (window.google && google.accounts && google.accounts.id) return ok(); const s = document.createElement('script'); s.src = 'https://accounts.google.com/gsi/client'; s.async = true; s.onload = () => ok(); s.onerror = () => { this.lib = null; no(new Error('offline')); }; document.head.appendChild(s); })); },
  parse(jwt) { try { const b = String(jwt).split('.')[1].replace(/-/g, '+').replace(/_/g, '/'); return JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(b + '==='.slice((b.length + 3) % 4)), c => c.charCodeAt(0)))); } catch (e) { return null; } },
  /* returns [English, Arabic] when the account cannot be used, or null when it is fine */
  check(p) {
    const c = this.cfg(), now = Date.now() / 1000;
    if (!p || !p.email || p.aud !== c.cid || !/^(https:\/\/)?accounts\.google\.com$/.test(p.iss || '') || !(p.exp > now - 60)) return ['Google could not confirm this account. Try again.', 'تعذّر تأكيد الحساب. حاول مرة أخرى.'];
    if (p.email_verified === false) return ['This e-mail address is not verified by Google.', 'هذا البريد غير مؤكَّد لدى Google.'];
    const d = this.domains(), dom = p.email.toLowerCase().split('@')[1];
    if (d.length && !d.includes(dom)) return [`Use a ${d.map(x => '@' + x).join(' or ')} account. (${p.email} is not allowed.)`, 'استخدم حساب Gmail أو بريد المدرسة.'];
    return null;
  },
  /* the token came back from Google: open the matching account, or make it */
  done(resp, m) {
    const p = this.parse(resp && resp.credential), bad = this.check(p), E = m && $('#gE', m);
    if (bad) { if (E) E.innerHTML = `${esc(bad[0])} <span class="ar">${esc(bad[1])}</span>`; return false; }
    const email = p.email.toLowerCase(), P = Store.data.profiles;
    let u = Object.values(P).find(x => (x.email || '').toLowerCase() === email && x.id !== 'teacher' && x.id !== 'guest');
    if (!u) {
      if (!Cfg.sec().selfSignup) { if (E) E.innerHTML = 'This e-mail is not on the class list. Ask your teacher to add you. <span class="ar">اطلب من معلمك إضافتك.</span>'; return false; }
      const id = 'p' + Date.now().toString(36) + [...Sec.rnd(2)].map(x => x.toString(16).padStart(2, '0')).join('');
      u = P[id] = { id, name: String(p.name || email.split('@')[0]).slice(0, 40), cls: '', email, g: true, progress: {}, created: Date.now() };
    }
    u.g = true; Auth.start(u.id, 'student'); if (m) m.remove(); go('home'); return true;
  },
  open(hint) {
    const c = this.cfg();
    if (!c.cid) { const m = sheet(`<h3>${this.ICON.replace('<svg', '<svg style="width:22px;height:22px;vertical-align:-4px"')} Sign in with Google</h3><p>Google sign-in is not switched on yet. The teacher adds the Google sign-in key in <b>⚙️ Settings → Sign in with Google</b>.</p><p class="ar ar-block">لم يُفعَّل الدخول عبر Google بعد. يضيف المعلم مفتاح الدخول من الإعدادات.</p><div class="navrow" style="justify-content:flex-end"><button class="btn" id="gX">OK</button></div>`); $('#gX', m).onclick = () => m.remove(); return; }
    const d = this.domains();
    const m = sheet(`<h3>Sign in with Google <span class="ar">الدخول عبر Google</span></h3>
      <p class="muted" style="margin:.3rem 0 0">Use your ${d.length ? d.map(x => '<b>@' + esc(x) + '</b>').join(' or ') : 'Google'} account.${hint ? ' (' + esc(hint) + ')' : ''} <span class="ar">استخدم حساب Gmail أو بريد المدرسة.</span></p>
      <div class="gbox" id="gBox"><span class="muted">Opening Google…</span></div>
      <p class="pinmsg bad" id="gE" role="alert"></p>
      <p class="secnote">🔒 Google confirms your name and e-mail. Your lessons and progress stay on this device. <span class="ar ar-block">يؤكّد Google اسمك وبريدك فقط، ويبقى تقدّمك على هذا الجهاز.</span></p>
      <div class="navrow" style="justify-content:flex-end"><button class="btn sec" id="gX">Cancel</button></div>`);
    $('#gX', m).onclick = () => m.remove();
    this.load().then(() => {
      if (!document.body.contains(m)) return;
      google.accounts.id.initialize({ client_id: c.cid, callback: r => this.done(r, m), auto_select: false, ux_mode: 'popup', login_hint: hint || undefined });
      const box = $('#gBox', m); box.innerHTML = ''; google.accounts.id.renderButton(box, { theme: 'outline', size: 'large', shape: 'pill', text: 'signin_with', width: 280 });
    }).catch(() => { const E = $('#gE', m); if (E) { $('#gBox', m).innerHTML = ''; E.innerHTML = 'Google could not be reached. Check the internet and try again. <span class="ar">تعذّر الاتصال بـ Google. تحقّق من الإنترنت.</span>'; } });
  }
};
"""

GSET = r"""  ${tcard('🔑', 'Sign in with Google', 'الدخول عبر Google', `<p style="margin:.2rem 0 .6rem">Students can sign in with <b>Gmail</b> or the school's Google e-mail instead of a PIN. It works in the browser version of the app. Progress still stays on each device.</p>
    <p class="ar ar-block">يستطيع الطلاب الدخول ببريد Gmail أو بريد المدرسة بدلًا من الرمز، في نسخة المتصفح فقط، ويبقى التقدّم على كل جهاز.</p>
    <div class="field"><label for="gCid">Google sign-in key (OAuth client ID) <span class="ar">مفتاح الدخول</span></label><input type="text" id="gCid" maxlength="120" autocomplete="off" spellcheck="false" placeholder="1234567890-abc….apps.googleusercontent.com" value="${esc(GSI.cfg().cid)}"></div>
    <div class="field"><label for="gDom">Allowed e-mail endings <span class="ar">نطاقات البريد المسموح بها</span></label><input type="text" id="gDom" maxlength="120" autocomplete="off" spellcheck="false" placeholder="gmail.com, your-school.edu.sa" value="${esc(GSI.cfg().domains)}"><small class="muted">Separate with commas. Leave empty to allow any Google account.</small></div>
    <div class="ctrls" style="justify-content:flex-start"><button class="btn sm" id="gSave">💾 Save</button><span class="muted" id="gMsg"></span></div>
    <details style="margin-top:10px"><summary><b>How to get the key (once, free)</b></summary><ol style="margin:.5rem 0 0;padding-left:20px"><li>Open <b>console.cloud.google.com</b> with your Google account and create a project.</li><li>Open <b>APIs &amp; Services → OAuth consent screen</b>: choose <b>External</b>, type the app name and your e-mail, then press <b>Publish app</b>.</li><li>Open <b>Credentials → Create credentials → OAuth client ID → Web application</b>.</li><li>Under <b>Authorized JavaScript origins</b> add <b>${esc(location.origin.startsWith('http') ? location.origin : 'https://mrwaleedyoussif.github.io')}</b>.</li><li>Copy the <b>Client ID</b>, paste it above and press Save.</li></ol></details>`)}
"""

# ------------------------------------------------------------------ www/index.html
p = P('www', 'index.html')
s = rd(p)
s = cut(s, '/* ---------- Departments (v1.8) ---------- */', '/* =============== VIEWS =============== */', JS_HEAD.lstrip('\n') + '\n', 'depts')
s = cut(s, 'VIEWS.home = m => {', '/* --- Listening and Speaking department: choose a level --- */', HOME, 'home')
s = cut(s, 'VIEWS.signin = m => {', 'async function studentSignIn(id) {', SIGNIN, 'signin')
k = s.index('</style>'); s = s[:k] + CSS + s[k:]

W = 'index.html'
# --- names
s = one(s, '<title>Listen Up! Speak Out! — by Mr. Waleed Youssef</title>', '<title>From Zero To Hero (English Language)</title>', 1, W)
s = one(s, '<meta name="apple-mobile-web-app-title" content="Listen Up!">', '<meta name="apple-mobile-web-app-title" content="Zero To Hero">', 1, W)
s = one(s, 'content="Listen Up! Speak Out! — Andalus International Schools, Taif:', 'content="From Zero To Hero (English Language) — Andalus International Schools, Taif:', 1, W)
s = one(s, """${SCH}<span>Listen Up! Speak Out!<small>Andalus International Schools · Taif</small></span></button>""", """${SCH}<span>${nameFX(false)}<small>English Language · Andalus International Schools · Taif</small></span></button>""", 1, W)
s = one(s, """<div class="auth-head">${SCH}${LOGO}<div><h1>Welcome to Listen Up! Speak Out!</h1><span class="ar">مرحبًا بك في برنامج Listen Up! Speak Out!</span></div></div>""",
        """<div class="auth-head"><span class="big wave">👋</span><div><h1>Welcome!</h1><span class="ar">مرحبًا بك في برنامج From Zero To Hero</span></div></div>""", 1, W)
s = one(s, """m.innerHTML = `<section class="auth"><div class="card">
    <div class="auth-head"><span class="big wave">👋</span><div><h1>Welcome!</h1>""", """m.innerHTML = `<section class="auth">${AUTH_HERO()}<div class="card">
    <div class="auth-head"><span class="big wave">👋</span><div><h1>Welcome!</h1>""", 1, W)
s = one(s, 'placeholder="e.g., Mr. Waleed Youssef"', 'placeholder="e.g., Waleed Youssef"', 1, W)
s = s.replace('Listen Up! Speak Out!', 'From Zero To Hero')
assert 'Listen Up!' not in s.replace('Listen Up! records', ''), [x[:80] for x in re.findall(r'.{40}Listen Up!.{20}', s)][:3]
for a, b in (('Mr. Waleed Youssef', 'Waleed Youssef'), ('أ. وليد يوسف', 'وليد يوسف'), ('الأستاذ وليد يوسف', 'وليد يوسف')):
    s = s.replace(a, b)
assert 'Mr. Waleed' not in s and 'أ. وليد' not in s
# --- Shadowing in Arabic: المحاكاة only
s = one(s, 'التظليل يعني أن تستمع', 'المحاكاة تعني أن تستمع', 1, W)
s = s.replace('التظليل', 'المحاكاة')
# --- welcome background, entrance, sign-out
s = one(s, "  document.body.classList.toggle('classmode', !!Store.data.settings.classmode);",
        "  document.body.classList.toggle('classmode', !!Store.data.settings.classmode);\n  document.body.classList.toggle('onauth', !IN); if (S.view !== 'home') ENTER = false;", 1, W)
s = one(s, "start(id, role) { const now = Date.now(); this.A.session", "start(id, role) { ENTER = true; const now = Date.now(); this.A.session", 1, W)
s = one(s, "  signOut(why) { AU.stop(); stopAllRec(); RX.hush(); this.A.session = null;",
        "  signOut(why) { const who = this.user(); if (!why && who) byeFX(who); AU.stop(); stopAllRec(); RX.hush(); this.A.session = null;", 1, W)
s = one(s, "/* ---------- Accounts ---------- */", """/* ---------- Sign-out animation ---------- */
function byeFX(who) {
  document.querySelectorAll('.bye').forEach(x => x.remove());
  const d = document.createElement('div'); d.className = 'bye'; d.setAttribute('aria-hidden', 'true');
  d.innerHTML = `<div><img src="img/andalus-logo-light.png" alt="" width="121" height="150"><h2>See you soon${who.id === 'guest' ? '' : ', ' + esc(who.name)}!</h2><span class="ar">إلى اللقاء!</span><div class="wave">👋</div><p style="margin:.6rem 0 0;font-weight:800">${nameFX(false)}</p></div>`;
  document.body.appendChild(d); setTimeout(() => d.remove(), 2000);
  setTimeout(() => RX.sfx('leave'), 60);
}

/* ---------- Accounts ---------- */""", 1, W)
s = one(s, "    else if (kind === 'celeb') {", """    else if (kind === 'enter') {      // entrance: a bright rising phrase with a sparkle
      [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => this.bell(f, i * 0.12, 0.34, 0.13));
      [659.25, 783.99, 1046.5, 1318.5].forEach(f => this.tone(f, 0.5, 1.1, { type: 'triangle', v: 0.055, a: 0.03 }));
      this.bell(1568, 0.5, 0.9, 0.12);
      for (let i = 0; i < 7; i++) this.tone(2000 + Math.random() * 2200, 0.62 + i * 0.07, 0.14, { v: 0.04 });
    }
    else if (kind === 'leave') { [783.99, 659.25, 523.25].forEach((f, i) => this.bell(f, i * 0.14, 0.4, 0.12)); this.tone(392, 0.42, 0.7, { type: 'triangle', v: 0.06, a: 0.03 }); }
    else if (kind === 'celeb') {""", 1, W)
# --- navigation and safe-update screens
s = one(s, "    else if (v === 'ls' || v === 'teacher' || v === 'studio') go('home');", "    else if (v === 'ls' || v === 'ghars' || v === 'teacher' || v === 'studio') go('home');", 1, W)
s = one(s, "safe() { return ['home', 'ls', 'grade',", "safe() { return ['home', 'ls', 'ghars', 'grade',", 1, W)
# --- Google accounts
s = one(s, "  const p = Store.data.profiles[id]; if (!p) return;\n  if (!p.pin) {", "  const p = Store.data.profiles[id]; if (!p) return;\n  if (p.g && GSI.can()) return GSI.open(p.email);\n  if (!p.pin) {", 1, W)
s = one(s, "  ${tcard('👥', 'Students', 'الطلاب',", GSET + "  ${tcard('👥', 'Students', 'الطلاب',", 1, W)
s = one(s, "    on('sSu', v => Cfg.putSec('selfSignup', v)); on('sGu', v => Cfg.putSec('guest', v));",
        "    on('sSu', v => Cfg.putSec('selfSignup', v)); on('sGu', v => Cfg.putSec('guest', v));\n    { const gs = $('#gSave', m); if (gs) gs.onclick = () => { const cid = $('#gCid', m).value.trim(), G = $('#gMsg', m); if (cid && !/^[\\w-]+\\.apps\\.googleusercontent\\.com$/.test(cid)) { G.textContent = 'The key should end with .apps.googleusercontent.com'; return; } GSI.put('cid', cid); GSI.put('domains', $('#gDom', m).value.trim()); G.textContent = cid ? 'Saved. The Google button is now on the sign-in page (browser version).' : 'Saved. Google sign-in is off.'; }; }", 1, W)
s = one(s, "<p>All accounts, recordings and progress stay on this device. Nothing is uploaded.", "<p>All accounts, recordings and progress stay on this device. Nothing is uploaded. If Google sign-in is used, Google confirms the student's name and e-mail, and the app keeps them on this device only.", 1, W)
s = one(s, "<li><b>Departments:</b> after sign-in, students choose a department: Listening and Speaking (Levels 2–5), Shadowing or MAP Test. Reading and Writing, Grammar and Vocabulary, STEP Preparation and Phonics are marked “Soon”.</li>",
        "<li><b>Departments:</b> after sign-in, students choose a department: Listening and Speaking (Levels 2–5), Shadowing or MAP Test. Reading and Writing, Grammar and Vocabulary, STEP Preparation, Phonics and Ghars (Wordline and Performing Art) are marked “Soon”.</li>\n    <li><b>Sign in with Google:</b> in the browser version, students can use Gmail or the school's Google e-mail after you add the sign-in key in ⚙️ Settings.</li>", 1, W)
s = one(s, "const APP_VER = '1.8.0';", "const APP_VER = '1.9.0';", 1, W)
wr(p, s)

# ------------------------------------------------------------------ other files
for f, pairs in {
    P('www', 'map.js'): [('Listen Up! Speak Out!', 'From Zero To Hero'), ('Mr. Waleed Youssef', 'Waleed Youssef')],
    P('www', 'pwa.js'): [('Open <b>Listen Up!</b> from the Home Screen', 'Open <b>Zero To Hero</b> from the Home Screen'), ('Listen Up! Speak Out!', 'From Zero To Hero'), ('Mr. Waleed Youssef', 'Waleed Youssef')],
    P('www', 'img', 'seal.svg'): [('MR. WALEED YOUSSEF', 'WALEED YOUSSEF'), ('Mr. Waleed Youssef', 'Waleed Youssef')],
    P('www', 'manifest.webmanifest'): [('"name": "Listen Up! Speak Out!"', '"name": "From Zero To Hero (English Language)"'), ('"short_name": "Listen Up!"', '"short_name": "Zero To Hero"'), ('Mr. Waleed Youssef', 'Waleed Youssef')],
    P('electron', 'main.js'): [("title: 'Listen Up! Speak Out!'", "title: 'From Zero To Hero (English Language)'")],
    P('android', 'app', 'src', 'main', 'res', 'values', 'strings.xml'): [('>Listen Up!<', '>Zero To Hero<')],
    P('ios', 'App', 'App', 'Info.plist'): [('<string>Listen Up!</string>', '<string>Zero To Hero</string>'), ('Listen Up! records your voice', 'Zero To Hero records your voice')],
    P('capacitor.config.json'): [('"appName": "Listen Up! Speak Out!"', '"appName": "From Zero To Hero"')],
    # productName stays: Windows keeps its saved accounts in a folder named after it
    P('package.json'): [('"shortcutName": "Listen Up! Speak Out!"', '"shortcutName": "From Zero To Hero"'), ('"author": "Mr. Waleed Youssef"', '"author": "Waleed Youssef"'), ('© 2026 Mr. Waleed Youssef', '© 2026 Waleed Youssef'), ('"version": "1.8.0"', '"version": "1.9.0"')],
    P('.github', 'workflows', 'build.yml'): [('**Listen Up! Speak Out!** – Grades 3–6 listening & speaking program', '**From Zero To Hero (English Language)** – Andalus International Schools, Taif'), ('--title "Listen Up! Speak Out! $TAG"', '--title "From Zero To Hero $TAG"')],
}.items():
    t = rd(f)
    for a, b in pairs:
        assert a in t or 'Waleed' in a, f'{f}: {a!r} not found'   # the name pairs are optional
        t = t.replace(a, b)
    wr(f, t)
print('v1.9.0 patched')
