/* ==========================================================================
   ScrollReveal nativo (adaptado do React Bits "ScrollReveal")
   Palavras acendem uma a uma conforme a rolagem avança — usado apenas nas
   duas declarações de posicionamento. Em movimento reduzido ou sem GSAP,
   o texto aparece normalmente.
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;
  if (!T.anim) return;

  T.onReady(function () {
    T.$$('[data-scroll-reveal]').forEach(function (el) {
      var words = T.splitWords(el);
      if (!words.length) return;
      window.gsap.fromTo(words,
        { opacity: 0.14 },
        {
          opacity: 1,
          ease: 'none',
          stagger: 0.12,
          scrollTrigger: {
            trigger: el,
            start: 'top 84%',
            end: 'bottom 55%',
            scrub: true
          }
        });
    });
  });
})();
