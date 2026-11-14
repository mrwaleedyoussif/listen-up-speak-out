/* Listen Up! Speak Out! — a small, safe bridge between the app page and the desktop updater.
   The page can only ask for update information, check, download and install; nothing else. */
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('lspDesktop', {
  update: {
    info: () => ipcRenderer.invoke('upd:info'),
    check: download => ipcRenderer.invoke('upd:check', !!download),
    download: () => ipcRenderer.invoke('upd:download'),
    install: () => ipcRenderer.invoke('upd:install'),
    onEvent: cb => { const h = (_e, m) => cb(m); ipcRenderer.on('upd:event', h); return () => ipcRenderer.removeListener('upd:event', h); }
  }
});
