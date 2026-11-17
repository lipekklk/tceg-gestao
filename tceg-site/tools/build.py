#!/usr/bin/env python3
"""
TCEG — gerador do site estático.

Gera todas as páginas HTML na raiz do projeto a partir de:
  - tools/partials/home.html  (conteúdo da página inicial)
  - os dados e modelos abaixo (páginas internas)

Uso:  python3 tools/build.py

O HTML gerado é independente: o site funciona sem executar este script.
Ele existe apenas para manter cabeçalho, menu e rodapé idênticos em todas as páginas.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.tceg.com.br"
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800"
         "&family=Instrument+Sans:wght@400;500;600;700&display=swap")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"
SCROLLTRIGGER = "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"
LENIS = "https://cdn.jsdelivr.net/npm/lenis@1.1.20/dist/lenis.min.js"
WHATSAPP = "https://wa.me/5513998089720"
INSTAGRAM = "https://instagram.com/tcegconformidade"
EMAIL = "contato@tceg.com.br"
ORG_DESC = ("TCEG: consultoria em Segurança e Saúde do Trabalho, PGR, PCMSO, LTCAT, avaliações ocupacionais, "
            "ergonomia e eSocial SST. Baixada Santista e São Paulo.")
OG_IMAGE = SITE + "/assets/tceg-industria-medicina.webp"

# ----------------------------------------------------------------------------
# Ícones (sprite SVG, 24x24, traço)
# ----------------------------------------------------------------------------
ICONS = {
    "arrow": '<path d="M7 17 17 7M8 7h9v9"/>',
    "shield": '<path d="M12 3 19 6v5c0 5-3 8-7 10-4-2-7-5-7-10V6z"/><path d="m9 12 2 2 4-4"/>',
    "cross": '<path d="M9 4h6v5h5v6h-5v5H9v-5H4V9h5z"/>',
    "doc": '<path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="m10 14 2 2 3.5-4.5"/>',
    "file": '<path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="M10 12h6M10 16h6"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4"/><path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3"/>',
    "gauge": '<path d="M4 17a8 8 0 1 1 16 0"/><path d="m12 17 4-5"/><path d="M8 21h8"/>',
    "nodes": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8.5 6h7M7.3 8.2l3.6 7.6M16.7 8.2l-3.6 7.6"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
    "brief": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 13h18"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="m3.5 6 1 1 2-2M3.5 12l1 1 2-2M3.5 18l1 1 2-2"/>',
    "people": '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.5 2.5-6 6-6s6 2.5 6 6M15 14.5c3 0 6 1.5 6 5.5"/>',
    "ear": '<path d="M8 10a4 4 0 1 1 8 0c0 3-2 3.5-2 6a3 3 0 0 1-6 0"/><path d="M12 10a1.5 1.5 0 0 1 1.5 1.5"/>',
    "wave": '<path d="M2 12c1.5-5 3-5 4.5 0s3 5 4.5 0 3-5 4.5 0 3 5 4.5 0"/>',
    "spark": '<path d="M12 3v18M4.2 7.5l15.6 9M19.8 7.5l-15.6 9"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "insta": '<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.5"/><path d="M17 7h.01"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
}


def sprite():
    symbols = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    return f'<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true" focusable="false">{symbols}</svg>'


def icon(name, cls="i"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def ico():
    return f'<span class="btn__ico">{icon("arrow")}</span>'


def render(text):
    text = text.replace("{{ico}}", ico())
    return re.sub(r"\{\{i:([a-z]+)\}\}", lambda m: icon(m.group(1)), text)


def btn(label, href, kind="primary", small=False, extra=""):
    cls = f"btn btn--{kind}" + (" btn--sm" if small else "")
    return f'<a class="{cls}" href="{href}"{extra}><span class="btn__label">{label}</span>{ico()}</a>'


# ----------------------------------------------------------------------------
# Estrutura compartilhada
# ----------------------------------------------------------------------------
def head(title, desc, path, robots="index,follow", jsonld=None):
    canonical = SITE + "/" + path
    ld = ""
    for obj in (jsonld or []):
        ld += f'\n  <script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'
    return f"""<!doctype html>
<html lang="pt-BR" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#1e252d">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="{robots}">
  <meta name="author" content="TCEG – Gestão Estratégica e Conformidade Técnica">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1600">
  <meta property="og:image:height" content="854">
  <meta property="og:image:alt" content="Imagem ilustrativa de segurança e saúde ocupacional em ambiente industrial">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS.replace(chr(38), chr(38)+"amp;")}">
  <link rel="stylesheet" href="assets/css/tokens.css">
  <link rel="stylesheet" href="assets/css/base.css">
  <link rel="stylesheet" href="assets/css/components.css">
  <link rel="stylesheet" href="assets/css/home.css">
  <link rel="stylesheet" href="assets/css/pages.css">
  <script>
    /* Aprimoramento progressivo: estados iniciais de animação só valem se o JS rodar. */
    (function () {{
      var d = document.documentElement;
      d.classList.remove('no-js'); d.classList.add('js');
      if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
        d.classList.add('js-anim');
        setTimeout(function () {{ d.classList.remove('js-anim'); }}, 4500); /* failsafe: CDN lenta */
      }}
    }})();
  </script>{ld}
</head>"""


SCRIPTS_COMMON = [
    GSAP, SCROLLTRIGGER, LENIS,
    "assets/js/core.js", "assets/js/smooth-scroll.js",
    "assets/js/effects/split-text.js", "assets/js/effects/dot-grid.js",
    "assets/js/effects/interactions.js", "assets/js/effects/scroll-reveal.js",
    "assets/js/nav.js", "assets/js/accordion.js", "assets/js/forms.js",
]


def scripts(home=False):
    # defer preserva a ordem de execução: bibliotecas → módulos
    items = SCRIPTS_COMMON + (["assets/js/home.js"] if home else [])
    return "\n".join(f'  <script src="{s}" defer></script>' for s in items)


def header(home, cta_href):
    base = "" if home else "index.html"
    return f"""<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
{sprite()}
<header class="site-header" id="topo">
  <div class="container site-header__inner">
    <a class="brand" href="{base or '#'}" aria-label="TCEG – página inicial">
      <img src="assets/img/logo-wordmark.svg" alt="TCEG" width="395" height="130">
      <span class="brand__text">Gestão estratégica e<br>conformidade técnica</span>
    </a>
    <nav class="nav" aria-label="Principal">
      <a href="{'index.html' if not home else '#'}">Início</a>
      <a href="servicos.html">Serviços</a>
      <a href="cases.html">Nossa atuação</a>
      <a href="faq.html">Perguntas frequentes</a>
    </nav>
    <div class="site-header__actions">
      {btn('Solicitar proposta', cta_href, 'primary', True)}
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="menu-btn__label">Menu</span><span class="menu-btn__bars" aria-hidden="true"></span></button>
    </div>
  </div>
</header>"""


def menu(home):
    p = "" if home else "index.html"
    main = [("Sobre", "sobre"), ("Missão e valores", "diretrizes"), ("Soluções", "solucoes"),
            ("Ferramentas", "ferramentas"), ("Diferenciais", "diferenciais"), ("Dúvidas", "faq")]
    n = 0
    li_main = ""
    for label, anchor in main:
        li_main += f'<a href="{p}#{anchor}" data-m style="--i:{n}">{label}</a>\n          '
        n += 1
    sec = [("Início", "index.html" if not home else "#"), ("Serviços em detalhe", "servicos.html"),
           ("Nossa atuação", "cases.html"), ("Perguntas frequentes", "faq.html"),
           ("Solicitar proposta", "#contato" if home else "diagnostico.html")]
    li_sec = ""
    for label, href in sec:
        li_sec += f'<a href="{href}" data-m style="--i:{n}">{label}</a>\n          '
        n += 1
    return f"""<div class="menu" id="menu" role="dialog" aria-modal="true" aria-label="Menu do site" aria-hidden="true">
  <div class="container menu__grid">
    <nav aria-label="Menu completo">
      <div class="menu__list">
          {li_main}</div>
      <div class="menu__list menu__list--secondary" style="margin-top:2rem">
          {li_sec}</div>
    </nav>
    <div class="menu__aside">
      <div>
        <a class="contact-line" href="mailto:{EMAIL}" data-m style="--i:{n}">{icon('mail')}<span>{EMAIL}</span></a>
        <a class="contact-line" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer" data-m style="--i:{n+1}">{icon('chat')}<span>Atendimento via WhatsApp</span></a>
        <a class="contact-line" href="{INSTAGRAM}" target="_blank" rel="noopener noreferrer" data-m style="--i:{n+2}">{icon('insta')}<span>@tcegconformidade</span></a>
      </div>
      <p data-m style="--i:{n+3}">Atendimento: Baixada Santista e São Paulo</p>
    </div>
  </div>
</div>"""


def footer(home):
    p = "" if home else "index.html"
    cta = "#contato" if home else "diagnostico.html"
    return f"""<footer class="site-footer on-dark">
  <div class="container">
    <div class="site-footer__top">
      <div>
        <a class="brand" href="{p or '#'}" aria-label="TCEG – página inicial">
          <img src="assets/img/logo-wordmark.svg" alt="TCEG" width="395" height="130" loading="lazy">
          <span class="brand__text" style="display:block">Gestão estratégica e<br>conformidade técnica</span>
        </a>
        <p class="site-footer__claim">Gestão estratégica. Conformidade técnica. Compromisso com pessoas e negócios.</p>
      </div>
      <div>
        <h2>Explore</h2>
        <ul>
          <li><a href="{p}#sobre">Sobre a TCEG</a></li>
          <li><a href="{p}#diferenciais">Diferenciais</a></li>
          <li><a href="{p}#solucoes">Soluções</a></li>
          <li><a href="{p}#contato">Contato</a></li>
          <li><a href="privacidade.html">Privacidade e dados pessoais</a></li>
        </ul>
      </div>
      <div>
        <h2>Serviços</h2>
        <ul>
          <li><a href="servicos.html">Todos os serviços</a></li>
          <li><a href="cases.html">Nossa atuação</a></li>
          <li><a href="faq.html">Perguntas frequentes</a></li>
        </ul>
      </div>
      <div>
        <h2>Contato</h2>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="{INSTAGRAM}" target="_blank" rel="noopener noreferrer">@tcegconformidade</a></li>
          <li><a href="{cta}">Solicitar proposta</a></li>
          <li><a href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">Atendimento via WhatsApp</a></li>
        </ul>
      </div>
    </div>
    <div class="site-footer__bottom">
      <div>
        <p>© <span data-year>2026</span> TCEG – Gestão Estratégica e Conformidade Técnica.</p>
        <p>Atendimento: Baixada Santista e São Paulo</p>
        <p>Segurança do Trabalho · Medicina Ocupacional · Conformidade Técnica</p>
      </div>
      <a class="back-top" href="#">Voltar ao topo ↑</a>
    </div>
  </div>
</footer>"""


RAIL = """<nav class="rail" aria-label="Seções da página">
  <ul>
    <li><a href="#sobre"><span>Quem somos</span><b>01</b></a></li>
    <li><a href="#diretrizes"><span>Nossa essência</span><b>02</b></a></li>
    <li><a href="#diferenciais"><span>Diferenciais TCEG</span><b>03</b></a></li>
    <li><a href="#solucoes"><span>Nossas soluções</span><b>04</b></a></li>
    <li><a href="#metodologia"><span>Nossa abordagem</span><b>05</b></a></li>
    <li><a href="#faq"><span>Dúvidas frequentes</span><b>06</b></a></li>
    <li><a href="#contato"><span>Entre em contato</span><b>07</b></a></li>
  </ul>
</nav>"""

MARK = ('<svg class="phero__mark" viewBox="0 0 640 600" aria-hidden="true">'
        '<defs><clipPath id="m-a"><circle cx="240" cy="235" r="175"/></clipPath><clipPath id="m-b"><circle cx="400" cy="235" r="175"/></clipPath></defs>'
        '<circle cx="240" cy="235" r="175"/><circle cx="400" cy="235" r="175"/><circle cx="320" cy="375" r="175"/>'
        '<g clip-path="url(#m-a)"><g clip-path="url(#m-b)"><circle class="core" cx="320" cy="375" r="175"/></g></g></svg>')


def page(*, title, desc, path, body, home=False, robots="index,follow", jsonld=None, cta=None, rail=False, body_class=""):
    cta = cta or ("#contato" if home else "diagnostico.html")
    html = head(title, desc, path, robots, jsonld)
    html += f'\n<body class="{body_class}">\n{header(home, cta)}\n{menu(home)}\n'
    html += (RAIL + "\n") if rail else ""
    html += body + "\n" + footer(home) + "\n" + scripts(home) + "\n</body>\n</html>\n"
    return render(html)


def write(name, html):
    (ROOT / name).write_text(html, encoding="utf-8")
    print("  ✓", name)


def breadcrumbs(items):
    """items: lista de (rótulo, href|None)."""
    li = ""
    for i, (label, href) in enumerate(items):
        if href:
            li += f'<li><a href="{href}">{label}</a></li>'
        else:
            li += f'<li aria-current="page">{label}</li>'
    return f'<nav aria-label="Trilha de navegação" class="crumbs"><ol>{li}</ol></nav>'


def phero(kicker, h1, lede, crumbs_html=""):
    return f"""<section class="phero on-dark">
  {MARK}
  <div class="container phero__inner">
    {crumbs_html}
    <p class="kicker">{kicker}</p>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>"""


# ----------------------------------------------------------------------------
# Dados: soluções
# ----------------------------------------------------------------------------
SERVICES = [
    dict(slug="pgr", title="PGR e gestão de riscos ocupacionais", short="PGR e gestão de riscos ocupacionais",
         tag="Gestão de riscos ocupacionais",
         meta="PGR e gestão de riscos ocupacionais: inventário, plano de ação e definição do escopo conforme a operação. Atendimento TCEG na Baixada Santista e São Paulo.",
         lede="Estruture a identificação dos perigos, a avaliação dos riscos e o planejamento de medidas de prevenção.",
         summary="Inventário de riscos ocupacionais, plano de ação e apoio à implementação de controles.",
         ref="NR-1 e disposições aplicáveis. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="O conteúdo e as avaliações dependem das atividades, processos, exposições e informações disponíveis.",
         h3="Organização do escopo e entregáveis",
         body="O trabalho pode compreender reconhecimento das atividades, inventário de riscos e plano de ação, conforme a aplicabilidade e o contrato. Para dimensionar a proposta, informe funções, unidades, processos e documentos disponíveis. A implementação e o acompanhamento das medidas devem ter responsabilidades definidas entre os envolvidos.",
         card="Serviço especializado", card_title="PGR e gestão de riscos ocupacionais",
         card_desc="Estruture a identificação dos perigos, a avaliação dos riscos e o planejamento de medidas de prevenção."),
    dict(slug="pcmso", title="PCMSO e medicina ocupacional", short="PCMSO e medicina ocupacional",
         tag="Medicina ocupacional",
         meta="PCMSO e medicina ocupacional com planejamento orientado pelos riscos e coordenação de atendimentos. Conheça o escopo e solicite uma proposta à TCEG.",
         lede="Organize o planejamento médico ocupacional com foco nos riscos identificados e no acompanhamento da saúde dos trabalhadores.",
         summary="Programa de Controle Médico de Saúde Ocupacional e coordenação de exames clínicos e complementares pertinentes.",
         ref="NR-7 e demais requisitos pertinentes. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="Exames, periodicidades e critérios são definidos pelo médico responsável, conforme o caso.",
         h3="Integração com os riscos e a rede de atendimento",
         body="Informe funções, número de trabalhadores, localidades e documentação de riscos disponível. O escopo pode abranger planejamento do programa e coordenação dos atendimentos previstos, com critérios médicos definidos pelo responsável habilitado. A escolha da rede de saúde ocupacional deve ser alinhada com o cliente.",
         card_title="PCMSO e medicina ocupacional",
         card_desc="Organize o planejamento médico ocupacional com foco nos riscos identificados e no acompanhamento da saúde dos trabalhadores."),
    dict(slug="ltcat", title="LTCAT e laudos técnicos", short="LTCAT e laudos técnicos",
         tag="Laudos técnicos",
         meta="LTCAT e laudos técnicos de insalubridade e periculosidade: conheça finalidades, informações necessárias e critérios para solicitar uma proposta à TCEG.",
         lede="Documentação técnica para subsidiar a caracterização de exposições e enquadramentos trabalhistas e previdenciários.",
         summary="LTCAT, laudos de insalubridade e periculosidade e avaliações de exposição, conforme escopo.",
         ref="Decreto nº 3.048/1999, NR-15, NR-16 e demais requisitos pertinentes. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="A emissão dos laudos exige avaliação das condições reais e responsável técnico legalmente habilitado.",
         h3="Finalidade dos documentos e informações necessárias",
         body="LTCAT e laudos de insalubridade ou periculosidade têm finalidades distintas; o documento necessário deve ser definido conforme a demanda. Informe atividades, agentes, locais de trabalho e registros existentes. A necessidade de visita e de medições será definida na análise técnica do escopo.",
         card_title="LTCAT e laudos técnicos",
         card_desc="Documentação técnica para subsidiar a caracterização de exposições e enquadramentos trabalhistas e previdenciários."),
    dict(slug="avaliacoes-ocupacionais", title="Avaliações ambientais ocupacionais", short="Avaliações ambientais ocupacionais",
         tag="Avaliações ambientais ocupacionais",
         meta="Avaliações ocupacionais de ruído, calor, vibrações e agentes químicos, com planejamento conforme a exposição. Solicite análise de escopo à TCEG.",
         lede="Medições e avaliações técnicas de agentes físicos, químicos e outros fatores pertinentes aos ambientes de trabalho.",
         summary="Dosimetria de ruído, calor, vibrações, agentes químicos e outras avaliações conforme necessidade.",
         ref="Normas de Higiene Ocupacional da Fundacentro e Normas Regulamentadoras aplicáveis. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="A escolha de métodos e instrumentos depende de reconhecimento técnico e estratégia de amostragem.",
         h3="Planejamento das avaliações",
         body="Informe os agentes suspeitos, tarefas, jornadas, locais e avaliações anteriores. O reconhecimento orienta a estratégia de amostragem e a escolha dos métodos e equipamentos. Resultados devem ser interpretados dentro das condições avaliadas; uma medição isolada não representa automaticamente todos os ambientes ou jornadas.",
         card_title="Avaliações ambientais ocupacionais",
         card_desc="Medições e avaliações técnicas de agentes físicos, químicos e outros fatores pertinentes aos ambientes de trabalho."),
    dict(slug="ergonomia", title="Ergonomia: AEP e AET", short="Ergonomia: AEP e AET",
         tag="Ergonomia",
         meta="Ergonomia com AEP e AET conforme a necessidade: avaliação das tarefas, organização do trabalho e recomendações. Conheça o atendimento da TCEG.",
         lede="Apoio à avaliação das condições de trabalho e à melhoria da adequação das tarefas às características psicofisiológicas dos trabalhadores.",
         summary="Avaliação Ergonômica Preliminar, Análise Ergonômica do Trabalho quando aplicável e recomendações técnicas.",
         ref="NR-17 e requisitos pertinentes. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="A abordagem depende da organização do trabalho, das tarefas e das situações analisadas.",
         h3="Entendimento das tarefas e organização do trabalho",
         body="Informe funções, postos, demandas físicas e cognitivas e mudanças previstas. A avaliação preliminar e a análise aprofundada têm escopos diferentes, definidos conforme as situações de trabalho. As recomendações devem considerar as atividades reais e ser acompanhadas conforme o plano acordado.",
         card_title="Ergonomia: AEP e AET",
         card_desc="Apoio à avaliação das condições de trabalho e à melhoria da adequação das tarefas às características psicofisiológicas dos trabalhadores."),
    dict(slug="esocial-sst", title="Gestão eSocial SST", short="Gestão eSocial SST",
         tag="Gestão de SST e conformidade",
         meta="Gestão eSocial SST com apoio à consistência documental, organização de informações e responsabilidades. Conheça o escopo e solicite proposta à TCEG.",
         lede="Organize informações e processos necessários ao atendimento das obrigações de Segurança e Saúde no Trabalho no eSocial.",
         summary="Apoio à consistência documental e à gestão dos eventos SST, conforme responsabilidades contratadas.",
         ref="Leiautes e orientações oficiais do eSocial e legislação aplicável. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="Transmissões e responsabilidades devem observar o enquadramento e as fontes oficiais vigentes.",
         h3="Consistência das informações e responsabilidades",
         body="Informe os eventos envolvidos, a rotina atual de envio e as fontes documentais disponíveis. O escopo pode incluir conferência de informações e apoio à organização de prazos e responsabilidades. O envio de eventos não substitui a elaboração dos documentos técnicos ou a execução das medidas de prevenção.",
         card_title="Gestão eSocial SST",
         card_desc="Organize informações e processos necessários ao atendimento das obrigações de Segurança e Saúde no Trabalho no eSocial."),
    dict(slug="treinamentos", title="Treinamentos e prevenção", short="Treinamentos de segurança",
         tag="Capacitação e prevenção",
         meta="Treinamentos de segurança, prevenção e planos de emergência conforme atividades e normas aplicáveis. Informe sua necessidade e solicite proposta à TCEG.",
         lede="Capacitações e procedimentos orientados aos riscos e atividades executadas pelas equipes.",
         summary="Treinamentos NR, orientações operacionais e planos de emergência e resgate, conforme escopo.",
         ref="Normas Regulamentadoras aplicáveis à atividade. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="Carga horária, conteúdo e requisitos de instrutores dependem da norma e da modalidade pertinente.",
         h3="Planejamento das capacitações",
         body="Informe atividades, quantidade de participantes, localidades e necessidades de capacitação. A definição de conteúdo, duração, modalidade, requisitos de instrutores e registros depende da norma aplicável e do escopo. Treinamentos e planos de emergência exigem alinhamento com a realidade operacional da empresa.",
         card_title="Treinamentos e prevenção",
         card_desc="Capacitações e procedimentos orientados aos riscos e atividades executadas pelas equipes."),
    dict(slug="pca-ppr", title="PCA e PPR: programas preventivos", short="PCA e PPR",
         tag="Programas preventivos",
         meta="PCA e PPR: organização de medidas para conservação auditiva e proteção respiratória conforme exposições. Conheça o escopo e fale com a TCEG.",
         lede="Estruture medidas preventivas e acompanhamento de exposições relacionadas a ruído e proteção respiratória.",
         summary="Programa de Conservação Auditiva e Programa de Proteção Respiratória, conforme necessidade.",
         ref="Normas aplicáveis e referências técnicas pertinentes. Os requisitos específicos são verificados conforme a atividade e o caso concreto.",
         crit="As medidas devem considerar riscos, avaliação de exposição, EPI e gestão operacional.",
         h3="Programas conectados às exposições",
         body="Informe atividades com ruído ou agentes que demandem proteção respiratória, avaliações existentes e medidas já adotadas. O escopo pode compreender organização de procedimentos e acompanhamento de medidas preventivas. A seleção de proteção e os controles devem considerar as condições reais e os critérios técnicos aplicáveis.",
         card_title="PCA e PPR: programas preventivos",
         card_desc="Estruture medidas preventivas e acompanhamento de exposições relacionadas a ruído e proteção respiratória."),
]

# Ordem exibida na página /servicos (igual ao site original)
SERVICES_ORDER = ["pgr", "pcmso", "ltcat", "avaliacoes-ocupacionais", "ergonomia", "esocial-sst", "treinamentos", "pca-ppr"]
BY_SLUG = {s["slug"]: s for s in SERVICES}

FAQ_ITEMS = [
    ("Toda empresa precisa de PGR?", "A aplicação e as dispensas previstas na NR-1 dependem do enquadramento e das condições da organização. A avaliação deve considerar o caso concreto."),
    ("O PCMSO substitui o PGR?", "Não. São instrumentos com finalidades distintas e articulação técnica. O PCMSO é elaborado sob responsabilidade médica conforme NR-7."),
    ("LTCAT é a mesma coisa que laudo de insalubridade?", "Não. Embora possam envolver avaliação de agentes, possuem finalidades e critérios próprios, especialmente em matéria previdenciária e trabalhista."),
    ("Como são feitas as avaliações ambientais ocupacionais?", "A estratégia e os métodos são definidos conforme o agente e a exposição, utilizando referências técnicas pertinentes, como as NHO da Fundacentro e normas aplicáveis."),
    ("A TCEG realiza AEP e AET?", "Essas avaliações integram as soluções apresentadas. A necessidade e a abrangência de cada uma dependem da análise das situações de trabalho."),
    ("A empresa pode contratar somente um documento?", "Sim, é possível solicitar uma proposta pontual ou discutir um acompanhamento mais amplo, observando a necessidade técnica de cada serviço."),
    ("Como funciona a gestão de eSocial SST?", "A equipe avalia o escopo documental e operacional contratado, alinhando as responsabilidades com as obrigações e leiautes oficiais aplicáveis."),
    ("A TCEG atende a Baixada Santista e a capital paulista?", "O atendimento divulgado contempla a Baixada Santista e São Paulo. Outras localidades ou modalidades podem ser analisadas na proposta."),
    ("O orçamento é automático?", "Não. O formulário reúne informações para que a TCEG analise a demanda e entre em contato. O envio não representa contratação."),
    ("Posso informar exames e dados de saúde de funcionários no site?", "Não. Os formulários comerciais não devem receber diagnósticos, exames médicos nem dados sensíveis de trabalhadores."),
]


# ----------------------------------------------------------------------------
# Páginas
# ----------------------------------------------------------------------------
def build_home():
    body = (ROOT / "tools/partials/home.html").read_text(encoding="utf-8")
    org = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": "TCEG – Gestão Estratégica e Conformidade Técnica", "url": SITE + "/",
        "logo": SITE + "/assets/logo-wordmark.svg", "email": EMAIL,
        "areaServed": ["Baixada Santista", "São Paulo"], "description": ORG_DESC,
    }
    write("index.html", page(
        title="TCEG | Segurança do Trabalho, Medicina Ocupacional e Gestão de SST",
        desc=ORG_DESC, path="", body=body, home=True, jsonld=[org], rail=True, body_class="home"))


def build_service(s):
    others = "".join(
        f'<li><a href="{o["slug"]}.html"><span>{o["title"]}</span>{{{{i:arrow}}}}</a></li>'
        for o in (BY_SLUG[k] for k in SERVICES_ORDER) if o["slug"] != s["slug"])
    crumbs = breadcrumbs([("Início", "index.html"), ("Serviços", "servicos.html"), (s["title"], None)])
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Serviços", "item": SITE + "/servicos.html"},
        {"@type": "ListItem", "position": 3, "name": s["title"], "item": f'{SITE}/{s["slug"]}.html'}]}
    body = f"""<main id="conteudo">
{phero(s['tag'], s['title'] + '.', s['lede'], crumbs)}
<section class="spec" aria-labelledby="spec-title">
  <div class="container spec__grid">
    <div class="spec__intro">
      <p class="kicker">O que compreende</p>
      <h2 id="spec-title">Soluções alinhadas à sua operação.</h2>
      <p class="lede">{s['summary']}</p>
    </div>
    <div class="spec__blocks">
      <div class="spec__block"><h3>Referências normativas</h3><p>{s['ref']}</p></div>
      <div class="spec__block"><h3>Critérios de execução</h3><p>{s['crit']}</p></div>
      <div class="spec__block"><h3>{s['h3']}</h3><p>{s['body']}</p></div>
    </div>
  </div>
</section>
<section class="offer" aria-labelledby="offer-title">
  <div class="container">
    <div class="offer__card">
      <p class="kicker">Atendimento TCEG</p>
      <h3 id="offer-title">Solicite uma avaliação do escopo</h3>
      <p>Informe empresa, localidade, segmento e o serviço de interesse. Nossa equipe avaliará a necessidade antes de apresentar condições comerciais.</p>
      {btn('Solicitar proposta', 'diagnostico.html', 'primary', extra=' data-magnet')}
      <p class="form-note">Não envie laudos médicos nem dados sensíveis de trabalhadores.</p>
    </div>
  </div>
</section>
<section class="others" aria-labelledby="others-title">
  <div class="container">
    <h2 id="others-title">Outras soluções TCEG</h2>
    <ul class="others__list">{others}</ul>
  </div>
</section>
<section class="endcta" aria-labelledby="end-title">
  <div class="container endcta__inner">
    <h2 id="end-title">Precisa de {s['short']}?</h2>
    <p>Apresente a necessidade da sua empresa e receba um retorno comercial após análise do escopo.</p>
    {btn('Solicitar proposta para minha empresa', 'diagnostico.html', 'dark')}
  </div>
</section>
</main>"""
    write(f"{s['slug']}.html", page(title=f"{s['title']} | TCEG", desc=s["meta"], path=f"{s['slug']}.html",
                                    body=body, jsonld=[ld]))


def build_servicos():
    cards = ""
    for k in SERVICES_ORDER:
        s = BY_SLUG[k]
        cards += f"""<a class="svc" href="{k}.html" data-spotlight>
        <p class="svc__tag">Serviço especializado</p>
        <h3>{s['card_title']}</h3>
        <p>{s['card_desc']}</p>
        <span class="link-arrow"><span>Conhecer solução</span>{{{{i:arrow}}}}</span>
      </a>
      """
    body = f"""<main id="conteudo">
{phero('Soluções corporativas', 'Segurança do Trabalho com visão de gestão.', 'Conheça os serviços da TCEG e solicite uma proposta conforme a realidade da sua empresa. Atendimento na Baixada Santista e em São Paulo.')}
<section class="svc-list" aria-labelledby="areas-title">
  <div class="container">
    <h2 id="areas-title">Áreas de atuação</h2>
    <div class="svc-grid">
      {cards}</div>
    <p class="page-note">Os serviços dependem do escopo contratado, da avaliação das necessidades e da atuação de profissionais habilitados.</p>
  </div>
</section>
<section class="closing" aria-labelledby="closing-title">
  <div class="container closing__inner">
    <h2 id="closing-title">Vamos entender sua necessidade?</h2>
    <p>Solicite uma proposta sem compromisso de contratação automática.</p>
    {btn('Solicitar proposta', 'diagnostico.html', 'primary', extra=' data-magnet')}
  </div>
</section>
</main>"""
    write("servicos.html", page(
        title="Serviços de SST e conformidade técnica | TCEG",
        desc="Conheça as soluções TCEG: PGR, PCMSO, LTCAT, avaliações ocupacionais, ergonomia, eSocial SST, treinamentos e programas preventivos.",
        path="servicos.html", body=body))


def build_cases():
    body = f"""<main id="conteudo">
{phero('Nossa atuação', 'Da necessidade operacional à solução técnica.', 'Entenda como organizamos o trabalho. Os cenários abaixo são ilustrativos, não representam contratos ou resultados comprovados.')}
<section class="stages" aria-labelledby="etapas-title">
  <div class="container">
    <h2 id="etapas-title">Etapas da abordagem</h2>
    <ol class="stages__list">
      <li><h3>Entender</h3><p>Reunimos informações sobre operação, locais, atividades e documentos existentes.</p></li>
      <li><h3>Planejar</h3><p>Definimos escopo, referências aplicáveis, responsáveis e entregas.</p></li>
      <li><h3>Acompanhar</h3><p>Apoiamos a organização e revisão das ações acordadas no contrato.</p></li>
    </ol>
  </div>
</section>
<section class="scenarios" aria-labelledby="cenarios-title">
  <div class="container">
    <h2 id="cenarios-title">Cenários ilustrativos</h2>
    <p class="scenarios__lead">Exemplos de necessidades comuns para diferentes segmentos — não são relatos de clientes ou indicadores de desempenho.</p>
    <div class="scenarios__grid">
      <article class="scenario"><p class="scenario__tag">Exemplo ilustrativo de escopo</p><h3>Indústria e manutenção</h3><p>Levantamento de exposições ocupacionais, avaliação de agentes físicos e químicos e integração documental com a operação.</p></article>
      <article class="scenario"><p class="scenario__tag">Exemplo ilustrativo de escopo</p><h3>Construção civil e obras</h3><p>Estruturação de gestão de riscos por etapa da obra, atividades críticas, treinamentos e suporte a documentação de terceiros.</p></article>
      <article class="scenario"><p class="scenario__tag">Exemplo ilustrativo de escopo</p><h3>Comércio, logística e serviços</h3><p>Organização de documentos de SST, avaliações ergonômicas, exames ocupacionais e rotinas de atualização.</p></article>
    </div>
    <p class="page-note">Cases reais, depoimentos e logotipos de clientes poderão ser incorporados mediante autorização e validação das informações.</p>
  </div>
</section>
<section class="closing" aria-labelledby="closing-title">
  <div class="container closing__inner">
    <h2 id="closing-title">Cada operação requer um escopo próprio.</h2>
    <p>Apresente sua necessidade para análise da TCEG.</p>
    {btn('Solicitar proposta', 'diagnostico.html', 'primary', extra=' data-magnet')}
  </div>
</section>
</main>"""
    write("cases.html", page(
        title="Abordagem técnica e cenários de atuação | TCEG",
        desc="Veja como a TCEG estrutura soluções para indústria, construção civil, logística e serviços. Exemplos ilustrativos sem identificação de clientes.",
        path="cases.html", body=body))


def build_faq():
    items = ""
    for i, (q, a) in enumerate(FAQ_ITEMS, 1):
        items += f"""<div class="acc__item">
        <h2 class="visually-hidden-h"><button class="acc__q" id="fq{i}" aria-expanded="false" aria-controls="fa{i}" type="button"><span>{q}</span><span class="acc__plus" aria-hidden="true"></span></button></h2>
        <div class="acc__a" id="fa{i}" role="region" aria-labelledby="fq{i}"><div><p>{a}</p></div></div>
      </div>
      """
    body = f"""<main id="conteudo">
{phero('Central de orientação', 'Respostas para decidir melhor.', 'Perguntas frequentes sobre serviços, documentos e gestão de SST. Orientações gerais que não substituem avaliação técnica do caso concreto.')}
<section class="faq-page" aria-label="Perguntas frequentes">
  <div class="container faq-page__inner">
    <div class="acc">
      {items}</div>
    <div class="faq-page__foot">
      <p>Conteúdo informativo, sujeito à legislação e aos critérios vigentes.</p>
      {btn('Falar sobre minha empresa', 'diagnostico.html', 'dark')}
    </div>
  </div>
</section>
</main>"""
    # as perguntas são títulos (h2) neste contexto; estilo neutro para o título
    body = body.replace('class="visually-hidden-h"', 'style="margin:0;font-size:inherit;letter-spacing:inherit;line-height:inherit"')
    write("faq.html", page(
        title="Perguntas frequentes sobre SST e serviços TCEG | TCEG",
        desc="Respostas às dúvidas de empresários e profissionais de RH sobre PGR, PCMSO, LTCAT, ergonomia, eSocial e contratação de serviços de SST.",
        path="faq.html", body=body))


SELECT_SEG = "".join(f"<option>{o}</option>" for o in ["Indústria", "Construção civil", "Comércio", "Serviços", "Saúde", "Transporte e logística", "Outro"])
SELECT_TRAB = "".join(f"<option>{o}</option>" for o in ["Sem empregados", "1 a 9", "10 a 49", "50 a 99", "100 a 499", "500 ou mais"])
WIZ_SERVICES = [
    "PGR – Programa de Gerenciamento de Riscos",
    "PCMSO – Programa de Controle Médico de Saúde Ocupacional",
    "LTCAT – Laudo Técnico das Condições Ambientais do Trabalho",
    "Laudos de Insalubridade e Periculosidade",
    "Avaliações ambientais e ocupacionais (NHO e normas aplicáveis)",
    "AEP e AET – Ergonomia",
    "Gestão eSocial SST",
    "Exames ocupacionais",
    "Treinamentos das Normas Regulamentadoras",
    "PCA e PPR – Programas preventivos",
    "Planos de emergência e resgate",
    "Gestão de SST e documentação de terceiros",
    "Consultoria e auditoria técnica em SST",
    "Outros serviços / orientação técnica",
]


def build_diagnostico():
    checks = "".join(f'<label><input name="servicos" type="checkbox" value="{s}"><span>{s}</span></label>' for s in WIZ_SERVICES)
    body = f"""<main id="conteudo" class="wiz">
  <div class="container wiz__grid">
    <div>
      <a class="wiz__back" href="index.html#ferramentas">{{{{i:arrow}}}}<span>Voltar ao site</span></a>
      <p class="kicker">Atendimento corporativo · TCEG</p>
      <h1>Solicitação inteligente de proposta.</h1>
      <p class="wiz__intro">Conte sobre sua empresa e selecione os serviços de interesse. Nossa equipe analisará a demanda e entrará em contato para alinhar o escopo.</p>
      <p class="wiz__intro">Se não conseguir utilizar o formulário, solicite atendimento diretamente pelo <a href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">WhatsApp da TCEG</a> ou pelo e-mail <a href="mailto:{EMAIL}">{EMAIL}</a>. Não envie dados médicos ou informações sensíveis de trabalhadores.</p>

      <ol class="wiz__markers" aria-label="Etapas">
        <li class="wizard-indicator is-active"><b>01</b> Empresa</li>
        <li class="wizard-indicator"><b>02</b> Proposta</li>
        <li class="wizard-indicator"><b>03</b> Revisão</li>
      </ol>
      <p class="wiz__step-text" id="unified-step-text">Etapa 1 de 3 · Identificação</p>

      <div class="wiz__panel">
        <form id="unified-form" name="proposta-tceg" method="POST" action="/obrigado" accept-charset="UTF-8" data-netlify="true" netlify-honeypot="bot-field" data-tceg-form novalidate aria-label="Solicitação de proposta">
          <input id="unified-replyto" name="email_resposta" type="hidden">
          <input name="form-name" type="hidden" value="proposta-tceg">
          <input class="honeypot" name="bot-field" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">
          <input id="unified-services-input" name="servicos_solicitados" type="hidden">
          <input name="origem" type="hidden" value="Solicitação comercial TCEG V12.1">

          <section class="unified-step" data-step="0" aria-labelledby="step-title-0">
            <span class="tool-eyebrow">01 / 03 · Identificação</span>
            <h2 id="step-title-0" tabindex="-1">Conte-nos sobre sua empresa.</h2>
            <p class="tool-help">Preencha os dados para receber um atendimento alinhado à sua realidade.</p>
            <div class="tool-fields">
              <label class="field">Razão social ou nome fantasia *<input name="empresa" autocomplete="organization" maxlength="120" placeholder="Nome da empresa" required></label>
              <label class="field"><span>CNPJ <span class="optional">(opcional)</span></span><input name="cnpj" autocapitalize="characters" spellcheck="false" maxlength="18" placeholder="00.000.000/0000-00 ou alfanumérico"></label>
              <label class="field">Nome do responsável *<input name="responsavel" autocomplete="name" maxlength="100" placeholder="Seu nome" required></label>
              <label class="field">Cargo ou função<input name="cargo" maxlength="80" placeholder="Ex.: RH, direção, SESMT"></label>
              <label class="field">E-mail corporativo *<input name="email" type="email" autocomplete="email" maxlength="130" placeholder="contato@empresa.com.br" required></label>
              <label class="field">Telefone / WhatsApp *<input name="telefone" type="tel" autocomplete="tel" maxlength="25" placeholder="(13) 99999-9999" required></label>
              <label class="field">Cidade / UF *<input name="cidade" maxlength="90" placeholder="Ex.: Santos/SP" required></label>
              <label class="field">Segmento de atuação *<select name="segmento" required><option value="">Selecione</option>{SELECT_SEG}</select></label>
              <label class="field">Quantidade aproximada de trabalhadores *<select name="trabalhadores" required><option value="">Selecione</option>{SELECT_TRAB}</select></label>
              <label class="field">Unidades / estabelecimentos<input name="unidades" type="number" min="1" max="9999" step="1" placeholder="Ex.: 2"></label>
            </div>
          </section>

          <section class="unified-step" data-step="1" aria-labelledby="step-title-1" hidden>
            <span class="tool-eyebrow">02 / 03 · Soluções</span>
            <h2 id="step-title-1" tabindex="-1">Qual é a sua necessidade?</h2>
            <p class="tool-help">Selecione um ou mais serviços. Se ainda não souber exatamente o que contratar, descreva sua necessidade para avaliarmos o escopo com você.</p>
            <fieldset class="services-fieldset">
              <legend>Serviços de interesse (opcional)</legend>
              <div class="service-checkboxes" id="unified-services">{checks}</div>
            </fieldset>
            <div class="tool-fields">
              <label class="field span-2">Descreva a sua demanda<textarea name="necessidade" maxlength="1800" placeholder="Ex.: elaboração de documentos, avaliações ocupacionais, atendimento de unidades, treinamentos. Não inclua dados médicos de funcionários."></textarea></label>
              <label class="field">Prazo desejado<select name="prazo"><option>Sem prazo definido</option><option>Urgente</option><option>Até 15 dias</option><option>Até 30 dias</option><option>Acima de 30 dias</option></select></label>
              <label class="field">Modalidade<select name="modalidade"><option>A definir com a TCEG</option><option>Atendimento presencial</option><option>Atendimento remoto</option><option>Ambos</option></select></label>
              <label class="field"><span>Como conheceu a TCEG? <span class="optional">(opcional)</span></span><select name="origem_contato"><option value="">Selecione</option><option>Pesquisa no Google</option><option>Instagram / redes sociais</option><option>Indicação</option><option>Contato comercial</option><option>Outro</option></select></label>
            </div>
          </section>

          <section class="unified-step" data-step="2" aria-labelledby="step-title-2" hidden>
            <span class="tool-eyebrow">03 / 03 · Revisão</span>
            <h2 id="step-title-2" tabindex="-1">Confira sua solicitação.</h2>
            <p class="tool-help">Revise as informações antes do envio à equipe da TCEG.</p>
            <div class="review-company" id="unified-company"></div>
            <div class="review-services" id="unified-selected-services"></div>
            <div class="review-company" id="unified-details"></div>
            <label class="tool-consent"><input name="consentimento" type="checkbox" required><span>Autorizo a utilização dos dados fornecidos para responder à minha solicitação e entrar em contato, conforme a <a href="privacidade.html" target="_blank" rel="noopener noreferrer">Política de Privacidade</a>. *</span></label>
            <p class="tool-fine">Não inclua dados de saúde, resultados de exames ou informações pessoais de trabalhadores neste formulário.</p>
          </section>

          <div class="form-step-actions">
            <button class="btn btn--outline" id="unified-back" type="button" hidden><span class="btn__label">← Voltar</span></button>
            <button class="btn btn--primary" id="unified-next" type="button"><span class="btn__label">Continuar</span>{{{{ico}}}}</button>
            <button class="btn btn--primary" id="unified-send" type="submit" hidden data-label="Enviar solicitação de proposta"><span class="btn__label">Enviar solicitação de proposta</span>{{{{ico}}}}</button>
          </div>
          <p id="unified-feedback" role="status" aria-live="polite" tabindex="-1"></p>
        </form>
      </div>
    </div>

    <aside class="wiz__aside cut" aria-labelledby="aside-title">
      <p class="kicker">Atendimento consultivo</p>
      <h2 id="aside-title">Sua demanda, nosso compromisso.</h2>
      <ol>
        <li>01. Identificação: entendemos o porte, o segmento e a localização da empresa.</li>
        <li>02. Proposta: você seleciona os serviços e descreve a necessidade.</li>
        <li>03. Retorno: nossa equipe avalia as informações e entra em contato para definir os próximos passos.</li>
      </ol>
      <p class="fine">O preenchimento não gera contratação ou orçamento automático. Os serviços dependem de definição e validação de escopo.</p>
      <a class="link-arrow" href="mailto:{EMAIL}"><span>Dúvidas? {EMAIL}</span>{{{{i:arrow}}}}</a>
    </aside>
  </div>
</main>"""
    write("diagnostico.html", page(
        title="Solicitação inteligente de proposta | TCEG",
        desc="Solicite uma proposta personalizada de Segurança e Saúde no Trabalho com um formulário simples e seguro.",
        path="diagnostico.html", body=body))


def build_privacidade():
    secs = [
        ("Dados fornecidos", "O contato solicita nome, empresa, e-mail, telefone, serviço de interesse, mensagem e autorização de contato. A proposta também permite informar CNPJ, cargo, cidade/UF, segmento, quantidade aproximada de trabalhadores e unidades, serviços pretendidos, demanda, prazo, modalidade e como conheceu a TCEG. Alguns campos são opcionais. São registrados ainda a origem do formulário e os dados técnicos necessários ao processamento e à prevenção de spam."),
        ("Finalidades e necessidade", "Os dados são utilizados para analisar a demanda, responder ao contato, preparar propostas e acompanhar a solicitação. Forneça apenas informações necessárias ao atendimento. Não envie dados de saúde, exames, prontuários ou informações pessoais de trabalhadores."),
        ("Processamento e fornecedores", "Os formulários são processados pelo Netlify Forms e disponibilizados no painel administrativo do projeto. Notificações por e-mail dependem da configuração do administrador. A hospedagem processa informações técnicas para disponibilizar o site e prevenir abusos. O carregamento das fontes Google Fonts envolve conexão com servidores do Google. Os links de WhatsApp e Instagram direcionam a serviços com políticas próprias; seu uso é opcional."),
        ("Proteção e conservação", "O tratamento deve observar finalidade, necessidade, transparência e segurança. O acesso às solicitações deve ficar restrito às pessoas autorizadas para o atendimento. Os dados devem ser conservados pelo período necessário à finalidade do contato e às obrigações aplicáveis, com revisão de necessidade e descarte quando cabível."),
    ]
    out = "".join(f"<h2>{h}</h2>\n      <p>{p}</p>\n      " for h, p in secs)
    body = f"""<main id="conteudo" class="prose-page">
  <div class="container">
    <a class="wiz__back" href="index.html">{{{{i:arrow}}}}<span>Voltar ao site</span></a>
    <div class="prose">
      <h1>Privacidade e dados pessoais</h1>
      <p>Esta política descreve o uso dos dados enviados pelos formulários de contato e solicitação de proposta da TCEG – Gestão Estratégica e Conformidade Técnica.</p>
      {out}<h2>Seus direitos e contato</h2>
      <p>Você pode solicitar informações sobre o tratamento, confirmação de existência, acesso, correção e, quando aplicável, eliminação, revisão de consentimento e informações sobre compartilhamento. Para exercer seus direitos ou esclarecer dúvidas, escreva para <a href="mailto:{EMAIL}">{EMAIL}</a>. A identificação do solicitante poderá ser verificada para proteger seus dados.</p>
      <h2>Transparência institucional</h2>
      <p>A identificação cadastral completa da pessoa jurídica, endereço institucional, definição formal do responsável pelo tratamento, critérios específicos de retenção e detalhes de eventual transferência internacional ainda dependem de confirmação institucional. Nenhum dado cadastral não confirmado é apresentado nesta página. O canal disponível para questões de privacidade é {EMAIL}.</p>
      <p class="updated">Atualização desta política: 14 de novembro de 2026.</p>
    </div>
  </div>
</main>"""
    write("privacidade.html", page(
        title="Privacidade | TCEG",
        desc="Saiba como são utilizados os dados dos formulários de contato e proposta da TCEG e como solicitar informações sobre privacidade.",
        path="privacidade.html", body=body))


def build_obrigado():
    body = f"""<main id="conteudo" class="center-page">
  {MARK.replace('phero__mark', 'phero__mark')}
  <div class="container center-page__inner">
    <span class="tick">{{{{i:check}}}}</span>
    <p class="kicker">TCEG · Atendimento corporativo</p>
    <h1>Solicitação enviada com sucesso!</h1>
    <p>Agradecemos pelo contato. Sua solicitação foi registrada para processamento. Nossa equipe poderá retornar pelos contatos informados após análise do pedido.</p>
    <p>Se precisar complementar a solicitação, escreva para <a href="mailto:{EMAIL}">{EMAIL}</a>. Não envie dados médicos ou informações sensíveis de trabalhadores.</p>
    <div class="center-page__actions">
      {btn('Voltar à página inicial', 'index.html', 'primary')}
      <a class="btn btn--light" href="index.html#solucoes"><span class="btn__label">Conhecer nossas soluções</span></a>
    </div>
  </div>
</main>"""
    write("obrigado.html", page(
        title="Solicitação recebida | TCEG", desc="Sua solicitação foi registrada pela equipe da TCEG.",
        path="obrigado.html", body=body, robots="noindex,follow"))


def build_404():
    body = f"""<main id="conteudo" class="center-page">
  {MARK}
  <div class="container center-page__inner">
    <p class="kicker">Erro 404</p>
    <h1>Página não encontrada.</h1>
    <p>O endereço que você acessou não existe ou foi movido. Volte ao início ou conheça as soluções da TCEG.</p>
    <div class="center-page__actions">
      {btn('Voltar à página inicial', 'index.html', 'primary')}
      <a class="btn btn--light" href="servicos.html"><span class="btn__label">Ver todos os serviços</span></a>
    </div>
  </div>
</main>"""
    write("404.html", page(
        title="Página não encontrada | TCEG", desc="A página solicitada não foi encontrada no site da TCEG.",
        path="404.html", body=body, robots="noindex,follow"))


def build_support_files():
    urls = [""] + [f"{n}.html" for n in ["servicos", "cases", "faq", "diagnostico", "privacidade"] + SERVICES_ORDER]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE}/{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    pretty = ["servicos", "cases", "faq", "diagnostico", "privacidade", "obrigado"] + SERVICES_ORDER
    redirects = "# URLs amigáveis (compatíveis com o site anterior). Netlify: status 200 = reescrita.\n"
    redirects += "".join(f"/{n}  /{n}.html  200\n" for n in pretty)
    (ROOT / "_redirects").write_text(redirects, encoding="utf-8")
    (ROOT / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n\n"
        "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n", encoding="utf-8")
    print("  ✓ sitemap.xml, robots.txt, _redirects, _headers")


if __name__ == "__main__":
    print("Gerando páginas…")
    build_home()
    for s in SERVICES:
        build_service(s)
    build_servicos()
    build_cases()
    build_faq()
    build_diagnostico()
    build_privacidade()
    build_obrigado()
    build_404()
    build_support_files()
    print("Concluído.")
