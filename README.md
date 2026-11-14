# Listen Up! Speak Out!

Elementary listening & speaking program for **Grades 3–6 (CEFR A1 → A2+)** designed by Mr. Waleed Youssef: 24 units, 72 listening lessons, 48 speaking lessons, pronunciation games, Unit Checks, a Shadowing Studio with word-by-word highlighting and recording, a teacher dashboard and Arabic support.

- **Open the web app:** https://mrwaleedyoussif.github.io/listen-up-speak-out/
- **Download the apps (Android, Windows):** [Releases](https://github.com/mrwaleedyoussif/listen-up-speak-out/releases/latest)
- **How to install, update and publish (English & Arabic):** [INSTALL.md](INSTALL.md)

## How the project is built

One app, four editions, all from the `www` folder:

- `www/`: the app itself (HTML/CSS/JS, `data.js` content, `audio/` MP3s with word timings). It works offline and is an installable web app (`manifest.webmanifest`, `sw.js`).
- `android/`, `ios/`: phone and tablet apps ([Capacitor](https://capacitorjs.com)), which put `www` inside a native app.
- `electron/`: the Windows desktop app ([Electron](https://www.electronjs.org)).
- `.github/workflows/build.yml`: every push to `main` builds the web app (GitHub Pages), the Android APK, the Windows installer and an unsigned iOS build, and publishes them on the Releases page.
- `tools/`: the content pipeline (lesson sources in `tools/content`, audio and timing generators, the Teacher's Book generator) and `tools/elevenlabs` for re-voicing all audio with ElevenLabs.

Local commands (Node 22, Python 3):

- `npm ci`: install the build tools.
- `npm run build:www`: refresh `www/sw.js` and `www/audio/files.json` after any change in `www`.
- `npm start`: run the desktop app.
- `npm run win`: build the Windows installer (on Windows).
- `npm run sync`: copy `www` into the Android and iOS projects (then open them in Android Studio or Xcode).

Designed by Mr. Waleed Youssef. © 2026 Mr. Waleed Youssef. All rights reserved.
