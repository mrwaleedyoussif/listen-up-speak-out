"""Prepare www/ for every edition: writes audio/files.json (offline lists per grade)
and sw.js (service worker with a version taken from the app files).
Run after changing anything in www/ (or after re-voicing audio with ElevenLabs):
    python tools/app/build_www.py
"""
import hashlib, json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
WWW = os.path.join(ROOT, 'www')

def rel(p): return os.path.relpath(p, WWW).replace(os.sep, '/')

# 1. audio lists per grade
grades, ah = {}, hashlib.sha1()
for g in sorted(os.listdir(os.path.join(WWW, 'audio'))):
    gd = os.path.join(WWW, 'audio', g)
    if not (os.path.isdir(gd) and g.startswith('g')): continue
    fl, by = [], 0
    for dp, dn, fn in os.walk(gd):
        dn.sort()
        for f in sorted(fn):
            if f.endswith('.mp3'):
                p = os.path.join(dp, f); fl.append(rel(p)); by += os.path.getsize(p)
                ah.update(rel(p).encode()); ah.update(open(p, 'rb').read())
    grades[g[1:]] = {'bytes': by, 'files': fl}
AV = ah.hexdigest()[:10]
json.dump({'v': AV, 'grades': grades}, open(os.path.join(WWW, 'audio', 'files.json'), 'w'), separators=(',', ':'))

# 2. app shell files (everything except audio clips and the service worker)
shell = ['index.html']
for dp, dn, fn in os.walk(WWW):
    dn.sort()
    for f in sorted(fn):
        p = os.path.join(dp, f); r = rel(p)
        if r.endswith('.mp3') or r in ('sw.js', 'index.html', 'version.json') or r.startswith(('icons/shots/', 'print/')) or f.startswith('.'): continue
        shell.append(r)
vh = hashlib.sha1()
for r in shell: vh.update(r.encode()); vh.update(open(os.path.join(WWW, r), 'rb').read())
V = vh.hexdigest()[:10]
tpl = open(os.path.join(ROOT, 'tools', 'app', 'sw.template.js')).read()
sw = tpl.replace('__VERSION__', V).replace('__AUDIO_VERSION__', AV).replace('__SHELL_FILES__', json.dumps(shell))
open(os.path.join(WWW, 'sw.js'), 'w').write(sw)
tot = sum(g['bytes'] for g in grades.values())
print(f'app version {V} · audio version {AV} · {len(shell)} app files · {sum(len(g["files"]) for g in grades.values())} audio files ({tot/1048576:.1f} MB)')

# 3. version.json: the newest version and what is new (the apps check it for updates).
#    In GitHub Actions, tools/app/release_info.py adds the download links of the release files.
import datetime
pkg = json.load(open(os.path.join(ROOT, 'package.json')))
log = json.load(open(os.path.join(ROOT, 'tools', 'app', 'changelog.json'), encoding='utf-8'))
ver = pkg['version']
vj = {'version': ver, 'date': datetime.date.today().isoformat(), 'notes': log.get(ver, {'en': [], 'ar': []}), 'files': {}}
json.dump(vj, open(os.path.join(WWW, 'version.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'version.json: {ver}')
