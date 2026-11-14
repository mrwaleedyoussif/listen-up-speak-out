"""Brand v1.1: new logo, designer credit 'Mr. Waleed Youssef' with photo and seal."""
import sys, re
p = sys.argv[1] if len(sys.argv) > 1 else 'www/index.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:90]); s = s.replace(old, new)
EMB = open('/home/claude/brand/emblem_inline.txt').read()
# 1. logo
i = s.index('const LOGO = `'); j = s.index('`;', i)
s = s[:i] + 'const LOGO = `' + EMB + s[j:]
# 2. header byline
rep('<span>Listen Up! Speak Out!<small>Listening & Speaking · Grades 3–6</small></span>', '<span>Listen Up! Speak Out!<small>by Mr. Waleed Youssef · Grades 3–6</small></span>')
# 3. title
rep('<title>Listen Up! Speak Out! — Elementary Listening & Speaking Program</title>', '<title>Listen Up! Speak Out! — by Mr. Waleed Youssef</title>')
rep('with Arabic support.">', 'with Arabic support. Designed by Mr. Waleed Youssef.">')
# 4. hero with the designer card
rep('''    <span class="pill" style="background:rgba(255,255,255,.22);color:#fff">Elementary · Grades 3–6 · CEFR A1 → A2+</span>
    <h1 style="margin-top:10px">Listen Up! Speak Out!</h1>
    <p>A complete listening and speaking program: real audio, smart listening tasks, pronunciation games, shadowing and role-plays — with Arabic support.</p>
    <p class="ar" style="color:#fff;text-align:left;direction:rtl">برنامج متكامل لتنمية مهارتي الاستماع والتحدث للمرحلة الابتدائية</p>
  </section>''', '''    <div class="hero-in"><div class="hero-tx">
    <span class="pill" style="background:rgba(255,255,255,.22);color:#fff">Elementary · Grades 3–6 · CEFR A1 → A2+</span>
    <h1 style="margin-top:10px"><span class="hero-logo">${LOGO}</span>Listen Up! Speak Out!</h1>
    <p>A complete listening and speaking program: real audio, smart listening tasks, pronunciation games, shadowing and role-plays — with Arabic support.</p>
    <p class="ar" style="color:#fff;text-align:left;direction:rtl">برنامج متكامل لتنمية مهارتي الاستماع والتحدث للمرحلة الابتدائية</p>
    </div>
    <div class="byline"><img class="by-ph" src="img/waleed-youssef.jpg" alt="Mr. Waleed Youssef" width="96" height="96"><div class="by-tx"><span class="by-k">Designed by</span><b>Mr. Waleed Youssef</b><span class="by-t">English Teacher & Curriculum Designer</span><span class="by-ar" lang="ar" dir="rtl">تصميم وإعداد: أ. وليد يوسف</span></div></div>
    </div>
  </section>''')
# 5. about the designer + footer
rep('''  <div id="appBox"></div>
  <p class="foot">Listen Up! Speak Out! · Designed for Mr. Waleed Yussuf · 72 listening lessons · 48 speaking lessons · 24 units · v${APP_VER}</p>`;''',
'''  <div id="appBox"></div>
  <section class="card about">
    <img class="ab-ph" src="img/waleed-youssef.jpg" alt="Mr. Waleed Youssef" width="128" height="128">
    <div class="ab-tx"><span class="by-k" style="color:var(--muted)">About the designer</span><h3>Mr. Waleed Youssef</h3>
      <p>Mr. Waleed Youssef is an English language teacher, a trainer of STEP and IELTS candidates, and a curriculum and materials designer. He created <b>Listen Up! Speak Out!</b> so that young learners listen with confidence and speak with joy.</p>
      <p class="ar ar-block">الأستاذ وليد يوسف معلّم لغة إنجليزية، ومدرّب لاختبارَي STEP وIELTS، ومصمّم مناهج ومواد تعليمية. صمّم هذا البرنامج ليستمع المتعلّمون الصغار بثقة ويتحدّثوا بمتعة.</p></div>
    <img class="ab-seal" src="img/seal.svg" alt="Mr. Waleed Youssef seal" width="112" height="112">
  </section>
  <p class="foot"><img src="img/seal.svg" alt="" width="22" height="22" style="vertical-align:-6px;margin-right:6px">Listen Up! Speak Out! · Designed by Mr. Waleed Youssef · 72 listening lessons · 48 speaking lessons · 24 units · v${APP_VER}</p>`;''')
# 6. certificate: logo, designer seal and signature
rep('''<div class="cert"><div style="font-size:3rem">🏅</div><h1>Certificate of Achievement</h1>''', '''<div class="cert"><div class="cert-logo">${LOGO}</div><h1>Certificate of Achievement</h1>''')
rep('''    <p style="margin-top:26px">______________________<br><span class="muted">Teacher</span></p></div>''', '''    <div class="cert-sign"><div><span class="line"></span><span class="muted">Teacher</span></div><img src="img/seal.svg" alt="Seal of Mr. Waleed Youssef" width="96" height="96"><div><span class="signame">Mr. Waleed Youssef</span><span class="line"></span><span class="muted">Program Designer</span></div></div>
    <p class="cert-foot">Listen Up! Speak Out! · Designed by Mr. Waleed Youssef</p></div>''')
# 7. CSS
rep('''/* studio v1.1: phases''', '''/* brand v1.1: logo, designer card, about, certificate */
.brand svg{border-radius:10px}
.hero-in{display:flex;gap:22px;align-items:center;justify-content:space-between;position:relative;z-index:1}
.hero-tx{flex:1 1 auto;min-width:0}
.hero-logo svg{width:1.15em;height:1.15em;vertical-align:-.2em;margin-right:.3em;filter:drop-shadow(0 4px 10px rgba(0,0,0,.18));border-radius:.28em}
.byline{flex:none;display:flex;align-items:center;gap:14px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.35);border-radius:22px;padding:14px 18px 14px 14px;backdrop-filter:blur(6px);box-shadow:0 10px 30px rgba(20,25,60,.18)}
.by-ph{width:96px;height:96px;border-radius:50%;object-fit:cover;background:#fff;border:4px solid #F2C14E;box-shadow:0 0 0 3px rgba(255,255,255,.9),0 8px 18px rgba(0,0,0,.2)}
.by-tx{display:flex;flex-direction:column;line-height:1.25}
.by-k{font-size:.74rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;opacity:.9}
.by-tx b{font-family:var(--fh);font-size:1.35rem;font-weight:800}
.by-t{font-size:.86rem;font-weight:700;opacity:.92}
.by-ar{font-family:var(--fa);font-size:.88rem;margin-top:2px;opacity:.95}
.about{display:flex;gap:20px;align-items:center;margin-top:16px;border-top:5px solid #1D3F9E}
.ab-ph{width:128px;height:128px;border-radius:50%;object-fit:cover;flex:none;border:4px solid #F2C14E;box-shadow:0 0 0 3px #fff,0 8px 20px rgba(29,63,158,.22)}
.ab-tx{flex:1;min-width:0}.ab-tx h3{font-size:1.45rem;margin:.1rem 0 .3rem;color:#1D3F9E}.ab-tx p{margin:.3rem 0}
.ab-seal{width:112px;height:112px;flex:none}
.cert-logo svg{width:84px;height:84px;border-radius:20px;box-shadow:0 8px 20px rgba(29,63,158,.25)}
.cert-sign{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-top:26px}
.cert-sign>div{display:flex;flex-direction:column;align-items:center;flex:1}
.cert-sign .line{display:block;width:180px;max-width:100%;border-bottom:2px solid var(--ink2);margin-bottom:4px}
.cert-sign .signame{font-family:var(--fh);font-weight:800;font-size:1.2rem;color:#1D3F9E;margin-bottom:2px}
.cert-sign img{width:96px;height:96px}
.cert-foot{font-size:.8rem;color:var(--muted);margin:16px 0 0}
@media (max-width:760px){.hero-in{flex-direction:column;align-items:flex-start}.byline{align-self:stretch}.by-ph{width:76px;height:76px}.about{flex-direction:column;text-align:center}.ab-seal{width:90px;height:90px}}
/* studio v1.1: phases''')
open(p, 'w', encoding='utf-8').write(s)
print('brand patched')
