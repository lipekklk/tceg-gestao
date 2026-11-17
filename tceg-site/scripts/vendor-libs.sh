#!/usr/bin/env bash
# Baixa GSAP, ScrollTrigger e Lenis para assets/js/vendor/ e troca as tags
# <script> dos CDNs por arquivos locais em todos os .html da raiz.
# Uso (na raiz do projeto):  bash scripts/vendor-libs.sh
set -euo pipefail

cd "$(dirname "$0")/.."
VENDOR="assets/js/vendor"
mkdir -p "$VENDOR"

GSAP_V="3.12.5"
LENIS_V="1.1.20"
CDN="https://cdn.jsdelivr.net/npm"

curl -fsSL "$CDN/gsap@$GSAP_V/dist/gsap.min.js"          -o "$VENDOR/gsap.min.js"
curl -fsSL "$CDN/gsap@$GSAP_V/dist/ScrollTrigger.min.js" -o "$VENDOR/ScrollTrigger.min.js"
curl -fsSL "$CDN/lenis@$LENIS_V/dist/lenis.min.js"       -o "$VENDOR/lenis.min.js"

for f in *.html; do
  sed -i \
    -e "s#$CDN/gsap@$GSAP_V/dist/gsap.min.js#$VENDOR/gsap.min.js#g" \
    -e "s#$CDN/gsap@$GSAP_V/dist/ScrollTrigger.min.js#$VENDOR/ScrollTrigger.min.js#g" \
    -e "s#$CDN/lenis@$LENIS_V/dist/lenis.min.js#$VENDOR/lenis.min.js#g" \
    "$f"
done

# Mantém tools/build.py coerente, para que uma nova geração não volte ao CDN.
if [ -f tools/build.py ]; then
  sed -i \
    -e "s#$CDN/gsap@$GSAP_V/dist/gsap.min.js#$VENDOR/gsap.min.js#g" \
    -e "s#$CDN/gsap@$GSAP_V/dist/ScrollTrigger.min.js#$VENDOR/ScrollTrigger.min.js#g" \
    -e "s#$CDN/lenis@$LENIS_V/dist/lenis.min.js#$VENDOR/lenis.min.js#g" \
    tools/build.py
fi

echo "Bibliotecas salvas em $VENDOR e referências atualizadas."
