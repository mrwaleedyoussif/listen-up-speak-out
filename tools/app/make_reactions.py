"""Spoken reactions for right / wrong answers and celebrations.

Makes short praise and encouragement clips with the narrator voice (Kokoro "af_heart", the voice of
the current program audio), checks every clip with speech recognition (all words heard, first word
first), trims and levels it, and packs all clips into www/sfx/reactions.js as base64 MP3, so they
play from the Web Audio context on every platform (also from file:// in the Windows app).

Usage: python3 tools/app/make_reactions.py            (needs kokoro-onnx and the Parakeet model)
Re-voicing later (e.g. with ElevenLabs): put MP3s named like the keys below into a folder and run
       python3 tools/app/make_reactions.py --from DIR
"""
import base64, json, os, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'elevenlabs'))
import el_pipeline as E  # noqa: E402

OUT = os.path.join(HERE, '..', '..', 'www', 'sfx', 'reactions.js')
SR = 24000
VOICE, LANG = 'af_heart', 'en-us'

PHRASES = {
    'right': ['Great job!', 'Well done!', 'Excellent!', 'You got it!', "That's right!", 'Super!',
              'Brilliant!', 'Perfect!', 'Awesome!', 'Nice work!'],
    'wrong': ['Oops! Not this time.', 'Nice try!', 'Almost!', 'Not quite.', 'Keep going!', "Don't give up!"],
    'celeb': ['Amazing! You did it!', 'Hurray! Well done!', 'Fantastic work!', "You're a star!",
              'Congratulations!', "Wow! You're amazing!"],
    'try':   ['Good try! Practise and try again.', 'Keep practising. You can do it!', "You're getting better. Try again!"],
}
# speech-recognition spellings that are the same word
SAME = {'hurray': 'hooray', 'practice': 'practise', 'practicing': 'practising', 'thats': "that's", 'youre': "you're", 'dont': "don't"}


def key(t):
    return ''.join(c if c.isalnum() else '_' for c in t.lower()).strip('_').replace('__', '_')


def nw(t):
    return [SAME.get(w.replace("'", ''), SAME.get(w, w)) for w in E.norm_words(t)]


def to16(x):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-ar', '16000', '-f', 'f32le', '-'],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32)


def check(x, text):
    h = E.asr(to16(x)); hw = [SAME.get(w.replace("'", ''), w) for w, _, _ in h]; ew = nw(text)
    m = E.align(ew, [(w, 0, 0) for w in hw])
    return len(m) / max(1, len(ew)), bool(hw) and hw[0] == ew[0], ' '.join(hw)


def tidy(x):
    env = E.rms_frames(x, SR); thr = max(env.max() * 0.025, 0.002); on = np.where(env > thr)[0]
    a = max(0, on[0] - 3) * SR // 100; b = min(len(x), (on[-1] + 12) * SR // 100)
    y = x[a:b].copy(); f = int(0.06 * SR); y[-f:] *= np.linspace(1, 0, f)
    y = np.concatenate([np.zeros(int(0.02 * SR), np.float32), y])
    r = np.sqrt(np.mean(y[np.abs(y) > 0.01] ** 2)); y = y * (0.13 / max(r, 1e-4))
    pk = np.max(np.abs(y)); return y * (0.93 / pk) if pk > 0.93 else y


def mp3(y):
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f: out = f.name
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-codec:a', 'libmp3lame', '-b:a', '48k', out],
                   input=y.astype(np.float32).tobytes(), check=True)
    b = open(out, 'rb').read(); os.remove(out); return b


def main():
    src = sys.argv[sys.argv.index('--from') + 1] if '--from' in sys.argv else None
    if not src:
        from kokoro_onnx import Kokoro
        K = Kokoro('/home/claude/models/kokoro-v1.0.onnx', '/home/claude/models/voices-v1.0.bin')
    pack, report = {}, []
    for kind, lst in PHRASES.items():
        pack[kind] = []
        for t in lst:
            best = None
            if src:
                takes = [E.decode(os.path.join(src, key(t) + '.mp3'), SR)]
            else:   # two takes (normal and slightly slower speed); the better one by speech recognition is kept
                takes = []
                for speed in (1.0, 0.95):
                    s, sr = K.create(t, voice=VOICE, speed=speed, lang=LANG); takes.append(np.asarray(s, np.float32))
            for x in takes:
                cov, first, heard = check(x, t)
                if best is None or (first, cov) > best[0]:
                    best = ((first, cov), x, heard)
                if first and cov == 1: break
            (first, cov), x, heard = best
            y = tidy(x); b = mp3(y)
            pack[kind].append({'t': t, 'a': base64.b64encode(b).decode()})
            report.append({'kind': kind, 'text': t, 'heard': heard, 'first_ok': first, 'coverage': round(cov, 2), 'sec': round(len(y) / SR, 2), 'kb': round(len(b) / 1024, 1)})
            print(f"{kind:5} {'OK ' if first and cov == 1 else 'CHK'} {t:36} heard: {heard:36} {len(y) / SR:.2f}s")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('/* Spoken reactions (narrator voice) as base64 MP3 — made by tools/app/make_reactions.py */\n')
        f.write('window.LSP_RX=' + json.dumps(pack, separators=(',', ':')) + ';\n')
    json.dump(report, open(os.path.join(HERE, 'reactions_report.json'), 'w'), indent=1)
    print('wrote', OUT, round(os.path.getsize(OUT) / 1024), 'KB')


if __name__ == '__main__':
    main()
