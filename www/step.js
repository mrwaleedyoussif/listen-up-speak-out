/* STEP Preparation department: 30 STEP-style mock exams (Set A Foundation, Set B Intermediate, Set C Exam Standard).
   Each exam has the four STEP sections: Reading Comprehension (40), Sentence Structure (30), Listening Comprehension (20)
   and Composition Analysis (10). A section is taken on its own, with a timer, then reviewed with the key, the question
   type, an explanation and an Arabic hint. Data: step/index.js (the list) and step/mNN.js (one exam, loaded when opened).
   Original practice material by Waleed Youssef; these are not official STEP papers. */
const STEPX = (() => {
  'use strict';
  const SETS = { A: ['Set A', 'Foundation', 'تأسيسي', '#12B5CB', '#0A7C96'], B: ['Set B', 'Intermediate', 'متوسط', '#F59E0B', '#C2570C'], C: ['Set C', 'Exam Standard', 'مستوى الاختبار', '#E0566F', '#B0304B'] };
  const SECS = [['R', 'Reading Comprehension', 'فهم المقروء', 40, 70, '📖'], ['S', 'Sentence Structure', 'تركيب الجمل', 30, 35, '🧩'],
    ['L', 'Listening Comprehension', 'فهم المسموع', 20, 30, '🎧'], ['C', 'Composition Analysis', 'التحليل الإنشائي', 10, 20, '✍️']];
  const sec = id => SECS.find(x => x[0] === id);
  const key = (n, s) => `step:${String(n).padStart(2, '0')}:${s}`;
  const prog = (n, s) => (Store.me().progress || {})[key(n, s)] || null;
  const total = n => { let got = 0, done = 0; SECS.forEach(x => { const p = prog(n, x[0]); if (p && p.done) { got += p.best; done++; } }); return { got, done }; };
  const fmt = t => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
  const grade = pc => pc >= 85 ? ['Excellent', 'ممتاز'] : pc >= 70 ? ['Good', 'جيد'] : pc >= 50 ? ['Developing', 'في تطوّر'] : ['Foundation needed', 'يحتاج إلى تأسيس'];
  const data = n => (window.STEP_DATA || {})[n];
  const loads = {};
  const load = n => loads[n] || (loads[n] = new Promise((ok, no) => { if (data(n)) return ok(); const s = document.createElement('script'); s.src = `step/m${String(n).padStart(2, '0')}.js`; s.onload = () => data(n) ? ok() : no(); s.onerror = () => { delete loads[n]; s.remove(); no(); }; document.head.appendChild(s); }));
  function need(m, n, again) {
    const d = data(n); if (d) return d;
    m.innerHTML = '<div class="card" style="text-align:center;margin-top:16px"><div style="font-size:2.4rem">⏳</div><p>Loading the exam… <span class="ar">جارٍ تحميل الاختبار…</span></p></div>';
    const v = S.view;
    load(n).then(() => { if (S.view === v && S.sm === n) again(); }).catch(() => { m.innerHTML = '<div class="card" style="margin-top:16px"><h3>😕 The exam could not be loaded</h3><p>Check the internet connection the first time you open an exam, then try again. <span class="ar ar-block">تحقق من الاتصال بالإنترنت عند فتح الاختبار أول مرة، ثم حاول مرة أخرى.</span></p><button class="btn" id="stRe">Try again</button></div>'; $('#stRe', m).onclick = () => render(); });
    return null;
  }
  let timer = null; const stopTimer = () => { if (timer) { clearInterval(timer); timer = null; } };

  const CSS = `
.st-sets{display:grid;gap:18px;margin-top:16px}
.st-set{border-radius:22px;padding:18px 20px;background:var(--card,#fff);box-shadow:0 6px 22px rgba(30,40,80,.08);border-top:7px solid var(--a)}
.st-set h2{margin:0;display:flex;flex-wrap:wrap;align-items:baseline;gap:10px}.st-set h2 small{font-size:.9rem;font-weight:700;color:var(--muted,#667)}
.st-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:12px}
.st-m{position:relative;border:2px solid var(--line,#E3E7F0);background:#fff;border-radius:16px;padding:12px 10px;text-align:center;cursor:pointer;font:inherit;transition:transform .2s cubic-bezier(.2,1.2,.4,1),box-shadow .2s,border-color .2s}
.st-m:hover{transform:translateY(-3px);box-shadow:0 10px 22px rgba(30,40,80,.12);border-color:var(--a)}
.st-m b{display:block;font:800 1.5rem/1.1 var(--fh,inherit);color:var(--b)}.st-m small{display:block;color:var(--muted,#667);font-weight:700}
.st-m .sc{display:block;margin-top:6px;font-weight:800;font-size:.9rem;color:#0B8A5A}.st-m .bar{display:block;height:6px;border-radius:9px;background:#EDF0F6;margin-top:6px;overflow:hidden}.st-m .bar i{display:block;height:100%;background:linear-gradient(90deg,var(--a),var(--b))}
.st-secs{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:16px}
.st-sec{display:flex;gap:14px;align-items:center}.st-sec .ic{font-size:2.2rem}.st-sec h3{margin:0}.st-sec .tx{flex:1;min-width:0}.st-sec .muted{font-size:.9rem}
.st-bar{position:sticky;top:var(--stt,64px);z-index:15;display:flex;flex-wrap:wrap;align-items:center;gap:10px;background:var(--card,#fff);border-radius:16px;padding:9px 14px;margin-top:12px;box-shadow:0 6px 20px rgba(30,40,80,.12)}
.st-bar .tm{font:800 1.15rem var(--fh,inherit);padding:3px 12px;border-radius:999px;background:var(--cl,#E8E9F7);color:var(--cd,#1F2052);font-variant-numeric:tabular-nums}.st-bar .tm.over{background:#FDE7EA;color:#B0304B}
.st-pal{display:flex;flex-wrap:wrap;gap:5px;flex:1 1 320px}.st-pal button{width:30px;height:28px;border-radius:8px;border:2px solid var(--line,#E3E7F0);background:#fff;font:700 .78rem inherit;cursor:pointer;padding:0}
.st-pal button.a{background:var(--c,#2E3074);border-color:var(--c,#2E3074);color:#fff}.st-pal button.cur{outline:3px solid #F2B330;outline-offset:1px}.st-pal button.ok{background:#1FB877;border-color:#1FB877;color:#fff}.st-pal button.no{background:#E0566F;border-color:#E0566F;color:#fff}
.st-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin-top:14px;align-items:start}
.st-pass{position:sticky;top:calc(var(--stt,64px) + 70px);max-height:calc(100vh - 170px);overflow:auto}.st-pass p{margin:.55rem 0;line-height:1.7}.st-pass p b{color:var(--c,#2E3074)}
.st-q{margin-top:12px}.st-q .stem{font-weight:800;line-height:1.55}.st-q .stem .num{display:inline-block;min-width:2.1em;color:var(--c,#2E3074)}
.st-q .ctx{background:#F6F7FB;border-left:5px solid var(--c,#2E3074);border-radius:10px;padding:10px 14px;margin:.5rem 0;line-height:1.7}
.st-q u{text-decoration-thickness:2px;text-underline-offset:4px}.st-q sub{font-weight:800;color:var(--coral,#E0566F);margin-left:1px}
.st-opts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:.55rem}.st-opts.long{grid-template-columns:1fr}
.st-opts .opt{cursor:pointer;font:inherit;width:100%}.st-opts .opt b{color:var(--c,#2E3074)}.st-opts .opt.on{border-color:var(--c,#2E3074);background:var(--cl,#E8E9F7)}
.st-opts .opt.ok{border-color:#1FB877;background:#E6F8EF}.st-opts .opt.no{border-color:#E0566F;background:#FDECEF}.st-opts .opt[disabled]{cursor:default;opacity:1}
.st-why{margin-top:.5rem;background:#F1F8FF;border-radius:12px;padding:9px 13px;line-height:1.6}.st-why .ty{display:inline-block;background:#DCEBFF;color:#1D4F91;border-radius:999px;padding:1px 10px;font-weight:800;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;margin-right:6px}
.st-aud{display:flex;flex-wrap:wrap;align-items:center;gap:12px}.st-aud audio{flex:1 1 280px;min-width:220px}.st-aud .ic{font-size:2rem}
.st-scr{margin-top:.6rem}.st-scr summary{cursor:pointer;font-weight:800}.st-scr p{margin:.3rem 0;line-height:1.6}
.st-res{text-align:center}.st-res .big{font:800 3.2rem/1 var(--fh,inherit);color:var(--c,#2E3074)}.st-types{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:8px;margin-top:12px;text-align:left}
.st-types div{background:#F6F7FB;border-radius:12px;padding:8px 12px;font-weight:700}.st-types div span{float:right;font-weight:800}.st-types .low{background:#FDECEF}
.st-books{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:12px}
.st-book{display:flex;flex-direction:column;align-items:flex-start;gap:2px;text-align:left;border:0;border-radius:22px;padding:18px;color:#fff;background:linear-gradient(135deg,var(--a),var(--b));cursor:pointer;font:inherit;box-shadow:0 10px 24px rgba(30,40,80,.16);transition:transform .25s cubic-bezier(.2,1.2,.4,1)}
.st-book:hover{transform:translateY(-4px)}.st-book .ic{font-size:2.2rem}.st-book b{font:800 1.45rem var(--fh,inherit)}.st-book .ar{color:#fff;font-weight:700}.st-book small{opacity:.95;font-weight:700}
.st-book .bar{display:block;width:100%;height:7px;border-radius:9px;background:rgba(255,255,255,.3);margin-top:8px;overflow:hidden}.st-book .bar i{display:block;height:100%;background:#fff}
.st-unit{margin-top:16px}.st-unit h2{margin:0 0 6px;display:flex;flex-wrap:wrap;gap:10px;align-items:baseline}.st-unit .lv{background:var(--a);color:#fff;border-radius:999px;padding:2px 12px;font-size:.9rem}
.st-page{line-height:1.7}.st-page h3{margin:1.2rem 0 .3rem;color:var(--b);border-bottom:3px solid var(--a);display:inline-block;padding-bottom:1px}.st-page h4{margin:1rem 0 .2rem}
.st-page p{margin:.4rem 0}.st-page blockquote{margin:.5rem 0;padding:8px 14px;border-left:5px solid var(--a);background:#F6F7FB;border-radius:10px}.st-page blockquote p{margin:.2rem 0}
.st-page .ar{direction:rtl;text-align:right;font-family:var(--fa,inherit);font-size:1.05em}.st-page table{border-collapse:collapse}.st-page td,.st-page th{border:1px solid var(--line,#E3E7F0);padding:4px 8px}
.st-lead p{margin:.35rem 0;line-height:1.7}.st-lead .hd{font-weight:800;color:var(--c,#2E3074)}
@media (max-width:900px){.st-books{grid-template-columns:repeat(2,1fr)}}
@media (max-width:900px){.st-split{grid-template-columns:1fr}.st-pass{position:static;max-height:42vh}.st-grid{grid-template-columns:repeat(3,1fr)}.st-secs{grid-template-columns:1fr}}
@media (max-width:520px){.st-opts{grid-template-columns:1fr}.st-grid{grid-template-columns:repeat(2,1fr)}.st-pal button{width:27px;height:26px}}
@media print{.st-bar{display:none}.st-pass{position:static;max-height:none}}`;

  const V = {};
  /* ---------- department home: the three sets ---------- */
  V.step = m => {
    stopTimer(); const IX = window.STEP_INDEX || [], parts = [['Home', () => go('home')], ['STEP Preparation']];
    const doneAll = IX.filter(x => total(x.n).done === 4).length;
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:#12B5CB;--b:#0A7C96"><span class="d-ic">🎓</span><div><span class="k">Department · 4 Foundation booklets · 30 mock exams</span><h1>STEP Preparation <span class="ar" style="color:#fff;font-size:.8em">التحضير لاختبار STEP</span></h1></div></section>
    ${introCard('step')}
    <h2 style="margin:18px 0 0">📚 Foundation booklets <span class="ar" style="font-size:.8em">كتيبات التأسيس</span></h2>
    <p class="muted" style="margin:.2rem 0 0">Learn each skill from A1 to B2+: read the lesson, then take its 30-question quiz. <span class="ar">تعلّم كل مهارة من A1 إلى B2+: اقرأ الدرس ثم أدِّ اختباره.</span></p>
    <section class="st-books">${(window.STEP_BOOKS || []).map(b => { const t = bookDone(b); return `<button class="st-book" data-sb="${b.id}" style="--a:${b.a};--b:${b.b}"><span class="ic">${b.ic}</span><b>${b.name}</b><span class="ar">${b.ar}</span><small>${t.all} lessons · STEP: ${esc(b.link)}</small><span class="bar"><i style="width:${Math.round(100 * t.done / t.all)}%"></i></span><small>${t.done}/${t.all} quizzes done</small></button>`; }).join('')}</section>
    <h2 style="margin:22px 0 0">📝 Mock exams <span class="ar" style="font-size:.8em">الاختبارات التجريبية</span></h2>
    <div class="st-sets">${Object.keys(SETS).map(k => { const T = SETS[k], list = IX.filter(x => x.set === k);
      return `<section class="st-set" style="--a:${T[3]};--b:${T[4]}"><h2>${T[0]} · ${T[1]} <span class="ar">${T[2]}</span><small>${esc(list[0] ? list[0].band : '')}</small></h2>
        <div class="st-grid">${list.map(x => { const t = total(x.n); return `<button class="st-m" data-sm="${x.n}" style="--a:${T[3]};--b:${T[4]}"><small>Mock</small><b>${x.n}</b>${t.done ? `<span class="sc">${t.done === 4 ? t.got + '/100' : t.done + '/4 sections'}</span>` : '<small>100 questions</small>'}<span class="bar"><i style="width:${t.done * 25}%"></i></span></button>`; }).join('')}</div></section>`; }).join('')}</div>
    <p class="muted" style="margin-top:14px">${doneAll} of ${IX.length} exams finished. These are practice exams written for this programme; they are not official STEP papers, and the score guide is not an official STEP conversion. <span class="ar ar-block">اختبارات تدريبية خاصة بالبرنامج وليست اختبارات STEP رسمية، ودليل الدرجات استرشادي.</span></p>`;
    bindCrumbs(m, parts); $$('[data-sm]', m).forEach(b => b.onclick = () => go('stepmock', { sm: +b.dataset.sm }));
    $$('[data-sb]', m).forEach(b => b.onclick = () => go('stepbook', { sb: b.dataset.sb }));
  };

  /* ---------- one exam: its four sections ---------- */
  V.stepmock = m => {
    stopTimer(); const n = S.sm, d = need(m, n, () => V.stepmock(m)); if (!d) return;
    const T = SETS[d.set], t = total(n), parts = [['Home', () => go('home')], ['STEP Preparation', () => go('step')], [`Mock ${n}`]];
    const g = t.done === 4 ? grade(t.got) : null;
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${T[3]};--b:${T[4]}"><span class="d-ic">📝</span><div><span class="k">${T[0]} · ${T[1]} · ${esc(d.band)}</span><h1>Mock ${n} <span style="font-size:.6em;opacity:.92">· 100 questions</span></h1>
      <p style="margin:.3rem 0 0;opacity:.95">Take the four sections in order, like the real test. Each section has a timer and is marked when you finish it.</p><span class="ar ar-block">أدِّ الأقسام الأربعة بالترتيب كما في الاختبار الحقيقي. لكل قسم مؤقّت، ويُصحَّح عند الانتهاء منه.</span></div></section>
    ${t.done ? `<section class="card st-res" style="margin-top:16px"><span class="muted">${t.done === 4 ? 'Your score' : `Score so far (${t.done} of 4 sections)`}</span><div class="big">${t.got}<span style="font-size:.45em;color:var(--muted,#667)"> / ${t.done === 4 ? 100 : SECS.filter(x => prog(n, x[0]) && prog(n, x[0]).done).reduce((a, x) => a + x[3], 0)}</span></div>${g ? `<b>${g[0]}</b> <span class="ar">${g[1]}</span>` : ''}</section>` : ''}
    <section class="st-secs">${SECS.map((x, i) => { const p = prog(n, x[0]); return `<div class="card st-sec"><span class="ic">${x[5]}</span><div class="tx"><span class="pill">Section ${i + 1}</span><h3>${x[1]} <span class="ar" style="font-size:.8em">${x[2]}</span></h3>
      <span class="muted">${x[3]} questions · ${x[4]} minutes${p && p.done ? ` · best <b>${p.best}/${x[3]}</b>${p.tries > 1 ? ` · ${p.tries} tries` : ''}` : ''}</span></div>
      <button class="btn${p && p.done ? ' sec' : ''}" data-ss="${x[0]}">${p && p.done ? '↻ Again' : 'Start →'}</button></div>`; }).join('')}</section>
    <section class="card" style="margin-top:16px"><h3 style="margin-top:0">Score guide <span class="ar" style="font-size:.85em">دليل الدرجات</span></h3>
      <p style="margin:.2rem 0"><b>85–100</b> Excellent · <b>70–84</b> Good · <b>50–69</b> Developing · <b>0–49</b> Foundation needed.</p><p class="muted" style="margin:.2rem 0">A guide for this series only, not an official STEP conversion. <span class="ar">دليل استرشادي خاص بالسلسلة وليس تحويلًا رسميًا لدرجات STEP.</span></p></section>`;
    bindCrumbs(m, parts); $$('[data-ss]', m).forEach(b => b.onclick = () => go('stepsec', { sm: n, ss: b.dataset.ss }));
  };

  /* ---------- one section: questions, timer, marking, review ---------- */
  const errStem = q => { let s = esc(q.s); q.o.forEach((o, i) => { const L = 'ABCD'[i], a = `(${L}) ${esc(o)}`; if (s.includes(a)) s = s.replace(a, `<u>${esc(o)}</u><sub>${L}</sub>`); }); return s; };
  function qHTML(q, A, done, err) {
    const a = A[q.n], long = q.o.some(o => o.length > 34);
    return `<div class="card st-q" id="sq${q.n}"><div class="stem"><span class="num">${q.n}.</span> ${err ? errStem(q) : esc(q.s)}</div>
      ${q.x ? `<div class="ctx">${q.x.map(esc).join('<br>')}</div>` : ''}
      <div class="st-opts${long ? ' long' : ''}">${q.o.map((o, i) => `<button class="opt${a === i && !done ? ' on' : ''}${done && i === q.k ? ' ok' : ''}${done && a === i && i !== q.k ? ' no' : ''}" data-q="${q.n}" data-i="${i}"${done ? ' disabled' : ''}><b>${'ABCD'[i]}.</b> <span>${esc(o)}</span>${done && i === q.k ? ' ✓' : ''}${done && a === i && i !== q.k ? ' ✗' : ''}</button>`).join('')}</div>
      ${done ? `<div class="st-why">${q.ty ? `<span class="ty">${esc(q.ty)}</span>` : ''}${a == null ? '<b>Not answered.</b> ' : ''}Answer <b>${'ABCD'[q.k]}</b>. ${esc(q.e)}${q.h ? `<span class="ar ar-block">تلميح: ${esc(q.h)}</span>` : ''}</div>` : ''}</div>`;
  }
  V.stepsec = m => {
    const n = S.sm, d = need(m, n, () => V.stepsec(m)); if (!d) return;
    const X = sec(S.ss), sc = d.sec.find(x => x.id === S.ss), T = SETS[d.set];
    if (!X || !sc) return go('stepmock', { sm: n });
    const A = S.sa = S.sa || {}, done = !!S.sres, G = sc.g, qs = G.flatMap(g => g.q);
    // pages: one passage or one recording per page; other sections 10 (structure) or 5 (composition) questions per page
    const pages = sc.id === 'R' || sc.id === 'L' ? G.map(g => ({ g, q: g.q })) : G.flatMap(g => { const sz = sc.id === 'S' ? 10 : 5, r = []; for (let i = 0; i < g.q.length; i += sz) r.push({ g, q: g.q.slice(i, i + sz) }); return r; });
    const pi = Math.min(S.sp || 0, pages.length - 1), P = pages[pi];
    if (!S.st0) S.st0 = Date.now();
    const parts = [['Home', () => go('home')], ['STEP Preparation', () => go('step')], [`Mock ${n}`, () => go('stepmock', { sm: n })], [X[1]]];
    const res = S.sres;
    let top = '';
    if (done) {
      const pc = Math.round(100 * res.got / qs.length), ty = {}; qs.forEach(q => { const t = ty[q.ty] = ty[q.ty] || [0, 0]; t[1]++; if (A[q.n] === q.k) t[0]++; });
      top = `<section class="card st-res" style="margin-top:14px"><span class="muted">${X[1]} · Mock ${n}</span><div class="big">${res.got}<span style="font-size:.45em;color:var(--muted,#667)"> / ${qs.length}</span></div>
        <b>${pc}%</b> · time ${fmt(res.secs)} of ${X[4]}:00${res.best > res.got ? ` · your best is ${res.best}` : ''}
        <div class="st-types">${Object.keys(ty).sort((a, b) => ty[a][0] / ty[a][1] - ty[b][0] / ty[b][1]).map(k => `<div class="${ty[k][0] / ty[k][1] < .5 ? 'low' : ''}">${esc(k)}<span>${ty[k][0]}/${ty[k][1]}</span></div>`).join('')}</div>
        <p class="muted" style="margin:.7rem 0 0">Question types you missed most are listed first. Review every answer below. <span class="ar">راجع كل إجابة في الأسفل.</span></p>
        <div class="ctrls" style="justify-content:center;margin-top:10px"><button class="btn" id="stBack">← Back to Mock ${n}</button><button class="btn sec" id="stAgain">↻ Try this section again</button></div></section>`;
    }
    const pal = `<div class="st-pal">${qs.map(q => `<button data-go="${q.n}" class="${done ? (A[q.n] === q.k ? 'ok' : 'no') : (A[q.n] != null ? 'a' : '')}${P.q.includes(q) ? ' cur' : ''}" title="Question ${q.n}">${q.n}</button>`).join('')}</div>`;
    const g = P.g;
    const lead = sc.id === 'L' ? `<div class="card st-aud" style="margin-top:14px"><span class="ic">🎧</span><div><b>Recording ${g.rec}</b>${done ? ` · ${esc(g.t)}` : ''}<br><span class="muted">${done ? 'Listen again while you read the script.' : 'Read the questions first. In the real test each recording is played once.'}</span></div>
        <audio controls preload="none" src="audio/step/${g.a}.mp3"></audio>${done ? `<details class="st-scr" style="flex:1 1 100%"><summary>📜 Script <span class="ar">نص التسجيل</span></summary>${g.sc.map(l => `<p>${esc(l)}</p>`).join('')}</details>` : ''}</div>` : '';
    const qsHTML = `${g.i && sc.id === 'S' && P.q[0] === g.q[0] ? `<p class="note" style="margin-top:14px"><b>${esc(g.i)}</b></p>` : ''}${P.q.map(q => qHTML(q, A, done, !!g.err)).join('')}`;
    const body = sc.id === 'R' ? `<div class="st-split"><aside class="card st-pass"><span class="pill">Passage ${pi + 1} of ${pages.length}</span><h3 style="margin:.4rem 0 0">${esc(g.t)}</h3>${g.p.map((p, i) => `<p><b>[${i + 1}]</b> ${esc(p)}</p>`).join('')}</aside><div>${qsHTML}</div></div>` : lead + qsHTML;
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${T[3]};--b:${T[4]}"><span class="d-ic">${X[5]}</span><div><span class="k">Mock ${n} · ${T[0]} ${T[1]} · Questions ${sc.from}–${sc.to}</span><h1>${X[1]} <span class="ar" style="color:#fff;font-size:.8em">${X[2]}</span></h1>
      ${sc.i && !done ? `<p style="margin:.3rem 0 0;opacity:.95">${esc(sc.i)}</p>` : ''}${sc.iar && !done ? `<span class="ar ar-block">${esc(sc.iar)}</span>` : ''}</div></section>
    ${top}
    <div class="st-bar">${done ? '<b>Review</b>' : `<span class="tm" id="stTm">0:00</span><span class="muted" id="stAns"></span>`}${pal}${done ? '' : '<button class="btn sm" id="stFin">Finish ✓</button>'}</div>
    ${body}
    <div class="navrow" style="margin-top:16px"><button class="btn sec" id="stPrev"${pi ? '' : ' disabled'}>← Previous</button><span class="muted">Page ${pi + 1} of ${pages.length}</span>${pi < pages.length - 1 ? '<button class="btn" id="stNext">Next →</button>' : done ? `<button class="btn" id="stBack2">← Back to Mock ${n}</button>` : '<button class="btn" id="stFin2">Finish the section ✓</button>'}</div>
    <div id="stAsk"></div>`;
    bindCrumbs(m, parts);
    const page = i => { AU.stop(); $$('audio', m).forEach(a => a.pause()); S.sp = i; V.stepsec(m); window.scrollTo({ top: 0 }); };
    const count = () => { const e = $('#stAns', m); if (e) e.textContent = `${qs.filter(q => A[q.n] != null).length}/${qs.length} answered`; };
    $$('[data-go]', m).forEach(b => b.onclick = () => { const qn = +b.dataset.go, i = pages.findIndex(p => p.q.some(q => q.n === qn)); if (i !== pi) page(i); const e = document.getElementById('sq' + qn); if (e) e.scrollIntoView({ block: 'center', behavior: 'smooth' }); });
    $('#stPrev', m).onclick = () => page(pi - 1); const nx = $('#stNext', m); if (nx) nx.onclick = () => page(pi + 1);
    ['#stBack', '#stBack2'].forEach(id => { const b = $(id, m); if (b) b.onclick = () => go('stepmock', { sm: n }); });
    const ag = $('#stAgain', m); if (ag) ag.onclick = () => go('stepsec', { sm: n, ss: S.ss });
    if (done) { stopTimer(); return; }
    count();
    $$('.opt[data-q]', m).forEach(b => b.onclick = () => { const qn = +b.dataset.q; A[qn] = +b.dataset.i; $$(`.opt[data-q="${qn}"]`, m).forEach(x => x.classList.toggle('on', x === b)); const pb = $(`[data-go="${qn}"]`, m); if (pb) pb.classList.add('a'); count(); });
    const tick = () => { const e = document.getElementById('stTm'); if (!e || S.view !== 'stepsec') return stopTimer(); const t = (Date.now() - S.st0) / 1000, left = X[4] * 60 - t; e.textContent = left >= 0 ? fmt(left) : '+' + fmt(-left); e.classList.toggle('over', left < 0); e.title = left >= 0 ? 'Time left' : 'Over the suggested time'; };
    stopTimer(); tick(); timer = setInterval(tick, 1000);
    const finish = () => {
      const left = qs.filter(q => A[q.n] == null).length, box = $('#stAsk', m);
      const mark = () => {
        stopTimer(); AU.stop(); const got = qs.filter(q => A[q.n] === q.k).length, secs = Math.round((Date.now() - S.st0) / 1000);
        const me = Store.me(), id = key(n, sc.id), old = (me.progress = me.progress || {})[id] || {};
        me.progress[id] = { done: true, score: got, total: qs.length, best: Math.max(got, old.best || 0), tries: (old.tries || 0) + 1, secs, at: Date.now() }; Store.save();
        S.sres = { got, secs, best: me.progress[id].best }; S.sp = 0; V.stepsec(m); window.scrollTo({ top: 0 });
        const r = got / qs.length; try { if (r >= .7) RX.praise(); else RX.encourage(); } catch (e) {}
      };
      if (!left) return mark();
      box.innerHTML = `<div class="card" style="margin-top:14px;border:3px solid #F2B330"><b>${left} question${left > 1 ? 's are' : ' is'} not answered.</b> There is no penalty for a wrong answer, so answer every question. <span class="ar ar-block">لا تُخصم درجات على الإجابة الخاطئة، فأجب عن كل الأسئلة.</span>
        <div class="ctrls" style="justify-content:flex-start;margin-top:8px"><button class="btn sec" id="stGo">Go to the first one</button><button class="btn" id="stMark">Finish anyway</button></div></div>`;
      box.scrollIntoView({ block: 'center', behavior: 'smooth' });
      $('#stGo', box).onclick = () => { const q = qs.find(q => A[q.n] == null); $(`[data-go="${q.n}"]`, m).click(); }; $('#stMark', box).onclick = mark;
    };
    ['#stFin', '#stFin2'].forEach(id => { const b = $(id, m); if (b) b.onclick = finish; });
  };

  /* ================= the four Foundation booklets: lessons with quizzes ================= */
  const bkey = (b, id) => `stepb:${b}:${id}`;
  const bprog = (b, id) => (Store.me().progress || {})[bkey(b, id)] || null;
  const book = id => (window.STEP_BOOKS || []).find(x => x.id === id);
  const bookDone = b => { let all = 0, done = 0; b.units.forEach(u => u.lessons.forEach(l => { all++; if (bprog(b.id, l[0])) done++; })); return { all, done }; };
  const udata = (b, u) => (window.STEP_BOOK || {})[b + u];
  const uloads = {};
  const uload = (b, u) => uloads[b + u] || (uloads[b + u] = new Promise((ok, no) => { if (udata(b, u)) return ok(); const s = document.createElement('script'); s.src = `step/bk/${b}${u}.js`; s.onload = () => udata(b, u) ? ok() : no(); s.onerror = () => { delete uloads[b + u]; s.remove(); no(); }; document.head.appendChild(s); }));
  function uneed(m, b, u, again) {
    const d = udata(b, u); if (d) return d;
    m.innerHTML = '<div class="card" style="text-align:center;margin-top:16px"><div style="font-size:2.4rem">⏳</div><p>Loading the unit… <span class="ar">جارٍ تحميل الوحدة…</span></p></div>';
    const v = S.view;
    uload(b, u).then(() => { if (S.view === v && S.sb === b && S.su === u) again(); }).catch(() => { m.innerHTML = '<div class="card" style="margin-top:16px"><h3>😕 The unit could not be loaded</h3><p>Check the internet connection the first time you open a unit, then try again. <span class="ar ar-block">تحقق من الاتصال بالإنترنت ثم حاول مرة أخرى.</span></p><button class="btn" id="stRe">Try again</button></div>'; $('#stRe', m).onclick = () => render(); });
    return null;
  }
  /* listening without recorded files: the device's English voice reads the script, one voice pitch per speaker */
  function say(lines, btn) {
    AU.stop(); if (!window.speechSynthesis) return false;
    const who = [], parts = lines.filter(l => !/^Situation:/.test(l)).map(l => { const m = l.match(/^([A-Z][^:]{0,32}):\s+(.*)$/); if (!m) return [null, l]; if (!who.includes(m[1])) who.push(m[1]); return [m[1], m[2]]; });
    const vs = speechSynthesis.getVoices().filter(v => /^en/i.test(v.lang)), tok = AU.token;
    parts.forEach(([sp, t], i) => { const u = new SpeechSynthesisUtterance(t); u.lang = 'en-US'; u.rate = .92; const k = sp ? who.indexOf(sp) : 0; u.pitch = [1, 1.3, .75, 1.15][k % 4]; if (vs.length > 1 && k % 2) u.voice = vs[1];
      if (i === parts.length - 1) u.onend = u.onerror = () => { if (btn) { btn.classList.remove('playing'); btn.textContent = '▶ Listen'; } };
      if (AU.token === tok) speechSynthesis.speak(u); });
    if (btn) btn.classList.add('playing'); return true;
  }
  V.stepbook = m => {
    stopTimer(); const b = book(S.sb); if (!b) return go('step');
    const parts = [['Home', () => go('home')], ['STEP Preparation', () => go('step')], [b.name]], t = bookDone(b);
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${b.a};--b:${b.b}"><span class="d-ic">${b.ic}</span><div><span class="k">Foundation booklet · A1 → B2+ · STEP section: ${esc(b.link)}</span><h1>${b.name} <span class="ar" style="color:#fff;font-size:.8em">${b.ar}</span></h1>
      <p style="margin:.3rem 0 0;opacity:.95">${t.all} lessons in 5 units. Read each lesson, take its quiz, then do the unit review. ${t.done} of ${t.all} quizzes done.</p><span class="ar ar-block">اقرأ كل درس ثم أدِّ اختباره، وبعد دروس الوحدة أدِّ مراجعة الوحدة.</span></div></section>
    ${b.units.map(u => `<section class="card st-unit" style="--a:${b.a};--b:${b.b}"><h2><span class="lv">${esc(u.level)}</span>Unit ${u.n}: ${esc(u.t)}</h2>
      ${u.lessons.map(l => { const p = bprog(b.id, l[0]); return `<button class="lrow${p ? ' done' : ''}" data-u="${u.n}" data-l="${l[0]}"><span class="ic">${p ? '✅' : b.ic}</span><span class="tx"><small>Lesson ${l[0]} · ${l[2]} questions</small><b>${esc(l[1])}</b></span><span class="st">${p ? `${p.best}/${p.total}` : '→'}</span></button>`; }).join('')}
      ${u.review ? (() => { const p = bprog(b.id, 'rev' + u.n); return `<button class="lrow${p ? ' done' : ''}" data-u="${u.n}" data-l="rev"><span class="ic">${p ? '🏅' : '🏁'}</span><span class="tx"><small>Unit review · ${u.review} questions</small><b>Unit ${u.n} Review</b></span><span class="st">${p ? `${p.best}/${p.total}` : '→'}</span></button>`; })() : ''}</section>`).join('')}`;
    bindCrumbs(m, parts);
    $$('[data-l]', m).forEach(x => x.onclick = () => x.dataset.l === 'rev' ? go('stepquiz', { sb: b.id, su: +x.dataset.u, sl: 'rev' }) : go('steplesson', { sb: b.id, su: +x.dataset.u, sl: x.dataset.l }));
  };
  V.steplesson = m => {
    stopTimer(); const b = book(S.sb); if (!b) return go('step');
    const d = uneed(m, b.id, S.su, () => V.steplesson(m)); if (!d) return;
    const les = d.lessons.find(x => x.id === S.sl); if (!les) return go('stepbook', { sb: b.id });
    const parts = [['Home', () => go('home')], ['STEP Preparation', () => go('step')], [b.name, () => go('stepbook', { sb: b.id })], [`Lesson ${les.id}`]], p = bprog(b.id, les.id);
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${b.a};--b:${b.b}"><span class="d-ic">${b.ic}</span><div><span class="k">${b.name} · Unit ${d.n} · ${esc(d.level)} · Lesson ${les.id}</span><h1>${esc(les.t)}</h1></div></section>
    <section class="card st-page" style="margin-top:16px;--a:${b.a};--b:${b.b}">${les.html}
      ${les.wu ? `<details style="margin-top:1rem"><summary><b>Answers to the warm-up and worked examples</b> <span class="ar">إجابات التمهيد والأمثلة</span></summary><p>${esc(les.wu)}</p></details>` : ''}</section>
    <section class="card" style="margin-top:16px;text-align:center"><h3 style="margin-top:0">Lesson ${les.id} Quiz · ${les.n} questions</h3>${p ? `<p>Your best score: <b>${p.best}/${p.total}</b></p>` : '<p class="muted">Do the quiz without looking back at the lesson, then check your answers.</p>'}
      <button class="btn" id="stQz">${p ? '↻ Take the quiz again' : 'Start the quiz →'}</button></section>`;
    bindCrumbs(m, parts);
    $('#stQz', m).onclick = () => go('stepquiz', { sb: b.id, su: d.n, sl: les.id });
    $$('.st-say', m).forEach(x => x.onclick = () => { if (x.classList.contains('playing')) { AU.stop(); x.classList.remove('playing'); } else if (!say(d.sc[x.dataset.tr] || [], x)) x.textContent = 'No voice on this device'; });
  };
  V.stepquiz = m => {
    stopTimer(); const b = book(S.sb); if (!b) return go('step');
    const d = uneed(m, b.id, S.su, () => V.stepquiz(m)); if (!d) return;
    const rev = S.sl === 'rev', src = rev ? d.review : d.lessons.find(x => x.id === S.sl); if (!src) return go('stepbook', { sb: b.id });
    const id = rev ? 'rev' + d.n : S.sl, title = rev ? `Unit ${d.n} Review` : `Lesson ${S.sl} Quiz`, A = S.sa = S.sa || {}, done = !!S.sres, G = src.quiz, qs = G.flatMap(g => g.q);
    // pages keep a text or a recording with its questions; about ten questions on a page
    const pages = []; G.flatMap(g => g.q.length > 12 && !g.a ? Array.from({ length: Math.ceil(g.q.length / 10) }, (_, i) => ({ l: i ? [] : g.l, q: g.q.slice(i * 10, i * 10 + 10) })) : [g]).forEach(g => { const last = pages[pages.length - 1]; if (last && last.n + g.q.length <= 10 && !(g.q.length >= 5 && last.n)) { last.g.push(g); last.n += g.q.length; } else pages.push({ g: [g], n: g.q.length }); });
    const pi = Math.min(S.sp || 0, pages.length - 1), P = pages[pi], pq = P.g.flatMap(g => g.q);
    const parts = [['Home', () => go('home')], ['STEP Preparation', () => go('step')], [b.name, () => go('stepbook', { sb: b.id })]].concat(rev ? [] : [[`Lesson ${S.sl}`, () => go('steplesson', { sb: b.id, su: d.n, sl: S.sl })]], [[rev ? title : 'Quiz']]);
    const res = S.sres; let top = '';
    if (done) top = `<section class="card st-res" style="margin-top:14px"><span class="muted">${title} · ${b.name}</span><div class="big">${res.got}<span style="font-size:.45em;color:var(--muted,#667)"> / ${qs.length}</span></div><b>${Math.round(100 * res.got / qs.length)}%</b>${res.best > res.got ? ` · your best is ${res.best}` : ''}
      <p class="muted" style="margin:.6rem 0 0">Review every answer below. Each one has an explanation and an Arabic hint. <span class="ar">راجع كل إجابة في الأسفل.</span></p>
      <div class="ctrls" style="justify-content:center;margin-top:10px"><button class="btn" id="stBack">← Back to ${b.name}</button><button class="btn sec" id="stAgain">↻ Try again</button></div></section>`;
    const lead = g => { const ls = g.l.filter(x => !/^\(\d+ words\)$/.test(x)); if (!ls.length && !g.a) return ''; const sc = g.a ? d.sc[g.a] || [] : null;
      return `<div class="card st-lead" style="margin-top:14px">${ls.map(x => /[؀-ۿ]/.test(x) && !/[A-Za-z]{5}/.test(x) ? `<p class="ar" dir="rtl">${esc(x)}</p>` : `<p${/^(Text|Recording|Part|Passage|Paragraph|Questions?) /.test(x) ? ' class="hd"' : ''}>${esc(x)}</p>`).join('')}
        ${g.a ? `<div class="ctrls" style="justify-content:flex-start"><button class="btn sm st-say" data-tr="${g.a}">▶ Listen</button><span class="muted">The device voice reads the recording.</span></div>${done ? `<details class="st-scr"><summary>📜 Script <span class="ar">نص التسجيل</span></summary>${sc.map(l => `<p>${esc(l)}</p>`).join('')}</details>` : ''}` : ''}</div>`; };
    const pal = `<div class="st-pal">${qs.map(q => `<button data-go="${q.n}" class="${done ? (A[q.n] === q.k ? 'ok' : 'no') : (A[q.n] != null ? 'a' : '')}${pq.includes(q) ? ' cur' : ''}">${q.n}</button>`).join('')}</div>`;
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${b.a};--b:${b.b}"><span class="d-ic">${rev ? '🏁' : b.ic}</span><div><span class="k">${b.name} · Unit ${d.n} · ${esc(d.level)} · ${qs.length} questions</span><h1>${title}${rev ? '' : ` <span style="font-size:.6em;opacity:.92">· ${esc(src.t)}</span>`}</h1></div></section>
    ${top}
    <div class="st-bar">${done ? '<b>Review</b>' : '<span class="muted" id="stAns"></span>'}${pal}${done ? '' : '<button class="btn sm" id="stFin">Finish ✓</button>'}</div>
    ${P.g.map(g => lead(g) + g.q.map(q => qHTML(q, A, done, /\(A\) /.test(q.s))).join('')).join('')}
    <div class="navrow" style="margin-top:16px"><button class="btn sec" id="stPrev"${pi ? '' : ' disabled'}>← Previous</button><span class="muted">Page ${pi + 1} of ${pages.length}</span>${pi < pages.length - 1 ? '<button class="btn" id="stNext">Next →</button>' : done ? `<button class="btn" id="stBack2">← Back to ${b.name}</button>` : '<button class="btn" id="stFin2">Finish ✓</button>'}</div><div id="stAsk"></div>`;
    bindCrumbs(m, parts);
    const page = i => { AU.stop(); S.sp = i; V.stepquiz(m); window.scrollTo({ top: 0 }); };
    const count = () => { const e = $('#stAns', m); if (e) e.textContent = `${qs.filter(q => A[q.n] != null).length}/${qs.length} answered`; };
    $$('[data-go]', m).forEach(x => x.onclick = () => { const qn = +x.dataset.go, i = pages.findIndex(p => p.g.some(g => g.q.some(q => q.n === qn))); if (i !== pi) page(i); const e = document.getElementById('sq' + qn); if (e) e.scrollIntoView({ block: 'center', behavior: 'smooth' }); });
    $$('.st-say', m).forEach(x => x.onclick = () => { if (x.classList.contains('playing')) { AU.stop(); x.classList.remove('playing'); x.textContent = '▶ Listen'; } else { $$('.st-say', m).forEach(y => { y.classList.remove('playing'); y.textContent = '▶ Listen'; }); if (say(d.sc[x.dataset.tr] || [], x)) x.textContent = '⏹ Stop'; else x.textContent = 'No voice on this device'; } });
    $('#stPrev', m).onclick = () => page(pi - 1); const nx = $('#stNext', m); if (nx) nx.onclick = () => page(pi + 1);
    ['#stBack', '#stBack2'].forEach(k => { const x = $(k, m); if (x) x.onclick = () => go('stepbook', { sb: b.id }); });
    const ag = $('#stAgain', m); if (ag) ag.onclick = () => go('stepquiz', { sb: b.id, su: d.n, sl: S.sl });
    if (done) return;
    count();
    $$('.opt[data-q]', m).forEach(x => x.onclick = () => { const qn = +x.dataset.q; A[qn] = +x.dataset.i; $$(`.opt[data-q="${qn}"]`, m).forEach(y => y.classList.toggle('on', y === x)); const pb = $(`[data-go="${qn}"]`, m); if (pb) pb.classList.add('a'); count(); });
    const finish = () => {
      const left = qs.filter(q => A[q.n] == null).length, box = $('#stAsk', m);
      const mark = () => { AU.stop(); const got = qs.filter(q => A[q.n] === q.k).length, me = Store.me(), k = bkey(b.id, id), old = (me.progress = me.progress || {})[k] || {};
        me.progress[k] = { done: true, score: got, total: qs.length, best: Math.max(got, old.best || 0), tries: (old.tries || 0) + 1, at: Date.now() }; Store.save();
        S.sres = { got, best: me.progress[k].best }; S.sp = 0; V.stepquiz(m); window.scrollTo({ top: 0 }); try { if (got / qs.length >= .7) RX.praise(); else RX.encourage(); } catch (e) {} };
      if (!left) return mark();
      box.innerHTML = `<div class="card" style="margin-top:14px;border:3px solid #F2B330"><b>${left} question${left > 1 ? 's are' : ' is'} not answered.</b> <span class="ar">توجد أسئلة لم تُجب عنها.</span><div class="ctrls" style="justify-content:flex-start;margin-top:8px"><button class="btn sec" id="stGo">Go to the first one</button><button class="btn" id="stMark">Finish anyway</button></div></div>`;
      box.scrollIntoView({ block: 'center', behavior: 'smooth' });
      $('#stGo', box).onclick = () => { const q = qs.find(q => A[q.n] == null); $(`[data-go="${q.n}"]`, m).click(); }; $('#stMark', box).onclick = mark;
    };
    ['#stFin', '#stFin2'].forEach(k => { const x = $(k, m); if (x) x.onclick = finish; });
  };

  /* small summary for the department card on the home page */
  function homeMeta() { const IX = window.STEP_INDEX || []; const d = IX.filter(x => total(x.n).done === 4).length; return d ? `${d}/${IX.length} exams done` : ''; }
  function register() {
    Object.assign(VIEWS, V);
    if (!document.getElementById('stepCss')) { const st = document.createElement('style'); st.id = 'stepCss'; st.textContent = CSS; document.head.appendChild(st); }
  }
  return { register, homeMeta, total, stopTimer };
})();
