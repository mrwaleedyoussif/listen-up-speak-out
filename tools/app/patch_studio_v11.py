"""Studio v1.1: listen first -> 2-second get-ready with sounds -> record (live voice meter)
-> clear score card (stars, %, four criteria, one tip, English + Arabic). Also keeps the audio
output awake so the first sound of a clip is never lost."""
import sys
p = sys.argv[1] if len(sys.argv) > 1 else 'www/index.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:90]); s = s.replace(old, new)
def between(a, b, new):
    global s
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]

# ---------- CSS ----------
rep('''textarea.bk{''', '''/* studio v1.1: phases, countdown, live voice meter, score card */
.phase{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin:12px 0 0}
.phase span{padding:5px 12px;border-radius:99px;background:#EEF1F7;color:var(--muted);font-weight:800;font-size:.85rem}
.phase span.on{background:var(--c);color:#fff}
.phase span.done{background:var(--cl);color:var(--cd)}
.cdown{display:inline-grid;place-items:center;width:64px;height:64px;border-radius:50%;background:var(--sun);color:#1D2433;font-family:var(--fh);font-size:2.2rem;font-weight:800;animation:cdp 1s ease-out infinite;vertical-align:middle;margin-right:10px}
@keyframes cdp{0%{box-shadow:0 0 0 0 rgba(255,194,51,.75)}100%{box-shadow:0 0 0 20px rgba(255,194,51,0)}}
.recdot{display:inline-block;width:16px;height:16px;border-radius:50%;background:var(--bad);margin-right:8px;vertical-align:-2px;animation:rp 1s infinite}
@keyframes rp{50%{opacity:.25}}
.recbox{display:flex;flex-direction:column;align-items:center;gap:8px}
.recbar{width:min(420px,90%);height:10px;border-radius:99px;background:var(--line);overflow:hidden}.recbar i{display:block;height:100%;width:0;background:var(--bad)}
.vu{display:flex;gap:3px;align-items:flex-end;height:30px}.vu i{width:7px;border-radius:3px;background:#D5DAE5;height:6px;transition:height .06s}.vu i.on{background:var(--ok)}
.fbtop{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.fbstars{font-size:2.1rem;letter-spacing:2px;color:var(--sun);line-height:1}.fbstars .off{color:#D5DAE5}
.fbscore{margin-left:auto;font-family:var(--fh);font-size:2.1rem;font-weight:800;color:var(--cd)}
.crit{display:grid;gap:8px;margin:12px 0}
.crow{display:grid;grid-template-columns:34px 110px 1fr;gap:8px;align-items:center;padding:8px 12px;border-radius:12px;background:#F5F7FC}
.crow .ci{font-size:1.3rem;text-align:center}.crow b{font-family:var(--fh)}
.crow.g2{background:var(--ok-l)}.crow.g1{background:#FFF6DE}.crow.g0{background:var(--bad-l)}
.crow .cd{font-size:.95rem}
.sbars{display:grid;gap:4px;margin-top:5px;max-width:360px}.sbars span{display:block;height:9px;border-radius:99px}
.tipbox{background:#F1ECFF;border-radius:14px;padding:10px 14px;margin:8px 0;font-weight:700;color:#3B2A8F}
.honest{font-size:.82rem;color:var(--muted);margin:.5rem 0 0}
@media (max-width:640px){.crow{grid-template-columns:30px 1fr}.crow .cd{grid-column:1/-1}.fbscore{font-size:1.7rem}}
textarea.bk{''')

# ---------- modes ----------
between("  { k: 'echo', icon: '🔁'", "];\nconst VOICED_TH", """  { k: 'echo', icon: '🔁', name: 'Echo', en: 'Listen first. After the 2-second countdown, say the line in the same way.', ar: 'استمع أولًا، وبعد العدّ التنازلي (ثانيتان) قل الجملة بالطريقة نفسها.' },
  { k: 'shadow', icon: '🗣️', name: 'Shadow', en: 'Listen first. After the 2-second countdown, speak at the same time as the speaker.', ar: 'استمع أولًا، وبعد العدّ التنازلي تحدّث في الوقت نفسه مع المتحدث.' },
  { k: 'blind', icon: '🙈', name: 'Blind Shadow', en: 'Listen first, then shadow without the text — use only your ears! The text appears after you finish.', ar: 'استمع أولًا ثم ظلّل دون النص معتمدًا على أذنيك فقط! يظهر النص بعد أن تنتهي.' },
  { k: 'run', icon: '🎬', name: 'Full Run', en: 'Listen to the whole conversation, then shadow all the lines without stopping.', ar: 'استمع إلى المحادثة كاملة، ثم ظلّل جميع الجمل دون توقف.' }
""")

# ---------- word tap: start a little earlier so the first sound is not cut ----------
rep("el.currentTime = base + Math.max(0, a - 0.03);", "el.currentTime = base + Math.max(0, a - 0.08);")
rep("setTimeout(() => { if (tok === this.token) el.pause(); res(); }, (b - a + 0.08) / (rate || 1) * 1000);",
    "setTimeout(() => { if (tok === this.token) el.pause(); res(); }, (b - a + 0.16) / (rate || 1) * 1000);")

# ---------- keep the audio output awake (Bluetooth speakers, Android, Windows) ----------
rep("AU.range = function (c, a, b, rate) {", """/* Keep the sound output awake: many speakers, Bluetooth links and phones need a moment to wake up,
   which cuts the first sound of a clip. A silent tone (-100 dB) keeps the output open while the app is visible. */
const Warm = {
  on: false,
  start() {
    const c = actx(); if (!c || this.on) return;
    try { const o = c.createOscillator(), g = c.createGain(); o.frequency.value = 40; g.gain.value = 0.00001; o.connect(g); g.connect(c.destination); o.start(); this.on = true; } catch (e) {}
  }
};
document.addEventListener('pointerdown', () => Warm.start(), { capture: true });
document.addEventListener('keydown', () => Warm.start(), { capture: true });
document.addEventListener('visibilitychange', () => { if (!ACX) return; try { document.hidden ? ACX.suspend() : ACX.resume(); } catch (e) {} });
AU.range = function (c, a, b, rate) {""")

# ---------- microphone level (live voice meter) ----------
rep("""  close() { try { if (this.mr && this.mr.state !== 'inactive') this.mr.stop(); } catch (e) {} try { this.stream && this.stream.getTracks().forEach(t => t.stop()); } catch (e) {} this.stream = null; }
};""", """  close() { try { if (this.mr && this.mr.state !== 'inactive') this.mr.stop(); } catch (e) {} try { this.stream && this.stream.getTracks().forEach(t => t.stop()); } catch (e) {} this.stream = null; },
  level() {   // loudness of the microphone right now (0 … about 0.3)
    const c = actx(); if (!c || !this.stream) return 0;
    try {
      if (this.anS !== this.stream) { this.an = c.createAnalyser(); this.an.fftSize = 1024; c.createMediaStreamSource(this.stream).connect(this.an); this.anS = this.stream; this.buf = new Uint8Array(this.an.fftSize); }
      this.an.getByteTimeDomainData(this.buf); let s = 0; for (let i = 0; i < this.buf.length; i++) { const v = (this.buf[i] - 128) / 128; s += v * v; } return Math.sqrt(s / this.buf.length);
    } catch (e) { return 0; }
  }
};
/* --- the recording routine: listen first -> 2-second get ready -> speak --- */
const SHT = { tok: 0 };
const PHASES = `<div class="phase" id="ph">${[['👂', 'Listen', 'استمع'], ['⏳', 'Get ready', 'استعد'], ['🎤', 'Speak', 'تحدّث'], ['📊', 'Result', 'النتيجة']].map((x, i) => `<span data-p="${i + 1}" title="${x[2]}">${i + 1} ${x[0]} ${x[1]}</span>`).join('')}</div>`;
function setPhase(B, n) { $$('#ph [data-p]', B).forEach(x => { const k = +x.dataset.p; x.classList.toggle('on', k === n); x.classList.toggle('done', k < n); }); }
async function getReady(msg, tok) {
  for (const n of [2, 1]) {
    if (tok !== SHT.tok) return false;
    msg.innerHTML = `<span class="cdown">${n}</span><b>Get ready…</b> <span class="ar">استعد…</span>`;
    beep(660, 130); await sleep(1000);
  }
  if (tok !== SHT.tok) return false;
  msg.innerHTML = '<b>🎤 Go!</b> <span class="ar">ابدأ!</span>';
  await beep(1047, 260);
  return tok === SHT.tok;
}
function recUI(msg, en, ar, rec, done) {
  msg.innerHTML = `<div class="recbox"><div>${rec ? '<span class="recdot"></span>' : '🗣️ '}<b>${en}</b> <span class="ar">${ar}</span></div>${rec ? `<div class="vu" aria-hidden="true">${'<i></i>'.repeat(14)}</div>` : ''}<div class="recbar"><i></i></div>${done ? '<button class="btn sm ok rdone">✓ Done</button>' : ''}</div>`;
}
function recLoop(msg, sec, tok, auto) {   // progress bar + voice meter; with auto, stops when the student has finished speaking
  let fin = false, iv = 0, end = () => {};
  const done = new Promise(r => { end = () => { if (!fin) { fin = true; clearInterval(iv); r(); } }; });
  const t0 = performance.now(), vu = $$('.vu i', msg), bar = $('.recbar i', msg), dn = $('.rdone', msg); let heard = false, q0 = 0;
  if (dn) dn.onclick = () => end();
  iv = setInterval(() => {
    if (tok !== SHT.tok) return end();
    const el = (performance.now() - t0) / 1000; if (bar) bar.style.width = Math.min(100, 100 * el / sec) + '%';
    const lv = Mic.level(), n = Math.min(vu.length, Math.round(Math.min(1, lv / 0.15) * vu.length));
    vu.forEach((v, i) => { const on = i < n; v.classList.toggle('on', on); v.style.height = (on ? 8 + 20 * (i + 1) / vu.length : 6) + 'px'; });
    if (auto) { if (lv > 0.025) { heard = true; q0 = 0; } else if (heard) { if (!q0) q0 = performance.now(); else if (performance.now() - q0 > 1300 && el > 1.2) end(); } }
    if (el >= sec) end();
  }, 60);
  return { done, end: () => end() };
}""")

# ---------- judging: four clear criteria, stars and a score ----------
between("function judge(A, model, mode) {", "function rhythmSVG(", r"""const CRIT_AR = { start: 'البداية', speed: 'السرعة', flow: 'الانسياب', voice: 'الصوت' };
function judge(A, model, mode) {
  if (!A) return { na: true };
  if (!A.segs.length || A.peak < 0.01) return { silent: true };
  const mw = model.words, m0 = mw[0][0], m1 = mw[mw.length - 1][1], s0 = A.segs[0][0], s1 = A.segs[A.segs.length - 1][1], rows = [];
  const row = (k, g, title, d, en, ar, x) => rows.push(Object.assign({ k, g, title, d, en, ar }, x || {}));
  if (mode === 'echo') {
    const lag = Math.max(0, s0 - (model.turn || 0));
    if (lag <= 1) row('start', 2, 'Start', `You started ${lag.toFixed(1)} s after the go sound.`);
    else row('start', lag <= 2 ? 1 : 0, 'Start', `You waited ${lag.toFixed(1)} s after the go sound.`, 'Start speaking right after the go sound.', 'ابدأ الكلام مباشرة بعد صوت البدء.');
  } else {
    const lag = s0 - m0;
    if (Math.abs(lag) <= 0.4) row('start', 2, 'Start', 'You started together with the speaker.');
    else if (lag < 0) row('start', lag < -0.9 ? 0 : 1, 'Start', `You started ${(-lag).toFixed(1)} s before the speaker.`, 'Wait for the speaker’s first word, then go together.', 'انتظر أول كلمة من المتحدث ثم انطلقا معًا.');
    else row('start', lag <= 0.9 ? 1 : 0, 'Start', `You started ${lag.toFixed(1)} s after the speaker.`, 'Start with the speaker’s first word.', 'ابدأ مع أول كلمة يقولها المتحدث.');
  }
  const you = s1 - s0, sp = Math.max(0.3, m1 - m0), r = you / sp, sx = { you, sp };
  const sd = `Speaker ${sp.toFixed(1)} s · You ${you.toFixed(1)} s`;
  if (r >= 0.8 && r <= 1.25) row('speed', 2, 'Speed', sd + ' — the same speed.', '', '', sx);
  else if (r > 1.25) row('speed', r <= 1.5 ? 1 : 0, 'Speed', sd + ' — slower.', 'You were slower than the speaker. Keep up with the words.', 'كنت أبطأ من المتحدث، حاول أن تجاريه في الكلمات.', sx);
  else row('speed', r >= 0.65 ? 1 : 0, 'Speed', sd + ' — faster.', 'You finished too fast. Did you say every word? Say them all clearly.', 'أنهيت بسرعة كبيرة؛ هل قلت كل الكلمات؟ قلها كلها بوضوح.', sx);
  const gaps = (arr, min) => arr.slice(1).filter((g, i) => g[0] - arr[i][1] > min).length;
  const extra = Math.max(0, gaps(A.segs, 0.5) - gaps(mw, 0.35));
  if (!extra) row('flow', 2, 'Flow', 'No extra stops — your words kept flowing.');
  else row('flow', extra === 1 ? 1 : 0, 'Flow', `${extra} extra stop${extra > 1 ? 's' : ''} in the middle of the line.`, 'Join the words together — don’t stop in the middle.', 'صِل الكلمات ببعضها ولا تتوقف في منتصف الجملة.');
  if (A.peak >= 0.05) row('voice', 2, 'Voice', 'Loud and clear enough.');
  else row('voice', A.peak >= 0.02 ? 1 : 0, 'Voice', 'Your voice was quiet.', 'Speak louder and hold the device closer to you.', 'تحدّث بصوت أعلى وقرّب الجهاز منك.');
  const score = Math.round(100 * rows.reduce((t, x) => t + x.g, 0) / (rows.length * 2));
  return { rows, score, stars: score >= 85 ? 3 : score >= 60 ? 2 : 1, top: rows.find(x => x.g === 0) || rows.find(x => x.g === 1) || null, s0, s1 };
}
""")
rep("""<div class="rl"><span><i style="background:var(--c)"></i>Speaker</span><span><i style="background:var(--coral)"></i>You</span><span class="muted">This picture shows timing and pauses, not pronunciation.</span></div>`;""",
    """<div class="rl"><span><i style="background:var(--c)"></i>Speaker’s words (top)</span><span><i style="background:var(--coral)"></i>Your voice (bottom)</span><span class="muted">Try to make the two rows match.</span></div>`;""")

# ---------- the single-line routine ----------
between("  } else {\n    const label = { 1: '🔁 Start Echo'", "function shFeedback(", r"""  } else {
    const label = { 1: '🔁 Start Echo', 2: '🗣️ Start Shadow', 3: '🙈 Start Blind Shadow' }[S.mode];
    act.innerHTML = `<button class="btn band" id="go">${label}</button><button class="btn sec" id="hear">▶ Listen</button><button class="btn sec" id="st">⏹ Stop</button>`;
    act.insertAdjacentHTML('beforebegin', PHASES);
    const goB = $('#go', B);
    $('#hear', B).onclick = () => { SHT.tok++; AU.one(clip, S.rate); };
    $('#st', B).onclick = () => { SHT.tok++; AU.stop(); Mic.stop(); msg.textContent = ''; setPhase(B, 0); goB.disabled = false; };
    goB.onclick = async () => {
      AU.stop(); actx(); const tok = ++SHT.tok; goB.disabled = true; S.fb = null; $('#fb', B).innerHTML = '';
      const quit = () => { if (tok === SHT.tok) { msg.textContent = ''; setPhase(B, 0); } goB.disabled = false; };
      const rec = !choral && await Mic.open();
      // 1. listen first
      setPhase(B, 1);
      msg.innerHTML = '👂 <b>Listen first.</b> <span class="ar">استمع أولًا.</span>' + (rec || choral ? '' : '<br><span class="muted" style="font-size:.9rem">🎤 Microphone not available — practise aloud; there will be no recording.</span>');
      const heard = await AU.one(clip, S.rate); if (!heard || tok !== SHT.tok) return quit();
      shTime(lineSec());
      // 2. get ready: 2 seconds with a sound each second, then the go sound
      setPhase(B, 2); if (!(await getReady(msg, tok))) return quit();
      // 3. speak (recording)
      setPhase(B, 3); let blob = null, model = null;
      if (S.mode === 1) {
        if (rec) await Mic.start(); const tGo = performance.now();
        recUI(msg, 'Your turn — say the line!', 'دورك، قل الجملة!', rec, true);
        await recLoop(msg, Math.max(3, lineSec() * 1.5 + 1.2), tok, rec).done;
        if (tok !== SHT.tok) return quit();
        if (rec) { blob = await Mic.stop(); model = { words: mwRec(0), turn: Math.max(0, (tGo - Mic.t0) / 1000) }; }
        shTime(lineSec());
      } else {
        if (rec) await Mic.start();
        recUI(msg, S.mode === 3 ? 'Shadow now — no text!' : 'Speak with the speaker!', S.mode === 3 ? 'ظلّل الآن دون نص!' : 'تحدّث مع المتحدث الآن!', rec, false);
        const R = recLoop(msg, lineSec() + 1.2, tok, false);
        let tPlay = performance.now(); AU.el.addEventListener('playing', () => { tPlay = performance.now(); }, { once: true });
        const ok = await AU.one(clip, S.rate); await sleep(700); R.end();
        if (rec) { blob = await Mic.stop(); model = { words: mwRec((tPlay - Mic.t0) / 1000) }; }
        if (!ok || tok !== SHT.tok) return quit();
        shTime(lineSec());
        if (S.mode === 3) { S.revealed = true; kt.classList.remove('blind'); }
      }
      beep(523, 160);
      // 4. result
      setPhase(B, 4); msg.textContent = '';
      shSave(l.audio, { lvl: S.mode });
      S.fb = { blob, model, A: blob ? await analyse(blob) : null };
      shFeedback($('#fb', B), l, labels, S.mode, rec, () => VIEWS.shadow(m));
      goB.disabled = false; goB.textContent = '↻ Try again';
      try { $('#fb', B).scrollIntoView({ behavior: 'smooth', block: 'nearest' }); } catch (e) {}
    };
    if (S.fb) { setPhase(B, 4); goB.textContent = '↻ Try again'; shFeedback($('#fb', B), l, labels, S.mode, !!S.fb.blob, () => VIEWS.shadow(m)); }
  }
};
""")

# ---------- feedback card + full run ----------
between("function shFeedback(", "/* ---------- Bidi", r"""function shFeedback(box, l, labels, mode, rec, rerender) {
  const F = S.fb; const md = SH_MODES[mode].k; let url = null;
  let html = `<div class="card fbcard">`;
  if (rec && F.blob) {
    url = URL.createObjectURL(F.blob);
    const J = judge(F.A, F.model, md);
    if (J.silent) html += `<div class="fbtop"><div class="fbstars">🎤</div><div><h3 style="margin:0">We could not hear you</h3><span class="ar">لم نسمع صوتك</span></div></div>
      <div class="tipbox">💡 Check that the microphone is allowed, then speak louder, close to the device.<span class="ar ar-block">تأكد من السماح للميكروفون، ثم تحدّث بصوت أعلى بالقرب من الجهاز.</span></div>`;
    else if (J.na) html += `<h3>Your recording is ready</h3><p class="muted">This device cannot measure it. Listen and compare.</p>`;
    else {
      const [en, ar] = J.stars === 3 ? ['Excellent!', 'ممتاز!'] : J.stars === 2 ? ['Good — nearly there!', 'جيد، اقتربت!'] : ['Keep practising!', 'واصل التدريب!'];
      const bars = r => { const mx = Math.max(r.sp, r.you); return `<span class="sbars"><span style="width:${Math.round(100 * r.sp / mx)}%;background:var(--c)" title="Speaker"></span><span style="width:${Math.round(100 * r.you / mx)}%;background:var(--coral)" title="You"></span></span>`; };
      html += `<div class="fbtop"><div class="fbstars" role="img" aria-label="${J.stars} of 3 stars">${'★'.repeat(J.stars)}<span class="off">${'★'.repeat(3 - J.stars)}</span></div><div><h3 style="margin:0">${en}</h3><span class="ar">${ar}</span></div><div class="fbscore">${J.score}%</div></div>
      <div class="crit">${J.rows.map(r => `<div class="crow g${r.g}"><span class="ci">${['🔴', '🟡', '✅'][r.g]}</span><b>${r.title}<span class="ar ar-block" style="font-weight:600;font-size:.8rem">${CRIT_AR[r.k]}</span></b><span class="cd">${esc(r.d)}${r.k === 'speed' ? bars(r) : ''}</span></div>`).join('')}</div>
      ${J.top ? `<div class="tipbox">💡 Next time: ${esc(J.top.en)}<span class="ar ar-block">${esc(J.top.ar)}</span></div>` : `<div class="tipbox">🏆 Great work! Try the next line, or a faster speed.<span class="ar ar-block">عمل رائع! جرّب الجملة التالية أو سرعة أعلى.</span></div>`}`;
      if (!F.scored) { F.scored = true; const d = shData(); (l.ids || [l.audio]).forEach(a => { const o = d.lines[a] || (d.lines[a] = { lvl: -1, n: 0 }); o.best = Math.max(o.best || 0, J.score); }); Store.save(); }
    }
    let mw = F.model.words;
    if (md === 'echo' && F.A && F.A.segs.length) { const off = F.A.segs[0][0] - mw[0][0]; mw = mw.map(w => [w[0] + off, w[1] + off]); }
    const total = Math.max(F.A ? F.A.dur : 0, mw[mw.length - 1][1] + 0.4);
    html += `${F.A && !J.silent ? rhythmSVG(mw, labels, F.A.segs, total) : ''}
      <div class="ctrls" style="justify-content:flex-start;margin-top:10px"><button class="btn sm sec" id="mine">▶ My voice</button><button class="btn sm sec" id="mod">🔊 Speaker</button>${md !== 'echo' ? '<button class="btn sm sec" id="both">🎧 Both together</button>' : ''}${SRec ? '<button class="btn sm sec" id="wcb">🎯 Word check (online)</button>' : ''}</div><div class="wc" id="wc"></div>
      ${!Store.data.settings.hp && md !== 'echo' ? '<p class="honest">Without headphones, the microphone may also hear the speaker, so the start and speed can look better than they were.</p>' : ''}
      <p class="honest">The app measures start, speed, flow and loudness. It does not grade pronunciation: check your sounds below, and with your teacher.<span class="ar ar-block">يقيس التطبيق البداية والسرعة والانسياب وارتفاع الصوت، ولا يقيّم النطق؛ قيّم أصواتك بنفسك أدناه ومع معلمك.</span></p>`;
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
  B.innerHTML = `<div class="card ${choral ? 'choral' : ''}"><div class="ctrls" style="justify-content:flex-start"><button class="btn band" id="go">🎬 Start Full Run</button><button class="btn sec" id="st">⏹ Stop</button></div>${PHASES}<p id="msg" class="shmsg"></p>
    <div id="fl">${lines.map((l, i) => `<div class="tline" data-l="${i}">${avatar(l.sp, l.name)}<span style="flex:1"><span class="who" style="color:${SPC[l.sp]}">${esc(l.name)}</span><br><span class="ktext sm" id="k${i}">${wordsOf(l.text).map((w, j) => `<span class="kw" data-w="${j}">${esc(w)}</span>`).join(' ')}</span></span></div>`).join('')}</div></div><div id="fb"></div>`;
  const nodes = $$('[data-l]', B), msg = $('#msg', B), goB = $('#go', B);
  lines.forEach((l, i) => karaoke($('#k' + i, B), l.audio, l.text));
  const mark = i => { nodes.forEach(x => x.classList.remove('playing')); if (i >= 0 && nodes[i]) { nodes[i].classList.add('playing'); nodes[i].scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } };
  const secOf = l => ((TM[l.audio] ? TM[l.audio][TM[l.audio].length - 1][1] + 0.15 : 3)) / S.rate;
  $('#st', B).onclick = () => { SHT.tok++; AU.stop(); Mic.stop(); msg.textContent = ''; setPhase(B, 0); mark(-1); goB.disabled = false; };
  goB.onclick = async () => {
    AU.stop(); actx(); const tok = ++SHT.tok; goB.disabled = true; $('#fb', B).innerHTML = '';
    const quit = () => { if (tok === SHT.tok) { msg.textContent = ''; setPhase(B, 0); mark(-1); } goB.disabled = false; };
    const rec = !choral && await Mic.open();
    // 1. listen to the whole conversation first (can be skipped)
    setPhase(B, 1); let skipped = false;
    msg.innerHTML = '👂 <b>Listen to the whole conversation first.</b> <span class="ar">استمع إلى المحادثة كاملة أولًا.</span> <button class="btn sm sec" id="skip">⏭ Skip</button>' + (rec || choral ? '' : '<br><span class="muted" style="font-size:.9rem">🎤 Microphone not available — shadow aloud without recording.</span>');
    $('#skip', B).onclick = () => { skipped = true; AU.stop(); };
    const heard = await AU.list(lines.map(clipOf), { rate: S.rate, gap: 500, onLine: mark }); mark(-1);
    if (tok !== SHT.tok || (!heard && !skipped)) return quit();
    // 2. get ready
    setPhase(B, 2); if (!(await getReady(msg, tok))) return quit();
    // 3. shadow every line (recording)
    setPhase(B, 3); if (rec) await Mic.start();
    recUI(msg, 'Shadow every line!', 'ظلّل كل الجمل!', rec, false);
    const R = recLoop(msg, lines.reduce((t, l) => t + secOf(l) + 0.5, 0.6), tok, false);
    const starts = []; const t0 = performance.now();
    const ok = await AU.list(lines.map(clipOf), { rate: S.rate, gap: 500, onLine: i => { mark(i); if (i >= 0) starts[i] = (performance.now() - (rec ? Mic.t0 : t0)) / 1000 + 0.05; } });
    await sleep(600); R.end(); const blob = rec ? await Mic.stop() : null; mark(-1);
    if (!ok || tok !== SHT.tok) return quit();
    beep(523, 160);
    // 4. result
    setPhase(B, 4); msg.textContent = '';
    shTime((performance.now() - t0) / 1000);
    lines.forEach(l => shSave(l.audio, { lvl: 4 }));
    const mw = [], labels = [];
    lines.forEach((l, i) => { const wt = wordTimes(l.audio, l.text); wt.times.forEach((w, j) => { if (w) { mw.push([starts[i] + w[0] / S.rate, starts[i] + w[1] / S.rate]); labels.push(wt.ws[j]); } }); });
    S.fb = { blob, model: { words: mw }, A: blob ? await analyse(blob) : null };
    shFeedback($('#fb', B), { audio: lines[0].audio, ids: lines.map(x => x.audio), text: lines.map(x => x.text).join(' '), sp: lines[0].sp }, labels, 4, rec, () => VIEWS.shadow(m));
    const sv = $('#sv', B); sv.onclick = () => { const good = $$('.selfc.on', B).length === 3; lines.forEach(l => shSave(l.audio, { lvl: 4, good: good || (shData().lines[l.audio] || {}).good })); $('#svm', B).textContent = good ? '⭐ All lines mastered!' : 'Saved.'; if (good) confetti(); setTimeout(() => VIEWS.shadow(m), 900); };
    const bb = $('#both', B); if (bb) bb.remove();
    const md = $('#mod', B); if (md) md.onclick = () => AU.list(lines.map(clipOf), { rate: S.rate, gap: 500 });
    goB.disabled = false; goB.textContent = '↻ Try again';
  };
}

""")
# best score on the line dots
rep("""<button class="dot ${shState(x.audio)} ${i === S.i ? 'cur' : ''}" data-i="${i}" title="Line ${i + 1}">${i + 1}</button>""",
    """<button class="dot ${shState(x.audio)} ${i === S.i ? 'cur' : ''}" data-i="${i}" title="Line ${i + 1}${(shData().lines[x.audio] || {}).best ? ' · best ' + shData().lines[x.audio].best + '%' : ''}">${i + 1}</button>""")
# navigation and Stop end any running routine
rep("  const prev = S.view;\n  AU.stop();", "  const prev = S.view;\n  SHT.tok++; AU.stop();")
rep("$('#pv', B).onclick = () => { S.i--;", "$('#pv', B).onclick = () => { SHT.tok++; S.i--;")
rep("$('#nx', B).onclick = () => { S.i++;", "$('#nx', B).onclick = () => { SHT.tok++; S.i++;")
rep("$$('[data-i]', m).forEach(b => b.onclick = () => { S.i = +b.dataset.i;", "$$('[data-i]', m).forEach(b => b.onclick = () => { SHT.tok++; S.i = +b.dataset.i;")
rep("$$('[data-md]', m).forEach(b => b.onclick = () => { S.mode = +b.dataset.md;", "$$('[data-md]', m).forEach(b => b.onclick = () => { SHT.tok++; S.mode = +b.dataset.md;")
rep("const APP_VER = '1.0.0';", "const APP_VER = '1.1.0';")
open(p, 'w', encoding='utf-8').write(s)
print('studio v1.1 patched')
