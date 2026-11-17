/* ==========================================================================
   Home — animações orquestradas
   1. Abertura do hero (títulos revelados por caractere + onda no DotGrid)
   2. Visão integrada: três círculos se fundem conforme a rolagem
   3. Soluções: pilha rolável (ScrollStack)
   4. Abordagem: linha que acompanha a rolagem
   Sem GSAP/ScrollTrigger (ou com movimento reduzido), tudo aparece em estado final.
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;
  var $ = T.$, $$ = T.$$;

  T.onReady(function () {
    if (!$('.hero')) return;

    // DotGrid roda mesmo sem GSAP (apenas canvas)
    T.initDotGrid($('.hero__dots'));

    // ---- Pilares ↔ diagrama (funciona sem GSAP) ----
    var venn = $('.venn');
    $$('.pillar[data-p]').forEach(function (p) {
      function on() { if (venn) venn.setAttribute('data-active', p.dataset.p); p.classList.add('is-on'); }
      function off() { if (venn) venn.removeAttribute('data-active'); p.classList.remove('is-on'); }
      p.addEventListener('mouseenter', on); p.addEventListener('mouseleave', off);
      p.addEventListener('focusin', on); p.addEventListener('focusout', off);
    });

    if (!T.anim) return;
    var gsap = window.gsap, ScrollTrigger = window.ScrollTrigger;

    // ---- 1. Abertura do hero ----
    var lines = $$('[data-hero-line]');
    var chars = [];
    lines.forEach(function (l) { chars = chars.concat(T.splitChars(l)); });
    gsap.set(lines, { visibility: 'visible' });
    gsap.set(chars, { yPercent: 118, rotate: 5 });
    var intro = gsap.timeline({ delay: 0.15 });
    intro.to(chars, { yPercent: 0, rotate: 0, duration: 1.25, ease: 'expo.out', stagger: { each: 0.022 } })
         .fromTo('[data-hero-fade]', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.95, ease: 'power3.out', stagger: 0.09 }, '-=0.85');

    // ---- 2. Visão integrada ----
    var section = $('#visao');
    if (section && venn) {
      var offs = { a: { x: -120, y: -80 }, b: { x: 120, y: -80 }, c: { x: 0, y: 130 } };
      var mm = gsap.matchMedia();

      function build(scrollTrigger) {
        var tl = gsap.timeline({ defaults: { ease: 'none' }, scrollTrigger: scrollTrigger });
        Object.keys(offs).forEach(function (k) {
          tl.fromTo($$('[data-p="' + k + '"]', venn), { x: offs[k].x, y: offs[k].y }, { x: 0, y: 0, duration: 1 }, 0);
        });
        tl.fromTo('.venn__spark', { opacity: 0, scale: 0.4, transformOrigin: '50% 50%' }, { opacity: 1, scale: 1, duration: 0.3 }, 0.7);
        tl.fromTo('.vision__note', { opacity: 0.25, y: 14 }, { opacity: 1, y: 0, duration: 0.3 }, 0.7);
        return tl;
      }

      mm.add('(min-width: 960px)', function () {
        build({ trigger: section, start: 'top top', end: '+=105%', scrub: 0.7, pin: true, anticipatePin: 1 });
      });
      mm.add('(max-width: 959px)', function () {
        build({ trigger: venn, start: 'top 88%', end: 'center 48%', scrub: 0.7 });
      });
    }

    // ---- 3. Pilha de soluções ----
    var cards = $$('.sol');
    if (cards.length) {
      var mm2 = gsap.matchMedia();
      mm2.add('(min-width: 900px)', function () {
        cards.forEach(function (card, i) {
          if (i === cards.length - 1) return;
          var next = cards[i + 1];
          gsap.to(card, {
            scale: 1 - (cards.length - 1 - i) * 0.012 - 0.03,
            ease: 'none',
            scrollTrigger: { trigger: next, start: 'top 88%', end: 'top 22%', scrub: true }
          });
        });
      });
    }

    // ---- 4. Abordagem ----
    var steps = $('.steps');
    if (steps) {
      steps.classList.add('is-live');
      var items = $$('.step', steps);
      var update = function (p) {
        steps.style.setProperty('--p', p.toFixed(3));
        items.forEach(function (it, i) {
          it.classList.toggle('is-reached', p >= i / (items.length - 1) - 0.02);
        });
      };
      update(0);
      ScrollTrigger.create({
        trigger: steps,
        start: 'top 72%',
        end: 'bottom 58%',
        scrub: true,
        onUpdate: function (self) { update(self.progress); }
      });
    }
  });
})();
