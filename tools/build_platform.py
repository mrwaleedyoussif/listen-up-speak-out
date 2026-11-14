#!/usr/bin/env python3
"""Write platform/data.js from build/program.json (slimmed for the browser)."""
import json, os, sys

root = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/lsp"
prog = json.load(open(os.path.join(root, "build/program.json"), encoding="utf-8"))

DROP = {"tts", "hash"}

def slim(o):
    if isinstance(o, dict):
        return {k: slim(v) for k, v in o.items() if k not in DROP}
    if isinstance(o, list):
        return [slim(x) for x in o]
    return o

data = slim(prog)
out = os.path.join(root, "platform/data.js")
with open(out, "w", encoding="utf-8") as f:
    f.write("/* Listen Up! Speak Out! — program content (generated) */\n")
    f.write("window.LSP_DATA = ")
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")
print("data.js", round(os.path.getsize(out) / 1024), "KB")
