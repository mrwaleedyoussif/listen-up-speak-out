"""v1.10.1: home banner — the name block is centred; Settings / Switch user (and the teacher's Dashboard)
sit under the left logo, and the "Designed by" chip sits under the right logo.
Run once:  python3 tools/app/patch_v1101.py"""
import os, json
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda p: open(p, encoding='utf-8').read()
wr = lambda p, s: open(p, 'w', encoding='utf-8').write(s)


def one(s, a, b, n=1, where=''):
    c = s.count(a)
    assert c == n, f'{where}: expected {n} x {a[:90]!r}, found {c}'
    return s.replace(a, b)


W = 'index.html'
p = P('www', 'index.html'); s = rd(p)

# --- markup: logo + buttons | centred name block | logo + designer chip
BY = """<div class="byline mini" title="تصميم وإعداد: وليد يوسف"><img class="by-ph" src="img/waleed-youssef.jpg" alt="Waleed Youssef" width="38" height="38"><div class="by-tx"><span class="by-k">Designed by</span><b>Waleed Youssef</b></div></div>"""
CT = """<div class="ctrls">${T ? '<button class="btn sm" id="wDash">📊 Dashboard</button>' : ''}<button class="btn sm" id="wSet">⚙️ Settings</button><button class="btn sm" id="wOut">🔁 Switch user</button>"""
s = one(s, """      ${LG('l')}
      <div class="hub-tx">""", """      <div class="hub-side hub-l">${LG('l')}""" + CT + """</div></div>
      <div class="hub-tx">""", 1, W)
s = one(s, """        <p class="ar" style="margin:0">مرحبًا! اختر القسم لتبدأ التعلّم.</p>
        """ + CT + BY + """</div>
      </div>
      ${LG('r')}
    </div>""", """        <p class="ar" style="margin:0">مرحبًا! اختر القسم لتبدأ التعلّم.</p>
      </div>
      <div class="hub-side hub-r">${LG('r')}""" + BY + """</div>
    </div>""", 1, W)

# --- styles
s = one(s, """.hub-in{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:26px}
.hub .ctrls{align-items:center}
.hub .byline.mini{align-self:center;margin-left:auto}
""", """.hub-in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,auto) minmax(0,1fr);align-items:start;gap:26px}
.hub-side{display:flex;flex-direction:column;align-items:center;gap:12px;width:180px;max-width:100%}
.hub-l{justify-self:start}.hub-r{justify-self:end}
.hub .lg img{height:132px}
.hub-tx{align-self:center;text-align:center}
.hub-tx .ar{text-align:center}
.hub-side .ctrls{flex-direction:column;align-items:stretch;gap:6px;margin-top:0}
.hub-side .ctrls .btn{justify-content:center}
.hub .byline.mini{align-self:center}
.hub .byline.mini .by-tx b{white-space:nowrap}
.hub-hi{line-height:1.35}
""", 1, W)
s = one(s, "@media (max-width:900px){.lg img{height:118px}.authhero .lg img{height:108px}.hub-in{gap:18px}.authhero{gap:14px}}",
        "@media (max-width:900px){.lg img,.hub .lg img{height:112px}.authhero .lg img{height:108px}.hub-in{gap:18px}.authhero{gap:14px}.hub-side{width:156px}.hub .byline.mini{padding:5px 11px 5px 5px;gap:7px}.hub .byline.mini .by-ph{width:30px;height:30px}.hub .byline.mini .by-tx b{font-size:.8rem}}", 1, W)
s = one(s, """  .hub-in .lg-l,.authhero .lg-l{justify-self:start}.hub-in .lg-r,.authhero .lg-r{justify-self:end;grid-column:2;grid-row:1}
  .hub-tx,.ah-tx{grid-column:1/-1;grid-row:2}
  .lg img,.authhero .lg img{height:92px}
  .hub .byline.mini{margin-left:0}
""", """  .authhero .lg-l{justify-self:start}.authhero .lg-r{justify-self:end;grid-column:2;grid-row:1}
  .hub-l,.hub-r{justify-self:center;width:auto}.hub-r{grid-column:2;grid-row:1}
  .hub-tx,.ah-tx{grid-column:1/-1;grid-row:2}
  .lg img,.authhero .lg img,.hub .lg img{height:92px}
""", 1, W)
# --- the waving-hand emoji shared its class name with the audio player's sound bars (since v1.9): keep the hand's style to the hand
s = one(s, ".wave{display:inline-block;transform-origin:70% 80%;animation:waveH 1.9s ease-in-out infinite}",
        ".hub-hi .wave,.auth-head .wave,.bye .wave{display:inline-block;height:auto;transform-origin:70% 80%;animation:waveH 1.9s ease-in-out infinite}", 1, W)
s = one(s, "const APP_VER = '1.10.0';", "const APP_VER = '1.10.1';", 1, W)
wr(p, s)

t = rd(P('package.json')); wr(P('package.json'), one(t, '"version": "1.10.0"', '"version": "1.10.1"', 1, 'package.json'))
t = rd(P('package-lock.json')); assert t.count('"version": "1.10.0"') >= 2
wr(P('package-lock.json'), t.replace('"version": "1.10.0"', '"version": "1.10.1"', 2))
cl = json.loads(rd(P('tools', 'app', 'changelog.json'))); assert '1.10.1' not in cl
cl = {'1.10.1': {
    'en': ['Home banner: the app name and the welcome line are now centred; Settings and Switch user are under the left logo, and “Designed by Waleed Youssef” is under the right logo.',
           'Fixed: the sound bars in the audio player no longer tilt.'],
    'ar': ['لافتة الصفحة الرئيسية: اسم البرنامج وعبارة الترحيب في الوسط، وزرّا الإعدادات وتبديل المستخدم تحت الشعار الأيسر، و«تصميم وليد يوسف» تحت الشعار الأيمن.',
           'إصلاح: أعمدة الصوت في مشغّل التسجيلات لم تعد تميل.']}, **cl}
wr(P('tools', 'app', 'changelog.json'), json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('v1.10.1 patched')
