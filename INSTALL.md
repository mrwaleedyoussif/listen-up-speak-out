# Listen Up! Speak Out! — install and publish guide

This one program runs everywhere, and it is the same in every edition: 24 units, 72 listening lessons, 48 speaking lessons, games, Unit Checks, the Shadowing Studio and the teacher dashboard.

- **Web app (every device):** https://mrwaleedyoussif.github.io/listen-up-speak-out/
- **Android app (.apk), Windows app (.exe), iPhone/iPad file (.ipa):** https://github.com/mrwaleedyoussif/listen-up-speak-out/releases/latest

Student progress is saved **on each device**. To move it to another device, use **Teacher dashboard → Back up all students**, then **Restore a backup** on the new device.

---

## 1. Web app — phones, tablets, Chromebooks and computers

1. Open https://mrwaleedyoussif.github.io/listen-up-speak-out/
2. Install it:
   - **Android (Chrome):** press **📲 Install on this device** on the Home page, or open the Chrome menu and choose **Install app**.
   - **Windows / Mac (Chrome or Edge):** press the install icon in the address bar, or open the menu and choose **Install app**.
   - **iPhone / iPad (Safari):** press **Share ⬆️**, then **Add to Home Screen**.
3. Open **Listen Up!** from the Home Screen, Start menu or desktop. It opens in its own window, like any app.
4. **Offline audio:** at the bottom of the Home page, press **⬇️ Download** next to each grade you teach (Grade 3 is 13 MB; all four grades are 61 MB). After that the lessons play without internet.

The web app updates itself. When a new version is ready, a small message appears; press **Update**.

## 2. Android app (.apk)

1. On the phone or tablet, open the Releases page and download `Listen-Up-Speak-Out-1.0.0.apk`.
2. Open the downloaded file. If Android asks, allow **Install unknown apps** for the browser or file manager, then press **Install**.
3. The first time a student records, Android asks for the **microphone**: press **Allow**.
4. **Updates:** press 🔄 in the app (or wait for its message). It opens the download of the new `.apk`; open the file and press **Update**. Accounts and progress stay.

All the audio is inside the app, so it works with no internet at all.

## 3. Windows app (.exe)

- **Installer:** `Listen-Up-Speak-Out-Setup-1.0.0.exe` installs the app with a desktop shortcut. The installer speaks English or Arabic.
- **Portable:** `Listen-Up-Speak-Out-Portable-1.0.0.exe` runs straight from a USB stick, with no installation.

**Updates:** the installer edition updates itself. It downloads a new version in the background and installs it when the app is closed (or at once with 🔄 → **Restart and update**). The portable edition shows the download link instead.

Windows may show **"Windows protected your PC"** because the app is new and not signed with a paid certificate. Press **More info → Run anyway**.

In class: **F11** switches full screen, and **Ctrl +** / **Ctrl −** zoom in and out for the board.

## 4. iPhone and iPad

- **Now:** use the web app (part 1, "Add to Home Screen"). It works like an app, with the microphone and offline audio.
- **App Store (later):** Apple only installs apps signed by a paid **Apple Developer Program** account (99 USD a year). The project for this is ready in the `ios` folder, and every build checks that it compiles (the `.ipa` file on the Releases page is that unsigned build). With an Apple developer account, open `ios/App/App.xcodeproj` in Xcode on a Mac, choose your team under **Signing & Capabilities**, then **Product → Archive → Distribute App**.

## Accounts, settings and updates

- **First start on a device:** the teacher (or a parent) creates the teacher account (username + password) and saves the **recovery code** that is shown once. Students then sign up with their name, class and a 4-digit PIN.
- **Security:** passwords and PINs are stored only as salted PBKDF2-SHA256 hashes; after 5 wrong tries the user must wait (the wait doubles each time); automatic sign-out after a time without activity; backups are encrypted with the teacher password (AES-GCM). Everything stays on the device.
- **⚙️ Settings:** sounds, spoken praise, volume, recording speed, text size, animations, Arabic support and the shadowing countdown for everyone; class mode, security, students (add, rename, reset PIN, delete), backups, progress reset and automatic updates for the teacher.
- **🔄 Updates:** a red dot means a new version is ready. The web app installs it by itself at a safe moment (never during a lesson). `version.json` on the website tells the apps which version is newest; GitHub Actions publishes it after the Releases page has the new app files.

## 5. Changing the program and making a new version

1. Change the files (for example `www/index.html`, or new audio in `www/audio`).
2. Run `python tools/app/build_www.py` (it refreshes the offline lists and the update check).
3. For a new numbered version, change `"version"` in `package.json` (for example `1.0.0` → `1.1.0`).
4. Commit and push to `main`. GitHub then builds everything automatically (the **Actions** tab shows progress, about 15–25 minutes). The web app updates itself, and the new files appear on the Releases page.

**Voices:** the program's recordings are made with ElevenLabs voices inside Mr. Waleed Youssef's ElevenLabs account, one grade at a time (Grade 3 first, the other grades as credits renew). They are cut into the program's clips and checked with speech recognition (`tools/elevenlabs/el_pipeline.py`). The app itself never connects to ElevenLabs. After new recordings are added, do steps 2–4.

## 6. Publishing to the stores (optional)

**Google Play** (one-time 25 USD Play Console account):

1. Create a private upload key once, on your own PC: `keytool -genkeypair -v -keystore upload.keystore -alias upload -keyalg RSA -keysize 2048 -validity 10000`. Keep the file and passwords safe.
2. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, add four secrets:
   - `ANDROID_KEYSTORE_BASE64`: the keystore file in base64. In PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("upload.keystore"))`
   - `ANDROID_KEYSTORE_PASSWORD`
   - `ANDROID_KEY_ALIAS`: `upload`
   - `ANDROID_KEY_PASSWORD`
3. Push any change. The build then also makes `Listen-Up-Speak-Out-…-play-store.aab`. Upload that file in the Play Console. Because the app is for children, complete the **Families** questions: no ads, no data collected, recordings stay on the device.

Note: APKs signed with the private key cannot install over the shared-key APKs from part 2. Back up students first, uninstall, install the new one, then restore.

**Microsoft Store:** possible later with the same Windows app (a free Microsoft developer account for individuals).

---

# دليل التثبيت والنشر — Listen Up! Speak Out!

البرنامج واحد ويعمل على كل الأجهزة، والمحتوى نفسه في كل النسخ: 24 وحدة، و72 درس استماع، و48 درس تحدث، والألعاب، واختبارات الوحدات، واستوديو التظليل، ولوحة المعلم.

- **تطبيق الويب (لكل الأجهزة):** https://mrwaleedyoussif.github.io/listen-up-speak-out/
- **تطبيق أندرويد (apk) وتطبيق ويندوز (exe) وملف الآيفون والآيباد (ipa):** https://github.com/mrwaleedyoussif/listen-up-speak-out/releases/latest

يُحفظ تقدّم الطلاب **على كل جهاز**. لنقله إلى جهاز آخر استخدم **لوحة المعلم ← Back up all students** ثم **Restore a backup** على الجهاز الجديد.

## ١. تطبيق الويب: الهواتف والأجهزة اللوحية والحواسيب

1. افتح الرابط أعلاه.
2. ثبّته:
   - **أندرويد (كروم):** اضغط **📲 Install on this device** في الصفحة الرئيسية، أو من قائمة كروم اختر **تثبيت التطبيق**.
   - **ويندوز أو ماك (كروم أو إيدج):** اضغط أيقونة التثبيت في شريط العنوان، أو اختر **تثبيت التطبيق** من القائمة.
   - **آيفون أو آيباد (سفاري):** اضغط **مشاركة ⬆️** ثم **إضافة إلى الشاشة الرئيسية**.
3. افتح **Listen Up!** من الشاشة الرئيسية، فيعمل في نافذة مستقلة مثل أي تطبيق.
4. **الصوت دون إنترنت:** في أسفل الصفحة الرئيسية اضغط **⬇️ Download** بجانب كل صف تدرّسه، فتعمل الدروس بعدها دون إنترنت.

يتحدّث تطبيق الويب تلقائيًا. عند ظهور رسالة الإصدار الجديد اضغط **Update**.

## ٢. تطبيق أندرويد (apk)

1. من الجهاز نفسه افتح صفحة الإصدارات ونزّل ملف `Listen-Up-Speak-Out-1.0.0.apk`.
2. افتح الملف. إذا طلب أندرويد ذلك فاسمح بـ **تثبيت التطبيقات غير المعروفة** للمتصفح أو مدير الملفات، ثم اضغط **تثبيت**.
3. عند أول تسجيل صوتي يطلب أندرويد إذن **الميكروفون**، فاضغط **سماح**.
4. **التحديث:** اضغط 🔄 في التطبيق (أو انتظر رسالته)، فيفتح تنزيل ملف apk الجديد؛ افتحه واضغط **تحديث**. تبقى الحسابات والتقدّم.

كل الصوتيات داخل التطبيق، فيعمل دون إنترنت إطلاقًا.

## ٣. تطبيق ويندوز (exe)

- **المثبّت:** الملف `Listen-Up-Speak-Out-Setup-1.0.0.exe` يثبّت التطبيق مع اختصار على سطح المكتب، والمثبّت بالعربية أو الإنجليزية.
- **النسخة المحمولة:** الملف `Listen-Up-Speak-Out-Portable-1.0.0.exe` يعمل مباشرة من ذاكرة USB دون تثبيت.

**التحديث:** نسخة المثبّت تحدّث نفسها؛ تنزّل الإصدار الجديد في الخلفية وتثبّته عند إغلاق التطبيق (أو فورًا من 🔄 ← **Restart and update**). أما النسخة المحمولة فتعرض رابط التنزيل.

قد يظهر تنبيه **"Windows protected your PC"** لأن التطبيق جديد وغير موقّع بشهادة مدفوعة. اضغط **More info** ثم **Run anyway**.

في الفصل: مفتاح **F11** للشاشة الكاملة، و**Ctrl +** و**Ctrl −** للتكبير والتصغير على السبورة.

## ٤. الآيفون والآيباد

- **الآن:** استخدم تطبيق الويب (القسم ١، «إضافة إلى الشاشة الرئيسية»)، ويعمل كتطبيق مع الميكروفون والصوت دون إنترنت.
- **متجر App Store لاحقًا:** تشترط أبل حساب **Apple Developer Program** المدفوع (99 دولارًا سنويًا). المشروع جاهز في مجلد `ios`، وبعد إنشاء الحساب يُفتح في برنامج Xcode على جهاز ماك ويُرفع إلى المتجر.

## الحسابات والإعدادات والتحديثات

- **أول تشغيل على الجهاز:** ينشئ المعلم (أو ولي الأمر) حساب المعلم باسم مستخدم وكلمة مرور، ويحفظ **رمز الاسترداد** الذي يظهر مرة واحدة. ثم يسجّل الطلاب بالاسم والفصل ورمز من 4 أرقام.
- **الأمان:** تُحفظ كلمات المرور والرموز كبصمات مشفّرة فقط، ويجب الانتظار بعد 5 محاولات خاطئة، مع خروج تلقائي بعد مدة دون نشاط، وتُشفَّر النسخ الاحتياطية بكلمة مرور المعلم. تبقى جميع البيانات على الجهاز.
- **⚙️ الإعدادات:** الأصوات وسرعة التسجيلات وحجم الخط والدعم بالعربية للجميع، وإعدادات الفصل والأمان والطلاب والنسخ الاحتياطية والتحديث التلقائي للمعلم.
- **🔄 التحديثات:** تعني النقطة الحمراء أن إصدارًا جديدًا جاهز، ويثبّته تطبيق الويب تلقائيًا في وقت مناسب.

## ٥. تعديل البرنامج وإصدار نسخة جديدة

1. عدّل الملفات (مثل `www/index.html` أو صوتيات جديدة في `www/audio`).
2. شغّل `python tools/app/build_www.py`.
3. لإصدار رقم جديد غيّر `"version"` في ملف `package.json`.
4. ارفع التعديل إلى `main`، فيبني GitHub كل النسخ تلقائيًا خلال 15 إلى 25 دقيقة (تابعها من تبويب **Actions**)، ويتحدّث تطبيق الويب، وتظهر الملفات الجديدة في صفحة الإصدارات.

**الأصوات:** تُسجَّل صوتيات البرنامج بأصوات ElevenLabs داخل حساب الأستاذ وليد يوسف، صفًّا بعد صف (الصف الثالث أولًا)، ثم تُقسَّم إلى مقاطع البرنامج وتُفحص بالتعرّف على الكلام. لا يتصل التطبيق نفسه بـ ElevenLabs.

## ٦. النشر في المتاجر (اختياري)

**Google Play:** يتطلب حساب Play Console برسوم 25 دولارًا مرة واحدة. أنشئ مفتاح توقيع خاصًا على حاسوبك، وأضفه مع كلمات المرور إلى GitHub كأسرار (القسم 6 في الجزء الإنجليزي)، فيُبنى ملف `.aab` الخاص بالمتجر تلقائيًا لترفعه في Play Console. ولأن التطبيق للأطفال أكمل أسئلة **Families**: لا إعلانات، ولا جمع بيانات، والتسجيلات تبقى على الجهاز.

**Microsoft Store:** ممكن لاحقًا بتطبيق ويندوز نفسه.
