/* English Pathway Programme – app core (data loading, storage, helpers, audio).
   Part of From Zero To Hero (Grammar and Vocabulary department). Designed by Waleed Youssef. */
'use strict';
(function () {
  const P = window.Pathway = window.Pathway || {};
  P.version = '1.0.0';

  /* ---------------------------------------------------------- data loading
     Every JSON file has a .js mirror that calls PathwayData.put(path, obj).
     Over http(s) the JSON is fetched; from file:// (double-click) the mirror is used. */
  P._data = {}; P._wait = {};
  window.PathwayData = {
    put(path, obj) {
      P._data[path] = obj;
      (P._wait[path] || []).forEach(fn => fn(obj));
      delete P._wait[path];
    }
  };
  P.load = function (path) {
    if (P._data[path]) return Promise.resolve(P._data[path]);
    const viaScript = () => new Promise((resolve, reject) => {
      (P._wait[path] = P._wait[path] || []).push(resolve);
      const s = document.createElement('script');
      s.src = path.replace(/\.json$/, '.js');
      s.onerror = () => reject(new Error('Could not load ' + path));
      document.head.appendChild(s);
    });
    return viaScript();   // the .js mirrors load everywhere (web, Android, iPhone and the Windows app)
  };

  /* ---------------------------------------------------------- storage */
  const HOST = window.GV_HOST || {};          // who is signed in to the main app (see host.js)
  const KEY = 'fzh.gv.v1.' + (HOST.uid || 'guest');   // each user of the device keeps their own progress
  P.host = HOST;
  /* level names on the app's scale */
  P.LV = {"1": "A1", "2": "A1+", "3": "A2", "4": "A2+", "5": "B1 · Part 1", "6": "B1 · Part 2", "7": "B1+", "8": "B2 · Part 1", "9": "B2 · Part 2", "10": "B2+", "11": "C1", "12": "C2"};
  P.lvs = n => P.LV[n] || String(n);
  P.lv = n => 'Level ' + P.lvs(n);
  const blank = () => ({
    profile: { name: '', cls: '' },
    settings: { arabic: true, teacher: false, showAnswers: false, pin: '1234', rate: 0.95 },
    lessons: {}, quizzes: {}, tests: {}, srs: {}, xp: 0, log: [], placement: null
  });
  P.store = {
    mem: null,
    get() {
      if (this.mem) return this.mem;
      let s = null;
      try { s = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { s = null; }
      const b = blank();
      this.mem = Object.assign(b, s || {});
      this.mem.settings = Object.assign(b.settings, (s && s.settings) || {});
      this.mem.profile = Object.assign(b.profile, (s && s.profile) || {});
      if (HOST.name) { this.mem.profile.name = HOST.name; this.mem.profile.cls = HOST.cls || ''; }
      if (HOST.role !== 'teacher') { this.mem.settings.teacher = false; this.mem.settings.showAnswers = false; }
      return this.mem;
    },
    save() { try { localStorage.setItem(KEY, JSON.stringify(this.mem)); } catch (e) { /* storage unavailable: keep in memory */ } },
    reset() { this.mem = blank(); this.save(); }
  };
  P.log = function (kind, id, detail) {
    const S = P.store.get();
    S.log.unshift({ kind, id, detail, ts: Date.now() });
    S.log = S.log.slice(0, 300);
    P.store.save();
  };
  P.addXP = function (n) { const S = P.store.get(); S.xp = (S.xp || 0) + n; P.store.save(); };

  /* ---------------------------------------------------------- DOM helpers */
  P.el = function (tag, attrs, ...kids) {
    const e = document.createElement(tag);
    if (attrs) for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else if (k === 'style' && typeof v === 'object') Object.assign(e.style, v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat(Infinity)) {
      if (k === null || k === undefined || k === false) continue;
      e.appendChild(typeof k === 'string' || typeof k === 'number' ? document.createTextNode(String(k)) : k);
    }
    return e;
  };
  P.ar = (text, cls) => text ? P.el('div', { class: 'ar ' + (cls || ''), dir: 'rtl', lang: 'ar' }, text) : null;
  P.toast = function (msg) {
    const t = document.getElementById('toast'); if (!t) return;
    t.textContent = msg; t.classList.add('show');
    clearTimeout(P._tt); P._tt = setTimeout(() => t.classList.remove('show'), 1800);
  };
  /* In-page yes/no dialog (works where window.confirm is blocked, e.g. embedded or sandboxed pages). */
  P.ask = function (msg, yes, no) {
    return new Promise(resolve => {
      const close = v => { m.remove(); resolve(v); };
      const m = P.el('div', { class: 'modal', role: 'dialog', 'aria-modal': 'true' }, P.el('div', { class: 'panel' },
        P.el('p', { style: { fontWeight: 700 } }, msg),
        P.el('div', { class: 'row' }, P.el('button', { class: 'btn alt', type: 'button', onclick: () => close(true) }, yes || 'Yes'),
          P.el('button', { class: 'btn ghost', type: 'button', onclick: () => close(false) }, no || 'Cancel'))));
      document.body.appendChild(m);
    });
  };
  P.shuffle = function (a, seed) {
    a = a.slice();
    let s = seed || Math.floor(Math.random() * 1e9);
    const rnd = () => { s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; };
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  };
  P.pct = (a, b) => b ? Math.round(100 * a / b) : 0;
  P.band = p => p >= 85 ? 'ok' : p >= 65 ? 'mid' : 'low';
  P.pad = n => String(n).padStart(2, '0');

  /* ---------------------------------------------------------- answer matching */
  P.clean = s => String(s || '').replace(/[‘’ʼ]/g, "'").replace(/[“”]/g, '"')
    .replace(/[–—]/g, '–').replace(/\s+/g, ' ').trim();
  P.loose = s => P.clean(s).toLowerCase().replace(/^[\s.,!?;:"']+|[\s.,!?;:"']+$/g, '');
  P.sameLoose = (a, b) => P.loose(a) === P.loose(b);
  P.sameStrict = (a, b) => P.clean(a) === P.clean(b);
  P.alternatives = ans => String(ans).split(/\s+\/\s+/).map(x => x.trim()).filter(Boolean);
  /* Mark the words in a faulty sentence that differ from the corrected one. */
  P.diffZone = function (wrong, right) {
    const a = P.clean(wrong).split(' '), b = P.clean(right).split(' ');
    let i = 0;
    while (i < a.length && i < b.length && a[i] === b[i]) i++;
    let j = 0;
    while (j < a.length - i && j < b.length - i && a[a.length - 1 - j] === b[b.length - 1 - j]) j++;
    let start = i, end = a.length - 1 - j;
    if (end < start) { start = Math.max(0, i - 1); end = Math.min(a.length - 1, i); }
    return { tokens: a, start, end, fix: b.slice(i, b.length - j).join(' ') };
  };
  P.similar = function (a, b) {
    const A = new Set(P.loose(a).split(' ')), B = new Set(P.loose(b).split(' '));
    let n = 0; A.forEach(x => { if (B.has(x)) n++; });
    return n / Math.max(A.size, B.size, 1);
  };

  /* ---------------------------------------------------------- audio
     A recorded file in media/audio/<id>.mp3 is used when present; otherwise the browser voice reads the text. */
  P.voice = null;
  function pickVoice() {
    if (!('speechSynthesis' in window)) return;
    const vs = speechSynthesis.getVoices();
    P.voice = vs.find(v => /en-US/i.test(v.lang) && /female|samantha|aria|jenny|google us/i.test(v.name)) ||
      vs.find(v => /en-US/i.test(v.lang)) || vs.find(v => /^en/i.test(v.lang)) || null;
  }
  if ('speechSynthesis' in window) { pickVoice(); speechSynthesis.onvoiceschanged = pickVoice; }
  P.speak = function (text, rate) {
    if (!('speechSynthesis' in window)) { P.toast('Audio is not available in this browser.'); return; }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(String(text).replace(/_{2,}/g, 'blank'));
    u.lang = 'en-US'; if (P.voice) u.voice = P.voice;
    u.rate = rate || P.store.get().settings.rate || 0.95;
    speechSynthesis.speak(u);
  };
  P.play = function (audioId, text) {
    if (!audioId || !P.recorded) return P.speak(text);   // no recorded files yet: the device voice reads the text
    const a = new Audio('media/audio/' + audioId + '.mp3');
    a.play().catch(() => P.speak(text));
  };
  P.sayBtn = (text, audioId, label) => P.el('button', {
    class: 'say', type: 'button', title: 'Listen', 'aria-label': label || 'Listen',
    onclick: e => { e.stopPropagation(); P.play(audioId, text); }
  }, '🔊');

  /* ---------------------------------------------------------- extension points for other strands */
  P.activityTypes = {};      // type -> function(item, ctx) returning an element
  P.gameMechanics = {};      // mechanic -> function(game, ctx) returning an element
  P.registerActivity = (type, fn) => { P.activityTypes[type] = fn; };
  P.registerGame = (mech, fn) => { P.gameMechanics[mech] = fn; };

  /* ---------------------------------------------------------- spaced repetition (Leitner, 5 boxes) */
  const DAY = 86400000, GAPS = [0, 1, 3, 7, 16, 35];
  P.srs = {
    add(card) {
      const S = P.store.get();
      const k = card.word.toLowerCase();
      if (!S.srs[k]) { S.srs[k] = Object.assign({ box: 0, due: Date.now(), seen: 0, right: 0 }, card); P.store.save(); return true; }
      return false;
    },
    due() { const S = P.store.get(), now = Date.now(); return Object.values(S.srs).filter(c => c.due <= now); },
    grade(word, quality) {           // quality: 0 again, 1 good, 2 easy
      const S = P.store.get(), c = S.srs[word.toLowerCase()]; if (!c) return;
      c.seen++;
      if (quality === 0) c.box = 0; else { c.right++; c.box = Math.min(5, c.box + quality); }
      c.due = Date.now() + GAPS[c.box] * DAY + (c.box === 0 ? 60000 : 0);
      P.store.save();
    }
  };

})();
