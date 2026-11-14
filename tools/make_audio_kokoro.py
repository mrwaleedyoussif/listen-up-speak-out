#!/usr/bin/env python3
"""Draft audio generator (open-source Kokoro voices).
Reads build/manifest.json, writes MP3 clips + assembled tracks into platform/audio/.
Skips clips whose text has not changed. Usage:
  python3 make_audio_kokoro.py build/manifest.json platform/audio [grade ...]
"""
import json, os, sys, subprocess, time, hashlib
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

MODEL = "/home/claude/models/kokoro-v1.0.onnx"
VOICES = "/home/claude/models/voices-v1.0.bin"
CACHE = "/home/claude/build/wavcache"
SPEED = {"3": 0.88, "4": 0.92, "5": 0.96, "6": 1.0}
GAP = {"3": 0.85, "4": 0.75, "5": 0.65, "6": 0.6}
SR = 24000


def trim(x, thr=0.008):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(0.03 * SR)); b = min(len(x), idx[-1] + int(0.06 * SR))
    return x[a:b]


def norm(x, target_rms=0.085):
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    y = x * (target_rms / rms)
    peak = np.max(np.abs(y))
    if peak > 0.97:
        y = y * (0.97 / peak)
    return y.astype(np.float32)


def to_mp3(wav_path, mp3_path):
    os.makedirs(os.path.dirname(mp3_path), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path, "-ac", "1", "-ar", "24000",
                    "-codec:a", "libmp3lame", "-b:a", "48k", mp3_path], check=True)


def main():
    man_path, out_dir = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    man = json.load(open(man_path, encoding="utf-8"))
    if only:
        man = [c for c in man if c["path"].split("/")[0][1:] in only]
    os.makedirs(CACHE, exist_ok=True)
    k = Kokoro(MODEL, VOICES)
    t0 = time.time(); done = 0; made = 0; audio_sec = 0.0
    durations = {}
    dur_path = os.path.join(out_dir, "durations.json")
    if os.path.exists(dur_path):
        durations = json.load(open(dur_path))
    tracks = {}
    for c in man:
        g = c["path"].split("/")[0][1:]
        key = hashlib.md5(f"{c['voice']}|{c['text']}|{SPEED[g]}".encode()).hexdigest()[:12]
        wav = os.path.join(CACHE, key + ".wav")
        mp3 = os.path.join(out_dir, c["path"])
        if not os.path.exists(wav):
            s, sr = k.create(c["text"], voice=c["voice"], speed=SPEED[g], lang=c["lang"])
            s = norm(trim(np.asarray(s, dtype=np.float32)))
            s = np.concatenate([np.zeros(int(0.08 * SR), np.float32), s, np.zeros(int(0.12 * SR), np.float32)])
            sf.write(wav, s, SR)
            made += 1
        stamp = mp3 + ".src"
        if not (os.path.exists(mp3) and os.path.exists(stamp) and open(stamp).read() == key):
            to_mp3(wav, mp3)
            open(stamp, "w").write(key)
        info = sf.info(wav)
        durations[c["path"]] = round(info.duration, 2)
        audio_sec += info.duration
        if "track" in c:
            tracks.setdefault(c["track"], []).append((c["order"], wav, g))
        done += 1
        if done % 25 == 0:
            el = time.time() - t0
            print(f"{done}/{len(man)} clips  new={made}  audio={audio_sec/60:.1f} min  elapsed={el/60:.1f} min", flush=True)
            json.dump(durations, open(dur_path, "w"), indent=0)
    # assemble full tracks
    for tr, parts in tracks.items():
        parts.sort()
        g = parts[0][2]
        gap = np.zeros(int(GAP[g] * SR), np.float32)
        seg = []
        for _, w, _ in parts:
            x, _ = sf.read(w, dtype="float32")
            seg += [x, gap]
        full = np.concatenate([np.zeros(int(0.4 * SR), np.float32)] + seg)
        tmp = os.path.join(CACHE, "track_tmp.wav")
        sf.write(tmp, full, SR)
        to_mp3(tmp, os.path.join(out_dir, tr))
        durations[tr] = round(len(full) / SR, 2)
    json.dump(durations, open(dur_path, "w"), indent=0)
    print(f"DONE {done} clips ({made} new), {len(tracks)} tracks, audio {audio_sec/60:.1f} min, "
          f"time {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
