/* =====================================================================
   v1.4 — ACCOUNTS (kept on this device), SETTINGS and UPDATES
   • Teacher / parent account: username + password. Only a salted
     PBKDF2-SHA256 hash is stored (600,000 rounds), never the password.
     A one-time recovery code resets a forgotten password.
   • Students: name + class + 4-digit PIN (hashed the same way).
   • Wrong tries: after 5, a waiting time that doubles each time.
   • Automatic sign-out after a time without activity.
   • Backups are encrypted with the teacher password (AES-GCM-256).
   ===================================================================== */

/* ---------- Security helpers (Web Crypto; a small built-in SHA-256 is the fallback) ---------- */
const SHA_K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
function sha256js(m) {
  const H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  const l = m.length, nb = ((l + 72) >> 6) << 6, b = new Uint8Array(nb); b.set(m); b[l] = 0x80;
  const dv = new DataView(b.buffer); dv.setUint32(nb - 4, (l * 8) >>> 0); dv.setUint32(nb - 8, Math.floor(l / 536870912));
  const w = new Int32Array(64);
  for (let o = 0; o < nb; o += 64) {
    for (let i = 0; i < 16; i++) w[i] = dv.getInt32(o + i * 4);
    for (let i = 16; i < 64; i++) { const x = w[i - 15], y = w[i - 2]; w[i] = (((x >>> 7 | x << 25) ^ (x >>> 18 | x << 14) ^ (x >>> 3)) + w[i - 16] + ((y >>> 17 | y << 15) ^ (y >>> 19 | y << 13) ^ (y >>> 10)) + w[i - 7]) | 0; }
    let a = H[0], bb = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
    for (let i = 0; i < 64; i++) {
      const t1 = (h + ((e >>> 6 | e << 26) ^ (e >>> 11 | e << 21) ^ (e >>> 25 | e << 7)) + ((e & f) ^ (~e & g)) + SHA_K[i] + w[i]) | 0;
      const t2 = (((a >>> 2 | a << 30) ^ (a >>> 13 | a << 19) ^ (a >>> 22 | a << 10)) + ((a & bb) ^ (a & c) ^ (bb & c))) | 0;
      h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = bb; bb = a; a = (t1 + t2) | 0;
    }
    H[0] = (H[0] + a) | 0; H[1] = (H[1] + bb) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0; H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
  }
  const out = new Uint8Array(32), ov = new DataView(out.buffer); H.forEach((x, i) => ov.setInt32(i * 4, x)); return out;
}
function pbkdf2js(pw, salt, iter) {
  let key = pw.length > 64 ? sha256js(pw) : pw; const k = new Uint8Array(64); k.set(key);
  const ip = k.map(x => x ^ 0x36), op = k.map(x => x ^ 0x5c);
  const hmac = msg => { const a = new Uint8Array(64 + msg.length); a.set(ip); a.set(msg, 64); const ih = sha256js(a); const o = new Uint8Array(96); o.set(op); o.set(ih, 64); return sha256js(o); };
  const s1 = new Uint8Array(salt.length + 4); s1.set(salt); s1[salt.length + 3] = 1;
  let u = hmac(s1); const t = u.slice();
  for (let i = 1; i < iter; i++) { u = hmac(u); for (let j = 0; j < 32; j++) t[j] ^= u[j]; }
  return t;
}
const Sec = {
  te: new TextEncoder(),
  rnd(n) { const a = new Uint8Array(n); crypto.getRandomValues(a); return a; },
  b64(a) { let s = ''; for (let i = 0; i < a.length; i++) s += String.fromCharCode(a[i]); return btoa(s); },
  unb64(s) { const b = atob(s), a = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a; },
  subtle() { try { return window.crypto && crypto.subtle && window.isSecureContext !== false ? crypto.subtle : null; } catch (e) { return null; } },
  async bits(secret, salt, iter) {
    const S = this.subtle();
    if (S) { const k = await S.importKey('raw', this.te.encode(secret), 'PBKDF2', false, ['deriveBits']); return new Uint8Array(await S.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: iter }, k, 256)); }
    await sleep(20); return pbkdf2js(this.te.encode(secret), salt, iter);
  },
  async make(secret, iter) { if (!this.subtle()) iter = Math.min(iter, 120000); const salt = this.rnd(16); return { a: 'pbkdf2-sha256', i: iter, s: this.b64(salt), h: this.b64(await this.bits(secret, salt, iter)) }; },
  async check(secret, rec) {
    if (!rec || !rec.h || !rec.s) return false;
    const h = await this.bits(String(secret), this.unb64(rec.s), rec.i), w = this.unb64(rec.h);
    let d = h.length ^ w.length; for (let i = 0; i < h.length; i++) d |= h[i] ^ (w[i] | 0); return d === 0;   // constant-time compare
  },
  async key(pass, salt, iter) { const S = this.subtle(); const k = await S.importKey('raw', this.te.encode(pass), 'PBKDF2', false, ['deriveKey']); return S.deriveKey({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: iter }, k, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']); },
  async seal(text, pass) { const salt = this.rnd(16), iv = this.rnd(12), i = 310000; const k = await this.key(pass, salt, i); const c = new Uint8Array(await this.subtle().encrypt({ name: 'AES-GCM', iv }, k, this.te.encode(text))); return { alg: 'AES-GCM-256 / PBKDF2-SHA256', i, s: this.b64(salt), iv: this.b64(iv), c: this.b64(c) }; },
  async open(o, pass) { const k = await this.key(pass, this.unb64(o.s), o.i); return new TextDecoder().decode(await this.subtle().decrypt({ name: 'AES-GCM', iv: this.unb64(o.iv) }, k, this.unb64(o.c))); },
  code() { const A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', r = this.rnd(12); let s = ''; for (let i = 0; i < 12; i++) { s += A[r[i] % 32]; if (i === 3 || i === 7) s += '-'; } return s; },
  normCode: c => String(c || '').toUpperCase().replace(/[^A-Z0-9]/g, '').replace(/O/g, '0').replace(/I/g, '1').replace(/(.{4})(.{4})(.{4})/, '$1-$2-$3')
};

/* ---------- Settings (this device) ---------- */
const SET_DEF = { rx: true, rxVoice: true, rxVol: 90, speed: 1, ts: 1, motion: true, cd: 2, classmode: false };
const SEC_DEF = { selfSignup: true, guest: true, idle: 30, tidle: 20 };
const Cfg = {
  get(k) { const s = Store.data.settings; return k in s ? s[k] : SET_DEF[k]; },
  put(k, v) { Store.data.settings[k] = v; Store.save(); this.apply(); },
  sec() { return Object.assign({}, SEC_DEF, Store.data.settings.sec || {}); },
  putSec(k, v) { const s = Store.data.settings.sec = Store.data.settings.sec || {}; s[k] = v; Store.save(); },
  upd() { return Object.assign({ auto: true }, Store.data.settings.upd || {}); },
  putUpd(k, v) { const s = Store.data.settings.upd = Store.data.settings.upd || {}; s[k] = v; Store.save(); },
  apply() {
    document.documentElement.style.setProperty('--ts', this.get('ts'));
    document.body.classList.toggle('nomotion', this.get('motion') === false);
    AU.rate = +this.get('speed') || 1;
    if (RX.g) RX.g.gain.value = 0.9 * (this.get('rxVol') / 100);
  }
};

/* ---------- Accounts ---------- */
const ITER = { pass: 600000, pin: 100000, code: 100000 };
const T_AR = { four: 'اكتب 4 أرقام.', same: 'لا تستخدم الرقم نفسه 4 مرات.', seq: 'لا تستخدم أرقامًا متتالية مثل 1234.' };
const Auth = {
  get A() { const d = Store.data; if (!d.auth) d.auth = { v: 1, teacher: null, session: null, fails: {} }; d.auth.fails = d.auth.fails || {}; return d.auth; },
  ready() { return !!(Store.data.auth && Store.data.auth.teacher && Store.data.auth.teacher.pw); },
  user() { const s = this.A.session; return s && Store.data.profiles[s.id] ? Store.data.profiles[s.id] : null; },
  role() { const s = this.A.session; return s ? s.role : null; },
  isT() { return this.role() === 'teacher' && !!this.user(); },
  start(id, role) { const now = Date.now(); this.A.session = { id, role, at: now, last: now }; Store.data.current = id; delete this.A.fails[id]; Store.save(); },
  signOut(why) { AU.stop(); stopAllRec(); RX.hush(); this.A.session = null; Store.data.current = 'guest'; Store.save(); S.signedOut = why || ''; for (const k of Object.keys(S)) if (k !== 'signedOut') delete S[k]; S.view = 'signin'; render(); },
  locked(id) { const f = this.A.fails[id]; return f && f.until > Date.now() ? Math.ceil((f.until - Date.now()) / 1000) : 0; },
  fail(id, teacher) {
    const f = this.A.fails[id] || (this.A.fails[id] = { n: 0, until: 0 }); f.n++;
    if (f.n >= 5) { const base = teacher ? 60 : 30, cap = teacher ? 1800 : 900; f.until = Date.now() + Math.min(cap, base * 2 ** (f.n - 5)) * 1000; }
    Store.save(); return { bad: true, wait: this.locked(id), left: Math.max(0, 5 - f.n) };
  },
  pinRule(p) {
    if (!/^\d{4}$/.test(p)) return 'four'; if (/^(\d)\1{3}$/.test(p)) return 'same';
    const d = [...p].map(Number), up = d.every((x, i) => !i || x === d[i - 1] + 1), dn = d.every((x, i) => !i || x === d[i - 1] - 1);
    return up || dn ? 'seq' : '';
  },
  passRule(p, user) {
    if (p.length < 8) return ['Use at least 8 characters.', 'استخدم 8 أحرف على الأقل.'];
    if (!/[A-Za-z؀-ۿ]/.test(p) || !/\d/.test(p)) return ['Use letters and numbers.', 'استخدم حروفًا وأرقامًا.'];
    const low = p.toLowerCase();
    if (/^(password|passw0rd|qwerty|abc|12345|admin|teacher|school|listenup)/.test(low) || /(.)\1{3,}/.test(p) || (user && user.length > 2 && low.includes(user.toLowerCase()))) return ['This password is too easy to guess.', 'كلمة المرور هذه سهلة التخمين.'];
    return null;
  },
  strength(p) { let s = 0; if (p.length >= 8) s++; if (p.length >= 12) s++; if (/[a-z]/.test(p) && /[A-Z]/.test(p)) s++; if (/\d/.test(p) && /[^A-Za-z0-9]/.test(p)) s++; return Math.min(4, s + (p.length >= 16 ? 1 : 0)); },
  async createTeacher(name, user, pass) {
    const code = Sec.code();
    this.A.teacher = { name: name.trim(), user: user.trim().toLowerCase(), pw: await Sec.make(pass, ITER.pass), rc: await Sec.make(code, ITER.code), created: Date.now() };
    const P = Store.data.profiles; P.teacher = Object.assign(P.teacher || { progress: {} }, { id: 'teacher', name: name.trim(), cls: '', role: 'teacher' });
    this.start('teacher', 'teacher'); return code;
  },
  async teacherIn(user, pass) {
    const w = this.locked('teacher'); if (w) return { wait: w };
    const T = this.A.teacher, okU = !!T && String(user).trim().toLowerCase() === T.user, okP = await Sec.check(pass, T && T.pw);
    if (!(okU && okP)) return this.fail('teacher', true);
    this.start('teacher', 'teacher'); return { ok: true };
  },
  async verifyTeacher(pass) {
    const w = this.locked('teacher'); if (w) return { wait: w };
    if (await Sec.check(pass, this.A.teacher && this.A.teacher.pw)) { delete this.A.fails.teacher; Store.save(); return { ok: true }; }
    return this.fail('teacher', true);
  },
  async studentIn(id, pin) {
    const w = this.locked(id); if (w) return { wait: w };
    const p = Store.data.profiles[id]; if (!p) return { bad: true };
    if (!(await Sec.check(pin, p.pin))) return this.fail(id, false);
    this.start(id, id === 'teacher' ? 'teacher' : 'student'); return { ok: true };
  },
  async setPin(id, pin) { Store.data.profiles[id].pin = await Sec.make(pin, ITER.pin); Store.save(); },
  async signUp(name, cls, pin) {
    const id = 'p' + Date.now().toString(36) + [...Sec.rnd(2)].map(x => x.toString(16).padStart(2, '0')).join('');
    Store.data.profiles[id] = { id, name: name.trim(), cls: cls.trim(), progress: {}, created: Date.now(), pin: await Sec.make(pin, ITER.pin) };
    this.start(id, 'student'); return id;
  },
  guestIn() { if (!Cfg.sec().guest) return false; this.start('guest', 'guest'); return true; },
  async recover(code, pass) {
    const w = this.locked('recover'); if (w) return { wait: w };
    const T = this.A.teacher; if (!T || !(await Sec.check(Sec.normCode(code), T.rc))) return this.fail('recover', true);
    const nc = Sec.code(); T.pw = await Sec.make(pass, ITER.pass); T.rc = await Sec.make(nc, ITER.code); delete this.A.fails.teacher; delete this.A.fails.recover;
    this.start('teacher', 'teacher'); return { ok: true, code: nc };
  },
  async newCode() { const nc = Sec.code(); this.A.teacher.rc = await Sec.make(nc, ITER.code); Store.save(); return nc; },
  dupName(name, cls, skip) { const n = name.trim().toLowerCase(), c = (cls || '').trim().toLowerCase(); return Object.values(Store.data.profiles).some(p => p.id !== skip && p.id !== 'guest' && p.id !== 'teacher' && p.name.trim().toLowerCase() === n && (p.cls || '').trim().toLowerCase() === c); },
  students() { return Object.values(Store.data.profiles).filter(p => p.id !== 'guest' && p.id !== 'teacher').sort((a, b) => (a.cls || '').localeCompare(b.cls || '') || a.name.localeCompare(b.name)); },
  // activity and automatic sign-out
  lastSave: 0,
  touch() { const s = this.A.session; if (!s) return; s.last = Date.now(); if (s.last - this.lastSave > 20000) { this.lastSave = s.last; Store.save(); } },
  idleMin() { const s = this.A.session; if (!s) return 0; const c = Cfg.sec(); return s.role === 'teacher' ? +c.tidle : +c.idle; },
  idleCheck(boot) {
    const s = this.A.session; if (!s) return; const lim = this.idleMin(); if (!(lim > 0)) return;
    const busy = !boot && ((AU.el && !AU.el.paused) || Active.rec || (Mic.mr && Mic.mr.state === 'recording'));
    if (busy) { s.last = Date.now(); return; }
    if (Date.now() - s.last > lim * 60000) this.signOut(`You were signed out after ${lim} minutes without activity.`);
  }
};
['pointerdown', 'keydown', 'wheel', 'touchstart'].forEach(ev => document.addEventListener(ev, () => Auth.touch(), { capture: true, passive: true }));
setInterval(() => Auth.idleCheck(false), 30000);
document.addEventListener('visibilitychange', () => { if (!document.hidden) Auth.idleCheck(false); });

/* ---------- small UI helpers ---------- */
const avCol = n => ['#2F7BEA', '#E2558C', '#F08A24', '#16A34A', '#A855F7', '#0EA5E9'][((n || '?').charCodeAt(0) || 0) % 6];
const avHTML = p => `<span class="av" style="background:${p.id === 'guest' ? '#94A3B8' : p.id === 'teacher' ? '#1B4FA3' : avCol(p.name)}">${p.id === 'teacher' ? '🧑‍🏫' : esc((p.name || '?')[0].toUpperCase())}</span>`;
const mmss = s => Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
function sheet(html, cls) {
  const m = document.createElement('div'); m.className = 'modal ' + (cls || ''); m.innerHTML = `<div class="card">${html}</div>`;
  document.body.appendChild(m); m.addEventListener('click', e => { if (e.target === m && !m.dataset.sticky) m.remove(); });
  return m;
}
function pwField(id, label, ar, auto) {
  return `<div class="field"><label for="${id}">${label} <span class="ar">${ar}</span></label><div class="pwrow"><input type="password" id="${id}" autocomplete="${auto || 'current-password'}" autocapitalize="off" spellcheck="false" maxlength="128"><button type="button" class="btn sm sec eye" data-eye="${id}" aria-label="Show password">👁</button></div></div>`;
}
function bindEyes(root) { $$('[data-eye]', root).forEach(b => b.onclick = () => { const i = $('#' + b.dataset.eye, root); i.type = i.type === 'password' ? 'text' : 'password'; b.textContent = i.type === 'password' ? '👁' : '🙈'; }); }
function meterHTML(id) { return `<div class="meter5" id="${id}" aria-hidden="true"><i></i><i></i><i></i><i></i></div>`; }
function bindMeter(inp, box) { inp.addEventListener('input', () => { const s = Auth.strength(inp.value), col = ['#E5484D', '#F08A24', '#E8B400', '#1FA463', '#1FA463'][s]; $$('i', box).forEach((x, i) => x.style.background = i < Math.max(1, s) && inp.value ? col : ''); }); }

/* PIN pad: big keys for young children. check(pin) returns {ok} | {bad, left, wait} | {msg}. */
function pinPad(o) {
  return new Promise(done => {
    const m = sheet(`<div class="pinhead">${o.who ? avHTML(o.who) : ''}<div><h3 style="margin:0">${esc(o.title)}</h3>${o.ar ? `<span class="ar">${esc(o.ar)}</span>` : ''}</div></div>
      ${o.sub ? `<p class="muted" style="margin:.4rem 0 0;text-align:center">${o.sub}</p>` : ''}
      <div class="pindots" aria-live="polite">${'<i></i>'.repeat(4)}</div><p class="pinmsg" role="alert"></p>
      <div class="pinpad">${[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => `<button type="button" data-k="${n}">${n}</button>`).join('')}<button type="button" data-k="x" aria-label="Cancel">✕</button><button type="button" data-k="0">0</button><button type="button" data-k="b" aria-label="Delete">⌫</button></div>`, 'pinmodal');
    let pin = '', busy = false, tm = null; const dots = $$('.pindots i', m), msg = $('.pinmsg', m);
    const paint = () => dots.forEach((d, i) => d.classList.toggle('on', i < pin.length));
    const say = (en, ar, bad) => { msg.innerHTML = `${esc(en)}${ar ? ` <span class="ar">${esc(ar)}</span>` : ''}`; msg.classList.toggle('bad', !!bad); };
    const close = v => { clearInterval(tm); document.removeEventListener('keydown', kd, true); m.remove(); done(v); };
    const waitFor = w => { m.classList.add('wait'); const t0 = Date.now(); const tick = () => { const left = w - Math.floor((Date.now() - t0) / 1000); if (left <= 0) { clearInterval(tm); m.classList.remove('wait'); say('Try again now.', 'حاول الآن.'); return; } say(`Too many tries. Wait ${mmss(left)}.`, `محاولات كثيرة. انتظر ${mmss(left)}.`, true); }; tick(); clearInterval(tm); tm = setInterval(tick, 1000); };
    const key = async k => {
      if (busy || m.classList.contains('wait')) { if (k === 'x') close(null); return; }
      if (k === 'x') return close(null);
      if (k === 'b') { pin = pin.slice(0, -1); paint(); return; }
      if (pin.length >= 4) return; pin += k; paint();
      if (pin.length < 4) return;
      busy = true; m.classList.add('busy'); const r = await o.check(pin); busy = false; m.classList.remove('busy');
      if (r && r.ok) return close(r.value != null ? r.value : pin);
      pin = ''; paint(); const box = $('.card', m); box.classList.remove('shake'); void box.offsetWidth; box.classList.add('shake');
      if (r && r.wait) waitFor(r.wait);
      else if (r && r.msg) say(r.msg[0], r.msg[1], true);
      else say(r && r.left != null ? `Wrong PIN. ${r.left} ${r.left === 1 ? 'try' : 'tries'} left.` : 'Wrong PIN.', 'رمز خاطئ.', true);
    };
    const kd = e => { if (/^\d$/.test(e.key)) { key(e.key); e.preventDefault(); } else if (e.key === 'Backspace') { key('b'); e.preventDefault(); } else if (e.key === 'Escape') { key('x'); e.preventDefault(); } };
    document.addEventListener('keydown', kd, true);
    $$('[data-k]', m).forEach(b => b.onclick = () => key(b.dataset.k));
    m.dataset.sticky = '1';
    if (o.wait) waitFor(o.wait);
  });
}
// choose a new PIN twice; resolves with the PIN or null
async function newPinFlow(who, title) {
  let first = null;
  const p = await pinPad({ who, title: title || 'Choose your 4-digit PIN', ar: 'اختر رمزًا من 4 أرقام', sub: 'Keep it secret. <span class="ar">احتفظ به سرًّا.</span>', check: async pin => { const r = Auth.pinRule(pin); return r ? { msg: [r === 'four' ? 'Type 4 numbers.' : r === 'same' ? 'Do not use the same number 4 times.' : 'Do not use numbers in a row like 1234.', T_AR[r]] } : { ok: true }; } });
  if (!p) return null; first = p;
  return pinPad({ who, title: 'Type the same PIN again', ar: 'اكتب الرمز نفسه مرة أخرى', check: async pin => pin === first ? { ok: true } : { msg: ['The two PINs are different. Try again.', 'الرمزان مختلفان. حاول مرة أخرى.'] } });
}

/* ---------- First run: create the teacher (or parent) account ---------- */
VIEWS.setup = m => {
  const had = Auth.students().length;
  m.innerHTML = `<section class="auth"><div class="card">
    <div class="auth-head">${LOGO}<div><h1>Welcome to Listen Up! Speak Out!</h1><span class="ar">مرحبًا بك في برنامج Listen Up! Speak Out!</span></div></div>
    <p>First, create the <b>teacher or parent account</b>. It protects the teacher dashboard, the settings and the backups. Students then sign up with their name and a 4-digit PIN.${had ? ` <b>Your ${had} student${had === 1 ? '' : 's'} and all progress are kept.</b>` : ''}</p>
    <p class="ar ar-block">أولًا، أنشئ حساب المعلم أو ولي الأمر. يحمي هذا الحساب لوحة المعلم والإعدادات والنسخ الاحتياطية، ثم يسجّل الطلاب بأسمائهم ورمز من 4 أرقام.</p>
    <form id="stF" autocomplete="on" novalidate>
      <div class="field"><label for="stN">Your name <span class="ar">اسمك</span></label><input type="text" id="stN" maxlength="40" autocomplete="name" placeholder="e.g., Mr. Waleed Youssef"></div>
      <div class="field"><label for="stU">Username <span class="ar">اسم المستخدم</span></label><input type="text" id="stU" maxlength="24" autocomplete="username" autocapitalize="off" spellcheck="false" placeholder="e.g., waleed"><small class="muted">3–24 letters or numbers (a dot, dash or underscore is allowed).</small></div>
      ${pwField('stP', 'Password', 'كلمة المرور', 'new-password')}${meterHTML('stM')}<small class="muted">At least 8 characters, with letters and numbers.</small>
      ${pwField('stP2', 'Type the password again', 'أعد كتابة كلمة المرور', 'new-password')}
      <p class="pinmsg bad" id="stE" role="alert"></p>
      <button class="btn" type="submit" id="stB">🔐 Create the teacher account</button>
    </form>
    <p class="secnote">🔒 The password is never stored. The app keeps only a salted PBKDF2-SHA256 hash, and all accounts and progress stay on this device. <span class="ar ar-block">لا تُحفظ كلمة المرور نفسها، بل بصمة مشفّرة فقط، وتبقى جميع الحسابات والتقدّم على هذا الجهاز.</span></p>
  </div></section>`;
  bindEyes(m); bindMeter($('#stP', m), $('#stM', m));
  $('#stF', m).onsubmit = async e => {
    e.preventDefault(); const E = $('#stE', m), n = $('#stN', m).value.trim(), u = $('#stU', m).value.trim(), p = $('#stP', m).value, p2 = $('#stP2', m).value;
    const err = (en, ar) => { E.innerHTML = `${esc(en)} <span class="ar">${esc(ar)}</span>`; };
    if (n.length < 2) return err('Type your name.', 'اكتب اسمك.');
    if (!/^[A-Za-z0-9._-]{3,24}$/.test(u)) return err('The username needs 3–24 letters or numbers.', 'يحتاج اسم المستخدم إلى 3–24 حرفًا أو رقمًا.');
    const pr = Auth.passRule(p, u); if (pr) return err(pr[0], pr[1]);
    if (p !== p2) return err('The two passwords are different.', 'كلمتا المرور مختلفتان.');
    const B = $('#stB', m); B.disabled = true; B.textContent = 'Creating the account…';
    const code = await Auth.createTeacher(n, u, p);
    $('#stP', m).value = $('#stP2', m).value = '';
    showRecovery(m, code, () => go('home'));
  };
};
function showRecovery(m, code, next) {
  m.innerHTML = `<section class="auth"><div class="card">
    <div class="auth-head"><span class="big">🗝️</span><div><h1>Save your recovery code</h1><span class="ar">احفظ رمز الاسترداد</span></div></div>
    <p>If you forget the teacher password, this code lets you choose a new one. It is shown <b>only once</b>. Write it down or save it, and keep it in a safe place.</p>
    <p class="ar ar-block">إذا نسيت كلمة مرور المعلم، يتيح لك هذا الرمز اختيار كلمة جديدة. يظهر مرة واحدة فقط، فاكتبه أو احفظه في مكان آمن.</p>
    <div class="rcode" id="rc">${code}</div>
    <div class="ctrls" style="margin-top:10px"><button class="btn sm sec" id="rcC">📋 Copy</button><button class="btn sm sec" id="rcS">💾 Save as a file</button><span class="muted" id="rcm"></span></div>
    <label class="chk"><input type="checkbox" id="rcOk"> I have saved my recovery code. <span class="ar">حفظتُ رمز الاسترداد.</span></label>
    <div class="navrow" style="justify-content:flex-end"><button class="btn" id="rcN" disabled>Continue →</button></div>
  </div></section>`;
  const txt = `Listen Up! Speak Out! — teacher recovery code\n${code}\nKeep this code private. Created ${new Date().toLocaleString()}.`;
  $('#rcC', m).onclick = () => copyText(code).then(() => $('#rcm', m).textContent = 'Copied.', () => $('#rcm', m).textContent = 'Copy is not allowed here — write it down.');
  $('#rcS', m).onclick = () => { if (saveFile('listen-up-recovery-code.txt', txt, 'text/plain')) $('#rcm', m).textContent = 'Saved.'; else $('#rcm', m).textContent = 'Saving is blocked here — write it down.'; };
  $('#rcOk', m).onchange = e => { $('#rcN', m).disabled = !e.target.checked; };
  $('#rcN', m).onclick = next;
}

/* ---------- Sign in ---------- */
VIEWS.signin = m => {
  const sec = Cfg.sec(), list = Auth.students(), classes = [...new Set(list.map(p => p.cls || ''))].filter(Boolean).sort();
  const f = S.cls != null && classes.includes(S.cls) ? S.cls : '';
  const shown = f ? list.filter(p => (p.cls || '') === f) : list;
  m.innerHTML = `<section class="auth wide"><div class="card">
    <div class="auth-head">${LOGO}<div><h1>Who is learning today?</h1><span class="ar">من يتعلّم اليوم؟</span></div></div>
    ${S.signedOut ? `<p class="note">🔒 ${esc(S.signedOut)} <span class="ar">تم تسجيل خروجك تلقائيًا.</span></p>` : ''}
    <p class="muted" style="margin:.2rem 0 0">Tap your name, then type your PIN. <span class="ar">اضغط على اسمك ثم اكتب رمزك.</span></p>
    ${classes.length > 1 ? `<div class="seg" id="clsF" style="margin-top:12px"><button data-c="" class="${f ? '' : 'on'}">All</button>${classes.map(c => `<button data-c="${esc(c)}" class="${f === c ? 'on' : ''}">${esc(c)}</button>`).join('')}</div>` : ''}
    <div class="ptiles">${shown.map(p => `<button class="ptile" data-sid="${esc(p.id)}">${avHTML(p)}<span>${esc(p.name)}<small>${esc(p.cls || '')}${p.pin ? '' : (p.cls ? ' · ' : '') + 'new PIN'}</small></span></button>`).join('')}
      ${sec.guest ? `<button class="ptile" data-sid="guest">${avHTML({ id: 'guest', name: 'Guest' })}<span>Guest<small>practice only</small></span></button>` : ''}</div>
    ${list.length ? '' : '<p class="muted" style="margin-top:12px">No students yet. Press “New student” to sign up. <span class="ar">لا يوجد طلاب بعد. اضغط «طالب جديد» للتسجيل.</span></p>'}
    <div class="ctrls" style="justify-content:flex-start;margin-top:16px">
      ${sec.selfSignup ? '<button class="btn" id="suB">➕ New student — sign up <span class="ar" style="color:#fff">تسجيل طالب جديد</span></button>' : '<span class="muted">New student? Ask your teacher to add you. <span class="ar">اطلب من معلمك إضافتك.</span></span>'}
      <button class="btn sec" id="tB">🔑 Teacher sign in <span class="ar">دخول المعلم</span></button>
    </div></div>
    <p class="foot">Listen Up! Speak Out! · Designed by Mr. Waleed Youssef · v${APP_VER} · 🔒 accounts stay on this device</p></section>`;
  $$('#clsF [data-c]', m).forEach(b => b.onclick = () => { S.cls = b.dataset.c; VIEWS.signin(m); });
  $$('[data-sid]', m).forEach(b => b.onclick = () => studentSignIn(b.dataset.sid));
  const su = $('#suB', m); if (su) su.onclick = signUpFlow;
  $('#tB', m).onclick = () => teacherSignIn();
};
async function studentSignIn(id) {
  if (id === 'guest') { if (Auth.guestIn()) go('home'); return; }
  const p = Store.data.profiles[id]; if (!p) return;
  if (!p.pin) {   // first sign-in after an update, or the teacher reset the PIN
    const pin = await newPinFlow(p, `Hello ${p.name}! Choose your PIN`); if (!pin) return;
    await Auth.setPin(id, pin); Auth.start(id, 'student'); go('home'); return;
  }
  const r = await pinPad({ who: p, title: `Hello ${p.name}!`, ar: 'اكتب رمزك', sub: 'Type your 4-digit PIN.', wait: Auth.locked(id), check: pin => Auth.studentIn(id, pin) });
  if (r) go('home');
}
async function signUpFlow() {
  if (!Cfg.sec().selfSignup) return;
  const m = sheet(`<h3>New student <span class="ar">طالب جديد</span></h3>
    <form id="suF" novalidate><div class="field"><label for="suN">Your name <span class="ar">اسمك</span></label><input type="text" id="suN" maxlength="30" autocomplete="off" placeholder="e.g., Omar Ali"></div>
    <div class="field"><label for="suC">Your class <span class="ar">فصلك</span></label><input type="text" id="suC" maxlength="12" autocomplete="off" placeholder="e.g., 4B"></div>
    <p class="pinmsg bad" id="suE" role="alert"></p>
    <div class="navrow"><button type="button" class="btn sec" id="suX">Cancel</button><button class="btn" type="submit">Next: choose a PIN →</button></div></form>`);
  $('#suN', m).focus(); $('#suX', m).onclick = () => m.remove();
  $('#suF', m).onsubmit = async e => {
    e.preventDefault(); const n = $('#suN', m).value.trim(), c = $('#suC', m).value.trim(), E = $('#suE', m);
    if (n.length < 2) { E.innerHTML = 'Type your name. <span class="ar">اكتب اسمك.</span>'; return; }
    if (Auth.dupName(n, c)) { E.innerHTML = 'This name is already here. Add your class or your family name. <span class="ar">هذا الاسم موجود. أضف فصلك أو اسم عائلتك.</span>'; return; }
    m.remove(); const pin = await newPinFlow({ id: 'new', name: n }); if (!pin) return;
    await Auth.signUp(n, c, pin); go('home'); setTimeout(() => celebrate(['Welcome, ' + n + '!', 'أهلًا بك!']), 300);
  };
}
function teacherSignIn(after) {
  const T = Auth.A.teacher || {};
  const m = sheet(`<h3>🔑 Teacher sign in <span class="ar">دخول المعلم</span></h3>
    <form id="tiF" novalidate><div class="field"><label for="tiU">Username <span class="ar">اسم المستخدم</span></label><input type="text" id="tiU" maxlength="24" autocomplete="username" autocapitalize="off" spellcheck="false"></div>
    ${pwField('tiP', 'Password', 'كلمة المرور')}
    <p class="pinmsg bad" id="tiE" role="alert"></p>
    <div class="navrow"><button type="button" class="btn sec" id="tiX">Cancel</button><button class="btn" type="submit" id="tiB">Sign in</button></div>
    <p style="margin:.6rem 0 0;text-align:center"><button type="button" class="linkbtn" id="tiR">Forgot the password? <span class="ar">نسيت كلمة المرور؟</span></button></p></form>`);
  bindEyes(m); $('#tiU', m).focus(); $('#tiX', m).onclick = () => m.remove();
  let tm = null; const E = $('#tiE', m), B = $('#tiB', m);
  const wait = w => { B.disabled = true; const t0 = Date.now(); clearInterval(tm); const tick = () => { const l = w - Math.floor((Date.now() - t0) / 1000); if (l <= 0) { clearInterval(tm); B.disabled = false; E.textContent = ''; return; } E.innerHTML = `Too many tries. Wait ${mmss(l)}. <span class="ar">انتظر ${mmss(l)}.</span>`; }; tick(); tm = setInterval(tick, 1000); };
  if (Auth.locked('teacher')) wait(Auth.locked('teacher'));
  $('#tiF', m).onsubmit = async e => {
    e.preventDefault(); if (B.disabled) return; B.disabled = true; B.textContent = 'Checking…';
    const r = await Auth.teacherIn($('#tiU', m).value, $('#tiP', m).value); B.textContent = 'Sign in'; B.disabled = false;
    if (r.ok) { clearInterval(tm); m.remove(); if (after) after(); else go('home'); return; }
    $('#tiP', m).value = ''; const c = $('.card', m); c.classList.remove('shake'); void c.offsetWidth; c.classList.add('shake');
    if (r.wait) wait(r.wait); else E.innerHTML = `The username or password is not right. ${r.left} ${r.left === 1 ? 'try' : 'tries'} left. <span class="ar">اسم المستخدم أو كلمة المرور غير صحيحة.</span>`;
  };
  $('#tiR', m).onclick = () => { clearInterval(tm); m.remove(); recoverFlow(after); };
}
function recoverFlow(after) {
  const m = sheet(`<h3>🗝️ Choose a new teacher password <span class="ar">اختر كلمة مرور جديدة</span></h3>
    <p class="muted" style="margin-top:.3rem">Type the recovery code you saved when the teacher account was made.</p>
    <form id="reF" novalidate><div class="field"><label for="reC">Recovery code <span class="ar">رمز الاسترداد</span></label><input type="text" id="reC" maxlength="20" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="XXXX-XXXX-XXXX"></div>
    ${pwField('reP', 'New password', 'كلمة المرور الجديدة', 'new-password')}${meterHTML('reM')}
    ${pwField('reP2', 'Type it again', 'أعد كتابتها', 'new-password')}
    <p class="pinmsg bad" id="reE" role="alert"></p>
    <div class="navrow"><button type="button" class="btn sec" id="reX">Cancel</button><button class="btn" type="submit" id="reB">Save the new password</button></div></form>`);
  bindEyes(m); bindMeter($('#reP', m), $('#reM', m)); $('#reX', m).onclick = () => m.remove();
  $('#reF', m).onsubmit = async e => {
    e.preventDefault(); const E = $('#reE', m), p = $('#reP', m).value;
    const pr = Auth.passRule(p, (Auth.A.teacher || {}).user); if (pr) { E.innerHTML = `${esc(pr[0])} <span class="ar">${esc(pr[1])}</span>`; return; }
    if (p !== $('#reP2', m).value) { E.innerHTML = 'The two passwords are different. <span class="ar">كلمتا المرور مختلفتان.</span>'; return; }
    const B = $('#reB', m); B.disabled = true; B.textContent = 'Checking…';
    const r = await Auth.recover($('#reC', m).value, p); B.disabled = false; B.textContent = 'Save the new password';
    if (r.ok) { m.remove(); const v = document.createElement('div'); showRecovery(v, r.code, () => { v.remove(); if (after) after(); else go('home'); }); v.className = 'modal'; v.firstElementChild.classList.add('in-modal'); document.body.appendChild(v); return; }
    E.innerHTML = r.wait ? `Too many tries. Wait ${mmss(r.wait)}.` : `This recovery code is not right. ${r.left} ${r.left === 1 ? 'try' : 'tries'} left. <span class="ar">رمز الاسترداد غير صحيح.</span>`;
  };
}
// asks for the teacher password before a sensitive action; resolves true/false
function confirmTeacher(title, en, ar) {
  return new Promise(done => {
    const m = sheet(`<h3>${title}</h3>${en ? `<p>${en}</p>` : ''}${ar ? `<p class="ar ar-block">${ar}</p>` : ''}
      <form id="ctF" novalidate>${pwField('ctP', 'Teacher password', 'كلمة مرور المعلم')}<p class="pinmsg bad" id="ctE" role="alert"></p>
      <div class="navrow"><button type="button" class="btn sec" id="ctX">Cancel</button><button class="btn" type="submit" id="ctB">Confirm</button></div></form>`);
    bindEyes(m); $('#ctP', m).focus();
    $('#ctX', m).onclick = () => { m.remove(); done(false); };
    $('#ctF', m).onsubmit = async e => {
      e.preventDefault(); const B = $('#ctB', m); B.disabled = true; const r = await Auth.verifyTeacher($('#ctP', m).value); B.disabled = false;
      if (r.ok) { const pw = $('#ctP', m).value; m.remove(); done(pw); return; }
      $('#ctP', m).value = ''; $('#ctE', m).innerHTML = r.wait ? `Too many tries. Wait ${mmss(r.wait)}.` : `Wrong password. ${r.left} ${r.left === 1 ? 'try' : 'tries'} left. <span class="ar">كلمة مرور خاطئة.</span>`;
    };
  });
}
function userMenu() {
  const u = Auth.user(); if (!u) return;
  const role = Auth.isT() ? 'Teacher' : u.id === 'guest' ? 'Guest' : 'Student';
  const m = sheet(`<div class="pinhead">${avHTML(u)}<div><h3 style="margin:0">${esc(u.name)}</h3><span class="muted">${role}${u.cls ? ' · ' + esc(u.cls) : ''}</span></div></div>
    <div class="menu">
      <button data-a="settings">⚙️ Settings <span class="ar">الإعدادات</span></button>
      ${Auth.isT() ? '<button data-a="teacher">📊 Teacher dashboard <span class="ar">لوحة المعلم</span></button>' : ''}
      ${u.id !== 'guest' ? `<button data-a="pin">${Auth.isT() ? '🔐 Change my password' : '🔐 Change my PIN'} <span class="ar">${Auth.isT() ? 'تغيير كلمة المرور' : 'تغيير الرمز'}</span></button>` : ''}
      <button data-a="out">🚪 Sign out / switch user <span class="ar">تسجيل الخروج</span></button>
    </div>`, 'menumodal');
  $$('[data-a]', m).forEach(b => b.onclick = () => { m.remove(); const a = b.dataset.a; if (a === 'out') Auth.signOut(); else if (a === 'pin') go('settings', { focus: 'acct' }); else go(a); });
}

/* ---------- Updates ---------- */
const SITE = 'https://mrwaleedyoussif.github.io/listen-up-speak-out/';
const REL_PAGE = 'https://github.com/mrwaleedyoussif/listen-up-speak-out/releases/latest';
const vcmp = (a, b) => { const x = String(a || 0).split('.').map(n => parseInt(n, 10) || 0), y = String(b || 0).split('.').map(n => parseInt(n, 10) || 0); for (let i = 0; i < 3; i++) { const d = (x[i] || 0) - (y[i] || 0); if (d) return d; } return 0; };
const openExt = url => { try { window.open(url, '_blank', 'noopener'); } catch (e) { location.href = url; } };
const Upd = {
  st: 'idle', info: null, ver: null, pct: 0, err: '', how: null, desk: null,
  kind() {
    if (PLAT === 'electron') return window.lspDesktop && window.lspDesktop.update ? 'desktop' : 'link';
    if (NATIVE) return PLAT;                                   // 'android' | 'ios'
    return window.LSP_SW && LSP_SW.ok ? 'web' : 'link';        // 'link': the offline ZIP folder
  },
  auto() { return Cfg.upd().auto !== false; },
  set(st, o) { this.st = st; Object.assign(this, o || {}); this.paint(); },
  paint() {
    const b = $('#updT'); if (b) { b.classList.toggle('has', this.st === 'available' || this.st === 'ready'); b.classList.toggle('busy', this.st === 'checking' || this.st === 'downloading'); b.title = this.label(); }
    $$('.updbox').forEach(x => { x.innerHTML = this.html(); this.bind(x); });
  },
  label() { return { checking: 'Checking for updates…', downloading: 'Downloading the update…', available: `Version ${this.ver} is available`, ready: 'The update is ready', none: 'You have the latest version', error: 'Could not check for updates' }[this.st] || 'Check for updates'; },
  notes() { const n = this.info && this.info.notes; if (!n || !n.en || !n.en.length) return ''; return `<div class="updnotes"><b>What’s new <span class="ar">ما الجديد</span></b><ul>${n.en.map((x, i) => `<li>${esc(x)}${n.ar && n.ar[i] ? `<span class="ar ar-block">${esc(n.ar[i])}</span>` : ''}</li>`).join('')}</ul></div>`; },
  html() {
    const k = this.kind(), v = this.ver ? esc(this.ver) : '';
    let line = '', btn = '<button class="btn sm band" data-u="check">🔄 Check for updates</button>';
    if (this.st === 'checking') { line = '⏳ Checking for updates… <span class="ar">جارٍ البحث عن تحديث…</span>'; btn = ''; }
    else if (this.st === 'none') line = `✅ You have the latest version (${APP_VER}). <span class="ar">لديك أحدث إصدار.</span>`;
    else if (this.st === 'error') line = `⚠️ ${esc(this.err || 'Could not check for updates. Check the internet connection.')} <span class="ar">تعذّر البحث عن تحديث. تحقّق من الاتصال بالإنترنت.</span>`;
    else if (this.st === 'downloading') { line = `⬇️ Downloading version ${v}… ${this.pct ? this.pct + '%' : ''} <span class="ar">جارٍ تنزيل التحديث…</span><span class="bar" style="margin-top:6px"><i style="width:${this.pct || 5}%"></i></span>`; btn = ''; }
    else if (this.st === 'ready') { line = `✨ Version ${v} is ready. <span class="ar">التحديث جاهز.</span>`; btn = `<button class="btn sm ok" data-u="apply">${k === 'desktop' ? '🔁 Restart and update' : '✨ Update now'}</button>`; }
    else if (this.st === 'available') {
      line = `✨ Version ${v} is available. <span class="ar">يتوفر إصدار جديد.</span>`;
      if (k === 'android') { btn = this.how ? '<button class="btn sm ok" data-u="apply">⬇️ Download and install</button>' : ''; line += this.how ? '' : ' The Android file is not ready yet — try again in a few minutes.'; }
      else if (k === 'ios') btn = '<button class="btn sm ok" data-u="apply">📲 How to update</button>';
      else if (k === 'desktop') btn = '<button class="btn sm ok" data-u="apply">⬇️ Download the update</button>';
      else if (k === 'link') btn = '<button class="btn sm ok" data-u="apply">⬇️ Get the new version</button>';
      else btn = '<button class="btn sm ok" data-u="apply">✨ Update now</button>';
    }
    else line = `Version ${APP_VER}.`;
    return `<div class="updline">${line}</div><div class="ctrls" style="justify-content:flex-start;margin-top:8px">${btn}</div>${this.st === 'available' || this.st === 'ready' ? this.notes() : ''}`;
  },
  bind(x) { $$('[data-u]', x).forEach(b => b.onclick = () => b.dataset.u === 'check' ? this.check(true) : this.apply(true)); },
  async fetchInfo() {
    const url = (PLAT === 'web' && /^https?:$/.test(location.protocol) ? 'version.json' : SITE + 'version.json') + '?t=' + Date.now();
    const r = await fetch(url, { cache: 'no-store' }); if (!r.ok) throw new Error('HTTP ' + r.status); return r.json();
  },
  async check(manual) {
    if (this.st === 'checking' || this.st === 'downloading') return;
    if (this.st === 'ready' && !manual) return;
    const k = this.kind(); this.set('checking', { err: '' }); Cfg.putUpd('last', Date.now());
    try {
      if (k === 'desktop') return this.deskCheck(manual);
      let info = null; try { info = await this.fetchInfo(); } catch (e) { if (k !== 'web') throw e; }
      this.info = info || this.info; const v = info && info.version;
      if (k === 'web') {
        await LSP_SW.check();
        if (LSP_SW.waiting) return this.set('ready', { ver: v && vcmp(v, APP_VER) > 0 ? v : (this.ver || 'new') });
        if (v && vcmp(v, APP_VER) > 0) { this.set('downloading', { ver: v, pct: 0 }); const ok = await LSP_SW.waitReady(90000); return ok ? this.set('ready', { ver: v }) : this.set('available', { ver: v }); }
        return this.set('none');
      }
      if (!v || vcmp(v, APP_VER) <= 0) return this.set('none');
      const f = (info.files || {});
      const how = k === 'android' ? f.apk : k === 'ios' ? (f.ipa || REL_PAGE) : (f.portable || f.setup || REL_PAGE);
      this.set('available', { ver: v, how });
      if (!manual && this.auto() && Cfg.upd().seen !== v) { Cfg.putUpd('seen', v); this.prompt(); }
    } catch (e) { if (!manual) return this.set('idle'); this.set('error', { err: navigator.onLine === false ? 'You are offline.' : 'Could not check for updates. Check the internet connection.' }); }
  },
  async deskCheck(manual) {
    const D2 = window.lspDesktop.update;
    if (!this.desk) { this.desk = await D2.info().catch(() => ({})); D2.onEvent(ev => this.deskEvent(ev)); }
    if (!this.desk.can) {   // portable .exe: show the download page
      let info = null; try { info = await this.fetchInfo(); } catch (e) {}
      this.info = info; const v = info && info.version;
      if (v && vcmp(v, APP_VER) > 0) return this.set('available', { ver: v, how: (info.files || {}).portable || REL_PAGE, deskLink: true });
      return info ? this.set('none') : manual ? this.set('error', { err: 'Could not check for updates. Check the internet connection.' }) : this.set('idle');
    }
    try { this.info = await this.fetchInfo(); } catch (e) {}
    const r = await D2.check(this.auto() || manual);
    if (!r || !r.ok) return manual ? this.set('error', { err: 'Could not check for updates. Check the internet connection.' }) : this.set('idle');
    if (!r.newer) return this.set('none');
    this.set(this.auto() || manual ? 'downloading' : 'available', { ver: r.version, pct: 0 });
  },
  deskEvent(ev) {
    if (ev.type === 'progress') this.set('downloading', { pct: ev.percent });
    else if (ev.type === 'downloaded') { this.set('ready', { ver: ev.version }); if (!this.toasted) { this.toasted = true; this.toast(`✨ Version ${esc(ev.version)} is ready. It installs when you close the app.`, 'Restart now', () => this.apply(true)); } }
    else if (ev.type === 'error' && this.st === 'downloading') this.set('error', { err: 'The download stopped. Try again later.' });
  },
  async apply(manual) {
    const k = this.kind();
    if (k === 'web') {
      if (this.st !== 'ready') return this.check(true);
      this.toast('✨ Updating to the new version…'); setTimeout(() => LSP_SW.apply(), 400); return;
    }
    if (k === 'desktop' && !this.deskLink) {
      if (this.st === 'ready') { Store.save(); return window.lspDesktop.update.install(); }
      if (this.st === 'available') { this.set('downloading', { pct: 0 }); const ok = await window.lspDesktop.update.download(); if (!ok) this.set('error', { err: 'The download did not work. Try again later.' }); return; }
      return this.check(true);
    }
    if (this.st !== 'available') return this.check(true);
    if (k === 'ios') return modal(`<h3>📲 Update on iPhone or iPad</h3><p>Open the website in Safari: it always has the newest version. If you use the installed app, install the new version ${esc(this.ver)} the same way you installed the first one.</p><p class="ar ar-block">افتح الموقع في سفاري؛ فهو يحتوي دائمًا على أحدث إصدار. وإذا كنت تستخدم التطبيق المثبّت، فثبّت الإصدار الجديد بالطريقة نفسها.</p>`, () => openExt(SITE), 'Open the website');
    if (k === 'android') { Store.save(); openExt(this.how); return modal(`<h3>⬇️ Install the update</h3><ol><li>Wait until the download finishes (see the notification bar).</li><li>Open <b>Listen-Up-Speak-Out-${esc(this.ver)}.apk</b> and press <b>Update</b>.</li></ol><p>Android always asks you to confirm an update of an app that is not from the Play Store. All progress and accounts are kept.</p><p class="ar ar-block">انتظر انتهاء التنزيل، ثم افتح الملف واضغط «تحديث». يحتفظ التطبيق بجميع الحسابات والتقدّم.</p>`, null, 'OK'); }
    openExt(this.how || REL_PAGE);
  },
  prompt() { this.toast(`✨ Version ${esc(this.ver)} is available.`, this.kind() === 'android' ? 'Install' : 'See how', () => this.apply(true)); },
  toast(html, btn, onBtn) {
    const old = document.querySelector('.toast'); if (old) old.remove();
    const t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status');
    t.innerHTML = `<span>${html}</span>${btn ? `<button class="btn">${btn}</button>` : ''}<button class="iconbtn" aria-label="Close" style="background:transparent;border-color:#46506a;color:#fff">✕</button>`;
    document.body.appendChild(t); if (btn) t.querySelector('.btn').onclick = () => { t.remove(); onBtn(); };
    t.querySelector('.iconbtn').onclick = () => t.remove(); if (!btn) setTimeout(() => t.remove(), 4000);
  },
  // web: a new version was downloaded in the background
  webReady() {
    this.set('ready', { ver: this.ver || (this.info && this.info.version) || 'new' });
    if (this.auto()) this.safeApply(); else this.toast('✨ A new version is ready.', 'Update', () => this.apply(true));
  },
  safe() { return ['home', 'grade', 'unit', 'signin', 'setup', 'settings', 'teacher', 'studio'].includes(S.view || 'home') && !Active.rec && (!AU.el || AU.el.paused) && !document.querySelector('.modal'); },
  safeApply() { if (this.kind() === 'web' && this.st === 'ready' && this.auto() && this.safe()) this.apply(true); },
  boot() {
    if (this.kind() === 'web') LSP_SW.onReady(() => this.webReady());
    const last = Cfg.upd().last || 0;
    if (this.auto() && Date.now() - last > (this.kind() === 'web' ? 0 : 6 * 3600 * 1000)) setTimeout(() => this.check(false), 4000);
    setInterval(() => { if (this.auto()) this.check(false); }, 6 * 3600 * 1000);
  },
  panel() { const m = sheet(`<h3>🔄 Updates <span class="ar">التحديثات</span></h3><div class="updbox"></div><p class="muted" style="margin:.8rem 0 0;font-size:.85rem">Automatic updates: <b>${this.auto() ? 'on' : 'off'}</b> (change it in ⚙️ Settings).</p><div class="navrow" style="justify-content:flex-end"><button class="btn sec" data-x>Close</button></div>`); $('[data-x]', m).onclick = () => m.remove(); this.paint(); if (this.st === 'idle' || this.st === 'none' || this.st === 'error') this.check(true); }
};

/* ---------- Settings page ---------- */
function tgl(id, on, en, ar, sub, dis) { return `<div class="srow"><span class="lbl"><b>${en}</b>${sub ? `<small>${sub}</small>` : ''}<span class="ar ar-block">${ar}</span></span><label class="tgl"><input type="checkbox" id="${id}" ${on ? 'checked' : ''} ${dis ? 'disabled' : ''}><span></span></label></div>`; }
function segRow(id, en, ar, opts, val, sub) { return `<div class="srow"><span class="lbl"><b>${en}</b>${sub ? `<small>${sub}</small>` : ''}<span class="ar ar-block">${ar}</span></span><span class="seg" id="${id}">${opts.map(([v, l]) => `<button data-v="${v}" class="${String(v) === String(val) ? 'on' : ''}">${l}</button>`).join('')}</span></div>`; }
VIEWS.settings = m => {
  const T = Auth.isT(), u = Auth.user(), sec = Cfg.sec(), ar = Store.data.settings.ar || {};
  const lock = T ? '' : `<div class="lockbar">🔒 <span>Only the teacher can change these settings. <span class="ar">يستطيع المعلم فقط تغيير هذه الإعدادات.</span></span><button class="btn sm sec" data-tsign>🔑 Teacher sign in</button></div>`;
  const tcard = (icon, en, arT, body) => `<section class="card setcard"><h3>${icon} ${en} <span class="ar">${arT}</span></h3>${lock}<div class="${T ? '' : 'locked'}" ${T ? '' : 'aria-disabled="true" inert'}>${body}</div></section>`;
  const studs = Auth.students();
  m.innerHTML = crumbs([['Home', () => go('home')], ['Settings']]) + `<section class="lhead"><span class="k">⚙️ Settings · الإعدادات</span><h1>Settings</h1><p style="margin:.3rem 0 0">Signed in as <b>${esc(u.name)}</b>${T ? ' (teacher)' : ''}.</p></section>
  <div class="setgrid">
  <section class="card setcard"><h3>🔔 Sounds and voice <span class="ar">الأصوات</span></h3>
    ${tgl('sRx', Cfg.get('rx'), 'Reaction sounds', 'أصوات التفاعل', 'A chime for right answers, a soft sound for wrong ones and a fanfare for finished tasks.')}
    ${tgl('sRv', Cfg.get('rxVoice'), 'Spoken praise', 'كلمات التشجيع المنطوقة', '“Great job!”, “Nice try!”, “You did it!”')}
    <div class="srow"><span class="lbl"><b>Reaction volume</b><span class="ar ar-block">مستوى صوت التفاعل</span></span><span style="display:flex;align-items:center;gap:8px"><input type="range" id="sVol" min="10" max="100" step="10" value="${Cfg.get('rxVol')}" aria-label="Reaction volume"><button class="btn sm sec" id="sTest">▶ Test</button></span></div>
  </section>
  <section class="card setcard"><h3>📖 Lessons and screen <span class="ar">الدروس والشاشة</span></h3>
    ${segRow('sSpd', 'Recording speed', 'سرعة التسجيلات', [[0.85, '🐢 Slow'], [1, 'Normal']], Cfg.get('speed'), 'For listening lessons and games.')}
    ${segRow('sTs', 'Text size', 'حجم الخط', [[1, 'A'], [1.12, 'A+'], [1.25, 'A++']], Cfg.get('ts'))}
    ${tgl('sMo', Cfg.get('motion'), 'Animations and confetti', 'الحركة والقصاصات الملونة', 'Turn off for a calmer screen.')}
    <div class="srow"><span class="lbl"><b>Arabic support</b><span class="ar ar-block">الدعم باللغة العربية</span></span><span class="seg" id="sAr">${[3, 4, 5, 6].map(g => `<button data-g="${g}" class="${(g in ar ? ar[g] : g <= 4) ? 'on' : ''}">G${g}</button>`).join('')}</span></div>
  </section>
  <section class="card setcard"><h3>🎙️ Shadowing <span class="ar">التظليل</span></h3>
    ${segRow('sCd', 'Countdown before you speak', 'العدّ التنازلي قبل التحدث', [[2, '2 s'], [3, '3 s'], [5, '5 s']], Cfg.get('cd'), 'More time helps younger students get ready.')}
  </section>
  <section class="card setcard" id="acct"><h3>🔐 My account <span class="ar">حسابي</span></h3>
    ${u.id === 'guest' ? '<p class="muted">You are practising as a guest. Guest progress is shared by everyone on this device. <span class="ar ar-block">أنت تتدرّب كضيف، وتقدّم الضيف مشترك بين جميع مستخدمي الجهاز.</span></p>'
      : T ? `<div class="srow"><span class="lbl"><b>${esc(Auth.A.teacher.name)}</b><small>Username: ${esc(Auth.A.teacher.user)}</small></span><span class="ctrls"><button class="btn sm sec" id="aName">✏️ Name</button><button class="btn sm sec" id="aPass">🔐 Change password</button><button class="btn sm sec" id="aCode">🗝️ New recovery code</button></span></div>`
      : `<div class="srow"><span class="lbl"><b>${esc(u.name)}</b><small>${esc(u.cls || '')}</small></span><button class="btn sm sec" id="aPin">🔐 Change my PIN</button></div>`}
    <div class="srow"><span class="lbl"><b>Sign out</b><small>Use it when you finish, on a shared device.</small><span class="ar ar-block">سجّل الخروج عند الانتهاء على جهاز مشترك.</span></span><button class="btn sm sec" id="aOut">🚪 Sign out</button></div>
  </section>
  <section class="card setcard"><h3>🔄 Updates <span class="ar">التحديثات</span></h3>
    <div class="updbox"></div>
    ${tgl('sAu', Upd.auto(), 'Automatic updates', 'التحديث التلقائي', Upd.kind() === 'web' ? 'New versions install by themselves at a safe moment (never during a lesson).' : Upd.kind() === 'desktop' ? 'New versions download in the background and install when you close the app.' : 'The app checks for new versions and tells you when one is ready to install.', !T)}
    ${T ? '' : '<p class="muted" style="font-size:.85rem;margin:.3rem 0 0">🔒 Only the teacher can turn automatic updates on or off.</p>'}
  </section>
  ${tcard('🧑‍🏫', 'Classroom', 'الفصل', `${tgl('sCm', !!Store.data.settings.classmode, 'Class mode', 'وضع الفصل', 'Shows a Teacher card with Kagan structures in every lesson. The 🧑‍🏫 button appears at the top.')}`)}
  ${tcard('🛡️', 'Security', 'الأمان', `${tgl('sSu', sec.selfSignup, 'Students can sign up by themselves', 'يستطيع الطلاب التسجيل بأنفسهم', 'Turn off to add students yourself (below).')}
    ${tgl('sGu', sec.guest, 'Allow Guest practice', 'السماح بالدخول كضيف', 'Guests do not need a PIN; their progress is shared.')}
    ${segRow('sId', 'Sign students out after no activity', 'تسجيل خروج الطلاب بعد عدم النشاط', [[0, 'Never'], [10, '10 min'], [20, '20 min'], [30, '30 min'], [60, '60 min']], sec.idle)}
    ${segRow('sTi', 'Lock the teacher account after no activity', 'قفل حساب المعلم بعد عدم النشاط', [[5, '5 min'], [10, '10 min'], [20, '20 min'], [60, '60 min'], [0, 'Never']], sec.tidle)}
    <p class="secnote">🔒 Passwords and PINs are kept only as salted PBKDF2-SHA256 hashes. After 5 wrong tries the app makes the user wait, and the wait doubles each time. <span class="ar ar-block">تُحفظ كلمات المرور والرموز كبصمات مشفّرة فقط، وبعد 5 محاولات خاطئة يجب الانتظار، ويتضاعف وقت الانتظار في كل مرة.</span></p>`)}
  ${tcard('👥', 'Students', 'الطلاب', `${studs.length ? studs.map(p => `<div class="srow"><span class="lbl" style="display:flex;align-items:center;gap:10px">${avHTML(p)}<span><b>${esc(p.name)}</b><small>${esc(p.cls || 'no class')} · ${p.pin ? 'PIN set' : 'no PIN yet'}${Auth.locked(p.id) ? ' · locked' : ''}</small></span></span><span class="ctrls"><button class="btn sm sec" data-rp="${esc(p.id)}">🔑 Reset PIN</button><button class="btn sm sec" data-rn="${esc(p.id)}">✏️</button><button class="btn sm sec" data-dl="${esc(p.id)}" aria-label="Delete">🗑️</button></span></div>`).join('') : '<p class="muted">No students yet.</p>'}
    <form id="adF" class="addrow" novalidate><input type="text" id="adN" maxlength="30" placeholder="Student name" aria-label="Student name"><input type="text" id="adC" maxlength="12" placeholder="Class" aria-label="Class"><button class="btn sm" type="submit">➕ Add student</button></form>
    <p class="muted" style="font-size:.85rem;margin:.4rem 0 0">A student you add chooses a PIN at the first sign-in. “Reset PIN” lets a student choose a new one.</p><p class="pinmsg bad" id="adE"></p>`)}
  ${tcard('💾', 'Data', 'البيانات', `<div class="srow"><span class="lbl"><b>Back up all students</b><small>The backup file is encrypted with the teacher password.</small><span class="ar ar-block">نسخة احتياطية مشفّرة بكلمة مرور المعلم.</span></span><span class="ctrls"><button class="btn sm" id="dBk">💾 Back up</button><button class="btn sm sec" id="dRs">♻️ Restore</button></span></div>
    <div class="srow"><span class="lbl"><b>Reset all progress</b><small>Keeps the accounts; removes stars, scores and shadowing records.</small><span class="ar ar-block">يحذف التقدّم ويحتفظ بالحسابات.</span></span><button class="btn sm sec" id="dRz">🧹 Reset</button></div><p class="muted" id="dM"></p>`)}
  <section class="card setcard"><h3>ℹ️ About and privacy <span class="ar">حول البرنامج والخصوصية</span></h3>
    <p style="margin-top:.3rem"><b>Listen Up! Speak Out!</b> v${APP_VER} · designed by Mr. Waleed Youssef.</p>
    <p>All accounts, recordings and progress stay on this device. Nothing is uploaded. Recordings are deleted when you leave the Shadowing Studio. <span class="ar ar-block">تبقى جميع الحسابات والتسجيلات والتقدّم على هذا الجهاز، ولا يُرفع أي شيء.</span></p>
    <p class="muted" style="font-size:.85rem">Pictures: Fluent Emoji © Microsoft (MIT licence). Fonts: Baloo 2, Nunito, Tajawal (OFL).</p></section>
  </div>`;
  bindCrumbs(m, [['Home', () => go('home')], ['Settings']]);
  Upd.paint();
  const on = (id, f) => { const e = $('#' + id, m); if (e) e.onchange = () => f(e.checked); };
  const seg = (id, f) => $$('#' + id + ' [data-v]', m).forEach(b => b.onclick = () => { $$('#' + id + ' [data-v]', m).forEach(x => x.classList.toggle('on', x === b)); f(b.dataset.v); });
  on('sRx', v => { Cfg.put('rx', v); const h = $('#rxT'); if (h) { h.classList.toggle('on', v); h.firstChild.textContent = v ? '🔔 ' : '🔕 '; } if (v) RX.praise(); });
  on('sRv', v => { Cfg.put('rxVoice', v); if (v) RX.praise(); });
  $('#sVol', m).oninput = e => Cfg.put('rxVol', +e.target.value);
  $('#sTest', m).onclick = () => RX.praise();
  seg('sSpd', v => Cfg.put('speed', +v)); seg('sTs', v => Cfg.put('ts', +v)); seg('sCd', v => Cfg.put('cd', +v));
  on('sMo', v => Cfg.put('motion', v));
  $$('#sAr [data-g]', m).forEach(b => b.onclick = () => { const s = Store.data.settings.ar = Store.data.settings.ar || {}, g = +b.dataset.g; s[g] = !b.classList.contains('on'); b.classList.toggle('on', s[g]); Store.save(); });
  on('sAu', v => { if (!Auth.isT()) return; Cfg.putUpd('auto', v); if (v) Upd.check(false); });
  $$('[data-tsign]', m).forEach(b => b.onclick = () => teacherSignIn(() => go('settings')));
  const aPin = $('#aPin', m); if (aPin) aPin.onclick = async () => {
    const ok = await pinPad({ who: u, title: 'Type your PIN now', ar: 'اكتب رمزك الحالي', wait: Auth.locked(u.id), check: async pin => { const w = Auth.locked(u.id); if (w) return { wait: w }; return (await Sec.check(pin, u.pin)) ? { ok: true } : Auth.fail(u.id, false); } });
    if (!ok) return; const np = await newPinFlow(u, 'Choose your new PIN'); if (!np) return; await Auth.setPin(u.id, np); Upd.toast('✅ Your new PIN is saved. <span class="ar">حُفظ الرمز الجديد.</span>');
  };
  const aOut = $('#aOut', m); if (aOut) aOut.onclick = () => Auth.signOut();
  if (T) {
    on('sCm', v => { Store.data.settings.classmode = v; Store.save(); render(); });
    on('sSu', v => Cfg.putSec('selfSignup', v)); on('sGu', v => Cfg.putSec('guest', v));
    seg('sId', v => Cfg.putSec('idle', +v)); seg('sTi', v => Cfg.putSec('tidle', +v));
    $('#aName', m).onclick = () => { const mm = sheet(`<h3>✏️ Your name</h3><input type="text" id="nmI" maxlength="40" value="${esc(Auth.A.teacher.name)}" style="width:100%"><div class="navrow"><button class="btn sec" data-x>Cancel</button><button class="btn" data-s>Save</button></div>`); $('[data-x]', mm).onclick = () => mm.remove(); $('[data-s]', mm).onclick = () => { const v = $('#nmI', mm).value.trim(); if (v.length < 2) return; Auth.A.teacher.name = v; Store.data.profiles.teacher.name = v; Store.save(); mm.remove(); render(); }; };
    $('#aPass', m).onclick = () => changePassFlow();
    $('#aCode', m).onclick = async () => { if (!(await confirmTeacher('🗝️ New recovery code', 'The old recovery code will stop working.', 'سيتوقف رمز الاسترداد القديم عن العمل.'))) return; const c = await Auth.newCode(); const v = document.createElement('div'); v.className = 'modal'; showRecovery(v, c, () => v.remove()); document.body.appendChild(v); };
    $$('[data-rp]', m).forEach(b => b.onclick = () => { const p = Store.data.profiles[b.dataset.rp]; modal(`<h3>Reset the PIN of ${esc(p.name)}?</h3><p>${esc(p.name)} will choose a new PIN at the next sign-in.</p><p class="ar ar-block">سيختار الطالب رمزًا جديدًا عند الدخول القادم.</p>`, () => { delete p.pin; delete Auth.A.fails[p.id]; Store.save(); render(); }, 'Reset PIN'); });
    $$('[data-rn]', m).forEach(b => b.onclick = () => { const p = Store.data.profiles[b.dataset.rn]; const mm = sheet(`<h3>✏️ Student</h3><div class="field"><label>Name</label><input type="text" id="rnN" maxlength="30" value="${esc(p.name)}"></div><div class="field"><label>Class</label><input type="text" id="rnC" maxlength="12" value="${esc(p.cls || '')}"></div><p class="pinmsg bad" id="rnE"></p><div class="navrow"><button class="btn sec" data-x>Cancel</button><button class="btn" data-s>Save</button></div>`); $('[data-x]', mm).onclick = () => mm.remove(); $('[data-s]', mm).onclick = () => { const n = $('#rnN', mm).value.trim(), c = $('#rnC', mm).value.trim(); if (n.length < 2) return; if (Auth.dupName(n, c, p.id)) { $('#rnE', mm).textContent = 'This name is already used in this class.'; return; } p.name = n; p.cls = c; Store.save(); mm.remove(); render(); }; });
    $$('[data-dl]', m).forEach(b => b.onclick = () => { const p = Store.data.profiles[b.dataset.dl]; modal(`<h3>Delete ${esc(p.name)}?</h3><p>The account and all saved progress of <b>${esc(p.name)}</b> on this device will be removed.</p><p class="ar ar-block">سيُحذف الحساب وكل التقدّم المحفوظ.</p>`, () => { delete Store.data.profiles[p.id]; delete Auth.A.fails[p.id]; Store.save(); render(); }, 'Delete'); });
    $('#adF', m).onsubmit = e => { e.preventDefault(); const n = $('#adN', m).value.trim(), c = $('#adC', m).value.trim(); if (n.length < 2) { $('#adN', m).focus(); return; } if (Auth.dupName(n, c)) { $('#adE', m).textContent = 'This name is already used in this class.'; return; } const id = 'p' + Date.now().toString(36) + [...Sec.rnd(2)].map(x => x.toString(16).padStart(2, '0')).join(''); Store.data.profiles[id] = { id, name: n, cls: c, progress: {}, created: Date.now() }; Store.save(); render(); };
    $('#dBk', m).onclick = () => backupFlow($('#dM', m));
    $('#dRs', m).onclick = () => restoreFlow();
    $('#dRz', m).onclick = async () => { if (!(await confirmTeacher('🧹 Reset all progress?', 'Stars, scores and shadowing records of every student on this device will be removed. The accounts stay.', 'سيُحذف تقدّم جميع الطلاب على هذا الجهاز، وتبقى الحسابات.'))) return; Object.values(Store.data.profiles).forEach(p => { p.progress = {}; delete p.shadow; }); Store.save(); $('#dM', m).textContent = '✅ All progress was reset.'; };
  }
  if (S.focus) { const el = $('#' + S.focus, m); if (el) setTimeout(() => el.scrollIntoView({ block: 'start', behavior: 'smooth' }), 50); }
};
function changePassFlow() {
  const m = sheet(`<h3>🔐 Change the teacher password <span class="ar">تغيير كلمة المرور</span></h3><form id="cpF" novalidate>
    ${pwField('cpO', 'Current password', 'كلمة المرور الحالية')}${pwField('cpN', 'New password', 'كلمة المرور الجديدة', 'new-password')}${meterHTML('cpM')}${pwField('cpN2', 'Type it again', 'أعد كتابتها', 'new-password')}
    <p class="pinmsg bad" id="cpE" role="alert"></p><div class="navrow"><button type="button" class="btn sec" id="cpX">Cancel</button><button class="btn" type="submit" id="cpB">Save</button></div></form>`);
  bindEyes(m); bindMeter($('#cpN', m), $('#cpM', m)); $('#cpX', m).onclick = () => m.remove();
  $('#cpF', m).onsubmit = async e => {
    e.preventDefault(); const E = $('#cpE', m), n = $('#cpN', m).value;
    const pr = Auth.passRule(n, Auth.A.teacher.user); if (pr) { E.innerHTML = `${esc(pr[0])} <span class="ar">${esc(pr[1])}</span>`; return; }
    if (n !== $('#cpN2', m).value) { E.innerHTML = 'The two new passwords are different.'; return; }
    const B = $('#cpB', m); B.disabled = true; const r = await Auth.verifyTeacher($('#cpO', m).value);
    if (!r.ok) { B.disabled = false; E.innerHTML = r.wait ? `Too many tries. Wait ${mmss(r.wait)}.` : 'The current password is not right.'; return; }
    Auth.A.teacher.pw = await Sec.make(n, ITER.pass); Store.save(); m.remove(); Upd.toast('✅ The new password is saved. <span class="ar">حُفظت كلمة المرور الجديدة.</span>');
  };
}

/* ---------- Backups: encrypted with the teacher password ---------- */
function bkData() { const d = JSON.parse(JSON.stringify(Store.data)); if (d.auth) { d.auth.session = null; d.auth.fails = {}; } return d; }
async function backupFlow(msgEl) {
  const pw = await confirmTeacher('💾 Back up all students', 'The backup is locked with the teacher password. You need this password to restore it.', 'تُقفل النسخة الاحتياطية بكلمة مرور المعلم، وتحتاجها لاستعادتها.'); if (!pw) return;
  const say = t => { if (msgEl) msgEl.textContent = t; };
  let body;
  if (Sec.subtle()) body = { app: 'listen-up-speak-out', backup: 2, saved: new Date().toISOString(), version: APP_VER, enc: await Sec.seal(JSON.stringify(bkData()), pw) };
  else { body = { app: 'listen-up-speak-out', backup: 1, saved: new Date().toISOString(), data: bkData() }; say('This browser cannot encrypt files, so the backup is not encrypted. Keep it private.'); }
  const name = 'listen-up-backup-' + new Date().toISOString().slice(0, 10) + '.json', t = JSON.stringify(body);
  if (saveFile(name, t, 'application/json')) { say('✅ Encrypted backup saved: ' + name); return; }
  if (navigator.share) { navigator.share({ title: name, text: t }).then(() => say('✅ Backup shared.'), () => copyText(t).then(() => say('Backup copied — paste it into a note or e-mail and keep it.'))); return; }
  copyText(t).then(() => say('Backup copied — paste it into a note or e-mail and keep it.'), () => say('Could not save the backup here.'));
}
function restoreFlow() {
  const m = sheet(`<h3>♻️ Restore a backup <span class="ar">استعادة نسخة احتياطية</span></h3><p>Choose a backup file, or paste the backup text. <b>This replaces all accounts and progress on this device.</b></p><p class="ar ar-block">اختر ملف النسخة الاحتياطية أو الصق نصّها. سيحلّ ذلك محلّ جميع الحسابات والتقدّم على هذا الجهاز.</p>
    <input type="file" id="bkF" accept=".json,application/json,text/plain" style="margin:6px 0 10px"><textarea class="bk" id="bkT" placeholder='{"app":"listen-up-speak-out", …}'></textarea>
    <div id="bkPw" hidden>${pwField('bkP', 'Password of the teacher who made the backup', 'كلمة مرور المعلم الذي أنشأ النسخة')}</div>
    <p class="pinmsg bad" id="bkE" role="alert"></p><div class="navrow"><button class="btn sec" data-x>Cancel</button><button class="btn" data-ok>Restore</button></div>`);
  bindEyes(m); const ta = $('#bkT', m), E = $('#bkE', m);
  const parse = () => { try { return JSON.parse(ta.value.trim()); } catch (e) { return null; } };
  const look = () => { const o = parse(); $('#bkPw', m).hidden = !(o && o.enc); };
  $('#bkF', m).onchange = e => { const f = e.target.files[0]; if (f) f.text().then(t => { ta.value = t; look(); }); };
  ta.oninput = look; $('[data-x]', m).onclick = () => m.remove();
  $('[data-ok]', m).onclick = async () => {
    const o = parse(); if (!o || o.app !== 'listen-up-speak-out') { E.textContent = 'This is not a Listen Up! Speak Out! backup.'; return; }
    let data = o.data;
    if (o.enc) {
      if (!Sec.subtle()) { E.textContent = 'This browser cannot open encrypted backups. Use the app or Chrome/Edge.'; return; }
      try { data = JSON.parse(await Sec.open(o.enc, $('#bkP', m).value)); } catch (e) { E.innerHTML = 'Wrong password, or the backup is damaged. <span class="ar">كلمة مرور خاطئة أو ملف تالف.</span>'; return; }
    }
    if (!data || typeof data.profiles !== 'object') { E.textContent = 'This is not a Listen Up! Speak Out! backup.'; return; }
    const keepAuth = Store.data.auth;
    if (!(data.auth && data.auth.teacher)) data.auth = keepAuth;     // a backup from version 1.3 or older: keep this device's teacher account
    data.auth.fails = {}; Store.data = data; Store.save(); Store.load();
    Auth.start('teacher', 'teacher'); m.remove(); Upd.toast('✅ The backup was restored. <span class="ar">تمت الاستعادة.</span>'); go('settings');
  };
}
