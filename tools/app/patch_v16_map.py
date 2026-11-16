"""v1.6.0: Language Usage material in the MAP Growth department — makes www/map.js subject-aware.
Run once:  python3 tools/app/patch_v16_map.py"""
import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = os.path.join(ROOT, 'www', 'map.js')
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, f'expected {n} x {a[:80]!r}, found {c}'
    s = s.replace(a, b)

# goal areas and per-subject wording
rep("""  const GOALS = { LT: ['Literary Text', 'النص الأدبي', '📖'], IT: ['Informational Text', 'النص المعلوماتي', '📰'], VO: ['Vocabulary', 'المفردات', '🔤'] };""",
"""  const GOALS = { LT: ['Literary Text', 'النص الأدبي', '📖'], IT: ['Informational Text', 'النص المعلوماتي', '📰'], VO: ['Vocabulary', 'المفردات', '🔤'],
    WR: ['Writing', 'الكتابة', '📝'], GU: ['Grammar and Usage', 'القواعد والاستخدام', '🧩'], ME: ['Mechanics', 'الترقيم والإملاء والحروف الكبيرة', '✏️'] };""")
rep("""    reading: { name: 'Reading', ar: 'القراءة', em: '📚', blurb: 'Literary Text, Informational Text and Vocabulary' },
    language: { name: 'Language Usage', ar: 'استخدام اللغة', em: '✍️', blurb: 'Writing, Grammar and Usage, and Mechanics' }
  };""",
"""    reading: { name: 'Reading', ar: 'القراءة', em: '📚', blurb: 'Literary Text, Informational Text and Vocabulary', goals: ['LT', 'IT', 'VO'],
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
  };""")
rep("""  /* ---------- data ---------- */""",
"""  const LHABITS = [
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

  /* ---------- data ---------- */""")
# breadcrumbs carry the subject
rep("""  const crumbsTo = (g, last) => [['Home', () => go('home')], ['MAP Growth', () => go('map')], [`Reading · Grade ${g}`, () => go('mapgrade', { mg: g })], [last]];""",
    """  const crumbsTo = (g, last, subj = cur()) => [['Home', () => go('home')], ['MAP Growth', () => go('map', { subj })], [`${SUBJ[subj].name} · Grade ${g}`, () => go('mapgrade', { mg: g, subj })], [last]];""")
# map home: about text
rep("""        <li>The <b>Reading</b> test reports three goal areas: Literary Text, Informational Text and Vocabulary. Every question here is labelled with its goal area, its skill and the RIT band where the skill appears.</li>""",
    """        <li>The <b>Reading</b> test reports three goal areas: Literary Text, Informational Text and Vocabulary. The <b>Language Usage</b> test reports Writing (revising a draft for its purpose and audience), Grammar and Usage, and Mechanics (capital letters, punctuation and spelling). Every question here is labelled with its goal area, its skill and the RIT band where the skill is usually learned.</li>""")
rep("""        <li>All passages and questions were written by Mr. Waleed Youssef for practice.""", """        <li>All passages, drafts and questions were written by Mr. Waleed Youssef for practice.""")
# grade page
rep("""    const g = S.mg, subj = 'reading';
    const d = needData(m, subj, g, () => V.mapgrade(m)); if (!d) return;
    const parts = [['Home', () => go('home')], ['MAP Growth', () => go('map')], [`Reading · Grade ${g}`]];""",
    """    const g = S.mg, subj = cur(), SJ = SUBJ[subj];
    const d = needData(m, subj, g, () => V.mapgrade(m)); if (!d) return;
    const parts = [['Home', () => go('home')], ['MAP Growth', () => go('map', { subj })], [`${SJ.name} · Grade ${g}`]];""")
rep("""<b>${esc((s.passage && s.passage.title) || 'Words in sentences')}</b>""", """<b>${esc((s.passage && s.passage.title) || SJ.noPass)}</b>""")
rep("""<section class="lhead" style="background:${COL[g][3]}"><span class="k">MAP Growth · Reading</span>""", """<section class="lhead" style="background:${COL[g][3]}"><span class="k">MAP Growth · ${SJ.name}</span>""")
rep("""    <details class="card mhab"><summary><b>💡 Smart reading habits</b> <span class="ar">عادات القراءة الذكية</span></summary><ol>${HABITS.map(""",
    """    <details class="card mhab"><summary><b>${SJ.habitsTitle[0]}</b> <span class="ar">${SJ.habitsTitle[1]}</span></summary><ol>${(subj === 'language' ? LHABITS : HABITS).map(""")
rep("""    <p class="muted" style="margin:-4px 0 12px">43 questions each: 15 Literary Text, 15 Informational Text and 13 Vocabulary, with six passages. No time limit; answers are saved as you go. <span class="ar">43 سؤالًا لكل اختبار، دون وقت محدد، وتُحفظ إجاباتك تلقائيًا.</span></p>""",
    """    <p class="muted" style="margin:-4px 0 12px">${SJ.mockLine[0]} <span class="ar">${SJ.mockLine[1]}</span></p>""")
rep("""go('mapset', { mg: g, mu: u, ms: s }); });
    $$('[data-mock]', m).forEach(b => b.onclick = () => go('mapmock', { mg: g, mk: b.dataset.mock }));""",
    """go('mapset', { mg: g, mu: u, ms: s, subj }); });
    $$('[data-mock]', m).forEach(b => b.onclick = () => go('mapmock', { mg: g, mk: b.dataset.mock, subj }));""")
# practice set
rep("""    const g = S.mg, subj = 'reading';
    const d = needData(m, subj, g, () => V.mapset(m)); if (!d) return;""", """    const g = S.mg, subj = cur(), SJ = SUBJ[subj];
    const d = needData(m, subj, g, () => V.mapset(m)); if (!d) return;""")
rep("""    if (!set) { go('mapgrade', { mg: g }); return; }""", """    if (!set) { go('mapgrade', { mg: g, subj }); return; }""")
rep("""<div class="card mwords"><b>🔑 Word box</b> <span class="ar">كلمات مهمة</span>""", """<div class="card mwords"><b>${SJ.words[0]}</b> <span class="ar">${SJ.words[1]}</span>""")
rep("""    <p class="instrline">Read the passage, then answer the questions. Press <b>Check answers</b> when you finish. <span class="ar ar-block">اقرأ النص ثم أجب عن الأسئلة، واضغط "تحقّق" عندما تنتهي.</span></p>""",
    """    <p class="instrline">${SJ.instr[0]} <span class="ar ar-block">${SJ.instr[1]}</span></p>""")
rep("""aria-label="Passage">${passageHTML(set.passage)}""", """aria-label="${SJ.pass}">${passageHTML(set.passage)}""")
rep("""${r >= .8 ? 'Excellent reading! 🎉' : r >= .5 ? 'Good work. Look at the questions you missed and find the proof in the text.' : 'Read the passage again and look for the sentence that proves each answer.'}""",
    """${r >= .8 ? SJ.fb[0] : r >= .5 ? SJ.fb[1] : SJ.fb[2]}""")
rep("""        const nx = $('#mNext', SC); if (nx) nx.onclick = () => go('mapset', Object.assign({ mg: g }, next));""",
    """        const nx = $('#mNext', SC); if (nx) nx.onclick = () => go('mapset', Object.assign({ mg: g, subj }, next));""")
rep("""    $('#mBack', m).onclick = () => go('mapgrade', { mg: g });
    $('#mChk', m).onclick""", """    $('#mBack', m).onclick = () => go('mapgrade', { mg: g, subj });
    $('#mChk', m).onclick""")
# mock exam
rep("""    const g = S.mg, subj = 'reading';
    const d = needData(m, subj, g, () => V.mapmock(m)); if (!d) return;
    const M = d.mocks.find(x => x.id === S.mk); if (!M) { go('mapgrade', { mg: g }); return; }""",
    """    const g = S.mg, subj = cur(), SJ = SUBJ[subj];
    const d = needData(m, subj, g, () => V.mapmock(m)); if (!d) return;
    const M = d.mocks.find(x => x.id === S.mk); if (!M) { go('mapgrade', { mg: g, subj }); return; }""")
rep("""<span class="k">Grade ${g} · MAP Growth Reading</span>""", """<span class="k">Grade ${g} · MAP Growth ${SJ.name}</span>""")
rep("""      const weak = Object.keys(GOALS).filter(k => gc[k])""", """      const weak = SJ.goals.filter(k => gc[k])""")
rep("""${r >= .8 ? 'Outstanding! You are reading at a high level for this test.' : r >= .6""", """${r >= .8 ? 'Outstanding! You are working at a high level for this test.' : r >= .6""")
rep("""        ${Object.entries(GOALS).filter(([k]) => gc[k]).map(([k, v]) =>""", """        ${SJ.goals.filter(k => gc[k]).map(k => [k, GOALS[k]]).map(([k, v]) =>""")
rep("""<summary><b>📄 ${esc(s.passage.title)}</b> <span class="muted">(open the passage)</span></summary>${passageHTML(s.passage)}</details>` : '<h3 style="margin:14px 0 8px">🔤 Vocabulary</h3>'}""",
    """<summary><b>📄 ${esc(s.passage.title)}</b> <span class="muted">(open the ${SJ.pass.toLowerCase()})</span></summary>${passageHTML(s.passage)}</details>` : `<h3 style="margin:14px 0 8px">${esc(secName(subj, s, si))}</h3>`}""")
rep("""      const again = () => { delete pr()[wid]; Store.save(); go('mapmock', { mg: g, mk: M.id, run: true }); };""",
    """      const again = () => { delete pr()[wid]; Store.save(); go('mapmock', { mg: g, mk: M.id, run: true, subj }); };""")
rep("""      $('#mBack', m).onclick = () => go('mapgrade', { mg: g });
      $$('[data-u]', m).forEach(b => b.onclick = () => go('mapset', { mg: g, mu: b.dataset.u, ms: 'A' }));""",
    """      $('#mBack', m).onclick = () => go('mapgrade', { mg: g, subj });
      $$('[data-u]', m).forEach(b => b.onclick = () => go('mapset', { mg: g, mu: b.dataset.u, ms: 'A', subj }));""")
rep("""        <ul class="mlist"><li><b>43 questions:</b> six passages and a vocabulary section — 15 Literary Text, 15 Informational Text and 13 Vocabulary questions.</li>
          <li><b>No time limit.</b> Most students need 50–70 minutes. Read carefully and look back at the passage.</li>""",
    """        <ul class="mlist"><li>${SJ.mockFirst}</li>
          <li>${SJ.mockTime}</li>""")
rep("""      $('#mGo', m).onclick = () => go('mapmock', { mg: g, mk: M.id, run: true });""", """      $('#mGo', m).onclick = () => go('mapmock', { mg: g, mk: M.id, run: true, subj });""")
rep("""() => { delete pr()[wid]; Store.save(); go('mapmock', { mg: g, mk: M.id, run: true }); }, 'Start again');""",
    """() => { delete pr()[wid]; Store.save(); go('mapmock', { mg: g, mk: M.id, run: true, subj }); }, 'Start again');""")
rep("""      const ls = $('#mLast', m); if (ls) ls.onclick = () => go('mapmock', { mg: g, mk: M.id, res: true });""",
    """      const ls = $('#mLast', m); if (ls) ls.onclick = () => go('mapmock', { mg: g, mk: M.id, res: true, subj });""")
rep("""data-s="${k}">${x.passage ? 'Passage ' + (k + 1) : '🔤 Vocabulary'}</button>`""", """data-s="${k}">${esc(secName(subj, x, k, true))}</button>`""")
rep("""aria-label="Passage">${passageHTML(s.passage)}""", """aria-label="${SJ.pass}">${passageHTML(s.passage)}""")
rep("""          go('mapmock', { mg: g, mk: M.id, res: true, resA: A, resSec: secs });""", """          go('mapmock', { mg: g, mk: M.id, res: true, resA: A, resSec: secs, subj });""")
# the floating button says "Draft" in Language Usage
rep("""  const fab = '<button class="mp-fab" id="mFab" hidden>📄 Passage</button>';""", """  const fab = '<button class="mp-fab" id="mFab" hidden>📄 <span class="fabt">Text</span></button>';""")
rep("""  function bindFab(m) {
    const b = $('#mFab', m), p = $('#mPass', m); if (!b || !p) return;""", """  function bindFab(m) {
    const b = $('#mFab', m), p = $('#mPass', m); if (!b || !p) return;
    const t = $('.fabt', b); if (t) t.textContent = SUBJ[cur()].pass;""")
# results CSV: Language Usage goal columns
rep("""Mock average %,Literary Text %,Informational Text %,Vocabulary %'];""", """Mock average %,Literary Text %,Informational Text %,Vocabulary %,Writing %,Grammar and Usage %,Mechanics %'];""")
rep("""s.mockAvg == null ? '' : pct(s.mockAvg), gp('LT'), gp('IT'), gp('VO')]""", """s.mockAvg == null ? '' : pct(s.mockAvg), gp('LT'), gp('IT'), gp('VO'), gp('WR'), gp('GU'), gp('ME')]""")
# home card
rep("""    const me = Store.me(), done = GRADES.reduce((a, g) => { const s = gradeSummary(me, 'reading', g); return a + s.sets + s.mocks; }, 0);""",
    """    const me = Store.me(), done = ['reading', 'language'].reduce((t, subj) => t + GRADES.reduce((a, g) => { const s = gradeSummary(me, subj, g); return a + s.sets + s.mocks; }, 0), 0);
    const lu = (IDX().language || []).length;""")
rep("""<span><b>Reading</b>: 6 practice units and 5 full mock exams of 43 questions for every grade, scored by goal area (Literary Text, Informational Text, Vocabulary). <b>Language Usage</b>: coming soon.</span>
      <span class="ar ar-block">التدريب على اختبار MAP Growth: وحدات تدريب واختبارات تجريبية كاملة في القراءة للصفوف 3–9، واستخدام اللغة قريبًا.</span></span>""",
    """<span><b>Reading</b> and <b>Language Usage</b>${lu ? '' : ' (coming soon)'}: 6 practice units and 5 full mock exams of 43 questions for every grade, scored by goal area.</span>
      <span class="ar ar-block">التدريب على اختبار MAP Growth: وحدات تدريب واختبارات تجريبية كاملة في القراءة واستخدام اللغة للصفوف 3–9.</span></span>""")
rep("""<span class="hud"><span>📚 7 grades</span>""", """<span class="hud"><span>📚 ${lu ? '2 subjects · ' : ''}7 grades</span>""")
# a question may hold several lines (the question, then the sentence it asks about)
rep("""<div class="q"><span class="num">${it.n}</span>${md(it.s)}</div>""", """<div class="q"><span class="num">${it.n}</span>${md(it.s).replace(/\\n/g, '<br>')}</div>""")
open(P, 'w', encoding='utf-8').write(s)
print('map.js patched for v1.6.0')
