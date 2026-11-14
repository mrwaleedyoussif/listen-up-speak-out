/* Listen Up! Speak Out! — Windows / macOS / Linux desktop app (Electron).
   Loads the same app as the web and phone editions from the www folder. */
const { app, BrowserWindow, session, shell, Menu, ipcMain } = require('electron');
const path = require('path');

if (!app.requestSingleInstanceLock()) { app.quit(); }
let win = null;

function createWindow() {
  win = new BrowserWindow({
    width: 1280, height: 860, minWidth: 380, minHeight: 560,
    title: 'Listen Up! Speak Out!',
    icon: path.join(__dirname, '..', 'build-res', process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
    backgroundColor: '#F5F7FC',
    autoHideMenuBar: true,
    show: false,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false, sandbox: true, spellcheck: false, autoplayPolicy: 'no-user-gesture-required' }
  });
  win.once('ready-to-show', () => win.show());
  win.loadFile(path.join(__dirname, '..', 'www', 'index.html'));
  // links to websites open in the normal browser, never inside the app
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => { if (!url.startsWith('file:')) { e.preventDefault(); if (/^https?:/.test(url)) shell.openExternal(url); } });
  // F11 full screen for the classroom board, Ctrl +/- zoom
  win.webContents.on('before-input-event', (e, input) => {
    if (input.type === 'keyDown' && input.key === 'F11') { win.setFullScreen(!win.isFullScreen()); e.preventDefault(); }
  });
}

/* ---------- Updates (Windows installer edition) ----------
   electron-updater reads the newest release on GitHub (latest.yml), downloads it in the background
   and installs it when the app closes, or at once when the user presses "Restart and update".
   The portable .exe cannot update itself; the page then shows the download link instead. */
const PORTABLE = !!process.env.PORTABLE_EXECUTABLE_DIR;
let UPD = null;
const newer = (a, b) => { const x = String(a).split('.').map(Number), y = String(b).split('.').map(Number); for (let i = 0; i < 3; i++) { if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) > (y[i] || 0); } return false; };
function updater() {
  if (UPD !== null) return UPD;
  UPD = false;
  if (!app.isPackaged || PORTABLE || process.platform !== 'win32') return UPD;
  try {
    UPD = require('electron-updater').autoUpdater;
    UPD.autoInstallOnAppQuit = true; UPD.allowPrerelease = false; UPD.allowDowngrade = false;
    const send = m => { if (win && !win.isDestroyed()) win.webContents.send('upd:event', m); };
    UPD.on('update-available', i => send({ type: 'available', version: i.version }));
    UPD.on('update-not-available', i => send({ type: 'none', version: i && i.version }));
    UPD.on('download-progress', p => send({ type: 'progress', percent: Math.round(p.percent || 0) }));
    UPD.on('update-downloaded', i => send({ type: 'downloaded', version: i.version }));
    UPD.on('error', e => send({ type: 'error', message: String((e && e.message) || e).slice(0, 200) }));
  } catch (e) { UPD = false; }
  return UPD;
}
const fromApp = e => !!win && e.sender === win.webContents;
ipcMain.handle('upd:info', e => fromApp(e) ? { version: app.getVersion(), portable: PORTABLE, can: !!updater() } : null);
ipcMain.handle('upd:check', async (e, download) => {
  if (!fromApp(e)) return null;
  const u = updater(); if (!u) return { ok: false, reason: PORTABLE ? 'portable' : 'unsupported' };
  u.autoDownload = !!download;
  try {
    const r = await u.checkForUpdates(); const v = r && r.updateInfo && r.updateInfo.version;
    return { ok: true, version: v || null, newer: !!v && newer(v, app.getVersion()) };
  } catch (err) { return { ok: false, reason: 'error', message: String((err && err.message) || err).slice(0, 200) }; }
});
ipcMain.handle('upd:download', async e => { const u = fromApp(e) && updater(); if (!u) return false; try { await u.downloadUpdate(); return true; } catch (err) { return false; } });
ipcMain.handle('upd:install', e => { const u = fromApp(e) && updater(); if (!u) return false; setImmediate(() => u.quitAndInstall(true, true)); return true; });

app.on('second-instance', () => { if (win) { if (win.isMinimized()) win.restore(); win.focus(); } });
app.whenReady().then(() => {
  // only the microphone may be used (for recording practice); everything else is refused
  session.defaultSession.setPermissionRequestHandler((wc, permission, cb, details) => {
    cb(permission === 'media' && (!details.mediaTypes || details.mediaTypes.every(t => t === 'audio')));
  });
  session.defaultSession.setPermissionCheckHandler((wc, permission) => permission === 'media');
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' }] : []),
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'togglefullscreen' }, { type: 'separator' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { role: 'resetZoom' }] },
    { role: 'editMenu' }
  ]));
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
