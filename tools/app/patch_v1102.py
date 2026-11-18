"""v1.10.2: home banner — Dashboard, Settings, Switch user and the "Designed by" chip form one row
along the bottom of the banner; the logos stand alone on the left and the right.
Run once:  python3 tools/app/patch_v1102.py"""
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
BY = """<div class="byline mini" title="تصميم وإعداد: وليد يوسف"><img class="by-ph" src="img/waleed-youssef.jpg" alt="Waleed Youssef" width="38" height="38"><div class="by-tx"><span class="by-k">Designed by</span><b>Waleed Youssef</b></div></div>"""
CT = """${T ? '<button class="btn sm" id="wDash">📊 Dashboard</button>' : ''}<button class="btn sm" id="wSet">⚙️ Settings</button><button class="btn sm" id="wOut">🔁 Switch user</button>"""
# on a phone the buttons show their icon only, so the row stays on one line
CT2 = """${T ? '<button class="btn sm" id="wDash" aria-label="Dashboard" title="Dashboard">📊<span class="bl"> Dashboard</span></button>' : ''}<button class="btn sm" id="wSet" aria-label="Settings" title="Settings">⚙️<span class="bl"> Settings</span></button><button class="btn sm" id="wOut" aria-label="Switch user" title="Switch user">🔁<span class="bl"> Switch user</span></button>"""
s = one(s, """      <div class="hub-side hub-l">${LG('l')}<div class="ctrls">""" + CT + """</div></div>
""", """      ${LG('l')}
""", 1, W)
s = one(s, """      <div class="hub-side hub-r">${LG('r')}""" + BY + """</div>
""", """      ${LG('r')}
      <div class="ctrls hub-bar">""" + CT2 + BY + """</div>
""", 1, W)
s = one(s, """.hub-in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,auto) minmax(0,1fr);align-items:start;gap:26px}
.hub-side{display:flex;flex-direction:column;align-items:center;gap:12px;width:180px;max-width:100%}
.hub-l{justify-self:start}.hub-r{justify-self:end}
""", """.hub-in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,auto) minmax(0,1fr);align-items:center;gap:18px 26px}
.hub-in>.lg-l{justify-self:start}.hub-in>.lg-r{justify-self:end}
.hub .hub-bar{grid-column:1/-1;justify-content:center;align-items:center;gap:10px;margin-top:0;padding-top:16px;border-top:1px solid rgba(255,255,255,.2)}
""", 1, W)
s = one(s, """.hub-side .ctrls{flex-direction:column;align-items:stretch;gap:6px;margin-top:0}
.hub-side .ctrls .btn{justify-content:center}
""", "", 1, W)
s = one(s, ".authhero{gap:14px}.hub-side{width:156px}.hub .byline.mini{padding:5px 11px 5px 5px;gap:7px}.hub .byline.mini .by-ph{width:30px;height:30px}.hub .byline.mini .by-tx b{font-size:.8rem}}",
        ".authhero{gap:14px}}", 1, W)
s = one(s, "  .hub-l,.hub-r{justify-self:center;width:auto}.hub-r{grid-column:2;grid-row:1}\n",
        "  .hub-in>.lg-r{grid-column:2;grid-row:1}.hub .hub-bar{grid-row:3;gap:8px;padding-top:14px;flex-wrap:nowrap}.hub-bar .bl{display:none}.hub-bar .btn{min-width:44px;justify-content:center;font-size:1.1rem}\n  .hub .byline.mini{padding:5px 11px 5px 5px;gap:7px}.hub .byline.mini .by-ph{width:30px;height:30px}.hub .byline.mini .by-tx b{font-size:.8rem}\n", 1, W)
s = one(s, "const APP_VER = '1.10.1';", "const APP_VER = '1.10.2';", 1, W)
wr(p, s)

t = rd(P('package.json')); wr(P('package.json'), one(t, '"version": "1.10.1"', '"version": "1.10.2"', 1, 'package.json'))
t = rd(P('package-lock.json')); assert t.count('"version": "1.10.1"') >= 2
wr(P('package-lock.json'), t.replace('"version": "1.10.1"', '"version": "1.10.2"', 2))
cl = json.loads(rd(P('tools', 'app', 'changelog.json'))); assert '1.10.2' not in cl
cl = {'1.10.2': {
    'en': ['Home banner: Dashboard, Settings, Switch user and “Designed by Waleed Youssef” are now in one row along the bottom of the banner.'],
    'ar': ['لافتة الصفحة الرئيسية: لوحة المتابعة والإعدادات وتبديل المستخدم و«تصميم وليد يوسف» في صف واحد أسفل اللافتة.']}, **cl}
wr(P('tools', 'app', 'changelog.json'), json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('v1.10.2 patched')
