/* =====================================================================
   SHADOWING STUDIO — 5-stage shadowing with word-by-word highlighting,
   recording, honest timing feedback and Arabic-speaker sound hints
   ===================================================================== */
const TM = window.LSP_TIMINGS || {};
const SH_MODES = [
  { k: 'read', icon: '👂', name: 'Listen & Read', en: 'Listen and follow the words as they light up. Tap any word to hear it again.', ar: 'استمع وتابع الكلمات وهي تُضاء. اضغط على أي كلمة لتسمعها مرة أخرى.' },
  { k: 'echo', icon: '🔁', name: 'Echo', en: 'Listen to the whole line. After the beep, say it in the same way.', ar: 'استمع إلى الجملة كاملة، وبعد الصافرة قلها بالطريقة نفسها.' },
  { k: 'shadow', icon: '🗣️', name: 'Shadow', en: 'Speak at the same time as the speaker. Follow the words as they light up.', ar: 'تحدّث في الوقت نفسه مع المتحدث، وتابع الكلمات المضاءة.' },
  { k: 'blind', icon: '🙈', name: 'Blind Shadow', en: 'Shadow without the text — use only your ears! The text appears after you finish.', ar: 'ظلّل دون النص واعتمد على أذنيك فقط! يظهر النص بعد أن تنتهي.' },
  { k: 'run', icon: '🎬', name: 'Full Run', en: 'Shadow all the lines without stopping, like a real conversation.', ar: 'ظلّل جميع الجمل دون توقف، كأنها محادثة حقيقية.' }
];
const VOICED_TH = /^(the|this|that|these|those|they|them|their|theirs|there|then|than|though|with|without|mother|father|brother|other|another|together|weather|clothes|gather|smooth|breathe|rather|either|neither)$/;

function wordsOf(t) { return String(t).split(/\s+/).filter(Boolean); }
const spoken = w => /[A-Za-z0-9]/.test(w);
function wordTimes(src, text) {
  const ws = wordsOf(text), idx = ws.map((w, i) => spoken(w) ? i : -1).filter(i => i >= 0), out = ws.map(() => null);
  const sp = TM[src];
  if (!sp || !sp.length || !idx.length) return { ws, times: out, has: false };
  if (sp.length === idx.length) idx.forEach((wi, k) => out[wi] = sp[k]);
  else {
    const a = sp[0][0], b = sp[sp.length - 1][1], len = wi => ws[wi].replace(/[^A-Za-z0-9]/g, '').length + 1;
    const L = idx.reduce((s, wi) => s + len(wi), 0); let t = a;
    idx.forEach(wi => { const d = (b - a) * len(wi) / L; out[wi] = [t, t + d * 0.9]; t += d; });
  }
  return { ws, times: out, has: true };
}
function soundHints(text) {
  const H = [], seen = new Set(), add = (k, en, ar) => { if (!seen.has(k) && H.length < 2) { seen.add(k); H.push({ en, ar }); } };
  for (const raw of wordsOf(text)) {
    const w = raw.toLowerCase().replace(/[^a-z']/g, '');
    if (!w) continue;
    if (/p/.test(w) && !/ph/.test(w)) add('p', `/p/ in “${w}”: a puff of air, no voice.`, `صوت /p/ في “${w}”: دفعة هواء بلا صوت.`);
    if (/v/.test(w)) add('v', `/v/ in “${w}”: top teeth on your lip, with voice.`, `صوت /v/ في “${w}”: الأسنان على الشفة مع الصوت.`);
    if (/th/.test(w)) { if (VOICED_TH.test(w)) add('dh', `“${w}”: tongue between teeth, with voice — like ذ.`, `“${w}”: اللسان بين الأسنان مع الصوت مثل الذال.`); else add('th', `“${w}”: tongue between teeth, only air — like ث.`, `“${w}”: اللسان بين الأسنان مع الهواء فقط مثل الثاء.`); }
    if (/^(spr|str|scr|spl|sp|st|sk|sc[^h]|sm|sn|sl|sw|pl|pr|bl|br|cl|cr|fl|fr|gl|gr|tr|dr|tw)/.test(w)) add('cl', `“${w}” starts with two consonants — no extra vowel before it.`, `تبدأ “${w}” بحرفين ساكنين — لا تضف حركة قبلها.`);
    if (/[a-z]{3,}ed$/.test(w) && !/(need|feed|speed|seed|bleed|weed|hundred)$/.test(w)) add('ed', `-ed in “${w}”: listen — is it /t/, /d/ or /ɪd/?`, `نهاية -ed في “${w}”: هل هي /t/ أم /d/ أم /ɪd/؟`);
  }
  return H;
}

/* --- audio helpers --- */
let ACX = null;
function actx() { if (!ACX) { try { ACX = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} } if (ACX && ACX.state === 'suspended') ACX.resume(); return ACX; }
function beep(f = 880, ms = 140) {
  const c = actx(); if (!c) return sleep(ms);
  try { const o = c.createOscillator(), g = c.createGain(); o.frequency.value = f; g.gain.value = 0.18; o.connect(g); g.connect(c.destination); o.start(); g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + ms / 1000); o.stop(c.currentTime + ms / 1000 + 0.03); } catch (e) {}
  return sleep(ms);
}
AU.range = function (c, a, b, rate) {
  this.stop(); const tok = this.token, el = this.el, SPR = window.LSP_SPRITES, sp = SPR && SPR[c.src];
  const base = sp ? sp[1] : 0, url = sp ? sp[0] : 'audio/' + c.src;
  this.cur = c.src; this.base = base; el.onerror = null; el.onended = null;
  return new Promise(res => {
    const go2 = () => { try { el.currentTime = base + Math.max(0, a - 0.03); } catch (e) {} el.playbackRate = rate || 1; const p = el.play(); if (p && p.catch) p.catch(() => {}); setTimeout(() => { if (tok === this.token) el.pause(); res(); }, (b - a + 0.08) / (rate || 1) * 1000); };
    if (!el.src || !el.src.endsWith(url)) { el.onloadedmetadata = () => { el.onloadedmetadata = null; go2(); }; el.src = url; el.load(); } else go2();
  });
};
function karaoke(box, src, text) {
  const { times, has } = wordTimes(src, text), spans = $$('.kw', box); let raf = 0;
  const tick = () => {
    if (!document.body.contains(box)) return;
    if (AU.cur === src && !AU.el.paused) {
      const t = AU.el.currentTime - (AU.base || 0);
      let tm = times;
      if (!has) { const SPR = window.LSP_SPRITES, sp = SPR && SPR[src]; const d = sp ? sp[2] - sp[1] : AU.el.duration; if (d) { const n = spans.length; tm = spans.map((_, i) => [0.1 + (d - 0.2) * i / n, 0.1 + (d - 0.2) * (i + 1) / n]); } }
      spans.forEach((s, i) => { const w = tm[i]; if (!w) return; s.classList.toggle('on', t >= w[0] - 0.03 && t < w[1] + 0.04); s.classList.toggle('past', t >= w[1] + 0.04); });
    }
    raf = requestAnimationFrame(tick);
  };
  raf = requestAnimationFrame(tick);
  return () => { cancelAnimationFrame(raf); spans.forEach(s => s.classList.remove('on', 'past')); };
}

/* --- microphone for the studio --- */
const Mic = {
  stream: null, mr: null, chunks: [], t0: 0,
  async open() {
    if (this.stream && this.stream.active) return true; if (!canMic) return false;
    try { this.stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } }); return true; } catch (e) { return false; }
  },
  start() { return new Promise(res => { this.chunks = []; this.mr = new MediaRecorder(this.stream); this.mr.ondataavailable = e => { if (e.data && e.data.size) this.chunks.push(e.data); }; this.mr.onstart = () => { this.t0 = performance.now(); res(); }; this.mr.start(); }); },
  stop() { return new Promise(res => { if (!this.mr || this.mr.state === 'inactive') return res(null); this.mr.onstop = () => res(new Blob(this.chunks, { type: this.mr.mimeType || 'audio/webm' })); this.mr.stop(); }); },
  close() { try { if (this.mr && this.mr.state !== 'inactive') this.mr.stop(); } catch (e) {} try { this.stream && this.stream.getTracks().forEach(t => t.stop()); } catch (e) {} this.stream = null; }
};
async function analyse(blob) {
  const c = actx(); if (!c || !blob) return null;
  try {
    const buf = await c.decodeAudioData(await blob.arrayBuffer()); const x = buf.getChannelData(0), sr = buf.sampleRate, fr = Math.round(sr * 0.02), env = [];
    for (let i = 0; i + fr <= x.length; i += fr) { let s = 0; for (let j = i; j < i + fr; j++) s += x[j] * x[j]; env.push(Math.sqrt(s / fr)); }
    const so = env.slice().sort((a, b) => a - b), noise = so[Math.floor(so.length * 0.15)] || 0, peak = so[so.length - 1] || 0;
    const thr = Math.max(noise * 2.5, peak * 0.12, 0.004); const segs = []; let s = -1;
    env.forEach((v, i) => { if (v > thr && s < 0) s = i; if ((v <= thr || i === env.length - 1) && s >= 0) { segs.push([s * 0.02, i * 0.02]); s = -1; } });
    const m = []; segs.forEach(g => { if (m.length && g[0] - m[m.length - 1][1] < 0.15) m[m.length - 1][1] = g[1]; else m.push(g.slice()); });
    return { segs: m.filter(g => g[1] - g[0] >= 0.08), dur: x.length / sr, peak };
  } catch (e) { return null; }
}
function judge(A, model, mode) {
  // model.words: [[start,end]...] on the recording's time line; model.turn: echo turn start
  if (!A) return { items: [{ ok: null, t: 'Your recording is saved, but this browser cannot measure it. Listen and compare.' }] };
  if (!A.segs.length || A.peak < 0.01) return { items: [{ ok: false, t: 'We could not hear you. Check the microphone and speak a little louder.' }] };
  const mw = model.words, m0 = mw[0][0], m1 = mw[mw.length - 1][1], s0 = A.segs[0][0], s1 = A.segs[A.segs.length - 1][1], items = [];
  if (mode === 'echo') {
    const lag = s0 - model.turn;
    items.push(lag <= 1.2 ? { ok: true, t: 'You started soon after the beep. ✓' } : { ok: false, t: `You waited ${lag.toFixed(1)} s after the beep. Try to start sooner.` });
  } else {
    const lag = s0 - m0;
    items.push(Math.abs(lag) <= 0.45 ? { ok: true, t: 'You started on time with the speaker. ✓' } : lag > 0 ? { ok: false, t: `You started ${lag.toFixed(1)} s late. Start with the first word.` } : { ok: false, t: 'You started before the speaker. Wait for the first word.' });
  }
  const ratio = (s1 - s0) / Math.max(0.3, m1 - m0);
  items.push(ratio >= 0.8 && ratio <= 1.25 ? { ok: true, t: 'Your speed was close to the speaker’s. ✓' } : ratio > 1.25 ? { ok: false, t: `You took ${Math.round(ratio * 100)}% of the speaker’s time. Try to keep up.` } : { ok: false, t: 'You finished much faster. Did you say every word?' });
  const longGaps = (arr, min) => arr.slice(1).filter((g, i) => g[0] - arr[i][1] > min).length;
  const extra = Math.max(0, longGaps(A.segs, 0.5) - longGaps(mw, 0.35));
  items.push(extra === 0 ? { ok: true, t: 'No extra pauses — your voice kept flowing. ✓' } : { ok: false, t: `${extra} extra pause${extra > 1 ? 's' : ''} in the middle. Keep the words joined.` });
  if (A.peak < 0.05) items.push({ ok: false, t: 'Your voice was quiet. Speak a little louder.' });
  return { items, s0, s1 };
}
function rhythmSVG(mw, labels, segs, total) {
  const W = 600, sx = t => 6 + Math.max(0, t) / total * (W - 12);
  const mr = mw.map((w, i) => { const x = sx(w[0]), wd = Math.max(3, sx(w[1]) - x); const lab = wd > 34 ? `<text x="${x + 3}" y="21" font-size="11" fill="#fff">${esc(labels[i] || '')}</text>` : ''; return `<rect x="${x}" y="6" width="${wd}" height="22" rx="5" fill="var(--c)"/>${lab}`; }).join('');
  const yr = (segs || []).map(g => `<rect x="${sx(g[0])}" y="40" width="${Math.max(3, sx(g[1]) - sx(g[0]))}" height="22" rx="5" fill="var(--coral)"/>`).join('');
  return `<svg viewBox="0 0 ${W} 68" class="rhythm" role="img" aria-label="Timing picture"><rect x="0" y="0" width="${W}" height="68" rx="10" fill="#F5F7FC"/>${mr}${yr}</svg>
    <div class="rl"><span><i style="background:var(--c)"></i>Speaker</span><span><i style="background:var(--coral)"></i>You</span><span class="muted">This picture shows timing and pauses, not pronunciation.</span></div>`;
}

/* --- progress --- */
const today = () => new Date().toISOString().slice(0, 10);
function shData() { const p = Store.me(); p.shadow = p.shadow || { lines: {}, sec: 0, days: {} }; return p.shadow; }
function shSave(src, upd) { const d = shData(), o = d.lines[src] || { lvl: -1, n: 0 }; d.lines[src] = Object.assign(o, upd, { lvl: Math.max(o.lvl, upd.lvl == null ? -1 : upd.lvl), n: o.n + 1 }); Store.save(); }
function shTime(sec) { const d = shData(); d.sec = (d.sec || 0) + sec; d.days[today()] = (d.days[today()] || 0) + sec; Store.save(); }
const shState = src => { const o = shData().lines[src]; return !o ? '' : (o.good && o.lvl >= 2) ? 'ms' : 'pr'; };
function shStats(p) {
  const d = (p || Store.me()).shadow || { lines: {}, sec: 0, days: {} };
  let streak = 0; for (let i = 0; i < 365; i++) { const k = new Date(Date.now() - i * 864e5).toISOString().slice(0, 10); if (d.days[k]) streak++; else if (i > 0) break; }
  return { min: Math.round((d.sec || 0) / 60), lines: Object.keys(d.lines).length, mastered: Object.values(d.lines).filter(o => o.good && o.lvl >= 2).length, streak };
}

/* --- tracks --- */
function shTracks(g, u) {
  const U0 = U(g, u);
  return [...U0.listen.map(L => ({ key: 'l' + L.n, title: `Listening ${L.n}: ${L.title}`, lines: L.script, icon: '🎧' })), ...U0.speak.map(Sp => ({ key: 's' + Sp.n, title: `Speaking ${Sp.n}: ${Sp.title}`, lines: Sp.model, icon: '🗣️' }))];
}
function shDaily(g) {
  const gr = G(g); let best = gr.units[0], bt = 0;
  gr.units.forEach(u0 => lessonList(u0).forEach(x => { const p = Store.get(x.L.id); if (p && p.ts > bt) { bt = p.ts; best = u0; } }));
  const pool = shTracks(g, best.n).flatMap(t => t.lines).filter(l => l.sp !== 'NARRATOR' && wordsOf(l.text).length >= 4 && wordsOf(l.text).length <= 16 && shState(l.audio) !== 'ms');
  return { u: best.n, lines: pickN(pool.length >= 5 ? pool : shTracks(g, best.n).flatMap(t => t.lines).filter(l => l.sp !== 'NARRATOR'), 5) };
}

/* --- Studio hub --- */
VIEWS.studio = m => {
  S.g = S.g || Store.data.settings.shG || 3; setBand(S.g);
  const st = shStats(), gr = G(S.g);
  m.innerHTML = crumbs([['Home', () => go('home')], ['Shadowing Studio']]) + `
  <section class="lhead" style="background:linear-gradient(120deg,var(--c),#FF6B4A)"><span class="k">🎙️ Shadowing Studio</span><h1>Speak like the speaker!</h1>
    <p style="margin:.3rem 0 0;max-width:720px">Shadowing means listening to English and speaking <b>with</b> it, copying the sounds, the rhythm and the music. Practise a little every day.</p>
    <p class="ar" style="color:#fff">التظليل يعني أن تستمع إلى الإنجليزية وتتحدث معها في الوقت نفسه، مقلّدًا الأصوات والإيقاع والنغمة. تدرّب قليلًا كل يوم.</p></section>
  <div class="hud" style="margin:14px 0"><span>⏱️ ${st.min} min</span><span>🗣️ ${st.lines} lines practised</span><span>⭐ ${st.mastered} mastered</span><span>🔥 ${st.streak}-day streak</span></div>
  <div class="card"><b>The 5 steps of shadowing</b><div class="grid g3" style="margin-top:10px">${SH_MODES.map((x, i) => `<div class="kag"><b>${i + 1}. ${x.icon} ${esc(x.name)}</b><br><span style="font-size:.92rem">${esc(x.en)}</span><span class="ar ar-block">${esc(x.ar)}</span></div>`).join('')}</div>
    <p class="muted" style="margin:.8rem 0 0">🎧 Use headphones for steps 3–5, so the microphone hears only you.</p></div>
  <div class="section-title"><h2>Choose your grade</h2></div>
  <div class="seg" id="gsel">${D.grades.map(x => `<button data-g="${x.grade}" class="${x.grade === S.g ? 'on' : ''}">Grade ${x.grade}</button>`).join('')}</div>
  <div class="ctrls" style="justify-content:flex-start;margin-top:14px"><button class="btn" id="daily">⚡ Daily 5 — five lines for today</button></div>
  <div class="grid g2" style="margin-top:16px">${gr.units.map(u0 => { const tr = shTracks(S.g, u0.n); const all = tr.flatMap(t => t.lines); const ms = all.filter(l => shState(l.audio) === 'ms').length;
    return `<div class="card"><div class="uh" style="display:flex;gap:10px;align-items:center"><span class="ue" style="width:46px;height:46px;border-radius:14px;background:var(--cl);display:grid;place-items:center;font-size:1.5rem">${u0.emoji}</span><div><span class="pill">Unit ${u0.n}</span><h3 style="font-size:1.1rem">${esc(u0.title)}</h3></div></div>
      <div class="lesson-list" style="margin-top:10px">${tr.map(t => { const d = t.lines.filter(l => shState(l.audio) === 'ms').length; return `<button class="lrow" data-tr="${u0.n}|${t.key}" style="padding:9px 12px"><span class="ic" style="width:34px;height:34px">${t.icon}</span><span class="tx"><b style="font-size:.95rem">${esc(t.title)}</b><small>${t.lines.length} lines · ⭐ ${d}</small></span></button>`; }).join('')}</div>
      <div class="muted" style="font-size:.85rem;margin-top:8px">⭐ ${ms}/${all.length} lines mastered</div></div>`; }).join('')}</div>`;
  bindCrumbs(m, [['Home', () => go('home')], ['Studio']]);
  $$('#gsel button', m).forEach(b => b.onclick = () => { Store.data.settings.shG = +b.dataset.g; Store.save(); go('studio', { g: +b.dataset.g }); });
  $$('[data-tr]', m).forEach(b => b.onclick = () => { const [u0, key] = b.dataset.tr.split('|'); go('shadow', { g: S.g, u: +u0, src: key }); });
  $('#daily', m).onclick = () => { const d = shDaily(S.g); go('shadow', { g: S.g, u: d.u, src: 'daily', dl: d.lines }); };
};

/* --- Studio session --- */
VIEWS.shadow = m => {
  const set = Store.data.settings; S.mode = S.mode == null ? (set.shMode || 0) : S.mode; S.i = S.i || 0; S.rate = S.rate || 1; S.loop = S.loop || 1; S.who = S.who || '';
  const u0 = U(S.g, S.u); let title, all;
  if (S.src === 'daily') { title = '⚡ Daily 5'; all = S.dl; } else { const t = shTracks(S.g, S.u).find(x => x.key === S.src); title = t.title; all = t.lines; }
  const people = [...new Map(all.filter(l => l.sp !== 'NARRATOR').map(l => [l.sp, l.name])).entries()];
  const lines = S.who ? all.filter(l => l.sp === S.who) : all; if (S.i >= lines.length) S.i = 0;
  const l = lines[S.i], md = SH_MODES[S.mode], choral = !!set.classmode;
  const parts = [['Home', () => go('home')], ['Studio', () => go('studio', { g: S.g })], [`Unit ${u0.n}`]];
  m.innerHTML = crumbs(parts) + `
  <section class="lhead"><span class="k">🎙️ Shadowing Studio · Grade ${S.g} · Unit ${u0.n}</span><h1>${esc(title)}</h1></section>
  <nav class="steps">${SH_MODES.map((x, i) => `<button class="${i === S.mode ? 'cur' : ''}" data-md="${i}">${i + 1}. ${x.icon} ${esc(x.name)}</button>`).join('')}</nav>
  <div class="instr"><span class="n">${md.icon}</span><div><b>${esc(md.en)}</b><span class="ar ar-block">${esc(md.ar)}</span></div></div>
  <div class="ctrls" style="justify-content:flex-start;margin-bottom:12px">
    <span class="seg" id="rt">${[0.7, 0.85, 1, 1.15].map(r => `<button data-r="${r}" class="${r === S.rate ? 'on' : ''}">${r === 1 ? 'Normal' : r + '×'}</button>`).join('')}</span>
    ${S.mode === 0 ? `<span class="seg" id="lp"><button data-l="1" class="${S.loop === 1 ? 'on' : ''}">Play once</button><button data-l="3" class="${S.loop === 3 ? 'on' : ''}">🔁 ×3</button></span>` : ''}
    ${people.length > 1 && S.src !== 'daily' ? `<select id="who" class="chip" aria-label="Lines to practise"><option value="">All lines</option>${people.map(([k, n]) => `<option value="${k}" ${S.who === k ? 'selected' : ''}>Only ${esc(n)}’s lines</option>`).join('')}</select>` : ''}
    ${S.mode >= 2 ? `<label class="chip"><input type="checkbox" id="hp" ${set.hp ? 'checked' : ''}> 🎧 I’m using headphones</label>` : ''}
  </div>
  <div id="sbody"></div>
  <div class="dots">${lines.map((x, i) => `<button class="dot ${shState(x.audio)} ${i === S.i ? 'cur' : ''}" data-i="${i}" title="Line ${i + 1}">${i + 1}</button>`).join('')}</div>
  <p class="muted" style="font-size:.85rem;text-align:center">⚪ new · 🔵 practised · ⭐ mastered (good self-check in Shadow, Blind or Full Run)</p>`;
  bindCrumbs(m, parts);
  $$('[data-md]', m).forEach(b => b.onclick = () => { S.mode = +b.dataset.md; Store.data.settings.shMode = S.mode; Store.save(); S.fb = null; AU.stop(); VIEWS.shadow(m); });
  $$('#rt button', m).forEach(b => b.onclick = () => { S.rate = +b.dataset.r; VIEWS.shadow(m); });
  $$('#lp button', m).forEach(b => b.onclick = () => { S.loop = +b.dataset.l; VIEWS.shadow(m); });
  const who = $('#who', m); if (who) who.onchange = () => { S.who = who.value; S.i = 0; S.fb = null; VIEWS.shadow(m); };
  const hp = $('#hp', m); if (hp) hp.onchange = () => { Store.data.settings.hp = hp.checked; Store.save(); };
  $$('[data-i]', m).forEach(b => b.onclick = () => { S.i = +b.dataset.i; S.fb = null; AU.stop(); VIEWS.shadow(m); });
  const B = $('#sbody', m);
  if (S.mode === 4) return shFullRun(B, lines, m);
  const hints = soundHints(l.text);
  B.innerHTML = `<div class="card shcard ${choral ? 'choral' : ''}">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><span class="round">Line ${S.i + 1} of ${lines.length}</span><span style="display:flex;gap:8px;align-items:center">${avatar(l.sp, l.name)}<b style="color:${SPC[l.sp]}">${esc(l.name)}</b></span></div>
    <p class="ktext ${S.mode === 3 && !S.revealed ? 'blind' : ''}" id="kt">${wordsOf(l.text).map((w, i) => `<span class="kw" data-w="${i}">${esc(w)}</span>`).join(' ')}</p>
    ${hints.length && S.mode !== 3 ? `<div class="hints">${hints.map(h => `<span class="hint">🔤 ${esc(h.en)}<span class="ar ar-block">${esc(h.ar)}</span></span>`).join('')}</div>` : ''}
    <div class="ctrls" id="act" style="margin-top:12px"></div><p id="msg" class="shmsg"></p></div>
    <div id="fb"></div>
    <div class="navrow"><button class="btn sm sec" id="pv" ${S.i === 0 ? 'disabled' : ''}>← Previous</button><button class="btn sm band" id="nx" ${S.i === lines.length - 1 ? 'disabled' : ''}>Next line →</button></div>`;
  const kt = $('#kt', B), msg = $('#msg', B), act = $('#act', B), clip = clipOf(l);
  karaoke(kt, l.audio, l.text);
  const wt = wordTimes(l.audio, l.text);
  $$('.kw', kt).forEach((s, i) => s.onclick = () => { const w = wt.times[i]; if (w) AU.range(clip, w[0], w[1], Math.min(S.rate, 1)); });
  $('#pv', B).onclick = () => { S.i--; S.fb = null; S.revealed = false; AU.stop(); VIEWS.shadow(m); };
  $('#nx', B).onclick = () => { S.i++; S.fb = null; S.revealed = false; AU.stop(); VIEWS.shadow(m); };
  const mwRec = off => (wt.has ? wt.times.filter(Boolean) : [[0.1, 1]]).map(w => [off + w[0] / S.rate, off + w[1] / S.rate]);
  const labels = wt.ws.filter((w, i) => wt.times[i]);
  const lineSec = () => { const SPR = window.LSP_SPRITES, sp = SPR && SPR[l.audio]; return ((sp ? sp[2] - sp[1] : (TM[l.audio] ? TM[l.audio][TM[l.audio].length - 1][1] + 0.15 : 3))) / S.rate; };
  if (S.mode === 0) {
    act.innerHTML = `<button class="btn band" id="p1">▶ Listen</button><button class="btn sec" id="pall">▶ Play all lines</button><button class="btn sec" id="st">⏹</button>`;
    $('#p1', B).onclick = async () => { for (let k = 0; k < S.loop; k++) { const ok = await AU.one(clip, S.rate); if (!ok) return; shTime(lineSec()); if (k < S.loop - 1) await sleep(700); } shSave(l.audio, { lvl: 0 }); };
    $('#pall', B).onclick = async () => { for (let k = S.i; k < lines.length; k++) { if (k !== S.i) { S.i = k; VIEWS.shadow(m); } const ok = await AU.one(clipOf(lines[k]), S.rate); if (!ok) return; shTime(lineSec()); await sleep(600); } };
    $('#st', B).onclick = () => AU.stop();
  } else {
    const label = { 1: '🔁 Start Echo', 2: '🗣️ Shadow now', 3: '🙈 Shadow blind' }[S.mode];
    act.innerHTML = `<button class="btn band" id="go">${label}</button><button class="btn sec" id="hear">▶ Listen first</button><button class="btn sec" id="st">⏹</button>`;
    $('#hear', B).onclick = () => AU.one(clip, S.rate);
    $('#st', B).onclick = () => { AU.stop(); Mic.stop(); msg.textContent = ''; };
    $('#go', B).onclick = async () => {
      AU.stop(); actx(); $('#go', B).disabled = true; S.fb = null; $('#fb', B).innerHTML = '';
      const rec = !choral && await Mic.open();
      if (!rec && !choral) msg.innerHTML = '🎤 Microphone not available — practise aloud; there will be no recording.';
      let blob = null, model = null;
      if (S.mode === 1) {
        msg.textContent = '👂 Listen…'; const ok = await AU.one(clip, S.rate); if (!ok) { $('#go', B).disabled = false; return; }
        await beep(880, 160); if (rec) await Mic.start(); const tStart = performance.now();
        const sec = Math.max(2, lineSec() * 1.35 + 0.8); msg.innerHTML = `🎤 Your turn! <b id="cd">${Math.ceil(sec)}</b>s <button class="btn sm ok" id="done">✓ Done</button>`;
        await new Promise(res => { let left = Math.ceil(sec); const iv = setInterval(() => { left--; const cd = $('#cd', B); if (cd) cd.textContent = Math.max(0, left); if (left <= 0) { clearInterval(iv); res(); } }, 1000); const dn = $('#done', B); if (dn) dn.onclick = () => { clearInterval(iv); res(); }; });
        if (rec) { blob = await Mic.stop(); model = { words: mwRec(0.15), turn: (tStart - Mic.t0) / 1000 }; }
        shTime(lineSec() * 2);
      } else {
        for (const f of [440, 440, 440]) { msg.textContent = '…'; await beep(f, 110); await sleep(300); }
        msg.textContent = S.mode === 3 ? '🙈 Shadow now — no text!' : '🗣️ Shadow now!';
        if (rec) await Mic.start();
        let tPlay = performance.now(); AU.el.addEventListener('playing', () => { tPlay = performance.now(); }, { once: true });
        const ok = await AU.one(clip, S.rate); await sleep(700);
        if (rec) { blob = await Mic.stop(); model = { words: mwRec((tPlay - Mic.t0) / 1000) }; }
        if (!ok) { $('#go', B).disabled = false; return; }
        shTime(lineSec());
        if (S.mode === 3) { S.revealed = true; kt.classList.remove('blind'); }
      }
      msg.textContent = '';
      shSave(l.audio, { lvl: S.mode });
      S.fb = { blob, model, A: blob ? await analyse(blob) : null };
      shFeedback($('#fb', B), l, labels, S.mode, rec, () => VIEWS.shadow(m));
      $('#go', B).disabled = false;
    };
    if (S.fb) shFeedback($('#fb', B), l, labels, S.mode, !!S.fb.blob, () => VIEWS.shadow(m));
  }
};
function shFeedback(box, l, labels, mode, rec, rerender) {
  const F = S.fb; const md = SH_MODES[mode].k; let url = null;
  let html = `<div class="card fbcard"><h3>How did it go?</h3>`;
  if (rec && F.blob) {
    url = URL.createObjectURL(F.blob);
    const J = judge(F.A, F.model, md);
    const total = Math.max(F.A ? F.A.dur : 0, F.model.words[F.model.words.length - 1][1] + 0.4);
    html += `<ul class="mlist">${J.items.map(x => `<li class="${x.ok === true ? 'ok' : x.ok === false ? 'no' : ''}">${esc(x.t)}</li>`).join('')}</ul>
      ${F.A ? rhythmSVG(F.model.words, labels, F.A.segs, total) : ''}
      <div class="ctrls" style="justify-content:flex-start;margin-top:10px"><button class="btn sm sec" id="mine">▶ My voice</button><button class="btn sm sec" id="mod">🔊 Speaker</button>${md !== 'echo' ? '<button class="btn sm sec" id="both">🎧 Both together</button>' : ''}${SRec ? '<button class="btn sm sec" id="wcb">🎯 Word check</button>' : ''}</div><div class="wc" id="wc"></div>
      ${!Store.data.settings.hp && md !== 'echo' ? '<p class="muted" style="font-size:.85rem">Without headphones, the microphone may also hear the speaker, so these measures can be less exact.</p>' : ''}`;
  } else html += `<p class="muted">No recording this time. Check yourself honestly below.</p>`;
  html += `<div style="margin-top:12px"><b>Check yourself:</b> <span class="ar">قيّم نفسك بصدق</span>
    <div class="pairrow" style="margin-top:8px">${[['r', '🎵 Rhythm like the speaker'], ['s', '🔤 Clear sounds'], ['f', '🌊 Smooth, no stops']].map(([k, t]) => `<button class="chip selfc" data-k="${k}">${t}</button>`).join('')}</div>
    <div class="ctrls" style="justify-content:flex-start;margin-top:10px"><button class="btn sm ok" id="sv">Save</button><span class="muted" id="svm"></span></div></div></div>`;
  box.innerHTML = html;
  const sel = {}; $$('.selfc', box).forEach(b => b.onclick = () => { sel[b.dataset.k] = !sel[b.dataset.k]; b.classList.toggle('on', sel[b.dataset.k]); });
  $('#sv', box).onclick = () => { const good = sel.r && sel.s && sel.f; shSave(l.audio, { lvl: mode, good: good || (shData().lines[l.audio] || {}).good }); $('#svm', box).textContent = good && mode >= 2 ? '⭐ Line mastered!' : 'Saved.'; if (good && mode >= 2) confetti(); setTimeout(rerender, 900); };
  if (url) {
    const mine = new Audio(url);
    $('#mine', box).onclick = () => { AU.stop(); mine.currentTime = 0; mine.play().catch(() => {}); };
    $('#mod', box).onclick = () => { mine.pause(); AU.one(clipOf(l), S.rate); };
    const bb = $('#both', box); if (bb) bb.onclick = () => { AU.stop(); mine.currentTime = 0; mine.play().catch(() => {}); const off = F.model.words[0][0] - (TM[l.audio] ? TM[l.audio][0][0] / S.rate : 0); setTimeout(() => AU.one(clipOf(l), S.rate), Math.max(0, off) * 1000); };
    const wb = $('#wcb', box); if (wb) wb.onclick = () => {
      const wc = $('#wc', box);
      try { const r = new SRec(); r.lang = 'en-US'; r.maxAlternatives = 3; wc.innerHTML = '<span class="muted">Say the line now…</span>';
        r.onresult = e => { const heard = new Set(); for (const a of e.results[0]) normWords(a.transcript).forEach(w => heard.add(w)); const tw = normWords(l.text); let hit = 0;
          wc.innerHTML = '<b>Word check:</b> ' + tw.map(w => { const h = heard.has(w); if (h) hit++; return `<span class="${h ? 'hit' : 'miss'}">${esc(w)}</span>`; }).join(' ') + ` <span class="muted">(${hit}/${tw.length} words recognised — words only, not pronunciation)</span>`; };
        r.onerror = ev => { wc.innerHTML = `<span class="muted">Word check is not available now (${esc(ev.error)}). It needs Chrome and internet.</span>`; }; r.start();
      } catch (e) { wc.innerHTML = '<span class="muted">Word check is not available in this browser.</span>'; }
    };
  }
}
function shFullRun(B, lines, m) {
  const choral = !!Store.data.settings.classmode;
  B.innerHTML = `<div class="card ${choral ? 'choral' : ''}"><div class="ctrls" style="justify-content:flex-start"><button class="btn band" id="go">🎬 Start Full Run</button><button class="btn sec" id="st">⏹ Stop</button></div><p id="msg" class="shmsg"></p>
    <div id="fl">${lines.map((l, i) => `<div class="tline" data-l="${i}">${avatar(l.sp, l.name)}<span style="flex:1"><span class="who" style="color:${SPC[l.sp]}">${esc(l.name)}</span><br><span class="ktext sm" id="k${i}">${wordsOf(l.text).map((w, j) => `<span class="kw" data-w="${j}">${esc(w)}</span>`).join(' ')}</span></span></div>`).join('')}</div></div><div id="fb"></div>`;
  const nodes = $$('[data-l]', B), msg = $('#msg', B);
  lines.forEach((l, i) => karaoke($('#k' + i, B), l.audio, l.text));
  $('#st', B).onclick = () => { AU.stop(); Mic.stop(); msg.textContent = ''; };
  $('#go', B).onclick = async () => {
    actx(); const rec = !choral && await Mic.open(); if (!rec && !choral) msg.textContent = '🎤 Microphone not available — shadow aloud without recording.';
    for (const f of [440, 440, 440]) { await beep(f, 110); await sleep(300); }
    msg.textContent = '🎬 Go! Shadow every line.'; if (rec) await Mic.start();
    const starts = []; const t0 = performance.now();
    const ok = await AU.list(lines.map(clipOf), { rate: S.rate, gap: 500, onLine: i => { nodes.forEach(x => x.classList.remove('playing')); if (i >= 0) { nodes[i].classList.add('playing'); nodes[i].scrollIntoView({ block: 'nearest', behavior: 'smooth' }); starts[i] = (performance.now() - (rec ? Mic.t0 : t0)) / 1000 + 0.05; } } });
    await sleep(600); const blob = rec ? await Mic.stop() : null; msg.textContent = '';
    if (!ok) return;
    shTime((performance.now() - t0) / 1000);
    lines.forEach(l => shSave(l.audio, { lvl: 4 }));
    const mw = [], labels = [];
    lines.forEach((l, i) => { const wt = wordTimes(l.audio, l.text); wt.times.forEach((w, j) => { if (w) { mw.push([starts[i] + w[0] / S.rate, starts[i] + w[1] / S.rate]); labels.push(wt.ws[j]); } }); });
    S.fb = { blob, model: { words: mw }, A: blob ? await analyse(blob) : null };
    shFeedback($('#fb', B), { audio: lines[0].audio, text: lines.map(x => x.text).join(' '), sp: lines[0].sp }, labels, 4, rec, () => VIEWS.shadow(m));
    const sv = $('#sv', B); const orig = sv.onclick; sv.onclick = () => { const good = $$('.selfc.on', B).length === 3; lines.forEach(l => shSave(l.audio, { lvl: 4, good: good || (shData().lines[l.audio] || {}).good })); $('#svm', B).textContent = good ? '⭐ All lines mastered!' : 'Saved.'; if (good) confetti(); setTimeout(() => VIEWS.shadow(m), 900); };
    const bb = $('#both', B); if (bb) bb.remove();
    const md = $('#mod', B); if (md) md.onclick = () => AU.list(lines.map(clipOf), { rate: S.rate, gap: 500 });
  };
}
