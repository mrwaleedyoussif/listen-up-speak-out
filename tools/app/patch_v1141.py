#!/usr/bin/env python3
"""v1.14.1: Cursive Handwriting moves into Ghars > Wordline; recordings stop when the student leaves a page; texts updated."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def one(s, a, b, n=1, where=''):
    assert s.count(a) == n, (where or a[:60], s.count(a)); return s.replace(a, b)
p = os.path.join(ROOT, 'www', 'index.html'); s = open(p, encoding='utf-8').read()
HW = "['hw', 'Cursive Handwriting', 'الخط المتصل', 'Watch · Trace · Write · 77 pages', '#F2994A', '#D9480F', 'hw', 0]"
s = one(s, "  " + HW + ",\n", "")
s = one(s, "  ['ghars', 'Ghars', 'غرس', '', '#7CB518', '#3D7A0A', 'ghars', 1]\n];", "  ['ghars', 'Ghars', 'غرس', 'Wordline · Cursive Handwriting', '#7CB518', '#3D7A0A', 'ghars', 0]\n];\n/* programmes that live inside a department (Ghars > Wordline > Cursive Handwriting) */\nconst SUBS = [" + HW + "];")
s = one(s, "d = DEPTS.find(x => x[0] === id) || [];\n  return `<section class=\"card intro\"", "d = DEPTS.concat(SUBS).find(x => x[0] === id) || [];\n  return `<section class=\"card intro\"")
s = one(s, "d[0] === 'hw' && typeof HWX !== 'undefined' ? HWX.homeMeta()", "d[0] === 'ghars' && typeof HWX !== 'undefined' ? HWX.homeMeta()")
a = s.index("/* --- Ghars department (coming soon): Wordline and Performing Art --- */"); b = s.index("/* --- Listening and Speaking department: choose a level --- */")
s = s[:a] + """/* --- Ghars department: Wordline (open: Cursive Handwriting) and Performing Art (coming soon) --- */
VIEWS.ghars = m => {
  const parts = [['Home', () => go('home')], ['Ghars']], d = DEPTS.find(x => x[0] === 'ghars');
  m.innerHTML = crumbs(parts) + `
  <section class="lhead dhead" style="--a:${d[4]};--b:${d[5]}"><span class="d-ic">${DIC.ghars}</span><div><span class="k">Department · Wordline · Performing Art</span><h1>Ghars <span class="ar" style="color:#fff;font-size:.8em">غرس</span></h1></div></section>
  ${introCard('ghars')}
  <section class="sub2">${GHARS.map(([id, en, ar, a, b], i) => deptCard([id, en, ar, id === 'wl' ? 'Cursive Handwriting' : '', a, b, id === 'wl' ? 'wl' : '', id === 'wl' ? 0 : 1], i, null, INTRO[id])).join('')}</section>
  <p class="soonmsg" id="soonMsg" role="status" aria-live="polite"></p>`;
  bindCrumbs(m, parts);
  $$('[data-dept]', m).forEach(b => b.onclick = () => { const g = GHARS.find(x => x[0] === b.dataset.dept); if (g[0] === 'wl') return go('wl'); b.classList.remove('nudge'); void b.offsetWidth; b.classList.add('nudge'); $('#soonMsg', m).textContent = g[1] + ' is coming soon.'; });
};
/* --- Wordline (inside Ghars): its programmes --- */
VIEWS.wl = m => {
  const parts = [['Home', () => go('home')], ['Ghars', () => go('ghars')], ['Wordline']], g = GHARS.find(x => x[0] === 'wl');
  m.innerHTML = crumbs(parts) + `
  <section class="lhead dhead" style="--a:${g[3]};--b:${g[4]}"><span class="d-ic">${DIC.wl}</span><div><span class="k">Ghars · Programme</span><h1>Wordline</h1></div></section>
  <section class="card intro" style="--a:${g[3]};--b:${g[4]}"><span class="in-k">Introduction <span class="ar">مقدمة</span></span><p>${esc(INTRO.wl[0])}</p><p class="ar ar-block">${esc(INTRO.wl[1])}</p></section>
  <section class="sub2">${SUBS.map((d, i) => deptCard(d, i, typeof HWX !== 'undefined' ? HWX.homeMeta() : '')).join('')}</section>`;
  bindCrumbs(m, parts);
  $$('[data-dept]', m).forEach(b => b.onclick = () => go(SUBS.find(x => x[0] === b.dataset.dept)[6]));
};

""" + s[b:]
a = s.index("  ghars: ['Ghars will bring two programmes"); b = s.index("  pa: ['Performing Art", a)
s = s[:a] + """  ghars: ['Ghars brings two programmes together in one place. Wordline is open now and starts with Cursive Handwriting. Performing Art is coming soon.',
    'قسم غرس يجمع برنامجين في مكان واحد. برنامج Wordline متاح الآن ويبدأ بالخط المتصل، وبرنامج الفنون الأدائية قريبًا.', ['Wordline · open', 'Performing Art · soon']],
  wl: ['Wordline is a programme about words: writing them beautifully, learning new ones and using them. It starts with Cursive Handwriting.', 'برنامج عن الكلمات: كتابتها بخط جميل، وتعلّم كلمات جديدة واستخدامها. ويبدأ بالخط المتصل.'],
""" + s[b:]
s = one(s, "    if (v === 'hw') { go('home'); return true; }", "    if (v === 'hw') { go('wl'); return true; }\n    if (v === 'wl') { go('ghars'); return true; }")
s = one(s, "'steplesson', 'hw', 'ph', 'grade',", "'steplesson', 'hw', 'wl', 'ph', 'grade',")
# a recording that is playing must stop when the student opens another page
s = one(s, "  SHT.tok++; AU.stop(); stopAllRec();", "  SHT.tok++; AU.stop(); stopAllRec(); document.querySelectorAll('#main audio, main audio').forEach(x => { try { x.pause(); } catch (e) {} }); if (typeof HWX !== 'undefined') HWX.stop();")
OLD_D = "Listening and Speaking, Shadowing, Language Usage (Levels A1 to C2) and MAP test practice (Grades 3–9), with Arabic support."
NEW_D = "Listening and Speaking, Shadowing, MAP test practice (Grades 3–9), Language Usage (Levels A1 to C2), STEP Preparation, Phonics and Cursive Handwriting, with Arabic support."
s = one(s, OLD_D, NEW_D)
a = s.index("    <li><b>Departments:</b> after sign-in"); b = s.index("</li>", a) + 5
s = s[:a] + "    <li><b>Departments:</b> after sign-in, students choose a department: Listening and Speaking (Levels A1 to A2+; B1 to C2 are marked “Soon”), Shadowing, MAP Test, Language Usage (Levels A1 to C2), STEP Preparation (4 Foundation booklets and 30 mock exams), Phonics (Phonics Made Clear, 40 parts with audio) or Ghars (Wordline with Cursive Handwriting; Performing Art is marked “Soon”). Reading and Writing is marked “Soon”. Every department opens with a short introduction in English and Arabic.</li>" + s[b:]
s = one(s, ".sub2 .dept.soon{grid-column:auto;min-height:190px}", ".sub2 .dept.soon{grid-column:auto;min-height:190px}.sub2 .dept{grid-column:auto;min-height:190px}")
s = one(s, "const APP_VER = '1.14.0';", "const APP_VER = '1.14.1';")
open(p, 'w', encoding='utf-8').write(s)
q = os.path.join(ROOT, 'www', 'manifest.webmanifest'); t = open(q, encoding='utf-8').read(); open(q, 'w', encoding='utf-8').write(one(t, OLD_D, NEW_D))
q = os.path.join(ROOT, 'www', 'hw.js'); t = open(q, encoding='utf-8').read()
t = one(t, "parts = [['Home', () => go('home')], ['Cursive Handwriting']];", "parts = [['Home', () => go('home')], ['Ghars', () => go('ghars')], ['Wordline', () => go('wl')], ['Cursive Handwriting']];")
t = one(t, "const parts = [['Home', () => go('home')], ['Cursive Handwriting', () => go('hw')], [L.t]];", "const parts = [['Home', () => go('home')], ['Wordline', () => go('wl')], ['Cursive Handwriting', () => go('hw')], [L.t]];")
t = one(t, "<span class=\"k\">Department · 26 letters", "<span class=\"k\">Ghars · Wordline · 26 letters")
open(q, 'w', encoding='utf-8').write(t)
for f, n in (('package.json', 1), ('package-lock.json', 2)):
    q = os.path.join(ROOT, f); t = open(q, encoding='utf-8').read(); assert t.count('"version": "1.14.0"') >= n; open(q, 'w', encoding='utf-8').write(t.replace('"version": "1.14.0"', '"version": "1.14.1"', n))
q = os.path.join(ROOT, 'tools', 'app', 'changelog.json'); cl = json.load(open(q, encoding='utf-8'))
cl = {'1.14.1': {'en': ['Cursive Handwriting is now inside Ghars, in the Wordline programme. Ghars is open; Performing Art stays “Soon”.', 'A recording that is playing now stops when you open another page.'],
                  'ar': ['الخط المتصل أصبح داخل قسم غرس ضمن برنامج Wordline. قسم غرس متاح الآن، وبرنامج الفنون الأدائية ما زال «قريبًا».', 'التسجيل الصوتي يتوقف الآن عند فتح صفحة أخرى.']}, **cl}
open(q, 'w', encoding='utf-8').write(json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('patched 1.14.1')
