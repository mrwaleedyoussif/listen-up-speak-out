"""v1.3: audio reactions for right / wrong answers and a celebration when a task is finished well."""
import sys
p = sys.argv[1] if len(sys.argv) > 1 else 'www/index.html'
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:110]); s = s.replace(old, new)


rep('<script src="img/pics/index.js"></script>', '<script src="img/pics/index.js"></script>\n<script src="sfx/reactions.js"></script>')

# ---------- styles ----------
rep("@keyframes fall{to{transform:translateY(105vh) rotate(540deg);opacity:.9}}", """@keyframes fall{to{transform:translateY(105vh) rotate(540deg);opacity:.9}}
.confetti i.c{width:11px;height:11px;border-radius:50%}.confetti i.s{width:6px;height:18px;border-radius:2px}
.confetti i.d{animation-name:fall2;animation-duration:2.4s;animation-timing-function:cubic-bezier(.25,.6,.5,1)}
@keyframes fall2{0%{transform:translate(0,0) rotate(0)}100%{transform:translate(var(--dx),108vh) rotate(var(--rot));opacity:.85}}
.celebrate{position:fixed;inset:0;display:grid;place-items:center;z-index:60;pointer-events:none}
.cbadge{background:#fff;border-radius:28px;padding:20px 34px 18px;text-align:center;border:4px solid #FFC233;box-shadow:0 22px 60px rgba(20,30,60,.32);display:flex;flex-direction:column;align-items:center;gap:2px;max-width:86vw;animation:cpop .55s cubic-bezier(.2,1.6,.4,1) both}
.cbadge .cstar{font-size:3.6rem;line-height:1.1;animation:cwob .9s ease-in-out .35s 2}
.cbadge b{font:800 1.8rem/1.2 var(--fh);color:#1D2433}.cbadge .ar{font-size:1.15rem;color:#56607A}
.cbadge .cst{color:#FFB400;font-size:1.5rem;letter-spacing:4px}
.celebrate.out .cbadge{animation:cout .45s ease-in forwards}
@keyframes cpop{from{transform:scale(.3);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes cout{to{transform:scale(.7) translateY(-40px);opacity:0}}
@keyframes cwob{0%,100%{transform:rotate(0)}25%{transform:rotate(-14deg) scale(1.15)}75%{transform:rotate(14deg) scale(1.15)}}
@keyframes rbump{40%{transform:scale(1.07)}}
@keyframes rshake{20%,60%{transform:translateX(-6px)}40%,80%{transform:translateX(6px)}}
.pick4 button.right,.bigchoice.right,.opt.right.just{animation:rbump .35s ease-out}
.pick4 button.wrong,.bigchoice.wrong{animation:rshake .4s ease-in-out}
@media (prefers-reduced-motion:reduce){.confetti{display:none}.cbadge,.cbadge .cstar,.pick4 button,.bigchoice{animation:none!important}}""")

# ---------- reaction engine ----------
rep("function confetti() {\n  const c = document.createElement('div'); c.className = 'confetti'; const cols = ['#FF6B4A', '#FFC233', '#2F7BEA', '#1FA463', '#A855F7'];\n  for (let i = 0; i < 60; i++) { const s = document.createElement('i'); s.style.left = Math.random() * 100 + 'vw'; s.style.background = cols[i % 5]; s.style.animationDelay = Math.random() * .6 + 's'; c.appendChild(s); }\n  document.body.appendChild(c); setTimeout(() => c.remove(), 2600);\n}",
"""function confetti(big) {
  const c = document.createElement('div'); c.className = 'confetti'; const cols = ['#FF6B4A', '#FFC233', '#2F7BEA', '#1FA463', '#A855F7', '#FF5FA2', '#2DD4BF'];
  const n = big ? 130 : 60;
  for (let i = 0; i < n; i++) {
    const s = document.createElement('i'); s.style.left = Math.random() * 100 + 'vw'; s.style.background = cols[i % cols.length]; s.style.animationDelay = Math.random() * (big ? .9 : .6) + 's';
    if (big) { s.className = 'd ' + ['', 'c', 's'][i % 3]; s.style.setProperty('--dx', (Math.random() * 30 - 15) + 'vw'); s.style.setProperty('--rot', (Math.random() * 900 - 450) + 'deg'); }
    c.appendChild(s);
  }
  document.body.appendChild(c); setTimeout(() => c.remove(), big ? 3600 : 2600);
}
/* ---------- Audio reactions (v1.3) ----------
   Right answer: a bright chime and a short word of praise. Wrong answer: a soft, friendly sound and a word of
   encouragement. A task finished well: fanfare, confetti, a big badge and a spoken celebration.
   The sounds are made by the app (Web Audio); the spoken words are short clips in sfx/reactions.js.
   Teachers can switch all reaction sounds off with the 🔔 button. */
const RX_AR = { 'Amazing! You did it!': 'رائع! لقد نجحت!', 'Hurray! Well done!': 'مرحى! أحسنت!', 'Fantastic work!': 'عمل رائع!', "You're a star!": 'أنت نجم!', 'Congratulations!': 'تهانينا!', "Wow! You're amazing!": 'واو! أنت مذهل!' };
const RX = {
  bufs: {}, last: {}, src: null, g: null,
  on() { return Store.data.settings.rx !== false; },
  out() { const c = actx(); if (!c) return null; if (!this.g) { this.g = c.createGain(); this.g.gain.value = 0.9; this.g.connect(c.destination); } return c; },
  tone(f, t, d, o = {}) {
    const c = this.out(); if (!c) return;
    try {
      const t0 = c.currentTime + t, os = c.createOscillator(), g = c.createGain(), v = o.v || 0.2;
      os.type = o.type || 'sine'; os.frequency.setValueAtTime(f, t0); if (o.to) os.frequency.exponentialRampToValueAtTime(o.to, t0 + d);
      g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(v, t0 + (o.a || 0.008)); g.gain.exponentialRampToValueAtTime(0.0001, t0 + d);
      os.connect(g); g.connect(this.g); os.start(t0); os.stop(t0 + d + 0.05);
    } catch (e) {}
  },
  bell(f, t, d, v) { this.tone(f, t, d, { v }); this.tone(f * 2.01, t, d * 0.6, { v: v * 0.3 }); this.tone(f * 3.01, t, d * 0.35, { v: v * 0.1 }); },
  sfx(kind) {
    if (!this.on() || !this.out()) return;
    if (kind === 'right') { this.bell(1046.5, 0, 0.32, 0.15); this.bell(1568, 0.1, 0.55, 0.15); }
    else if (kind === 'wrong') { this.tone(330, 0, 0.2, { type: 'triangle', v: 0.17, to: 290 }); this.tone(247, 0.18, 0.34, { type: 'triangle', v: 0.17, to: 208 }); }
    else if (kind === 'try') { this.tone(392, 0, 0.24, { type: 'triangle', v: 0.14 }); this.tone(523.25, 0.17, 0.42, { type: 'triangle', v: 0.14 }); }
    else if (kind === 'celeb') {
      [523.25, 659.25, 783.99].forEach((f, i) => this.bell(f, i * 0.11, 0.3, 0.13));
      [523.25, 659.25, 783.99, 1046.5].forEach(f => this.tone(f, 0.34, 1.25, { type: 'triangle', v: 0.06, a: 0.02 }));
      this.bell(1046.5, 0.34, 1.0, 0.13);
      for (let i = 0; i < 10; i++) this.tone(1900 + Math.random() * 2300, 0.5 + i * 0.085, 0.16, { v: 0.045 });
    }
  },
  load(kind, i) {
    const k = kind + i; if (this.bufs[k]) return this.bufs[k];
    const c = this.out(), it = window.LSP_RX && window.LSP_RX[kind] && window.LSP_RX[kind][i]; if (!c || !it) return Promise.resolve(null);
    return this.bufs[k] = new Promise(res => {
      try { const bin = atob(it.a), u = new Uint8Array(bin.length); for (let j = 0; j < bin.length; j++) u[j] = bin.charCodeAt(j);
        const pr = c.decodeAudioData(u.buffer, res, () => res(null)); if (pr && pr.catch) pr.catch(() => res(null)); } catch (e) { res(null); }
    });
  },
  warm() { if (this.warmed || !window.LSP_RX) return; this.warmed = true; Object.keys(window.LSP_RX).forEach(k => window.LSP_RX[k].forEach((_, i) => this.load(k, i))); },
  pick(kind) { const L = (window.LSP_RX && window.LSP_RX[kind]) || []; if (!L.length) return -1; let i; do { i = Math.floor(Math.random() * L.length); } while (L.length > 1 && i === this.last[kind]); this.last[kind] = i; return i; },
  hush() { if (this.src) { try { this.src.stop(); } catch (e) {} this.src = null; } },
  async say(kind, i) {
    if (!this.on()) return; if (i == null) i = this.pick(kind); if (i < 0) return;
    const b = await this.load(kind, i); const c = this.out(); if (!b || !c) return;
    this.hush(); const s = c.createBufferSource(); s.buffer = b; s.connect(this.g); this.src = s;
    return new Promise(res => { s.onended = () => { if (this.src === s) this.src = null; res(); }; try { s.start(); } catch (e) { res(); } setTimeout(res, b.duration * 1000 + 250); });
  },
  // a right or wrong answer: sound, then a short spoken reaction; resolves when it has finished
  async answer(ok) { if (!this.on()) return; AU.stop(); this.sfx(ok ? 'right' : 'wrong'); await sleep(ok ? 280 : 420); await this.say(ok ? 'right' : 'wrong'); },
  async praise() { if (!this.on()) return; this.sfx('right'); await sleep(280); await this.say('right'); },
  async encourage() { if (!this.on()) return; this.sfx('try'); await sleep(450); await this.say('try'); },
  // a finished task with score r (0..1): celebrate from `hi`, praise from `mid`, otherwise encourage
  done(r, hi = 0.9, mid = 0.7, msg) { if (this.on()) AU.stop(); return r >= hi ? celebrate(msg) : r >= mid ? this.praise() : this.encourage(); }
};
// msg = [English, Arabic] for the badge; without it the badge shows the spoken celebration
function celebrate(msg, stars) {
  confetti(true);
  const i = RX.pick('celeb'), said = i >= 0 ? window.LSP_RX.celeb[i].t : 'Well done!';
  const m = msg || [said, RX_AR[said] || 'أحسنت!'];
  $$('.celebrate').forEach(x => x.remove());
  const d = document.createElement('div'); d.className = 'celebrate'; d.setAttribute('role', 'status');
  d.innerHTML = `<div class="cbadge"><span class="cstar">🏆</span>${stars ? `<span class="cst">${'★'.repeat(stars)}</span>` : ''}<b>${esc(m[0])}</b><span class="ar">${esc(m[1])}</span></div>`;
  document.body.appendChild(d); setTimeout(() => d.classList.add('out'), 2300); setTimeout(() => d.remove(), 2800);
  if (!RX.on()) return Promise.resolve();
  RX.sfx('celeb'); return sleep(700).then(() => RX.say('celeb', i));
}""")
rep("document.addEventListener('pointerdown', () => Warm.start(), { capture: true });",
    "document.addEventListener('pointerdown', () => { Warm.start(); RX.warm(); }, { capture: true });")
# a new recording or line always stops a reaction that is still speaking
rep("  async one(c, rate, node) {\n    this.stop();", "  async one(c, rate, node) {\n    RX.hush(); this.stop();")
rep("  async list(items, o = {}) {\n    this.stop();", "  async list(items, o = {}) {\n    RX.hush(); this.stop();")
rep("AU.range = function (c, a, b, rate) {\n  this.stop();", "AU.range = function (c, a, b, rate) {\n  RX.hush(); this.stop();")

# ---------- header switch ----------
rep("""    <button class="chip ${Store.data.settings.classmode ? 'on' : ''}" id="cmT" title="Teacher / class mode">🧑‍🏫 <span class="hide-sm">Class mode</span></button>""",
    """    <button class="chip ${Store.data.settings.classmode ? 'on' : ''}" id="cmT" title="Teacher / class mode">🧑‍🏫 <span class="hide-sm">Class mode</span></button>
    <button class="chip ${RX.on() ? 'on' : ''}" id="rxT" title="Sounds for right and wrong answers" aria-pressed="${RX.on()}">${RX.on() ? '🔔' : '🔕'} <span class="hide-sm">Sounds</span></button>""")
rep("""  $('#cmT').onclick = () => {""", """  $('#rxT').onclick = () => { const on = !RX.on(); Store.data.settings.rx = on; Store.save(); const b = $('#rxT'); b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); b.firstChild.textContent = on ? '🔔 ' : '🔕 '; if (on) RX.praise(); else RX.hush(); };
  $('#cmT').onclick = () => {""")
rep("""    <li><b>Class mode (🧑‍🏫):</b>""", """    <li><b>Sounds (🔔):</b> a chime and a spoken word of praise for right answers, a soft sound and a word of encouragement for wrong ones, and a celebration (fanfare, confetti, trophy) when a task is finished well. Press 🔔 to switch them off, for example during a quiet test.</li>
    <li><b>Class mode (🧑‍🏫):</b>""")

# ---------- hooks ----------
# listening and speaking lessons finished
rep("else { const r = S.best || 0; Store.rec(L.id, { done: true, stars: starsFor(r), best: r }); confetti(); go('unit', { g: S.g, u: S.u }); }",
    "else { const r = S.best || 0; Store.rec(L.id, { done: true, stars: starsFor(r), best: r }); celebrate(['Lesson complete!', 'أنهيت الدرس!'], starsFor(r)); go('unit', { g: S.g, u: S.u }); }")
rep("Store.rec(L.id, { done: true, stars: Math.max(starsFor(r), S.roleDone ? 1 : 0), best: r }); confetti(); go('unit', { g: S.g, u: S.u }); }",
    "Store.rec(L.id, { done: true, stars: Math.max(starsFor(r), S.roleDone ? 1 : 0), best: r }); celebrate(['Lesson complete!', 'أنهيت الدرس!'], Math.max(starsFor(r), S.roleDone ? 1 : 0)); go('unit', { g: S.g, u: S.u }); }")
# listening tasks checked
rep("    if (r >= .9) confetti();\n    renderTasks(P, L);", "    RX.done(r, .9, .7, r === 1 ? ['Perfect score!', 'علامة كاملة!'] : null);\n    renderTasks(P, L);")
# sound check: every answer, then the result
rep("    Q.res.push(c.ok);\n    await sleep(c.ok ? 900 : 1900);", "    Q.res.push(c.ok);\n    await Promise.all([sleep(c.ok ? 900 : 1900), RX.answer(c.ok)]);")
rep("Store.rec(L.id, { stars: starsFor(r), best: r }); if (r >= .9) confetti();", "Store.rec(L.id, { stars: starsFor(r), best: r }); if (!Q.cel) { Q.cel = true; RX.done(r, .9, .7, r >= .9 ? ['Super ears!', 'أذنان رائعتان!'] : null); }")
# role-play finished
rep("if (ok) { S.roleDone = true; $('#rmsg', P).innerHTML = '🎉 Well done! Now swap roles and try again.'; }",
    "if (ok) { S.roleDone = true; $('#rmsg', P).innerHTML = '🎉 Well done! Now swap roles and try again.'; RX.praise(); }")
# games: every round, lineup plays the right order after the reaction, the result
rep("const nextRound = async ok => { st.res.push(ok); if (ok) { st.streak++; st.score += 10 + Math.min(st.streak - 1, 5) * 2; } else st.streak = 0; await sleep(ok ? 900 : 2000); if (S.st !== st) return;",
    "const nextRound = async (ok, after) => { st.res.push(ok); if (ok) { st.streak++; st.score += 10 + Math.min(st.streak - 1, 5) * 2; } else st.streak = 0; const t0 = performance.now(); await RX.answer(ok); if (after && S.st === st) await after(); const left = (ok ? 900 : 2000) - (performance.now() - t0); if (left > 0) await sleep(left); if (S.st !== st) return;")
rep("if (!ok) AU.list(R.seg.map(clipOf), { gap: 400 }); nextRound(ok); };", "nextRound(ok, ok ? null : () => AU.list(R.seg.map(clipOf), { gap: 400 })); };")
rep("Store.rec(u.id + S.game, { stars: starsFor(r), best: r, done: true }); if (r >= .7) confetti();",
    "Store.rec(u.id + S.game, { stars: starsFor(r), best: r, done: true }); if (!st.cel) { st.cel = true; RX.done(r, .7, .5, r >= .7 ? [r === 1 ? 'Perfect game!' : 'Great game!', r === 1 ? 'لعبة مثالية!' : 'لعبة رائعة!'] : null); }")
# unit check result
rep("Store.rec(u.id + 'check', { stars: starsFor(r), best: r, done: true }); if (r >= .7) confetti();",
    "Store.rec(u.id + 'check', { stars: starsFor(r), best: r, done: true }); if (!C.cel) { C.cel = true; RX.done(r, .7, .7, ['You passed the Unit Check!', 'نجحت في اختبار الوحدة!']); }")
# shadowing score card (once per recording), mastered lines
rep("      if (!F.scored) { F.scored = true; const d = shData();",
    "      if (!F.scored) { F.scored = true; if (J.stars === 3) celebrate(null, 3); else if (J.stars === 2) RX.praise(); else RX.encourage(); const d = shData();")
rep("if (good && mode >= 2) confetti(); setTimeout(rerender, 900);", "if (good && mode >= 2) celebrate(['Line mastered!', 'أتقنت الجملة!']); setTimeout(rerender, 900);")
rep("if (good) confetti(); setTimeout(() => VIEWS.shadow(m), 900);", "if (good) celebrate(['All lines mastered!', 'أتقنت كل الجمل!']); setTimeout(() => VIEWS.shadow(m), 900);")

rep("const APP_VER = '1.2.0';", "const APP_VER = '1.3.0';")
open(p, 'w', encoding='utf-8').write(s)
print('v1.3 patched')
