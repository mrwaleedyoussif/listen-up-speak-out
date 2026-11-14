# Re-voice the program with ElevenLabs

The program already includes **draft audio** made with a free neural voice, so everything works today.
This folder lets you replace every clip with **ElevenLabs voices**. The script uses the same file names, so the platform picks up the new audio automatically.

## What you need (one time)
1. **Python 3.8 or newer** on your computer — https://www.python.org/downloads/ (on Windows, tick *"Add Python to PATH"* when installing). No extra packages are needed.
2. **Your ElevenLabs API key**, from ElevenLabs → *Profile* → *API Keys*.
3. In this `elevenlabs` folder, create a text file named **`.env`** with one line:
   `ELEVENLABS_API_KEY=paste_your_key_here`
   The key stays on your computer and is only sent to ElevenLabs. Never share this file.

## Make the audio
- **Windows:** double-click `RUN_ON_WINDOWS.bat`, then type a grade (3, 4, 5, 6) or ALL.
- **Mac/Linux:** run `./run_mac_linux.sh`.
- **Command line:**
  - `python make_audio_elevenlabs.py --check` — test the key, the voices and your credits
  - `python make_audio_elevenlabs.py --grade 3 --dry-run` — see clips and characters, no cost
  - `python make_audio_elevenlabs.py --grade 3 --limit 10` — make 10 clips as a quick test
  - `python make_audio_elevenlabs.py --grade 3` — make all of Grade 3
  - `python make_audio_elevenlabs.py --flash` — use the Flash model, which costs about half the credits

You can stop at any time (Ctrl+C) and run the same command later; finished clips are skipped.

## How many credits?
| Grade | Clips | Characters |
|---|---|---|
| 3 | 563 | 14,514 |
| 4 | 552 | 16,785 |
| 5 | 533 | 22,714 |
| 6 | 533 | 25,757 |
| **All** | **2,181** | **79,770** |

With the default model (`eleven_multilingual_v2`), 1 character is about 1 credit. With `--flash` it is about half. You can make one grade per month to fit a smaller plan.

## Voices
`voices.json` links each character to a standard ElevenLabs voice (for example Sarah for the narrator and George for Grandpa). To change a voice:
1. In ElevenLabs, add the voice you like (for example a child voice from the Voice Library) to **My Voices**.
2. Run `python make_audio_elevenlabs.py --list-voices` and copy its `voice_id`.
3. Paste it into `voices.json`, then run the script with `--force --grade N` to re-make that grade.

## Full lesson tracks
After making clips, the script rebuilds one MP3 per lesson (`track.mp3`) for classroom speakers. If **ffmpeg** is installed, the joins are perfect; without it, the script uses a simple join that works in most players.

---

# إعادة إنتاج الأصوات باستخدام ElevenLabs

يحتوي البرنامج على أصوات تجريبية جاهزة تعمل الآن. يتيح لك هذا المجلد استبدال جميع المقاطع بأصوات ElevenLabs بالأسماء نفسها، فيستخدمها البرنامج تلقائيًا.

1. ثبّت **Python** على جهازك (وفي ويندوز فعّل خيار *Add Python to PATH*).
2. انسخ **مفتاح API** من حسابك في ElevenLabs.
3. أنشئ في هذا المجلد ملفًا نصيًا باسم **`.env`** يحتوي على سطر واحد: `ELEVENLABS_API_KEY=المفتاح`. يبقى المفتاح على جهازك ولا يُرسل إلا إلى ElevenLabs.
4. في ويندوز: انقر نقرًا مزدوجًا على `RUN_ON_WINDOWS.bat` واكتب رقم الصف أو ALL.

يمكنك الإيقاف في أي وقت ثم المتابعة لاحقًا، فالمقاطع المنجزة لا تُعاد. يستهلك البرنامج كاملًا قرابة 80 ألف حرف (أو نصفها تقريبًا مع الخيار `--flash`)، ويمكنك إنتاج صف واحد كل شهر.
