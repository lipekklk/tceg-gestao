/* ==========================================================================
   DotGrid nativo (adaptado do React Bits "DotGrid")
   Grade de pontos em canvas que reage ao cursor e abre uma onda na carga.
   Renderiza sob demanda: sem interação, o canvas fica parado.
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;

  T.initDotGrid = function (canvas) {
    if (!canvas || !canvas.getContext) return;
    var host = canvas.parentElement;
    var ctx = canvas.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var GAP = 34, BASE = 1.5, MAX = 5.4, REACH = 180;
    var w = 0, h = 0, cols = 0, rows = 0;
    var mx = -9999, my = -9999, tx = -9999, ty = -9999;
    var ripple = { r: -1, x: 0, y: 0, on: false };
    var raf = 0;
    var interactive = T.finePointer && !T.reduced;

    function resize() {
      var rect = canvas.getBoundingClientRect();
      w = rect.width; h = rect.height;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cols = Math.ceil(w / GAP) + 1;
      rows = Math.ceil(h / GAP) + 1;
      draw();
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      var ox = (w - (cols - 1) * GAP) / 2, oy = (h - (rows - 1) * GAP) / 2;
      var moving = false;
      for (var i = 0; i < cols; i++) {
        for (var j = 0; j < rows; j++) {
          var x = ox + i * GAP, y = oy + j * GAP;
          var t = 0;
          var dx = x - mx, dy = y - my;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < REACH) t = Math.pow(1 - d / REACH, 2);
          if (ripple.on) {
            var rx = x - ripple.x, ry = y - ripple.y;
            var rd = Math.sqrt(rx * rx + ry * ry);
            var k = Math.exp(-Math.pow((rd - ripple.r) / 70, 2));
            t = Math.max(t, k * 0.9);
          }
          var r = BASE + (MAX - BASE) * t;
          // cinza-azulado → laranja-sinal
          var cr = Math.round(159 + (236 - 159) * t);
          var cg = Math.round(176 + (116 - 176) * t);
          var cb = Math.round(186 + (31 - 186) * t);
          ctx.fillStyle = 'rgba(' + cr + ',' + cg + ',' + cb + ',' + (0.2 + 0.75 * t).toFixed(3) + ')';
          ctx.beginPath();
          ctx.arc(x, y, r, 0, 6.2832);
          ctx.fill();
        }
      }
      return moving;
    }

    function tick() {
      var dx = tx - mx, dy = ty - my;
      mx += dx * 0.16; my += dy * 0.16;
      var settled = Math.abs(dx) < 0.4 && Math.abs(dy) < 0.4;
      if (ripple.on) {
        ripple.r += 16;
        if (ripple.r > Math.max(w, h) * 1.3) ripple.on = false;
      }
      draw();
      if (!settled || ripple.on) raf = requestAnimationFrame(tick);
      else raf = 0;
    }
    function kick() { if (!raf) raf = requestAnimationFrame(tick); }

    resize();
    window.addEventListener('resize', resize);

    if (interactive) {
      host.addEventListener('pointermove', function (e) {
        var rect = canvas.getBoundingClientRect();
        tx = e.clientX - rect.left; ty = e.clientY - rect.top;
        if (mx < -9000) { mx = tx; my = ty; }
        kick();
      });
      host.addEventListener('pointerleave', function () { tx = -9999; ty = -9999; mx = -9999; my = -9999; kick(); });
      // onda inicial
      ripple.x = w * 0.72; ripple.y = h * 0.4; ripple.r = 0; ripple.on = true;
      kick();
    }
  };
})();
