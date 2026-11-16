"""v1.7.0: printable copies (Word and PDF) of the MAP student booklets and mock exams on every MAP grade page.
The files live in print/map/ (repo root). The website build copies them to www/print/map/; the phone and
desktop apps open them on the website, so they are not packed inside the apps and are not saved for offline use.
Run once:  python3 tools/app/patch_v17.py"""
import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)

def patch(path, pairs):
    s = open(path, encoding='utf-8').read()
    for a, b in pairs:
        c = s.count(a)
        assert c == 1, f'{path}: expected 1 x {a[:70]!r}, found {c}'
        s = s.replace(a, b)
    open(path, 'w', encoding='utf-8').write(s)

# ---- www/map.js: the "Print copies" card
patch(P('www', 'map.js'), [
 ("""  /* ---------- data ---------- */""",
  """  /* printable copies: on the website they come from the same site; the apps open them in the browser */
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

  /* ---------- data ---------- */"""),
 ("""}).join('')}</section>`;
    bindCrumbs(m, parts);
    $$('[data-set]', m)""",
  """}).join('')}</section>
    ${printHTML(subj, g)}`;
    bindCrumbs(m, parts);
    $$('a[data-ext]', m).forEach(a => a.onclick = e => { e.preventDefault(); if (typeof openExt === 'function') openExt(a.href); else window.open(a.href, '_blank'); });
    $$('[data-set]', m)"""),
 (""".mmock{display:flex;flex-direction:column;gap:4px;text-align:left;border:2px solid transparent;position:relative;min-height:150px}""",
  """.mmock{display:flex;flex-direction:column;gap:4px;text-align:left;border:2px solid transparent;position:relative;min-height:150px}
.mprint{display:flex;flex-direction:column;gap:4px}
.mprint .mp-btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.mprint .mp-btns small{font-weight:600;opacity:.8}"""),
])

# ---- www/index.html: version and teacher help
patch(P('www', 'index.html'), [
 ("const APP_VER = '1.6.0';", "const APP_VER = '1.7.0';"),
 ("scored by goal area (Reading: Literary Text, Informational Text, Vocabulary; Language Usage: Writing, Grammar and Usage, Mechanics). Mock answers are saved as students go.</li>",
  "scored by goal area (Reading: Literary Text, Informational Text, Vocabulary; Language Usage: Writing, Grammar and Usage, Mechanics). Mock answers are saved as students go. Each grade page also has print copies (PDF and Word) of the student booklet and the mock exams.</li>"),
])

# ---- the print files never go into the offline app files
patch(P('tools', 'app', 'build_www.py'), [
 ("if r.endswith('.mp3') or r in ('sw.js', 'index.html', 'version.json') or r.startswith('icons/shots/') or f.startswith('.'): continue",
  "if r.endswith('.mp3') or r in ('sw.js', 'index.html', 'version.json') or r.startswith(('icons/shots/', 'print/')) or f.startswith('.'): continue"),
])

# ---- website build: copy the print files after the offline file list is made
patch(P('.github', 'workflows', 'build.yml'), [
 ("""      - run: python3 tools/app/build_www.py
      - run: python3 tools/app/release_info.py "v${{ needs.version.outputs.name }}\"""",
  """      - run: python3 tools/app/build_www.py
      - run: mkdir -p www/print && cp -r print/map www/print/   # print copies: website only (the apps open them here)
      - run: python3 tools/app/release_info.py "v${{ needs.version.outputs.name }}\""""),
])
print('v1.7.0 patched')
