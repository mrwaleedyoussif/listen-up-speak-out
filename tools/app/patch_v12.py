"""v1.2: colour-coded lesson icons, pictures for vocabulary (Fluent Emoji 3D), silent recording in shadowing."""
import sys
p = sys.argv[1] if len(sys.argv) > 1 else 'www/index.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:100]); s = s.replace(old, new)

# ---------- pictures ----------
rep('<script src="data.js"></script>', '<script src="img/pics/index.js"></script>\n<script src="data.js"></script>')
rep("const LET = ['a', 'b', 'c', 'd'];", """const LET = ['a', 'b', 'c', 'd'];
/* Pictures (Microsoft Fluent Emoji 3D, MIT licence) for vocabulary and units; the emoji is the fallback */
const PICS = new Set(window.LSP_PICS || []);
const picKey = e => [...String(e || '')].map(c => c.codePointAt(0).toString(16)).filter(x => x !== 'fe0f').join('-');
const pic = (e, cls) => { const k = picKey(e); return PICS.has(k) ? `<img class="${cls || 'pic'}" src="img/pics/${k}.webp" alt="" draggable="false" loading="lazy">` : `<span class="emo">${e || '🔤'}</span>`; };""")
rep("""<button class="vcard" data-v="${i}"><span class="em">${v.emoji || '🔤'}</span>""", """<button class="vcard" data-v="${i}"><span class="em">${pic(v.emoji)}</span>""")
rep("""<button data-o="${j}"><span class="em">${o.emoji || '🔤'}</span>${esc(o.w)}</button>""", """<button data-o="${j}"><span class="em">${pic(o.emoji)}</span>${esc(o.w)}</button>""")
rep("""<div class="uh"><span class="ue">${u.emoji}</span>""", """<div class="uh"><span class="ue">${pic(u.emoji)}</span>""")
rep("""<h1>${u.emoji} ${esc(u.title)}</h1>""", """<h1><span class="hpic">${pic(u.emoji)}</span>${esc(u.title)}</h1>""")
rep("""font-size:1.5rem">${u0.emoji}</span>""", """font-size:1.5rem">${pic(u0.emoji)}</span>""")

# ---------- colour-coded lesson icons ----------
rep("""<span class="ic">${isL ? '🎧' : '🗣️'}</span>""", """<span class="ic ic-${isL ? 'l' : 's'}${x.L.n}">${isL ? '🎧' : '🗣️'}<i>${x.L.n}</i></span>""")
rep("""<button class="lrow" id="ucheck"><span class="ic">🏅</span>""", """<button class="lrow" id="ucheck"><span class="ic ic-ck">🏅</span>""")
rep("""<button class="gtile" data-game="${k}"><span class="em">${em}</span>""", """<button class="gtile" data-game="${k}"><span class="em gem gem-${k}">${em}</span>""")
rep("""<button class="gtile" data-sh="${t.key}"><span class="em">${t.icon}</span>""", """<button class="gtile" data-sh="${t.key}"><span class="em gem gem-sh${t.key[0]}">${t.icon}</span>""")
# lesson page header carries the same colour badge
rep("""<section class="lhead"><span class="k">${L.kind === 'listen' ? '🎧 Listening ' + L.n : '🗣️ Speaking ' + L.n}""",
    """<section class="lhead"><span class="k"><span class="kbadge ic-${L.kind === 'listen' ? 'l' : 's'}${L.n}">${L.kind === 'listen' ? '🎧' : '🗣️'}</span>${L.kind === 'listen' ? 'Listening ' + L.n : 'Speaking ' + L.n}""")

rep("/* studio v1.1: phases", """/* v1.2: colour-coded lesson icons and pictures */
.lrow .ic{width:50px;height:50px;border-radius:15px;position:relative;font-size:1.5rem;box-shadow:inset 0 -3px 0 rgba(0,0,0,.14),0 5px 12px rgba(20,30,60,.14)}
.lrow .ic i{position:absolute;right:-7px;bottom:-7px;width:22px;height:22px;border-radius:50%;background:#fff;color:#1D2433;font:800 .78rem/22px var(--fh);font-style:normal;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.25)}
.ic-l1{background:linear-gradient(135deg,#5AB0FF,#1F5FD6)!important}.ic-l2{background:linear-gradient(135deg,#3FE0C5,#0E8F80)!important}.ic-l3{background:linear-gradient(135deg,#B49CFF,#6A3BE0)!important}
.ic-s1{background:linear-gradient(135deg,#FFB067,#EF6A1E)!important}.ic-s2{background:linear-gradient(135deg,#FF86A5,#DE2F5E)!important}.ic-ck{background:linear-gradient(135deg,#FFE066,#E8A200)!important}
.lrow:has(.ic-l1):hover{border-color:#1F5FD6}.lrow:has(.ic-l2):hover{border-color:#0E8F80}.lrow:has(.ic-l3):hover{border-color:#6A3BE0}.lrow:has(.ic-s1):hover{border-color:#EF6A1E}.lrow:has(.ic-s2):hover{border-color:#DE2F5E}
.gtile .em.gem{width:66px;height:66px;border-radius:20px;display:grid;place-items:center;font-size:2.1rem;box-shadow:inset 0 -4px 0 rgba(0,0,0,.14),0 6px 14px rgba(20,30,60,.15)}
.gem-catch{background:linear-gradient(135deg,#4BE3A3,#0E9F6E)}.gem-who{background:linear-gradient(135deg,#CF9BFF,#8B3FE0)}.gem-lineup{background:linear-gradient(135deg,#FFCF4A,#E58A00)}
.gem-shl{background:linear-gradient(135deg,#55CCFF,#0B7FC4)}.gem-shs{background:linear-gradient(135deg,#FF8AC8,#D12A80)}
.kbadge{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:10px;margin-right:8px;vertical-align:middle;font-size:1rem;box-shadow:inset 0 -2px 0 rgba(0,0,0,.14)}
img.pic{display:block;object-fit:contain;-webkit-user-drag:none;user-select:none}
.vcard .em{min-height:96px;display:grid;place-items:center}.vcard .em img.pic{width:96px;height:96px;filter:drop-shadow(0 6px 8px rgba(20,30,60,.18));transition:transform .15s}
.vcard:hover .em img.pic,.vcard.playing .em img.pic{transform:scale(1.08) rotate(-3deg)}
.pick4 button .em img.pic{width:76px;height:76px;filter:drop-shadow(0 4px 6px rgba(20,30,60,.15))}
.ucard .ue img.pic{width:42px;height:42px}
.hpic img.pic{display:inline-block;width:1.25em;height:1.25em;vertical-align:-.22em;margin-right:.3em}
.uh .ue img.pic{width:36px;height:36px}
/* studio v1.1: phases""")

# ---------- shadowing: no sound while the student records ----------
rep("""        if (rec) await Mic.start();
        recUI(msg, S.mode === 3 ? 'Shadow now — no text!' : 'Speak with the speaker!', S.mode === 3 ? 'ظلّل الآن دون نص!' : 'تحدّث مع المتحدث الآن!', rec, false);
        const R = recLoop(msg, lineSec() + 1.2, tok, false);
        let tPlay = performance.now(); AU.el.addEventListener('playing', () => { tPlay = performance.now(); }, { once: true });
        const ok = await AU.one(clip, S.rate); await sleep(700); R.end();""",
"""        if (rec) await Mic.start();
        recUI(msg, S.mode === 3 ? 'Say it from memory — at the speaker’s speed!' : 'Say the line as the words light up!', S.mode === 3 ? 'قلها من الذاكرة بسرعة المتحدث!' : 'قل الجملة والكلمات تُضاء!', rec, false);
        const R = recLoop(msg, lineSec() + 1.2, tok, false);
        // the line runs silently: only the student's voice is recorded, the words light up at the speaker's pace
        let tPlay = performance.now(); AU.el.addEventListener('playing', () => { tPlay = performance.now(); }, { once: true });
        AU.el.muted = !!rec; let ok;
        try { ok = await AU.one(clip, S.rate); await sleep(700); } finally { AU.el.muted = false; }
        R.end();""")
rep("""    recUI(msg, 'Shadow every line!', 'ظلّل كل الجمل!', rec, false);
    const R = recLoop(msg, lines.reduce((t, l) => t + secOf(l) + 0.5, 0.6), tok, false);
    const starts = []; const t0 = performance.now();
    const ok = await AU.list(lines.map(clipOf), { rate: S.rate, gap: 500, onLine: i => { mark(i); if (i >= 0) starts[i] = (performance.now() - (rec ? Mic.t0 : t0)) / 1000 + 0.05; } });
    await sleep(600); R.end();""",
"""    recUI(msg, 'Say every line as the words light up!', 'قل كل الجمل والكلمات تُضاء!', rec, false);
    const R = recLoop(msg, lines.reduce((t, l) => t + secOf(l) + 0.5, 0.6), tok, false);
    const starts = []; const t0 = performance.now();
    AU.el.muted = !!rec; let ok;   // silent guide: only the student's voice is recorded
    try { ok = await AU.list(lines.map(clipOf), { rate: S.rate, gap: 500, onLine: i => { mark(i); if (i >= 0) starts[i] = (performance.now() - (rec ? Mic.t0 : t0)) / 1000 + 0.05; } }); await sleep(600); }
    finally { AU.el.muted = false; }
    R.end();""")
# blind mode: show a moving bar instead of the hidden words
rep("""  { k: 'shadow', icon: '🗣️', name: 'Shadow', en: 'Listen first. After the 2-second countdown, speak at the same time as the speaker.', ar: 'استمع أولًا، وبعد العدّ التنازلي تحدّث في الوقت نفسه مع المتحدث.' },
  { k: 'blind', icon: '🙈', name: 'Blind Shadow', en: 'Listen first, then shadow without the text — use only your ears! The text appears after you finish.', ar: 'استمع أولًا ثم ظلّل دون النص معتمدًا على أذنيك فقط! يظهر النص بعد أن تنتهي.' },
  { k: 'run', icon: '🎬', name: 'Full Run', en: 'Listen to the whole conversation, then shadow all the lines without stopping.', ar: 'استمع إلى المحادثة كاملة، ثم ظلّل جميع الجمل دون توقف.' }""",
"""  { k: 'shadow', icon: '🗣️', name: 'Shadow', en: 'Listen first. After the 2-second countdown, say the line as the words light up at the speaker’s speed. Only your voice is recorded.', ar: 'استمع أولًا، وبعد العدّ التنازلي قل الجملة والكلمات تُضاء بسرعة المتحدث. يُسجَّل صوتك وحدك.' },
  { k: 'blind', icon: '🙈', name: 'Blind Shadow', en: 'Listen first, then say the line from memory — no text and no sound; the hidden words light up one by one at the speaker’s speed. The text appears after you finish.', ar: 'استمع أولًا، ثم قل الجملة من الذاكرة دون نص ودون صوت؛ تُضاء الكلمات المخفية واحدة تلو الأخرى بسرعة المتحدث. يظهر النص بعد أن تنتهي.' },
  { k: 'run', icon: '🎬', name: 'Full Run', en: 'Listen to the whole conversation, then say all the lines without stopping as the words light up. Only your voice is recorded.', ar: 'استمع إلى المحادثة كاملة، ثم قل جميع الجمل دون توقف والكلمات تُضاء. يُسجَّل صوتك وحدك.' }""")
# headphones are no longer needed while recording
rep("""    ${S.mode >= 2 ? `<label class="chip"><input type="checkbox" id="hp" ${set.hp ? 'checked' : ''}> 🎧 I’m using headphones</label>` : ''}
""", "")
rep("""      ${!Store.data.settings.hp && md !== 'echo' ? '<p class="honest">Without headphones, the microphone may also hear the speaker, so the start and speed can look better than they were.</p>' : ''}
""", "")
# picture credit
rep("""24 units · v${APP_VER}</p>`;""", """24 units · v${APP_VER}<br><span style="font-size:.75rem">Pictures: Fluent Emoji © Microsoft (MIT licence)</span></p>`;""")
rep("const APP_VER = '1.1.0';", "const APP_VER = '1.2.0';")
open(p, 'w', encoding='utf-8').write(s)
print('v1.2 patched')
