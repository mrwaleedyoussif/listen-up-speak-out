/* Cursive Handwriting department: interactive practice for letters, joined letters and words.
   Every item has three steps: Watch (the app writes it and shows where to start and which way to go),
   Trace (write over the model) and Write (write it alone on the lines). The app measures the writing against the
   model's pen strokes and shows what was covered, what was missed and where the line left the path.
   Data: hw/data.js (single-stroke cursive letters in writing order, built by tools/app/build_hw.py). */
const HWX = (() => {
  'use strict';
  const D = () => window.HW_DATA;
  const A = '#F2994A', B = '#D9480F';
  const PASS = 60;
  const V = {};
  const CSS = `
.hw-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:10px;margin-top:10px}
.hw-tile{display:flex;flex-direction:column;align-items:center;gap:2px;padding:10px 6px;border-radius:16px;border:2px solid var(--line,#E3E7F0);background:#fff;cursor:pointer;font:inherit;transition:transform .2s}
.hw-tile:hover{transform:translateY(-3px);border-color:${A}}.hw-tile.done{border-color:#22B573;background:#F1FBF6}
.hw-tile canvas{width:88px;height:56px}.hw-tile b{font-size:.9rem}.hw-tile small{color:#F2B330;letter-spacing:1px;min-height:1.1em}
.hw-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.hw-chip{border:2px solid var(--line,#E3E7F0);background:#fff;border-radius:14px;padding:4px 10px;cursor:pointer;font:inherit;display:flex;flex-direction:column;align-items:center}
.hw-chip canvas{height:44px}.hw-chip.on{border-color:${B};background:#FFF4EA}.hw-chip small{color:#F2B330;min-height:1em;font-size:.75rem}
.hw-steps{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}.hw-step{flex:1;min-width:130px;border:2px solid var(--line,#E3E7F0);background:#fff;border-radius:14px;padding:8px 10px;cursor:pointer;font:inherit;text-align:left}
.hw-step b{display:block}.hw-step .ar{font-size:.85em}.hw-step.on{border-color:${B};background:#FFF4EA}.hw-step small{color:#22B573;font-weight:800}
.hw-pad{position:relative;margin-top:12px;border-radius:18px;background:#fff;border:2px solid var(--line,#E3E7F0);overflow:hidden}
.hw-pad canvas{display:block;width:100%;touch-action:none;cursor:crosshair}
.hw-ex{display:flex;align-items:center;gap:10px;padding:8px 12px;background:#FFF9F2;border-bottom:2px dashed #F4D9BF;flex-wrap:wrap}.hw-ex canvas{touch-action:auto;cursor:default;width:auto;max-width:100%}
.hw-res{margin-top:12px;border-radius:18px;padding:14px 16px;background:#fff;border:3px solid #22B573}.hw-res.low{border-color:#F2B330}
.hw-res .big{font:800 2.2rem var(--fh,inherit)}.hw-res .stars{font-size:1.6rem;color:#F2B330;letter-spacing:3px}
.hw-bars{display:grid;grid-template-columns:auto 1fr auto;gap:6px 10px;align-items:center;margin-top:8px;max-width:520px}
.hw-bars .bar{height:10px;border-radius:9px;background:#EEF1F7;overflow:hidden}.hw-bars .bar i{display:block;height:100%;border-radius:9px}
.hw-key{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:.9rem}.hw-key i{display:inline-block;width:14px;height:14px;border-radius:50%;vertical-align:-2px;margin-right:5px}
.hw-tips{margin:.5rem 0 0;padding-left:1.1rem}.hw-tips li{margin:.2rem 0}
`;

  /* ---------- lessons ---------- */
  let LES = null;
  function lessons() {
    if (LES) return LES; const d = D(); LES = [];
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach(U => { const l = U.toLowerCase(); LES.push({ id: 'L-' + U, kind: 'L', t: `Letter ${U}${l}`, show: U + l, items: [U, l, U + l, l + l + l] }); });
    d.joins.forEach((j, i) => LES.push({ id: 'J-' + String(i + 1).padStart(2, '0'), kind: 'J', t: 'Joined letters: ' + j.join(', '), show: j[0], items: j }));
    Object.keys(d.words).forEach(k => LES.push({ id: 'W-' + k, kind: 'W', t: `Words: “${k.toUpperCase()}”`, show: d.words[k][0], items: d.words[k] }));
    return LES;
  }
  const les = id => lessons().find(x => x.id === id);
  const prog = id => (Store.me().progress || {})['hw:' + id] || null;
  const best = (p, mode, i) => (p && p[mode] && p[mode][i]) || 0;
  const starsOf = s => s >= 80 ? 3 : s >= PASS ? 2 : s >= 40 ? 1 : 0;
  const starTxt = n => '★'.repeat(n) + '☆'.repeat(3 - n);
  function lessonStars(L) { const p = prog(L.id); if (!p) return 0; let s = 0; L.items.forEach((_, i) => { s += (best(p, 't', i) + best(p, 'w', i)) / 2; }); return starsOf(s / L.items.length); }
  const lessonDone = L => { const p = prog(L.id); return !!p && L.items.every((_, i) => best(p, 't', i) >= PASS && best(p, 'w', i) >= PASS); };

  /* ---------- geometry: text → smooth pen strokes in writing order ---------- */
  const geoCache = {};
  function chaikin(pts) { if (pts.length < 3) return pts; const o = [pts[0]]; for (let i = 0; i < pts.length - 1; i++) { const p = pts[i], q = pts[i + 1]; o.push([p[0] * .75 + q[0] * .25, p[1] * .75 + q[1] * .25], [p[0] * .25 + q[0] * .75, p[1] * .25 + q[1] * .75]); } o.push(pts[pts.length - 1]); return o; }
  function resample(pts, step) { const o = [pts[0]]; let need = step; for (let i = 1; i < pts.length; i++) { let a = pts[i - 1]; const b = pts[i]; let seg = Math.hypot(b[0] - a[0], b[1] - a[1]); while (seg >= need) { const t = need / seg; a = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; o.push(a); seg -= need; need = step; } need -= seg; } const l = pts[pts.length - 1], e = o[o.length - 1]; if (Math.hypot(l[0] - e[0], l[1] - e[1]) > step * .4) o.push(l); return o; }
  function geo(text) {
    if (geoCache[text]) return geoCache[text];
    const d = D(); let x = 0; const raw = [];
    const join = (list, gap) => { const o = []; list.forEach(p => { const last = o[o.length - 1]; if (last) { const e = last[last.length - 1]; if (Math.hypot(e[0] - p[0][0], e[1] - p[0][1]) <= gap) { last.push(...p); return; } } o.push(p.slice()); }); return o; };
    for (const ch of text) {
      const g = d.g[ch]; if (!g) { x += 300; continue; }
      let gs = g[1].map(s => { const p = []; for (let i = 0; i < s.length; i += 2) p.push([s[i] + x, s[i + 1]]); return p; });
      if (ch === 'i' || ch === 'j') gs.push(gs.shift());   // the body first, the dot last
      // inside one letter the pen stays down across a short retrace (u, n, m, y…)
      raw.push(...join(gs, 110)); x += g[0];
    }
    // a stroke that starts where the last one ended is the same pen movement (the join between two letters)
    const st = join(raw, 48);
    const strokes = st.map(p => resample(chaikin(chaikin(p)), 9));
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; strokes.forEach(s => s.forEach(p => { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); }));
    return (geoCache[text] = { strokes, x0, x1, y0, y1, n: strokes.reduce((a, s) => a + s.length, 0) });
  }
  /* place a text on a canvas of the given CSS size: returns scale, the model points in pixels and the four lines */
  function place(text, w, h, pad) {
    const d = D(), g = geo(text), H = d.asc - d.desc + 160, W = g.x1 - g.x0;
    const s = Math.min((w - 2 * pad) / W, h / H), ox = (w - W * s) / 2 - g.x0 * s, top = (h - H * s) / 2 + 80 * s;
    const X = x => ox + x * s, Y = y => top + (d.asc - y) * s;
    const strokes = g.strokes.map(st => st.map(p => [X(p[0]), Y(p[1])]));
    return { s, strokes, pts: strokes.flatMap((st, k) => st.map(p => [p[0], p[1], k])), lines: { asc: Y(d.asc), mid: Y(d.xh), base: Y(0), desc: Y(d.desc) }, box: { x0: X(g.x0), x1: X(g.x1), y0: Y(g.y1), y1: Y(g.y0) } };
  }
  function setup(cv, w, h) { const r = Math.min(window.devicePixelRatio || 1, 3); cv.width = Math.round(w * r); cv.height = Math.round(h * r); cv.style.height = h + 'px'; const c = cv.getContext('2d'); c.setTransform(r, 0, 0, r, 0, 0); c.lineCap = c.lineJoin = 'round'; return c; }
  function drawLines(c, L, w) {
    c.save(); c.lineWidth = 1.5;
    [[L.asc, '#C9D6EE', []], [L.mid, '#9DB7E8', [8, 7]], [L.base, '#E0566F', []], [L.desc, '#DDE4F1', [3, 6]]].forEach(([y, col, dash]) => { c.strokeStyle = col; c.setLineDash(dash); c.beginPath(); c.moveTo(8, y); c.lineTo(w - 8, y); c.stroke(); });
    c.restore();
  }
  function path(c, st, upto) { c.beginPath(); const n = upto == null ? st.length : Math.min(upto, st.length); for (let i = 0; i < n; i++) i ? c.lineTo(st[i][0], st[i][1]) : c.moveTo(st[i][0], st[i][1]); c.stroke(); }
  /* where to start (numbered green dots) and which way to go (arrows along the path) */
  function drawDirections(c, P) {
    const s = P.s, gap = Math.max(19, Math.round(46 / (9 * s))), a = Math.max(4, 30 * s);
    c.save(); c.strokeStyle = B; c.fillStyle = B; c.lineWidth = Math.max(1.5, 7 * s);
    P.strokes.forEach(st => { for (let i = Math.floor(gap * .6); i < st.length - 2; i += gap) { const p = st[i], q = st[Math.min(i + 2, st.length - 1)], ang = Math.atan2(q[1] - p[1], q[0] - p[0]); c.beginPath(); c.moveTo(p[0] - a * Math.cos(ang - .5), p[1] - a * Math.sin(ang - .5)); c.lineTo(p[0], p[1]); c.lineTo(p[0] - a * Math.cos(ang + .5), p[1] - a * Math.sin(ang + .5)); c.stroke(); } });
    const r = Math.max(7, 34 * s);
    P.strokes.forEach((st, k) => { const p = st[0]; c.beginPath(); c.fillStyle = '#22B573'; c.arc(p[0], p[1], r, 0, 7); c.fill(); c.fillStyle = '#fff'; c.font = `800 ${Math.round(r * 1.25)}px sans-serif`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(k + 1, p[0], p[1] + r * .08); });
    c.restore();
  }
  function drawModel(c, P, col, wd, dash) { c.save(); c.strokeStyle = col; c.lineWidth = wd; if (dash) c.setLineDash(dash); P.strokes.forEach(st => path(c, st)); c.restore(); }
  function drawThumb(cv, text, w, h, col) { const c = setup(cv, w, h); cv.style.width = w + 'px'; const P = place(text, w, h, 5); c.clearRect(0, 0, w, h); drawModel(c, P, col || '#2E3074', Math.max(1.6, 26 * P.s)); }

  /* ---------- measuring the writing ---------- */
  /* model: [[x,y,stroke]] in writing order; ink: [[[x,y],...],...]; tol in pixels.
     coverage = how much of the model was written; onPath = how much of the ink stays on the model;
     direction = how much of the ink moves the same way as the model. */
  function measure(model, ink, tol) {
    const pts = []; ink.forEach((st, k) => { const r = st.length > 1 ? resample(st, 3) : st; r.forEach(p => pts.push([p[0], p[1], k])); });
    const n = model.length, covered = new Uint8Array(n), on = new Uint8Array(pts.length), t2 = tol * tol;
    let fwd = 0, back = 0, prev = -1, prevStroke = -1, onCount = 0;
    pts.forEach((p, i) => {
      if (p[2] !== prevStroke) { prev = -1; prevStroke = p[2]; }
      let bestJ = -1, bestD = 1e18, nearJ = -1, nearGap = 1e9;
      for (let j = 0; j < n; j++) { const dx = model[j][0] - p[0], dy = model[j][1] - p[1], d = dx * dx + dy * dy; if (d <= t2) { covered[j] = 1; if (prev >= 0) { const g = Math.abs(j - prev - 1); if (g < nearGap) { nearGap = g; nearJ = j; } } } if (d < bestD) { bestD = d; bestJ = j; } }
      if (bestD <= t2) { on[i] = 1; onCount++; const j = prev >= 0 && nearJ >= 0 ? nearJ : bestJ; if (prev >= 0 && j !== prev) { if (j > prev) fwd++; else back++; } prev = j; }
    });
    let cov = 0; for (let j = 0; j < n; j++) cov += covered[j];
    return { coverage: n ? cov / n : 0, onPath: pts.length ? onCount / pts.length : 0, direction: fwd + back ? fwd / (fwd + back) : 0, covered, pts, on, empty: pts.length < 4 };
  }
  /* free writing has no model under the pen, so the ink is first moved and resized onto the model's box */
  function fitInk(ink, box) {
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; ink.forEach(st => st.forEach(p => { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); }));
    const uw = Math.max(x1 - x0, 1), uh = Math.max(y1 - y0, 1), mw = box.x1 - box.x0, mh = box.y1 - box.y0;
    const mk = k => ink.map(st => st.map(p => [box.x0 + mw / 2 + (p[0] - (x0 + x1) / 2) * k, box.y0 + mh / 2 + (p[1] - (y0 + y1) / 2) * k]));
    return { byH: mk(mh / uh), byW: mk(mw / uw), size: uh / mh, dy: ((y0 + y1) / 2 - (box.y0 + box.y1) / 2) };
  }
  /* order-aware comparison for free writing: both lines are cut into the same number of points and matched in order
     (dynamic time warping), so the right shape written the right way scores high and a scribble in the same place does not */
  function seqDist(model, ink) {
    const pick = (a, n) => Array.from({ length: n }, (_, i) => a[Math.round(i * (a.length - 1) / (n - 1))]);
    const flat = ink.flatMap(st => st.length > 1 ? resample(st, 3) : st); if (flat.length < 4) return 1e9;
    const N = 56, A = pick(model, N), U = pick(flat, N), W = 14, INF = 1e18, d = Array.from({ length: N + 1 }, () => new Float64Array(N + 1).fill(INF)); d[0][0] = 0;
    for (let i = 1; i <= N; i++) for (let j = Math.max(1, i - W); j <= Math.min(N, i + W); j++) { const c = Math.hypot(A[i - 1][0] - U[j - 1][0], A[i - 1][1] - U[j - 1][1]); d[i][j] = c + Math.min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]); }
    return d[N][N] / N;
  }
  function grade(P, ink, mode) {
    const xh = D().xh * P.s, tol = Math.max(mode === 't' ? 7 : 9, (mode === 't' ? 48 : 60) * P.s);
    let m, raw;
    if (mode === 't') { m = measure(P.pts, ink, tol); m.match = m.onPath; raw = Math.pow(m.coverage, 1.5) * (.3 + .7 * m.onPath) * (.7 + .3 * m.direction); }
    else {
      const fit = fitInk(ink, P.box), one = f => { const r = measure(P.pts, f, tol), fw = seqDist(P.pts, f) / xh, bw = seqDist(P.pts, f.map(st => st.slice().reverse()).reverse()) / xh; r.back = bw + .08 < fw; r.seq = Math.max(0, Math.min(1, 1 - (Math.min(fw, bw) - .12) / .55)); if (r.back) r.direction = Math.min(r.direction, .3); return r; };
      const a = one(fit.byH), b = one(fit.byW); m = a.coverage * (.3 + .7 * a.seq) >= b.coverage * (.3 + .7 * b.seq) ? a : b;
      m.sizeOk = fit.size > .6 && fit.size < 1.55; m.lineOk = Math.abs(fit.dy) < xh * .6; m.size = fit.size; m.match = m.seq;
      raw = Math.pow(m.coverage, 1.2) * (.2 + .8 * m.seq) * (.7 + .3 * m.direction) * (.7 + (m.sizeOk ? .15 : 0) + (m.lineOk ? .15 : 0));
    }
    // a human hand never lands exactly on the model, so the top of the scale is reached a little early
    m.score = m.empty ? 0 : Math.max(0, Math.min(100, Math.round(raw / .9 * 100)));
    m.tol = tol; return m;
  }
  function tips(m, mode) {
    const t = [];
    if (m.empty) return [['Write on the lines first, then press Check.', 'اكتب على السطور أولًا ثم اضغط «تحقّق».']];
    if (m.coverage < .8) t.push(mode === 't' ? ['Some parts are missing: they are shown in red. Trace the whole shape.', 'بعض الأجزاء ناقصة وهي باللون الأحمر. تتبّع الشكل كاملًا.'] : ['Some parts of the shape are missing or look different: they are shown in red.', 'بعض أجزاء الشكل ناقصة أو مختلفة وهي باللون الأحمر.']);
    if (m.match < .8) t.push(mode === 't' ? ['Your line left the path in the orange places. Go slowly and stay on the line.', 'خرج خطك عن المسار في الأماكن البرتقالية. اكتب ببطء والتزم بالخط.'] : ['The shape does not match the model closely yet. Look at the example again and copy each part in the same order.', 'الشكل لا يطابق النموذج جيدًا بعد. انظر إلى المثال مرة أخرى واكتب كل جزء بالترتيب نفسه.']);
    if (m.direction < .75) t.push(['Check the direction: start at the green dot number 1 and follow the arrows.', 'انتبه للاتجاه: ابدأ من النقطة الخضراء رقم 1 واتبع الأسهم.']);
    if (mode === 'w' && m.sizeOk === false) t.push(m.size < 1 ? ['Your writing is too small. Tall letters touch the top line; small letters reach the dashed line.', 'كتابتك صغيرة جدًا. الحروف الطويلة تلمس السطر العلوي والحروف القصيرة تصل إلى الخط المتقطع.'] : ['Your writing is too big. Keep small letters between the red line and the dashed line.', 'كتابتك كبيرة جدًا. اجعل الحروف القصيرة بين الخط الأحمر والخط المتقطع.']);
    if (mode === 'w' && m.lineOk === false) t.push(['Sit your letters on the red base line.', 'اجعل حروفك تجلس على السطر الأحمر.']);
    if (!t.length) t.push(['Beautiful cursive! Every part is in the right place.', 'خط متصل جميل! كل جزء في مكانه الصحيح.']);
    return t;
  }

  /* ---------- views ---------- */
  V.hw = m => {
    stop(); const L = lessons(), parts = [['Home', () => go('home')], ['Cursive Handwriting']];
    const sec = (k, h, ar, note) => { const ls = L.filter(x => x.kind === k); return `<h2 style="margin:22px 0 0">${h} <span class="ar" style="font-size:.8em">${ar}</span></h2><p class="muted" style="margin:.2rem 0 0">${note} · ${ls.filter(lessonDone).length}/${ls.length} done</p>
      <section class="hw-grid">${ls.map(x => { const st = lessonStars(x); return `<button class="hw-tile${lessonDone(x) ? ' done' : ''}" data-hl="${x.id}"><canvas data-th="${esc(x.show)}"></canvas><b>${esc(k === 'L' ? x.t.replace('Letter ', '') : k === 'J' ? x.items.join(' · ') : x.t.replace('Words: ', ''))}</b><small>${prog(x.id) ? starTxt(st) : ''}</small></button>`; }).join('')}</section>`; };
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${A};--b:${B}"><span class="d-ic">✍️</span><div><span class="k">Department · 26 letters · ${L.filter(x => x.kind === 'J').length} joined-letter pages · 104 words</span><h1>Cursive Handwriting <span class="ar" style="color:#fff;font-size:.8em">الخط المتصل</span></h1></div></section>
    ${typeof introCard === 'function' ? introCard('hw') : ''}
    ${sec('L', '🔤 Letters', 'الحروف', 'Capital and small letters, A to Z')}${sec('J', '🔗 Joined letters', 'الحروف الموصولة', 'How two or three letters join')}${sec('W', '📝 Words', 'الكلمات', 'Four words for every letter')}`;
    bindCrumbs(m, parts);
    $$('[data-th]', m).forEach(cv => drawThumb(cv, cv.dataset.th, 88, 56));
    $$('[data-hl]', m).forEach(b => b.onclick = () => go('hwp', { hk: b.dataset.hl }));
  };

  let raf = 0, onRes = null;
  function stop() { cancelAnimationFrame(raf); raf = 0; if (onRes) { window.removeEventListener('resize', onRes); onRes = null; } }

  V.hwp = m => {
    stop(); const L = les(S.hk); if (!L) return go('hw');
    const idx = Math.min(S.hi || 0, L.items.length - 1), text = L.items[idx], mode = S.hm || 'v', p = prog(L.id);
    const all = lessons(), li = all.indexOf(L), nextL = all[li + 1];
    const parts = [['Home', () => go('home')], ['Cursive Handwriting', () => go('hw')], [L.t]];
    const STEPS = [['v', '1 · Watch 👀', 'شاهد', 'See where to start and which way to go'], ['t', '2 · Trace ✏️', 'تتبّع', 'Write over the grey model'], ['w', '3 · Write 📝', 'اكتب', 'Write it alone on the lines']];
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${A};--b:${B}"><span class="d-ic">✍️</span><div><span class="k">Cursive Handwriting · ${L.kind === 'L' ? 'Letters' : L.kind === 'J' ? 'Joined letters' : 'Words'}</span><h1>${esc(L.t)}</h1></div></section>
    <div class="hw-chips">${L.items.map((t, i) => `<button class="hw-chip${i === idx ? ' on' : ''}" data-i="${i}"><canvas data-th="${esc(t)}"></canvas><small>${best(p, 't', i) || best(p, 'w', i) ? starTxt(starsOf((best(p, 't', i) + best(p, 'w', i)) / 2)) : ''}</small></button>`).join('')}</div>
    <div class="hw-steps">${STEPS.map(s => `<button class="hw-step${s[0] === mode ? ' on' : ''}" data-m="${s[0]}"><b>${s[1]} <span class="ar">${s[2]}</span></b><span class="muted">${s[3]}</span>${s[0] !== 'v' && best(p, s[0], idx) ? ` <small>best ${best(p, s[0], idx)}%</small>` : ''}</button>`).join('')}</div>
    <div class="hw-pad">${mode === 'w' ? `<div class="hw-ex"><b>Example <span class="ar">مثال</span></b><canvas id="hwEx"></canvas><button class="btn sm sec" id="hwExPlay">▶ Show me</button></div>` : ''}<canvas id="hwCv"></canvas></div>
    <div class="ctrls" style="justify-content:flex-start;margin-top:10px">
      ${mode === 'v' ? '<button class="btn sec" id="hwPlay">↻ Watch again</button><button class="btn" id="hwGoT">Now trace it →</button>' : `<button class="btn sec" id="hwClear">🧽 Clear</button><button class="btn sec" id="hwUndo">↶ Undo</button>${mode === 't' ? '<button class="btn sec" id="hwPlay">▶ Show me</button>' : ''}<button class="btn" id="hwCheck">✓ Check my writing</button>`}
    </div>
    <p class="muted" style="margin:.5rem 0 0">${mode === 'v' ? 'Start at the green dot number 1 and follow the orange arrows. <span class="ar">ابدأ من النقطة الخضراء رقم 1 واتبع الأسهم البرتقالية.</span>' : mode === 't' ? 'Use your finger, a pen or the mouse. Start at the green dot and follow the arrows. <span class="ar">استخدم إصبعك أو القلم أو الفأرة. ابدأ من النقطة الخضراء واتبع الأسهم.</span>' : 'Look at the example, then write it on the lines: sit on the red line, small letters reach the dashed line. <span class="ar">انظر إلى المثال ثم اكتبه على السطور.</span>'}</p>
    <div id="hwOut"></div>`;
    bindCrumbs(m, parts);
    $$('[data-th]', m).forEach(cv => { const w = Math.max(40, Math.min(150, Math.round((geo(cv.dataset.th).x1 - geo(cv.dataset.th).x0) / 1200 * 44 + 26))); drawThumb(cv, cv.dataset.th, w, 44); });
    $$('[data-i]', m).forEach(b => b.onclick = () => go('hwp', { hk: L.id, hi: +b.dataset.i, hm: 'v' }));
    $$('[data-m]', m).forEach(b => b.onclick = () => go('hwp', { hk: L.id, hi: idx, hm: b.dataset.m }));

    const cv = $('#hwCv', m), pad = cv.parentNode; let w, h, c, P, ink = [], cur = null, res = null, anim = null;
    const size = () => { w = pad.clientWidth; const g = geo(text), d = D(), H = d.asc - d.desc + 160; h = Math.round(Math.max(170, Math.min(330, (w - 36) / (g.x1 - g.x0) * H))); c = setup(cv, w, h); P = place(text, w, h, 18); };
    const inkW = () => Math.max(3.5, 30 * P.s);
    function draw() {
      c.clearRect(0, 0, w, h); drawLines(c, P.lines, w);
      if (mode === 'v') { drawModel(c, P, '#E6EAF3', Math.max(3, 30 * P.s)); }
      if (mode === 't' && !res) { drawModel(c, P, '#E8EEF9', Math.max(8, 2 * 48 * P.s)); drawModel(c, P, '#9AAACB', Math.max(1.5, 8 * P.s), [2, Math.max(6, 22 * P.s)]); drawDirections(c, P); }
      if (anim) { c.save(); c.strokeStyle = '#2E3074'; c.lineWidth = inkW(); let left = anim.n, pen = null; P.strokes.forEach(st => { if (left <= 0) return; path(c, st, left); pen = st[Math.min(left, st.length) - 1]; left -= st.length; }); c.restore(); drawDirections(c, P); if (pen && anim.n < P.pts.length) { c.beginPath(); c.fillStyle = '#E0445C'; c.arc(pen[0], pen[1], Math.max(6, 30 * P.s), 0, 7); c.fill(); } }
      if (res) {
        // the model, coloured by what the writing covered
        const r = Math.max(2.2, 15 * P.s); P.pts.forEach((q, j) => { c.beginPath(); c.fillStyle = res.covered[j] ? '#22B573' : '#E0445C'; c.arc(q[0], q[1], r, 0, 7); c.fill(); });
        if (mode === 't') { c.save(); c.lineWidth = Math.max(2, inkW() * .45); res.pts.forEach((q, i) => { if (!res.on[i]) { c.beginPath(); c.fillStyle = '#F2994A'; c.arc(q[0], q[1], Math.max(2, inkW() * .4), 0, 7); c.fill(); } }); c.restore(); }
      }
      if (!anim && !(res && mode === 't')) { c.save(); c.strokeStyle = res ? 'rgba(29,63,170,.38)' : '#1D3FAA'; c.lineWidth = inkW(); ink.forEach(st => { if (st.length === 1) { c.beginPath(); c.fillStyle = c.strokeStyle; c.arc(st[0][0], st[0][1], inkW() / 2, 0, 7); c.fill(); } else path(c, st); }); c.restore(); }
      else if (res && mode === 't') { c.save(); c.strokeStyle = 'rgba(29,63,170,.3)'; c.lineWidth = Math.max(2, inkW() * .5); ink.forEach(st => path(c, st)); c.restore(); }
    }
    function play(target, Pm, cm, wm, hm, done) {
      cancelAnimationFrame(raf); const total = Pm.pts.length; let n = 0, last = performance.now();
      const speed = Math.max(55, Math.min(150, total / 4.5));   // points a second: a letter takes about two seconds, a word about five
      const tick = now => { n = Math.min(total, n + (now - last) / 1000 * speed); last = now; target(Math.round(n)); if (n < total) raf = requestAnimationFrame(tick); else { raf = 0; if (done) setTimeout(done, 500); } };
      raf = requestAnimationFrame(tick);
    }
    const playMain = () => { res = null; $('#hwOut', m).innerHTML = ''; play(n => { anim = { n }; draw(); }, P, c, w, h, () => { if (mode !== 'v') { anim = null; draw(); } }); };
    size(); draw();
    if (mode === 'v') playMain();
    onRes = () => { if (S.view !== 'hwp' || !document.body.contains(cv)) return stop(); const ow = w; if (pad.clientWidth === ow) return; const k = pad.clientWidth / ow; size(); ink = []; res = null; anim = mode === 'v' ? { n: P.pts.length } : null; $('#hwOut', m).innerHTML = ''; draw(); exDraw(); void k; };
    window.addEventListener('resize', onRes);

    // the small example above the writing lines (Write step)
    const ex = $('#hwEx', m); let exP, exC, exW, exH;
    function exDraw(n) { if (!ex) return; exH = 92; const g = geo(text); exW = Math.round(Math.min(pad.clientWidth - 150, Math.max(90, (g.x1 - g.x0) / 1200 * exH + 40))); exC = setup(ex, exW, exH); ex.style.width = exW + 'px'; exP = place(text, exW, exH, 8); exC.clearRect(0, 0, exW, exH); drawLines(exC, exP.lines, exW);
      exC.strokeStyle = '#2E3074'; exC.lineWidth = Math.max(1.8, 28 * exP.s); let left = n == null ? 1e9 : n; exP.strokes.forEach(st => { if (left <= 0) return; path(exC, st, left); left -= st.length; }); drawDirections(exC, exP); }
    exDraw();
    const xp = $('#hwExPlay', m); if (xp) xp.onclick = () => play(n => exDraw(n), exP);
    const pl = $('#hwPlay', m); if (pl) pl.onclick = () => { ink = []; playMain(); };
    const gt = $('#hwGoT', m); if (gt) gt.onclick = () => go('hwp', { hk: L.id, hi: idx, hm: 't' });
    if (mode === 'v') return;

    const pos = e => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * (w / r.width), (e.clientY - r.top) * (h / r.height)]; };
    cv.onpointerdown = e => { if (anim) { cancelAnimationFrame(raf); anim = null; } if (res) { res = null; ink = []; $('#hwOut', m).innerHTML = ''; } e.preventDefault(); try { cv.setPointerCapture(e.pointerId); } catch (x) {} cur = [pos(e)]; ink.push(cur); draw(); };
    cv.onpointermove = e => { if (!cur) return; const q = pos(e), l = cur[cur.length - 1]; if (Math.hypot(q[0] - l[0], q[1] - l[1]) < 1.5) return; cur.push(q); c.save(); c.strokeStyle = '#1D3FAA'; c.lineWidth = inkW(); c.beginPath(); c.moveTo(l[0], l[1]); c.lineTo(q[0], q[1]); c.stroke(); c.restore(); };
    cv.onpointerup = cv.onpointercancel = cv.onpointerleave = () => { cur = null; };
    $('#hwClear', m).onclick = () => { cancelAnimationFrame(raf); anim = null; ink = []; res = null; $('#hwOut', m).innerHTML = ''; draw(); };
    $('#hwUndo', m).onclick = () => { if (res) return; ink.pop(); draw(); };
    $('#hwCheck', m).onclick = () => {
      cancelAnimationFrame(raf); anim = null; const g = grade(P, ink, mode), out = $('#hwOut', m), tp = tips(g, mode);
      if (g.empty) { out.innerHTML = `<div class="hw-res low"><b>${tp[0][0]}</b> <span class="ar">${tp[0][1]}</span></div>`; return; }
      res = g; draw();
      const me = Store.me(), k = 'hw:' + L.id, pr = (me.progress = me.progress || {})[k] || { t: {}, w: {} }; pr.t = pr.t || {}; pr.w = pr.w || {};
      const old = pr[mode][idx] || 0; pr[mode][idx] = Math.max(old, g.score);
      let sum = 0; L.items.forEach((_, i) => { sum += ((pr.t[i] || 0) + (pr.w[i] || 0)) / 2; }); pr.score = Math.round(sum / L.items.length); pr.total = 100; pr.best = pr.score; pr.done = L.items.every((_, i) => (pr.t[i] || 0) >= PASS && (pr.w[i] || 0) >= PASS); pr.at = Date.now();
      me.progress[k] = pr; Store.save();
      const st = starsOf(g.score), bar = (lab, ar, v, col) => `<span>${lab} <span class="ar">${ar}</span></span><span class="bar"><i style="width:${Math.round(v * 100)}%;background:${col}"></i></span><b>${Math.round(v * 100)}%</b>`;
      const nextBtn = mode === 't' ? ['w', idx, 'Now write it alone →'] : idx < L.items.length - 1 ? ['v', idx + 1, 'Next one →'] : null;
      out.innerHTML = `<div class="hw-res${g.score >= PASS ? '' : ' low'}"><span class="muted">${mode === 't' ? 'Tracing' : 'Writing'} score <span class="ar">${mode === 't' ? 'درجة التتبّع' : 'درجة الكتابة'}</span></span>
        <div><span class="big">${g.score}%</span> <span class="stars">${starTxt(st)}</span>${old && g.score > old ? ' <b style="color:#22B573">New best!</b>' : ''}</div>
        <div class="hw-bars">${bar('Shape completed', 'اكتمال الشكل', g.coverage, '#22B573')}${bar(mode === 't' ? 'Stayed on the line' : 'Matches the model', mode === 't' ? 'الالتزام بالخط' : 'مطابقة النموذج', g.match, '#2F9BF0')}${bar('Direction', 'الاتجاه', g.direction, '#9B6CF6')}</div>
        <div class="hw-key"><span><i style="background:#22B573"></i>written correctly</span><span><i style="background:#E0445C"></i>missed</span>${mode === 't' ? '<span><i style="background:#F2994A"></i>off the line</span>' : ''}</div>
        <ul class="hw-tips">${tp.map(t => `<li>${t[0]} <span class="ar">${t[1]}</span></li>`).join('')}</ul>
        <div class="ctrls" style="justify-content:flex-start;margin-top:8px"><button class="btn sec" id="hwRetry">↻ Try again</button>${g.score >= PASS && nextBtn ? `<button class="btn" id="hwNext">${nextBtn[2]}</button>` : ''}${g.score >= PASS && !nextBtn && nextL ? `<button class="btn" id="hwNextL">Next page: ${esc(nextL.t)} →</button>` : ''}${g.score >= PASS && !nextBtn ? '<button class="btn sec" id="hwHome">All pages</button>' : ''}</div></div>`;
      $('#hwRetry', out).onclick = () => $('#hwClear', m).click();
      const nb = $('#hwNext', out); if (nb) nb.onclick = () => go('hwp', { hk: L.id, hi: nextBtn[1], hm: nextBtn[0] });
      const nl = $('#hwNextL', out); if (nl) nl.onclick = () => go('hwp', { hk: nextL.id }); const hb = $('#hwHome', out); if (hb) hb.onclick = () => go('hw');
      out.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      try { if (g.score >= PASS) RX.praise(); else RX.encourage(); } catch (e) {}
    };
  };

  function homeMeta() { const L = lessons(), d = L.filter(lessonDone).length; return d ? `${d}/${L.length} pages done` : ''; }
  function register() {
    Object.assign(VIEWS, V);
    if (!document.getElementById('hwCss')) { const st = document.createElement('style'); st.id = 'hwCss'; st.textContent = CSS; document.head.appendChild(st); }
  }
  return { register, homeMeta, stop, _t: { geo, place, grade, lessons } };
})();
