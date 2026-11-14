"""Adds the download links of a GitHub release to www/version.json (run in GitHub Actions after the release).
Usage: python3 tools/app/release_info.py v1.4.0      (needs the gh CLI and GH_TOKEN)"""
import json, os, subprocess, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
VJ = os.path.join(ROOT, 'www', 'version.json')
tag = sys.argv[1]
vj = json.load(open(VJ, encoding='utf-8'))
try:
    rel = json.loads(subprocess.run(['gh', 'api', f'repos/{os.environ.get("GITHUB_REPOSITORY", "mrwaleedyoussif/listen-up-speak-out")}/releases/tags/{tag}'],
                                    capture_output=True, text=True, check=True).stdout)
except Exception as e:
    print('no release for', tag, '-', e); rel = {'assets': []}
files = {}
for a in rel.get('assets', []):
    n, u = a['name'], a['browser_download_url']
    if n.endswith('.apk'): files['apk'] = u
    elif n.endswith('.ipa'): files['ipa'] = u
    elif n.endswith('.exe') and 'Setup' in n: files['setup'] = u
    elif n.endswith('.exe') and 'Portable' in n: files['portable'] = u
if rel.get('html_url'): files['page'] = rel['html_url']
vj['files'] = files
json.dump(vj, open(VJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('version.json files:', ', '.join(files) or 'none')
