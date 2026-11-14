#!/usr/bin/env python3
"""Word timings for every draft clip, from Kokoro's own duration predictor.
Writes platform/audio/timings.js:  window.LSP_TIMINGS = {"g3/u1/l1/01.mp3": [[start,end], ...], ...}
(one [start,end] in seconds per spoken word of the clip's TTS text).
"""
import json, hashlib, re, sys
import numpy as np, onnxruntime as ort, soundfile as sf
from kokoro_onnx import Kokoro

ROOT = "/home/claude/lsp"; CACHE = "/home/claude/build/wavcache"; M = "/home/claude/models"
SPEED = {"3": 0.88, "4": 0.92, "5": 0.96, "6": 1.0}
SR = 24000; HOP = 600
k = Kokoro(f"{M}/kokoro-v1.0.onnx", f"{M}/voices-v1.0.bin")
dur = ort.InferenceSession(f"{M}/kokoro_durations.onnx", providers=["CPUExecutionProvider"])
vocab = k.tokenizer.vocab
man = json.load(open(f"{ROOT}/build/manifest.json", encoding="utf-8"))
LETTER = re.compile(r"[^\W_]", re.U)

def word_spans(text, voice, lang, speed):
    ph = " ".join(k.tokenizer.phonemize(text, lang).split())
    chars = [c for c in ph if c in vocab]
    toks = [vocab[c] for c in chars]
    style = k.voices[voice][len(toks) - 1]
    d = dur.run(None, {"tokens": np.array([[0, *toks, 0]], dtype=np.int64),
                       "style": np.asarray(style, dtype=np.float32),
                       "speed": np.array([speed], dtype=np.float32)})[0].ravel()
    edges = np.concatenate([[0], np.cumsum(d)]) * HOP / SR   # edges[i] = start of token i (0 = pad)
    words, cur = [], []
    for i, c in enumerate(chars):
        if c == " ":
            if cur: words.append(cur); cur = []
        else:
            cur.append((i + 1, c))
    if cur: words.append(cur)
    spans = []
    for w in words:
        letters = [(ti, c) for ti, c in w if LETTER.match(c) or c in "ˈˌːəɪʊæʌɑɔɜθðʃʒŋɚɐᵻ"]
        if not letters: continue
        spans.append([edges[letters[0][0]], edges[letters[-1][0] + 1]])
    return spans, edges[1], len(d)

out, errs = {}, []
for n, c in enumerate(man):
    g = c["path"].split("/")[0][1:]
    spans, first, _ = word_spans(c["text"], c["voice"], c["lang"], SPEED[g])
    if not spans: continue
    key = hashlib.md5(f"{c['voice']}|{c['text']}|{SPEED[g]}".encode()).hexdigest()[:12]
    x, _ = sf.read(f"{CACHE}/{key}.wav", dtype="float32")
    idx = np.where(np.abs(x) > 0.02)[0]
    onset, offset = idx[0] / SR, idx[-1] / SR          # speech start/end in the final clip
    shift = onset - first
    sp = [[a + shift, b + shift] for a, b in spans]
    fr = int(0.02 * SR); env = np.array([np.sqrt(np.mean(x[i:i + fr] ** 2)) for i in range(0, len(x) - fr, fr)])
    thr = 0.06 * env.max()
    for w in sp:   # trim word ends that run into a following pause
        i0, i1 = int(w[0] / 0.02), min(int(w[1] / 0.02) + 1, len(env))
        loud = np.where(env[i0:i1] > thr)[0]
        if len(loud): w[1] = max(w[0] + 0.08, min(w[1], (i0 + loud[-1] + 1) * 0.02 + 0.03))
    sp = [[round(a, 2), round(b, 2)] for a, b in sp]
    errs.append(offset - sp[-1][1])                     # predicted vs real speech end
    out[c["path"]] = sp
    if n % 400 == 0: print(n, "/", len(man), flush=True)
errs = np.array(errs)
print(f"clips {len(out)}; end-alignment error: median {np.median(errs):+.3f}s, 90% within ±{np.percentile(np.abs(errs), 90):.3f}s")
with open(f"{ROOT}/platform/audio/timings.js", "w") as f:
    f.write("window.LSP_TIMINGS=" + json.dumps(out, separators=(",", ":")) + ";\n")
print("wrote timings.js")
