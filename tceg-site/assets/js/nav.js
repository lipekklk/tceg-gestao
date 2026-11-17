/* ==========================================================================
   Navegação: header que recolhe, menu em tela cheia, âncoras, trilho de seções
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;
  var $ = T.$, $$ = T.$$;

  T.onReady(function () {
    var header = $('.site-header');
    var menu = $('#menu');
    var btn = $('.menu-btn');

    // ---- Ano no rodapé ----
    $$('[data-year]').forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

    // ---- Header: recolhe ao descer, volta ao subir ----
    var lastY = window.scrollY;
    window.addEventListener('scroll', function () {
      if (!header || document.body.classList.contains('menu-open')) return;
      var y = window.scrollY, d = y - lastY;
      if (y > 220 && d > 8) header.classList.add('is-hidden');
      else if (d < -8 || y <= 140) header.classList.remove('is-hidden');
      lastY = y;
    }, { passive: true });

    // ---- Menu em tela cheia ----
    function setMenu(open) {
      if (!menu || !btn) return;
      menu.classList.toggle('is-open', open);
      menu.setAttribute('aria-hidden', String(!open));
      btn.setAttribute('aria-expanded', String(open));
      btn.querySelector('.menu-btn__label').textContent = open ? 'Fechar' : 'Menu';
      document.body.classList.toggle('menu-open', open);
      if (T.lenis) { if (open) T.lenis.stop(); else T.lenis.start(); }
      if (open) {
        header.classList.remove('is-hidden');
        var first = $('.menu__list a', menu);
        if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 450);
      }
    }
    T.closeMenu = function () { if (menu && menu.classList.contains('is-open')) setMenu(false); };

    if (btn && menu) {
      btn.addEventListener('click', function () { setMenu(!menu.classList.contains('is-open')); });
      document.addEventListener('keydown', function (e) {
        if (!menu.classList.contains('is-open')) return;
        if (e.key === 'Escape') { setMenu(false); btn.focus(); return; }
        if (e.key === 'Tab') {
          var items = $$('a[href], button', menu).concat([btn]);
          var idx = items.indexOf(document.activeElement);
          if (e.shiftKey && idx <= 0) { e.preventDefault(); items[items.length - 1].focus(); }
          else if (!e.shiftKey && idx === items.length - 1) { e.preventDefault(); items[0].focus(); }
        }
      });
      $$('a', menu).forEach(function (a) {
        a.addEventListener('click', function () { if (a.getAttribute('href').charAt(0) !== '#') return; setMenu(false); });
      });
    }

    // ---- Âncoras internas (#id) ----
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href').slice(1);
      // "#" e "#topo" levem ao início da página (o cabeçalho é fixo, não serve de alvo)
      if (!id || id === 'topo') {
        e.preventDefault();
        if (a.closest('#menu')) setMenu(false);
        T.scrollToTarget(0);
        try { history.replaceState(null, '', location.pathname + location.search); } catch (err) { /* file:// */ }
        return;
      }
      var target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      T.scrollToTarget(target);
      try { history.pushState(null, '', '#' + id); } catch (err) { /* file:// */ }
    });

    if (location.hash.length > 1) {
      var t = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (t) window.addEventListener('load', function () { setTimeout(function () { T.scrollToTarget(t, { immediate: true }); }, 80); });
    }

    // ---- Trilho de seções numeradas (home) ----
    var rail = $('.rail');
    if (rail && 'IntersectionObserver' in window) {
      var links = $$('a', rail);
      var map = {};
      links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          links.forEach(function (l) { l.classList.remove('is-active'); l.removeAttribute('aria-current'); });
          var l = map[en.target.id];
          if (l) { l.classList.add('is-active'); l.setAttribute('aria-current', 'true'); }
        });
      }, { rootMargin: '-45% 0px -50% 0px' });
      Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
    }
  });
})();
