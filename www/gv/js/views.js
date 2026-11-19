/* English Pathway Programme – screens and router.
   Routes: #/  #/s/<strand>  #/s/<strand>/L5  #/s/<strand>/L5/U3  #/s/<strand>/L5/U3/LS2[/tab]
           #/s/<strand>/L5/U3/test  #/s/<strand>/L5/U3/timed  #/s/<strand>/test/L05-MID  #/s/<strand>/placement
           #/cards  #/progress  #/teacher */
'use strict';
(function () {
  const P = window.Pathway, el = P.el;
  const app = () => document.getElementById('app');
  const LS_NAMES = { 1: 'Grammar discovery', 2: 'Grammar practice', 3: 'Vocabulary in depth', 4: 'Mechanics & editing', 5: 'Language in use & review' };
  const LS_AR = { 1: 'اكتشاف القاعدة', 2: 'تدريب على القاعدة', 3: 'المفردات بعمق', 4: 'الترقيم والتحرير', 5: 'استخدام اللغة والمراجعة' };
  const BANDS = [[8, 1], [14, 2], [19, 3], [24, 4], [29, 5], [34, 6], [39, 7], [44, 8], [49, 9], [53, 10], [57, 11], [60, 12]];

  /* ---------------------------------------------------------- data access */
  let strands = null;
  const idx = {};
  async function getStrands() { if (!strands) strands = await P.load('data/strands.json'); return strands; }
  async function getIndex(sid) {
    if (idx[sid]) return idx[sid];
    const st = (await getStrands()).find(s => s.id === sid);
    if (!st || !st.enabled) throw new Error('This strand module is not installed yet.');
    idx[sid] = await P.load(st.index); idx[sid]._base = st.index.replace(/index\.json$/, ''); idx[sid]._strand = st;
    return idx[sid];
  }
  async function getUnit(sid, lv, u) {
    const I = await getIndex(sid);
    const U = I.levels[lv - 1].units[u - 1];
    return P.load(I._base + U.file);
  }
  const lessonState = id => { const S = P.store.get(); return S.lessons[id] || (S.lessons[id] = { done: false, practice: {} }); };
  const levelDone = (I, lv) => I.levels[lv - 1].units.reduce((n, U) => n + U.lessons.filter(l => (P.store.get().lessons[l.id] || {}).done).length, 0);
  const unitDone = U => U.lessons.filter(l => (P.store.get().lessons[l.id] || {}).done).length;
  const bar = (a, b) => el('div', { class: 'bar' }, el('i', { style: { width: P.pct(a, b) + '%' } }));
  const crumbs = (...parts) => el('div', { class: 'crumbs' }, parts.map((p, i) => [i ? ' › ' : '', p[1] ? el('a', { href: p[1] }, p[0]) : p[0]]));
  const base = sid => '#/s/' + sid;

  function setFonts(lv) { document.body.classList.toggle('upper', lv >= 7); }

  /* ---------------------------------------------------------- home */
  async function home() {
    setFonts(0);
    const S = P.store.get(), list = (await getStrands()).filter(x => x.enabled);
    const view = el('div');
    view.appendChild(el('section', { class: 'hero' },
      el('h1', null, 'Language Usage'),
      el('p', null, 'Levels A1 to C2 • 72 units • 360 lessons'),
      P.ar('استخدام اللغة – من المستوى A1 إلى المستوى C2')));
    view.appendChild(el('section', { class: 'panel intro' }, el('span', { class: 'in-k' }, 'Introduction ', el('span', { class: 'ar', lang: 'ar' }, 'مقدمة')),
      el('p', null, 'This department gives you the rules and the words that every skill needs. Each lesson explains one point with clear examples in English and Arabic, then you practise it in activities and a game and finish with a short exit quiz. Take the Placement Test to find your level, or start at Level A1.'),
      P.ar('هذا القسم يعطيك القواعد والكلمات التي تحتاجها كل مهارة. كل درس يشرح نقطة واحدة بأمثلة واضحة بالإنجليزية والعربية، ثم تتدرّب عليها في أنشطة ولعبة وتنهي الدرس باختبار قصير. أدِّ اختبار تحديد المستوى لتعرف مستواك، أو ابدأ من المستوى A1.'),
      el('ul', { class: 'in-pts' }, ['12 steps from A1 to C2', '5 lessons in each unit', 'Word Cards for review'].map(x => el('li', null, x)))));
    if (!S.profile.name) {
      const n = el('input', { type: 'text', placeholder: 'Your name', 'aria-label': 'Your name' }), c = el('input', { type: 'text', placeholder: 'Class (e.g., 7B)', 'aria-label': 'Class' });
      view.appendChild(el('div', { class: 'panel' }, el('h3', null, 'Welcome! What is your name?'), P.ar('مرحبًا! ما اسمك؟'),
        el('div', { class: 'row' }, n, c, el('button', { class: 'btn alt', type: 'button', onclick: () => { S.profile.name = n.value.trim(); S.profile.cls = c.value.trim(); P.store.save(); route(); } }, 'Save'))));
    } else {
      view.appendChild(el('div', { class: 'row', style: { marginBottom: '12px' } }, el('b', null, 'Hello, ' + S.profile.name + '!'), el('span', { class: 'pill ok' }, '★ ' + (S.xp || 0) + ' XP'),
        S.placement ? el('span', { class: 'pill mid' }, 'Placement: ' + P.lv(S.placement.level)) : null));
    }
    const last = S.log.find(x => x.kind === 'lesson');
    if (last && last.detail && last.detail.href) view.appendChild(el('a', { class: 'btn', href: last.detail.href, style: { marginBottom: '14px' } }, '▶ Continue: ' + last.detail.title));
    view.appendChild(el('h2', null, 'Start here'));
    const g = el('div', { class: 'grid' });
    list.forEach(s => {
      const inner = [el('span', { class: 'tag' }, 'Levels A1 → C2'), el('div', { class: 'big' }, 'All levels and units'), P.ar(s.title_ar),
        el('div', { class: 'sub' }, s.enabled ? '12 levels • 72 units • 360 lessons' : 'Module not installed yet – it plugs in here.')];
      g.appendChild(s.enabled ? el('a', { class: 'card strand', href: base(s.id), style: { '--c': s.color } }, inner) : el('div', { class: 'card strand off', style: { '--c': s.color } }, inner));
    });
    view.appendChild(g);
    view.appendChild(el('h2', { style: { marginTop: '20px' } }, 'Quick start'));
    const due = P.srs.due().length;
    view.appendChild(el('div', { class: 'grid' },
      el('a', { class: 'card', href: base('grammar_vocabulary') + '/placement' }, el('div', { class: 'big' }, '🧭 Placement Test'), el('div', { class: 'sub' }, 'Language Usage • 60 questions • find your level'), P.ar('اختبار تحديد المستوى')),
      el('a', { class: 'card', href: '#/cards' }, el('div', { class: 'big' }, '🃏 Word Cards'), el('div', { class: 'sub' }, due + ' card(s) to review today'), P.ar('بطاقات المفردات')),
      el('a', { class: 'card', href: '#/progress' }, el('div', { class: 'big' }, '📈 My Progress'), el('div', { class: 'sub' }, 'Lessons, quizzes and tests'), P.ar('تقدّمي'))));
    return view;
  }

  /* ---------------------------------------------------------- strand: levels */
  async function strandView(sid) {
    setFonts(0);
    const I = await getIndex(sid), view = el('div');
    view.append(crumbs(['Home', '#/'], [I.title]),
      el('section', { class: 'hero' }, el('h1', null, I.title), el('p', null, 'Language Usage • MAP-style items at every level • SAT-style items from Level 8'), P.ar(I._strand.title_ar)));
    const g = el('div', { class: 'grid' });
    I.levels.forEach(L => {
      const d = levelDone(I, L.level);
      g.appendChild(el('a', { class: 'card', href: base(sid) + '/L' + L.level },
        el('span', { class: 'tag' }, 'Level'), el('div', { class: 'big' }, P.lvs(L.level)),
        el('div', { class: 'sub' }, L.units.map(u => u.theme).slice(0, 3).join(' • ') + ' …'), bar(d, 30), el('div', { class: 'sub' }, d + ' / 30 lessons')));
    });
    view.append(g, el('div', { class: 'row', style: { marginTop: '16px' } }, el('a', { class: 'btn alt', href: base(sid) + '/placement' }, '🧭 Placement Test')));
    return view;
  }

  /* ---------------------------------------------------------- level: units + tests */
  async function levelView(sid, lv) {
    setFonts(lv);
    const I = await getIndex(sid), L = I.levels[lv - 1], view = el('div'), S = P.store.get();
    view.append(crumbs(['Home', '#/'], [I.title, base(sid)], [P.lv(lv)]),
      el('h1', null, P.lv(lv)));
    const g = el('div', { class: 'grid' });
    const testCard = kind => {
      const key = 'L' + P.pad(lv) + '-' + kind, T = I.tests[key]; if (!T) return null;
      const r = S.tests[T.code];
      return el('a', { class: 'card', href: base(sid) + '/test/' + key, style: { borderTop: '6px solid var(--coral)' } },
        el('span', { class: 'tag' }, kind === 'MID' ? 'After Unit 3' : 'After Unit 6'), el('div', { class: 'big' }, kind === 'MID' ? '📝 Mid-Level Test' : '🏆 End-of-Level Test'),
        el('div', { class: 'sub' }, T.items + ' questions + writing • ' + (T.minutes || 45) + ' min'), r ? el('span', { class: 'pill ' + P.band(r.pct) }, 'Best ' + r.pct + '%') : null);
    };
    L.units.forEach(U => {
      const d = unitDone(U);
      g.appendChild(el('a', { class: 'card', href: base(sid) + '/L' + lv + '/U' + U.unit },
        el('span', { class: 'tag' }, 'Unit ' + U.unit), el('div', { class: 'big' }, U.theme), P.ar(U.theme_ar),
        el('div', { class: 'sub' }, U.eq), bar(d, 5), el('div', { class: 'sub' }, d + ' / 5 lessons • ' + U.words + ' words')));
      if (U.unit === 3) g.appendChild(testCard('MID'));
      if (U.unit === 6) g.appendChild(testCard('END'));
    });
    view.appendChild(g);
    return view;
  }

  /* ---------------------------------------------------------- unit */
  async function unitView(sid, lv, u) {
    setFonts(lv);
    const I = await getIndex(sid), J = await getUnit(sid, lv, u), S = P.store.get(), view = el('div');
    const href = base(sid) + '/L' + lv + '/U' + u;
    view.append(crumbs(['Home', '#/'], [I.title, base(sid)], [P.lv(lv), base(sid) + '/L' + lv], ['Unit ' + u]),
      el('section', { class: 'hero' }, el('h1', null, 'Unit ' + u + ': ' + J.theme), P.ar(J.theme_ar),
        el('p', null, el('b', null, 'Essential question: '), J.essential_question), P.ar(J.essential_question_ar)),
      J.can_do ? el('div', { class: 'box mint' }, el('b', null, 'I can… '), J.can_do.replace(/^I can /, ''), P.ar(J.can_do_ar)) : null);
    const g = el('div', { class: 'grid' });
    J.lessons.forEach((L, i) => {
      const st = S.lessons[L.id] || {};
      g.appendChild(el('a', { class: 'card', href: href + '/LS' + (i + 1) },
        el('span', { class: 'tag' }, 'LS' + (i + 1) + ' • ' + LS_NAMES[i + 1]), el('div', { class: 'big' }, L.title), P.ar(LS_AR[i + 1]),
        st.done ? el('span', { class: 'pill ' + P.band(P.pct(st.quiz, st.total)) }, '✓ Exit quiz ' + st.quiz + '/' + st.total) : el('div', { class: 'sub' }, '45 minutes')));
    });
    view.appendChild(g);
    const ut = S.tests[J.lessons[0].id.replace(/-LS1$/, '-TEST')];
    view.appendChild(el('div', { class: 'row', style: { marginTop: '16px' } },
      el('a', { class: 'btn', href: href + '/test' }, '📝 Unit Test (' + J.unit_test.length + ')'), ut ? el('span', { class: 'pill ' + P.band(ut.pct) }, 'Best ' + ut.pct + '%') : null,
      el('a', { class: 'btn alt', href: href + '/timed' }, '⏱ Timed Grammar Challenge'),
      el('button', { class: 'btn ghost', type: 'button', onclick: () => { let n = 0; J.lessons.forEach(L => L.vocabulary.forEach(w => { if (addCard(w, J, L)) n++; })); P.toast(n + ' new word card(s) added'); updateBadge(); } }, '🃏 Add unit words to my cards')));
    return view;
  }
  function addCard(w, J, L) {
    return P.srs.add({ word: w.word, pos: w.pos, ipa: w.ipa, definition: w.definition, arabic: w.arabic, example: w.example, audio: w.audio_id, src: L.id, theme: J.theme });
  }

  /* ---------------------------------------------------------- lesson */
  async function lessonView(sid, lv, u, n, tab) {
    setFonts(lv);
    const I = await getIndex(sid), J = await getUnit(sid, lv, u), L = J.lessons[n - 1], S = P.store.get(), st = lessonState(L.id);
    const href = base(sid) + '/L' + lv + '/U' + u + '/LS' + n;
    st.opened = Date.now(); P.store.save();
    P.log('lesson', L.id, { title: P.lv(lv) + ' Unit ' + u + ' – ' + L.title, href });
    const view = el('div');
    view.append(crumbs(['Home', '#/'], [I.title, base(sid)], [P.lv(lv), base(sid) + '/L' + lv], ['Unit ' + u, base(sid) + '/L' + lv + '/U' + u], ['LS' + n]),
      el('span', { class: 'tag' }, L.id + ' • ' + LS_NAMES[n]), el('h1', null, L.title));
    const tabs = [['learn', '📘 Learn'], ['video', '▶ Video'], ['practice', '✎ Practice'], ['game', '🎮 Game'], ['quiz', '✔ Exit Quiz']];
    tab = tabs.find(t => t[0] === tab) ? tab : 'learn';
    view.appendChild(el('div', { class: 'tabs', role: 'tablist' }, tabs.map(([k, t]) => el('button', { class: k === tab ? 'on' : '', role: 'tab', type: 'button', onclick: () => { location.hash = href + '/' + k; } }, t))));
    const body = el('div');
    view.appendChild(body);
    if (tab === 'learn') body.appendChild(learnTab(J, L));
    if (tab === 'video') body.appendChild(videoTab(L));
    if (tab === 'practice') {
      const p = el('div', { class: 'panel' });
      L.activities.forEach(a => p.appendChild(P.renderActivity(a, { onScore: (id, r, ans, tot) => { st.practice[id] = [r, ans, tot]; P.store.save(); if (ans === tot) { P.addXP(r); P.toast('Activity complete: ' + r + '/' + tot); } } })));
      body.appendChild(p);
    }
    if (tab === 'game') body.appendChild(el('div', { class: 'panel' }, P.renderGame(L.game, { lesson: L, lessons: J.lessons, unit: J })));
    if (tab === 'quiz') {
      const p = el('div', { class: 'panel' }, el('h2', null, 'Exit Quiz'), P.ar('الاختبار الختامي'),
        st.done ? el('p', { class: 'sub' }, 'Your best score: ' + (st.best || st.quiz) + ' / ' + st.total) : el('p', { class: 'sub' }, '10 questions. Choose the best answer, then press Submit.'));
      p.appendChild(P.renderQuiz(L.exit_quiz, {
        onSubmit: (score, total) => {
          st.done = true; st.quiz = score; st.total = total; st.best = Math.max(score, st.best || 0); st.ts = Date.now();
          S.quizzes[L.id] = { last: score, best: st.best, total, ts: Date.now(), attempts: ((S.quizzes[L.id] || {}).attempts || 0) + 1 };
          L.vocabulary.forEach(w => addCard(w, J, L)); P.store.save(); updateBadge();
          P.log('quiz', L.id, { score, total });
          const next = n < 5 ? href.replace(/LS\d$/, 'LS' + (n + 1)) : base(sid) + '/L' + lv + '/U' + u + '/test';
          p.appendChild(el('div', { class: 'row', style: { marginTop: '10px' } }, el('a', { class: 'btn', href: next }, n < 5 ? 'Next lesson →' : 'Unit Test →')));
        }
      }));
      body.appendChild(p);
    }
    const nav = el('div', { class: 'row', style: { marginTop: '14px' } },
      n > 1 ? el('a', { class: 'btn ghost sm', href: href.replace(/LS\d$/, 'LS' + (n - 1)) }, '← Previous lesson') : null, el('span', { class: 'spacer' }),
      n < 5 ? el('a', { class: 'btn ghost sm', href: href.replace(/LS\d$/, 'LS' + (n + 1)) }, 'Next lesson →') : null);
    view.appendChild(nav);
    return view;
  }

  function learnTab(J, L) {
    const S = P.store.get(), wrap = el('div');
    const obj = el('div', { class: 'panel' }, el('h2', null, '★ Objectives'), el('ul', null, L.objectives.map(o => el('li', null, o))));
    if (S.settings.arabic) obj.appendChild(el('ul', { class: 'ar', dir: 'rtl' }, L.objectives_ar.map(o => el('li', null, o))));
    wrap.appendChild(obj);
    if (L.vocabulary.length) {
      const v = el('div', { class: 'vocab' });
      L.vocabulary.forEach(w => v.appendChild(el('div', { class: 'word' },
        el('div', null, el('b', null, w.word), el('span', { class: 'pos' }, w.pos), ' ', P.sayBtn(w.word + '. ' + w.example, w.audio_id, 'Listen to ' + w.word)),
        el('div', { class: 'ipa' }, w.ipa), el('div', null, w.definition), P.ar(w.arabic), el('div', { class: 'sub' }, '“' + w.example + '”'))));
      wrap.appendChild(el('div', { class: 'panel' }, el('div', { class: 'row' }, el('h2', null, '● Vocabulary'), el('span', { class: 'spacer' }),
        el('button', { class: 'btn ghost sm', type: 'button', onclick: () => { let k = 0; L.vocabulary.forEach(w => { if (addCard(w, J, L)) k++; }); P.toast(k + ' card(s) added'); updateBadge(); } }, '🃏 Add to my cards')), v));
    }
    L.texts.forEach(t => wrap.appendChild(el('div', { class: 'panel' },
      el('div', { class: 'row' }, el('h2', null, t.title), el('span', { class: 'spacer' }), el('button', { class: 'btn ghost sm', type: 'button', onclick: () => P.play(t.audio_id, t.body) }, '🔊 Listen')),
      el('div', { class: 'pre', style: { fontSize: '1.05rem' } }, t.body))));
    const E = L.explanation;
    const ex = el('div', { class: 'panel' }, el('h2', null, '◆ Explanation'), el('div', { class: 'box mint pre' }, E.text));
    if (E.examples.length) ex.append(el('h3', null, 'Examples'), el('ul', { class: 'clean' }, E.examples.map(x => el('li', null, P.sayBtn(x), ' ', x))));
    if (E.common_errors.length) ex.appendChild(el('div', { class: 'box gold' }, el('b', null, '⚠ Common mistakes of Arab learners'), el('ul', { class: 'clean' }, E.common_errors.map(x => el('li', null, x)))));
    if (E.arabic) ex.appendChild(P.ar(E.arabic, 'box sky ar pre'));
    wrap.appendChild(ex);
    if (S.settings.teacher) {
      wrap.appendChild(el('details', { class: 'panel' }, el('summary', null, el('b', null, 'Teacher: image briefs and audio scripts')),
        el('ul', null, L.images.map(im => el('li', null, el('b', null, im.id + ': '), im.prompt))),
        el('ul', null, L.audio.slice(0, 40).map(a => el('li', null, el('b', null, a.id + ': '), a.script)))));
    }
    return wrap;
  }

  function videoTab(L) {
    const wrap = el('div', { class: 'panel' });
    const slot = el('div', { class: 'slot', hidden: true }, 'Video slot: add the file media/video/' + L.id + '.mp4 to show the video here. Until then, use the storyboard below or press “Play narration”.');
    const v = el('video', { controls: true, preload: 'metadata', src: 'media/video/' + L.id + '.mp4' });
    v.addEventListener('error', () => { v.hidden = true; slot.hidden = false; });
    wrap.append(el('h2', null, '▶ Video explanation with Zaki'), v, slot,
      el('div', { class: 'row', style: { margin: '10px 0' } },
        el('button', { class: 'btn alt sm', type: 'button', onclick: () => P.speak(L.video.script.map(s => s.narration).join(' ')) }, '🔊 Play narration'),
        el('button', { class: 'btn ghost sm', type: 'button', onclick: () => window.speechSynthesis && speechSynthesis.cancel() }, '■ Stop')));
    const ol = el('ol', { class: 'story' });
    L.video.script.forEach((s, i) => ol.appendChild(el('li', null, el('span', { class: 't' }, s.time), s.narration,
      s.on_screen ? el('div', { class: 'sub' }, 'On screen: ' + s.on_screen) : null,
      L.video.captions_ar && L.video.captions_ar[i] ? P.ar(typeof L.video.captions_ar[i] === 'string' ? L.video.captions_ar[i] : (L.video.captions_ar[i].text || '')) : null)));
    wrap.append(el('h3', null, 'Storyboard'), ol);
    return wrap;
  }

  /* ---------------------------------------------------------- unit test, timed challenge */
  async function unitTest(sid, lv, u) {
    setFonts(lv);
    const I = await getIndex(sid), J = await getUnit(sid, lv, u), S = P.store.get(), code = J.lessons[0].id.replace(/-LS1$/, '-TEST');
    const view = el('div');
    view.append(crumbs(['Home', '#/'], [I.title, base(sid)], [P.lv(lv), base(sid) + '/L' + lv], ['Unit ' + u, base(sid) + '/L' + lv + '/U' + u], ['Unit Test']),
      el('h1', null, 'Unit Test: ' + J.theme), P.ar('اختبار الوحدة'));
    const p = el('div', { class: 'panel' });
    p.appendChild(P.renderQuiz(J.unit_test, { onSubmit: (score, total) => { save(S, code, score, total, 'unit'); P.log('test', code, { score, total }); } }));
    view.appendChild(p);
    return view;
  }
  function save(S, code, score, total, kind, extra) {
    const pct = P.pct(score, total), old = S.tests[code];
    S.tests[code] = Object.assign({ score, total, pct: Math.max(pct, old ? old.pct : 0), last: pct, kind, ts: Date.now(), attempts: (old ? old.attempts : 0) + 1 }, extra || {});
    P.store.save();
  }
  async function timedView(sid, lv, u) {
    setFonts(lv);
    const I = await getIndex(sid), J = await getUnit(sid, lv, u), view = el('div');
    view.append(crumbs(['Home', '#/'], [I.title, base(sid)], [P.lv(lv), base(sid) + '/L' + lv], ['Unit ' + u, base(sid) + '/L' + lv + '/U' + u], ['Timed Challenge']),
      el('h1', null, '⏱ Timed Grammar Challenge'), el('p', { class: 'sub' }, 'Questions from the whole unit. Beat your best score!'));
    const game = { name: 'Unit ' + u + ' – ' + J.theme, mechanic: 'timed_quiz', rules: ['Play alone, in pairs, or as two teams on the projector.', 'Read each question quickly and choose the best answer.', 'A correct answer moves you on at once; a wrong answer shows the right one.'], data: [] };
    const all = { id: J.lessons[0].id.replace(/-LS1$/, ''), activities: [].concat(...J.lessons.map(l => l.activities)), exit_quiz: [].concat(...J.lessons.map(l => l.exit_quiz)) };
    view.appendChild(el('div', { class: 'panel' }, P.renderGame(game, { lesson: all, lessons: [], unit: J })));
    return view;
  }

  /* ---------------------------------------------------------- level tests and placement */
  async function levelTest(sid, key) {
    const I = await getIndex(sid), meta = I.tests[key];
    if (!meta) throw new Error('Test not found.');
    const T = await P.load(I._base + meta.file), S = P.store.get();
    setFonts(T.level);
    const view = el('div');
    const items = [].concat(...T.parts.map(p => p.items.map(it => Object.assign({ _part: p.name, _part_ar: p.name_ar }, it))));
    view.append(crumbs(['Home', '#/'], [I.title, base(sid)], T.level ? [P.lv(T.level), base(sid) + '/L' + T.level] : ['Placement'], [T.kind === 'mid' ? 'Mid-Level Test' : T.kind === 'end' ? 'End-of-Level Test' : 'Placement Test']),
      el('h1', null, T.title), el('p', { class: 'sub' }, items.length + ' questions' + (T.writing && T.writing.task ? ' + writing (10 marks)' : '') + ' • ' + (T.time_minutes || 45) + ' minutes'));
    const startBtn = el('button', { class: 'btn alt', type: 'button' }, 'Start the test');
    const timedChk = el('input', { type: 'checkbox', id: 'tm' });
    const intro = el('div', { class: 'panel' },
      el('p', null, 'Read each question carefully. For “Find and Fix”, rewrite the sentence correctly in the box.'),
      P.ar('اقرأ كل سؤال بعناية. في أسئلة «صحّح الخطأ» أعد كتابة الجملة صحيحة في المربع.'),
      el('label', null, timedChk, ' Use the timer (' + (T.time_minutes || 45) + ' minutes)'), el('div', { class: 'row', style: { marginTop: '10px' } }, startBtn));
    view.appendChild(intro);
    startBtn.onclick = () => {
      intro.remove();
      const p = el('div', { class: 'panel' });
      p.appendChild(P.renderQuiz(items, {
        minutes: timedChk.checked ? (T.time_minutes || 45) : 0, writing: T.writing, feedback: T.kind !== 'placement', placement: T.kind === 'placement',
        onSubmit: (score, total, detail, writingText) => {
          if (T.kind === 'placement') return placementResult(sid, p, score, total, detail);
          const byUnit = {};
          detail.forEach(d => { const k = 'Unit ' + d.unit; (byUnit[k] = byUnit[k] || [0, 0]); byUnit[k][1]++; if (d.ok) byUnit[k][0]++; });
          save(S, T.code, score, total, T.kind, { byUnit, writing: writingText ? writingText.slice(0, 2000) : '' });
          P.log('test', T.code, { score, total });
          const sk = el('div', { class: 'panel' }, el('h3', null, 'Skills map: review these units'));
          Object.entries(byUnit).forEach(([k, [a, b]]) => {
            const pc = P.pct(a, b), uu = k.split(' ')[1];
            sk.appendChild(el('div', { class: 'row' }, el('span', { class: 'pill ' + P.band(pc) }, pc + '%'), el('b', null, k + ': ' + a + '/' + b),
              pc < 65 ? el('a', { href: base(sid) + '/L' + T.level + '/U' + uu }, 'Review this unit →') : el('span', { class: 'sub' }, 'Secure')));
          });
          p.appendChild(sk);
        }
      }));
      view.appendChild(p);
    };
    return view;
  }
  function placementResult(sid, p, score, total, detail) {
    const S = P.store.get();
    let band = 1; for (const [max, lv] of BANDS) { if (score <= max) { band = lv; break; } }
    const per = {}; detail.forEach(d => { per[d.level] = per[d.level] || [0, 0]; per[d.level][1]++; if (d.ok) per[d.level][0]++; });
    let ceiling = null; for (let lv = 1; lv <= 12; lv++) if (per[lv] && per[lv][0] < 4) { ceiling = lv; break; }
    const rec = Math.min(band, ceiling || 12);
    S.placement = { score, total, band, ceiling, level: rec, ts: Date.now() }; P.store.save();
    P.log('placement', 'GV-PLACEMENT', { score, level: rec });
    p.appendChild(el('div', { class: 'panel', style: { borderTop: '6px solid var(--leaf)' } },
      el('h2', null, '🧭 Recommended start: Level ' + rec), P.ar('المستوى المقترح للبدء: ' + rec),
      el('p', null, 'Score ' + score + '/' + total + ' → score band Level ' + band + (ceiling ? '; first level with fewer than 4 of 5 correct: Level ' + ceiling : '') + '.'),
      el('p', { class: 'sub' }, 'Your teacher may adjust this after the first unit.'),
      el('a', { class: 'btn alt', href: base(sid) + '/L' + rec }, 'Go to Level ' + rec + ' →')));
  }

  /* ---------------------------------------------------------- word cards (spaced repetition) */
  async function cardsView() {
    setFonts(0);
    const S = P.store.get(), view = el('div');
    const all = Object.values(S.srs), due = P.srs.due();
    view.append(crumbs(['Home', '#/'], ['Word Cards']), el('h1', null, '🃏 My Word Cards'), P.ar('بطاقات المفردات – المراجعة المتباعدة'),
      el('p', { class: 'sub' }, 'Cards come back after 1, 3, 7, 16 and 35 days. Words are added when you finish a lesson\'s exit quiz, or with “Add to my cards”.'));
    const boxes = [0, 1, 2, 3, 4, 5].map(b => el('span', null, 'Box ' + b + ': ' + all.filter(c => c.box === b).length));
    view.appendChild(el('div', { class: 'boxes' }, boxes));
    const stage = el('div');
    view.appendChild(el('div', { class: 'row', style: { justifyContent: 'center', margin: '14px 0' } },
      el('button', { class: 'btn alt', type: 'button', disabled: !due.length, onclick: () => review(P.shuffle(due).slice(0, 20), stage) }, due.length ? 'Review ' + Math.min(20, due.length) + ' due card(s)' : 'No cards due – well done!'),
      el('button', { class: 'btn ghost', type: 'button', disabled: !all.length, onclick: () => review(P.shuffle(all).slice(0, 20), stage) }, 'Practice any 20')));
    view.appendChild(stage);
    if (all.length) {
      const q = el('input', { type: 'text', placeholder: 'Search my words…', 'aria-label': 'Search' });
      const list = el('div', { class: 'vocab', style: { marginTop: '10px' } });
      const draw = () => { list.innerHTML = ''; all.filter(c => c.word.toLowerCase().includes(q.value.toLowerCase())).sort((a, b) => a.word.localeCompare(b.word)).slice(0, 120).forEach(c => list.appendChild(el('div', { class: 'word' }, el('b', null, c.word), ' ', P.sayBtn(c.word, c.audio), el('div', null, c.definition), P.ar(c.arabic), el('div', { class: 'sub' }, 'Box ' + c.box + ' • ' + (c.theme || ''))))); };
      q.oninput = draw; draw();
      view.append(el('h2', null, 'All my words (' + all.length + ')'), q, list);
    }
    return view;
  }
  function review(cards, stage) {
    let i = 0, right = 0;
    const show = () => {
      stage.innerHTML = '';
      if (i >= cards.length) { stage.appendChild(el('div', { class: 'cue', style: { textAlign: 'center' } }, '🎉 Review finished: ' + right + ' / ' + cards.length + ' remembered.')); updateBadge(); return; }
      const c = cards[i];
      const card = el('div', { class: 'flash' }, el('div', { class: 'inner', onclick: () => card.classList.toggle('flip') },
        el('div', { class: 'face' }, el('div', { class: 'sub' }, (i + 1) + ' / ' + cards.length), el('div', { class: 'w' }, c.word), el('div', { class: 'sub' }, c.pos + ' ' + (c.ipa || '')), el('div', { class: 'sub' }, 'Tap to flip')),
        el('div', { class: 'face back' }, el('div', null, el('b', null, c.word), ': ' + c.definition), P.ar(c.arabic), el('div', { class: 'sub', style: { marginTop: '8px' } }, '“' + c.example + '”'))));
      const grade = q => { P.srs.grade(c.word, q); if (q) right++; i++; show(); };
      stage.append(card, el('div', { class: 'row', style: { justifyContent: 'center' } }, P.sayBtn(c.word + '. ' + c.example, c.audio),
        el('button', { class: 'btn warn', type: 'button', onclick: () => grade(0) }, 'Again'),
        el('button', { class: 'btn', type: 'button', onclick: () => grade(1) }, 'Good'),
        el('button', { class: 'btn alt', type: 'button', onclick: () => grade(2) }, 'Easy')));
    };
    show();
  }

  /* ---------------------------------------------------------- progress */
  function summary(S) {
    const lessons = Object.entries(S.lessons).filter(([, v]) => v.done);
    const qs = lessons.map(([, v]) => P.pct(v.quiz, v.total));
    const tests = Object.entries(S.tests);
    return {
      done: lessons.length, quizAvg: qs.length ? Math.round(qs.reduce((a, b) => a + b, 0) / qs.length) : null,
      unitTests: tests.filter(([, t]) => t.kind === 'unit'), levelTests: tests.filter(([, t]) => t.kind === 'mid' || t.kind === 'end'),
      weak: lessons.filter(([, v]) => P.pct(v.quiz, v.total) < 65).map(([k]) => k),
      last: S.log[0] ? new Date(S.log[0].ts).toLocaleString() : '—'
    };
  }
  async function progressView() {
    setFonts(0);
    const S = P.store.get(), view = el('div'), sm = summary(S);
    const n = el('input', { type: 'text', value: S.profile.name, 'aria-label': 'Name' }), c = el('input', { type: 'text', value: S.profile.cls, 'aria-label': 'Class' });
    view.append(crumbs(['Home', '#/'], ['My Progress']), el('h1', null, '📈 My Progress'),
      el('div', { class: 'panel' }, el('div', { class: 'row' }, 'Name', n, 'Class', c, el('button', { class: 'btn sm', type: 'button', onclick: () => { S.profile.name = n.value.trim(); S.profile.cls = c.value.trim(); P.store.save(); P.toast('Saved'); } }, 'Save')),
        el('p', null, el('span', { class: 'pill ok' }, '★ ' + (S.xp || 0) + ' XP'), '  Lessons completed: ', el('b', null, sm.done), '  •  Exit-quiz average: ', el('b', null, sm.quizAvg === null ? '—' : sm.quizAvg + '%'),
          S.placement ? ['  •  Placement: ', el('b', null, P.lv(S.placement.level))] : null)));
    try {
      const I = await getIndex('grammar_vocabulary');
      const g = el('div', { class: 'grid' });
      I.levels.forEach(L => { const d = levelDone(I, L.level); g.appendChild(el('a', { class: 'card', href: base('grammar_vocabulary') + '/L' + L.level }, el('b', null, P.lv(L.level)), bar(d, 30), el('div', { class: 'sub' }, d + ' / 30 lessons'))); });
      view.append(el('h2', null, 'Language Usage'), g);
    } catch (e) { /* strand not installed */ }
    const tl = el('ul', { class: 'clean' });
    Object.entries(S.tests).sort((a, b) => b[1].ts - a[1].ts).forEach(([k, t]) => tl.appendChild(el('li', null, el('span', { class: 'pill ' + P.band(t.pct) }, t.pct + '%'), ' ', k, ' – best of ' + t.attempts + ' attempt(s)')));
    view.append(el('h2', null, 'Tests'), Object.keys(S.tests).length ? tl : el('p', { class: 'sub' }, 'No tests yet.'));
    const lg = el('ul', { class: 'clean' });
    S.log.slice(0, 15).forEach(x => lg.appendChild(el('li', { class: 'sub' }, new Date(x.ts).toLocaleString() + ' – ' + x.kind + ' ' + x.id + (x.detail && x.detail.score !== undefined ? ' (' + x.detail.score + '/' + (x.detail.total || '') + ')' : ''))));
    view.append(el('h2', null, 'Recent activity'), lg);
    view.append(el('div', { class: 'panel' }, el('h3', null, 'Share or move my progress'),
      el('p', { class: 'sub' }, 'Download your progress file and send it to your teacher, or load it on another device.'),
      el('div', { class: 'row' }, el('button', { class: 'btn', type: 'button', onclick: exportMine }, '⬇ Download my progress'),
        fileBtn('⬆ Load a progress file', files => files[0].text().then(t => { const d = JSON.parse(t); if (!d.data) throw new Error(); return P.ask('Replace the progress on this device with this file?', 'Replace').then(ok => { if (ok) { P.store.mem = Object.assign(P.store.get(), d.data); P.store.save(); route(); } }); }).catch(() => P.toast('That file could not be read.'))))));
    return view;
  }
  function exportMine() {
    const S = P.store.get();
    const blob = new Blob([JSON.stringify({ app: 'English Pathway Programme', version: P.version, exported: new Date().toISOString(), data: S }, null, 1)], { type: 'application/json' });
    download(blob, 'progress-' + (S.profile.name || 'student').replace(/\W+/g, '_') + (S.profile.cls ? '-' + S.profile.cls.replace(/\W+/g, '_') : '') + '.json');
  }
  function download(blob, name) { const a = el('a', { href: URL.createObjectURL(blob), download: name }); document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function fileBtn(label, cb, multiple) {
    const inp = el('input', { type: 'file', accept: '.json,application/json', hidden: true, multiple: !!multiple });
    inp.onchange = () => { if (inp.files.length) cb([...inp.files]); inp.value = ''; };
    return el('span', null, inp, el('button', { class: 'btn ghost', type: 'button', onclick: () => inp.click() }, label));
  }

  /* ---------------------------------------------------------- teacher dashboard */
  let unlocked = false, roster = [];
  async function teacherView() {
    setFonts(0);
    const S = P.store.get(), view = el('div');
    view.append(crumbs(['Home', '#/'], ['Teacher']), el('h1', null, '👩‍🏫 Teacher Dashboard'), P.ar('لوحة المعلم'));
    if (P.host.role === 'teacher') unlocked = true;
    else if (P.host.locked) { view.appendChild(el('div', { class: 'panel' }, el('p', null, 'This page is for the teacher. Sign in to the app with the teacher account to open it.'), P.ar('هذه الصفحة للمعلم. سجّل الدخول بحساب المعلم لفتحها.'))); return view; }
    if (!unlocked) {
      const pin = el('input', { type: 'password', inputmode: 'numeric', placeholder: 'PIN', 'aria-label': 'Teacher PIN' });
      const go = () => { if (pin.value === S.settings.pin) { unlocked = true; route(); } else P.toast('Wrong PIN'); };
      pin.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
      view.appendChild(el('div', { class: 'panel' }, el('p', null, 'Enter the teacher PIN (first use: 1234 – change it below after you sign in).'), el('div', { class: 'row' }, pin, el('button', { class: 'btn', type: 'button', onclick: go }, 'Open'))));
      return view;
    }
    const tgl = (label, key) => { const c = el('input', { type: 'checkbox', checked: !!S.settings[key] }); c.onchange = () => { S.settings[key] = c.checked; P.store.save(); }; return el('label', { style: { display: 'block', margin: '4px 0' } }, c, ' ', label); };
    const newPin = el('input', { type: 'password', placeholder: 'New PIN', 'aria-label': 'New PIN' });
    view.appendChild(el('div', { class: 'panel' }, el('h2', null, 'Settings on this device'),
      tgl('Teacher view: show image briefs and audio scripts in lessons', 'teacher'),
      tgl('Show answer keys under questions (needs teacher view)', 'showAnswers'),
      tgl('Arabic support', 'arabic'),
      el('div', { class: 'row', style: { marginTop: '8px' } }, newPin, el('button', { class: 'btn sm', type: 'button', onclick: () => { if (newPin.value.length >= 4) { S.settings.pin = newPin.value; P.store.save(); P.toast('PIN changed'); newPin.value = ''; } else P.toast('Use at least 4 characters'); } }, 'Change PIN'),
        el('button', { class: 'btn warn sm', type: 'button', onclick: () => P.ask('Delete ALL progress on this device? This cannot be undone.', 'Delete everything').then(ok => { if (ok) { P.store.reset(); unlocked = false; route(); } }) }, 'Reset this device'))));
    // class results from imported student files
    const box = el('div', { class: 'panel' }, el('h2', null, 'Class results'),
      el('p', { class: 'sub' }, 'Students press “Download my progress” on the My Progress page and send you the file. Load all the files here to see the class (nothing is uploaded; files stay on this device).'),
      el('div', { class: 'row' }, fileBtn('⬆ Load student files', files => Promise.all(files.map(f => f.text().then(t => JSON.parse(t)).catch(() => null))).then(list => {
        list.filter(d => d && d.data).forEach(d => { roster = roster.filter(r => !(r.data.profile.name === d.data.profile.name && r.data.profile.cls === d.data.profile.cls)); roster.push(d); });
        route();
      }), true), el('button', { class: 'btn ghost', type: 'button', disabled: !roster.length, onclick: csv }, '⬇ Export CSV'), el('button', { class: 'btn ghost', type: 'button', disabled: !roster.length, onclick: () => { roster = []; route(); } }, 'Clear')));
    const rows = roster.length ? roster : [{ data: S, self: true }];
    const t = el('table', { class: 'list' }, el('thead', null, el('tr', null, ['Student', 'Class', 'Lessons', 'Exit quiz avg', 'Unit tests', 'Level tests', 'Placement', 'Lessons below 65%', 'Last active'].map(h => el('th', null, h)))));
    const tb = el('tbody');
    rows.forEach(r => {
      const d = r.data, sm = summary(d);
      tb.appendChild(el('tr', null, el('td', null, (d.profile.name || '(no name)') + (r.self ? ' – this device' : '')), el('td', null, d.profile.cls || ''), el('td', null, sm.done),
        el('td', null, sm.quizAvg === null ? '—' : el('span', { class: 'pill ' + P.band(sm.quizAvg) }, sm.quizAvg + '%')),
        el('td', null, sm.unitTests.length ? sm.unitTests.map(([k, x]) => k.replace('GV-', '').replace('-TEST', '') + ' ' + x.pct + '%').join(', ') : '—'),
        el('td', null, sm.levelTests.length ? sm.levelTests.map(([k, x]) => k.replace('GV-', '') + ' ' + x.pct + '%').join(', ') : '—'),
        el('td', null, d.placement ? P.lv(d.placement.level) + ' (' + d.placement.score + '/60)' : '—'),
        el('td', null, sm.weak.length ? sm.weak.map(x => x.replace('GV-', '')).join(', ') : '—'), el('td', null, sm.last)));
    });
    t.appendChild(tb);
    box.appendChild(el('div', { style: { overflowX: 'auto' } }, t));
    if (roster.length) {
      const weak = {};
      roster.forEach(r => summary(r.data).weak.forEach(id => { weak[id] = (weak[id] || 0) + 1; }));
      const top = Object.entries(weak).sort((a, b) => b[1] - a[1]).slice(0, 10);
      box.appendChild(el('div', { class: 'box gold' }, el('b', null, 'Reteach first (lessons where most students scored below 65%): '),
        top.length ? top.map(([k, v]) => k.replace('GV-', '') + ' (' + v + ')').join(' • ') : 'none – great work!'));
    }
    view.appendChild(box);
    view.appendChild(el('div', { class: 'panel' }, el('h2', null, 'Using the results'),
      el('ul', null, el('li', null, '85–100%: secure – continue.'), el('li', null, '65–84%: developing – reteach the skills with two or more wrong answers.'), el('li', null, 'Below 65%: needs support – repeat the exit quizzes and practice stages of the weakest units.')),
      P.ar('85–100%: متمكن • 65–84%: في طور النمو • أقل من 65%: يحتاج دعمًا')));
    return view;
  }
  function csv() {
    const head = ['Student', 'Class', 'Lessons completed', 'Exit quiz average %', 'Placement level', 'Placement score', 'Test', 'Test best %'];
    const lines = [head];
    roster.forEach(r => {
      const d = r.data, sm = summary(d);
      const baseRow = [d.profile.name, d.profile.cls, sm.done, sm.quizAvg === null ? '' : sm.quizAvg, d.placement ? d.placement.level : '', d.placement ? d.placement.score : ''];
      const tests = Object.entries(d.tests);
      if (!tests.length) lines.push(baseRow.concat(['', '']));
      tests.forEach(([k, t]) => lines.push(baseRow.concat([k, t.pct])));
    });
    const text = '﻿' + lines.map(l => l.map(v => '"' + String(v === undefined ? '' : v).replace(/"/g, '""') + '"').join(',')).join('\r\n');
    download(new Blob([text], { type: 'text/csv' }), 'class-results.csv');
  }

  /* ---------------------------------------------------------- router */
  function updateBadge() {
    const b = document.getElementById('dueBadge'); if (!b) return;
    const n = P.srs.due().length; b.textContent = n; b.hidden = !n;
  }
  P.updateBadge = updateBadge;
  async function route() {
    const h = (location.hash || '#/').slice(1).split('/').filter(Boolean);
    const main = app();
    document.querySelectorAll('[data-nav]').forEach(a => a.classList.toggle('on', a.dataset.nav === (h[0] === 's' ? 'home' : (h[0] || 'home'))));
    if (window.speechSynthesis) speechSynthesis.cancel();
    let view;
    try {
      if (!h.length) view = await home();
      else if (h[0] === 'cards') view = await cardsView();
      else if (h[0] === 'progress') view = await progressView();
      else if (h[0] === 'teacher') view = await teacherView();
      else if (h[0] === 's') {
        const sid = h[1], rest = h.slice(2);
        const num = s => parseInt(String(s).replace(/\D/g, ''), 10);
        if (!rest.length) view = await strandView(sid);
        else if (rest[0] === 'placement') view = await levelTest(sid, 'PLACEMENT');
        else if (rest[0] === 'test') view = await levelTest(sid, rest[1]);
        else if (rest.length === 1) view = await levelView(sid, num(rest[0]));
        else if (rest.length === 2) view = await unitView(sid, num(rest[0]), num(rest[1]));
        else if (rest[2] === 'test') view = await unitTest(sid, num(rest[0]), num(rest[1]));
        else if (rest[2] === 'timed') view = await timedView(sid, num(rest[0]), num(rest[1]));
        else view = await lessonView(sid, num(rest[0]), num(rest[1]), num(rest[2]), rest[3]);
      } else view = await home();
    } catch (e) {
      console.error(e);
      view = el('div', { class: 'panel' }, el('h2', null, 'Something went wrong'), el('p', null, String(e.message || e)),
        location.protocol === 'file:' ? el('p', { class: 'sub' }, 'Tip: keep the whole app folder together (index.html, js, css, data).') : null, el('a', { class: 'btn', href: '#/' }, 'Home'));
    }
    main.innerHTML = ''; main.appendChild(view);
    window.scrollTo(0, 0);
    updateBadge();
  }
  function applyArabic() {
    const S = P.store.get();
    document.body.classList.toggle('no-ar', !S.settings.arabic);
    const b = document.getElementById('arToggle'); if (b) b.classList.toggle('on', !!S.settings.arabic);
  }
  window.addEventListener('hashchange', route);
  window.addEventListener('DOMContentLoaded', () => {
    applyArabic();
    document.getElementById('arToggle').onclick = () => { const S = P.store.get(); S.settings.arabic = !S.settings.arabic; P.store.save(); applyArabic(); route(); };
    route();
  });
  P.route = route;
})();
