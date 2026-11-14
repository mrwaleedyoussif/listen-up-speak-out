"""One-time upgrade of www/index.html for the app editions (PWA, Android, iOS, Windows)."""
import sys, re
p = sys.argv[1] if len(sys.argv) > 1 else 'www/index.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:80])
    s = s.replace(old, new)

# A. head: offline fonts, PWA manifest, icons, safe-area viewport
rep('''<meta name="viewport" content="width=device-width, initial-scale=1">''',
    '''<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">''')
rep('''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;600;700;800&family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">''',
'''<meta name="description" content="Listening and speaking program for Grades 3–6 (CEFR A1 → A2+): real audio, listening tasks, pronunciation games, shadowing and role-plays, with Arabic support.">
<meta name="theme-color" content="#2F7BEA">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="icons/icon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Listen Up!">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="stylesheet" href="fonts.css">''')

# B. CSS: safe areas (phones with notches), toast, offline/download panel
rep('''@media print{.top,.noprint{display:none!important}body{background:#fff}.cert{margin:0 auto;box-shadow:none}}
</style>''', '''@media print{.top,.noprint{display:none!important}body{background:#fff}.cert{margin:0 auto;box-shadow:none}}
/* ---- app editions: safe areas, toast, offline panel ---- */
.top{padding-top:env(safe-area-inset-top)}
.top .in{padding-left:max(18px,env(safe-area-inset-left));padding-right:max(18px,env(safe-area-inset-right))}
.wrap{padding-bottom:calc(60px + env(safe-area-inset-bottom))}
@media (max-width:640px){.top .in{padding-left:max(12px,env(safe-area-inset-left));padding-right:max(12px,env(safe-area-inset-right))}.wrap{padding-bottom:calc(50px + env(safe-area-inset-bottom))}}
.toast{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom));transform:translateX(-50%);z-index:80;background:#1D2433;color:#fff;padding:10px 12px 10px 16px;border-radius:16px;box-shadow:0 12px 30px rgba(20,30,60,.3);display:flex;gap:12px;align-items:center;font-weight:700;max-width:calc(100vw - 24px)}
.toast .btn{padding:8px 14px}
.appbox{margin-top:16px}
.appbox h3{font-size:1.2rem}
.approw{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.dlrow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 0;border-top:1px solid var(--line)}
.dlrow:first-of-type{border-top:none}
.dlrow b{min-width:86px}
.dlbar{flex:1 1 120px;height:10px;border-radius:99px;background:var(--line);overflow:hidden}
.dlbar i{display:block;height:100%;width:0;background:var(--c);transition:width .2s}
.dlrow .st{font-weight:700;font-size:.88rem;color:var(--muted);min-width:110px}
.dlrow .st.ok{color:#1F8A4C}
.steps-ios{margin:.5rem 0 0;padding-left:20px}
textarea.bk{width:100%;min-height:120px;font:inherit;font-size:.85rem;border:1px solid var(--line);border-radius:12px;padding:10px}
</style>''')

# C. platform detection
rep("const LET = ['a', 'b', 'c', 'd'];", """const LET = ['a', 'b', 'c', 'd'];

/* ---------- Edition / platform ---------- */
const APP_VER = '1.0.0';
const PLAT = (() => { try { const C = window.Capacitor; if (C && C.isNativePlatform && C.isNativePlatform()) return C.getPlatform(); } catch (e) {} return /Electron\\//.test(navigator.userAgent) ? 'electron' : 'web'; })();
const NATIVE = PLAT === 'android' || PLAT === 'ios';      // phone/tablet app (Capacitor)
document.documentElement.dataset.plat = PLAT;
const copyText = t => (navigator.clipboard && window.isSecureContext ? navigator.clipboard.writeText(t) : Promise.reject(0)).catch(() => new Promise((ok, no) => {
  const ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;top:-1000px;opacity:0';
  document.body.appendChild(ta); ta.select(); let r = false; try { r = document.execCommand('copy'); } catch (e) {} ta.remove(); r ? ok() : no();
}));
function saveFile(name, text, type) {
  if (NATIVE || window.LSP_SPRITES) return false;
  try { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); return true; } catch (e) { return false; }
}""")

# D. Speech recognition: not available inside the Windows app or Android app
rep("const SRec = window.SpeechRecognition || window.webkitSpeechRecognition;",
    "const SRec = (PLAT === 'electron' || PLAT === 'android') ? null : (window.SpeechRecognition || window.webkitSpeechRecognition);")

# E. Back button / back gesture = up one level (phones, PWA, browsers)
rep("""function go(view, p = {}) {
  AU.stop(); stopAllRec(); if (view !== 'shadow') { try { Mic.close(); } catch (e) {} }
  for (const k of Object.keys(S)) delete S[k];
  Object.assign(S, { view }, p);
  render(); window.scrollTo({ top: 0 });
}""", """function go(view, p = {}) {
  const prev = S.view;
  AU.stop(); stopAllRec(); if (view !== 'shadow') { try { Mic.close(); } catch (e) {} }
  if (view === 'shadow' && prev === 'studio' && !p.upTo) p = Object.assign({}, p, { upTo: 'studio' });
  for (const k of Object.keys(S)) delete S[k];
  Object.assign(S, { view }, p);
  render(); window.scrollTo({ top: 0 });
  Nav.sync();
}
/* One history entry guards every screen except Home, so the phone's Back button,
   the swipe-back gesture and the browser's Back button go UP one level instead of leaving the app. */
const Nav = {
  armed: false, skip: 0,
  sync() {
    try {
      if (S.view !== 'home' && !this.armed) { history.pushState({ lsp: 1 }, ''); this.armed = true; }
      else if (S.view === 'home' && this.armed) { this.armed = false; this.skip++; history.back(); }
    } catch (e) {}
  },
  up() {
    const mo = document.querySelector('.modal'); if (mo) { mo.remove(); return true; }
    const v = S.view;
    if (v === 'home') return false;
    if ((v === 'listen' || v === 'speak') && S.step > 0) { S.step--; AU.stop(); stopAllRec(); render(); window.scrollTo({ top: 0 }); return true; }
    if (v === 'grade' || v === 'teacher' || v === 'studio') go('home');
    else if (v === 'unit') go('grade', { g: S.g });
    else if (v === 'shadow' && S.upTo === 'studio') go('studio', { g: S.g });
    else if (S.g && S.u) go('unit', { g: S.g, u: S.u });
    else go('home');
    return true;
  }
};
window.addEventListener('popstate', () => {
  if (Nav.skip) { Nav.skip--; return; }
  Nav.armed = false;
  if (Nav.up()) Nav.sync();
});""")

# F. Teacher dashboard: CSV only where downloads work, robust Copy, Share, Backup / Restore
rep("""<div class="ctrls" style="justify-content:flex-start;margin-top:14px">${window.LSP_SPRITES ? '' : '<button class="btn" id="csv">⬇️ Download CSV</button>'}<button class="btn sec" id="cp">📋 Copy results</button><span class="muted" id="cpm"></span></div>""",
"""<div class="ctrls" style="justify-content:flex-start;margin-top:14px">${(window.LSP_SPRITES || NATIVE) ? '' : '<button class="btn" id="csv">⬇️ Download CSV</button>'}<button class="btn sec" id="cp">📋 Copy results</button>${navigator.share ? '<button class="btn sec" id="shr">📤 Share</button>' : ''}<span class="muted" id="cpm"></span></div>
  <div class="section-title"><h2>Back up or move students</h2></div>
  <div class="card"><p style="margin-top:0">Save every student's progress in one backup, then restore it on another device or after reinstalling the app.</p>
    <p class="ar ar-block">احفظ تقدّم جميع الطلاب في نسخة احتياطية واحدة، ثم استعدها على جهاز آخر أو بعد إعادة تثبيت التطبيق.</p>
    <div class="ctrls" style="justify-content:flex-start;margin-top:10px"><button class="btn" id="bkS">💾 Back up all students</button><button class="btn sec" id="bkR">♻️ Restore a backup</button><span class="muted" id="bkm"></span></div></div>""")
rep("""  if ($('#csv', m)) $('#csv', m).onclick = () => { try { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['﻿' + csv()], { type: 'text/csv' })); a.download = 'listen-up-speak-out-progress.csv'; document.body.appendChild(a); a.click(); a.remove(); } catch (e) { $('#cpm', m).textContent = 'Download is blocked here — use Copy.'; } };
  $('#cp', m).onclick = () => { navigator.clipboard.writeText(csv()).then(() => $('#cpm', m).textContent = 'Copied! Paste into Excel or Google Sheets.', () => $('#cpm', m).textContent = 'Copy is not allowed here.'); };""",
"""  if ($('#csv', m)) $('#csv', m).onclick = () => { if (!saveFile('listen-up-speak-out-progress.csv', '﻿' + csv(), 'text/csv')) $('#cpm', m).textContent = 'Download is blocked here — use Copy.'; };
  $('#cp', m).onclick = () => { copyText(csv()).then(() => $('#cpm', m).textContent = 'Copied! Paste into Excel or Google Sheets.', () => $('#cpm', m).textContent = 'Copy is not allowed here.'); };
  if ($('#shr', m)) $('#shr', m).onclick = () => { navigator.share({ title: 'Listen Up! Speak Out! — progress', text: csv() }).catch(() => {}); };
  const bkText = () => JSON.stringify({ app: 'listen-up-speak-out', backup: 1, saved: new Date().toISOString(), data: Store.data });
  $('#bkS', m).onclick = () => {
    const name = 'listen-up-backup-' + new Date().toISOString().slice(0, 10) + '.json', t = bkText();
    if (saveFile(name, t, 'application/json')) { $('#bkm', m).textContent = 'Backup saved: ' + name; return; }
    if (navigator.share) { navigator.share({ title: name, text: t }).then(() => $('#bkm', m).textContent = 'Backup shared.', () => copyText(t).then(() => $('#bkm', m).textContent = 'Backup copied — paste it into a note or e-mail and keep it.')); return; }
    copyText(t).then(() => $('#bkm', m).textContent = 'Backup copied — paste it into a note or e-mail and keep it.', () => $('#bkm', m).textContent = 'Could not save the backup here.');
  };
  $('#bkR', m).onclick = () => {
    modal(`<h3>Restore a backup</h3><p>Choose a backup file, or paste the backup text. <b>This replaces all students on this device.</b></p><p class="ar ar-block">اختر ملف النسخة الاحتياطية أو الصق نصّها. سيحلّ ذلك محلّ جميع الطلاب على هذا الجهاز.</p>
      <input type="file" id="bkF" accept=".json,application/json,text/plain" style="margin:6px 0 10px"><textarea class="bk" id="bkT" placeholder='{"app":"listen-up-speak-out", …}'></textarea><p class="muted" id="bkE" style="margin:.4rem 0 0"></p>`, null, 'Restore');
    const mo = document.querySelector('.modal'), ok = mo.querySelector('[data-m=ok]'), ta = mo.querySelector('#bkT');
    mo.querySelector('#bkF').onchange = e => { const f = e.target.files[0]; if (f) f.text().then(t => { ta.value = t; }); };
    ok.onclick = () => {
      let o = null; try { o = JSON.parse(ta.value.trim()); } catch (e) {}
      if (!o || o.app !== 'listen-up-speak-out' || !o.data || typeof o.data.profiles !== 'object') { mo.querySelector('#bkE').textContent = 'This is not a Listen Up! Speak Out! backup.'; return; }
      Store.data = o.data; Store.save(); Store.load(); mo.remove(); go('teacher');
    };
  };""")

# G. Home: app / offline box (filled by pwa.js on the web edition) + version
rep("""  <p class="foot">Listen Up! Speak Out! · Designed for Mr. Waleed Yussuf · 72 listening lessons · 48 speaking lessons · 24 units</p>`;""",
"""  <div id="appBox"></div>
  <p class="foot">Listen Up! Speak Out! · Designed for Mr. Waleed Yussuf · 72 listening lessons · 48 speaking lessons · 24 units · v${APP_VER}</p>`;
  if (window.LSP_PWA) LSP_PWA.box($('#appBox', m));""")

# H. load pwa.js after the main script
rep("""</script>
</body>
</html>""", """</script>
<script src="pwa.js"></script>
</body>
</html>""")
open(p, 'w', encoding='utf-8').write(s)
print('patched', p)
