#!/usr/bin/env python3
"""ElevenLabs recordings -> program audio  (no API key: the recordings are made inside the ElevenLabs account).

  plan GRADE              write el_plan_gGRADE.json: one batch per character (lines separated by blank lines, <= 1800 characters)
  split GRADE RAW_DIR     cut every batch recording (RAW_DIR/<batch id>.mp3) back into the program's clips in www/audio:
                          - finds each line with speech recognition (NVIDIA Parakeet) and cuts in the pause between lines
                          - trims, adds a 0.30 s lead-in (so speakers never swallow the first sound) and a short tail
                          - levels the loudness, encodes MP3 (mono, 32 kHz, 56 kbps)
                          - makes word timings for the highlighting, rebuilds the lesson tracks
                          - checks every clip again with speech recognition and writes el_report_gGRADE.json
Needs: ffmpeg, numpy, sherpa-onnx and the Parakeet model folder (PARAKEET env var).
"""
import difflib, json, os, re, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
AUDIO = os.environ.get('LSP_AUDIO', os.path.join(ROOT, 'www', 'audio'))
MAN = json.load(open(os.path.join(HERE, 'manifest.json'), encoding='utf-8'))
VOICES = json.load(open(os.path.join(HERE, 'voices.json'), encoding='utf-8'))
SPEED = {'3': 0.90, '4': 0.94, '5': 0.97, '6': 1.0}
GAP = {'3': 0.85, '4': 0.75, '5': 0.65, '6': 0.6}
SR, LEAD, TAIL = 32000, 0.30, 0.25
MODEL = 'eleven_multilingual_v2'
PARAKEET = os.environ.get('PARAKEET', '/home/claude/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8')
NUM = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '10': 'ten'}


def norm_words(t):
    t = t.lower().replace('’', "'")
    t = re.sub(r"[^a-z0-9' ]", ' ', t)
    return [NUM.get(w.strip("'"), w.strip("'")) for w in t.split() if w.strip("'")]


def plan(g):
    by = {}
    for c in MAN:
        if c['path'].startswith('g' + g + '/'):
            by.setdefault(c['speaker'], []).append(c)
    out = []
    for sp, cl in by.items():
        cur, n, k = [], 0, 1
        for c in cl:
            L = len(c['text']) + 2
            if cur and n + L > 1800:
                out.append((sp, k, cur)); cur, n, k = [], 0, k + 1
            cur.append(c); n += L
        if cur:
            out.append((sp, k, cur))
    res = [{'id': f'g{g}-{sp}-{k}', 'grade': g, 'speaker': sp, 'voice_id': VOICES[sp]['voice_id'], 'voice': VOICES[sp]['name'],
            'speed': SPEED[g], 'model': MODEL, 'paths': [c['path'] for c in cl], 'text': '\n\n'.join(c['text'] for c in cl)} for sp, k, cl in out]
    json.dump(res, open(os.path.join(HERE, f'el_plan_g{g}.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'Grade {g}: {len(res)} batches, {sum(len(r["text"]) for r in res):,} characters')
    return res


_rec = None
def asr(x16):
    """[(word, start, end)] from Parakeet token timestamps."""
    global _rec
    import sherpa_onnx
    if _rec is None:
        M = PARAKEET
        _rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{M}/encoder.int8.onnx', decoder=f'{M}/decoder.int8.onnx', joiner=f'{M}/joiner.int8.onnx',
                                                            tokens=f'{M}/tokens.txt', num_threads=2, model_type='nemo_transducer')
    s = _rec.create_stream(); s.accept_waveform(16000, x16); _rec.decode_stream(s); r = s.result
    durs = list(r.durations) if getattr(r, 'durations', None) else [0.08] * len(r.tokens)
    words = []
    for tok, t, d in zip(r.tokens, r.timestamps, durs):
        if tok.startswith(' ') or not words:
            words.append([tok.strip(), t, t + max(d, 0.04)])
        else:
            words[-1][0] += tok; words[-1][2] = t + max(d, 0.04)
    out = []   # one entry per normalized word (a recognised "B-E-N" becomes b, e, n)
    for w, a, b in words:
        for nw in norm_words(w):
            out.append((nw, a, b))
    return out


def decode(path, sr):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768


def rms_frames(x, sr, hop=0.01):
    n = int(sr * hop); m = len(x) // n
    return np.sqrt(np.mean(x[:m * n].reshape(m, n) ** 2, axis=1) + 1e-12)


def align(exp, hyp):
    """index map expected-word -> hypothesis-word for matching words."""
    sm = difflib.SequenceMatcher(None, exp, [h[0] for h in hyp], autojunk=False)
    m = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            m[a + k] = b + k
    return m


def encode(y, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as f:
        f.write((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); tmp = f.name
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', tmp, '-codec:a', 'libmp3lame', '-b:a', '56k', out], check=True)
    os.remove(tmp)


def level(y):
    r = np.sqrt(np.mean(y[np.abs(y) > 0.01] ** 2)) if np.any(np.abs(y) > 0.01) else 0.05
    y = y * (0.11 / max(r, 1e-4))
    pk = np.max(np.abs(y))
    return y * (0.95 / pk) if pk > 0.95 else y


def word_spans(text, hyp, t_shift, t_max):
    """[start,end] for every spoken word of the line text (whitespace words with letters or digits)."""
    toks = [w for w in text.split() if re.search(r'[A-Za-z0-9]', w)]
    exp, owner = [], []
    for i, w in enumerate(toks):
        for nw in norm_words(w):
            exp.append(nw); owner.append(i)
    m = align(exp, hyp)
    spans = [None] * len(toks)
    for ei, hi in m.items():
        i = owner[ei]; a, b = hyp[hi][1] + t_shift, hyp[hi][2] + t_shift
        spans[i] = [a, b] if spans[i] is None else [min(spans[i][0], a), max(spans[i][1], b)]
    known = [i for i, s in enumerate(spans) if s]
    if not known:
        return None, 0.0
    for i in range(len(spans)):   # fill gaps by interpolation
        if spans[i] is None:
            prev = max([k for k in known if k < i], default=None); nxt = min([k for k in known if k > i], default=None)
            a = spans[prev][1] if prev is not None else max(t_shift, (spans[nxt][0] - 0.3) if nxt is not None else t_shift)
            b = spans[nxt][0] if nxt is not None else min(t_max, a + 0.35)
            gap = [k for k in range(prev + 1 if prev is not None else 0, nxt if nxt is not None else len(spans))]
            j = gap.index(i); step = max(0.05, (b - a) / len(gap))
            spans[i] = [a + j * step, a + (j + 1) * step]
    for i in range(1, len(spans)):   # keep them in order and not overlapping
        if spans[i][0] < spans[i - 1][1]:
            spans[i][0] = spans[i - 1][1]
        if spans[i][1] < spans[i][0] + 0.04:
            spans[i][1] = spans[i][0] + 0.04
    acc = len(m) / max(1, len(exp))
    return [[round(a, 2), round(b, 2)] for a, b in spans], acc


def split(g, raw_dir):
    P = json.load(open(os.environ.get('LSP_PLAN', os.path.join(HERE, f'el_plan_g{g}.json')), encoding='utf-8'))
    byp = {c['path']: c for c in MAN}
    timings, report = {}, {}
    for b in P:
        src = os.path.join(raw_dir, b['id'] + '.mp3')
        if not os.path.exists(src):
            print('missing', src); continue
        x = decode(src, SR); x16 = decode(src, 16000)
        hyp = asr(x16)
        lines = [byp[p] for p in b['paths']]
        exp, owner = [], []
        for li, c in enumerate(lines):
            for w in norm_words(c['text']):
                exp.append(w); owner.append(li)
        m = align(exp, hyp)
        st, en = [None] * len(lines), [None] * len(lines)
        for ei, hi in m.items():
            li = owner[ei]
            st[li] = hyp[hi][1] if st[li] is None else min(st[li], hyp[hi][1])
            en[li] = hyp[hi][2] if en[li] is None else max(en[li], hyp[hi][2])
        env = rms_frames(x, SR); thr = max(np.percentile(env, 10) * 3, env.max() * 0.02)
        cuts = [0.0]
        for i in range(len(lines) - 1):
            a = en[i] if en[i] is not None else (st[i] if st[i] is not None else cuts[-1])
            bb = st[i + 1] if st[i + 1] is not None else None
            if bb is None:   # next line not recognised: look ahead for the next known start
                nxt = [st[k] for k in range(i + 2, len(lines)) if st[k] is not None]
                bb = nxt[0] if nxt else len(x) / SR
            if bb <= a:
                a, bb = bb - 0.15, a + 0.15
            fa, fb = max(0, int(a * 100)), min(len(env) - 1, int(bb * 100))
            seg = env[fa:fb + 1] if fb > fa else env[fa:fa + 1]
            low = seg < thr; best, run, bs = None, 0, 0
            for k, v in enumerate(low):   # longest quiet run in the gap
                if v:
                    run += 1
                    if not best or run > best[1]: best = (k - run + 1, run)
                else:
                    run = 0
            cut = (fa + best[0] + best[1] / 2) / 100 if best else (fa + int(np.argmin(seg))) / 100
            cuts.append(max(cut, cuts[-1] + 0.05))
        cuts.append(len(x) / SR)
        for i, c in enumerate(lines):
            seg = x[int(cuts[i] * SR):int(cuts[i + 1] * SR)]
            e = rms_frames(seg, SR); th = max(e.max() * 0.03, 0.002)
            on = np.where(e > th)[0]
            if len(on) == 0:
                report[c['path']] = {'ok': False, 'why': 'silent segment', 'batch': b['id']}; continue
            a, z = max(0, on[0] - 5) * SR // 100, min(len(seg), (on[-1] + 12) * SR // 100)
            y = level(seg[a:z])
            y = np.concatenate([np.zeros(int(LEAD * SR), np.float32), y, np.zeros(int(TAIL * SR), np.float32)]).astype(np.float32)
            out = os.path.join(AUDIO, c['path']); encode(y, out)
            # check the finished clip and make its word timings
            y16 = decode(out, 16000); h2 = asr(y16)
            spans, acc = word_spans(c['text'], h2, 0.0, len(y16) / 16000)
            if spans:   # keep the highlighting inside the real speech (after the lead-in, before the tail)
                on_t, off_t = LEAD - 0.02, len(y) / SR - TAIL + 0.04
                for sp_ in spans:
                    sp_[0] = round(min(max(sp_[0], on_t), off_t - 0.05), 2); sp_[1] = round(min(max(sp_[1], sp_[0] + 0.05), off_t), 2)
                timings[c['path']] = spans
            hw = [w for w, _, _ in h2]; ew = norm_words(c['text'])
            first_ok = bool(hw) and bool(ew) and hw[0] == ew[0]
            report[c['path']] = {'ok': acc >= 0.75 and first_ok, 'acc': round(acc, 2), 'first_ok': first_ok, 'heard': ' '.join(hw), 'text': c['text'], 'batch': b['id'], 'dur': round(len(y) / SR, 2)}
        print(f"{b['id']}: {len(lines)} clips, {sum(1 for c in lines if report.get(c['path'], {}).get('ok'))} pass")
    # merge timings
    tp = os.path.join(AUDIO, 'timings.js'); txt = open(tp, encoding='utf-8').read().strip() if os.path.exists(tp) else 'x={};'
    cur = json.loads(txt[txt.index('=') + 1:].rstrip(';')); cur.update(timings)
    open(tp, 'w', encoding='utf-8').write('window.LSP_TIMINGS=' + json.dumps(cur, separators=(',', ':')) + ';\n')
    build_tracks(g)
    json.dump(report, open(os.path.join(HERE, f'el_report_g{g}.json'), 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
    bad = [k for k, v in report.items() if not v.get('ok')]
    print(f'Grade {g}: {len(report)} clips, {len(bad)} to check: {bad[:30]}')


def build_tracks(g):
    tracks = {}
    for c in MAN:
        if 'track' in c and c['path'].startswith('g' + g + '/'):
            tracks.setdefault(c['track'], []).append((c['order'], c['path']))
    for tr, parts in tracks.items():
        parts.sort(); segs = [np.zeros(int(0.4 * SR), np.float32)]
        for _, p in parts:
            segs += [decode(os.path.join(AUDIO, p), SR), np.zeros(int(GAP[g] * SR), np.float32)]
        encode(np.concatenate(segs), os.path.join(AUDIO, tr))
    print(f'Grade {g}: rebuilt {len(tracks)} lesson tracks')


if __name__ == '__main__':
    cmd, g = sys.argv[1], sys.argv[2]
    if cmd == 'plan': plan(g)
    elif cmd == 'split': split(g, sys.argv[3])
    elif cmd == 'tracks': build_tracks(g)
