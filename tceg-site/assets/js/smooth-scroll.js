/* ==========================================================================
   Rolagem suave — Lenis sincronizado com GSAP / ScrollTrigger
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;

  T.lenis = null;

  if (T.hasLenis && !T.reduced) {
    var lenis = new window.Lenis({
      duration: 1.15,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 1.4
    });
    T.lenis = lenis;

    if (T.hasST) {
      // Lenis alimenta o ScrollTrigger; o ticker do GSAP conduz o Lenis.
      lenis.on('scroll', window.ScrollTrigger.update);
      window.gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
      window.gsap.ticker.lagSmoothing(0);
    } else {
      var raf = function (time) { lenis.raf(time); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
  }

  // Rolagem programática (âncoras, "voltar ao topo")
  T.scrollToTarget = function (target, opts) {
    opts = opts || {};
    // 0 (ou 'top') rola ao topo da página, sem depender de elemento (o cabeçalho é fixo)
    if (target === 0 || target === 'top') {
      if (T.lenis) T.lenis.scrollTo(0, { duration: opts.duration || 1.5, immediate: !!opts.immediate });
      else window.scrollTo({ top: 0, behavior: T.reduced || opts.immediate ? 'auto' : 'smooth' });
      return;
    }
    var el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;
    if (T.lenis) {
      var margin = parseFloat(getComputedStyle(el).scrollMarginTop) || 0;
      T.lenis.scrollTo(el, { offset: -margin, duration: opts.duration || 1.5, immediate: !!opts.immediate });
    } else {
      el.scrollIntoView({ behavior: T.reduced || opts.immediate ? 'auto' : 'smooth', block: 'start' });
    }
  };

  // Recalcula gatilhos quando fontes/imagens terminam de carregar
  if (T.hasST) {
    window.addEventListener('load', function () { window.ScrollTrigger.refresh(); });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { window.ScrollTrigger.refresh(); });
    }
  }
})();
