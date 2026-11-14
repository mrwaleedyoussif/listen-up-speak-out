"""v1.4: secure on-device accounts (sign up / sign in), Settings page, update button and automatic updates."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
p = sys.argv[1] if len(sys.argv) > 1 else 'www/index.html'
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)


def cut(start, end, new):
    """replace the text from `start` up to (not including) `end`"""
    global s
    i = s.index(start); j = s.index(end, i); s = s[:i] + new + s[j:]


# ---------- styles ----------
rep("/* v1.2: colour-coded lesson icons and pictures */", """/* v1.4: accounts, settings, updates */
html{font-size:calc(100% * var(--ts,1))}
body{font-size:calc(17px * var(--ts,1))}
body.nomotion *,body.nomotion *::before,body.nomotion *::after{animation-duration:.001s!important;animation-iteration-count:1!important;transition:none!important}
body.nomotion .confetti{display:none}
.iconbtn.upd{position:relative}.iconbtn.upd .dot{position:absolute;top:3px;right:3px;width:11px;height:11px;border-radius:50%;background:#EF4444;border:2px solid #fff;display:none}
.iconbtn.upd.has .dot{display:block}.iconbtn.upd.busy .ui{display:inline-block;animation:uspin 1.1s linear infinite}
@keyframes uspin{to{transform:rotate(360deg)}}
.auth{max-width:620px;margin:22px auto}.auth.wide{max-width:820px}.auth .foot{text-align:center}
.auth-head{display:flex;align-items:center;gap:14px;margin-bottom:6px}.auth-head svg{width:58px;height:58px;flex:none}.auth-head .big{font-size:2.6rem}
.auth-head h1{font-size:1.6rem}
.ptiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:14px}
.ptile{display:flex;align-items:center;gap:10px;padding:12px;border:2px solid var(--line);border-radius:16px;background:#fff;font-weight:800;text-align:left;cursor:pointer;min-height:66px}
.ptile:hover,.ptile:focus-visible{border-color:var(--c);outline:none;box-shadow:0 0 0 3px var(--cl)}
.ptile small{display:block;color:var(--muted);font-weight:700;font-size:.8rem}
.av{width:42px;height:42px;border-radius:50%;display:inline-grid;place-items:center;color:#fff;font-weight:800;flex:none;font-size:1.1rem}
.pinhead{display:flex;align-items:center;gap:12px;justify-content:center;text-align:left}
.pinmodal .card{max-width:340px;text-align:center}
.pindots{display:flex;gap:16px;justify-content:center;margin:16px 0 6px}
.pindots i{width:20px;height:20px;border-radius:50%;border:3px solid var(--c);transition:background .1s}.pindots i.on{background:var(--c)}
.pinpad{display:grid;grid-template-columns:repeat(3,76px);gap:10px;justify-content:center;margin:8px 0 2px}
.pinpad button{height:62px;border-radius:18px;border:2px solid var(--line);background:#fff;font:800 1.55rem var(--fh);color:var(--ink)}
.pinpad button:active{background:var(--cl)}.pinpad [data-k=x],.pinpad [data-k=b]{font-size:1.2rem;color:var(--muted)}
.pinmodal.wait .pinpad button:not([data-k=x]),.pinmodal.busy .pinpad button{opacity:.4}
.pinmsg{min-height:1.4em;text-align:center;font-weight:800;margin:.3rem 0}.pinmsg.bad{color:var(--bad)}
.shake{animation:rshake .4s ease-in-out}
.field{display:flex;flex-direction:column;gap:4px;margin:10px 0}.field label{font-weight:800}.field input{width:100%}
.pwrow{display:flex;gap:6px}.pwrow input{flex:1}
input[type=password]{font:inherit;padding:11px 14px;border-radius:12px;border:2px solid var(--line);background:#fff;min-width:0}
input[type=password]:focus{border-color:var(--c);outline:none}
.meter5{display:flex;gap:4px;margin:2px 0 4px}.meter5 i{flex:1;height:6px;border-radius:3px;background:var(--line)}
.rcode{font:800 1.7rem/1.3 ui-monospace,Consolas,Menlo,monospace;letter-spacing:3px;background:#FFF7DB;border:2px dashed #E8A200;border-radius:14px;padding:16px;text-align:center;user-select:all;margin-top:10px}
.chk{display:flex;gap:8px;align-items:center;font-weight:800;margin-top:14px}.chk input{width:20px;height:20px}
.secnote{font-size:.85rem;color:var(--ink2);background:#F1F6FF;border-radius:12px;padding:10px 12px;margin:14px 0 0}
.note{background:#FFF7DB;border:1px solid #F2D27A;border-radius:12px;padding:8px 12px;font-weight:700}
.linkbtn{background:none;border:0;color:var(--c);font-weight:800;text-decoration:underline;cursor:pointer;padding:4px}
.menu{display:flex;flex-direction:column;gap:8px;margin-top:14px}.menu button{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 14px;border:2px solid var(--line);border-radius:14px;background:#fff;font-weight:800;text-align:left}
.menu button:hover{border-color:var(--c)}
.welcome{display:flex;align-items:center;gap:14px;flex-wrap:wrap}.welcome .av{width:54px;height:54px;font-size:1.4rem}.welcome h2{font-size:1.35rem;margin:0}
.setgrid{display:grid;gap:14px;margin-top:14px}
.setcard h3{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 6px}
.srow{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0;border-top:1px solid var(--line);flex-wrap:wrap}
.setcard h3+.srow,.lockbar+div>.srow:first-child,.setcard>div>.srow:first-child{border-top:0}
.srow .lbl{flex:1 1 240px;min-width:0}.srow .lbl b{display:block}.srow .lbl small{color:var(--muted);display:block}
.tgl{position:relative;width:56px;height:32px;flex:none;display:inline-block}
.tgl input{opacity:0;width:0;height:0;position:absolute}
.tgl span{position:absolute;inset:0;border-radius:32px;background:#CBD5E1;transition:background .2s;cursor:pointer}
.tgl span::after{content:'';position:absolute;left:4px;top:4px;width:24px;height:24px;border-radius:50%;background:#fff;transition:transform .2s;box-shadow:0 1px 3px rgba(0,0,0,.3)}
.tgl input:checked+span{background:var(--ok)}.tgl input:checked+span::after{transform:translateX(24px)}
.tgl input:focus-visible+span{outline:3px solid var(--c);outline-offset:2px}.tgl input:disabled+span{opacity:.5;cursor:not-allowed}
.locked{opacity:.5;pointer-events:none;user-select:none}
.lockbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:#FFF7DB;border:1px solid #F2D27A;border-radius:12px;padding:8px 12px;margin:6px 0 8px}.lockbar>span{flex:1}
.addrow{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.addrow input[type=text]{flex:1 1 140px}
.updline{font-weight:700}.updnotes{margin-top:10px;background:#F1F6FF;border-radius:12px;padding:10px 14px}.updnotes ul{margin:.3rem 0 0;padding-left:18px}
input[type=range]{accent-color:var(--c);width:150px}
/* v1.2: colour-coded lesson icons and pictures */""")

# ---------- core (accounts, settings, updates) ----------
core = open(os.path.join(HERE, 'v14_core.js'), encoding='utf-8').read()
rep("/* ---------- Bidi: keep English phrases inside Arabic text in the right order ---------- */", core + "\n/* ---------- Bidi: keep English phrases inside Arabic text in the right order ---------- */")
rep("else { Store.load(); render(); }", "else { Store.load(); Cfg.apply(); Auth.idleCheck(true); render(); window.addEventListener('load', () => Upd.boot()); }")

# ---------- render: sign-in gate and new header ----------
rep("""function render() {
  const g = S.g || null; setBand(g);""", """function render() {
  if (!Auth.ready()) { if (S.view !== 'setup') { for (const k of Object.keys(S)) delete S[k]; S.view = 'setup'; } }
  else if (!Auth.user()) { if (S.view !== 'signin') { for (const k of Object.keys(S)) delete S[k]; S.view = 'signin'; } }
  else if (S.view === 'setup' || S.view === 'signin') { for (const k of Object.keys(S)) delete S[k]; S.view = 'home'; }
  const IN = !!Auth.user() && S.view !== 'setup' && S.view !== 'signin', T = Auth.isT();
  const g = S.g || null; setBand(g);""")
rep("""    <button class="brand" data-go="home" aria-label="Home">""", """    <button class="brand" ${IN ? 'data-go="home"' : ''} aria-label="Home">""")
cut("""    ${g ? `<button class="chip ${arOn(g) ? 'on' : ''}" id="arT" title="Arabic support">""", "  </div></header>", """    ${IN ? `${g ? `<button class="chip ${arOn(g) ? 'on' : ''}" id="arT" title="Arabic support">ع <span class="hide-sm">Arabic</span></button>` : ''}
    ${T ? `<button class="chip ${Store.data.settings.classmode ? 'on' : ''}" id="cmT" title="Teacher / class mode">🧑‍🏫 <span class="hide-sm">Class mode</span></button>` : ''}
    <button class="chip ${RX.on() ? 'on' : ''}" id="rxT" title="Sounds for right and wrong answers" aria-pressed="${RX.on()}">${RX.on() ? '🔔' : '🔕'} <span class="hide-sm">Sounds</span></button>
    <button class="chip" id="meT" title="My account">👤 <span class="hide-sm">${esc(me.name)}</span></button>
    ${T ? '<button class="iconbtn" data-go="teacher" title="Teacher dashboard" aria-label="Teacher dashboard">📊</button>' : ''}
    <button class="iconbtn" data-go="settings" title="Settings" aria-label="Settings">⚙️</button>` : ''}
    <button class="iconbtn upd" id="updT" title="Check for updates" aria-label="Check for updates"><span class="ui">🔄</span><i class="dot"></i></button>
""")
rep("""  $('#rxT').onclick = () => {""", """  const meT = $('#meT'); if (meT) meT.onclick = userMenu;
  $('#updT').onclick = () => Upd.st === 'ready' ? Upd.apply(true) : Upd.panel();
  if ($('#rxT')) $('#rxT').onclick = () => {""")
rep("""  $('#cmT').onclick = () => {""", """  if ($('#cmT')) $('#cmT').onclick = () => {""")
rep("""  (VIEWS[S.view] || VIEWS.home)($('#main'));
}""", """  (VIEWS[S.view] || VIEWS.home)($('#main'));
  Upd.paint();
}""")
# navigation: a waiting web update is applied at a safe moment
rep("""  render(); window.scrollTo({ top: 0 });
  Nav.sync();
}""", """  render(); window.scrollTo({ top: 0 });
  Nav.sync();
  setTimeout(() => Upd.safeApply(), 600);
}""")
rep("""function go(view, p = {}) {
  const prev = S.view;""", """function go(view, p = {}) {
  const prev = S.view; document.querySelectorAll('.modal').forEach(x => x.remove());""")

# ---------- home: welcome card instead of the old student picker ----------
cut("""  <section class="card" style="margin-top:16px">
    <h2 style="font-size:1.35rem">Who is learning today?</h2>""", """  <div class="section-title"><h2>Choose your level</h2></div>""", """  <section class="card welcome" style="margin-top:16px">${avHTML(me)}<div style="flex:1 1 220px"><h2>Hello, ${esc(me.name)}! 👋</h2><span class="muted">${me.id === 'teacher' ? 'Teacher account' : me.id === 'guest' ? 'Guest — practice progress is shared on this device' : (me.cls ? 'Class ' + esc(me.cls) + ' · ' : '') + 'your progress is saved on this device'}</span></div>
    <div class="ctrls">${me.id === 'teacher' ? '<button class="btn sm sec" id="wDash">📊 Dashboard</button>' : ''}<button class="btn sm sec" id="wSet">⚙️ Settings</button><button class="btn sm sec" id="wOut">🔁 Switch user</button></div></section>
""")
cut("""  $$('[data-prof]', m).forEach(b => b.onclick = () => { Store.data.current = b.dataset.prof; Store.save(); render(); });""", """  $$('[data-grade]', m).forEach(""", """  if ($('#wDash', m)) $('#wDash', m).onclick = () => go('teacher');
  $('#wSet', m).onclick = () => go('settings'); $('#wOut', m).onclick = () => Auth.signOut();
""")

# ---------- teacher dashboard: teacher only; backups go through the encrypted flow ----------
rep("""VIEWS.teacher = m => {
  const P = Store.data.profiles; const list = Object.values(P);""", """VIEWS.teacher = m => {
  if (!Auth.isT()) { m.innerHTML = `<section class="auth"><div class="card" style="text-align:center"><div style="font-size:3rem">🔒</div><h2>Teacher dashboard</h2><p>Only the teacher can open the dashboard. <span class="ar">يستطيع المعلم فقط فتح لوحة المعلم.</span></p><button class="btn" id="tdS">🔑 Teacher sign in</button></div></section>`; $('#tdS', m).onclick = () => teacherSignIn(() => go('teacher')); return; }
  const P = Store.data.profiles; const list = Object.values(P).filter(p => p.id !== 'teacher');""")
cut("""  const bkText = () => JSON.stringify(""", """\n};\n\n/* =====================================================================\n   SHADOWING STUDIO""", """  $('#bkS', m).onclick = () => backupFlow($('#bkm', m));
  $('#bkR', m).onclick = () => restoreFlow();""")
rep("""<li><b>Class mode (🧑‍🏫):</b>""", """<li><b>Accounts (🔐):</b> the teacher signs in with a username and password; each student signs in with his name and a 4-digit PIN. Manage students, PINs, security and backups in ⚙️ Settings.</li>
    <li><b>Updates (🔄):</b> press 🔄 at the top to check for a new version. With automatic updates on, new versions install by themselves.</li>
    <li><b>Class mode (🧑‍🏫):</b>""")

# ---------- settings used by the rest of the app ----------
rep("  out() { const c = actx(); if (!c) return null; if (!this.g) { this.g = c.createGain(); this.g.gain.value = 0.9; this.g.connect(c.destination); } return c; },",
    "  out() { const c = actx(); if (!c) return null; if (!this.g) { this.g = c.createGain(); this.g.gain.value = 0.9 * (Cfg.get('rxVol') / 100); this.g.connect(c.destination); } return c; },")
rep("    if (!this.on()) return; if (i == null) i = this.pick(kind); if (i < 0) return;",
    "    if (!this.on() || Cfg.get('rxVoice') === false) return; if (i == null) i = this.pick(kind); if (i < 0) return;")
rep("function confetti(big) {\n", "function confetti(big) {\n  if (Cfg.get('motion') === false) return;\n")
rep("  for (const n of [2, 1]) {", "  const cd = Math.max(1, Math.min(9, +Cfg.get('cd') || 2));\n  for (let n = cd; n >= 1; n--) {")
rep("tm = setTimeout(() => { if (tok === this.token && !done) { el.pause(); fin(true); } }, (sp[2] - sp[1]) / (rate || 1) * 1000 + 80);",
    "tm = setTimeout(() => { if (tok === this.token && !done) { el.pause(); fin(true); } }, (sp[2] - sp[1]) / (rate || this.rate || 1) * 1000 + 80);")

rep("const APP_VER = '1.3.0';", "const APP_VER = '1.4.0';")
open(p, 'w', encoding='utf-8').write(s)
print('v1.4 patched')
