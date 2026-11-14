// Listen Up! Speak Out! — Teacher's Book generator (docx-js)
// Spec: A4, 1.5 cm margins, Times New Roman 15 pt, bold questions, choices not bold and horizontal,
// no tables, Arabic support (RTL), page numbers.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Footer, Header, PageNumber,
  PageBreak, LevelFormat, TabStopType, BorderStyle, TableOfContents, ShadingType, ImageRun
} = require('docx');
const IMG = f => fs.readFileSync('/home/claude/brand/' + f);
const img = (f, w, h) => new ImageRun({ type: 'png', data: IMG(f), transformation: { width: w, height: h } });

const ROOT = '/home/claude/lsp';
const P = JSON.parse(fs.readFileSync(`${ROOT}/build/program.json`, 'utf8'));
const K = JSON.parse(fs.readFileSync(`${ROOT}/build/kagan.json`, 'utf8'));
const OUT = process.argv[2] || `${ROOT}/out/Listen_Up_Speak_Out_Teachers_Book.docx`;

const FONT = 'Times New Roman';
const SZ = 30; // 15 pt
const BANDC = { 3: '1B4FA3', 4: '08706E', 5: '1D6B34', 6: '4630A8' };
const BAND = { 3: 'Sky', 4: 'Ocean', 5: 'Forest', 6: 'Summit' };
const LET = ['a', 'b', 'c', 'd'];
const out = [];

// ---------- helpers ----------
const r = (text, o = {}) => new TextRun({ text, font: { ascii: FONT, hAnsi: FONT, cs: FONT }, size: o.size || SZ, sizeComplexScript: o.size || SZ, bold: o.bold, italics: o.italics, color: o.color, rightToLeft: o.rtl });
const para = (runs, o = {}) => new Paragraph({ children: Array.isArray(runs) ? runs : [runs], spacing: { after: o.after == null ? 100 : o.after, before: o.before || 0, line: 300 }, alignment: o.align, indent: o.indent, keepNext: o.keepNext, keepLines: o.keepLines, tabStops: o.tabs, bidirectional: o.rtl, border: o.border, shading: o.shading, numbering: o.numbering });
const p = (text, o = {}) => para(r(text, o), o);
const b = (text, o = {}) => para(r(text, { ...o, bold: true }), o);
const LAT = /[A-Za-z\/][A-Za-z0-9\/ '’\-…:ːˈɪʊəæʌɑɔɜθðʃʒŋ.?!]*[A-Za-z0-9\/ːɪʊəæʌɑɔɜθðʃʒŋ]/g;
const isoL = t => t.replace(LAT, m => '\u2066' + m + '\u2069');
const ar = (text, o = {}) => text ? para(r(isoL(text), { rtl: true, color: o.color || '333F55' }), { ...o, rtl: true, align: AlignmentType.START }) : null;
const h = (lvl, text, color) => new Paragraph({ heading: lvl, children: [new TextRun({ text, color, font: FONT })], keepNext: true });
const iso = t => '\u2067' + t + '\u2069';
const mixed = parts => para(parts.map(x => typeof x === 'string' ? r(x) : r(x.t, x)), {});
const bullet = (runs, lvl = 0) => para(Array.isArray(runs) ? runs : [r(runs)], { numbering: { reference: 'bul', level: lvl }, after: 60 });
const numbered = (text, ref) => para([r(text)], { numbering: { reference: ref, level: 0 }, after: 60 });
const pb = () => new Paragraph({ children: [new PageBreak()] });
const rule = color => para([r('')], { border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: color || 'C9D1E3', space: 1 } }, after: 160 });
const box = (lines, fill = 'FFF6E5') => lines.map((ln, i) => para(Array.isArray(ln) ? ln : [r(ln)], { shading: { type: ShadingType.CLEAR, fill, color: 'auto' }, after: i === lines.length - 1 ? 160 : 0, indent: { left: 120, right: 120 } }));
const push = (...xs) => xs.flat().forEach(x => x && out.push(x));
let numRefCount = 0; const numRefs = [];
const newNum = () => { const ref = 'num' + (++numRefCount); numRefs.push(ref); return ref; };
// horizontal choices: tabs at quarter widths of the 18 cm text width
const TABS = [0, 2550, 5100, 7650].map(pos => ({ type: TabStopType.LEFT, position: pos }));
const choiceLine = opts => {
  const runs = [];
  opts.forEach((o, j) => { if (j) runs.push(new TextRun({ text: '\t', font: FONT, size: SZ })); runs.push(r(`${LET[j]}) ${o}`)); });
  const long = opts.some(o => o.length + 3 > 17);
  if (!long) return [para(runs, { tabs: TABS, after: 140, indent: { left: 360 } })];
  // longer choices: two per line
  const mk = (i0) => { const rr = []; [i0, i0 + 1].forEach((j, k) => { if (k) rr.push(new TextRun({ text: '\t', font: FONT, size: SZ })); rr.push(r(`${LET[j]}) ${opts[j]}`)); }); return rr; };
  if (opts.some(o => o.length + 3 > 38)) return opts.map((o, j) => para([r(`${LET[j]}) ${o}`)], { indent: { left: 360 }, after: j === 3 ? 140 : 20 }));
  return [para(mk(0), { tabs: [{ type: TabStopType.LEFT, position: 0 }, { type: TabStopType.LEFT, position: 5100 }], indent: { left: 360 }, after: 20 }),
          para(mk(2), { tabs: [{ type: TabStopType.LEFT, position: 0 }, { type: TabStopType.LEFT, position: 5100 }], indent: { left: 360 }, after: 140 })];
};

// ---------- statistics for QA ----------
const stats = P.grades.map(G => {
  const mcq = []; const tf = []; let gaps = 0, orders = 0, words = 0, lines = 0;
  G.units.forEach(U => { U.listen.forEach(L => { L.tasks.forEach(t => { if (t.type === 'mcq') mcq.push(t.ans); if (t.type === 'tf') tf.push(t.ans); if (t.type === 'gap') gaps++; if (t.type === 'order') orders++; }); words += L.script.reduce((a, x) => a + x.text.split(' ').length, 0); lines += L.script.length; }); U.check.forEach(c => mcq.push(c.ans)); });
  return { g: G.grade, mcq, tf, gaps, orders, words, lines };
});
const manifest = JSON.parse(fs.readFileSync(`${ROOT}/build/manifest.json`, 'utf8'));

// ================= COVER =================
push(
  para([r('')], { after: 300 }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [img('emblem_600.png', 150, 150)] }),
  para([r('Listen Up! Speak Out!', { size: 72, bold: true, color: '1B4FA3' })], { align: AlignmentType.CENTER, after: 200 }),
  para([r('Elementary Listening & Speaking Program', { size: 40, color: 'E0502F', bold: true })], { align: AlignmentType.CENTER, after: 120 }),
  para([r("Teacher's Book", { size: 44, bold: true })], { align: AlignmentType.CENTER, after: 400 }),
  para([r('Grades 3–6  ·  CEFR A1 → A2+  ·  24 units', { size: 32 })], { align: AlignmentType.CENTER, after: 120 }),
  para([r('72 listening lessons · 48 speaking lessons · 2,181 audio clips', { size: 28, color: '4B5568' })], { align: AlignmentType.CENTER, after: 600 }),
  para([r('برنامج متكامل لتنمية مهارتي الاستماع والتحدث للمرحلة الابتدائية', { rtl: true, size: 32, color: '1B4FA3' })], { align: AlignmentType.CENTER, rtl: true, after: 120 }),
  para([r('دليل المعلم', { rtl: true, size: 32, bold: true })], { align: AlignmentType.CENTER, rtl: true, after: 500 }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [img('photo_circle.png', 128, 128)] }),
  para([r('Designed by Mr. Waleed Youssef', { size: 34, bold: true, color: '1D3F9E' })], { align: AlignmentType.CENTER, after: 40 }),
  para([r('English Teacher & Curriculum Designer', { size: 26, color: '4B5568' })], { align: AlignmentType.CENTER, after: 40 }),
  para([r('تصميم وإعداد: أ. وليد يوسف', { rtl: true, size: 28, color: '1D3F9E', bold: true })], { align: AlignmentType.CENTER, rtl: true }),
  pb(),
  // about the designer
  h(HeadingLevel.HEADING_1, 'About the Designer'),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [img('photo_circle.png', 170, 170), new TextRun({ text: '      ' }), img('seal_400.png', 140, 140)] }),
  para([r('Mr. Waleed Youssef', { size: 40, bold: true, color: '1D3F9E' })], { align: AlignmentType.CENTER, after: 60 }),
  para([r('English Teacher & Curriculum Designer', { size: 28, color: '4B5568' })], { align: AlignmentType.CENTER, after: 300 }),
  p('Mr. Waleed Youssef is an English language teacher, a trainer of STEP and IELTS candidates, and a curriculum and materials designer. He designed Listen Up! Speak Out! so that young learners listen with confidence and speak with joy: real voices, clear tasks, games, shadowing and full Arabic support, in one program that works on the classroom board, on tablets and phones, and at home.'),
  ar('الأستاذ وليد يوسف معلّم لغة إنجليزية، ومدرّب لاختبارَي STEP وIELTS، ومصمّم مناهج ومواد تعليمية. صمّم برنامج Listen Up! Speak Out! ليستمع المتعلّمون الصغار بثقة ويتحدّثوا بمتعة: أصوات حقيقية، ومهام واضحة، وألعاب، وتظليل، ودعم كامل باللغة العربية، في برنامج واحد يعمل على سبورة الفصل والأجهزة اللوحية والهواتف وفي المنزل.'),
  pb()
);

// ================= CONTENTS =================
push(h(HeadingLevel.HEADING_1, 'Contents'),
  p('Right-click the table below and choose "Update Field" if the page numbers do not appear.', { italics: true, color: '6B7280' }),
  new TableOfContents('Contents', { hyperlink: true, headingStyleRange: '1-2' }),
  para([r('')], { after: 200 }),
  b('At a glance', { keepNext: true }),
  bullet('Part A. About the Program — overview, levels, design principles'),
  bullet('Part B. Using the Platform and the Audio — lesson steps, games, recording, dashboard, ElevenLabs'),
  bullet('Part C. Kagan Cooperative Structures — 20 structures with steps'),
  bullet('Part D. Assessment — stars, Unit Checks and the speaking rubric'),
  bullet('Part E. Scope and Sequence — all 24 units'),
  bullet('Part F. Lesson Procedures — 40-minute plans and differentiation'),
  bullet('Part G. Units, Scripts and Answer Keys — Grade 3, Grade 4, Grade 5, Grade 6'),
  bullet('Appendix. Quality Assurance Record'),
  pb());

// ================= PART A: INTRODUCTION =================
push(h(HeadingLevel.HEADING_1, 'Part A. About the Program'));
push(h(HeadingLevel.HEADING_2, '1. Overview'),
  p('Listen Up! Speak Out! is a complete listening and speaking program for the elementary stage, from Grade 3 (CEFR A1) to Grade 6 (CEFR A2+). It is general English and is not tied to a coursebook, so it can be used next to any curriculum. The program has three parts that work together:'),
  bullet([r('The interactive platform', { bold: true }), r(' (index.html): students listen to real audio, answer graded tasks, practise sounds, shadow and role-play. It works offline on a computer or tablet and saves each student’s progress.')]),
  bullet([r('The audio', { bold: true }), r(': 2,181 MP3 clips (every line, word and sentence) and 120 full lesson tracks for classroom speakers. A tool is included to re-voice everything with ElevenLabs.')]),
  bullet([r("This Teacher's Book", { bold: true }), r(': lesson procedures with Kagan structures, every audio script, every answer key, pronunciation notes for Arabic speakers, assessment guidance and Arabic support.')]),
  ar('البرنامج عام وغير مرتبط بكتاب مدرسي محدد، ويمكن استخدامه إلى جانب أي منهج. يتكوّن من منصة تفاعلية تعمل دون إنترنت، وملفات صوتية، ودليل للمعلم يتضمن النصوص الصوتية ومفاتيح الإجابات وإجراءات التدريس.'),
  h(HeadingLevel.HEADING_2, '2. Levels and structure'),
  p('Each grade has six units. Each unit has three listening lessons, two speaking lessons, three games and a Unit Check. Difficulty rises gradually in four ways: the length and speed of the recordings, the number of speakers, the type of task (from picture-like choices to inference and note completion) and the amount of Arabic support.'),
  bullet([r('Grade 3 — Sky Level (A1): ', { bold: true }), r('short dialogues of 60–100 words, slow speech (0.88× speed), 4 MCQs + 3 True/False + 1 ordering task per lesson, full Arabic support.')]),
  bullet([r('Grade 4 — Ocean Level (A1+): ', { bold: true }), r('recordings of 90–130 words, announcements and clue-based inference, gap-fill begins, full Arabic support.')]),
  bullet([r('Grade 5 — Forest Level (A2): ', { bold: true }), r('interviews, stories, presentations and documentaries of 130–180 words, two note-completion gaps per lesson, reduced Arabic support (glosses and tips).')]),
  bullet([r('Grade 6 — Summit Level (A2+): ', { bold: true }), r('commentary, news, adverts, talks and discussions of 150–210 words at natural speed, 5 MCQs + 2 True/False + 2 gaps, fact vs. opinion and inference of feelings; Arabic for key words, tips and pronunciation only.')]),
  h(HeadingLevel.HEADING_2, '3. Principles behind the design'),
  b('Listening is taught, not only tested.'),
  p('Every listening lesson follows a pre-, while- and post-listening cycle. Students first meet the key words, predict content and receive a strategy tip (for example, "listen for the number before the noun"). They listen twice with a clear purpose each time and only then see the script, so they can notice what they missed. This builds both top-down skills (gist, prediction, inference) and bottom-up skills (sounds, word boundaries, numbers).'),
  b('Speaking is scaffolded from model to free production.'),
  p('Every speaking lesson moves from input to output: listen to a model conversation, learn useful chunks, practise one key sound, shadow the model line by line, role-play with the app playing the other speaker, and finally speak freely with a partner using a sentence frame. Self-assessment with "I can" statements closes the lesson.'),
  b('Pronunciation targets the real needs of Arabic speakers.'),
  p('The Sound Check in each speaking lesson focuses on contrasts and patterns that Arabic-speaking children find difficult: /p/–/b/, /f/–/v/, /ɪ/–/iː/, /e/–/æ/, /θ/–/s/, /ð/–/d/, /tʃ/–/ʃ/, /dʒ/–/j/ (common in Gulf speech), consonant clusters without extra vowels, -s and -ed endings, word stress, weak forms, contractions and linking. Arabic letters are used as anchors (ث for /θ/, ذ for /ð/) and the explanations are given in English and Arabic. The checks are listening discrimination tasks; they do not claim to score a student’s pronunciation automatically.'),
  b('Cooperative learning with Kagan structures.'),
  p('Each lesson suggests two Kagan structures (for example RallyRobin, Inside-Outside Circle or Numbered Heads Together) so that every student speaks, not only the confident ones. Part C describes all 20 structures step by step.'),
  b('Culturally appropriate and meaningful content.'),
  p('A recurring cast — Sami, his sister Noor, his friends Ben, Adam and Yusuf, Noor’s friend Lina, their teachers Mr. Hassan and Ms. Green, and Sami’s family — lives in Taif. Topics include Saudi places (AlUla, Diriyah, Abha, Al-Hada, the Red Sea), national days, Eid, the Saudi Green Initiative and values such as charity, respect for neighbors and saving water.'),
  b('Arabic support is a bridge, not a replacement.'),
  p('Arabic (MSA) is used for instructions, word glosses, strategy tips and pronunciation explanations. It never gives away answers. Support is full in Grades 3–4 and is reduced in Grades 5–6; on the platform, students can switch it on or off with the ع button.'),
  pb());

// ---------- Platform guide ----------
const nPlat = newNum();
push(h(HeadingLevel.HEADING_1, 'Part B. Using the Platform and the Audio'),
  h(HeadingLevel.HEADING_2, '4. Getting started'),
  numbered('Install the program the way that suits each device: the web app (https://mrwaleedyoussif.github.io/listen-up-speak-out/, then "Install"), the Android app (.apk) or the Windows app (.exe) from the Releases page, or the program folder opened in Chrome or Edge. On iPhone and iPad, open the web app in Safari and choose Share → Add to Home Screen. The install guide (INSTALL.md) gives every step in English and Arabic.', nPlat),
  numbered('The Android and Windows apps contain all the audio and work with no internet. In the web app, press Download next to a grade on the Home page to save its audio for offline use.', nPlat),
  numbered('Each student adds his name and class on the home page, or uses Guest. Progress is saved on that device.', nPlat),
  numbered('Choose a grade, then a unit. Lessons can be done in any order, but the suggested order is Listening 1–3, then Speaking 1–2, then the games and the Unit Check.', nPlat),
  numbered('On the classroom screen, switch on Class mode (🧑‍🏫). Each lesson then shows a Teacher card with the Kagan structures and the teaching tip from this book.', nPlat),
  h(HeadingLevel.HEADING_2, '5. The six steps of a listening lesson'),
  bullet([r('1. Words — ', { bold: true }), r('six key words with picture symbols, Arabic glosses and example sentences; tap to hear each word.')]),
  bullet([r('2. Predict — ', { bold: true }), r('a prediction question, a listening strategy tip and a preview of the first questions.')]),
  bullet([r('3. Listen — ', { bold: true }), r('the full recording, with Slow and Normal speeds and a play counter. Students should listen twice.')]),
  bullet([r('4. Tasks — ', { bold: true }), r('multiple choice, True/False, ordering and gap-fill. Students check their answers, see their score and stars, and can try the wrong ones again.')]),
  bullet([r('5. Script — ', { bold: true }), r('opens after the check. Each line can be played again; the whole script can be played with highlighting.')]),
  bullet([r('6. Speak — ', { bold: true }), r('a personalised speaking task with a sentence frame and a recorder.')]),
  h(HeadingLevel.HEADING_2, '6. The six steps of a speaking lesson'),
  bullet([r('1. Listen — ', { bold: true }), r('the model conversation with the text; tap any line to hear it again.')]),
  bullet([r('2. Useful language — ', { bold: true }), r('five chunks with audio; "Listen and repeat" leaves pauses for the students.')]),
  bullet([r('3. Sound Check — ', { bold: true }), r('an explanation of one sound or pattern, then a 9–10 item listening game (minimal pairs or sorting).')]),
  bullet([r('4. Shadowing — ', { bold: true }), r('line by line: listen, record, compare with the model. Slow speed is available.')]),
  bullet([r('5. Role-play — ', { bold: true }), r('the student chooses a part; the app plays the other speaker and gives a timed turn. The "Show my lines" option can be switched off for a challenge.')]),
  bullet([r('6. Your turn — ', { bold: true }), r('a pair or group speaking task with a frame, a recorder and an "I can" self-check (😟 not yet · 🙂 with help · 🤩 yes, I can).')]),
  h(HeadingLevel.HEADING_2, '7. Games, Unit Check and certificates'),
  p('Every unit has three games built from the unit audio: Sound Catcher (hear a word, choose the picture), Who Said It? (hear a sentence, choose the speaker) and Line Up (put conversation lines in order). The Unit Check has 10 questions: four written comprehension questions on lines from the unit recordings (keys below in each unit), three word-recognition items and three "Who said this?" items. Each recording can be played twice. A score of 70% or more unlocks a printable certificate.'),
  h(HeadingLevel.HEADING_2, '8. Recording and the Word check'),
  p('Recording uses the device microphone and works when the platform is opened from its folder in Chrome or Edge (the browser asks for permission once). Students listen to their own voice and then to the model, and notice the differences. If the microphone is blocked — for example inside some shared links — students can tap "Use my device recorder" or simply speak aloud. The optional Word check (Chrome with internet) shows which words the browser recognised. It checks words only and is not a pronunciation score; your judgement and the rubric in Part D remain the assessment.'),
  h(HeadingLevel.HEADING_2, '9. Teacher dashboard'),
  p('The 📊 button opens the dashboard: every student on the device, lessons completed per grade, stars and the Unit Check average. Results can be downloaded as a CSV file or copied and pasted into Excel or Google Sheets. "Back up all students" saves every student’s progress in one file (or copies it), and "Restore a backup" brings it back on another device or after reinstalling the app.'),
  h(HeadingLevel.HEADING_2, '10. The audio files'),
  p('The audio folder is organised by grade, unit and lesson. For example, audio/g4/u2/l3/ contains Grade 4, Unit 2, Listening 3: one clip per line (01.mp3, 02.mp3…), the vocabulary words (v1.mp3–v6.mp3) and track.mp3, the full recording with natural pauses for classroom speakers. Speaking folders (s1, s2) also contain the chunks (c1–c5) and the Sound Check items (p1a/p1b or i1–i9).'),
  p('The recordings are being re-made with ElevenLabs voices, one grade at a time, starting with Grade 3. They are generated inside the program designer’s ElevenLabs account and then cut into the program’s clips; the app itself never connects to ElevenLabs, and the file names stay the same, so lessons do not change. Every clip starts with a short silence of about 0.3 seconds and the app keeps the sound output awake, so speakers, Bluetooth devices and phones never cut the first sound. Every clip is also checked with speech recognition against its script.'),
  ar('يُعاد تسجيل الصوتيات بأصوات ElevenLabs صفًّا بعد صف بدءًا من الصف الثالث، داخل حساب مصمّم البرنامج، ثم تُقسَّم إلى مقاطع البرنامج. لا يتصل التطبيق نفسه بـ ElevenLabs، وتبقى أسماء الملفات كما هي. يبدأ كل مقطع بصمت قصير حتى لا تضيع بداية الصوت في السماعات والأجهزة.'),
  h(HeadingLevel.HEADING_2, '11. The Shadowing Studio'),
  p('Shadowing means listening to a recording and speaking with it at the same time, copying its sounds, stress, rhythm and intonation. It joins listening and speaking in one activity and is especially useful for Arabic-speaking learners, because English rhythm (strong and weak beats, linking, reduced words) is very different from Arabic. The Studio (🎙️ on the home page) turns every recording in the program — all 72 listening scripts and 48 model conversations — into shadowing material.'),
  ar('التظليل يعني الاستماع إلى تسجيل والتحدث معه في الوقت نفسه، مع تقليد الأصوات والنبر والإيقاع والنغمة. وهو مفيد جدًا للمتعلمين العرب لأن إيقاع الإنجليزية يختلف كثيرًا عن إيقاع العربية.'),
  b('The five steps', { keepNext: true }),
  bullet([r('1. Listen & Read: ', { bold: true }), r('each word lights up at the moment it is spoken. Students follow with their eyes and can tap any word to hear it alone. Use "×3" to hear a line three times.')]),
  bullet([r('2. Echo: ', { bold: true }), r('students listen first, then a 2-second countdown with a sound each second and a "go" sound; the app records while the student says the line alone. A live voice meter shows that the microphone hears him, and the recording stops by itself when he has finished. This is the bridge from repetition to real shadowing.')]),
  bullet([r('3. Shadow: ', { bold: true }), r('students listen first, then the same 2-second countdown; the line plays again and students speak at the same time as the speaker while the words light up.')]),
  bullet([r('4. Blind Shadow: ', { bold: true }), r('the same, but the text is hidden until the end, so students rely on their ears.')]),
  bullet([r('5. Full Run: ', { bold: true }), r('students listen to the whole conversation (or press Skip), then after the countdown they shadow every line without stopping, like a performance.')]),
  p('A strip above the buttons always shows where the student is: 1 Listen → 2 Get ready → 3 Speak → 4 Result. Stop ends the routine at any moment.'),
  ar('في كل خطوة تسجيل: يستمع الطالب أولًا، ثم عدّ تنازلي لمدة ثانيتين مع صوت تنبيه، ثم يبدأ التسجيل. ويظهر شريط يبيّن المرحلة: استمع ← استعد ← تحدّث ← النتيجة.'),
  b('Tools on every line', { keepNext: true }),
  bullet('Four speeds (0.7×, 0.85×, normal, 1.15×) without changing the voice pitch.'),
  bullet('"Only Sami’s lines" (or any character): students shadow one role in a dialogue.'),
  bullet('Sound hints for Arabic speakers appear automatically when a line contains /p/, /v/, "th" (ث or ذ), a word starting with two consonants, or an -ed ending, in English and Arabic.'),
  bullet('Daily 5: five lines chosen from the unit the student worked on most recently, avoiding lines already mastered.'),
  b('What the feedback measures — and what it does not', { keepNext: true }),
  p('After a recording, the app shows a clear score card: one to three stars, a percentage and four rows marked green (good), yellow (nearly) or red (work on this). Start: did the student begin on time (right after the go sound in Echo, with the speaker’s first word in Shadow)? Speed: the speaker’s time and the student’s time, side by side as two bars. Flow: did he add extra stops in the middle? Voice: was it loud enough? Under the rows, one tip says the most important thing to do next, in English and Arabic. The best score for each line is saved and shown on the line buttons. A timing picture shows the speaker’s words (top row) and the student’s voice (bottom row). These are timing and fluency measures only; the app does not claim to score pronunciation. Pronunciation is judged by the student’s self-check (rhythm, clear sounds, smoothness) and by you, listening to the recording with "My voice", "Speaker" and "Both together". A line counts as mastered when the student gives himself all three self-checks in Shadow, Blind Shadow or Full Run.'),
  p('The word timings come from the voice engine itself (and from ElevenLabs’ own timestamps after re-voicing), so the highlighting follows the voice closely, within a few hundredths of a second.'),
  b('Headphones and privacy', { keepNext: true }),
  p('For steps 3–5, students should wear headphones; otherwise the microphone also hears the speaker and the timing measures become less exact. Recordings are kept only in the device’s memory during the session and are deleted when the student leaves the Studio; nothing is uploaded. The optional "Word check (online)" button uses the browser’s online speech service (Google in Chrome), so use it only where your school’s policy and parents allow.'),
  b('Suggested routines', { keepNext: true }),
  bullet([r('Daily (5 minutes): ', { bold: true }), r('Daily 5 at the start of the lesson or at home: Listen & Read → Echo → Shadow for each line.')]),
  bullet([r('Weekly cycle for one script: ', { bold: true }), r('Day 1 Listen & Read and Echo; Day 2 Shadow at 0.85×; Day 3 Shadow at normal speed; Day 4 Blind Shadow; Day 5 Full Run, recorded for the teacher.')]),
  bullet([r('Choral shadowing in class: ', { bold: true }), r('switch on Class mode, choose a line or the Full Run and let the whole class shadow together with the big highlighted text on the board. Then pairs practise one role each.')]),
  bullet([r('Tracking: ', { bold: true }), r('the dashboard shows each student’s shadowing minutes, lines mastered and daily streak.')]),
  pb());

// ---------- Kagan ----------
push(h(HeadingLevel.HEADING_1, 'Part C. Kagan Cooperative Structures'),
  p('These 20 structures are used across the program. Each lesson names two of them. Use the steps below the first time you introduce a structure; after that, the name alone is enough for the class.'));
Object.entries(K).forEach(([name, v]) => {
  const ref = newNum();
  push(h(HeadingLevel.HEADING_3, name), p(v[0]), ...v[1].map(s => numbered(s, ref)), ar(v[2]));
});
push(pb());

// ---------- Assessment ----------
push(h(HeadingLevel.HEADING_1, 'Part D. Assessment'),
  h(HeadingLevel.HEADING_2, '12. What is assessed and how'),
  bullet([r('Listening: ', { bold: true }), r('the lesson tasks (stars: 3★ = 90% or more, 2★ = 70–89%, 1★ = 40–69%) and the Unit Check (pass mark 70%). Keep the first-attempt score for reporting; the retry is for learning.')]),
  bullet([r('Speaking: ', { bold: true }), r('observation during the Kagan activities and the "Your turn" task, using the rubric below, plus the students’ own "I can" self-checks.')]),
  bullet([r('Pronunciation: ', { bold: true }), r('the Sound Check scores show whether students can hear a contrast; production is judged by the teacher during shadowing and role-play.')]),
  h(HeadingLevel.HEADING_2, '13. Speaking rubric (described in prose)'),
  p('Use four criteria. For each, decide whether the student is Beginning (1), Developing (2) or Secure (3). The total out of 12 can be reported each term.'),
  b('Criterion 1 — Task completion and interaction.'),
  p('A Beginning student answers with single words and needs the frame read to him. A Developing student completes the frame and asks at least one question with help. A Secure student completes the task, asks and answers follow-up questions and keeps the conversation going without help.'),
  b('Criterion 2 — Language range and accuracy.'),
  p('A Beginning student uses memorised chunks with frequent errors that block meaning. A Developing student uses the unit chunks correctly and makes errors that do not block meaning. A Secure student uses the unit chunks and adds his own words; errors are rare.'),
  b('Criterion 3 — Pronunciation.'),
  p('A Beginning student is often difficult to understand and adds extra vowels in clusters (for example "isnack"). A Developing student is understood with some effort and produces the lesson’s target sound when reminded. A Secure student is easy to understand and produces the target sound and word stress without reminders.'),
  b('Criterion 4 — Fluency and confidence.'),
  p('A Beginning student pauses for a long time and speaks very quietly. A Developing student speaks in short phrases with some pauses. A Secure student speaks in connected sentences, at a natural speed, with eye contact.'),
  p('Grade-band expectations: in Grade 3 a "Secure" student uses short sentences from the frame; in Grade 4 he adds one detail; in Grade 5 he gives reasons with "because"; in Grade 6 he links ideas with signpost words and reacts to his partner.'),
  ar('يُقيَّم التحدث وفق أربعة معايير: إنجاز المهمة والتفاعل، ومدى اللغة ودقتها، والنطق، والطلاقة والثقة. ولكل معيار ثلاثة مستويات: مبتدئ، ونامٍ، ومتمكّن.'),
  pb());

// ---------- Scope and sequence ----------
push(h(HeadingLevel.HEADING_1, 'Part E. Scope and Sequence'));
P.grades.forEach(G => {
  push(h(HeadingLevel.HEADING_2, `Grade ${G.grade} — ${BAND[G.grade]} Level (CEFR ${G.level})`, BANDC[G.grade]));
  G.units.forEach(U => {
    push(b(`Unit ${U.n}: ${U.title}`, { color: BANDC[G.grade], keepNext: true }), ar(U.ar, { keepNext: true }));
    U.listen.forEach(L => push(bullet([r(`Listening ${L.n} — ${L.title}: `, { bold: true }), r(L.skill)])));
    U.speak.forEach(S => push(bullet([r(`Speaking ${S.n} — ${S.title}: `, { bold: true }), r(`${S.func}. Sound focus: ${S.sound.title}`)])));
  });
});
push(pb());

// ---------- Lesson procedures (general) ----------
push(h(HeadingLevel.HEADING_1, 'Part F. Lesson Procedures (40 minutes)'),
  h(HeadingLevel.HEADING_2, '14. Listening lesson procedure'),
  bullet([r('Words (5 min): ', { bold: true }), r('play each word, students repeat and point to the symbol; Arabic glosses for checking meaning only. Ask a quick concept question, for example "Is a sharpener for paper or for pencils?"')]),
  bullet([r('Predict (3 min): ', { bold: true }), r('students discuss the prediction question in pairs (Think-Pair-Share works well). Read the tip aloud and model it.')]),
  bullet([r('First listening (3 min): ', { bold: true }), r('gist only — "Who is speaking? Where are they?" Students do not write.')]),
  bullet([r('Second listening and tasks (12 min): ', { bold: true }), r('students read the questions, listen again, then answer. Use the lesson’s first Kagan structure to compare answers before checking.')]),
  bullet([r('Script (5 min): ', { bold: true }), r('play the script with highlighting; students find the line that proves each answer. This is where real learning happens.')]),
  bullet([r('Speak (12 min): ', { bold: true }), r('the personalised task with the second Kagan structure; monitor with the rubric.')]),
  h(HeadingLevel.HEADING_2, '15. Speaking lesson procedure'),
  bullet([r('Listen (4 min): ', { bold: true }), r('play the model; ask "Who? Where? What do they want?"')]),
  bullet([r('Useful language (5 min): ', { bold: true }), r('drill the chunks chorally, then in pairs; use the pauses in "Listen and repeat".')]),
  bullet([r('Sound Check (7 min): ', { bold: true }), r('teach the sound with the explanation and the mouth tip; students do the game in pairs and then say the words.')]),
  bullet([r('Shadowing (7 min): ', { bold: true }), r('three or four key lines; students record and compare. Focus on rhythm and stress, not only sounds.')]),
  bullet([r('Role-play (8 min): ', { bold: true }), r('first with the app, then in pairs without it; swap roles. Challenge stronger students to hide their lines.')]),
  bullet([r('Your turn (9 min): ', { bold: true }), r('the free task with the Kagan structures; finish with the "I can" self-check.')]),
  h(HeadingLevel.HEADING_2, '16. Differentiation'),
  bullet([r('Support: ', { bold: true }), r('use Slow speed, keep Arabic on, allow a third listening, give the sentence frame on a card, and let students answer orally before writing.')]),
  bullet([r('Challenge: ', { bold: true }), r('switch Arabic off, hide the lines in role-play, ask for an extra detail or a reason, and ask fast finishers to write two new questions about the recording for a partner.')]),
  bullet([r('Classes with one device: ', { bold: true }), r('use Class mode on the board, play full tracks through speakers and run the tasks as whole-class Showdown with mini-whiteboards.')]),
  pb());

// ================= PART G: UNITS =================
const fmtTask = (t, i, keyArr) => {
  const n = i + 1;
  if (t.type === 'mcq') { push(b(`${n}. ${t.q}`, { keepNext: true, after: 60 }), ...choiceLine(t.opts)); keyArr.push(`${n} ${LET[t.ans]}) ${t.opts[t.ans]}`); }
  if (t.type === 'tf') { push(b(`${n}. ${t.s}`, { keepNext: true, after: 60 }), para([r('a) True'), new TextRun({ text: '\t', font: FONT, size: SZ }), r('b) False')], { tabs: TABS, indent: { left: 360 }, after: 140 })); keyArr.push(`${n} ${t.ans ? 'a) True' : 'b) False'}`); }
  if (t.type === 'gap') { push(b(`${n}. ${t.s.replace('___', '__________')}`, { after: 140 })); keyArr.push(`${n} ${t.ans.join(' / ')}`); }
  if (t.type === 'order') {
    // display in a fixed shuffled order for the printed book
    const idx = t.items.map((_, k) => k); const sh = [idx[2] ?? 0, idx[0], idx[3] ?? idx[1], idx[1], ...idx.slice(4)].filter((v, k, a) => a.indexOf(v) === k && v != null);
    push(b(`${n}. Put these in the order you hear them. Write 1–${t.items.length}.`, { keepNext: true, after: 60 }), ...sh.map(k => para([r(`(   ) ${t.items[k]}`)], { indent: { left: 360 }, after: 20 })), para([r('')], { after: 80 }));
    keyArr.push(`${n} (top to bottom) ${sh.map(k => k + 1).join(' – ')}`);
  }
};
const scriptLines = lines => lines.map((l, i) => para([r(`${String(i + 1).padStart(2, '0')}  `, { color: '7A8499', size: 26 }), r(`${l.name}: `, { bold: true }), r(l.text)], { indent: { left: 567, hanging: 567 }, after: 40 }));

push(h(HeadingLevel.HEADING_1, 'Part G. Units, Scripts and Answer Keys'));
P.grades.forEach(G => {
  const C = BANDC[G.grade];
  push(pb(), h(HeadingLevel.HEADING_1, `Grade ${G.grade} — ${BAND[G.grade]} Level (CEFR ${G.level})`, C),
    p(G.grade <= 4 ? 'Arabic support: full (instructions, glosses, prediction questions, tips, chunks and pronunciation notes).' : G.grade === 5 ? 'Arabic support: reduced (glosses, tips, chunks and pronunciation notes; prediction questions in English only).' : 'Arabic support: minimal (glosses, tips and pronunciation notes; chunks and prediction questions in English only).', { italics: true, color: '4B5568' }));
  G.units.forEach(U => {
    push(h(HeadingLevel.HEADING_2, `Unit ${U.n}: ${U.title} ${U.emoji}`, C), ar(U.ar),
      b('Unit goals', { keepNext: true }), ...U.goals.map(g => bullet(g)));
    // listening lessons
    U.listen.forEach(L => {
      push(rule(C), h(HeadingLevel.HEADING_3, `Listening ${L.n}: ${L.title}`, C),
        mixed([{ t: 'Skill: ', bold: true }, L.skill, { t: `   ·   CEFR ${G.level}   ·   Audio: audio/${L.track}`, color: '6B7280', size: 26 }]),
        ar(L.skill_ar),
        mixed([{ t: 'Kagan structures: ', bold: true }, L.kagan.join(' and ')]),
        b('Key words', { keepNext: true }),
        ...L.vocab.map(v => para([r(`${v.w}`, { bold: true }), r(' — '), r(iso(v.ar), { rtl: true, color: '333F55' }), r(` — ${v.ex}`)], { numbering: { reference: 'bul', level: 0 }, after: 40 })),
        b('Before listening', { keepNext: true, before: 120 }),
        p(`Prediction: ${L.predict.en}`), ar(L.predict.ar),
        p(`Strategy tip: ${L.tip.en}`), ar(L.tip.ar),
        b('While listening — tasks (student questions)', { keepNext: true, before: 120 }));
      const key = [];
      L.tasks.forEach((t, i) => fmtTask(t, i, key));
      push(b('After listening — speaking task', { keepNext: true, before: 60 }), p(L.speak.prompt), L.speak.frame ? p(`Frame: ${L.speak.frame}`, { italics: true }) : null,
        ...box([[r('Teaching tip: ', { bold: true }), r(L.teach)]]),
        b('Audio script', { keepNext: true }), ...scriptLines(L.script),
        ...box([[r('Answer key: ', { bold: true }), r(key.join('   ·   '))]], 'E8F6EE'));
    });
    // speaking lessons
    U.speak.forEach(S => {
      const s = S.sound;
      push(rule(C), h(HeadingLevel.HEADING_3, `Speaking ${S.n}: ${S.title}`, C),
        mixed([{ t: 'Function: ', bold: true }, S.func, { t: `   ·   Audio: audio/${S.track}`, color: '6B7280', size: 26 }]),
        ar(S.func_ar),
        mixed([{ t: 'Kagan structures: ', bold: true }, S.kagan.join(' and ')]),
        b('Model conversation', { keepNext: true }), ...scriptLines(S.model),
        mixed([{ t: 'Role-play parts: ', bold: true }, S.roles.map(rr => (S.model.find(l => l.sp === rr) || {}).name || rr).join(' / ')]),
        b('Useful language', { keepNext: true }),
        ...S.chunks.map(c => para(c.ar ? [r(c.en, { bold: true }), r('  —  '), r(iso(c.ar), { rtl: true, color: '333F55' })] : [r(c.en, { bold: true })], { numbering: { reference: 'bul', level: 0 }, after: 40 })),
        b(`Sound focus: ${s.title}`, { keepNext: true, before: 120 }), p(s.en), ar(s.ar));
      if (s.type === 'pairs') push(p('Minimal pairs (the platform plays one word at random; students choose): ' + s.pairs.map(pr => `${pr[0]} – ${pr[1]}`).join(';  ')));
      else push(p('Groups: ' + s.cats.map(c => c.label).join('  |  ')), p('Items and key: ' + s.items.map(it => `${it.text} (${it.key})`).join(';  ')));
      push(b('Your turn', { keepNext: true, before: 60 }), p(S.task.prompt), S.task.frame ? p(`Frame: ${S.task.frame}`, { italics: true }) : null,
        b('I can…', { keepNext: true }), ...S.cando.map(c => bullet(c)),
        ...box([[r('Teaching tip: ', { bold: true }), r(S.teach)]]));
    });
    // unit check
    push(rule(C), h(HeadingLevel.HEADING_3, `Unit ${U.n} Check — written comprehension items`, C),
      p('These four items appear in the platform’s Unit Check together with three word-recognition and three "Who said this?" items chosen from the unit. Each item plays one line from a unit recording.'));
    const ck = [];
    U.check.forEach((c, i) => { push(para([r(`Plays: Listening ${c.ref[1]}, line ${c.ref.split('#')[1]}`, { italics: true, color: '6B7280', size: 26 })], { after: 20, keepNext: true })); fmtTask({ type: 'mcq', q: c.q, opts: c.opts, ans: c.ans }, i, ck); });
    push(...box([[r('Answer key: ', { bold: true }), r(ck.join('   ·   '))]], 'E8F6EE'));
  });
});

// ================= QA RECORD =================
push(pb(), h(HeadingLevel.HEADING_1, 'Appendix. Quality Assurance Record'),
  p('Totals: 4 grades, 24 units, 72 listening lessons, 48 speaking lessons, 72 games (3 per unit), 24 Unit Checks.'),
  p(`Audio: ${manifest.length.toLocaleString('en')} clips plus 120 full lesson tracks; ${manifest.reduce((a, c) => a + c.text.length, 0).toLocaleString('en')} characters of text-to-speech; 15 character voices.`));
stats.forEach(s => {
  const cnt = [0, 1, 2, 3].map(i => s.mcq.filter(x => x === i).length);
  push(b(`Grade ${s.g}`, { keepNext: true, color: BANDC[s.g] }),
    bullet(`Multiple-choice items (lessons + Unit Checks): ${s.mcq.length}. Correct-answer distribution: a = ${cnt[0]}, b = ${cnt[1]}, c = ${cnt[2]}, d = ${cnt[3]}. Positions were assigned by a balancing routine with no three identical keys in a row and no a-b-c-d runs.`),
    bullet(`True/False items: ${s.tf.length} (True = ${s.tf.filter(Boolean).length}, False = ${s.tf.filter(x => !x).length}). Gap-fill items: ${s.gaps}. Ordering items: ${s.orders}.`),
    bullet(`Listening scripts: ${s.lines} lines, ${s.words.toLocaleString('en')} words (average ${Math.round(s.words / 18)} words per recording).`));
});
push(p('Checks carried out: every answer key was generated from the same data as the platform; every Unit Check item points to an existing audio line; every audio clip in the manifest exists in the audio folder; the platform was tested in a browser for every lesson type, the games, the Unit Check and the dashboard.'));

// ================= DOCUMENT =================
const doc = new Document({
  creator: 'Mr. Waleed Youssef', title: "Listen Up! Speak Out! — Teacher's Book",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: SZ } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 44, bold: true, color: '1B4FA3' }, paragraph: { spacing: { before: 240, after: 180 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 36, bold: true, color: '1D2433' }, paragraph: { spacing: { before: 280, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 32, bold: true, color: '1D2433' }, paragraph: { spacing: { before: 160, after: 100 }, keepNext: true, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [
      { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 340 } } } }, { level: 1, format: LevelFormat.BULLET, text: '◦', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1134, hanging: 340 } } } }] },
      ...numRefs.map(ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] }))
    ]
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 850, right: 850, bottom: 850, left: 850, header: 420, footer: 420 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Listen Up! Speak Out! — Teacher's Book", font: FONT, size: 20, color: '7A8499' })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ['Designed by Mr. Waleed Youssef  ·  Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], font: FONT, size: 20, color: '7A8499' })] })] }) },
    children: out
  }]
});
fs.mkdirSync(require('path').dirname(OUT), { recursive: true });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('wrote', OUT, Math.round(buf.length / 1024) + ' KB'); });
