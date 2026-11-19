/* Reading and Writing: the activity types that this strand adds to the department page.
   sequence (put parts in order), timed_reading (read against the clock), highlight (find the evidence in the text),
   and open / organizer / writing (write, compare with a model answer, mark yourself). */
'use strict';
(function () {
  const P = window.Pathway, el = P.el;
  const norm = s => String(s).toLowerCase().replace(/[“”"'’‘*]/g, '').replace(/[^a-z0-9؀-ۿ ]+/g, ' ').replace(/\s+/g, ' ').trim();
  const words = s => (String(s).trim().match(/\S+/g) || []).length;
  const fb = (ok, item, extra) => P.feedback(ok, item, extra);

  /* write, then compare with the model answer and mark yourself */
  function openItem(item, ctx, n) {
    const box = el('div', { class: 'item' }); box.appendChild(P.qText(item.q, n));
    const w = item._w, ta = el('textarea', { rows: w ? 7 : 3, 'aria-label': 'Your answer' }), count = el('span', { class: 'sub' }, '');
    const target = w && (w.min || w.max) ? (w.min || 0) + '–' + (w.max || '') + ' words' : '';
    ta.oninput = () => { const k = words(ta.value); count.textContent = k + ' word' + (k === 1 ? '' : 's') + (target ? ' · aim for ' + target : ''); };
    if (target) count.textContent = '0 words · aim for ' + target;
    box.append(ta, count);
    if (w && w.checklist && w.checklist.length) box.appendChild(el('div', { class: 'box mint', style: { marginTop: '8px' } }, el('b', null, 'Checklist'),
      el('ul', { class: 'clean' }, w.checklist.map(c => el('li', null, el('label', null, el('input', { type: 'checkbox' }), ' ' + c))))));
    const model = el('div', { class: 'model', hidden: true }, el('div', null, el('b', null, 'Model answer: '), el('span', { class: 'pre' }, item.answer)),
      el('div', { class: 'sub' }, item.explanation || ''), P.store.get().settings.arabic && item.explanation_ar ? P.ar(item.explanation_ar) : null,
      el('div', { class: 'row', style: { marginTop: '6px' } }, el('span', { class: 'sub' }, 'Compare, then mark your answer:'),
        el('button', { class: 'btn alt sm', type: 'button', onclick: e => mark(true, e.target) }, '✓ Mine is as good'),
        el('button', { class: 'btn ghost sm', type: 'button', onclick: e => mark(false, e.target) }, 'I need more practice')));
    let marked = false;
    function mark(ok, b) { if (marked) return; marked = true; b.parentNode.querySelectorAll('button').forEach(x => x.disabled = true); ctx.result(ok); if (window.Cheer) Cheer.react(ok); P.toast(ok ? 'Great work!' : 'Keep practicing – you can do it!'); }
    const show = el('button', { class: 'btn sm', type: 'button', onclick: () => { if (!ta.value.trim()) return P.toast('Write your answer first.'); model.hidden = false; show.disabled = true; } }, 'Show model answer');
    box.append(el('div', { class: 'row' }, show), model);
    if (ctx.showAnswers) model.hidden = false;
    return box;
  }
  const RWD = /[?&]d=rw\b/.test(location.search);   // 'open' keeps its own behaviour in Language Usage
  (RWD ? ['open', 'organizer', 'writing'] : ['organizer', 'writing']).forEach(t => P.registerActivity(t, (item, ctx, n) => item.options && item.options.length ? choice(item, ctx, n) : openItem(item, ctx, n)));

  /* a multiple-choice item inside one of this strand's own activity types */
  function choice(item, ctx, n) {
    const box = el('div', { class: 'item' }); box.appendChild(P.qText(item.q, n));
    const opts = el('div', { class: 'opts' + (item.options.some(o => o.length > 38) ? ' col' : '') }); let done = false;
    item.options.forEach((o, i) => { const b = el('button', { class: 'opt', type: 'button' }, 'abcdefgh'[i] + ') ' + o);
      b.onclick = () => { if (done) return; done = true; const ok = o === item.answer; b.classList.add(ok ? 'ok' : 'bad'); [...opts.children].forEach((x, k) => { x.disabled = true; if (item.options[k] === item.answer) x.classList.add('ok'); }); box.appendChild(fb(ok, item)); ctx.result(ok); };
      opts.appendChild(b); });
    box.appendChild(opts); return box;
  }

  /* put the parts in order: tap the arrows, then check */
  P.registerActivity('sequence', (item, ctx, n) => {
    if (!item.parts) return openItem(item, ctx, n);
    const box = el('div', { class: 'item' }); box.appendChild(P.qText(item.q, n));
    let cur = P.shuffle(item.parts.map((t, i) => i), n * 11 + item.parts.length); if (cur.every((v, i) => item.parts[v] === item.target[i])) cur.reverse();
    const list = el('div', { class: 'rw-seq' }); let done = false;
    const draw = () => { list.innerHTML = ''; cur.forEach((pi, pos) => list.appendChild(el('div', { class: 'rw-row' }, el('span', { class: 'n' }, (pos + 1) + '.'), el('span', { class: 'rw-part' }, item.parts[pi]),
      el('button', { class: 'btn ghost sm', type: 'button', disabled: done || pos === 0, 'aria-label': 'Move up', onclick: () => { [cur[pos - 1], cur[pos]] = [cur[pos], cur[pos - 1]]; draw(); } }, '↑'),
      el('button', { class: 'btn ghost sm', type: 'button', disabled: done || pos === cur.length - 1, 'aria-label': 'Move down', onclick: () => { [cur[pos + 1], cur[pos]] = [cur[pos], cur[pos + 1]]; draw(); } }, '↓')))); };
    draw();
    const btn = el('button', { class: 'btn alt sm', type: 'button', onclick: () => { if (done) return; done = true; btn.disabled = true; const ok = cur.every((pi, i) => item.parts[pi] === item.target[i]); draw(); box.appendChild(fb(ok, item)); ctx.result(ok); } }, 'Check the order');
    box.append(list, el('div', { class: 'row', style: { marginTop: '8px' } }, btn));
    return box;
  });

  /* read the text against the clock */
  P.registerActivity('timed_reading', (item, ctx, n) => {
    const box = el('div', { class: 'item' }); box.appendChild(P.qText(item.q + ' ' + item.words + ' words' + (item.limit ? ' · goal: ' + Math.floor(item.limit / 60) + ':' + P.pad(item.limit % 60) : ''), n));
    const text = el('div', { class: 'pre rw-text', hidden: true }, item.body), clock = el('span', { class: 'timer' }, '0:00'), out = el('div');
    let t0 = 0, iv = null, done = false;
    const start = el('button', { class: 'btn alt sm', type: 'button' }, '▶ Start reading'), stop = el('button', { class: 'btn sm', type: 'button', disabled: true }, '■ I finished');
    start.onclick = () => { if (t0 || done) return; t0 = Date.now(); text.hidden = false; start.disabled = true; stop.disabled = false; iv = setInterval(() => { const s = Math.round((Date.now() - t0) / 1000); clock.textContent = Math.floor(s / 60) + ':' + P.pad(s % 60); if (!document.body.contains(box)) clearInterval(iv); }, 500); };
    stop.onclick = () => { if (done || !t0) return; done = true; clearInterval(iv); stop.disabled = true; const s = Math.max(1, Math.round((Date.now() - t0) / 1000)), wpm = Math.round(item.words * 60 / s), tooFast = wpm > 400, ok = !tooFast && (!item.limit || s <= item.limit);
      out.appendChild(el('div', { class: 'fb ' + (ok ? 'ok' : 'bad') }, el('b', null, 'Your time: ' + Math.floor(s / 60) + ':' + P.pad(s % 60) + ' · about ' + wpm + ' words a minute. '),
        tooFast ? 'That was too fast to read every word. Read it again carefully.' : ok ? 'You reached the goal. Well done!' : 'Good reading. Read it again tomorrow and try to be a little faster.'));
      if (window.Cheer) Cheer.react(ok); ctx.result(ok); };
    box.append(el('div', { class: 'row' }, start, stop, clock), text, out);
    return box;
  });

  /* find the evidence: tap the sentence in the text */
  P.registerActivity('highlight', (item, ctx, n) => {
    if (item.options && item.options.length) return choice(item, ctx, n);
    if (!item.sentences) return openItem(item, ctx, n);
    const want = norm(item.evidence || item.answer), hit = s => { const k = norm(s); return k.length > 5 && (want.includes(k) || (k.includes(want) && want.length > 8)); };
    if (!item.sentences.some(hit)) return openItem(item, ctx, n);
    const box = el('div', { class: 'item' }); box.appendChild(P.qText(item.q, n)); box.appendChild(el('div', { class: 'sub' }, 'Tap the sentence in the text.'));
    const text = el('div', { class: 'rw-text rw-pick' }); let done = false;
    item.sentences.forEach(s => { const b = el('button', { class: 'rw-sent', type: 'button' }, s + ' ');
      b.onclick = () => { if (done) return; done = true; const ok = hit(s); b.classList.add(ok ? 'ok' : 'bad'); [...text.children].forEach((x, k) => { x.disabled = true; if (hit(item.sentences[k])) x.classList.add('ok'); }); box.appendChild(fb(ok, item)); ctx.result(ok); };
      text.appendChild(b); });
    box.appendChild(text); return box;
  });

  const css = document.createElement('style');
  css.textContent = '.rw-row{display:flex;gap:8px;align-items:center;padding:6px 8px;border:2px solid var(--line,#E3E7F0);border-radius:12px;margin:6px 0;background:#fff}.rw-row .rw-part{flex:1}.rw-row .n{font-weight:800}' +
    '.rw-text{background:#FFFDF6;border:2px solid #F3E3B5;border-radius:14px;padding:12px 14px;margin-top:8px;line-height:1.9;font-size:1.05rem}' +
    '.rw-sent{display:inline;border:0;background:none;font:inherit;text-align:left;padding:2px 1px;border-radius:6px;cursor:pointer;line-height:inherit;color:inherit}.rw-sent:hover:not(:disabled){background:#FFF1B8}.rw-sent.ok{background:#CFF3DF}.rw-sent.bad{background:#FBD5DB}';
  document.head.appendChild(css);
})();
