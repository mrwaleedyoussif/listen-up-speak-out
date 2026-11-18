"""v1.10.0: the school logo on both sides (left and right) of the home banner and the welcome page,
calmer logo motion (smooth entrance, slow float, light glint), the school line "Taif Boys",
and a short introduction inside every department (the Soon departments now open a page).
Run once:  python3 tools/app/patch_v110.py"""
import os, json
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda p: open(p, encoding='utf-8').read()
wr = lambda p, s: open(p, 'w', encoding='utf-8').write(s)


def one(s, a, b, n=1, where=''):
    c = s.count(a)
    assert c == n, f'{where}: expected {n} x {a[:90]!r}, found {c}'
    return s.replace(a, b)


CSS = r"""
/* ===== v1.10: logo on the left and the right, calmer logo motion, department introductions ===== */
.lg{display:inline-block;flex:none;line-height:0;animation:lgIn 1.1s cubic-bezier(.16,1,.3,1) backwards .1s}
.lg-l{--from:-26px}.lg-r{--from:26px;animation-delay:.24s}
@keyframes lgIn{from{opacity:0;transform:translate3d(var(--from,0),0,0) scale(.94)}}
.lg-f{position:relative;display:inline-block;animation:lgFloat 4.2s ease-in-out infinite alternate;will-change:transform}
@keyframes lgFloat{from{transform:translate3d(0,3px,0)}to{transform:translate3d(0,-5px,0)}}
.lg-f::before{content:"";position:absolute;inset:-8% -16%;border-radius:50%;background:radial-gradient(closest-side,rgba(255,255,255,.2),transparent);animation:lgGlow 4.2s ease-in-out infinite alternate}
@keyframes lgGlow{from{opacity:.45}to{opacity:1}}
.lg img{position:relative;display:block;height:150px;width:auto;filter:drop-shadow(0 12px 20px rgba(8,10,50,.4))}
/* a light glint crosses the logo every few seconds; the logo's own shape is the mask */
.lg-sheen{position:absolute;inset:0;pointer-events:none;-webkit-mask:url(img/andalus-logo-light.png) center/contain no-repeat;mask:url(img/andalus-logo-light.png) center/contain no-repeat;
  background:linear-gradient(112deg,transparent 45.5%,rgba(255,221,130,.95) 50%,transparent 54.5%) no-repeat;background-size:260% 100%;background-position:100% 0;animation:lgSheen 7.5s cubic-bezier(.45,0,.2,1) infinite 1.6s}
.lg-r .lg-sheen{animation-delay:2s}
@keyframes lgSheen{0%{background-position:100% 0}20%,100%{background-position:0 0}}
/* home banner: logo · text · logo */
.hub-in{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:26px}
.hub .ctrls{align-items:center}
.hub .byline.mini{align-self:center;margin-left:auto}
/* welcome page: logo · name · logo */
.authhero{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:22px;width:min(900px,calc(100vw - 32px));left:50%;transform:translateX(-50%);margin:14px 0 20px}
.authhero .lg img{height:132px}
.authhero h1{margin-top:0}
/* top bar: the shield keeps still; a glint passes now and then, and it lifts slightly on hover */
.brand .b-lg{position:relative;display:inline-block;flex:none;line-height:0;transition:transform .4s cubic-bezier(.16,1,.3,1)}
.brand:hover .b-lg{transform:translate3d(0,-2px,0) scale(1.05)}
.brand img.b-sch{background:none;border-radius:0;width:36px;height:42px;display:block}
.brand .lg-sheen{-webkit-mask-image:url(img/andalus-shield.png);mask-image:url(img/andalus-shield.png);background-image:linear-gradient(112deg,transparent 42%,rgba(255,255,255,.9) 50%,transparent 58%);animation-duration:9s;animation-delay:3s}
/* sign-out: the logo fades in, holds, and fades away */
.bye img{height:150px;width:auto;filter:drop-shadow(0 12px 20px rgba(8,10,50,.4));animation:byeLogo 1.9s cubic-bezier(.4,0,.2,1) forwards}
@keyframes byeLogo{0%{opacity:0;transform:translate3d(0,12px,0) scale(.93)}24%,74%{opacity:1;transform:none}100%{opacity:0;transform:translate3d(0,-8px,0) scale(1.03)}}
/* a short introduction inside every department */
.intro{position:relative;overflow:hidden;margin-top:16px;padding:18px 22px 18px 30px}
.intro::before{content:"";position:absolute;left:0;top:0;bottom:0;width:8px;background:linear-gradient(var(--a),var(--b))}
.in-k{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px;font-weight:800;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;color:var(--b)}
.in-k .ar{color:inherit;font-size:1rem;letter-spacing:0;font-weight:800}
.intro p{margin:.35rem 0 0;font-size:1.04rem;line-height:1.65;max-width:880px}
.intro p.ar{font-size:1.08rem}
.in-pts{display:flex;flex-wrap:wrap;gap:8px;margin:.9rem 0 0;padding:0;list-style:none}
.in-pts li{background:var(--cl);color:var(--cd);border-radius:999px;padding:5px 13px;font-weight:700;font-size:.9rem}
.dept .d-in{display:block;font-weight:600;font-size:.96rem;line-height:1.45;margin-top:.55rem;max-width:40ch}
.dept .d-in.ar{font-weight:700}
.soonbox{margin-top:16px;text-align:center}
.soonbox .d-soon{position:static!important;border:2px solid var(--b);margin-bottom:.4rem}
.soonbox p{margin:.3rem 0 0}.soonbox .btn{margin-top:1rem}
@media (max-width:900px){.lg img{height:118px}.authhero .lg img{height:108px}.hub-in{gap:18px}.authhero{gap:14px}}
@media (max-width:640px){
  .hub-in,.authhero{grid-template-columns:1fr 1fr;row-gap:12px}
  .hub-in .lg-l,.authhero .lg-l{justify-self:start}.hub-in .lg-r,.authhero .lg-r{justify-self:end;grid-column:2;grid-row:1}
  .hub-tx,.ah-tx{grid-column:1/-1;grid-row:2}
  .lg img,.authhero .lg img{height:92px}
  .hub .byline.mini{margin-left:0}
  .hub-shapes i:nth-child(3),.hub-shapes i:nth-child(8){display:none}
}
@media (prefers-reduced-motion:reduce){.lg,.lg-f,.lg-f::before,.lg-sheen,.bye img{animation:none!important}.brand .b-lg{transition:none}}
"""

W = 'index.html'
p = P('www', 'index.html'); s = rd(p)

# --- retire the v1.9 logo motion (sway, tilt, pulsing ring, spinning goodbye logo)
for old in (
    ".brand img.b-sch{background:none;border-radius:0;width:36px;height:42px;animation:logoSway 5s ease-in-out infinite}\n@keyframes logoSway{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg) scale(1.06)}}\n",
    ".hub-logo{background:none;box-shadow:none;padding:0;border-radius:0;animation:logoFloat 4.6s ease-in-out infinite}\n.hub-logo img{height:150px;filter:drop-shadow(0 10px 18px rgba(8,10,50,.45))}\n@keyframes logoFloat{0%,100%{transform:translateY(0) rotate(-2.5deg)}50%{transform:translateY(-10px) rotate(2.5deg)}}\n.logo-ring{position:relative;display:inline-block}\n.logo-ring::before{content:\"\";position:absolute;inset:-14px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.28),transparent 68%);animation:ringPulse 3s ease-in-out infinite}\n@keyframes ringPulse{0%,100%{transform:scale(.86);opacity:.55}50%{transform:scale(1.12);opacity:1}}\n.logo-ring img{position:relative}\n",
    ".authhero .logo-ring img{height:128px;width:auto;animation:logoFloat 4.6s ease-in-out infinite;filter:drop-shadow(0 10px 18px rgba(8,10,50,.45))}\n",
    ".bye img{height:150px;width:auto;animation:byeLogo 1.9s ease-in-out forwards;filter:drop-shadow(0 10px 18px rgba(8,10,50,.45))}\n@keyframes byeLogo{0%{transform:scale(.4) rotate(-25deg)}22%{transform:scale(1.08) rotate(4deg)}34%,70%{transform:scale(1) rotate(0)}100%{transform:scale(.6) translateY(-80px)}}\n",
):
    s = one(s, old, '', 1, W)
s = one(s, ".sub2{grid-template-columns:1fr}.hub-logo img{height:104px}.authhero .logo-ring img{height:100px}.hub .byline.mini{align-self:flex-start;flex:none}}",
        ".sub2{grid-template-columns:1fr}.hub .byline.mini{flex:none}}", 1, W)
s = one(s, "body.onauth::before,.authfx i,.brand img.b-sch,.hub-logo,.logo-ring::before,.authhero .logo-ring img,.nm .ch,", "body.onauth::before,.authfx i,.nm .ch,", 1, W)
s = one(s, ".authhero{text-align:center;color:#fff;margin:6px 0 16px}", ".authhero{text-align:center;color:#fff}", 1, W)

# --- new styles, after the v1.9 block
anchor = "@media (prefers-reduced-motion:reduce){body.onauth::before,.authfx i,.nm .ch,"
i = s.index(anchor); j = s.index('\n', i) + 1
s = s[:j] + CSS.lstrip('\n') + s[j:]

# --- the logo, used on the left and on the right
s = one(s, """const SCH = '<img class="b-sch" src="img/andalus-shield.png" alt="Andalus International Schools" width="36" height="42">';""",
        """const SCH = '<span class="b-lg"><img class="b-sch" src="img/andalus-shield.png" alt="Andalus International Schools" width="36" height="42"><i class="lg-sheen" aria-hidden="true"></i></span>';
/* the school logo for dark banners; side 'l' or 'r' (the right one is decoration for screen readers) */
const LG = side => `<span class="lg lg-${side}"${side === 'r' ? ' aria-hidden="true"' : ''}><span class="lg-f"><img src="img/andalus-logo-light.png" alt="${side === 'r' ? '' : 'Andalus International Schools'}" width="121" height="150"><i class="lg-sheen" aria-hidden="true"></i></span></span>`;""", 1, W)
s = one(s, """<div class="authhero"><span class="logo-ring"><img src="img/andalus-logo-light.png" alt="Andalus International Schools" width="104" height="128"></span>
  <h1>${nameFX(true)}<span class="nm-sub">English Language · اللغة الإنجليزية</span></h1>
  <p class="tag">Start from zero. Become a hero! 🚀</p><span class="ar">ابدأ من الصفر وكن بطلًا!</span></div>`;""",
        """<div class="authhero">${LG('l')}<div class="ah-tx">
  <h1>${nameFX(true)}<span class="nm-sub">English Language · اللغة الإنجليزية</span></h1>
  <p class="tag">Start from zero. Become a hero! 🚀</p><span class="ar">ابدأ من الصفر وكن بطلًا!</span></div>${LG('r')}</div>`;""", 1, W)
s = one(s, """      <div class="hub-logo logo-ring"><img src="img/andalus-logo-light.png" alt="Andalus International Schools" width="121" height="150"></div>
""", """      ${LG('l')}
""", 1, W)
BY = """<div class="byline mini" title="تصميم وإعداد: وليد يوسف"><img class="by-ph" src="img/waleed-youssef.jpg" alt="Waleed Youssef" width="38" height="38"><div class="by-tx"><span class="by-k">Designed by</span><b>Waleed Youssef</b></div></div>"""
s = one(s, """<button class="btn sm" id="wOut">🔁 Switch user</button></div>
      </div>
      """ + BY + """
    </div>""", """<button class="btn sm" id="wOut">🔁 Switch user</button>""" + BY + """</div>
      </div>
      ${LG('r')}
    </div>""", 1, W)

# --- the floating shapes keep clear of the two logos
s = one(s, """  const shapes = [['8%', '12%', 30, '#F2B330', 20, -22, 9, 0, 45], ['37%', '5%', 22, '#E16378', -16, 14, 11, -2, 0], ['52%', '8%', 18, '#fff', 14, 20, 8, -1, 45], ['68%', '70%', 40, '#278FC2', -22, -26, 12, -3, 0],
    ['82%', '14%', 34, '#E16378', 18, 24, 10, -4, 45], ['93%', '58%', 26, '#F2B330', -14, -30, 9, -5, 0], ['60%', '86%', 16, '#fff', 20, -10, 7, -2, 45], ['1.5%', '70%', 20, '#278FC2', 10, 14, 13, -6, 45]];""",
        """  const shapes = [['30%', '-4%', 26, '#F2B330', 16, 14, 9, 0, 45], ['47%', '6%', 18, '#fff', -14, 12, 11, -2, 0], ['62%', '14%', 30, '#E16378', 12, 18, 10, -1, 45], ['73%', '38%', 22, '#F2B330', -16, -18, 12, -3, 0],
    ['56%', '78%', 34, '#278FC2', 16, -14, 10, -4, 45], ['40%', '88%', 16, '#fff', 18, -10, 9, -5, 0], ['17%', '84%', 20, '#278FC2', 14, 8, 13, -6, 45], ['78%', '4%', 20, '#E16378', -12, 10, 8, -2, 0]];""", 1, W)

# --- school line: Taif Boys
s = one(s, "<small>English Language · Andalus International Schools · Taif</small>", "<small>English Language · Andalus International Schools · Taif Boys</small>", 1, W)
s = one(s, '<span class="pill">Andalus International Schools · Taif</span>', '<span class="pill">Andalus International Schools · Taif Boys</span>', 1, W)
s = one(s, 'Andalus International Schools · Taif <span class="ar" style="color:inherit">مدارس الأندلس العالمية</span>', 'Andalus International Schools · Taif Boys <span class="ar" style="color:inherit">مدارس الأندلس العالمية · الطائف بنين</span>', 1, W)
s = one(s, '<p class="foot">Andalus International Schools · Taif · ${APP}', '<p class="foot">Andalus International Schools · Taif Boys · ${APP}', 1, W)
s = one(s, "(English Language) — Andalus International Schools, Taif:", "(English Language) — Andalus International Schools, Taif Boys:", 1, W)
assert 'Schools · Taif<' not in s and 'Schools · Taif ·' not in s and 'Schools, Taif:' not in s
# --- a short introduction inside every department; the Soon departments now open a page
INTRO_JS = r"""
/* A short introduction for each department: English, Arabic, a few key points */
const INTRO = {
  ls: ['Train your ears and your voice. In every unit you listen to short recordings of everyday English and answer listening tasks, then you speak in pronunciation games and role-plays. Start with Level 2 and move up one level at a time.',
    'درّب أذنك وصوتك. في كل وحدة تستمع إلى تسجيلات قصيرة من الإنجليزية اليومية وتجيب عن مهام الاستماع، ثم تتحدث في ألعاب النطق ولعب الأدوار. ابدأ بالمستوى 2 ثم انتقل مستوى بعد مستوى.',
    ['6 units in each level', '3 listening lessons and 2 speaking lessons in each unit', '3 games and a Unit Check']],
  sh: ['Shadowing means listening to English and speaking with it at the same moment, copying the sounds, the rhythm and the music of the voice. It trains clear pronunciation and smooth, confident speech. Follow the five steps below and practise for a few minutes every day.',
    'المحاكاة تعني أن تستمع إلى الإنجليزية وتتحدث معها في اللحظة نفسها، مقلّدًا الأصوات والإيقاع ونغمة الصوت. وهي تدرّبك على النطق الواضح والكلام السلس الواثق. اتبع الخطوات الخمس أدناه وتدرّب بضع دقائق كل يوم.',
    ['5 steps', 'Levels 2–5', 'Daily 5: five lines for today']],
  map: ['MAP Growth is a computer test that measures your level in Reading and in Language Usage and reports it as a RIT score. This department gets you ready for it: choose the subject and your grade, work through the practice units, then sit a full mock exam and see your result in each goal area.',
    'اختبار MAP Growth اختبار على الحاسوب يقيس مستواك في القراءة واستخدام اللغة ويعطيك درجة RIT. هذا القسم يجهّزك له: اختر المادة وصفّك، وتدرّب على الوحدات، ثم أدِّ اختبارًا تجريبيًا كاملًا واعرف نتيجتك في كل مجال.',
    ['Reading and Language Usage', 'Grades 3–9', 'Practice units and full mock exams']],
  rw: ['Reading and Writing will take you from short, simple texts to clear paragraphs of your own. You will read and understand a text, learn its new words, and then write step by step with a model to follow.',
    'قسم القراءة والكتابة سيأخذك من النصوص القصيرة البسيطة إلى كتابة فقرات واضحة بنفسك. ستقرأ النص وتفهمه، وتتعلم كلماته الجديدة، ثم تكتب خطوة بخطوة مع نموذج تتبعه.',
    ['Read and understand', 'New words from the text', 'Write step by step']],
  gv: ['Grammar and Vocabulary will give you the rules and the words that every skill needs. Each lesson will explain one point with clear examples in English and Arabic, then give you practice that grows harder little by little.',
    'قسم القواعد والمفردات سيعطيك القواعد والكلمات التي تحتاجها كل مهارة. كل درس سيشرح نقطة واحدة بأمثلة واضحة بالإنجليزية والعربية، ثم يقدّم لك تدريبًا يزداد صعوبة شيئًا فشيئًا.',
    ['One point in each lesson', 'Clear examples', 'Practice from easy to hard']],
  step: ['STEP Preparation will train you for the Standardized Test of English Proficiency (STEP). You will practise its four parts, then try full practice tests.',
    'قسم التحضير لاختبار STEP سيدرّبك على اختبار كفايات اللغة الإنجليزية (STEP). ستتدرّب على أقسامه الأربعة، ثم تجرّب اختبارات تدريبية كاملة.',
    ['Reading comprehension', 'Sentence structure', 'Listening comprehension', 'Compositional analysis']],
  ph: ['Phonics will teach you the sounds of English letters and letter groups, so that you can read new words and spell them correctly. You will hear each sound, say it, and join sounds together to make words.',
    'قسم الصوتيات سيعلّمك أصوات الحروف الإنجليزية ومجموعات الحروف، لتقرأ الكلمات الجديدة وتكتبها كتابة صحيحة. ستسمع كل صوت وتنطقه، ثم تدمج الأصوات لتكوّن كلمات.',
    ['Hear the sound', 'Say the sound', 'Blend sounds into words']],
  ghars: ['Ghars will bring two programmes together in one place: Wordline and Performing Art. Each programme will have its own activities here.',
    'قسم غراس سيجمع برنامجين في مكان واحد: Wordline والفنون الأدائية. وسيكون لكل برنامج أنشطته الخاصة هنا.', []],
  wl: ['Wordline will be a programme about words: learning new words, saying them and using them.', 'برنامج عن الكلمات: تعلّم كلمات جديدة ونطقها واستخدامها.'],
  pa: ['Performing Art will let students use English on stage, in short plays, role-plays and presentations.', 'استخدام الإنجليزية على المسرح في مسرحيات قصيرة ولعب أدوار وعروض تقديمية.']
};
const introCard = id => { const [en, ar, pts] = INTRO[id], d = DEPTS.find(x => x[0] === id) || [];
  return `<section class="card intro" style="--a:${d[4] || 'var(--c)'};--b:${d[5] || 'var(--cd)'}"><span class="in-k">Introduction <span class="ar">مقدمة</span></span>
    <p>${esc(en)}</p><p class="ar ar-block">${esc(ar)}</p>${pts && pts.length ? `<ul class="in-pts">${pts.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}</section>`; };"""
G_OLD = "const GHARS = [['wl', 'Wordline', '', '#12B5CB', '#0A7C96'], ['pa', 'Performing Art', 'الفنون الأدائية', '#F0569C', '#C92671']];"
s = one(s, G_OLD, G_OLD + INTRO_JS, 1, W)
s = one(s, "const deptCard = ([id, en, ar, k, a, b, view, soon], i, meta) => `", "const deptCard = ([id, en, ar, k, a, b, view, soon], i, meta, tx) => `", 1, W)
s = one(s, """      ${ar ? `<span class="ar">${esc(ar)}</span>` : ''}
      ${meta ?""", """      ${ar ? `<span class="ar">${esc(ar)}</span>` : ''}${tx ? `<span class="d-in">${esc(tx[0])}</span><span class="d-in ar">${esc(tx[1])}</span>` : ''}
      ${meta ?""", 1, W)
for k in ("'#F59E0B', '#EA5B0C'", "'#9B6CF6', '#6D3BE0'", "'#12B5CB', '#0A7C96'", "'#F0569C', '#C92671'"):
    s = one(s, k + ", '', 1]", k + ", 'dept', 1]", 1, W)
s = one(s, """    if (d[6]) return go(d[6]);
    b.classList.remove('nudge'); void b.offsetWidth; b.classList.add('nudge');
    $('#soonMsg', m).innerHTML = `${esc(d[1])} is coming soon. <span class="ar" style="color:inherit">${esc(d[2])}: قريبًا</span>`;
  });""", """    go(d[6], d[6] === 'dept' ? { dp: d[0] } : {});
  });""", 1, W)
s = one(s, """/* --- Ghars department (coming soon): Wordline and Performing Art --- */""", """/* --- a department that is coming soon: its introduction and a note --- */
VIEWS.dept = m => {
  const d = DEPTS.find(x => x[0] === S.dp && x[6] === 'dept'); if (!d) return go('home');
  const parts = [['Home', () => go('home')], [d[1]]];
  m.innerHTML = crumbs(parts) + `
  <section class="lhead dhead" style="--a:${d[4]};--b:${d[5]}"><span class="d-ic">${DIC[d[0]]}</span><div><span class="k">Department · coming soon</span><h1>${esc(d[1])} <span class="ar" style="color:#fff;font-size:.8em">${esc(d[2])}</span></h1></div></section>
  ${introCard(d[0])}
  <section class="card soonbox" style="--b:${d[5]}"><span class="d-soon"><i></i>Soon · قريبًا</span>
    <p><b>This department is being prepared.</b> It will open here in a coming update.</p>
    <p class="ar" style="text-align:center">هذا القسم قيد الإعداد، وسيُفتح هنا في تحديث قادم.</p>
    <button class="btn" id="dBack">← Back to the departments <span class="ar" style="color:inherit">العودة إلى الأقسام</span></button></section>`;
  bindCrumbs(m, parts); $('#dBack', m).onclick = () => go('home');
};

/* --- Ghars department (coming soon): Wordline and Performing Art --- */""", 1, W)
s = one(s, """<h1>Ghars <span class="ar" style="color:#fff;font-size:.8em">غراس</span></h1>
    <p style="margin:.3rem 0 0;opacity:.95">Two programmes will open here: Wordline and Performing Art.</p>
    <p class="ar" style="color:#fff;margin:0">برنامجان قريبًا في هذا القسم.</p></div></section>
  <section class="sub2">${GHARS.map(([id, en, ar, a, b], i) => deptCard([id, en, ar, '', a, b, '', 1], i)).join('')}</section>""",
        """<h1>Ghars <span class="ar" style="color:#fff;font-size:.8em">غراس</span></h1></div></section>
  ${introCard('ghars')}
  <section class="sub2">${GHARS.map(([id, en, ar, a, b], i) => deptCard([id, en, ar, '', a, b, '', 1], i, null, INTRO[id])).join('')}</section>""", 1, W)
s = one(s, """<h1>Listening and Speaking</h1>
    <p style="margin:.3rem 0 0;opacity:.95;max-width:720px">Real audio, smart listening tasks, pronunciation games and role-plays. Each level has 6 units; each unit has 3 listening lessons, 2 speaking lessons, 3 games and a Unit Check.</p>
    <p class="ar" style="color:#fff;margin:0">الاستماع والتحدث: تسجيلات حقيقية ومهام استماع وألعاب نطق ولعب أدوار، في أربعة مستويات.</p></div></section>""",
        """<h1>Listening and Speaking <span class="ar" style="color:#fff;font-size:.8em">الاستماع والتحدث</span></h1></div></section>
  ${introCard('ls')}""", 1, W)
s = one(s, """<h1>Speak like the speaker!</h1>
    <p style="margin:.3rem 0 0;max-width:720px">Shadowing means listening to English and speaking <b>with</b> it, copying the sounds, the rhythm and the music. Practise a little every day.</p>
    <p class="ar" style="color:#fff">المحاكاة تعني أن تستمع إلى الإنجليزية وتتحدث معها في الوقت نفسه، مقلّدًا الأصوات والإيقاع والنغمة. تدرّب قليلًا كل يوم.</p></section>""",
        """<h1>Speak like the speaker! <span class="ar" style="color:#fff;font-size:.8em">المحاكاة</span></h1></section>
  ${introCard('sh')}""", 1, W)
s = one(s, "    else if (v === 'ls' || v === 'ghars' || v === 'teacher' || v === 'studio') go('home');", "    else if (v === 'ls' || v === 'ghars' || v === 'dept' || v === 'teacher' || v === 'studio') go('home');", 1, W)
s = one(s, "safe() { return ['home', 'ls', 'ghars', 'grade',", "safe() { return ['home', 'ls', 'ghars', 'dept', 'grade',", 1, W)
s = one(s, "Phonics and Ghars (Wordline and Performing Art) are marked “Soon”.</li>", "Phonics and Ghars (Wordline and Performing Art) are marked “Soon”. Every department opens with a short introduction in English and Arabic.</li>", 1, W)

# --- MAP department (map.js): the introduction, and the name without the title
mp = P('www', 'map.js'); t = rd(mp)
t = one(t, """<h1>🎯 MAP Growth Practice</h1>
      <p style="margin:.3rem 0 0;opacity:.95">Practice units and full mock exams for the MAP Growth Reading and Language Usage tests, written to the MAP goal areas and RIT bands.</p>
      <span class="ar ar-block">تدريب على اختبار MAP Growth في القراءة واستخدام اللغة للصفوف من الثالث إلى التاسع.</span></section>""",
        """<h1>🎯 MAP Growth Practice <span class="ar" style="color:#fff;font-size:.8em">اختبار MAP</span></h1></section>
    ${introCard('map')}""", 1, mp)
t = one(t, "من إعداد أ. وليد يوسف", "من إعداد وليد يوسف", 1, mp)
wr(mp, t)
s = one(s, "const APP_VER = '1.9.0';", "const APP_VER = '1.10.0';", 1, W)
wr(p, s)

for f, pairs in {
    P('www', 'manifest.webmanifest'): [('"description": "Andalus International Schools, Taif:', '"description": "Andalus International Schools, Taif Boys:')],
    P('.github', 'workflows', 'build.yml'): [('Andalus International Schools, Taif (build', 'Andalus International Schools, Taif Boys (build')],
    P('README.md'): [('**Andalus International Schools – Taif**', '**Andalus International Schools – Taif Boys**')],
    P('package.json'): [('"version": "1.9.0"', '"version": "1.10.0"')],
}.items():
    t = rd(f)
    for a, b in pairs:
        t = one(t, a, b, 1, f)
    wr(f, t)
t = rd(P('package-lock.json')); assert t.count('"version": "1.9.0"') >= 2
wr(P('package-lock.json'), t.replace('"version": "1.9.0"', '"version": "1.10.0"', 2))

cl = json.loads(rd(P('tools', 'app', 'changelog.json')))
assert '1.10.0' not in cl
cl = {'1.10.0': {
    'en': ['The school logo now stands on both sides of the home banner and the welcome page.',
           'The logos move more calmly: they slide in, float slowly, and a light glint passes over them.',
           'The school line now reads “Andalus International Schools · Taif Boys”.',
           'Every department opens with a short introduction in English and Arabic. The Soon departments now open a page with their introduction.'],
    'ar': ['شعار المدرسة يظهر الآن على جانبي لافتة الصفحة الرئيسية وصفحة الترحيب.',
           'حركة الشعارات أصبحت أهدأ: تدخل بانسياب، وتطفو ببطء، ويمرّ عليها بريق خفيف.',
           'اسم المدرسة أصبح «Andalus International Schools · Taif Boys» (الطائف بنين).',
           'كل قسم يبدأ الآن بمقدمة قصيرة بالإنجليزية والعربية، والأقسام القادمة تفتح صفحة فيها مقدمتها.']}, **cl}
wr(P('tools', 'app', 'changelog.json'), json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('v1.10.0 patched')
