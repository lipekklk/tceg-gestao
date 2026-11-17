/* ==========================================================================
   Formulários: validação local, envio (Netlify Forms) e assistente em 3 etapas
   - #lead-form      → formulário rápido de contato (home)
   - #unified-form   → solicitação inteligente de proposta (diagnostico.html)
   ========================================================================== */
(function () {
  'use strict';
  var T = window.TCEG;
  var $ = T.$, $$ = T.$$;

  // ---------- Validadores ----------
  // CNPJ numérico ou alfanumérico (14 caracteres, dois dígitos verificadores).
  function cnpjValid(raw) {
    var s = String(raw).trim().toUpperCase().replace(/[.\/\-\s]/g, '');
    if (!/^[A-Z0-9]{12}[0-9]{2}$/.test(s) || /^(.)\1+$/.test(s)) return false;
    function digit(base) {
      var weight = 2, sum = 0;
      for (var i = base.length - 1; i >= 0; i--) {
        sum += (base.charCodeAt(i) - 48) * weight;
        weight = weight === 9 ? 2 : weight + 1;
      }
      var r = sum % 11;
      return r < 2 ? '0' : String(11 - r);
    }
    return digit(s.slice(0, 12)) === s[12] && digit(s.slice(0, 13)) === s[13];
  }

  function phoneValid(raw) {
    if (!/^[+()\d\s.-]+$/.test(raw)) return false;
    var n = raw.replace(/\D/g, '');
    if (n.length > 11 && n.indexOf('55') === 0) n = n.slice(2);
    return /^[1-9][0-9](?:[2-5][0-9]{7}|9[0-9]{8})$/.test(n);
  }

  function message(el) {
    var v = el.value.trim();
    if (el.required && ((el.type === 'checkbox' && !el.checked) || (el.type !== 'checkbox' && !v))) {
      return el.type === 'checkbox' ? 'Confirme a autorização para continuar.' : 'Preencha este campo.';
    }
    if (el.validity && el.validity.badInput) return 'Informe um número válido.';
    if (!v || el.type === 'checkbox') return '';
    if (el.type === 'email' && (el.validity.typeMismatch || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))) {
      return 'Informe um e-mail válido, como nome@empresa.com.br.';
    }
    if (el.name === 'telefone' && !phoneValid(v)) return 'Informe DDD e telefone brasileiro válido, com ou sem +55.';
    if (el.name === 'cnpj' && !cnpjValid(v)) return 'Confira o CNPJ e seus dígitos verificadores (14 caracteres).';
    if (el.type === 'number') {
      var n = Number(v), min = Number(el.min || 0);
      if (!Number.isInteger(n) || n < min || (el.max && n > Number(el.max))) {
        return 'Informe um número inteiro entre ' + (el.min || 0) + ' e ' + el.max + '.';
      }
    }
    if (el.maxLength > 0 && v.length > el.maxLength) return 'Respeite o limite de ' + el.maxLength + ' caracteres.';
    return '';
  }

  // ---------- Configuração de um formulário ----------
  function setup(form) {
    var controls = $$('input,select,textarea', form).filter(function (el) {
      return el.type !== 'hidden' && el.name !== 'bot-field' && el.name !== 'servicos';
    });
    controls.forEach(function (el, i) {
      if (!el.id) el.id = form.id + '-field-' + i;
      var error = document.createElement('span');
      error.id = el.id + '-error';
      error.className = 'field-error';
      error.hidden = true;
      var holder = el.closest('label') || el.parentElement;
      holder.appendChild(error);
      el.setAttribute('aria-describedby', ((el.getAttribute('aria-describedby') || '') + ' ' + error.id).trim());
    });
    function check(el) {
      el.setCustomValidity('');
      var msg = message(el);
      el.setCustomValidity(msg);
      el.setAttribute('aria-invalid', String(!!msg));
      var error = document.getElementById(el.id + '-error');
      if (error) { error.textContent = msg; error.hidden = !msg; }
      return !msg;
    }
    form.addEventListener('input', function (e) {
      if (controls.indexOf(e.target) > -1 && e.target.hasAttribute('aria-invalid')) check(e.target);
    });
    form.addEventListener('focusout', function (e) { if (controls.indexOf(e.target) > -1) check(e.target); });
    return {
      validate: function (root) {
        root = root || form;
        var first = null;
        controls.filter(function (el) { return root.contains(el); }).forEach(function (el) {
          if (!check(el) && !first) first = el;
        });
        return first;
      }
    };
  }

  // ---------- Envio ----------
  var isLocalPreview = location.protocol === 'file:' || /^(localhost|127\.0\.0\.1|\[::1\]|0\.0\.0\.0)$/.test(location.hostname);
  var sending = new WeakSet();

  function submit(form, feedback) {
    if (sending.has(form)) return;
    var button = $('button[type="submit"]', form);
    var label = button.querySelector('.btn__label').textContent;
    sending.add(form);
    button.disabled = true;
    button.querySelector('.btn__label').textContent = 'Enviando solicitação…';
    form.setAttribute('aria-busy', 'true');
    feedback.textContent = 'Enviando sua solicitação.';

    function restore() {
      sending.delete(form);
      button.disabled = false;
      button.querySelector('.btn__label').textContent = label;
      form.removeAttribute('aria-busy');
    }

    // Pré-visualização local: não há servidor para receber o POST (Netlify Forms só
    // processa no site publicado). Simulamos o sucesso para testar o fluxo completo.
    if (isLocalPreview) {
      if (window.console) console.info('[TCEG] Pré-visualização local: nenhum dado foi enviado. O envio real ocorre apenas no site publicado (Netlify Forms).');
      setTimeout(function () { location.assign('obrigado.html'); }, 500);
      return;
    }

    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, 25000);
    var redirected = false;
    fetch(form.getAttribute('action'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(new FormData(form)).toString(),
      signal: controller.signal
    }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      redirected = true;
      location.assign(form.getAttribute('action'));
    }).catch(function () {
      feedback.textContent = 'Não foi possível confirmar o recebimento. Seus dados continuam nesta página. Uma falha de conexão pode ocorrer após o registro: antes de tentar novamente, você pode confirmar pelo WhatsApp ou e-mail da TCEG.';
      feedback.focus();
    }).then(function () {
      clearTimeout(timer);
      if (!redirected) restore();
    });
  }

  // Se o usuário voltar pelo histórico, reativa o botão
  window.addEventListener('pageshow', function () {
    $$('form[data-tceg-form]').forEach(function (form) {
      sending.delete(form);
      form.removeAttribute('aria-busy');
      var b = $('button[type="submit"]', form);
      if (b) { b.disabled = false; var l = b.querySelector('.btn__label'); if (l && l.textContent === 'Enviando solicitação…') l.textContent = b.getAttribute('data-label') || 'Enviar solicitação'; }
    });
  });

  T.onReady(function () {
    // ---------- Formulário rápido (home) ----------
    var lead = $('#lead-form');
    if (lead) {
      var feedback = $('.form-feedback', lead);
      var v = setup(lead);
      lead.addEventListener('submit', function (e) {
        e.preventDefault();
        if (lead.getAttribute('aria-busy') === 'true') return;
        var invalid = v.validate();
        if (invalid) { feedback.textContent = 'Revise os campos indicados.'; invalid.focus(); return; }
        feedback.textContent = '';
        submit(lead, feedback);
      });
    }

    // ---------- Assistente de proposta (3 etapas) ----------
    var form = $('#unified-form');
    if (!form) return;
    var stages = $$('.unified-step', form);
    var markers = $$('.wizard-indicator');
    var fb = $('#unified-feedback');
    var send = $('#unified-send');
    var validator = setup(form);
    var current = 0;
    
    function value(name) { return String(new FormData(form).get(name) || '').trim(); }
    function make(tag, text) { var el = document.createElement(tag); el.textContent = text; return el; }

    function show(n, focus) {
      current = n;
      stages.forEach(function (el, i) { el.hidden = i !== n; });
      markers.forEach(function (el, i) {
        el.classList.toggle('is-active', i === n);
        el.classList.toggle('is-done', i < n);
        if (i === n) el.setAttribute('aria-current', 'step'); else el.removeAttribute('aria-current');
      });
      $('#unified-step-text').textContent = 'Etapa ' + (n + 1) + ' de 3 · ' + (['Identificação', 'Proposta', 'Revisão'][n]);
      $('#unified-back').hidden = n === 0;
      $('#unified-next').hidden = n === 2;
      send.hidden = n !== 2;
      fb.textContent = '';
      if (focus !== false) $('h2', stages[n]).focus();
    }

    function validateStep(n) {
      show(n, false);
      var invalid = validator.validate(stages[n]);
      if (invalid) { fb.textContent = 'Revise os campos indicados.'; invalid.focus(); return false; }
      return true;
    }

    function review() {
      var selected = $$('input[name="servicos"]:checked', form).map(function (el) { return el.value; });
      var labels = { empresa: 'Empresa', cnpj: 'CNPJ', responsavel: 'Responsável', cargo: 'Cargo', email: 'E-mail', telefone: 'Telefone', cidade: 'Cidade / UF', segmento: 'Segmento', trabalhadores: 'Trabalhadores', unidades: 'Unidades', necessidade: 'Demanda', prazo: 'Prazo', modalidade: 'Modalidade', origem_contato: 'Como conheceu a TCEG' };
      var groups = [
        ['#unified-company', ['empresa', 'cnpj', 'responsavel', 'cargo', 'email', 'telefone', 'cidade', 'segmento', 'trabalhadores', 'unidades']],
        ['#unified-details', ['necessidade', 'prazo', 'modalidade', 'origem_contato']]
      ];
      groups.forEach(function (g) {
        var target = $(g[0]);
        while (target.firstChild) target.removeChild(target.firstChild);
        g[1].forEach(function (name) { target.appendChild(make('div', labels[name] + ': ' + (value(name) || 'Não informado'))); });
      });
      var box = $('#unified-selected-services');
      while (box.firstChild) box.removeChild(box.firstChild);
      box.appendChild(make('strong', 'Serviços solicitados'));
      box.appendChild(make('p', selected.join(' · ') || 'Orientação inicial / definição de escopo'));
      $('#unified-services-input').value = selected.join(' | ') || 'Orientação inicial / definição de escopo';
      $('#unified-replyto').value = value('email');
    }

    $('#unified-next').addEventListener('click', function () {
      if (!validateStep(current)) return;
      if (current === 1) review();
      show(Math.min(2, current + 1));
      if (T.lenis) T.lenis.scrollTo(0, { duration: 0.8 }); else window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    $('#unified-back').addEventListener('click', function () { show(Math.max(0, current - 1)); });
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (form.getAttribute('aria-busy') === 'true') return;
      if (current < 2) { $('#unified-next').click(); return; }
      for (var n = 0; n < 3; n++) if (!validateStep(n)) return;
      review();
      submit(form, fb);
    });
    show(0, false);
  });
})();
