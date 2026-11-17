/* ==========================================================================
   Acordeão acessível (FAQ) — botão + região, animação por CSS grid
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;

  T.onReady(function () {
    T.$$('.acc__q').forEach(function (q) {
      q.addEventListener('click', function () {
        var open = q.getAttribute('aria-expanded') === 'true';
        q.setAttribute('aria-expanded', String(!open));
        if (T.hasST) setTimeout(function () { window.ScrollTrigger.refresh(); }, 600);
      });
    });
  });
})();
