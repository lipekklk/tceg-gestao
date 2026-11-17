# TCEG — site institucional (reconstrução)

Site estático multipágina em HTML5, CSS3 e JavaScript puro, com GSAP, ScrollTrigger e Lenis.
Sem frameworks e sem etapa de build obrigatória: abra e publique.

## Estrutura

```
index.html                 Home
servicos.html              Serviços em detalhe
pgr.html pcmso.html ltcat.html avaliacoes-ocupacionais.html
ergonomia.html esocial-sst.html treinamentos.html pca-ppr.html   Páginas de serviço
cases.html                 Nossa atuação
faq.html                   Perguntas frequentes
diagnostico.html           Solicitação de proposta (formulário em 3 etapas)
privacidade.html           Política de privacidade
obrigado.html  404.html    Confirmação de envio e página não encontrada
_redirects  _headers       Configuração do Netlify
sitemap.xml  robots.txt
assets/
  css/   tokens → base → components → home → pages
  js/    core, smooth-scroll, nav, accordion, forms, home
  js/effects/  split-text, dot-grid, interactions, scroll-reveal
  img/   logotipo e favicon
tools/
  build.py        Gera todos os .html a partir de modelos e dados
  partials/       Conteúdo da home
scripts/
  vendor-libs.sh  Baixa as bibliotecas para uso offline
```

## Rodar localmente

```bash
python3 -m http.server 8000
# abra http://localhost:8000
```

Abrir o `index.html` direto no navegador (file://) também funciona.

## Alterar conteúdo

Os `.html` são gerados. Edite `tools/build.py` (páginas internas, menu, rodapé) ou
`tools/partials/home.html` (home) e rode:

```bash
python3 tools/build.py
```

## Publicar (Netlify)

Envie a pasta inteira (arrastar para o painel ou conectar ao repositório). Não há comando de build:
publique a raiz do projeto.

- `_redirects` mantém URLs sem `.html` (ex.: `/servicos`).
- `_headers` define os cabeçalhos de segurança.
- Os formulários usam Netlify Forms (`data-netlify="true"`, campo isca `bot-field`).
  Ative a coleta e as notificações em *Site configuration → Forms* depois do primeiro deploy.

Antes de publicar, ajuste o domínio em `sitemap.xml` e `robots.txt` se for diferente do atual.

## Bibliotecas de animação

GSAP 3.12.5, ScrollTrigger e Lenis 1.1.20 são carregados por CDN (jsDelivr).
Para servir tudo do próprio site, rode `bash scripts/vendor-libs.sh`.

Se uma biblioteca não carregar ou o visitante preferir movimento reduzido
(`prefers-reduced-motion`), o site continua totalmente utilizável, sem animação.

## Efeitos (adaptados do React Bits para JS nativo)

| Efeito | Arquivo | Onde aparece |
| --- | --- | --- |
| SplitText | `effects/split-text.js` | Título do hero |
| DotGrid | `effects/dot-grid.js` | Fundo do hero |
| ScrollReveal | `effects/scroll-reveal.js` | Textos em destaque |
| SpotlightCard | `effects/interactions.js` | Cartões com `data-spotlight` |
| Magnet | `effects/interactions.js` | Botões com `data-magnet` |
| ScrollVelocity (faixa) | `effects/interactions.js` | Faixa em movimento |
| ScrollStack | `home.css` + `home.js` | Soluções |

## Formulários

`forms.js` valida os campos (e-mail, telefone brasileiro, CNPJ numérico ou alfanumérico) e envia por `fetch`.
Em `file://` e `localhost` o envio é simulado e leva a `obrigado.html`; o POST real só acontece no site publicado.

## Pontos para conferir

- Textos foram transcritos do site publicado; confira com o responsável antes de publicar.
- A imagem de compartilhamento (`og:image`) aponta para o site atual.
- O texto da página 404 é novo, pois o original não estava acessível.
- Nenhum depoimento, certificação, cliente ou número foi adicionado.
