/* Listen Up! Speak Out! — Windows / macOS / Linux desktop app (Electron).
   Loads the same app as the web and phone editions from the www folder. */
const { app, BrowserWindow, session, shell, Menu } = require('electron');
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
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, spellcheck: false, autoplayPolicy: 'no-user-gesture-required' }
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
