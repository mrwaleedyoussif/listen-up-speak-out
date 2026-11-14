#!/usr/bin/env python3
"""
Listen Up! Speak Out! — ElevenLabs re-voicing tool
=================================================
Replaces the draft MP3 files in ../audio with ElevenLabs voices.
Same file names, so the platform uses the new audio automatically.

Run it on YOUR computer (Python 3.8+, no extra packages needed).
Your API key stays on your computer: put it in a file called ".env"
in this folder (one line:  ELEVENLABS_API_KEY=your_key_here)
or set the environment variable ELEVENLABS_API_KEY.

Examples
  python make_audio_elevenlabs.py --check            # test key, voices and cost
  python make_audio_elevenlabs.py --list-voices      # show voices in your account
  python make_audio_elevenlabs.py --grade 3 --dry-run
  python make_audio_elevenlabs.py --grade 3          # make Grade 3 audio
  python make_audio_elevenlabs.py                    # make everything
  python make_audio_elevenlabs.py --grade 4 --flash  # cheaper, faster model
  python make_audio_elevenlabs.py --tracks-only      # only rebuild full tracks

It skips clips that were already made with ElevenLabs (see elevenlabs_done.json),
so you can stop at any time and continue later — for example one grade per month.
"""
import argparse, base64, hashlib, json, os, re, shutil, subprocess, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.normpath(os.path.join(HERE, "..", "audio"))
if not os.path.isdir(AUDIO) and os.path.isdir(os.path.join(HERE, "..", "..", "www", "audio")):
    AUDIO = os.path.normpath(os.path.join(HERE, "..", "..", "www", "audio"))  # app repository layout
API = "https://api.elevenlabs.io/v1"
SPEED = {"3": 0.90, "4": 0.94, "5": 0.97, "6": 1.0}      # ElevenLabs speed (0.7–1.2)
GAP_MS = {"3": 850, "4": 750, "5": 650, "6": 600}         # pause between lines in full tracks
DEFAULT_MODEL = "eleven_multilingual_v2"
FLASH_MODEL = "eleven_flash_v2_5"


def load_key():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    envf = os.path.join(HERE, ".env")
    if not k and os.path.exists(envf):
        for line in open(envf, encoding="utf-8"):
            if line.strip().startswith("ELEVENLABS_API_KEY"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        sys.exit("No API key found.\nCreate a file named .env in this folder with one line:\n"
                 "ELEVENLABS_API_KEY=your_key_here\n(or set the ELEVENLABS_API_KEY environment variable).")
    return k


def call(key, method, path, body=None, accept="application/json", retries=6):
    url = API + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("xi-api-key", key)
        req.add_header("Accept", accept)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")[:300]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                wait = 2 ** attempt * 3
                print(f"   server busy ({e.code}) — waiting {wait}s and trying again…")
                time.sleep(wait); continue
            if e.code == 401:
                sys.exit("ElevenLabs says the API key is not valid (401). Check your .env file.")
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(5); continue
            raise RuntimeError(f"Network error: {e}")


def account_voices(key):
    js = json.loads(call(key, "GET", "/voices"))
    return {v["voice_id"]: v["name"] for v in js.get("voices", [])}


def resolve_voices(key, cfg):
    have = account_voices(key)
    by_name = {n.lower().split(" ")[0]: vid for vid, n in have.items()}
    out, problems = {}, []
    for sp, v in cfg.items():
        if sp.startswith("_"):
            continue
        vid = v.get("voice_id", "")
        if vid in have:
            out[sp] = vid
        elif v.get("name", "").lower() in by_name:
            out[sp] = by_name[v["name"].lower()]
            print(f"   {sp}: voice id not found, using '{v['name']}' from your account ({out[sp]})")
        else:
            problems.append(f"{sp} → '{v.get('name')}' ({vid})")
    if problems:
        print("\nThese voices are not in your ElevenLabs account:\n  " + "\n  ".join(problems))
        print("Fix: run  python make_audio_elevenlabs.py --list-voices  and paste a voice_id into voices.json.")
        print("(Voices from the ElevenLabs Voice Library must first be added to 'My Voices'.)")
        sys.exit(1)
    return out


def fingerprint(vid, model, text, speed):
    return hashlib.md5(f"{vid}|{model}|{speed}|{text}".encode("utf-8")).hexdigest()[:16]


def word_spans(al):
    """Word start/end times from ElevenLabs character alignment (for highlighting in the Shadowing Studio)."""
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    spans, cur = [], None
    for c, a, b in zip(chars, st, en):
        if c.isspace():
            if cur: spans.append(cur); cur = None
        elif re.match(r"[A-Za-z0-9]", c):
            cur = [a, b] if cur is None else [cur[0], b]
    if cur: spans.append(cur)
    return [[round(a, 2), round(b, 2)] for a, b in spans]


def update_timings(new):
    """Merge new word timings into ../audio/timings.js (read by the platform)."""
    path = os.path.join(AUDIO, "timings.js"); cur = {}
    if os.path.exists(path):
        txt = open(path, encoding="utf-8").read().strip()
        cur = json.loads(txt[txt.index("=") + 1:].rstrip(";"))
    cur.update(new)
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.LSP_TIMINGS=" + json.dumps(cur, separators=(",", ":")) + ";\n")


def build_tracks(man, grades):
    """Join line clips into one MP3 per lesson (for classroom speakers)."""
    ff = shutil.which("ffmpeg")
    sil = open(os.path.join(HERE, "silence_250ms.mp3"), "rb").read()
    tracks = {}
    for c in man:
        if "track" in c and c["path"].split("/")[0][1:] in grades:
            tracks.setdefault(c["track"], []).append((c["order"], c["path"]))
    for tr, parts in sorted(tracks.items()):
        parts.sort(); g = tr.split("/")[0][1:]
        files = [os.path.join(AUDIO, p) for _, p in parts]
        out = os.path.join(AUDIO, tr)
        if ff:
            args = [ff, "-y", "-loglevel", "error"]
            for p in files:
                args += ["-i", p]
            fl = "".join(f"[{i}:a]aresample=44100,aformat=channel_layouts=mono,apad=pad_dur={GAP_MS[g] / 1000}[a{i}];" for i in range(len(files)))
            fl += "".join(f"[a{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1[out]"
            args += ["-filter_complex", fl, "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", out]
            subprocess.run(args, check=True)
        else:
            n = max(1, round(GAP_MS[g] / 250))
            with open(out, "wb") as f:
                f.write(sil * 2)
                for p in files:
                    f.write(open(p, "rb").read()); f.write(sil * n)
    print(f"Rebuilt {len(tracks)} full tracks" + ("" if ff else " (without ffmpeg — simple join)"))


def main():
    ap = argparse.ArgumentParser(description="Re-voice Listen Up! Speak Out! with ElevenLabs")
    ap.add_argument("--grade", action="append", choices=["3", "4", "5", "6"], help="grade to make (repeatable); default all")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"ElevenLabs model (default {DEFAULT_MODEL})")
    ap.add_argument("--flash", action="store_true", help=f"use {FLASH_MODEL} (about half the credits)")
    ap.add_argument("--dry-run", action="store_true", help="only show what would be made and the character count")
    ap.add_argument("--check", action="store_true", help="check key, voices and credits, then stop")
    ap.add_argument("--list-voices", action="store_true", help="list the voices in your account")
    ap.add_argument("--force", action="store_true", help="re-make clips even if already done")
    ap.add_argument("--tracks-only", action="store_true", help="only rebuild the full lesson tracks")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many new clips (for a test)")
    a = ap.parse_args()
    model = FLASH_MODEL if a.flash else a.model
    grades = set(a.grade or ["3", "4", "5", "6"])

    man = json.load(open(os.path.join(HERE, "manifest.json"), encoding="utf-8"))
    man = [c for c in man if c["path"].split("/")[0][1:] in grades]
    if a.tracks_only:
        build_tracks(man, grades); return

    chars = sum(len(c["text"]) for c in man)
    print(f"Grades {', '.join(sorted(grades))}: {len(man)} clips, {chars:,} characters.")
    print(f"Model: {model}  (credits used ≈ {chars if model == DEFAULT_MODEL else chars // 2:,} if everything is new)")
    if a.dry_run:
        for g in sorted(grades):
            cg = [c for c in man if c["path"].startswith("g" + g)]
            print(f"  Grade {g}: {len(cg)} clips, {sum(len(c['text']) for c in cg):,} characters")
        return

    key = load_key()
    if a.list_voices:
        for vid, n in sorted(account_voices(key).items(), key=lambda x: x[1]):
            print(f"{n:30s} {vid}")
        return
    cfg = json.load(open(os.path.join(HERE, "voices.json"), encoding="utf-8"))
    print("Checking voices…")
    vmap = resolve_voices(key, cfg)
    try:
        sub = json.loads(call(key, "GET", "/user/subscription"))
        left = sub.get("character_limit", 0) - sub.get("character_count", 0)
        print(f"Your plan: {sub.get('tier', '?')} — about {left:,} credits left this period.")
    except Exception:
        pass
    if a.check:
        print("All voices found. Ready."); return

    done_path = os.path.join(HERE, "elevenlabs_done.json")
    done = json.load(open(done_path)) if os.path.exists(done_path) else {}
    todo = []
    for c in man:
        g = c["path"].split("/")[0][1:]
        fp = fingerprint(vmap[c["speaker"]], model, c["text"], SPEED[g])
        if a.force or done.get(c["path"]) != fp:
            todo.append((c, fp, g))
    print(f"{len(todo)} clips to make ({len(man) - len(todo)} already done).")
    made = 0; t0 = time.time(); new_t = {}
    try:
        for i, (c, fp, g) in enumerate(todo, 1):
            body = {"text": c["text"], "model_id": model,
                    "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0,
                                       "use_speaker_boost": True, "speed": SPEED[g]}}
            js = json.loads(call(key, "POST", f"/text-to-speech/{vmap[c['speaker']]}/with-timestamps?output_format=mp3_44100_128", body))
            audio = base64.b64decode(js["audio_base64"])
            al = js.get("alignment") or js.get("normalized_alignment")
            if al:
                new_t[c["path"]] = word_spans(al)
            out = os.path.join(AUDIO, c["path"])
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out + ".tmp", "wb") as f:
                f.write(audio)
            os.replace(out + ".tmp", out)
            done[c["path"]] = fp; made += 1
            if made % 10 == 0 or i == len(todo):
                json.dump(done, open(done_path, "w"), indent=0)
                if new_t: update_timings(new_t); new_t = {}
                print(f"  {i}/{len(todo)}  {c['path']}  ({(time.time() - t0) / 60:.1f} min)")
            if a.limit and made >= a.limit:
                print("Limit reached."); break
    except KeyboardInterrupt:
        print("\nStopped. Run the same command again to continue.")
    except RuntimeError as e:
        print(f"\nStopped because of an error: {e}\nRun the same command again to continue.")
    finally:
        json.dump(done, open(done_path, "w"), indent=0)
        if new_t: update_timings(new_t)
    if made:
        build_tracks(man, grades)
    print(f"Done: {made} new clips. Open ../index.html to listen.")


if __name__ == "__main__":
    main()
