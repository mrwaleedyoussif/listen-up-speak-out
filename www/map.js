/* =====================================================================
   Listen Up! Speak Out! — MAP GROWTH DEPARTMENT
   Practice for the NWEA MAP Growth Reading and Language Usage tests, Grades 3–9:
   six practice units and five full mock exams (43 questions) per grade, scored by goal area.
   Content: www/map/<subject>_g<grade>.js (made by tools/app/build_map_data.py), loaded one grade at a time.
   All passages and questions are original practice material by Mr. Waleed Youssef; they are not NWEA items.
   Loaded before the main app script; the main script calls MAPX.register() before its first render,
   and these functions use the app's helpers (go, render, Store, VIEWS, esc …) only when they run.
   ===================================================================== */
'use strict';
const MAPX = (() => {
  const GRADES = [3, 4, 5, 6, 7, 8, 9];
  const COL = {
    3: ['#2F7BEA', '#E3EEFF', '#1B4FA3', 'linear-gradient(135deg,#4C9BFF,#2F7BEA)', '🎈'],
    4: ['#0E9C99', '#DCF5F3', '#08706E', 'linear-gradient(135deg,#2CC5BE,#0E9C99)', '🧭'],
    5: ['#2E9B4E', '#E2F5E7', '#1D6B34', 'linear-gradient(135deg,#55C26F,#2E9B4E)', '🔭'],
    6: ['#6A4CE0', '#ECE7FF', '#4630A8', 'linear-gradient(135deg,#8E72FF,#6A4CE0)', '🧩'],
    7: ['#E8590C', '#FFF0E6', '#A63C06', 'linear-gradient(135deg,#FF8A3D,#E8590C)', '🚀'],
    8: ['#C2255C', '#FCE8EF', '#8A1742', 'linear-gradient(135deg,#E64C80,#C2255C)', '🏛️'],
    9: ['#1D3F9E', '#E4EAFB', '#132B6E', 'linear-gradient(135deg,#3D63CC,#1D3F9E)', '🎓']
  };
  const GOALS = { LT: ['Literary Text', 'النص الأدبي', '📖'], IT: ['Informational Text', 'النص المعلوماتي', '📰'], VO: ['Vocabulary', 'المفردات', '🔤'],
    WR: ['Writing', 'الكتابة', '📝'], GU: ['Grammar and Usage', 'القواعد والاستخدام', '🧩'], ME: ['Mechanics', 'الترقيم والإملاء والحروف الكبيرة', '✏️'] };
  const SUBJ = {
    reading: { name: 'Reading', ar: 'القراءة', em: '📚', blurb: 'Literary Text, Informational Text and Vocabulary', goals: ['LT', 'IT', 'VO'],
      pass: 'Passage', passAr: 'النص', words: ['🔑 Word box', 'كلمات مهمة'], noPass: 'Words in sentences', secIcon: { VO: '🔤' },
      mockLine: ['43 questions each: 15 Literary Text, 15 Informational Text and 13 Vocabulary, with six passages. No time limit; answers are saved as you go.', '43 سؤالًا لكل اختبار، دون وقت محدد، وتُحفظ إجاباتك تلقائيًا.'],
      mockFirst: '<b>43 questions:</b> six passages and a vocabulary section — 15 Literary Text, 15 Informational Text and 13 Vocabulary questions.',
      mockTime: '<b>No time limit.</b> Most students need 50–70 minutes. Read carefully and look back at the passage.',
      instr: ['Read the passage, then answer the questions. Press <b>Check answers</b> when you finish.', 'اقرأ النص ثم أجب عن الأسئلة، واضغط "تحقّق" عندما تنتهي.'],
      fb: ['Excellent reading! 🎉', 'Good work. Look at the questions you missed and find the proof in the text.', 'Read the passage again and look for the sentence that proves each answer.'],
      habitsTitle: ['💡 Smart reading habits', 'عادات القراءة الذكية'] },
    language: { name: 'Language Usage', ar: 'استخدام اللغة', em: '✍️', blurb: 'Writing, Grammar and Usage, and Mechanics', goals: ['WR', 'GU', 'ME'],
      pass: 'Draft', passAr: 'المسودة', words: ['🔑 Key terms', 'مصطلحات مهمة'], noPass: 'Single sentences', secIcon: { WR: '📝', GU: '🧩', ME: '✏️' },
      mockLine: ['43 questions each: 15 Writing, 14 Grammar and Usage and 14 Mechanics — three student drafts, then three short sections of sentences. No time limit; answers are saved as you go.', '43 سؤالًا لكل اختبار: ثلاث مسودات ثم ثلاثة أقسام قصيرة، دون وقت محدد، وتُحفظ إجاباتك تلقائيًا.'],
      mockFirst: '<b>43 questions:</b> three student drafts with numbered sentences, then three short sections — 15 Writing, 14 Grammar and Usage and 14 Mechanics questions.',
      mockTime: '<b>No time limit.</b> Most students need 45–60 minutes. Read the whole draft, and read each answer choice back into the sentence.',
      instr: ['Read the draft (or each sentence), then answer the questions. Press <b>Check answers</b> when you finish.', 'اقرأ المسودة أو الجملة ثم أجب عن الأسئلة، واضغط "تحقّق" عندما تنتهي.'],
      fb: ['Excellent editing! 🎉', 'Good work. Look at the questions you missed and read each choice back into the sentence.', 'Read the draft again and test each answer choice in the sentence before you choose.'],
      habitsTitle: ['💡 Smart editing habits', 'عادات التحرير الذكية'] }
  };
  const NUMBERED = new Set(['story', 'informational', 'argument', 'persuasive', 'fable', 'folk tale', 'paired']);
  const LINES = new Set(['chart', 'timetable', 'schedule', 'menu', 'sign', 'label', 'poster', 'advertisement', 'announcement', 'map', 'public service announcement', 'how-to']);
  const L5 = ['A', 'B', 'C', 'D', 'E'];
  const HABITS = [
    ['Read the question first, so you know what to look for. Then read the whole passage carefully.', 'اقرأ السؤال أولًا لتعرف ما تبحث عنه، ثم اقرأ النص كاملًا بعناية.'],
    ['Every right answer can be proved with the text. Before you choose, find the sentence that proves it.', 'كل إجابة صحيحة يمكن إثباتها من النص. ابحث عن الجملة التي تثبتها قبل أن تختار.'],
    ['Read all the answer choices. Cross out the ones the text does not support, then choose the best one that is left.', 'اقرأ جميع الخيارات، واستبعد ما لا يدعمه النص، ثم اختر أفضل ما تبقّى.'],
    ['Look for key words in the question: NOT, BEST, MOST LIKELY, FIRST, LAST, BOTH.', 'انتبه للكلمات المهمة في السؤال مثل: NOT وBEST وMOST LIKELY.'],
    ['For a word question, read the whole sentence again and try each choice in the sentence.', 'في أسئلة المفردات، أعد قراءة الجملة كاملة وجرّب كل خيار فيها.'],
    ['Take your time. MAP Growth has no time limit; careful reading is worth more than finishing quickly.', 'خذ وقتك؛ اختبار MAP غير محدد بوقت، والقراءة المتأنية أهم من السرعة.']
  ];

  const LHABITS = [
    ['Read the whole draft once before you answer, so you know what the writer wants to say.', 'اقرأ المسودة كاملة مرة واحدة قبل الإجابة لتفهم ما يريد الكاتب قوله.'],
    ['When a question names a sentence number, find that sentence and read the sentences before and after it.', 'عندما يذكر السؤال رقم جملة، ابحث عنها واقرأ الجملة التي قبلها والتي بعدها.'],
    ['Read each answer choice back into the sentence. Choose the one that sounds right and follows the rule.', 'ضع كل خيار في الجملة واقرأها، واختر ما يبدو صحيحًا ويتبع القاعدة.'],
    ['For a BEST question, more than one choice may be possible. Choose the clearest one that fits the writer’s purpose.', 'في أسئلة BEST قد يصلح أكثر من خيار؛ اختر الأوضح والأنسب لهدف الكاتب.'],
    ['Look closely at small things: capital letters, commas, apostrophes, quotation marks, end marks and spelling.', 'انتبه للتفاصيل الصغيرة: الحروف الكبيرة والفواصل والفواصل العليا وعلامات التنصيص والإملاء.'],
    ['Take your time. MAP Growth has no time limit; careful reading is worth more than finishing quickly.', 'خذ وقتك؛ اختبار MAP غير محدد بوقت، والقراءة المتأنية أهم من السرعة.']
  ];
  const cur = () => (S.subj === 'language' ? 'language' : 'reading');
  /* section name in a mock exam: "Passage 2", "Draft 1", "🔤 Vocabulary", "🧩 Grammar and Usage" … */
  function secName(subj, s, k, short) {
    if (s.passage) return `${SUBJ[subj].pass} ${k + 1}`;
    const g = (s.items[0] || {}).g, ic = (SUBJ[subj].secIcon || {})[g] || '🔤';
    const lab = s.label || (GOALS[g] || ['Vocabulary'])[0];
    return `${ic} ${short ? lab.replace('Capitalization, Punctuation and Spelling', 'Mechanics') : lab}`;
  }

  /* printable copies: on the website they come from the same site; the apps open them in the browser */
  const PRN = () => window.MAP_PRINT || {};
  const WEB = () => (typeof PLAT === 'undefined' || PLAT === 'web');
  const prnURL = f => (WEB() ? '' : (typeof SITE !== 'undefined' ? SITE : 'https://mrwaleedyoussif.github.io/listen-up-speak-out/')) + 'print/map/' + f;
  const mb = b => (b >= 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(b / 1024)) + ' KB');
  function printHTML(subj, g) {
    const pr = PRN()[`${subj}_${g}`]; if (!pr) return '';
    const rows = [['booklet', '📘 Student booklet', 'كتيّب الطالب', '6 practice units · 78 questions'], ['mocks', '🎯 Mock exams A–E', 'الاختبارات التجريبية', '5 exams × 43 questions · answer sheets included']];
    return `<div class="section-title"><h2>🖨️ Print copies</h2></div>
    <p class="muted" style="margin:-4px 0 12px">Print the booklets for class or homework, or open them in Word to edit. Answer keys are in the teacher pack. An internet connection is needed. <span class="ar">نسخ للطباعة (PDF) أو للتعديل (Word)؛ يلزم الاتصال بالإنترنت.</span></p>
    <section class="grid mg2">${rows.filter(r => pr[r[0]]).map(([k, t, ar, sub]) => `<div class="card mprint"><b>${t}</b> <span class="ar">${ar}</span><span class="muted" style="font-size:.88rem">${sub}</span>
      <span class="mp-btns">${['pdf', 'docx'].filter(x => pr[k][x]).map(x => `<a class="btn sm ${x === 'pdf' ? 'band' : 'sec'}" href="${prnURL(pr[k][x].f)}" target="_blank" rel="noopener"${WEB() ? ` download="${pr[k][x].f}"` : ' data-ext="1"'}>⬇️ ${x === 'pdf' ? 'PDF' : 'Word'} <small>${mb(pr[k][x].b)}</small></a>`).join('')}</span></div>`).join('')}</section>`;
  }

  /* ---------- data ---------- */
  const IDX = () => window.MAP_INDEX || { reading: GRADES, language: [] };
  const has = (subj, g) => (IDX()[subj] || []).includes(g);
  const loading = {};
  function load(subj, g) {
    const k = subj + '_' + g, D = window.MAP_DATA || {};
    if (D[k]) return Promise.resolve(D[k]);
    if (!loading[k]) loading[k] = new Promise((ok, no) => {
      const s = document.createElement('script'); s.src = `map/${subj}_g${g}.js`; s.async = true;
      s.onload = () => { const d = (window.MAP_DATA || {})[k]; d ? ok(d) : no(new Error('empty')); };
      s.onerror = () => { delete loading[k]; s.remove(); no(new Error('missing')); };
      document.head.appendChild(s);
    });
    return loading[k];
  }
  const data = (subj, g) => (window.MAP_DATA || {})[subj + '_' + g] || null;

  /* ---------- helpers ---------- */
  const md = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\*(.+?)\*/g, '<i>$1</i>');
  const pct = r => Math.round(100 * r);
  const keyIdx = k => String(k).split(/\s*,\s*/).map(x => L5.indexOf(x.trim())).filter(x => x >= 0);
  const pkey = (subj, g, id) => `map${subj === 'reading' ? 'R' : 'L'}${g}_${id}`;
  const prog = (p, id) => ((p || Store.me()).progress || {})[id] || null;
  function band(g) { const c = COL[g] || COL[3], r = document.documentElement.style; r.setProperty('--c', c[0]); r.setProperty('--cl', c[1]); r.setProperty('--cd', c[2]); }
  function answered(it, a) { return it.t === 'ms' ? Array.isArray(a) && a.length === 2 : it.t === 'tp' ? !!a && a.a != null && a.b != null : a != null; }
  function right(it, a) {
    if (!answered(it, a)) return false;
    const k = keyIdx(it.k);
    if (it.t === 'ms') return a.length === k.length && k.every(x => a.includes(x));
    if (it.t === 'tp') return a.a === k[0] && a.b === keyIdx(it.pb.k)[0];
    return a === k[0];
  }
  const keyText = it => it.t === 'tp' ? `Part A ${it.k}, Part B ${it.pb.k}` : it.k.replace(/\s*,\s*/g, ' and ');

  function passageHTML(p) {
    if (!p) return '';
    const head = t => /^\*\*[^*]+\*\*$/.test(String(t).trim());
    let n = 0, h = `<h3 class="mp-t">${md(p.title)}</h3>`;
    if (p.intro) h += `<p class="mp-intro">${md(p.intro)}</p>`;
    if (p.poem) {
      const st = [[]]; p.paras.forEach(l => { if (!String(l).trim()) st.push([]); else st[st.length - 1].push(l); });
      return h + `<div class="mp-poem">${st.filter(x => x.length).map(x => `<p>${x.map(md).join('<br>')}</p>`).join('')}</div>`;
    }
    const lines = LINES.has(p.genre), num = NUMBERED.has(p.genre), drama = p.genre === 'drama';
    p.paras.forEach(t => {
      if (!String(t).trim()) return;
      if (head(t)) { h += `<h4 class="mp-h">${md(t.trim().slice(2, -2))}</h4>`; return; }
      if (lines && t.includes(' · ')) { h += `<ul class="mp-list">${t.split(' · ').map(x => `<li>${md(x)}</li>`).join('')}</ul>`; return; }
      let x = md(t);
      if (drama) x = x.replace(/^([A-Z][A-Z0-9 .’'\-]{1,28}):/, '<b class="mp-spk">$1:</b>');
      h += `<p class="${lines ? 'mp-line' : ''}">${num ? `<span class="mp-n">(${++n})</span> ` : ''}${x}</p>`;
    });
    return h;
  }

  function optsHTML(i, part, opts, chosen, keys, review) {
    const long = Math.max(...opts.map(o => String(o).length)) > 34;
    return `<div class="opts mopts ${long ? 'long' : ''}">${opts.map((o, j) => {
      const sel = chosen(j); let c = 'opt';
      if (sel) c += ' sel';
      if (review) { if (keys.includes(j)) c += ' right'; else if (sel) c += ' wrong'; }
      return `<button class="${c}" data-q="${i}" data-p="${part}" data-o="${j}" aria-pressed="${sel}"><span class="l">${L5[j]}</span><span class="ot">${md(o)}</span></button>`;
    }).join('')}</div>`;
  }
  function qHTML(it, i, a, review) {
    const ok = review && right(it, a);
    const g = GOALS[it.g] || null;
    let h = `<div class="task mq ${review ? (ok ? 'ok rv' : 'no rv') : ''}" id="mq${i}"><div class="q"><span class="num">${it.n}</span>${md(it.s).replace(/\n/g, '<br>')}</div>`;
    if (it.t === 'ms') h += `<div class="mhint">Choose <b>TWO</b> answers. <span class="ar">اختر إجابتين.</span></div>`;
    if (it.t === 'tp') {
      h += optsHTML(i, 'a', it.o, j => !!a && a.a === j, keyIdx(it.k), review);
      h += `<div class="q" style="margin-top:12px">Part B: ${md(it.pb.s)}</div>` + optsHTML(i, 'b', it.pb.o, j => !!a && a.b === j, keyIdx(it.pb.k), review);
    } else h += optsHTML(i, 'x', it.o, j => it.t === 'ms' ? Array.isArray(a) && a.includes(j) : a === j, keyIdx(it.k), review);
    if (review) h += `<div class="mfb">${ok ? '✅ Correct' : (answered(it, a) ? '❌ Not quite. ' : '⚪ Not answered. ') + (ok ? '' : `The answer is <b>${esc(keyText(it))}</b>.`)}<span class="msk">${g ? `<span class="pill">${g[2]} ${esc(g[0])}</span> ` : ''}${esc(it.sk)} · RIT ${esc(it.b)}</span></div>`;
    return h + '</div>';
  }
  /* Answer clicks update the stored answer and the buttons in place (no page re-render, so the scroll position stays). */
  function bindAnswers(root, items, A, onChange) {
    $$('.mq:not(.rv) [data-o]', root).forEach(b => b.onclick = () => {
      const i = +b.dataset.q, j = +b.dataset.o, part = b.dataset.p, it = items[i];
      if (it.t === 'ms') { let a = Array.isArray(A[i]) ? A[i].slice() : []; if (a.includes(j)) a = a.filter(x => x !== j); else { a.push(j); if (a.length > 2) a.shift(); } A[i] = a; }
      else if (it.t === 'tp') { A[i] = Object.assign({}, A[i] || {}, { [part]: j }); }
      else A[i] = j;
      const box = $('#mq' + i, root);
      $$('[data-o]', box).forEach(x => { const xp = x.dataset.p, xj = +x.dataset.o, a = A[i];
        const on = it.t === 'ms' ? a.includes(xj) : it.t === 'tp' ? a[xp] === xj : a === xj;
        x.classList.toggle('sel', on); x.setAttribute('aria-pressed', on); });
      onChange && onChange(i);
    });
  }
  const fab = '<button class="mp-fab" id="mFab" hidden>📄 <span class="fabt">Text</span></button>';
  function bindFab(m) {
    const b = $('#mFab', m), p = $('#mPass', m); if (!b || !p) return;
    const t = $('.fabt', b); if (t) t.textContent = SUBJ[cur()].pass;
    b.onclick = () => p.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (!('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver(es => es.forEach(e => { b.hidden = e.isIntersecting || window.innerWidth > 860; }), { threshold: 0 });
    io.observe(p);
  }
  const goalCount = (items, A) => {
    const r = {}; items.forEach((it, i) => { const g = it.g || 'X'; r[g] = r[g] || [0, 0]; r[g][1]++; if (right(it, A[i])) r[g][0]++; }); return r;
  };
  const crumbsTo = (g, last, subj = cur()) => [['Home', () => go('home')], ['MAP Growth', () => go('map', { subj })], [`${SUBJ[subj].name} · Grade ${g}`, () => go('mapgrade', { mg: g, subj })], [last]];
  const loadingHTML = '<div class="card" style="text-align:center;margin-top:16px"><div style="font-size:2.4rem">⏳</div><p>Loading the practice material… <span class="ar">جارٍ تحميل المادة…</span></p></div>';
  function needData(m, subj, g, again) {
    const d = data(subj, g); if (d) return d;
    m.innerHTML = loadingHTML; const v = S.view;
    load(subj, g).then(() => { if (S.view === v && S.mg === g && again) again(); }).catch(() => {
      m.innerHTML = `<div class="card" style="margin-top:16px"><h3>😕 The material could not be loaded</h3><p>Check the internet connection the first time you open a grade, then try again. <span class="ar ar-block">تحقق من الاتصال بالإنترنت عند فتح الصف أول مرة، ثم حاول مرة أخرى.</span></p><button class="btn" id="mRe">↻ Try again</button></div>`;
      $('#mRe', m).onclick = () => render();
    });
    return null;
  }

  /* ---------- progress summaries (also used by the teacher dashboard) ---------- */
  function gradeSummary(p, subj, g) {
    const pr = (p && p.progress) || {}, pre = pkey(subj, g, '');
    let sets = 0, setSum = 0, mocks = 0, mockSum = 0; const mk = {}, goals = {};
    Object.keys(pr).forEach(k => {
      if (!k.startsWith(pre) || k.includes('~')) return; const id = k.slice(pre.length), v = pr[k];
      if (/^U\d[AB]$/.test(id) && v.done) { sets++; setSum += v.best || 0; }
      if (/^M[A-E]$/.test(id) && v.done) { mocks++; mockSum += v.best || 0; mk[id[1]] = v.best || 0;
        Object.entries(v.bg || {}).forEach(([gk, cn]) => { goals[gk] = goals[gk] || [0, 0]; goals[gk][0] += cn[0]; goals[gk][1] += cn[1]; }); }
    });
    return { sets, setAvg: sets ? setSum / sets : null, mocks, mockAvg: mocks ? mockSum / mocks : null, mk, goals, any: sets + mocks > 0 };
  }

  /* =============== VIEWS (added to the app's views by register()) =============== */
  const V = {};
  V.map = m => {
    const subj = S.subj === 'language' ? 'language' : 'reading', me = Store.me();
    m.innerHTML = crumbs([['Home', () => go('home')], ['MAP Growth']]) + `
    <section class="lhead map-head"><span class="k">MAP Growth practice · Grades 3–9</span><h1>🎯 MAP Growth Practice</h1>
      <p style="margin:.3rem 0 0;opacity:.95">Practice units and full mock exams for the MAP Growth Reading and Language Usage tests, written to the MAP goal areas and RIT bands.</p>
      <span class="ar ar-block">تدريب على اختبار MAP Growth في القراءة واستخدام اللغة للصفوف من الثالث إلى التاسع.</span></section>
    <div class="mtabs" role="tablist">${Object.entries(SUBJ).map(([k, v]) => `<button role="tab" class="mtab ${k === subj ? 'on' : ''}" data-subj="${k}" aria-selected="${k === subj}">${v.em} ${v.name}<span class="ar">${v.ar}</span>${(IDX()[k] || []).length ? '' : '<small>Coming soon</small>'}</button>`).join('')}</div>
    <div id="mBody"></div>
    <section class="card" style="margin-top:18px"><h3>ℹ️ About MAP Growth and this practice</h3>
      <ul class="mlist">
        <li><b>MAP Growth</b> is a computer-adaptive test: each question gets easier or harder depending on the student’s answers. The result is a <b>RIT score</b>, which shows the student’s level on one scale for every grade.</li>
        <li>The <b>Reading</b> test reports three goal areas: Literary Text, Informational Text and Vocabulary. The <b>Language Usage</b> test reports Writing (revising a draft for its purpose and audience), Grammar and Usage, and Mechanics (capital letters, punctuation and spelling). Every question here is labelled with its goal area, its skill and the RIT band where the skill is usually learned.</li>
        <li>A mock-exam score here is the <b>percentage of questions correct</b>. It is not a RIT score, and it does not predict an exact RIT score.</li>
        <li>All passages, drafts and questions were written by Mr. Waleed Youssef for practice. They are not NWEA test questions. MAP® and MAP Growth™ are trademarks of NWEA; this app is not made or endorsed by NWEA.</li>
      </ul>
      <span class="ar ar-block">نتيجة الاختبار التجريبي هي نسبة الإجابات الصحيحة وليست درجة RIT. جميع النصوص والأسئلة من إعداد أ. وليد يوسف للتدريب، وليست أسئلة NWEA.</span></section>`;
    bindCrumbs(m, [['Home', () => go('home')]]);
    $$('[data-subj]', m).forEach(b => b.onclick = () => { S.subj = b.dataset.subj; V.map(m); });
    const B = $('#mBody', m), avail = IDX()[subj] || [];
    if (subj === 'language' && !avail.length) {
      B.innerHTML = `<section class="card mcoming"><div class="mc-em">✍️</div><div><h3>Language Usage — coming soon</h3>
        <p>The Language Usage section is ready for its material. It will follow the same plan as Reading for Grades 3–9: practice units and five full mock exams per grade, scored by goal area:</p>
        <ul class="mlist"><li><b>Writing:</b> planning, organising and revising texts for a purpose and an audience.</li><li><b>Grammar and Usage:</b> parts of speech, sentence structure, verb tenses and agreement.</li><li><b>Mechanics:</b> capital letters, punctuation and spelling.</li></ul>
        <span class="ar ar-block">قسم استخدام اللغة جاهز لإضافة مادته، وسيتبع نظام قسم القراءة نفسه: وحدات تدريب وخمسة اختبارات تجريبية لكل صف.</span></div></section>
        <section class="grid g3" style="margin-top:14px">${GRADES.map(g => `<div class="gcard mgc off" style="background:${COL[g][3]}"><span class="em">${COL[g][4]}</span><span class="lv">Language Usage</span><h3>Grade ${g}</h3><span class="meta" style="margin-top:auto">Coming soon · قريبًا</span></div>`).join('')}</section>`;
      return;
    }
    B.innerHTML = `<div class="section-title"><h2>${SUBJ[subj].em} ${SUBJ[subj].name}: choose your grade</h2></div>
      <p class="muted" style="margin:-4px 0 12px">Each grade: 6 practice units (78 questions) and 5 mock exams of 43 questions. <span class="ar">لكل صف: 6 وحدات تدريب و5 اختبارات تجريبية.</span></p>
      <section class="grid g3">${GRADES.map(g => { const ok = avail.includes(g), s = gradeSummary(me, subj, g);
        return `<button class="gcard mgc ${ok ? '' : 'off'}" style="background:${COL[g][3]}" ${ok ? `data-mg="${g}"` : 'disabled'}>
          <span class="em">${COL[g][4]}</span><span class="lv">${SUBJ[subj].name}</span><h3>Grade ${g}</h3>
          <span style="font-weight:700;opacity:.95;margin:.2rem 0 .8rem">6 units · 5 mock exams</span>
          <span class="bar"><i style="width:${Math.round(100 * (s.sets + s.mocks) / 17)}%"></i></span>
          <span class="meta">${ok ? `${s.sets}/12 practice sets · ${s.mocks}/5 mocks${s.mockAvg != null ? ' · 🎯 ' + pct(s.mockAvg) + '%' : ''}` : 'Coming soon'}</span></button>`; }).join('')}</section>`;
    $$('[data-mg]', B).forEach(b => b.onclick = () => go('mapgrade', { mg: +b.dataset.mg, subj }));
  };

  V.mapgrade = m => {
    const g = S.mg, subj = cur(), SJ = SUBJ[subj];
    const d = needData(m, subj, g, () => V.mapgrade(m)); if (!d) return;
    const parts = [['Home', () => go('home')], ['MAP Growth', () => go('map', { subj })], [`${SJ.name} · Grade ${g}`]];
    const setRow = (u, s) => { const id = u.id + s.set, p = prog(null, pkey(subj, g, id)) || {};
      return `<button class="lrow ${p.done ? 'done' : ''}" data-set="${u.id}|${s.set}"><span class="ic">${s.set === 'A' ? '📝' : '🧠'}</span><span class="tx"><small>Practice ${s.set} · ${s.items.length} questions</small><b>${esc((s.passage && s.passage.title) || SJ.noPass)}</b></span>${p.done ? `<span class="mscore">${pct(p.best)}%</span>${starHTML(p.stars || 0)}` : '<span class="muted">Start →</span>'}</button>`; };
    m.innerHTML = crumbs(parts) + `
    <section class="lhead" style="background:${COL[g][3]}"><span class="k">MAP Growth · ${SJ.name}</span><h1>${COL[g][4]} Grade ${g}</h1>
      <p style="margin:.3rem 0 0;opacity:.95">6 practice units (78 questions) and 5 full mock exams (43 questions each), ordered from easier to harder.</p>
      <span class="ar ar-block">6 وحدات تدريب و5 اختبارات تجريبية كاملة، مرتبة من الأسهل إلى الأصعب.</span></section>
    <details class="card mhab"><summary><b>${SJ.habitsTitle[0]}</b> <span class="ar">${SJ.habitsTitle[1]}</span></summary><ol>${(subj === 'language' ? LHABITS : HABITS).map(h => `<li>${esc(h[0])}<span class="ar ar-block">${esc(h[1])}</span></li>`).join('')}</ol></details>
    <div class="section-title"><h2>📘 Practice units</h2></div>
    <section class="grid mg2">${d.units.map(u => { const G = GOALS[u.goal] || ['', '', '📘'];
      return `<div class="card munit"><div class="uh"><span class="ue">${G[2]}</span><div><span class="pill">${esc(u.id.replace('U', 'Unit '))} · ${esc(G[0] || u.goal)}</span><h3>${esc(u.title)}</h3><span class="muted" style="font-size:.85rem">RIT ${esc(u.band)}</span></div></div>
        <ul class="msk-list">${u.skills.slice(0, 4).map(s => `<li>${esc(s)}</li>`).join('')}</ul>${u.sets.map(s => setRow(u, s)).join('')}</div>`; }).join('')}</section>
    <div class="section-title"><h2>🎯 Mock exams</h2></div>
    <p class="muted" style="margin:-4px 0 12px">${SJ.mockLine[0]} <span class="ar">${SJ.mockLine[1]}</span></p>
    <section class="grid g3">${d.mocks.map(M => { const k = pkey(subj, g, 'M' + M.id), p = prog(null, k) || {}, w = prog(null, k + '~wip');
      const nA = w ? Object.keys(w.ans || {}).length : 0;
      return `<button class="card mmock ${p.done ? 'done' : ''}" data-mock="${M.id}"><span class="mm-id">${M.id}</span><b>Mock Exam ${M.id}</b><span class="muted" style="font-size:.88rem">${esc(M.note)}</span>
        <span class="mm-st">${p.done ? `Best <b>${pct(p.best)}%</b> ${starHTML(p.stars || 0)}` : ''}${w ? `<span class="pill">⏸ ${nA}/43 answered</span>` : (p.done ? '' : '<span class="muted">Start →</span>')}</span></button>`; }).join('')}</section>
    ${printHTML(subj, g)}`;
    bindCrumbs(m, parts);
    $$('a[data-ext]', m).forEach(a => a.onclick = e => { e.preventDefault(); if (typeof openExt === 'function') openExt(a.href); else window.open(a.href, '_blank'); });
    $$('[data-set]', m).forEach(b => b.onclick = () => { const [u, s] = b.dataset.set.split('|'); go('mapset', { mg: g, mu: u, ms: s, subj }); });
    $$('[data-mock]', m).forEach(b => b.onclick = () => go('mapmock', { mg: g, mk: b.dataset.mock, subj }));
  };

  /* ---------- practice set ---------- */
  V.mapset = m => {
    const g = S.mg, subj = cur(), SJ = SUBJ[subj];
    const d = needData(m, subj, g, () => V.mapset(m)); if (!d) return;
    const ui = d.units.findIndex(u => u.id === S.mu), u = d.units[ui], set = u && u.sets.find(s => s.set === S.ms);
    if (!set) { go('mapgrade', { mg: g, subj }); return; }
    const id = pkey(subj, g, u.id + set.set), items = set.items, G = GOALS[u.goal] || ['', '', ''];
    S.A = S.A || {};
    const parts = crumbsTo(g, `${u.id.replace('U', 'Unit ')} · Practice ${set.set}`);
    const next = (() => { const si = u.sets.indexOf(set); if (si < u.sets.length - 1) return { mu: u.id, ms: u.sets[si + 1].set }; const nu = d.units[ui + 1]; return nu ? { mu: nu.id, ms: nu.sets[0].set } : null; })();
    const best = prog(null, id);
    m.innerHTML = crumbs(parts) + `
    <section class="lhead"><span class="k">Grade ${g} · ${esc(u.id.replace('U', 'Unit '))} · Practice ${set.set} · ${esc(G[0])}</span><h1>${esc(u.title)}</h1>
      <p style="margin:.3rem 0 0;opacity:.95">${esc(u.skills.join(' · '))}</p></section>
    ${set.set === 'A' && u.vocab && u.vocab.length ? `<div class="card mwords"><b>${SJ.words[0]}</b> <span class="ar">${SJ.words[1]}</span><div class="mw">${u.vocab.map(v => `<span class="mwd"><b>${esc(v[0])}</b> — ${esc(v[1])}</span>`).join('')}</div></div>` : ''}
    <p class="instrline">${SJ.instr[0]} <span class="ar ar-block">${SJ.instr[1]}</span></p>
    <div id="mScore"></div>
    <div class="${set.passage ? 'mp-split' : ''}">${set.passage ? `<aside class="card mp-pass" id="mPass" tabindex="0" aria-label="${SJ.pass}">${passageHTML(set.passage)}</aside>` : ''}
      <div class="mp-qs"><div id="mQs"></div>
        <div class="navrow"><button class="btn sec" id="mBack">← Grade ${g}</button><button class="btn band" id="mChk">✔ Check answers</button></div></div></div>${set.passage ? fab : ''}`;
    bindCrumbs(m, parts); bindFab(m);
    const Q = $('#mQs', m), SC = $('#mScore', m);
    const paint = () => {
      const rv = !!S.chk;
      Q.innerHTML = items.map((it, i) => qHTML(it, i, S.A[i], rv)).join('');
      if (!rv) bindAnswers(Q, items, S.A, () => {});
      const chk = $('#mChk', m); chk.textContent = rv ? '↺ Try again' : '✔ Check answers';
      if (rv) {
        const sc = items.filter((it, i) => right(it, S.A[i])).length, r = sc / items.length;
        SC.innerHTML = `<div class="scorebox"><span class="big">${pct(r)}%</span>${starHTML(starsFor(r))}<span style="flex:1">${sc} of ${items.length} correct. ${r >= .8 ? SJ.fb[0] : r >= .5 ? SJ.fb[1] : SJ.fb[2]}${best && best.done ? `<br><small class="muted">Best before: ${pct(best.best)}%</small>` : ''}</span>
          ${next ? '<button class="btn band" id="mNext">Next practice →</button>' : ''}</div>`;
        const nx = $('#mNext', SC); if (nx) nx.onclick = () => go('mapset', Object.assign({ mg: g, subj }, next));
      } else SC.innerHTML = '';
    };
    paint();
    $('#mBack', m).onclick = () => go('mapgrade', { mg: g, subj });
    $('#mChk', m).onclick = () => {
      if (S.chk) { S.chk = false; S.A = {}; paint(); window.scrollTo({ top: 0 }); return; }
      const todo = items.filter((it, i) => !answered(it, S.A[i])).length;
      const doCheck = () => {
        S.chk = true; const sc = items.filter((it, i) => right(it, S.A[i])).length, r = sc / items.length;
        Store.rec(id, { stars: starsFor(r), best: r, done: true, last: r });
        paint(); RX.done(r, .9, .67, r === 1 ? ['Perfect score!', 'علامة كاملة!'] : null);
        SC.scrollIntoView({ behavior: 'smooth', block: 'start' });
      };
      if (todo) modal(`<h3>${todo} question${todo > 1 ? 's are' : ' is'} not answered</h3><p>Check your answers now anyway?</p><p class="ar ar-block">هناك أسئلة لم تُجب عنها. هل تريد التحقق الآن؟</p>`, doCheck, 'Check now'); else doCheck();
    };
  };

  /* ---------- mock exam ---------- */
  V.mapmock = m => {
    const g = S.mg, subj = cur(), SJ = SUBJ[subj];
    const d = needData(m, subj, g, () => V.mapmock(m)); if (!d) return;
    const M = d.mocks.find(x => x.id === S.mk); if (!M) { go('mapgrade', { mg: g, subj }); return; }
    const id = pkey(subj, g, 'M' + M.id), wid = id + '~wip', me = Store.me();
    const items = [], secOf = [];
    M.sections.forEach((s, si) => s.items.forEach(it => { items.push(it); secOf.push(si); }));
    const parts = crumbsTo(g, `Mock Exam ${M.id}`);
    const head = `<section class="lhead"><span class="k">Grade ${g} · MAP Growth ${SJ.name}</span><h1>🎯 Mock Exam ${M.id}</h1><p style="margin:.3rem 0 0;opacity:.95">${esc(M.note)}</p></section>`;
    const pr = () => { me.progress = me.progress || {}; return me.progress; };
    const wip = () => pr()[wid] || null;

    /* results */
    if (S.res) {
      const rec = prog(null, id) || {}, A = S.resA || rec.lastAns || {};
      const sc = items.filter((it, i) => right(it, A[i])).length, r = sc / items.length, gc = goalCount(items, A);
      const weak = SJ.goals.filter(k => gc[k]).sort((a, b) => gc[a][0] / gc[a][1] - gc[b][0] / gc[b][1])[0];
      const missed = [...new Set(items.filter((it, i) => !right(it, A[i])).map(it => it.sk))].slice(0, 8);
      const units = d.units.filter(u => u.goal === weak);
      const mins = Math.round((S.resSec != null ? S.resSec : rec.sec || 0) / 60);
      m.innerHTML = crumbs(parts) + head + `
      <div class="scorebox"><span class="big">${pct(r)}%</span>${starHTML(starsFor(r))}<span style="flex:1"><b>${sc} of ${items.length} correct</b>${mins ? ` · about ${mins} minutes` : ''}<br>${r >= .8 ? 'Outstanding! You are working at a high level for this test.' : r >= .6 ? 'Good result. Practise your weakest goal area to go higher.' : 'Keep going: practise the units below, then try again.'}<span class="ar ar-block">${r >= .8 ? 'نتيجة ممتازة!' : r >= .6 ? 'نتيجة جيدة، تدرّب على المجال الأضعف.' : 'استمر في التدريب ثم أعد المحاولة.'}</span></span>
        <button class="btn band" id="mAgain">↺ Take it again</button></div>
      <section class="card"><h3>📊 Results by goal area <span class="ar">النتائج حسب المجال</span></h3>
        ${SJ.goals.filter(k => gc[k]).map(k => [k, GOALS[k]]).map(([k, v]) => { const [c, n] = gc[k], rr = c / n; return `<div class="mgoal"><span class="mg-l">${v[2]} <b>${v[0]}</b><span class="ar">${v[1]}</span></span><span class="mg-bar"><i style="width:${pct(rr)}%;background:${rr >= .8 ? 'var(--ok)' : rr >= .6 ? 'var(--sun)' : 'var(--bad)'}"></i></span><span class="mg-n">${c}/${n} · ${pct(rr)}%</span></div>`; }).join('')}
        ${weak && gc[weak][0] < gc[weak][1] ? `<p style="margin:.8rem 0 0"><b>Practise next:</b> ${GOALS[weak][0]} — ${units.map(u => `<button class="linkbtn" data-u="${u.id}">${esc(u.id.replace('U', 'Unit '))}: ${esc(u.title)}</button>`).join(', ')}.</p>` : ''}
        ${missed.length ? `<p style="margin:.6rem 0 0"><b>Skills to work on:</b> ${missed.map(esc).join('; ')}.</p>` : ''}</section>
      <div class="section-title"><h2>🔍 Review your answers <span class="ar">راجع إجاباتك</span></h2></div>
      ${M.sections.map((s, si) => `<section class="mrev">${s.passage ? `<details class="card mp-det"><summary><b>📄 ${esc(s.passage.title)}</b> <span class="muted">(open the ${SJ.pass.toLowerCase()})</span></summary>${passageHTML(s.passage)}</details>` : `<h3 style="margin:14px 0 8px">${esc(secName(subj, s, si))}</h3>`}
        ${items.map((it, i) => secOf[i] === si ? qHTML(it, i, A[i], true) : '').join('')}</section>`).join('')}
      <div class="navrow"><button class="btn sec" id="mBack">← Grade ${g}</button><button class="btn band" id="mAgain2">↺ Take it again</button></div>`;
      bindCrumbs(m, parts);
      const again = () => { delete pr()[wid]; Store.save(); go('mapmock', { mg: g, mk: M.id, run: true, subj }); };
      $('#mAgain', m).onclick = again; $('#mAgain2', m).onclick = again;
      $('#mBack', m).onclick = () => go('mapgrade', { mg: g, subj });
      $$('[data-u]', m).forEach(b => b.onclick = () => go('mapset', { mg: g, mu: b.dataset.u, ms: 'A', subj }));
      return;
    }

    /* start screen */
    if (!S.run) {
      const w = wip(), rec = prog(null, id), nA = w ? Object.keys(w.ans || {}).length : 0;
      m.innerHTML = crumbs(parts) + head + `
      <section class="card mstart"><h3>Before you start <span class="ar">قبل أن تبدأ</span></h3>
        <ul class="mlist"><li>${SJ.mockFirst}</li>
          <li>${SJ.mockTime}</li>
          <li>Your answers are <b>saved as you go</b>. You can stop and come back later.</li>
          <li>Press <b>Finish</b> to see your score by goal area and review every question.</li></ul>
        <span class="ar ar-block">43 سؤالًا، دون وقت محدد. تُحفظ إجاباتك تلقائيًا، ويمكنك التوقف والعودة لاحقًا. اضغط "إنهاء" لترى نتيجتك.</span>
        ${rec && rec.done ? `<p style="margin:.8rem 0 0">Your best score: <b>${pct(rec.best)}%</b> ${starHTML(rec.stars || 0)} · <button class="linkbtn" id="mLast">see your last result</button></p>` : ''}
        <div class="ctrls" style="justify-content:flex-start;margin-top:14px">${w ? `<button class="btn band" id="mGo">▶ Continue (${nA}/43 answered)</button><button class="btn sec" id="mNew">↺ Start again</button>` : '<button class="btn band" id="mGo">▶ Start the mock exam</button>'}</div></section>`;
      bindCrumbs(m, parts);
      $('#mGo', m).onclick = () => go('mapmock', { mg: g, mk: M.id, run: true, subj });
      const nw = $('#mNew', m); if (nw) nw.onclick = () => modal('<h3>Start again?</h3><p>Your saved answers for this mock exam will be cleared.</p><p class="ar ar-block">ستُمسح إجاباتك المحفوظة لهذا الاختبار.</p>', () => { delete pr()[wid]; Store.save(); go('mapmock', { mg: g, mk: M.id, run: true, subj }); }, 'Start again');
      const ls = $('#mLast', m); if (ls) ls.onclick = () => go('mapmock', { mg: g, mk: M.id, res: true, subj });
      return;
    }

    /* the exam */
    const W = pr()[wid] = wip() || { ans: {}, sec: 0, cur: 0, t: Date.now() };
    const A = W.ans; let last = Date.now();
    const tick = () => { const n = Date.now(); W.sec += Math.min(n - last, 300000) / 1000; last = n; };
    const save = () => { tick(); Store.save(); };
    const nSec = M.sections.length;
    const draw = () => {
      const si = Math.min(W.cur || 0, nSec - 1), s = M.sections[si];
      const nA = items.filter((it, i) => answered(it, A[i])).length;
      m.innerHTML = crumbs(parts) + `
      <div class="mbar card"><div class="mbar-top"><b>Mock Exam ${M.id}</b><span class="muted">${nA}/43 answered</span><span style="flex:1"></span><button class="btn sm ok" id="mFin">🏁 Finish</button></div>
        <div class="mpal">${items.map((it, i) => `<button class="mpn ${answered(it, A[i]) ? 'a' : ''} ${secOf[i] === si ? 'cur' : ''}" data-j="${i}" aria-label="Question ${it.n}">${it.n}</button>`).join('')}</div>
        <div class="msecs">${M.sections.map((x, k) => `<button class="mtab sm ${k === si ? 'on' : ''}" data-s="${k}">${esc(secName(subj, x, k, true))}</button>`).join('')}</div></div>
      <div class="${s.passage ? 'mp-split' : ''}">${s.passage ? `<aside class="card mp-pass" id="mPass" tabindex="0" aria-label="${SJ.pass}">${passageHTML(s.passage)}</aside>` : ''}
        <div class="mp-qs">${s.passage ? '' : '<p class="instrline">Read each question carefully and choose the best answer. <span class="ar ar-block">اقرأ كل سؤال بعناية واختر أفضل إجابة.</span></p>'}<div id="mQs">${items.map((it, i) => secOf[i] === si ? qHTML(it, i, A[i], false) : '').join('')}</div>
        <div class="navrow"><button class="btn sec" id="mPrev" ${si === 0 ? 'disabled' : ''}>← Previous</button>${si < nSec - 1 ? '<button class="btn sec" id="mFin2">🏁 Finish</button><button class="btn band" id="mNx">Next →</button>' : '<button class="btn ok" id="mFin2">🏁 Finish</button>'}</div></div></div>${s.passage ? fab : ''}`;
      bindCrumbs(m, parts); bindFab(m);
      bindAnswers($('#mQs', m), items, A, i => { save(); const b = $(`.mpn[data-j="${i}"]`, m); if (b) b.classList.toggle('a', answered(items[i], A[i])); $('.mbar-top .muted', m).textContent = `${items.filter((it, k) => answered(it, A[k])).length}/43 answered`; });
      const toSec = (k, j) => { W.cur = k; save(); draw(); const el = j != null && $('#mq' + j, m); if (el) el.scrollIntoView({ block: 'center' }); else window.scrollTo({ top: 0 }); };
      $$('[data-s]', m).forEach(b => b.onclick = () => toSec(+b.dataset.s));
      $$('[data-j]', m).forEach(b => b.onclick = () => { const j = +b.dataset.j; if (secOf[j] === si) { const el = $('#mq' + j, m); el && el.scrollIntoView({ behavior: 'smooth', block: 'center' }); } else toSec(secOf[j], j); });
      if ($('#mPrev', m)) $('#mPrev', m).onclick = () => toSec(si - 1);
      if ($('#mNx', m)) $('#mNx', m).onclick = () => toSec(si + 1);
      const fin = () => {
        const todo = items.filter((it, i) => !answered(it, A[i])).length;
        const done = () => {
          tick(); const sc = items.filter((it, i) => right(it, A[i])).length, r = sc / items.length, gc = goalCount(items, A);
          const old = prog(null, id) || {};
          const bg = !old.done || r >= (old.best || 0) ? gc : old.bg;
          Store.rec(id, { stars: starsFor(r), best: r, done: true, last: r, lastAns: JSON.parse(JSON.stringify(A)), goals: gc, bg, sec: Math.round(W.sec) });
          const secs = W.sec; delete pr()[wid]; Store.save();
          go('mapmock', { mg: g, mk: M.id, res: true, resA: A, resSec: secs, subj });
          RX.done(r, .85, .6, r >= .85 ? ['Outstanding result!', 'نتيجة رائعة!'] : null);
        };
        modal(`<h3>Finish the mock exam?</h3><p>You answered <b>${43 - todo} of 43</b> questions.${todo ? ` ${todo} question${todo > 1 ? 's are' : ' is'} not answered yet.` : ''}</p><p class="ar ar-block">أجبت عن ${43 - todo} من 43 سؤالًا. هل تريد إنهاء الاختبار؟</p>`, done, 'Finish');
      };
      $('#mFin', m).onclick = fin; if ($('#mFin2', m)) $('#mFin2', m).onclick = fin;
    };
    Store.save(); draw();
  };

  /* ---------- teacher dashboard ---------- */
  function dashRows(p) {
    return ['reading', 'language'].map(subj => GRADES.map(g => { const s = gradeSummary(p, subj, g); if (!s.any) return '';
      return `<div class="selfrow"><span><b>🎯 MAP ${SUBJ[subj].name} G${g}</b> · ${s.sets}/12 sets${s.setAvg != null ? ' (' + pct(s.setAvg) + '%)' : ''}</span><span>${Object.keys(s.mk).length ? 'Mocks: ' + Object.keys(s.mk).sort().map(k => `${k} ${pct(s.mk[k])}%`).join(' · ') : 'no mocks yet'}</span></div>`; }).join('')).join('');
  }
  function csv(profiles) {
    const L = ['Student,Class,Subject,Grade,Practice sets done (of 12),Practice average %,Mock A %,Mock B %,Mock C %,Mock D %,Mock E %,Mock average %,Literary Text %,Informational Text %,Vocabulary %,Writing %,Grammar and Usage %,Mechanics %'];
    profiles.forEach(p => ['reading', 'language'].forEach(subj => GRADES.forEach(g => { const s = gradeSummary(p, subj, g); if (!s.any) return;
      const gp = k => s.goals[k] && s.goals[k][1] ? pct(s.goals[k][0] / s.goals[k][1]) : '';
      L.push([p.name, p.cls || '', SUBJ[subj].name, g, s.sets, s.setAvg == null ? '' : pct(s.setAvg), ...'ABCDE'.split('').map(k => s.mk[k] == null ? '' : pct(s.mk[k])), s.mockAvg == null ? '' : pct(s.mockAvg), gp('LT'), gp('IT'), gp('VO'), gp('WR'), gp('GU'), gp('ME')]
        .map(v => `"${String(v).replace(/"/g, '""')}"`).join(','));
    })));
    return L.length > 1 ? L.join('\n') : '';
  }
  /* home-page card */
  function homeCard() {
    const me = Store.me(), done = ['reading', 'language'].reduce((t, subj) => t + GRADES.reduce((a, g) => { const s = gradeSummary(me, subj, g); return a + s.sets + s.mocks; }, 0), 0);
    const lu = (IDX().language || []).length;
    return `<button class="card map-card" id="toMap"><span class="big">🎯</span><span style="flex:1"><h3 style="font-size:1.45rem">MAP Growth Practice · Grades 3–9</h3>
      <span><b>Reading</b> and <b>Language Usage</b>${lu ? '' : ' (coming soon)'}: 6 practice units and 5 full mock exams of 43 questions for every grade, scored by goal area.</span>
      <span class="ar ar-block">التدريب على اختبار MAP Growth: وحدات تدريب واختبارات تجريبية كاملة في القراءة واستخدام اللغة للصفوف 3–9.</span></span>
      <span class="hud"><span>📚 ${lu ? '2 subjects · ' : ''}7 grades</span><span>✅ ${done}</span></span></button>`;
  }

  const CSS = `
.map-card{display:flex;gap:18px;align-items:center;flex-wrap:wrap;background:linear-gradient(120deg,#EAF1FF,#fff 70%);border:2px solid #C9D9FF;text-align:left;width:100%}
.map-card .big{font-size:3rem}
.map-card .hud{display:flex;gap:8px;flex-wrap:wrap}
.map-card .hud span{background:#fff;border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-weight:800;font-size:.85rem}
.lhead.map-head{background:linear-gradient(120deg,#1D3F9E 0%,#6A4CE0 60%,#E8590C 130%)}
.mtabs{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 4px}
.mtab{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:14px;border:2px solid var(--line);background:#fff;font-weight:800}
.mtab .ar{font-size:.85em}
.mtab small{background:var(--sun);color:#5A3C00;border-radius:99px;padding:1px 8px;font-size:.72rem;font-weight:800}
.mtab.on{border-color:var(--c);background:var(--cl);color:var(--cd)}
.mtab.sm{padding:6px 11px;font-size:.85rem;border-radius:11px}
.mgc{min-height:160px}
.mgc.off{filter:grayscale(.55);opacity:.7;cursor:default}
.mcoming{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
.mcoming .mc-em{font-size:3rem}
.mcoming>div{flex:1 1 300px}
.mlist{margin:.4rem 0 0;padding-left:20px}
.mlist li{margin:.3rem 0}
.mhab{margin-top:14px}
.mhab summary{cursor:pointer;list-style:none}
.mhab summary::-webkit-details-marker{display:none}
.mhab summary::before{content:'▸ ';color:var(--c)}
.mhab[open] summary::before{content:'▾ '}
.mhab ol{margin:.6rem 0 0;padding-left:22px}
.mhab li{margin:.35rem 0}
.munit{display:flex;flex-direction:column;gap:10px}
.munit .uh{display:flex;gap:12px;align-items:center}
.munit .ue{width:50px;height:50px;border-radius:15px;background:var(--cl);display:grid;place-items:center;font-size:1.6rem;flex:none}
.munit h3{font-size:1.15rem;margin-top:3px}
.msk-list{margin:0;padding-left:18px;color:var(--ink2);font-size:.88rem}
.mscore{font-weight:800;color:var(--cd)}
.mmock{display:flex;flex-direction:column;gap:4px;text-align:left;border:2px solid transparent;position:relative;min-height:150px}
.mprint{display:flex;flex-direction:column;gap:4px}
.mprint .mp-btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.mprint .mp-btns small{font-weight:600;opacity:.8}
.mmock:hover{border-color:var(--c)}
.mmock.done{border-color:#BDE8D0}
.mmock .mm-id{position:absolute;right:14px;top:10px;font-family:var(--fh);font-size:2.4rem;font-weight:800;color:var(--cl);-webkit-text-stroke:1.5px var(--c)}
.mmock b{font-size:1.15rem}
.mm-st{margin-top:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.mwords{margin-top:14px}
.mw{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.mwd{background:var(--cl);border-radius:12px;padding:6px 11px;font-size:.92rem}
.mwd b{color:var(--cd)}
.instrline{margin:14px 0 10px;font-weight:700;color:var(--ink2)}
.mp-split{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:18px;align-items:start}
.mp-pass{scroll-margin-top:72px;position:sticky;top:76px;max-height:calc(100vh - 96px);overflow:auto;font-size:1.02rem;line-height:1.7;padding:22px 24px}
.mp-t{font-size:1.3rem;text-align:center;margin-bottom:10px}
.mp-intro{font-style:italic;color:var(--ink2)}
.mp-pass p,.mp-det p{margin:0 0 .75rem}
.mp-n{color:var(--muted);font-weight:700;font-size:.85em}
.mp-h{font-size:1.05rem;margin:.9rem 0 .5rem;color:var(--cd)}
.mp-list{margin:0 0 .8rem;padding-left:22px}
.mp-list li{margin:.15rem 0}
.mp-pass p.mp-line,.mp-det p.mp-line{margin:0 0 .3rem}
.mp-poem p{margin:0 0 1rem;padding-left:18px;border-left:3px solid var(--cl)}
.mp-spk{color:var(--cd)}
.mp-qs{min-width:0}
.mq .q{line-height:1.45}
.mopts .opt{flex:1 1 220px;align-items:flex-start}
.mopts.long .opt{flex-basis:100%}
.mg2{grid-template-columns:repeat(auto-fill,minmax(min(100%,430px),1fr))}
.mp-fab{position:fixed;right:16px;bottom:calc(18px + env(safe-area-inset-bottom,0px));z-index:15;background:var(--c);color:#fff;font-weight:800;padding:10px 16px;border-radius:999px;box-shadow:0 6px 18px rgba(29,36,51,.25)}
.mp-fab[hidden]{display:none}
.mopts .opt .l{flex:none;width:24px;height:24px;border-radius:7px;background:var(--cl);display:inline-grid;place-items:center;font-size:.85rem}
.mopts .opt.sel .l{background:var(--c);color:#fff}
.mopts .opt.right .l{background:var(--ok);color:#fff}
.mopts .opt.wrong .l{background:var(--bad);color:#fff}
.mq.rv .opts{pointer-events:none}
.mhint{font-size:.9rem;color:var(--cd);margin:-4px 0 8px;font-weight:700}
.mfb{margin-top:10px;font-weight:700;display:flex;flex-direction:column;gap:6px}
.msk{font-weight:400;font-size:.86rem;color:var(--ink2)}
.mgoal{display:grid;grid-template-columns:210px 1fr 118px;gap:12px;align-items:center;padding:10px 0;border-bottom:1px dashed var(--line)}
.mg-l .ar{display:block;font-size:.85em}
.mg-bar{height:14px;border-radius:99px;background:var(--line);overflow:hidden}
.mg-bar i{display:block;height:100%;border-radius:99px}
.mg-n{font-weight:800;white-space:nowrap;text-align:right}
.linkbtn{color:var(--cd);font-weight:800;text-decoration:underline;padding:0}
.mrev{margin-bottom:6px}
.mp-det{margin:14px 0 10px}
.mp-det summary{cursor:pointer}
.mp-det[open] summary{margin-bottom:10px}
.mbar{padding:12px 14px;margin:8px 0 14px}
.mbar-top{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.mpal{display:flex;flex-wrap:wrap;gap:4px;margin:10px 0}
.mpn{width:30px;height:30px;border-radius:8px;border:2px solid var(--line);background:#fff;font-weight:800;font-size:.8rem;color:var(--muted)}
.mpn.a{background:var(--c);border-color:var(--c);color:#fff}
.mpn.cur{box-shadow:0 0 0 2px var(--sun)}
.msecs{display:flex;gap:6px;flex-wrap:wrap}
@media (max-width:860px){
 .mp-split{grid-template-columns:1fr}
 .mp-pass{position:static;max-height:none}
 .mpal{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}
 .mpn{flex:none}
 .msecs{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}
 .msecs .mtab{flex:none}
}
@media (max-width:640px){
 .mp-pass{padding:16px}
 .mgoal{grid-template-columns:1fr auto}
 .mg-l{min-width:0}
 .mg-bar{grid-column:1/-1;order:3}
 .mpn{width:28px;height:28px}
}
@media print{.mbar,.mtabs{display:none}.mp-pass{position:static;max-height:none;box-shadow:none}}
`;

  function register() {
    Object.assign(VIEWS, V);
    if (!document.getElementById('mapCss')) { const st = document.createElement('style'); st.id = 'mapCss'; st.textContent = CSS; document.head.appendChild(st); }
  }
  const doneCount = () => { const me = Store.me(); return ['reading', 'language'].reduce((t, subj) => t + GRADES.reduce((a, g) => { const s = gradeSummary(me, subj, g); return a + s.sets + s.mocks; }, 0), 0); };
  return { register, band, load, dashRows, csv, homeCard, doneCount, GRADES };
})();
