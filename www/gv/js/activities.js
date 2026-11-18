/* English Pathway Programme – interactive activities, quizzes and tests with instant feedback (English + Arabic). */
'use strict';
(function () {
  const P = window.Pathway, el = P.el;

  /* Question text: SAT items carry a short text, a blank line and then the question. */
  P.qText = function (q, n, fallback) {
    const wrap = el('div', { class: 'q' });
    if (n) wrap.appendChild(el('span', { class: 'n' }, n + '.'));
    const raw = q && q.trim() ? q : (fallback || 'Choose the correct sentence.');
    const parts = raw.split(/\n\n/);
    if (parts.length > 1) {
      wrap.appendChild(el('div', { class: 'pre', style: { fontWeight: 400 } }, parts.slice(0, -1).join('\n\n')));
      wrap.appendChild(el('div', { style: { marginTop: '6px' } }, parts[parts.length - 1]));
    } else wrap.appendChild(el('span', { class: 'pre' }, raw));
    return wrap;
  };

  P.feedback = function (ok, item, extra) {
    if (window.Cheer) Cheer.react(ok);
    const S = P.store.get();
    const head = ok ? '✓ Correct! ' : '✗ Not quite. ';
    const ans = ok ? '' : (item.answer ? 'Answer: ' + item.answer + '. ' : '');
    return el('div', { class: 'fb ' + (ok ? 'ok' : 'bad') },
      el('div', null, el('b', null, head), ans, item.explanation || '', extra || ''),
      S.settings.arabic && item.explanation_ar ? P.ar((ok ? 'أحسنت! ' : 'حاول مرة أخرى. ') + item.explanation_ar) : null);
  };

  /* ---------------------------------------------------------- item renderers (instant feedback) */
  function choiceItem(item, ctx, n) {
    const box = el('div', { class: 'item' });
    box.appendChild(P.qText(item.q, n, item.options.length === 2 ? 'True or false?' : null));
    const long = item.options.some(o => o.length > 38);
    const opts = el('div', { class: 'opts' + (long ? ' col' : '') });
    let done = false;
    item.options.forEach((o, i) => {
      const b = el('button', { class: 'opt', type: 'button' }, (item.options.length > 2 ? 'abcdefgh'[i] + ') ' : '') + o);
      b.onclick = () => {
        if (done) return;
        const ok = o === item.answer;
        b.classList.add(ok ? 'ok' : 'bad');
        if (!ok) [...opts.children].forEach(x => { if (x.textContent.endsWith(item.answer) && x.textContent.replace(/^[a-h]\) /, '') === item.answer) x.classList.add('ok'); });
        done = true; [...opts.children].forEach(x => x.disabled = true);
        box.appendChild(P.feedback(ok, item));
        ctx.result(ok);
      };
      opts.appendChild(b);
    });
    box.appendChild(opts);
    if (ctx.showAnswers) box.appendChild(el('div', { class: 'sub' }, 'Key: ' + item.answer));
    return box;
  }

  function gapItem(item, ctx, n) {
    const box = el('div', { class: 'item' });
    const q = el('div', { class: 'q' }, el('span', { class: 'n' }, n + '.'));
    const parts = item.q.split(/_{3,}/);
    const input = el('input', { class: 'gap', type: 'text', 'aria-label': 'Answer', autocomplete: 'off', autocapitalize: 'off', spellcheck: 'false' });
    q.appendChild(document.createTextNode(parts[0]));
    q.appendChild(input);
    q.appendChild(document.createTextNode(parts.slice(1).join(' ______ ')));
    box.appendChild(q);
    let tries = 0, done = false;
    const check = () => {
      if (done || !input.value.trim()) return;
      tries++;
      const ok = P.alternatives(item.answer).some(a => P.sameLoose(a, input.value));
      const old = box.querySelector('.fb'); if (old) old.remove();
      if (ok || tries >= 2) {
        done = true; input.disabled = true; btn.disabled = true;
        input.style.borderColor = ok ? 'var(--ok)' : 'var(--bad)';
        box.appendChild(P.feedback(ok, item));
        ctx.result(ok && tries === 1);
      } else {
        box.appendChild(el('div', { class: 'fb bad' }, 'Try again – check the form and the spelling.',
          P.store.get().settings.arabic ? P.ar('حاول مرة أخرى، وانتبه إلى الصيغة والإملاء.') : null));
      }
    };
    input.addEventListener('keydown', e => { if (e.key === 'Enter') check(); });
    const btn = el('button', { class: 'btn sm', type: 'button', onclick: check }, 'Check');
    box.appendChild(el('div', { class: 'row' }, btn));
    if (ctx.showAnswers) box.appendChild(el('div', { class: 'sub' }, 'Key: ' + item.answer));
    return box;
  }

  /* Drag-to-order / tap-to-order sentence builder */
  P.orderBuilder = function (tiles, answer, onDone, item) {
    const box = el('div');
    const pool = el('div', { class: 'tiles' }), build = el('div', { class: 'tiles build', 'aria-label': 'Your sentence' });
    let placed = [];
    const draw = () => {
      pool.innerHTML = ''; build.innerHTML = '';
      tiles.forEach((t, i) => {
        const used = placed.includes(i);
        pool.appendChild(el('button', { class: 'tile' + (used ? ' used' : ''), type: 'button', disabled: used, onclick: () => { placed.push(i); draw(); } }, t));
      });
      placed.forEach((i, pos) => {
        const b = el('button', { class: 'tile', type: 'button', draggable: 'true', title: 'Tap to remove or drag to move', onclick: () => { placed.splice(pos, 1); draw(); } }, tiles[i]);
        b.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', String(pos)); });
        b.addEventListener('dragover', e => e.preventDefault());
        b.addEventListener('drop', e => {
          e.preventDefault();
          const from = +e.dataTransfer.getData('text/plain'); const v = placed.splice(from, 1)[0]; placed.splice(pos, 0, v); draw();
        });
        build.appendChild(b);
      });
    };
    draw();
    let done = false, tries = 0;
    const check = el('button', { class: 'btn sm', type: 'button' }, 'Check');
    check.onclick = () => {
      if (done || placed.length < tiles.length) { P.toast('Use all the tiles.'); return; }
      tries++;
      const said = placed.map(i => tiles[i]).join(' ');
      const ok = P.sameLoose(said, answer);
      const old = box.querySelector('.fb'); if (old) old.remove();
      if (ok || tries >= 2) {
        done = true; check.disabled = true;
        box.appendChild(P.feedback(ok, item || { answer, explanation: '', explanation_ar: '' }));
        onDone(ok && tries === 1);
      } else box.appendChild(el('div', { class: 'fb bad' }, 'Not yet – check the word order and try again.'));
    };
    box.append(el('div', { class: 'sub' }, 'Tap the words in order. Tap a word in your sentence to take it out, or drag it to move it.'), pool, build,
      el('div', { class: 'row' }, check, el('button', { class: 'btn ghost sm', type: 'button', onclick: () => { if (!done) { placed = []; draw(); } } }, 'Clear')));
    return box;
  };
  function orderItem(item, ctx, n) {
    const box = el('div', { class: 'item' });
    box.appendChild(el('div', { class: 'q' }, el('span', { class: 'n' }, n + '.'), 'Put the words in order.', el('span', { class: 'sub' }, '  ' + (item.q.match(/\(\s*(.)\s*\)\s*$/) ? 'End with ' + item.q.match(/\(\s*(.)\s*\)\s*$/)[1] : ''))));
    box.appendChild(P.orderBuilder(P.shuffle(item.options, n * 7 + 3), item.answer.replace(/[.?!]$/, ''), ok => ctx.result(ok), item));
    return box;
  }

  /* Editing items: tap the mistake (error hunt), then rewrite the sentence. */
  P.isEdit = item => !/^answers will vary/i.test(item.explanation || '') && item.answer && item.q &&
    P.clean(item.q.replace(/\s{2,}\(.*?\)\s*$/, '')) !== P.clean(item.answer) && P.similar(item.q, item.answer) >= 0.5;
  function editItem(item, ctx, n) {
    const box = el('div', { class: 'item' });
    const hint = (item.q.match(/\s{2,}\((.*?)\)\s*$/) || [])[1];
    const wrong = item.q.replace(/\s{2,}\(.*?\)\s*$/, '');
    const z = P.diffZone(wrong, item.answer);
    box.appendChild(el('div', { class: 'q' }, el('span', { class: 'n' }, n + '.'), 'Tap the mistake, then write the sentence correctly.', hint ? el('span', { class: 'sub' }, '  (' + hint + ')') : null));
    const line = el('div', { style: { fontSize: '1.05rem', margin: '4px 0 8px' } });
    let found = false, misses = 0, firstTry = true;
    z.tokens.forEach((t, i) => {
      const b = el('button', { class: 'tok', type: 'button' }, t);
      b.onclick = () => {
        if (found) return;
        if (i >= z.start && i <= z.end) {
          found = true; b.classList.add('hit');
          for (let k = z.start; k <= z.end; k++) line.children[k].classList.add('hit');
          P.toast('Yes! You found the mistake.');
        } else {
          b.classList.add('miss'); misses++; firstTry = false;
          if (misses >= 2) for (let k = z.start; k <= z.end; k++) line.children[k].classList.add('zone');
        }
      };
      line.appendChild(b);
    });
    box.appendChild(line);
    const ta = el('textarea', { rows: 2, 'aria-label': 'Corrected sentence', spellcheck: 'false' }, wrong);
    box.appendChild(ta);
    let done = false, tries = 0;
    const btn = el('button', { class: 'btn sm', type: 'button' }, 'Check');
    btn.onclick = () => {
      if (done) return;
      tries++;
      const ok = P.sameSentence(ta.value, item.answer);
      const old = box.querySelector('.fb'); if (old) old.remove();
      if (ok || tries >= 2) {
        done = true; btn.disabled = true; ta.disabled = true;
        box.appendChild(P.feedback(ok, item));
        ctx.result(ok && tries === 1 && firstTry);
      } else box.appendChild(el('div', { class: 'fb bad' }, 'Not yet – look again at the words you tapped.',
        P.store.get().settings.arabic ? P.ar('ليس بعد – انظر مرة أخرى إلى موضع الخطأ.') : null));
    };
    box.appendChild(el('div', { class: 'row' }, btn));
    if (ctx.showAnswers) box.appendChild(el('div', { class: 'sub' }, 'Key: ' + item.answer));
    return box;
  }
  P.sameSentence = (a, b) => P.clean(a).replace(/\.$/, '') === P.clean(b).replace(/\.$/, '');

  function openItem(item, ctx, n) {
    const box = el('div', { class: 'item' });
    box.appendChild(P.qText(item.q, n));
    const ta = el('textarea', { rows: 3, 'aria-label': 'Your answer' });
    box.appendChild(ta);
    const model = el('div', { class: 'model', hidden: true },
      el('div', null, el('b', null, 'Model answer: '), item.answer),
      el('div', { class: 'sub' }, item.explanation || ''),
      P.store.get().settings.arabic && item.explanation_ar ? P.ar(item.explanation_ar) : null,
      el('div', { class: 'row', style: { marginTop: '6px' } }, el('span', { class: 'sub' }, 'Check your answer:'),
        el('button', { class: 'btn alt sm', type: 'button', onclick: e => { mark(true, e.target); } }, '✓ I used it correctly'),
        el('button', { class: 'btn ghost sm', type: 'button', onclick: e => { mark(false, e.target); } }, 'I need more practice')));
    let marked = false;
    function mark(ok, b) { if (marked) return; marked = true; b.parentNode.querySelectorAll('button').forEach(x => x.disabled = true); ctx.result(ok); if (window.Cheer) Cheer.react(ok); P.toast(ok ? 'Great work!' : 'Keep practicing – you can do it!'); }
    const show = el('button', { class: 'btn sm', type: 'button', onclick: () => { model.hidden = false; show.disabled = true; } }, 'Show model answer');
    box.append(el('div', { class: 'row' }, show), model);
    return box;
  }

  P.renderItem = function (item, type, ctx, n) {
    if (P.activityTypes[type]) return P.activityTypes[type](item, ctx, n);
    if (type === 'gap_fill') return gapItem(item, ctx, n);
    if (type === 'order') return orderItem(item, ctx, n);
    if (item.options && item.options.length) return choiceItem(item, ctx, n);
    if (P.isEdit(item)) return editItem(item, ctx, n);
    return openItem(item, ctx, n);
  };

  /* An activity block: instructions + items; reports right/total to onScore. */
  P.renderActivity = function (act, opts) {
    opts = opts || {};
    const S = P.store.get();
    const wrap = el('section', { class: 'act' });
    const [stage, ...rest] = act.instructions.split(': ');
    wrap.appendChild(el('h3', null, el('span', { class: 'tag' }, stage), ' ', rest.join(': ')));
    let right = 0, answered = 0;
    const ctx = {
      showAnswers: S.settings.teacher && S.settings.showAnswers,
      result(ok) { answered++; if (ok) right++; if (opts.onScore) opts.onScore(act.id, right, answered, act.items.length); }
    };
    act.items.forEach((it, i) => wrap.appendChild(P.renderItem(it, act.type, ctx, i + 1)));
    return wrap;
  };

  /* ---------------------------------------------------------- quizzes and tests (submit, then score) */
  P.renderQuiz = function (items, opts) {
    opts = opts || {};
    const S = P.store.get();
    const wrap = el('div', { class: 'quiz' });
    const answers = new Array(items.length).fill(null);
    const blocks = [];
    let secs = (opts.minutes || 0) * 60, timerEl = null, iv = null;
    if (secs) {
      timerEl = el('div', { class: 'timer' });
      const tick = () => { const m = Math.floor(secs / 60), s = secs % 60; timerEl.textContent = '⏱ ' + m + ':' + P.pad(s); if (secs-- <= 0) { clearInterval(iv); submit(true); } };
      wrap.appendChild(el('div', { class: 'row' }, el('span', { class: 'sub' }, 'Time left:'), timerEl));
      tick(); iv = setInterval(tick, 1000);
    }
    let lastPart = null;
    items.forEach((it, i) => {
      if (it._part && it._part !== lastPart) {
        lastPart = it._part;
        wrap.appendChild(el('h2', null, it._part));
        if (it._part_ar) wrap.appendChild(P.ar(it._part_ar));
      }
      const box = el('div', { class: 'item' });
      box.appendChild(P.qText(it.q, i + 1, it.options && it.options.length ? null : 'Find and fix the mistake. Write the sentence correctly.'));
      if (it.options && it.options.length) {
        const long = it.options.some(o => o.length > 38);
        const opts2 = el('div', { class: 'opts' + (long ? ' col' : '') });
        it.options.forEach((o, k) => {
          const b = el('button', { class: 'opt', type: 'button' }, 'abcd'[k] + ') ' + o);
          b.onclick = () => { if (wrap.dataset.done) return; answers[i] = o; [...opts2.children].forEach(x => x.classList.remove('sel')); b.classList.add('sel'); };
          opts2.appendChild(b);
        });
        box.appendChild(opts2);
      } else {
        const ta = el('textarea', { rows: 2, spellcheck: 'false', 'aria-label': 'Corrected sentence' }, it.q);
        ta.oninput = () => { answers[i] = ta.value; };
        answers[i] = null;
        box.appendChild(ta);
      }
      if (S.settings.teacher && S.settings.showAnswers) box.appendChild(el('div', { class: 'sub' }, 'Key: ' + it.answer));
      blocks.push(box); wrap.appendChild(box);
    });
    let writing = null;
    if (opts.writing && opts.writing.task) {
      wrap.appendChild(el('h2', null, 'Writing (10 marks)'));
      wrap.appendChild(el('div', { class: 'box mint' }, opts.writing.task));
      if (opts.writing.task_ar) wrap.appendChild(P.ar(opts.writing.task_ar, 'box sky'));
      writing = el('textarea', { rows: 8, 'aria-label': 'Your writing' });
      wrap.appendChild(writing);
    }
    const res = el('div');
    const btn = el('button', { class: 'btn alt', type: 'button' }, opts.submitLabel || 'Submit and check');
    wrap.append(el('div', { class: 'row', style: { marginTop: '14px' } }, btn), res);
    btn.onclick = () => {
      const missing = answers.filter(a => a === null).length;
      if (!missing) return submit(false);
      P.ask(missing + ' question(s) are not answered. Submit anyway?', 'Submit', 'Keep working').then(ok => { if (ok) submit(true); });
    };
    function submit(timeUp) {
      if (wrap.dataset.done) return;
      wrap.dataset.done = '1'; if (iv) clearInterval(iv); btn.disabled = true;
      let score = 0;
      const detail = [];
      items.forEach((it, i) => {
        const a = answers[i];
        const ok = it.options && it.options.length ? a === it.answer : (a !== null && P.sameSentence(a, it.answer));
        if (ok) score++;
        detail.push({ ok, level: it.level, unit: it.unit, part: it._part || '' });
        const box = blocks[i];
        box.querySelectorAll('.opt').forEach(b => {
          const txt = b.textContent.slice(3);
          if (txt === it.answer) b.classList.add('ok'); else if (txt === a) b.classList.add('bad');
          b.disabled = true;
        });
        const ta = box.querySelector('textarea'); if (ta) ta.disabled = true;
        if (opts.feedback !== false) box.appendChild(P.feedback(ok, it));
      });
      const p = P.pct(score, items.length);
      res.appendChild(el('div', { class: 'panel', style: { marginTop: '12px' } },
        el('div', { class: 'score' }, 'Score: ' + score + ' / ' + items.length + '  ', el('span', { class: 'pill ' + P.band(p) }, p + '%')),
        opts.placement ? null : el('div', null, p >= 85 ? 'Excellent! You are secure in this content.' : p >= 65 ? 'Good progress. Review the questions you missed.' : 'Keep going – review the lessons, then try again.'),
        opts.placement || !S.settings.arabic ? null : P.ar(p >= 85 ? 'ممتاز! أنت متمكّن من هذا المحتوى.' : p >= 65 ? 'تقدّم جيد. راجع الأسئلة التي أخطأت فيها.' : 'استمر – راجع الدروس ثم حاول مرة أخرى.')));
      if (writing) {
        res.appendChild(el('div', { class: 'panel' }, el('h3', null, 'Writing – model answer'), el('div', { class: 'model' }, opts.writing.model || ''),
          el('div', { class: 'sub' }, 'Rubric (10): task & content 3 • target grammar 3 • vocabulary 2 • organization & mechanics 2. Your teacher marks your writing.')));
      }
      P.addXP(score * 2);
      if (opts.onSubmit) opts.onSubmit(score, items.length, detail, writing ? writing.value : '');
      res.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    return wrap;
  };
})();
