#!/usr/bin/env python3
"""Build the web (artifact) edition: one audio sprite per lesson + sprites.js offsets.
Usage: python3 make_web.py  -> /home/claude/lsp/web/
"""
import json, os, shutil, subprocess, hashlib
import numpy as np, soundfile as sf

ROOT = "/home/claude/lsp"; WEB = os.environ.get("WEBOUT", f"{ROOT}/web"); CACHE = "/home/claude/build/wavcache"
SPEED = {"3": 0.88, "4": 0.92, "5": 0.96, "6": 1.0}; SR = 24000; GAP = 0.35
man = json.load(open(f"{ROOT}/build/manifest.json", encoding="utf-8"))
if os.environ.get("GRADES"): man = [c for c in man if c["path"].split("/")[0][1:] in os.environ["GRADES"].split(",")]
shutil.rmtree(WEB, ignore_errors=True); os.makedirs(f"{WEB}/sprites")
groups = {}
for c in man:
    d = "/".join(c["path"].split("/")[:3])  # g3/u1/l1
    groups.setdefault(d, []).append(c)
offsets = {}; total = 0
for d, clips in groups.items():
    segs = []; t = 0.0; name = d.replace("/", "") + ".mp3"
    for c in clips:
        g = c["path"].split("/")[0][1:]
        key = hashlib.md5(f"{c['voice']}|{c['text']}|{SPEED[g]}".encode()).hexdigest()[:12]
        x, sr = sf.read(f"{CACHE}/{key}.wav", dtype="float32")
        assert sr == SR
        offsets[c["path"]] = [f"sprites/{name}", round(t, 3), round(t + len(x) / SR, 3)]
        segs += [x, np.zeros(int(GAP * SR), np.float32)]
        t += len(x) / SR + GAP
    tmp = "/tmp/sprite.wav"; sf.write(tmp, np.concatenate(segs), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ac", "1", "-ar", "24000", "-codec:a", "libmp3lame",
                    "-b:a", "40k", f"{WEB}/sprites/{name}"], check=True)
    total += os.path.getsize(f"{WEB}/sprites/{name}")
with open(f"{WEB}/sprites.js", "w") as f:
    f.write("window.LSP_SPRITES=" + json.dumps(offsets, separators=(",", ":")) + ";\n")
shutil.copy(f"{ROOT}/platform/data.js", f"{WEB}/data.js")
os.makedirs(f"{WEB}/audio", exist_ok=True); shutil.copy(f"{ROOT}/platform/audio/timings.js", f"{WEB}/audio/timings.js")
html = open(f"{ROOT}/platform/index.html", encoding="utf-8").read()
html = html.replace('<script src="data.js"></script>', '<script src="data.js"></script>\n<script src="sprites.js"></script>')
open(f"{WEB}/index.html", "w", encoding="utf-8").write(html)
print(f"{len(groups)} sprites, {total/1e6:.1f} MB audio, {len(offsets)} clips mapped")
