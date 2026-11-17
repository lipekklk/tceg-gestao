/* ==========================================================================
   Interações: Spotlight, Magnet, Marquee com velocidade de rolagem
   (adaptados dos componentes SpotlightCard, Magnet e ScrollVelocity do React Bits)
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;

  T.onReady(function () {
    // ---- Spotlight: halo que segue o cursor ----
    if (T.finePointer) {
      T.$$('[data-spotlight]').forEach(function (el) {
        el.addEventListener('pointermove', function (e) {
          var r = el.getBoundingClientRect();
          el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
          el.style.setProperty('--my', (e.clientY - r.top) + 'px');
        });
      });
    }

    // ---- Magnet: botões atraídos pelo cursor ----
    if (T.hasGsap && T.finePointer && !T.reduced) {
      T.$$('[data-magnet]').forEach(function (el) {
        var xTo = window.gsap.quickTo(el, 'x', { duration: 0.6, ease: 'power3.out' });
        var yTo = window.gsap.quickTo(el, 'y', { duration: 0.6, ease: 'power3.out' });
        el.addEventListener('pointermove', function (e) {
          var r = el.getBoundingClientRect();
          xTo((e.clientX - (r.left + r.width / 2)) * 0.22);
          yTo((e.clientY - (r.top + r.height / 2)) * 0.32);
        });
        el.addEventListener('pointerleave', function () { xTo(0); yTo(0); });
      });
    }

    // ---- Marquee: acelera com a rolagem e inverte ao subir ----
    var marquee = T.$('.marquee');
    if (marquee && T.anim) {
      var track = T.$('.marquee__track', marquee);
      var tween = window.gsap.to(track, { xPercent: -50, duration: 55, ease: 'none', repeat: -1 });
      marquee.classList.add('is-gsap');
      var dir = 1, boost = 0;
      window.ScrollTrigger.create({
        start: 0, end: 'max',
        onUpdate: function (self) {
          var v = self.getVelocity();
          if (Math.abs(v) > 30) { dir = v < 0 ? -1 : 1; boost = Math.min(Math.abs(v) / 260, 6); }
        }
      });
      window.gsap.ticker.add(function () { boost *= 0.92; tween.timeScale(dir * (1 + boost)); });
      marquee.addEventListener('pointerenter', function () { tween.pause(); });
      marquee.addEventListener('pointerleave', function () { tween.resume(); });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (en) {
          if (en[0].isIntersecting) tween.resume(); else tween.pause();
        }).observe(marquee);
      }
    }
  });
})();
