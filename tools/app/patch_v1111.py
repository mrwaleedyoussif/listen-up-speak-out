"""v1.11.1: the app opens on the sign-in and sign-up page. The first-run "Welcome! create the teacher account" page is gone;
the teacher-account form is now reached from the Teacher button on the sign-in page (only while no teacher account exists).
Run once:  python3 tools/app/patch_v1111.py"""
import os, json
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda p: open(p, encoding='utf-8').read()
wr = lambda p, s: open(p, 'w', encoding='utf-8').write(s)


def one(s, a, b, n=1, where=''):
    c = s.count(a)
    assert c == n, f'{where}: expected {n} x {a[:90]!r}, found {c}'
    return s.replace(a, b)


W = 'index.html'; p = P('www', 'index.html'); s = rd(p)
# --- no forced first-run page: without a signed-in user the app shows the sign-in / sign-up page
s = one(s, """  if (!Auth.ready()) { if (S.view !== 'setup') { for (const k of Object.keys(S)) delete S[k]; S.view = 'setup'; } }
  else if (!Auth.user()) { if (S.view !== 'signin') { for (const k of Object.keys(S)) delete S[k]; S.view = 'signin'; } }""",
        """  // nobody signed in: the sign-in and sign-up page. The teacher-account form opens from its Teacher button, only while no teacher account exists.
  if (!Auth.user()) { if (S.view !== 'signin' && !(S.view === 'setup' && !Auth.ready())) { for (const k of Object.keys(S)) delete S[k]; S.view = 'signin'; } }""", 1, W)
# --- the teacher-account form: a normal page with a way back
s = one(s, """<div class="auth-head"><span class="big wave">👋</span><div><h1>Welcome!</h1><span class="ar">مرحبًا بك في برنامج From Zero To Hero</span></div></div>
    <p>First, create the <b>teacher or parent account</b>. It protects the teacher dashboard, the settings and the backups. Students then sign up with their name and a 4-digit PIN.""",
        """<div class="auth-head"><span class="big">🔑</span><div><h1>Create the teacher account</h1><span class="ar">إنشاء حساب المعلم</span></div></div>
    <p>The <b>teacher or parent account</b> protects the teacher dashboard, the settings and the backups. Students sign up on the first page with their name and a 4-digit PIN.""", 1, W)
s = one(s, "<p class=\"ar ar-block\">أولًا، أنشئ حساب المعلم أو ولي الأمر. يحمي هذا الحساب لوحة المعلم والإعدادات والنسخ الاحتياطية، ثم يسجّل الطلاب بأسمائهم ورمز من 4 أرقام.</p>",
        "<p class=\"ar ar-block\">حساب المعلم أو ولي الأمر يحمي لوحة المعلم والإعدادات والنسخ الاحتياطية. يسجّل الطلاب من الصفحة الأولى بأسمائهم ورمز من 4 أرقام.</p>", 1, W)
s = one(s, """      <button class="btn" type="submit" id="stB">🔐 Create the teacher account</button>
    </form>""", """      <div class="ctrls" style="justify-content:flex-start"><button class="btn" type="submit" id="stB">🔐 Create the teacher account</button><button class="btn sec" type="button" id="stX">← Back <span class="ar">رجوع</span></button></div>
    </form>""", 1, W)
s = one(s, "  bindEyes(m); bindMeter($('#stP', m), $('#stM', m));", "  bindEyes(m); bindMeter($('#stP', m), $('#stM', m));\n  $('#stX', m).onclick = () => go('signin');", 1, W)
# --- sign-in page: clearly a sign-in and sign-up page; the Teacher button creates the account when there is none yet
s = one(s, """<div class="auth-head"><span class="big wave">👋</span><div><h1>Who is learning today?</h1><span class="ar">من يتعلّم اليوم؟</span></div></div>""",
        """<div class="auth-head"><span class="big wave">👋</span><div><h1>Sign in or sign up</h1><span class="ar">سجّل الدخول أو أنشئ حسابًا جديدًا</span></div></div>""", 1, W)
s = one(s, """<p class="muted" style="margin:.2rem 0 0">Tap your name, then type your PIN. <span class="ar">اضغط على اسمك ثم اكتب رمزك.</span></p>""",
        """<p class="muted" style="margin:.2rem 0 0"><b>Sign in:</b> tap your name, then type your PIN. <b>Sign up:</b> press “New student”. <span class="ar">للدخول: اضغط على اسمك ثم اكتب رمزك. للتسجيل: اضغط «طالب جديد».</span></p>""", 1, W)
s = one(s, """      <button class="btn sec" id="tB">🔑 Teacher sign in <span class="ar">دخول المعلم</span></button>""",
        """      <button class="btn sec" id="tB">${Auth.ready() ? '🔑 Teacher sign in <span class="ar">دخول المعلم</span>' : '🔑 Teacher — create the account <span class="ar">إنشاء حساب المعلم</span>'}</button>""", 1, W)
s = one(s, "  $('#tB', m).onclick = () => teacherSignIn();\n};", "  $('#tB', m).onclick = () => Auth.ready() ? teacherSignIn() : go('setup');\n};", 1, W)
s = one(s, 'function teacherSignIn(after) {\n', "function teacherSignIn(after) {\n  // no teacher account on this device yet: it is created from the sign-in page\n  if (!Auth.ready()) { Auth.signOut('There is no teacher account yet. Press “Teacher — create the account”.'); render(); return; }\n", 1, W)
s = one(s, "const APP_VER = '1.11.0';", "const APP_VER = '1.11.1';", 1, W)
wr(p, s)

# --- Grammar and Vocabulary: every visitor is signed in now, so nobody gets teacher tools without the teacher account
for f in (P('www', 'gv', 'host.js'), P('tools', 'app', 'add_gv.py')):
    t = rd(f)
    t = one(t, "  if (ready && !ses) { location.replace('../index.html'); return; }       // accounts are set up and nobody is signed in",
            "  if (!ses) { location.replace('../index.html'); return; }       // nobody is signed in: back to the sign-in page", 1, f)
    t = one(t, "role: ses ? ses.role : (ready ? 'student' : 'teacher'), locked: ready };", "role: ses.role, locked: true };", 1, f)
    wr(f, t)

t = rd(P('package.json')); wr(P('package.json'), one(t, '"version": "1.11.0"', '"version": "1.11.1"', 1, 'package.json'))
t = rd(P('package-lock.json')); assert t.count('"version": "1.11.0"') >= 2
wr(P('package-lock.json'), t.replace('"version": "1.11.0"', '"version": "1.11.1"', 2))
cl = json.loads(rd(P('tools', 'app', 'changelog.json'))); assert '1.11.1' not in cl
cl = {'1.11.1': {
    'en': ['The app now opens on the sign-in and sign-up page. The first “Welcome” page is removed; the teacher account is created from the Teacher button on that page.'],
    'ar': ['يبدأ البرنامج الآن بصفحة تسجيل الدخول والتسجيل. أُزيلت صفحة «مرحبًا» الأولى، ويُنشأ حساب المعلم من زر المعلم في تلك الصفحة.']}, **cl}
wr(P('tools', 'app', 'changelog.json'), json.dumps(cl, ensure_ascii=False, indent=1) + '\n')
print('v1.11.1 patched')
