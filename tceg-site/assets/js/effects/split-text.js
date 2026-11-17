/* ==========================================================================
   SplitText nativo (inspirado no componente "SplitText" do React Bits)
   - splitChars(el): divide em caracteres, mantendo texto acessível
   - splitWords(el): divide em palavras, preservando elementos internos
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;

  T.splitChars = function (el) {
    var text = el.textContent.replace(/\s+/g, ' ').trim();
    el.textContent = '';

    // Texto original para leitores de tela
    var sr = document.createElement('span');
    sr.className = 'visually-hidden';
    sr.textContent = text;
    el.appendChild(sr);

    var visual = document.createElement('span');
    visual.setAttribute('aria-hidden', 'true');
    el.appendChild(visual);

    var chars = [];
    text.split(' ').forEach(function (word, wi, arr) {
      var w = document.createElement('span');
      w.style.display = 'inline-block';
      w.style.whiteSpace = 'nowrap';
      Array.prototype.forEach.call(word, function (ch) {
        var c = document.createElement('span');
        c.style.display = 'inline-block';
        c.textContent = ch;
        w.appendChild(c);
        chars.push(c);
      });
      visual.appendChild(w);
      if (wi < arr.length - 1) visual.appendChild(document.createTextNode(' '));
    });
    return chars;
  };

  T.splitWords = function (el) {
    var words = [];
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(function (node) {
      if (!node.textContent.trim()) return;
      var frag = document.createDocumentFragment();
      node.textContent.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
        var s = document.createElement('span');
        s.textContent = part;
        s.style.display = 'inline-block';
        frag.appendChild(s);
        words.push(s);
      });
      node.parentNode.replaceChild(frag, node);
    });
    return words;
  };
})();
