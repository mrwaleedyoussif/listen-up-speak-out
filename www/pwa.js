/* =====================================================================
   Listen Up! Speak Out! — installable web app (PWA) helper
   • registers the service worker (offline app + cached audio)
   • "Install the app" button / iPhone-iPad instructions
   • Offline audio: download a whole grade for use without internet
   • "New version ready" message after an update
   Runs only on the web edition (https). In the Android, iOS and Windows
   apps and in the offline ZIP folder it does nothing except show app links.
   ===================================================================== */
(() => {
  'use strict';
  const HTTP = /^https?:$/.test(location.protocol);
  const WEB = PLAT === 'web' && HTTP;
  const REL = 'https://github.com/mrwaleedyoussif/listen-up-speak-out/releases/latest';
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const standalone = () => matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  const canCache = WEB && 'caches' in window && 'serviceWorker' in navigator;
  let promptEv = null, files = null, lastBox = null, wantReload = false;
  const jobs = {};          // grade -> { done, total, failed, cancel }
  const counts = {};        // grade -> cached file count
  const MB = b => (b / 1048576).toFixed(b > 104857600 ? 0 : 1) + ' MB';

  /* ---------- service worker + updates ---------- */
  function toast(html, btn, onBtn) {
    const old = document.querySelector('.toast'); if (old) old.remove();
    const t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status');
    t.innerHTML = `<span>${html}</span>${btn ? `<button class="btn">${btn}</button>` : ''}<button class="iconbtn" aria-label="Close" style="background:transparent;border-color:#46506a;color:#fff">✕</button>`;
    document.body.appendChild(t);
    if (btn) t.querySelector('.btn').onclick = () => { t.remove(); onBtn(); };
    t.querySelector('.iconbtn').onclick = () => t.remove();
  }
  /* The app's update manager (Upd in index.html) uses this to check, wait for and apply a new version. */
  const SW = window.LSP_SW = {
    ok: WEB && 'serviceWorker' in navigator, reg: null, waiting: null, cbs: [],
    onReady(cb) { this.cbs.push(cb); if (this.waiting) cb(); },
    async check() { if (this.reg) await this.reg.update(); },
    waitReady(ms) { return new Promise(res => { if (this.waiting) return res(true); const t0 = Date.now(); const iv = setInterval(() => { if (this.waiting) { clearInterval(iv); res(true); } else if (Date.now() - t0 > ms) { clearInterval(iv); res(false); } }, 400); }); },
    apply() { const w = this.waiting || (this.reg && this.reg.waiting); if (!w) { location.reload(); return; } wantReload = true; w.postMessage('skipWaiting'); setTimeout(() => { if (wantReload) location.reload(); }, 5000); }
  };
  function offerUpdate(w) {
    SW.waiting = w;
    if (SW.cbs.length) SW.cbs.forEach(cb => { try { cb(); } catch (e) {} });
    else toast('✨ A new version is ready.', 'Update', () => SW.apply());
  }
  if (WEB && 'serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('controllerchange', () => { if (wantReload) { wantReload = false; location.reload(); } });
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('sw.js').then(reg => {
        SW.reg = reg;
        if (reg.waiting && navigator.serviceWorker.controller) offerUpdate(reg.waiting);
        reg.addEventListener('updatefound', () => {
          const w = reg.installing; if (!w) return;
          w.addEventListener('statechange', () => { if (w.state === 'installed' && navigator.serviceWorker.controller) offerUpdate(w); });
        });
        setInterval(() => reg.update().catch(() => {}), 60 * 60 * 1000);
      }).catch(() => {});
    });
  }
  window.addEventListener('beforeinstallprompt', e => { e.preventDefault(); promptEv = e; redraw(); });
  window.addEventListener('appinstalled', () => { promptEv = null; redraw(); });

  /* ---------- offline audio ---------- */
  async function loadFiles() {
    if (files) return files;
    const r = await fetch('audio/files.json'); files = await r.json(); return files;
  }
  const cacheName = () => 'lsp-audio-' + files.v;
  const abs = f => new URL(f, location.href).href;
  async function countCached() {
    const c = await caches.open(cacheName());
    const have = new Set((await c.keys()).map(r => r.url));
    for (const g of Object.keys(files.grades)) counts[g] = files.grades[g].files.filter(f => have.has(abs(f))).length;
    return have;
  }
  async function download(g) {
    if (jobs[g]) return;
    const F = files.grades[g], job = jobs[g] = { done: 0, total: F.files.length, failed: 0, cancel: false };
    try { if (navigator.storage && navigator.storage.persist) await navigator.storage.persist(); } catch (e) {}
    const c = await caches.open(cacheName()), have = await countCached(), todo = F.files.filter(f => !have.has(abs(f)));
    job.done = job.total - todo.length; redraw();
    let tick = 0;
    const worker = async () => {
      while (todo.length && !job.cancel) {
        const f = todo.shift();
        try { const res = await fetch(abs(f), { cache: 'no-cache' }); if (!res.ok) throw new Error(res.status); await c.put(abs(f), res); }
        catch (e) { job.failed++; }
        job.done++; if (++tick % 8 === 0) paint(g);
      }
    };
    await Promise.all(Array.from({ length: 6 }, worker));
    delete jobs[g]; await countCached(); redraw();
    if (job.failed && !job.cancel) toast(`⚠️ ${job.failed} files could not be downloaded. Check the internet and press Download again.`);
  }
  async function remove(g) {
    const c = await caches.open(cacheName());
    await Promise.all(files.grades[g].files.map(f => c.delete(abs(f))));
    await countCached(); redraw();
  }
  function paint(g) {
    const box = lastBox && lastBox.isConnected ? lastBox : null; if (!box) return;
    const row = box.querySelector(`[data-dlg="${g}"]`); if (!row) return;
    const F = files.grades[g], j = jobs[g], n = j ? j.done : (counts[g] || 0), all = n >= F.files.length;
    row.querySelector('.dlbar i').style.width = Math.round(100 * n / F.files.length) + '%';
    const st = row.querySelector('.st');
    st.className = 'st' + (all && !j ? ' ok' : '');
    st.textContent = j ? `Downloading… ${Math.round(100 * n / F.files.length)}%` : all ? '✓ Ready offline' : n ? `${Math.round(100 * n / F.files.length)}% saved` : 'Not saved';
  }

  /* ---------- the home-page box ---------- */
  function redraw() { if (lastBox && lastBox.isConnected) box(lastBox); }
  function links() {
    return `<div class="approw">
      <a class="btn sec" href="${REL}" target="_blank" rel="noopener">🤖 Android app</a>
      <a class="btn sec" href="${REL}" target="_blank" rel="noopener">🪟 Windows app</a>
    </div>`;
  }
  function install() {
    if (standalone()) return `<p style="margin:.4rem 0 0">✅ You are using the installed app.</p><p class="ar ar-block">أنت تستخدم التطبيق المثبّت.</p>`;
    if (promptEv) return `<div class="approw"><button class="btn" id="instB">📲 Install on this device</button></div>
      <p class="ar ar-block">ثبّت البرنامج على هذا الجهاز ليعمل مثل أي تطبيق، حتى دون إنترنت.</p>`;
    if (isIOS) return `<ol class="steps-ios"><li>Open this page in <b>Safari</b>.</li><li>Tap <b>Share</b> <span aria-hidden="true">⬆️</span>, then <b>Add to Home Screen</b>.</li><li>Open <b>Listen Up!</b> from the Home Screen.</li></ol>
      <p class="ar ar-block">على الآيفون والآيباد: افتح الصفحة في سفاري، ثم اضغط «مشاركة» ثم «إضافة إلى الشاشة الرئيسية».</p>`;
    return `<p style="margin:.4rem 0 0">In <b>Chrome</b> or <b>Edge</b>, open the browser menu and choose <b>Install app</b> (or the install icon in the address bar).</p>
      <p class="ar ar-block">في متصفح كروم أو إيدج: افتح قائمة المتصفح واختر «تثبيت التطبيق».</p>`;
  }
  function box(el) {
    lastBox = el;
    if (!el || PLAT !== 'web') { if (el) el.innerHTML = ''; return; }
    if (!HTTP) {   // offline ZIP folder opened from the computer
      el.innerHTML = `<section class="card appbox"><h3>📲 Get the app</h3><p style="margin:.3rem 0 0">Install Listen Up! Speak Out! on tablets, phones and computers.</p>${links()}</section>`;
      return;
    }
    el.innerHTML = `<section class="card appbox">
      <h3>📲 Use it as an app</h3>${install()}${links()}
    </section>
    ${canCache ? `<section class="card appbox" id="offBox"><h3>📥 Offline audio</h3>
      <p style="margin:.3rem 0 .4rem">Save the audio of a Listening and Speaking level on this device so lessons play without internet.</p>
      <p class="ar ar-block" style="margin-bottom:.4rem">احفظ صوتيات الصف على هذا الجهاز لتعمل الدروس دون إنترنت.</p>
      <div id="dlRows"><p class="muted">Checking saved audio…</p></div></section>` : ''}`;
    const ib = el.querySelector('#instB');
    if (ib) ib.onclick = async () => { const e = promptEv; promptEv = null; try { e.prompt(); await e.userChoice; } catch (x) {} redraw(); };
    if (!canCache) return;
    loadFiles().then(countCached).then(() => {
      const rows = el.querySelector('#dlRows'); if (!rows) return;
      rows.innerHTML = Object.keys(files.grades).map(g => {
        const F = files.grades[g];
        return `<div class="dlrow" data-dlg="${g}"><b>Level ${g - 1}</b><span class="dlbar"><i></i></span><span class="st"></span>
          <span class="muted" style="font-size:.85rem">${MB(F.bytes)}</span>
          ${jobs[g] ? `<button class="btn sm sec" data-dlx="${g}">Stop</button>` : (counts[g] || 0) >= F.files.length
            ? `<button class="btn sm sec" data-dlr="${g}">Remove</button>`
            : `<button class="btn sm" data-dl="${g}">⬇️ Download</button>`}</div>`;
      }).join('');
      Object.keys(files.grades).forEach(paint);
      rows.querySelectorAll('[data-dl]').forEach(b => b.onclick = () => download(b.dataset.dl));
      rows.querySelectorAll('[data-dlx]').forEach(b => b.onclick = () => { jobs[b.dataset.dlx].cancel = true; });
      rows.querySelectorAll('[data-dlr]').forEach(b => b.onclick = () => modal(`<h3>Remove Level ${b.dataset.dlr - 1} audio?</h3><p>Lessons will need the internet again for this level.</p>`, () => remove(b.dataset.dlr), 'Remove'));
    }).catch(() => { const rows = el.querySelector('#dlRows'); if (rows) rows.innerHTML = '<p class="muted">Offline audio is not available in this browser.</p>'; });
  }
  window.LSP_PWA = { box };
  // the home page was drawn before this file loaded: fill its box now
  const first = document.getElementById('appBox'); if (first) box(first);
})();
