/* Bridge between the Grammar and Vocabulary department and the main app (same device, same sign-in).
   It reads who is signed in (the main app keeps that in localStorage), keeps the session awake while
   the student works here, and sends the visitor back to the sign-in page when nobody is signed in. */
(function () {
  'use strict';
  var d = {}; try { d = JSON.parse(localStorage.getItem('lsp_v1') || '{}') || {}; } catch (e) { d = {}; }
  var auth = d.auth || {}, ses = auth.session || null, ready = !!(auth.teacher && auth.teacher.pw);
  var prof = (d.profiles || {})[ses ? ses.id : (d.current || 'guest')] || { id: 'guest', name: 'Guest', cls: '' };
  if (ready && !ses) { location.replace('../index.html'); return; }       // accounts are set up and nobody is signed in
  window.GV_HOST = { uid: prof.id || 'guest', name: prof.name || '', cls: prof.cls || '', role: ses ? ses.role : (ready ? 'student' : 'teacher'), locked: ready };
  /* keep the main app's idle timer fresh while someone is working here */
  var last = 0;
  function touch() {
    var now = Date.now(); if (now - last < 30000) return; last = now;
    try { var x = JSON.parse(localStorage.getItem('lsp_v1') || '{}'); if (x.auth && x.auth.session) { x.auth.session.last = now; localStorage.setItem('lsp_v1', JSON.stringify(x)); } } catch (e) {}
  }
  ['pointerdown', 'keydown'].forEach(function (ev) { document.addEventListener(ev, touch, { capture: true, passive: true }); });
  document.addEventListener('DOMContentLoaded', function () {
    var w = document.getElementById('who'); if (w) { if (prof.name) w.textContent = '👤 ' + prof.name; else w.remove(); }
    if (window.GV_HOST.role !== 'teacher') { var t = document.querySelector('[data-nav="teacher"]'); if (t) t.remove(); }
  });
})();
