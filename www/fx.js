/* Answer reactions, shared by every department of From Zero To Hero.
   Right answer: an animated cheer (a pop-up badge, a burst of stars, confetti) with a bright sound and a spoken word of praise.
   Wrong answer: a kind "try again" badge that wobbles, a gentle nudge of the page, and a soft, rising sound.
   Cheer.show(ok, text, ar)  – the animation only (the main app plays its own sounds).
   Cheer.react(ok, opts)     – sound + spoken word + animation (used by the Grammar and Vocabulary department).
   Everything is drawn with HTML and CSS; nothing is downloaded. Reduced-motion settings are respected. */
(function () {
  'use strict';
  const AR = {
    'Great job!': 'أحسنت!', 'Well done!': 'عمل جيد!', 'Excellent!': 'ممتاز!', 'You got it!': 'إجابة صحيحة!', "That's right!": 'هذا صحيح!',
    'Super!': 'رائع!', 'Brilliant!': 'مذهل!', 'Perfect!': 'متقن!', 'Awesome!': 'مدهش!', 'Nice work!': 'عمل جميل!',
    'Oops! Not this time.': 'ليس هذه المرة.', 'Nice try!': 'محاولة جيدة!', 'Almost!': 'اقتربت!', 'Not quite.': 'ليس تمامًا.',
    'Keep going!': 'واصل!', "Don't give up!": 'لا تستسلم!',
    'Good try! Practise and try again.': 'محاولة جيدة! تدرّب وحاول مرة أخرى.', 'Keep practising. You can do it!': 'واصل التدريب، أنت تستطيع!',
    "You're getting better. Try again!": 'أنت تتحسن. حاول مرة أخرى!'
  };
  const GOOD = ['Great job!', 'Excellent!', 'Well done!', 'Super!', 'You got it!', 'Brilliant!', 'Awesome!'];
  const TRY = ['Nice try!', 'Almost!', 'Keep going!', "Don't give up!"];
  const EM_OK = ['🌟', '🎉', '👏', '🏅', '🥳', '💯'], EM_NO = ['💪', '🌱', '🤗', '🧗'];
  const COLORS = ['#F2B330', '#E0566F', '#2F9BF0', '#1FB877', '#9B6CF6', '#FF7A59'];
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const still = () => window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;

  const CSS = `
.fx{position:fixed;inset:0;z-index:70;pointer-events:none;display:grid;place-items:center;overflow:hidden}
.fx-card{position:relative;display:flex;flex-direction:column;align-items:center;gap:2px;max-width:86vw;padding:18px 34px 16px;border-radius:28px;background:#fff;text-align:center;
  box-shadow:0 22px 60px rgba(20,30,60,.3);border:4px solid #F2B330;animation:fxPop .5s cubic-bezier(.2,1.5,.4,1) both,fxOut .4s ease-in 1.15s forwards}
.fx-no .fx-card{border-color:#FFB25B;animation:fxPop .45s cubic-bezier(.2,1.4,.4,1) both,fxOut .4s ease-in 1.4s forwards}
.fx-em{font-size:3.4rem;line-height:1.1;display:inline-block;animation:fxSpin .9s cubic-bezier(.2,1.4,.4,1) both}
.fx-no .fx-em{animation:fxWob 1.1s ease-in-out both}
.fx-t{font:800 1.9rem/1.15 "Baloo 2","Nunito","Segoe UI",system-ui,sans-serif;color:#0B8A5A;letter-spacing:.01em}
.fx-no .fx-t{color:#C2570C}
.fx-t i{display:inline-block;font-style:normal;animation:fxLetter .5s cubic-bezier(.2,1.6,.4,1) both;animation-delay:calc(.12s + var(--i) * .03s)}
.fx-ar{font:700 1.15rem/1.6 "Tajawal","Cairo","Segoe UI",Arial,sans-serif;color:#3D4A63;direction:rtl}
.fx-ring{position:absolute;left:50%;top:50%;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;border:6px solid #F2B330;opacity:0;animation:fxRing .9s ease-out .05s both}
.fx-no .fx-ring{border-color:#FFB25B;animation:fxRing 1.1s ease-out .05s both}
.fx-burst{position:absolute;left:50%;top:50%;width:0;height:0}
.fx-burst i{position:absolute;left:0;top:0;font-style:normal;font-size:var(--s);color:var(--c);line-height:1;transform:translate(-50%,-50%);opacity:0;
  animation:fxFly 1s cubic-bezier(.15,.8,.3,1) var(--t) both}
.fx-rain i{position:absolute;top:-24px;left:var(--x);width:10px;height:16px;border-radius:3px;background:var(--c);opacity:0;animation:fxRain var(--d) linear var(--t) both}
.fx-lite{position:fixed;left:50%;top:18%;z-index:70;pointer-events:none;font-size:2.6rem;line-height:1;transform:translateX(-50%);animation:fxLite .8s cubic-bezier(.2,1.4,.4,1) both}
.fx-nudge{animation:fxNudge .5s ease-in-out both}
@keyframes fxPop{from{opacity:0;transform:scale(.4) translateY(30px)}}
@keyframes fxOut{to{opacity:0;transform:translateY(-22px) scale(.94)}}
@keyframes fxSpin{0%{transform:scale(0) rotate(-200deg)}60%{transform:scale(1.25) rotate(14deg)}80%{transform:scale(.94) rotate(-6deg)}100%{transform:none}}
@keyframes fxWob{0%{transform:scale(.4)}18%{transform:scale(1.1) rotate(-14deg)}36%{transform:rotate(12deg)}54%{transform:rotate(-9deg)}72%{transform:rotate(6deg) translateY(-6px)}100%{transform:none}}
@keyframes fxLetter{from{opacity:0;transform:translateY(16px) scale(.5)}}
@keyframes fxRing{0%{opacity:.9;transform:scale(.4)}100%{opacity:0;transform:scale(3.4)}}
@keyframes fxFly{0%{opacity:0;transform:translate(-50%,-50%) scale(.2)}15%{opacity:1}100%{opacity:0;transform:translate(calc(-50% + var(--dx)),calc(-50% + var(--dy))) scale(1) rotate(var(--r))}}
@keyframes fxRain{0%{opacity:0;transform:translateY(0) rotate(0)}10%{opacity:1}100%{opacity:0;transform:translateY(105vh) rotate(var(--r))}}
@keyframes fxLite{0%{opacity:0;transform:translateX(-50%) scale(.3)}40%{opacity:1;transform:translateX(-50%) scale(1.15)}100%{opacity:0;transform:translateX(-50%) translateY(-40px) scale(1)}}
@keyframes fxNudge{0%,100%{transform:none}20%{transform:translateX(-7px)}40%{transform:translateX(6px)}60%{transform:translateX(-4px)}80%{transform:translateX(2px)}}
@media (max-width:520px){.fx-t{font-size:1.5rem}.fx-em{font-size:2.8rem}.fx-card{padding:14px 22px 12px}}
@media (prefers-reduced-motion:reduce){.fx-card{animation:fxFade 1.5s ease both}.fx-em,.fx-t i,.fx-lite{animation:none}.fx-ring,.fx-burst,.fx-rain{display:none}.fx-nudge{animation:none}}
@keyframes fxFade{0%,100%{opacity:0}12%,85%{opacity:1}}`;
  let styled = false;
  function style() { if (styled) return; styled = true; const s = document.createElement('style'); s.textContent = CSS; document.head.appendChild(s); }
  const esc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function show(ok, text, ar) {
    style();
    document.querySelectorAll('.fx').forEach(x => x.remove());
    const t = text || pick(ok ? GOOD : TRY), a = ar || AR[t] || (ok ? 'أحسنت!' : 'حاول مرة أخرى!');
    const d = document.createElement('div'); d.className = 'fx ' + (ok ? 'fx-ok' : 'fx-no'); d.setAttribute('role', 'status'); d.setAttribute('aria-live', 'polite');
    let h = '';
    if (ok && !still()) {
      h += '<div class="fx-rain">' + Array.from({ length: 18 }, (_, i) => `<i style="--x:${Math.round(Math.random() * 100)}%;--c:${COLORS[i % COLORS.length]};--d:${(1.1 + Math.random() * .7).toFixed(2)}s;--t:${(Math.random() * .35).toFixed(2)}s;--r:${Math.round(200 + Math.random() * 500)}deg"></i>`).join('') + '</div>';
      h += '<div class="fx-burst">' + Array.from({ length: 14 }, (_, i) => { const an = (i / 14) * Math.PI * 2 + Math.random() * .3, r = 130 + Math.random() * 110;
        return `<i style="--dx:${Math.round(Math.cos(an) * r)}px;--dy:${Math.round(Math.sin(an) * r)}px;--c:${COLORS[i % COLORS.length]};--s:${Math.round(18 + Math.random() * 20)}px;--t:${(Math.random() * .12).toFixed(2)}s;--r:${Math.round(Math.random() * 360)}deg">${i % 3 ? '★' : '✦'}</i>`; }).join('') + '</div>';
    }
    h += `<div class="fx-card"><span class="fx-ring"></span><span class="fx-em">${pick(ok ? EM_OK : EM_NO)}</span><b class="fx-t">${[...t].map((c, i) => c === ' ' ? ' ' : `<i style="--i:${i}">${esc(c)}</i>`).join('')}</b><span class="fx-ar" lang="ar">${esc(a)}</span></div>`;
    d.innerHTML = h; document.body.appendChild(d);
    if (!ok) nudge();
    setTimeout(() => d.remove(), ok ? 1650 : 1900);
    return t;
  }
  function nudge() {
    const m = document.querySelector('main') || document.getElementById('app'); if (!m || still()) return;
    m.classList.remove('fx-nudge'); void m.offsetWidth; m.classList.add('fx-nudge'); setTimeout(() => m.classList.remove('fx-nudge'), 600);
  }
  function lite(ok) {
    style(); const d = document.createElement('div'); d.className = 'fx-lite'; d.textContent = ok ? pick(['⭐', '✨', '👍']) : '💪';
    document.body.appendChild(d); setTimeout(() => d.remove(), 850); if (!ok) nudge();
  }

  /* ---- sound (only used where the page has no sound engine of its own) ---- */
  let ctx = null, gain = null, src = null; const bufs = {};
  function out() {
    try { if (!ctx) { const C = window.AudioContext || window.webkitAudioContext; if (!C) return null; ctx = new C(); gain = ctx.createGain(); gain.gain.value = .9; gain.connect(ctx.destination); }
      if (ctx.state === 'suspended') ctx.resume(); return ctx; } catch (e) { return null; }
  }
  function tone(f, t, d, o) {
    const c = out(); if (!c) return; o = o || {};
    try { const t0 = c.currentTime + t, os = c.createOscillator(), g = c.createGain(), v = o.v || .16;
      os.type = o.type || 'sine'; os.frequency.setValueAtTime(f, t0); if (o.to) os.frequency.exponentialRampToValueAtTime(o.to, t0 + d);
      g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(v, t0 + .01); g.gain.exponentialRampToValueAtTime(.0001, t0 + d);
      os.connect(g); g.connect(gain); os.start(t0); os.stop(t0 + d + .05); } catch (e) {}
  }
  const bell = (f, t, d, v) => { tone(f, t, d, { v }); tone(f * 2.01, t, d * .6, { v: v * .3 }); };
  function sfx(ok) {
    if (ok) { [1046.5, 1318.5, 1568].forEach((f, i) => bell(f, i * .08, .42, .14)); for (let i = 0; i < 6; i++) tone(2000 + Math.random() * 2200, .3 + i * .06, .13, { v: .04 }); }
    else { tone(349.23, 0, .18, { type: 'triangle', v: .15 }); tone(293.66, .16, .2, { type: 'triangle', v: .15 }); tone(440, .38, .42, { type: 'triangle', v: .14 }); }
  }
  function clip(kind, i) {
    const L = window.LSP_RX && window.LSP_RX[kind], it = L && L[i], c = out(); if (!it || !c) return Promise.resolve(null);
    const k = kind + i; if (bufs[k]) return bufs[k];
    return bufs[k] = new Promise(res => { try { const bin = atob(it.a), u = new Uint8Array(bin.length); for (let j = 0; j < bin.length; j++) u[j] = bin.charCodeAt(j);
      const pr = c.decodeAudioData(u.buffer, res, () => res(null)); if (pr && pr.catch) pr.catch(() => res(null)); } catch (e) { res(null); } });
  }
  function say(kind, i) {
    clip(kind, i).then(b => { if (!b || !ctx) return; try { if (src) src.stop(); } catch (e) {} const s = ctx.createBufferSource(); s.buffer = b; s.connect(gain); src = s; try { s.start(); } catch (e) {} });
  }
  const Cheer = {
    show, lite, ar: AR,
    /* sounds follow the app's 🔔 Sounds setting; a page can replace this test */
    soundOn() { try { const d = JSON.parse(localStorage.getItem('lsp_v1') || '{}'); return !(d.settings && d.settings.rx === false); } catch (e) { return true; } },
    react(ok, opts) {
      opts = opts || {};
      const kind = ok ? 'right' : 'wrong', L = (window.LSP_RX && window.LSP_RX[kind]) || [], i = L.length ? Math.floor(Math.random() * L.length) : -1, on = this.soundOn();
      if (opts.lite) { lite(ok); if (on) sfx(ok); return; }
      show(ok, i >= 0 ? L[i].t : null);
      if (on) { sfx(ok); if (i >= 0) setTimeout(() => say(kind, i), ok ? 300 : 520); }
    }
  };
  window.Cheer = Cheer;
})();
