/* Phonics department: "Phonics Made Clear" (Grade 3) by Waleed Youssef.
   40 parts in 11 units. Each part has the book pages with the recorded narration, and the Practice Book exercises
   made interactive (multiple choice, true/false, write the word, sort the words, dictation) with the book's answer key.
   Data: ph/index.js, book pages ph/pg/NNN.webp, narration audio/phonics/PNN.mp3 (built by tools/app/build_phonics.py). */
const PHX = (() => {
  'use strict';
  const D = () => window.PH_DATA, A = '#F0569C', B = '#C92671', V = {};
  const CSS = `
.ph-tabs{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}.ph-tab{flex:1;min-width:150px;border:2px solid var(--line,#E3E7F0);background:#fff;border-radius:14px;padding:10px 12px;cursor:pointer;font:inherit;font-weight:800;text-align:center}
.ph-tab.on{border-color:${B};background:#FFF0F7;color:${B}}
.ph-audio{position:sticky;top:70px;z-index:5;display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:#fff;border:2px solid ${A};border-radius:16px;padding:8px 12px;margin-top:12px;box-shadow:0 6px 18px rgba(30,40,80,.10)}
.ph-audio audio{flex:1;min-width:220px;height:40px}
.ph-pages{display:grid;gap:14px;margin-top:14px}.ph-pages img{width:100%;height:auto;display:block;border-radius:14px;border:2px solid var(--line,#E3E7F0);background:#fff}
.ph-ex{margin-top:14px}.ph-ex h3{margin:0 0 4px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}.ph-ex .lv{font-size:.8rem;background:${A};color:#fff;border-radius:999px;padding:1px 10px}
.ph-ex .pre{margin:.2rem 0;font-weight:700}.ph-box{background:#FFF7FB;border:2px dashed #F5BBD6;border-radius:12px;padding:8px 12px;margin:.4rem 0;font-weight:700}
.ph-q{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:8px 0;border-top:1px solid var(--line,#EEF1F7)}.ph-q .num{font-weight:800;color:${B};min-width:1.6em}.ph-q .st{flex:1;min-width:180px}
.ph-q input,.ph-q select{font:inherit;padding:6px 10px;border-radius:10px;border:2px solid var(--line,#D8DEEA);min-width:120px;max-width:100%}
.ph-opts{display:flex;flex-wrap:wrap;gap:6px;width:100%}.ph-o{border:2px solid var(--line,#D8DEEA);background:#fff;border-radius:10px;padding:6px 12px;cursor:pointer;font:inherit}
.ph-o.on{border-color:#2F6FE0;background:#EEF4FF}.ph-o.ok,.ph-q input.ok,.ph-q select.ok{border-color:#22B573;background:#EAFBF2}.ph-o.no,.ph-q input.no,.ph-q select.no{border-color:#E0445C;background:#FDECEF}
.ph-q .fix{color:#178A56;font-weight:800}.ph-self{white-space:pre-wrap;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.86rem;background:#F8F9FC;border-radius:12px;padding:10px;overflow-x:auto}
.ph-ex [hidden]{display:none!important}.ph-score{font-weight:800;margin-left:8px}.ph-key{margin-top:8px;background:#F1FBF6;border-radius:12px;padding:8px 12px}
@media (max-width:640px){.ph-audio{top:58px}}
`;
  const prog = id => (Store.me().progress || {})['ph:' + id] || null;
  const exList = id => id[0] === 'R' ? D().reviews[id.slice(1)] || [] : (D().parts[+id.slice(1) - 1] || {}).ex || [];
  const scored = e => e.ty !== 'self';
  const nItems = e => e.ty === 'sort' ? e.g.reduce((a, g) => a + g.w.length, 0) : (e.q || []).length;
  const totals = id => { const p = prog(id), ex = exList(id).filter(scored); let got = 0, all = 0, done = 0; ex.forEach(e => { all += nItems(e); const r = p && p.ex && p.ex[e.n]; if (r) { got += r.got; done++; } }); return { got, all, done, n: ex.length }; };
  const clean = s => String(s).toLowerCase().replace(/[’']/g, "'").replace(/\s*\+\s*/g, '+').replace(/[.,!?;:"]/g, '').replace(/\s+/g, ' ').trim();
  const right = (v, a) => { const x = clean(v); return !!x && a.split(/\s+\/\s+|\s+or\s+/).some(t => clean(t) === x); };
  function shuffle(a, seed) { const r = a.slice(); let s = seed || 7; for (let i = r.length - 1; i > 0; i--) { s = (s * 9301 + 49297) % 233280; const j = Math.floor(s / 233280 * (i + 1)); [r[i], r[j]] = [r[j], r[i]]; } return r; }
  function speak(w, btn) { try { AU.stop(); } catch (e) {} if (!window.speechSynthesis) { if (btn) btn.textContent = 'No voice on this device'; return; } speechSynthesis.cancel(); [w, w].forEach((t, i) => { const u = new SpeechSynthesisUtterance(t); u.lang = 'en-US'; u.rate = i ? .7 : .85; speechSynthesis.speak(u); }); }

  V.ph = m => {
    const d = D(), parts = [['Home', () => go('home')], ['Phonics']];
    const row = (id, ic, small, title, pagesN) => { const t = totals(id), started = t.done > 0, fin = t.n > 0 && t.done === t.n; return `<button class="lrow${fin ? ' done' : ''}" data-ph="${id}"><span class="ic">${fin ? '✅' : ic}</span><span class="tx"><small>${small}${pagesN ? ` · ${pagesN} pages · audio` : ''} · ${t.n} exercises</small><b>${esc(title)}</b></span><span class="st">${started ? `${t.got}/${t.all}` : '→'}</span></button>`; };
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${A};--b:${B}"><span class="d-ic">🔤</span><div><span class="k">Department · Phonics Made Clear · Grade 3 · 40 parts · 11 units</span><h1>Phonics <span class="ar" style="color:#fff;font-size:.8em">الصوتيات</span></h1></div></section>
    ${typeof introCard === 'function' ? introCard('ph') : ''}
    ${d.units.map(u => `<section class="card" style="margin-top:16px;--a:${A};--b:${B}"><h2 style="margin:0 0 6px"><span style="background:${A};color:#fff;border-radius:999px;padding:2px 12px;font-size:.9rem;margin-right:8px">Unit ${u.n}</span>${esc(u.t)}</h2>
      ${u.parts.map(n => { const p = d.parts[n - 1]; return row('P' + n, '🔤', `Part ${n}`, p.t, p.pages.length); }).join('')}
      ${d.reviews[u.n] ? row('R' + u.n, '🏁', 'Unit review', `Unit ${u.n} Review`, 0) : ''}</section>`).join('')}`;
    bindCrumbs(m, parts);
    $$('[data-ph]', m).forEach(b => b.onclick = () => go('phpart', { pp: b.dataset.ph }));
  };

  V.phpart = m => {
    const d = D(), id = S.pp || 'P1', rev = id[0] === 'R', P = rev ? null : d.parts[+id.slice(1) - 1], ex = exList(id); if (!rev && !P) return go('ph');
    const tab = rev ? 'x' : (S.pt || 'l'), title = rev ? `Unit ${id.slice(1)} Review` : `Part ${P.n} · ${P.t}`;
    const parts = [['Home', () => go('home')], ['Phonics', () => go('ph')], [rev ? title : `Part ${P.n}`]];
    const order = d.units.flatMap(u => u.parts.map(n => 'P' + n).concat(d.reviews[u.n] ? ['R' + u.n] : [])), nextId = order[order.indexOf(id) + 1];
    const pr = prog(id) || { ex: {} };
    const exHTML = e => {
      const done = pr.ex[e.n]; let body = '';
      const pre = (e.pre || []).map((x, i) => i === 0 ? `<p class="pre">${esc(x)}</p>` : `<div class="ph-box">${esc(x)}</div>`).join('');
      if (e.ty === 'mc') body = e.q.map((q, i) => `<div class="ph-q" data-i="${i}"><span class="num">${i + 1}.</span><span class="st">${esc(q.s)}</span><div class="ph-opts">${q.o.map((o, k) => `<button class="ph-o" data-k="${k}"><b>${'abcd'[k]})</b> ${esc(o)}</button>`).join('')}</div></div>`).join('');
      else if (e.ty === 'tf') body = e.q.map((q, i) => `<div class="ph-q" data-i="${i}"><span class="num">${i + 1}.</span><span class="st">${esc(q.s)}</span><div class="ph-opts"><button class="ph-o" data-k="1">True</button><button class="ph-o" data-k="0">False</button></div></div>`).join('');
      else if (e.ty === 'fill') body = e.q.map((q, i) => `<div class="ph-q" data-i="${i}"><span class="num">${i + 1}.</span><span class="st">${esc(q.s)}</span><input type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Answer ${i + 1}"><span class="fix"></span></div>`).join('');
      else if (e.ty === 'dict') body = `<p class="muted" style="margin:.2rem 0">Press 🔊 to hear each word two times, then write it. <span class="ar">اضغط 🔊 لتسمع كل كلمة مرتين ثم اكتبها.</span></p>` + e.q.map((q, i) => `<div class="ph-q" data-i="${i}"><span class="num">${i + 1}.</span><button class="btn sm sec ph-say" data-w="${esc(q.a)}">🔊 Listen</button><input type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Word ${i + 1}"><span class="fix"></span></div>`).join('');
      else if (e.ty === 'sort') { const words = shuffle(e.g.flatMap(g => g.w), e.n * 13 + ex.length); body = `<p class="muted" style="margin:.2rem 0">Choose the group for each word. <span class="ar">اختر المجموعة المناسبة لكل كلمة.</span></p>` + words.map((w, i) => `<div class="ph-q" data-w="${esc(w)}"><span class="num">${i + 1}.</span><span class="st"><b>${esc(w)}</b></span><select aria-label="Group for ${esc(w)}"><option value="">Choose…</option>${e.g.map(g => `<option>${esc(g.l)}</option>`).join('')}</select><span class="fix"></span></div>`).join(''); }
      else body = `<div class="ph-self">${esc(e.text.join('\n'))}</div><p class="muted">Do this exercise in your notebook, then check your answers. <span class="ar">حُلّ هذا التمرين في دفترك ثم راجع الإجابات.</span></p>`;
      return `<section class="card ph-ex" data-ex="${e.n}"><h3>Exercise ${e.n}<span class="lv">${esc(e.lv)}</span>${done ? `<span class="ph-score" style="color:#178A56">Best: ${done.got}/${done.total}</span>` : ''}</h3>${e.ty === 'self' ? '' : pre}${body}
        <div class="ctrls" style="justify-content:flex-start;margin-top:10px">${e.ty === 'self' ? '<button class="btn sec ph-show">Show the answers</button>' : '<button class="btn ph-check">✓ Check</button><button class="btn sec ph-again" hidden>↻ Try again</button>'}<span class="ph-score ph-now"></span></div><div class="ph-out"></div></section>`;
    };
    m.innerHTML = crumbs(parts) + `
    <section class="lhead dhead" style="--a:${A};--b:${B}"><span class="d-ic">${rev ? '🏁' : '🔤'}</span><div><span class="k">Phonics Made Clear${rev ? '' : ` · ${P.pages.length} pages · ${ex.length} exercises`}</span><h1>${esc(title)}</h1></div></section>
    ${rev ? '' : `<div class="ph-tabs"><button class="ph-tab${tab === 'l' ? ' on' : ''}" data-t="l">📖 Lesson and audio <span class="ar">الدرس والصوت</span></button><button class="ph-tab${tab === 'x' ? ' on' : ''}" data-t="x">✏️ Practice · ${ex.length} exercises <span class="ar">التدريب</span></button></div>`}
    ${tab === 'l' ? `<div class="ph-audio"><b>🎧 Listen to Part ${P.n}</b><audio controls controlslist="nodownload" preload="none" src="audio/phonics/P${String(P.n).padStart(2, '0')}.mp3"></audio></div>
      <div class="ph-pages">${P.pages.map((p, i) => `<img src="ph/pg/${String(p).padStart(3, '0')}.webp" alt="Phonics Made Clear, Part ${P.n}, page ${i + 1} of ${P.pages.length}" loading="${i ? 'lazy' : 'eager'}" width="794" height="1123">`).join('')}</div>
      <div class="navrow" style="margin-top:16px"><button class="btn sec" id="phBack">← All parts</button><button class="btn" id="phGoX">Go to the practice →</button></div>`
      : `${rev ? '' : `<section class="card" style="margin-top:14px;border-left:6px solid ${A}"><b>Remember</b> <span class="ar">تذكّر</span><p style="margin:.3rem 0 0">${esc(P.rem)}</p></section>`}
      ${ex.map(exHTML).join('')}
      <div class="navrow" style="margin-top:16px"><button class="btn sec" id="phBack">← All parts</button>${nextId ? `<button class="btn" id="phNext">Next: ${nextId[0] === 'R' ? `Unit ${nextId.slice(1)} Review` : `Part ${nextId.slice(1)}`} →</button>` : ''}</div>`}`;
    bindCrumbs(m, parts);
    $$('[data-t]', m).forEach(b => b.onclick = () => go('phpart', { pp: id, pt: b.dataset.t }));
    $('#phBack', m).onclick = () => go('ph'); const gx = $('#phGoX', m); if (gx) gx.onclick = () => { go('phpart', { pp: id, pt: 'x' }); window.scrollTo({ top: 0 }); };
    const nx = $('#phNext', m); if (nx) nx.onclick = () => { go('phpart', { pp: nextId }); window.scrollTo({ top: 0 }); };
    $$('.ph-say', m).forEach(b => b.onclick = () => speak(b.dataset.w, b));
    $$('.ph-ex', m).forEach(card => {
      const e = ex.find(x => x.n === +card.dataset.ex), out = $('.ph-out', card);
      $$('.ph-o', card).forEach(o => o.onclick = () => { if (card.dataset.done) return; $$('.ph-o', o.parentNode).forEach(y => y.classList.toggle('on', y === o)); });
      const sh = $('.ph-show', card); if (sh) { sh.onclick = () => { out.innerHTML = `<div class="ph-key"><b>Answers:</b> ${esc(e.key)}</div>`; }; return; }
      const again = $('.ph-again', card), chk = $('.ph-check', card);
      again.onclick = () => { delete card.dataset.done; $$('.ok,.no,.on', card).forEach(x => x.classList.remove('ok', 'no', 'on')); $$('input', card).forEach(x => { x.value = ''; x.disabled = false; }); $$('select', card).forEach(x => { x.value = ''; x.disabled = false; }); $$('.fix', card).forEach(x => x.textContent = ''); $('.ph-now', card).textContent = ''; again.hidden = true; chk.hidden = false; };
      chk.onclick = () => {
        let got = 0, total = 0;
        if (e.ty === 'mc' || e.ty === 'tf') $$('.ph-q', card).forEach(q => { const it = e.q[+q.dataset.i], want = e.ty === 'mc' ? it.k : (it.k ? 1 : 0), pick = $('.ph-o.on', q); total++; $$('.ph-o', q).forEach(o => { if (+o.dataset.k === want) o.classList.add('ok'); else if (o === pick) o.classList.add('no'); }); if (pick && +pick.dataset.k === want) got++; });
        else if (e.ty === 'sort') { const where = {}; e.g.forEach(g => g.w.forEach(w => where[w] = g.l)); $$('.ph-q', card).forEach(q => { const s = $('select', q), ok = s.value === where[q.dataset.w]; total++; s.classList.add(ok ? 'ok' : 'no'); s.disabled = true; if (ok) got++; else $('.fix', q).textContent = '→ ' + where[q.dataset.w]; }); }
        else $$('.ph-q', card).forEach(q => { const it = e.q[+q.dataset.i], inp = $('input', q), ok = right(inp.value, it.a); total++; inp.classList.add(ok ? 'ok' : 'no'); inp.disabled = true; if (ok) got++; else $('.fix', q).textContent = '→ ' + it.a; });
        card.dataset.done = '1'; chk.hidden = true; again.hidden = false; $('.ph-now', card).textContent = `${got}/${total}`; $('.ph-now', card).style.color = got === total ? '#178A56' : '#B5651D';
        const me = Store.me(), k = 'ph:' + id, p = (me.progress = me.progress || {})[k] || { ex: {} }; p.ex = p.ex || {}; const old = p.ex[e.n];
        if (!old || got > old.got) p.ex[e.n] = { got, total };
        const sc = ex.filter(scored); p.score = sc.reduce((a, x) => a + ((p.ex[x.n] || {}).got || 0), 0); p.total = sc.reduce((a, x) => a + nItems(x), 0); p.best = p.score; p.done = sc.every(x => p.ex[x.n]); p.at = Date.now(); me.progress[k] = p; Store.save();
        try { if (got / total >= .7) RX.praise(); else RX.encourage(); } catch (err) {}
      };
    });
  };

  function homeMeta() { const d = D(); if (!d) return ''; const n = d.parts.filter(p => { const t = totals('P' + p.n); return t.n && t.done === t.n; }).length; return n ? `${n}/40 parts done` : ''; }
  function register() {
    Object.assign(VIEWS, V);
    if (!document.getElementById('phCss')) { const st = document.createElement('style'); st.id = 'phCss'; st.textContent = CSS; document.head.appendChild(st); }
  }
  return { register, homeMeta };
})();
