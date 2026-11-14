#!/usr/bin/env python3
"""Check that every clip in the manifest exists and has a plausible duration."""
import json, os, sys, hashlib
import soundfile as sf
ROOT = "/home/claude/lsp"; CACHE = "/home/claude/build/wavcache"
SPEED = {"3": 0.88, "4": 0.92, "5": 0.96, "6": 1.0}
grades = sys.argv[1:] or ["3", "4", "5", "6"]
man = [c for c in json.load(open(f"{ROOT}/build/manifest.json")) if c["path"].split("/")[0][1:] in grades]
missing, odd, total = [], [], 0.0
tracks = set()
for c in man:
    p = f"{ROOT}/platform/audio/{c['path']}"
    if not os.path.exists(p) or os.path.getsize(p) < 500:
        missing.append(c["path"]); continue
    g = c["path"].split("/")[0][1:]
    key = hashlib.md5(f"{c['voice']}|{c['text']}|{SPEED[g]}".encode()).hexdigest()[:12]
    d = sf.info(f"{CACHE}/{key}.wav").duration; total += d
    cps = len(c["text"]) / max(d - 0.2, 0.05)
    if d < 0.45 or cps > 24 or (len(c["text"]) > 25 and cps < 6):
        odd.append((c["path"], round(d, 2), round(cps, 1), c["text"][:50]))
    if "track" in c: tracks.add(c["track"])
mt = [t for t in tracks if not os.path.exists(f"{ROOT}/platform/audio/{t}")]
print(f"grades {grades}: {len(man)} clips, missing {len(missing)}, tracks {len(tracks)} (missing {len(mt)}), audio {total/60:.1f} min")
print("odd durations:", len(odd))
for o in odd[:15]: print("  ", o)
