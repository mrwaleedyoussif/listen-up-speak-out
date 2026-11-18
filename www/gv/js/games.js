/* English Pathway Programme – lesson games. Each mechanic works on a projector (whole class, two teams) or on one device. */
'use strict';
(function () {
  const P = window.Pathway, el = P.el;

  function rulesBox(game) {
    const d = el('details', { class: 'box gold', style: { textAlign: 'left' } }, el('summary', null, el('b', null, 'How to play in class')));
    const ol = el('ol'); (game.rules || []).forEach(r => ol.appendChild(el('li', null, r))); d.appendChild(ol);
    return d;
  }
  function teams() {
    const sc = { A: 0, B: 0 };
    const a = el('span'), b = el('span');
    const draw = () => { a.textContent = 'Team A: ' + sc.A; b.textContent = 'Team B: ' + sc.B; };
    draw();
    const box = el('div', { class: 'teams' },
      el('div', { class: 't' }, a, ' ', el('button', { class: 'btn sm alt', type: 'button', onclick: () => { sc.A++; draw(); } }, '+1')),
      el('div', { class: 't' }, b, ' ', el('button', { class: 'btn sm alt', type: 'button', onclick: () => { sc.B++; draw(); } }, '+1')));
    return box;
  }
  /* Full sentences from the lesson's own items, for building and timed rounds. */
  P.sentencesFrom = function (lessons) {
    const out = [];
    lessons.forEach(L => {
      const items = [].concat(...L.activities.filter(a => a.type === 'mcq' || a.type === 'gap_fill').map(a => a.items), L.exit_quiz);
      items.forEach(it => {
        if (!it.q || it.q.includes('\n') || !/_{3,}/.test(it.q) || (it.q.match(/_{3,}/g) || []).length !== 1) return;
        const s = P.clean(it.q.replace(/_{3,}/, it.answer));
        const w = s.split(' ').length;
        if (w >= 4 && w <= 13 && !/[→•]/.test(s)) out.push(s);
      });
    });
    return [...new Set(out)];
  };
  P.mcqFrom = function (lessons, extra) {
    const out = [];
    lessons.forEach(L => {
      L.activities.filter(a => a.type === 'mcq').forEach(a => a.items.forEach(it => out.push(it)));
      L.exit_quiz.forEach(it => out.push(it));
    });
    (extra || []).forEach(it => out.push(it));
    return out.filter(it => it.options && it.options.length === 4);
  };

  /* ---------------------------------------------------------- spin the wheel */
  function spinWheel(game, ctx) {
    const labels = P.shuffle(game.data.map(d => d.label || d.cue || d.word)).slice(0, 12);
    const box = el('div', { class: 'game' });
    const cv = el('canvas', { width: 600, height: 600, 'aria-label': 'Spinning wheel' });
    const wrap = el('div', { class: 'wheel-wrap' }, el('div', { class: 'pointer' }), cv);
    const cue = el('div', { class: 'cue' }, 'Spin the wheel!');
    const colors = ['#2E3176', '#3FA66B', '#E06377', '#F0B232', '#2A90C5', '#7b5ea7'];
    let angle = 0;
    function draw() {
      const c = cv.getContext('2d'), n = labels.length, r = 290;
      c.clearRect(0, 0, 600, 600);
      labels.forEach((t, i) => {
        const a0 = angle + i * 2 * Math.PI / n, a1 = a0 + 2 * Math.PI / n;
        c.beginPath(); c.moveTo(300, 300); c.arc(300, 300, r, a0, a1); c.closePath();
        c.fillStyle = colors[i % colors.length]; c.fill(); c.strokeStyle = '#fff'; c.lineWidth = 4; c.stroke();
        c.save(); c.translate(300, 300); c.rotate(a0 + Math.PI / n); c.textAlign = 'right'; c.fillStyle = '#fff';
        c.font = 'bold ' + (t.length > 16 ? 20 : 26) + 'px Nunito, Arial'; c.fillText(t.length > 22 ? t.slice(0, 21) + '…' : t, r - 18, 9); c.restore();
      });
      c.beginPath(); c.arc(300, 300, 34, 0, 2 * Math.PI); c.fillStyle = '#fff'; c.fill();
    }
    draw();
    let spinning = false;
    const btn = el('button', { class: 'btn alt', type: 'button' }, 'Spin');
    btn.onclick = () => {
      if (spinning) return; spinning = true; cue.textContent = '…';
      const n = labels.length, pick = Math.floor(Math.random() * n);
      // pointer is at the top (−90°): bring the middle of slice `pick` there
      const target = -Math.PI / 2 - (pick + 0.5) * 2 * Math.PI / n;
      const start = angle, end = target - 2 * Math.PI * (5 + Math.ceil((start - target) / (2 * Math.PI)));
      const t0 = performance.now(), dur = 2600;
      const step = now => {
        const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        angle = start + (end - start) * e; draw();
        if (k < 1) requestAnimationFrame(step);
        else { spinning = false; cue.textContent = labels[pick]; P.speak(labels[pick]); }
      };
      requestAnimationFrame(step);
    };
    box.append(el('p', { class: 'sub' }, 'Spin, read the cue and make a correct sentence with today\'s grammar. Say it aloud or write it below.'),
      wrap, el('div', { class: 'row', style: { justifyContent: 'center' } }, btn), cue,
      el('textarea', { rows: 2, placeholder: 'Write your sentence here (optional)…' }), teams(), rulesBox(game));
    return box;
  }

  /* ---------------------------------------------------------- tic-tac-toe */
  function ticTacToe(game, ctx) {
    let cues = game.data.map(d => d.cue || d.label || d.word);
    while (cues.length < 9) cues = cues.concat(cues);
    cues = P.shuffle(cues).slice(0, 9);
    const box = el('div', { class: 'game' });
    const board = el('div', { class: 'ttt' });
    const status = el('div', { class: 'cue' });
    let turn = 'X', marks = Array(9).fill(''), over = false;
    const lines = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];
    const setStatus = () => { status.textContent = over ? status.textContent : 'Team ' + turn + ': choose a square.'; };
    function render() {
      board.innerHTML = '';
      cues.forEach((c, i) => {
        const b = el('button', { class: marks[i], type: 'button', disabled: !!marks[i] || over }, marks[i] || c);
        b.onclick = () => ask(i); board.appendChild(b);
      });
      setStatus();
    }
    function ask(i) {
      const m = el('div', { class: 'modal' }, el('div', { class: 'panel' },
        el('h3', null, 'Team ' + turn + ': make a sentence'), el('div', { class: 'cue' }, cues[i]),
        el('p', { class: 'sub' }, 'Say a correct sentence with the cue. The teacher (or the other team) decides.'),
        el('div', { class: 'row' },
          el('button', { class: 'btn alt', type: 'button', onclick: () => { marks[i] = turn; done(); } }, '✓ Correct'),
          el('button', { class: 'btn warn', type: 'button', onclick: () => done() }, '✗ Not correct'))));
      function done() {
        m.remove();
        const win = lines.find(l => l.every(k => marks[k] === turn));
        if (win) { over = true; status.textContent = '🎉 Team ' + turn + ' wins!'; }
        else if (marks.every(Boolean)) { over = true; status.textContent = 'It\'s a draw!'; }
        else turn = turn === 'X' ? 'O' : 'X';
        render();
      }
      document.body.appendChild(m);
    }
    render();
    box.append(status, board, el('button', { class: 'btn ghost sm', type: 'button', onclick: () => { marks = Array(9).fill(''); over = false; turn = 'X'; cues = P.shuffle(cues); render(); } }, 'New game'), rulesBox(game));
    return box;
  }

  /* ---------------------------------------------------------- sentence builder */
  function sentenceBuilder(game, ctx) {
    const pool = P.shuffle(P.sentencesFrom(ctx.lessons.length ? [ctx.lesson] : []).concat()).slice(0, 8);
    const sents = pool.length >= 4 ? pool : P.shuffle(P.sentencesFrom(ctx.lessons)).slice(0, 8);
    const box = el('div', { class: 'game' });
    let i = 0, right = 0;
    const stage = el('div');
    const info = el('div', { class: 'cue' });
    function next() {
      stage.innerHTML = '';
      if (i >= sents.length) { info.textContent = '🏁 You built ' + right + ' of ' + sents.length + ' sentences on the first try!'; P.addXP(right); return; }
      info.textContent = 'Sentence ' + (i + 1) + ' of ' + sents.length;
      const s = sents[i];
      const words = s.replace(/[.?!]$/, '').split(' ');
      const tiles = words.length > 9 ? words.reduce((acc, w, k) => { if (k % 2 === 0) acc.push(w); else acc[acc.length - 1] += ' ' + w; return acc; }, []) : words;
      stage.appendChild(P.orderBuilder(P.shuffle(tiles, i * 13 + 5), s.replace(/[.?!]$/, ''), ok => { if (ok) right++; i++; setTimeout(next, 1300); }));
    }
    next();
    const cues = el('details', { class: 'box sky', style: { textAlign: 'left' } }, el('summary', null, el('b', null, 'Speaking extension: cue cards')),
      el('ul', null, game.data.map(d => el('li', null, d.cue || d.label || d.word))));
    box.append(info, stage, cues, rulesBox(game));
    return box;
  }

  /* ---------------------------------------------------------- matching (word ↔ meaning / Arabic) */
  function matching(game, ctx) {
    const data = game.data.filter(d => d.word && (d.match || d.arabic));
    const box = el('div', { class: 'game' });
    let mode = 'match', round = 0, tries = 0, found = 0;
    const stage = el('div');
    const info = el('div', { class: 'cue' });
    const modeBtn = el('button', { class: 'chip', type: 'button' }, 'Match with Arabic');
    modeBtn.onclick = () => { mode = mode === 'match' ? 'arabic' : 'match'; modeBtn.textContent = mode === 'match' ? 'Match with Arabic' : 'Match with meanings'; round = 0; start(); };
    function start() {
      stage.innerHTML = ''; tries = 0; found = 0;
      const set = data.slice(round * 5, round * 5 + 5);
      if (!set.length) { round = 0; return start(); }
      info.textContent = 'Round ' + (round + 1) + ': tap a word, then its ' + (mode === 'match' ? 'meaning' : 'Arabic meaning') + '.';
      const left = el('div', { class: 'opts col' }), right = el('div', { class: 'opts col' });
      let sel = null;
      P.shuffle(set).forEach(d => left.appendChild(el('button', { class: 'opt', type: 'button', 'data-w': d.word, onclick: e => { left.querySelectorAll('.opt').forEach(x => x.classList.remove('sel')); sel = e.currentTarget; sel.classList.add('sel'); } }, d.word)));
      P.shuffle(set).forEach(d => {
        const b = el('button', { class: 'opt' + (mode === 'arabic' ? ' ar' : ''), type: 'button' }, mode === 'match' ? d.match : d.arabic);
        b.onclick = () => {
          if (!sel || b.disabled) return;
          tries++;
          if (sel.dataset.w === d.word) {
            sel.classList.remove('sel'); sel.classList.add('ok'); b.classList.add('ok'); sel.disabled = b.disabled = true; sel = null; found++; if (window.Cheer) Cheer.react(true, { lite: true });
            if (found === set.length) {
              info.textContent = '🎉 Round complete: ' + found + ' pairs in ' + tries + ' tries.'; P.addXP(found);
              stage.appendChild(el('div', { class: 'row', style: { justifyContent: 'center' } }, el('button', { class: 'btn alt', type: 'button', onclick: () => { round = (round + 1) % Math.ceil(data.length / 5); start(); } }, 'Next round')));
            }
          } else { b.classList.add('bad'); setTimeout(() => b.classList.remove('bad'), 600); if (window.Cheer) Cheer.react(false, { lite: true }); }
        };
        right.appendChild(b);
      });
      stage.appendChild(el('div', { class: 'pairs' }, left, right));
    }
    start();
    box.append(el('div', { class: 'row', style: { justifyContent: 'center' } }, modeBtn), info, stage, rulesBox(game));
    return box;
  }

  /* ---------------------------------------------------------- word builder (letter guessing) */
  function wordBuilder(game, ctx) {
    const words = P.shuffle(game.data.filter(d => d.word && /^[a-z' -]+$/i.test(d.word)));
    const box = el('div', { class: 'game' });
    let i = 0, guessed, wrong, solved = 0;
    const clue = el('div', { class: 'cue' }), blanks = el('div', { class: 'blanks' }), lives = el('div', { class: 'sub' }), keys = el('div', { class: 'letters' }), msg = el('div');
    function start() {
      guessed = new Set(); wrong = 0; msg.innerHTML = '';
      if (i >= words.length) { clue.textContent = '🏁 You solved ' + solved + ' of ' + words.length + ' words!'; blanks.textContent = ''; keys.innerHTML = ''; lives.textContent = ''; return; }
      clue.textContent = 'Clue: ' + (words[i].clue || words[i].match || '');
      keys.innerHTML = '';
      'abcdefghijklmnopqrstuvwxyz'.split('').forEach(ch => keys.appendChild(el('button', { type: 'button', onclick: e => guess(ch, e.currentTarget) }, ch)));
      draw();
    }
    function draw() {
      const w = words[i].word.toLowerCase();
      blanks.textContent = w.split('').map(c => /[a-z]/.test(c) ? (guessed.has(c) ? c : '_') : c).join('');
      lives.textContent = 'Wrong guesses left: ' + (6 - wrong);
    }
    function guess(ch, b) {
      const w = words[i].word.toLowerCase();
      b.disabled = true; guessed.add(ch);
      if (!w.includes(ch)) wrong++;
      draw();
      const won = w.split('').every(c => !/[a-z]/.test(c) || guessed.has(c));
      if (won || wrong >= 6) {
        keys.querySelectorAll('button').forEach(x => x.disabled = true);
        if (won) { solved++; P.addXP(1); }
        if (window.Cheer) Cheer.react(won);
        msg.appendChild(el('div', { class: 'fb ' + (won ? 'ok' : 'bad') }, (won ? '✓ Well done! ' : '✗ The word was: ') + words[i].word + '. ',
          P.sayBtn(words[i].word), ' ', el('button', { class: 'btn sm', type: 'button', onclick: () => { i++; start(); } }, 'Next word')));
      }
    }
    start();
    box.append(clue, blanks, lives, keys, msg, rulesBox(game));
    return box;
  }

  /* ---------------------------------------------------------- timed quiz */
  function timedQuiz(game, ctx) {
    const box = el('div', { class: 'game' });
    const pool = P.shuffle(P.mcqFrom([ctx.lesson]).concat(P.mcqFrom(ctx.lessons.filter(l => l !== ctx.lesson)).slice(0, 20)));
    const stage = el('div');
    const startBtn = el('button', { class: 'btn alt', type: 'button' }, 'Start 90-second challenge');
    startBtn.onclick = () => run(90);
    function run(secs) {
      startBtn.hidden = true;
      let k = 0, score = 0, left = secs;
      const timer = el('div', { class: 'timer' }), sc = el('div', { class: 'score' }), q = el('div');
      stage.innerHTML = ''; stage.append(el('div', { class: 'row', style: { justifyContent: 'center', gap: '24px' } }, timer, sc), q);
      const iv = setInterval(() => { left--; show(); if (left <= 0) end(); }, 1000);
      function show() { timer.textContent = '⏱ ' + left + 's'; sc.textContent = '★ ' + score; }
      function next() {
        if (k >= pool.length) return end();
        const it = pool[k++];
        q.innerHTML = '';
        q.appendChild(P.qText(it.q, k));
        const o = el('div', { class: 'opts', style: { justifyContent: 'center' } });
        it.options.forEach(op => o.appendChild(el('button', { class: 'opt', type: 'button', onclick: e => {
          const ok = op === it.answer; e.currentTarget.classList.add(ok ? 'ok' : 'bad'); if (ok) score++; if (window.Cheer) Cheer.react(ok, { lite: true });
          o.querySelectorAll('button').forEach(x => { x.disabled = true; if (x.textContent === it.answer) x.classList.add('ok'); });
          show(); setTimeout(next, ok ? 450 : 1200);
        } }, op)));
        q.appendChild(o);
      }
      function end() {
        clearInterval(iv); q.innerHTML = '';
        q.appendChild(el('div', { class: 'cue' }, '🏁 Time! You scored ' + score + ' in ' + secs + ' seconds.'));
        P.addXP(score); startBtn.hidden = false; startBtn.textContent = 'Play again';
        const S = P.store.get(), id = ctx.lesson.id + '-TIMED';
        S.quizzes[id] = { best: Math.max(score, (S.quizzes[id] || {}).best || 0), total: null, ts: Date.now(), kind: 'timed' }; P.store.save();
      }
      show(); next();
    }
    const tasks = el('details', { class: 'box sky', style: { textAlign: 'left' } }, el('summary', null, el('b', null, 'Classroom stations: cue words')),
      el('ul', null, game.data.map(d => el('li', null, (d.cue || d.word || d.label) + (d.tasks ? ' – ' + d.tasks.join(', ') : '')))));
    box.append(el('p', { class: 'sub' }, 'Answer as many questions as you can before time runs out.'), startBtn, stage, tasks, rulesBox(game));
    return box;
  }

  /* ---------------------------------------------------------- sort into groups (word family tree) */
  function dragDrop(game, ctx) {
    const data = P.shuffle(game.data.filter(d => d.word && d.category));
    const cats = [...new Set(data.map(d => d.category))];
    const box = el('div', { class: 'game' });
    const pool = el('div', { class: 'tiles' });
    const bins = el('div', { class: 'bins' });
    let sel = null, right = 0, placed = 0;
    const info = el('div', { class: 'cue' }, 'Tap a word, then tap its group (or drag it).');
    data.forEach(d => {
      const t = el('button', { class: 'tile', type: 'button', draggable: 'true' }, d.word);
      t._d = d;
      t.onclick = () => { pool.querySelectorAll('.tile').forEach(x => x.style.outline = ''); sel = t; t.style.outline = '3px solid var(--gold)'; };
      t.addEventListener('dragstart', e => { sel = t; e.dataTransfer.setData('text/plain', d.word); });
      pool.appendChild(t);
    });
    cats.forEach(c => {
      const b = el('div', { class: 'bin' }, el('h4', null, c));
      const drop = () => {
        if (!sel) return;
        const ok = sel._d.category === c;
        placed++; if (ok) right++;
        b.appendChild(el('span', { class: 'chipw' + (ok ? '' : ' bad'), title: ok ? 'Correct' : 'Should be: ' + sel._d.category }, (ok ? '✓ ' : '✗ ') + sel._d.word));
        sel.remove(); sel = null;
        if (placed === data.length) { info.textContent = '🎉 ' + right + ' of ' + data.length + ' words in the right group!'; P.addXP(right); }
      };
      b.addEventListener('click', drop);
      b.addEventListener('dragover', e => e.preventDefault());
      b.addEventListener('drop', e => { e.preventDefault(); drop(); });
      bins.appendChild(b);
    });
    const fams = [...new Set(data.map(d => d.family).filter(Boolean))];
    box.append(info, pool, bins, fams.length ? el('p', { class: 'sub' }, 'Word families: ' + fams.join(' • ')) : null, rulesBox(game));
    return box;
  }

  const builtIn = { spin_wheel: spinWheel, tic_tac_toe: ticTacToe, sentence_builder: sentenceBuilder, matching, word_builder: wordBuilder, timed_quiz: timedQuiz, drag_and_drop: dragDrop };
  P.renderGame = function (game, ctx) {
    const fn = P.gameMechanics[game.mechanic] || builtIn[game.mechanic];
    const wrap = el('div', null, el('h2', null, '🎮 ' + game.name));
    wrap.appendChild(fn ? fn(game, ctx) : el('div', { class: 'slot' }, 'This game type is played in class.', rulesBox(game)));
    return wrap;
  };
})();
