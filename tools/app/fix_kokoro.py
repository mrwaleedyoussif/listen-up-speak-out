#!/usr/bin/env python3
"""Clean the draft (Kokoro) clips of grades that are not yet re-recorded with ElevenLabs.

1. Every clip gets a 0.30 s lead-in so speakers and Bluetooth devices never swallow the first sound.
2. Clips whose first sound was damaged (speech recognition heard "a class" for "class", "zan" for "van")
   are made again after a carrier word ("Listen. van.") and the carrier is cut off, because the voice's
   start-up glitch lands on the carrier. The new take is kept only if speech recognition hears it better.
3. Word timings are moved to match and the lesson tracks are rebuilt.

Usage: fix_kokoro.py CHECK.json GRADE [GRADE ...]   (CHECK.json from the speech-recognition check)
"""
import hashlib, json, os, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'elevenlabs'))
import el_pipeline as E

CACHE = '/home/claude/build/wavcache'
KSPEED = {'3': 0.88, '4': 0.92, '5': 0.96, '6': 1.0}
KSR, LEAD = 24000, 0.30
_k = None


def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro('/home/claude/models/kokoro-v1.0.onnx', '/home/claude/models/voices-v1.0.bin')
    return _k


def to16(x, sr):
    import subprocess
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-ar', '16000', '-f', 'f32le', '-'], input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32)


def score(x, sr, text):
    h = E.asr(to16(x, sr)); hw = [w for w, _, _ in h]; ew = E.norm_words(text)
    m = E.align(ew, h)
    return len(m) / max(1, len(ew)), bool(hw) and bool(ew) and hw[0] == ew[0], h


def onset_cut(x, sr):
    e = E.rms_frames(x, sr); th = max(e.max() * 0.03, 0.002); on = np.where(e > th)[0]
    return max(0, on[0] - 4) * sr // 100 if len(on) else 0


def carrier_take(c, g):
    s, sr = kokoro().create('Listen. ' + c['text'], voice=c['voice'], speed=KSPEED[g], lang=c['lang'])
    x = np.asarray(s, np.float32)
    h = E.asr(to16(x, sr)); ew = E.norm_words(c['text'])
    m = E.align(['listen'] + ew, h)
    env = E.rms_frames(x, sr); thr = max(np.percentile(env, 10) * 3, env.max() * 0.03)
    t_prev = h[m[0]][2] if 0 in m else 0.25
    later = sorted(k for k in m if k >= 1)
    t_next = h[m[later[0]]][1] if later else min(len(x) / sr, t_prev + 1.0)
    if 1 in m:   # the line's first word was heard: cut just before it
        t_next = h[m[1]][1]
    fa, fb = int(t_prev * 100), max(int(t_prev * 100) + 1, int(t_next * 100))
    seg = env[fa:fb + 1]; best, run = None, 0
    for k, v in enumerate(seg < thr):   # longest quiet stretch = the pause after "Listen."
        run = run + 1 if v else 0
        if v and (not best or run > best[1]): best = (k - run + 1, run)
    if best is not None and best[1] >= 2:
        cut = (fa + best[0] + best[1] / 2) / 100
    else:   # no clear pause: the quietest moment just after "Listen"
        w = env[fa:min(len(env), fa + 40)]
        cut = (fa + int(np.argmin(w))) / 100 if len(w) else t_prev
    y = x[int(cut * sr):]
    y = y[onset_cut(y, sr):]
    return E.level(y)


def main():
    chk = json.load(open(sys.argv[1])); grades = sys.argv[2:]
    tp = os.path.join(E.AUDIO, 'timings.js'); txt = open(tp, encoding='utf-8').read().strip()
    TM = json.loads(txt[txt.index('=') + 1:].rstrip(';'))
    log = {}
    for c in E.MAN:
        g = c['path'].split('/')[0][1:]
        if g not in grades:
            continue
        key = hashlib.md5(f"{c['voice']}|{c['text']}|{KSPEED[g]}".encode()).hexdigest()[:12]
        x, sr = sf.read(os.path.join(CACHE, key + '.wav'), dtype='float32')
        cut = onset_cut(x, sr); y = x[cut:]; shift = LEAD - cut / sr; how = 'lead-in'
        r = chk.get(c['path'], {})
        if r and (not r.get('first_ok') or r.get('acc', 1) < 0.8):
            a0, f0, _ = score(y, sr, c['text'])
            z = carrier_take(c, g)
            if z is not None:
                a1, f1, _ = score(z, sr, c['text'])
                if (f1 and not f0) or (f1 == f0 and a1 > a0 + 0.05):
                    y, how = z, 'remade'
                    shift = None
            log[c['path']] = {'before': r.get('hyp'), 'how': how}
        out = np.concatenate([np.zeros(int(LEAD * sr), np.float32), y]).astype(np.float32)
        # write MP3 (same format as the other draft clips)
        import subprocess
        p = os.path.join(E.AUDIO, c['path'])
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-codec:a', 'libmp3lame', '-b:a', '48k', p], input=out.tobytes(), check=True)
        if shift is not None and c['path'] in TM:
            TM[c['path']] = [[round(max(LEAD - 0.02, a + shift), 2), round(max(LEAD + 0.03, b + shift), 2)] for a, b in TM[c['path']]]
        elif shift is None:   # new take: fresh word timings from speech recognition
            h = E.asr(to16(out, sr))
            spans, _ = E.word_spans(c['text'], h, 0.0, len(out) / sr)
            if spans:
                TM[c['path']] = [[round(max(a, LEAD - 0.02), 2), round(max(b, LEAD + 0.03), 2)] for a, b in spans]
    open(tp, 'w', encoding='utf-8').write('window.LSP_TIMINGS=' + json.dumps(TM, separators=(',', ':')) + ';\n')
    for g in grades:
        E.build_tracks(g)
    json.dump(log, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'kokoro_fix_{"".join(grades)}.json'), 'w'), indent=0)
    print('remade', sum(1 for v in log.values() if v['how'] == 'remade'), 'of', len(log), 'flagged clips')


if __name__ == '__main__':
    main()
