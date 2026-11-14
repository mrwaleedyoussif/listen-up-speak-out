"""v1.5.0: the MAP Growth department (Reading and Language Usage practice, Grades 3–9).
The department lives in www/map.js and www/map/; this patch connects it to www/index.html.
Run once:  python3 tools/app/patch_v15.py"""
import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = os.path.join(ROOT, 'www', 'index.html')
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, f'expected {n} x {a[:70]!r}, found {c}'
    s = s.replace(a, b)

M = 'typeof MAPX !== "undefined"'

# 1. load the department before the main script
rep('<script src="audio/timings.js"></script>\n', '<script src="audio/timings.js"></script>\n<script src="map/index.js"></script>\n<script src="map.js"></script>\n')
# 2. version
rep("const APP_VER = '1.4.0';", "const APP_VER = '1.5.0';")
# 3. Arabic support also for MAP grades (keys 'm3' … 'm9'; on by default in Grades 3–4)
rep("const arOn = g => { const s = Store.data.settings.ar || {}; return g in s ? s[g] : (g <= 4); };",
    "const arOn = g => { const s = Store.data.settings.ar || {}; return g in s ? s[g] : (parseInt(String(g).replace(/\\D/g, ''), 10) <= 4); };")
# 4. header: colours and the Arabic switch for MAP grades
rep("  const g = S.g || null; setBand(g);\n  document.body.classList.toggle('noar', g ? !arOn(g) : false);",
    "  const g = S.g || null; setBand(g); if (S.mg && " + M + ") MAPX.band(S.mg);\n  const ak = S.mg ? 'm' + S.mg : g;\n  document.body.classList.toggle('noar', ak ? !arOn(ak) : false);")
rep("${IN ? `${g ? `<button class=\"chip ${arOn(g) ? 'on' : ''}\" id=\"arT\"",
    "${IN ? `${ak ? `<button class=\"chip ${arOn(ak) ? 'on' : ''}\" id=\"arT\"")
rep("const ar = $('#arT'); if (ar) ar.onclick = () => { const s = Store.data.settings.ar = Store.data.settings.ar || {}; s[g] = !arOn(g); Store.save(); document.body.classList.toggle('noar', !arOn(g)); ar.classList.toggle('on', arOn(g)); };",
    "const ar = $('#arT'); if (ar) ar.onclick = () => { const s = Store.data.settings.ar = Store.data.settings.ar || {}; s[ak] = !arOn(ak); Store.save(); document.body.classList.toggle('noar', !arOn(ak)); ar.classList.toggle('on', arOn(ak)); };")
rep("<small>by Mr. Waleed Youssef · Grades 3–6</small>", "<small>by Mr. Waleed Youssef · Grades 3–9</small>")
# 5. Back button / Up for the MAP screens
rep("    if (v === 'grade' || v === 'teacher' || v === 'studio') go('home');",
    "    if (v === 'map') { go('home'); return true; }\n"
    "    if (v === 'mapgrade') { go('map', { subj: S.subj }); return true; }\n"
    "    if (v === 'mapset' || v === 'mapmock') { if (v === 'mapmock' && (S.run || S.res)) go('mapmock', { mg: S.mg, mk: S.mk }); else go('mapgrade', { mg: S.mg }); return true; }\n"
    "    if (v === 'grade' || v === 'teacher' || v === 'studio') go('home');")
# 6. home page: the department card
rep("  <div class=\"section-title\"><h2>Practise speaking</h2></div>",
    "  ${" + M + " ? `<div class=\"section-title\"><h2>MAP Growth practice</h2></div>${MAPX.homeCard()}` : ''}\n  <div class=\"section-title\"><h2>Practise speaking</h2></div>")
rep("  $('#toStudio', m).onclick = () => go('studio');\n};",
    "  $('#toStudio', m).onclick = () => go('studio');\n  const tm = $('#toMap', m); if (tm) tm.onclick = () => go('map');\n};")
rep("Listen Up! Speak Out! · Designed by Mr. Waleed Youssef · 72 listening lessons · 48 speaking lessons · 24 units · v${APP_VER}",
    "Listen Up! Speak Out! · Designed by Mr. Waleed Youssef · 72 listening lessons · 48 speaking lessons · 24 units · MAP Growth practice for Grades 3–9 · v${APP_VER}")
# 7. teacher dashboard: MAP results, MAP CSV and a line in "How to use"
rep("    ${per.map(x => `<div class=\"selfrow\"><span><b>Grade ${x.g}</b> · ${x.done}/${x.total} lessons</span><span>★ ${x.stars}${x.ck != null ? ' · 🏅 ' + x.ck + '%' : ''}</span></div>`).join('')}</div>`).join('') || '<p>No students yet.</p>'}</div>",
    "    ${per.map(x => `<div class=\"selfrow\"><span><b>Grade ${x.g}</b> · ${x.done}/${x.total} lessons</span><span>★ ${x.stars}${x.ck != null ? ' · 🏅 ' + x.ck + '%' : ''}</span></div>`).join('')}${" + M + " ? MAPX.dashRows(p) : ''}</div>`).join('') || '<p>No students yet.</p>'}</div>")
rep("<button class=\"btn sec\" id=\"cp\">📋 Copy results</button>${navigator.share ? '<button class=\"btn sec\" id=\"shr\">📤 Share</button>' : ''}<span class=\"muted\" id=\"cpm\"></span></div>",
    "<button class=\"btn sec\" id=\"cp\">📋 Copy results</button>${navigator.share ? '<button class=\"btn sec\" id=\"shr\">📤 Share</button>' : ''}<span class=\"muted\" id=\"cpm\"></span></div>\n"
    "  ${" + M + " ? `<div class=\"section-title\"><h2>🎯 MAP Growth results</h2></div><div class=\"card\"><p style=\"margin-top:0\">Practice sets and mock-exam scores (percentage correct, by goal area) for every student on this device.</p><p class=\"ar ar-block\">نتائج تدريبات واختبارات MAP التجريبية لجميع الطلاب على هذا الجهاز.</p><div class=\"ctrls\" style=\"justify-content:flex-start;margin-top:10px\">${(window.LSP_SPRITES || NATIVE) ? '' : '<button class=\"btn\" id=\"mcsv\">⬇️ MAP results (CSV)</button>'}<button class=\"btn sec\" id=\"mcp\">📋 Copy MAP results</button><span class=\"muted\" id=\"mcpm\"></span></div></div>` : ''}")
rep("  $('#bkS', m).onclick = () => backupFlow($('#bkm', m));",
    "  if (" + M + ") { const mc = () => MAPX.csv(list), say = t => $('#mcpm', m).textContent = t;\n"
    "    if ($('#mcsv', m)) $('#mcsv', m).onclick = () => { const t = mc(); if (!t) return say('No MAP results yet.'); if (!saveFile('map-growth-practice-results.csv', '\\ufeff' + t, 'text/csv')) say('Download is blocked here — use Copy.'); };\n"
    "    $('#mcp', m).onclick = () => { const t = mc(); if (!t) return say('No MAP results yet.'); copyText(t).then(() => say('Copied! Paste into Excel or Google Sheets.'), () => say('Copy is not allowed here.')); }; }\n"
    "  $('#bkS', m).onclick = () => backupFlow($('#bkm', m));")
rep("    <li><b>Games and Unit Check:</b>",
    "    <li><b>MAP Growth practice (🎯):</b> Reading for Grades 3–9 — 6 practice units (78 questions) and 5 full mock exams of 43 questions per grade, scored by goal area (Literary Text, Informational Text, Vocabulary). Mock answers are saved as students go. Language Usage is coming soon.</li>\n    <li><b>Games and Unit Check:</b>")
# 8. register the department before the first screen is drawn
rep("else { Store.load(); Cfg.apply(); Auth.idleCheck(true); render();",
    "else { if (" + M + ") MAPX.register(); Store.load(); Cfg.apply(); Auth.idleCheck(true); render();")

open(P, 'w', encoding='utf-8').write(s)
print('index.html patched for v1.5.0')
