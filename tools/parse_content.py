#!/usr/bin/env python3
"""Parse the Listen Up! Speak Out! content files (simple line-based format)
into one JSON program + an audio manifest.

Usage: python3 parse_content.py content_dir out_dir
"""
import json, os, re, sys, random, glob, hashlib

SPEAKERS = {
    # key: (display name, kokoro voice, kokoro lang)
    "NARRATOR": ("Narrator", "af_heart", "en-us"),
    "SAMI": ("Sami", "am_puck", "en-us"),
    "NOOR": ("Noor", "af_bella", "en-us"),
    "BEN": ("Ben", "bm_fable", "en-gb"),
    "ADAM": ("Adam", "am_fenrir", "en-us"),
    "LINA": ("Lina", "af_kore", "en-us"),
    "YUSUF": ("Yusuf", "am_liam", "en-us"),
    "MR_HASSAN": ("Mr. Hassan", "am_michael", "en-us"),
    "MS_GREEN": ("Ms. Green", "bf_emma", "en-gb"),
    "MOM": ("Mom", "af_sarah", "en-us"),
    "DAD": ("Dad", "am_onyx", "en-us"),
    "GRANDPA": ("Grandpa", "bm_george", "en-gb"),
    "MAN": ("Man", "am_eric", "en-us"),
    "WOMAN": ("Woman", "bf_isabella", "en-gb"),
    "ANNOUNCER": ("Announcer", "bm_daniel", "en-gb"),
}
WORD_VOICE = "NARRATOR"   # vocabulary, chunks and sound-focus items

BRACE = re.compile(r"\{([^{}|]*)\|([^{}]*)\}")
LINE = re.compile(r"^([A-Z_]+)(?:\[([^\]]+)\])?:\s*(.+)$")


def disp(t):
    return BRACE.sub(lambda m: m.group(1), t).strip()


def tts(t):
    t = BRACE.sub(lambda m: m.group(2), t)
    t = t.replace("___", "…")
    return re.sub(r"\s+", " ", t).strip()


def split(v):
    return [x.strip() for x in v.split("|")]


class ParseError(Exception):
    pass


def parse_file(path, grades):
    cur_grade = cur_unit = cur_les = None
    mode = None  # 'script' / 'model'
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for ln, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s:
            continue
        where = f"{os.path.basename(path)}:{ln}"
        try:
            if mode in ("script", "model"):
                if s == "end":
                    mode = None
                    continue
                m = LINE.match(s)
                if not m:
                    raise ParseError("bad script line")
                sp, nm, txt = m.groups()
                if sp not in SPEAKERS:
                    raise ParseError(f"unknown speaker {sp}")
                cur_les[mode].append({"sp": sp, "name": nm or SPEAKERS[sp][0],
                                      "text": disp(txt), "tts": tts(txt)})
                continue
            if s.startswith("#GRADE"):
                g = int(s.split()[1])
                cur_grade = grades.setdefault(g, {"grade": g, "units": []})
                continue
            if s.startswith("@UNIT"):
                p = split(s[5:])
                cur_unit = {"n": int(p[0]), "title": p[1], "ar": p[2], "emoji": p[3],
                            "goals": [], "listen": [], "speak": [], "check": []}
                cur_grade["units"].append(cur_unit)
                cur_les = None
                continue
            if s.startswith("@LISTEN"):
                p = split(s[7:])
                cur_les = {"kind": "listen", "n": int(p[0]), "title": p[1], "skill": p[2], "skill_ar": p[3],
                           "kagan": [], "vocab": [], "script": [], "tasks": [], "predict": None, "tip": None,
                           "speak": None, "teach": ""}
                cur_unit["listen"].append(cur_les)
                continue
            if s.startswith("@SPEAK"):
                p = split(s[6:])
                cur_les = {"kind": "speak", "n": int(p[0]), "title": p[1], "func": p[2], "func_ar": p[3],
                           "kagan": [], "model": [], "roles": [], "chunks": [], "sound": None,
                           "task": None, "cando": [], "teach": ""}
                cur_unit["speak"].append(cur_les)
                continue
            if s.startswith("@CHECK"):
                cur_les = "CHECK"
                continue
            key, _, val = s.partition(":")
            key = key.strip(); val = val.strip()
            if cur_unit is None:
                if key in ("level", "band", "speed"):
                    cur_grade[key] = float(val) if key == "speed" else val
                    continue
                raise ParseError(f"unexpected {key}")
            if key == "goals":
                cur_unit["goals"] = split(val); continue
            if cur_les == "CHECK":
                if key != "check":
                    raise ParseError("only check: lines in @CHECK")
                p = split(val)
                ref = p[0]
                m = re.match(r"L(\d)#(\d+)$", ref)
                if not m:
                    raise ParseError("bad check ref")
                opts = p[2:]
                cur_unit["check"].append(mk_mcq(p[1], opts, where, ref=ref))
                continue
            L = cur_les
            if key == "kagan": L["kagan"] = split(val)
            elif key == "vocab":
                p = split(val)
                if len(p) != 4: raise ParseError("vocab needs 4 parts")
                L["vocab"].append({"w": p[0], "ar": p[1], "emoji": p[2], "ex": p[3]})
            elif key == "predict":
                p = split(val); L["predict"] = {"en": p[0], "ar": p[1] if len(p) > 1 else ""}
            elif key == "tip":
                p = split(val); L["tip"] = {"en": p[0], "ar": p[1] if len(p) > 1 else ""}
            elif key == "script": mode = "script"
            elif key == "model": mode = "model"
            elif key == "mcq":
                p = split(val); L["tasks"].append(mk_mcq(p[0], p[1:], where))
            elif key == "tf":
                p = split(val)
                if p[1] not in ("T", "F"): raise ParseError("tf needs T or F")
                L["tasks"].append({"type": "tf", "s": p[0], "ans": p[1] == "T"})
            elif key == "order":
                p = split(val)
                if len(p) < 3: raise ParseError("order needs 3+ items")
                L["tasks"].append({"type": "order", "items": p})
            elif key == "gap":
                p = split(val)
                if "___" not in p[0]: raise ParseError("gap needs ___")
                L["tasks"].append({"type": "gap", "s": p[0], "ans": [a.strip() for a in p[1].split(",")]})
            elif key == "speak":
                p = split(val); L["speak"] = {"prompt": p[0], "frame": p[1] if len(p) > 1 else ""}
            elif key == "teach": L["teach"] = val
            elif key == "roles": L["roles"] = split(val)
            elif key == "chunks":
                out = []
                for c in split(val):
                    en, _, ar = c.partition("=")
                    out.append({"en": en.strip(), "ar": ar.strip(), "tts": tts(en.strip())})
                L["chunks"] = out
            elif key == "sound":
                p = split(val)
                typ = p[0]
                if typ == "pairs":
                    L["sound"] = {"type": "pairs", "title": p[1], "en": p[2], "ar": p[3], "pairs": []}
                elif typ == "sort":
                    cats = [c.strip() for c in p[2].split(";")]
                    L["sound"] = {"type": "sort", "title": p[1], "cats": [{"key": c.split()[0], "label": c} for c in cats],
                                  "en": p[3], "ar": p[4], "items": []}
                else:
                    raise ParseError("sound type")
            elif key == "pair":
                p = split(val); L["sound"]["pairs"].append(p)
            elif key == "item":
                p = split(val)
                keys = [c["key"] for c in L["sound"]["cats"]]
                if p[1] not in keys: raise ParseError(f"item key {p[1]} not in {keys}")
                L["sound"]["items"].append({"text": p[0], "key": p[1]})
            elif key == "task":
                p = split(val); L["task"] = {"prompt": p[0], "frame": p[1] if len(p) > 1 else ""}
            elif key == "cando": L["cando"] = split(val)
            else:
                raise ParseError(f"unknown key {key}")
        except ParseError as e:
            raise SystemExit(f"{where}: {e}\n  {raw}")
        except Exception as e:
            raise SystemExit(f"{where}: {type(e).__name__} {e}\n  {raw}")


def mk_mcq(q, opts, where, ref=None):
    if len(opts) != 4:
        raise SystemExit(f"{where}: MCQ needs exactly 4 options: {opts}")
    if not opts[0].startswith("*") or any(o.startswith("*") for o in opts[1:]):
        raise SystemExit(f"{where}: first option must be the starred correct one")
    d = {"type": "mcq", "q": q, "correct": opts[0][1:].strip(), "wrong": [o.strip() for o in opts[1:]]}
    if ref: d["ref"] = ref
    return d


def balanced_positions(n, seed):
    """Positions 0-3 for n items: equal counts, no 3 in a row, no a-b-c-d runs."""
    rnd = random.Random(seed)
    base = [i % 4 for i in range(n)]
    for _ in range(5000):
        rnd.shuffle(base)
        ok = True
        for i in range(2, n):
            if base[i] == base[i - 1] == base[i - 2]:
                ok = False; break
        if ok:
            for i in range(3, n):
                w = base[i - 3:i + 1]
                if w in ([0, 1, 2, 3], [3, 2, 1, 0]):
                    ok = False; break
        if ok:
            return base
    return base


def finalize(grades):
    """Assign balanced answer positions per grade; build ids and the audio manifest."""
    manifest = []
    for g, G in sorted(grades.items()):
        mcqs = []
        for U in G["units"]:
            for L in U["listen"]:
                mcqs += [t for t in L["tasks"] if t["type"] == "mcq"]
            mcqs += U["check"]
        pos = balanced_positions(len(mcqs), seed=1000 + g)
        rnd = random.Random(77 + g)
        for t, p in zip(mcqs, pos):
            wrong = t.pop("wrong"); rnd.shuffle(wrong)
            opts = wrong[:]
            opts.insert(p, t.pop("correct"))
            t["opts"] = opts; t["ans"] = p
        for U in G["units"]:
            uid = f"g{g}u{U['n']}"
            U["id"] = uid
            for L in U["listen"]:
                lid = f"{uid}l{L['n']}"; L["id"] = lid
                d = f"g{g}/u{U['n']}/l{L['n']}"
                for i, v in enumerate(L["vocab"], 1):
                    v["audio"] = f"{d}/v{i}.mp3"
                    manifest.append(clip(v["audio"], WORD_VOICE, v["w"] + "."))
                for i, ln in enumerate(L["script"], 1):
                    ln["audio"] = f"{d}/{i:02d}.mp3"
                    manifest.append(clip(ln["audio"], ln["sp"], ln["tts"], track=f"{d}/track.mp3", order=i))
                L["track"] = f"{d}/track.mp3"
            for S in U["speak"]:
                sid = f"{uid}s{S['n']}"; S["id"] = sid
                d = f"g{g}/u{U['n']}/s{S['n']}"
                for i, ln in enumerate(S["model"], 1):
                    ln["audio"] = f"{d}/{i:02d}.mp3"
                    manifest.append(clip(ln["audio"], ln["sp"], ln["tts"], track=f"{d}/track.mp3", order=i))
                S["track"] = f"{d}/track.mp3"
                for i, c in enumerate(S["chunks"], 1):
                    c["audio"] = f"{d}/c{i}.mp3"
                    manifest.append(clip(c["audio"], WORD_VOICE, c["tts"]))
                snd = S["sound"]
                if snd["type"] == "pairs":
                    snd["audio"] = []
                    for i, (a, b) in enumerate(snd["pairs"], 1):
                        pa, pb = f"{d}/p{i}a.mp3", f"{d}/p{i}b.mp3"
                        snd["audio"].append([pa, pb])
                        manifest.append(clip(pa, WORD_VOICE, end_punct(a)))
                        manifest.append(clip(pb, WORD_VOICE, end_punct(b)))
                else:
                    for i, it in enumerate(snd["items"], 1):
                        it["audio"] = f"{d}/i{i}.mp3"
                        manifest.append(clip(it["audio"], WORD_VOICE, end_punct(it["text"])))
            # resolve check refs to audio clips
            for c in U["check"]:
                ln_i = int(c["ref"].split("#")[1]); l_n = int(c["ref"][1])
                L = next(x for x in U["listen"] if x["n"] == l_n)
                if ln_i > len(L["script"]):
                    raise SystemExit(f"{uid} check ref {c['ref']} out of range")
                c["audio"] = L["script"][ln_i - 1]["audio"]
                c["line"] = L["script"][ln_i - 1]["text"]
                c["speaker"] = L["script"][ln_i - 1]["name"]
    return manifest


def end_punct(t):
    return t if t[-1:] in ".?!" else t + "."


def clip(path, sp, text, track=None, order=None):
    d = {"path": path, "speaker": sp, "voice": SPEAKERS[sp][1], "lang": SPEAKERS[sp][2],
         "text": text, "hash": hashlib.md5(f"{sp}|{text}".encode()).hexdigest()[:10]}
    if track:
        d["track"] = track; d["order"] = order
    return d


def main():
    src, out = sys.argv[1], sys.argv[2]
    grades = {}
    for p in sorted(glob.glob(os.path.join(src, "g*.txt"))):
        parse_file(p, grades)
    manifest = finalize(grades)
    os.makedirs(out, exist_ok=True)
    prog = {"title": "Listen Up! Speak Out!", "grades": [grades[g] for g in sorted(grades)],
            "speakers": {k: v[0] for k, v in SPEAKERS.items()}}
    with open(os.path.join(out, "program.json"), "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    # summary
    for G in prog["grades"]:
        nm = sum(1 for U in G["units"] for L in U["listen"] for t in L["tasks"] if t["type"] == "mcq") + sum(len(U["check"]) for U in G["units"])
        pos = [t["ans"] for U in G["units"] for L in U["listen"] for t in L["tasks"] if t["type"] == "mcq"] + [c["ans"] for U in G["units"] for c in U["check"]]
        tf = [t["ans"] for U in G["units"] for L in U["listen"] for t in L["tasks"] if t["type"] == "tf"]
        words = sum(len(l["tts"].split()) for U in G["units"] for L in U["listen"] for l in L["script"])
        print(f"Grade {G['grade']}: units={len(G['units'])} listen={sum(len(U['listen']) for U in G['units'])} "
              f"speak={sum(len(U['speak']) for U in G['units'])} mcq={nm} abcd={[pos.count(i) for i in range(4)]} "
              f"tf T/F={tf.count(True)}/{tf.count(False)} script_words={words}")
    chars = sum(len(c["text"]) for c in manifest)
    print(f"clips={len(manifest)} chars={chars}")


if __name__ == "__main__":
    main()
