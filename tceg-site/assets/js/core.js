/* ==========================================================================
   TCEG — núcleo
   Detecta bibliotecas (GSAP, ScrollTrigger, Lenis) e preferências do usuário.
   Se algo faltar, o site continua totalmente legível e funcional (sem animações).
   ========================================================================== */
(function () {
  'use strict';

  var T = (window.TCEG = window.TCEG || {});
  var root = document.documentElement;

  T.$ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  T.$$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  T.reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  T.finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  T.hasGsap = typeof window.gsap !== 'undefined';
  T.hasST = T.hasGsap && typeof window.ScrollTrigger !== 'undefined';
  T.hasLenis = typeof window.Lenis !== 'undefined';

  // Animações só se: GSAP + ScrollTrigger carregaram, movimento permitido,
  // e o failsafe do <head> não removeu a classe antes das bibliotecas chegarem.
  T.anim = T.hasGsap && T.hasST && !T.reduced && root.classList.contains('js-anim');

  if (T.hasST) window.gsap.registerPlugin(window.ScrollTrigger);
  if (!T.anim) root.classList.remove('js-anim');
  root.classList.add(T.anim ? 'anim-on' : 'anim-off');

  T.onReady = function (fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  };

  T.headerOffset = function () {
    return parseFloat(getComputedStyle(root).getPropertyValue('--header-h')) || 76;
  };
})();
