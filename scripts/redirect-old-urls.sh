#!/usr/bin/env bash
#
# Idempotent: creates S3 redirect objects at the old WordPress URLs
# (category-prefixed) so they 301 to the new Astro /blog/<slug>/ paths.
#
# `aws s3 sync --delete` in the deploy workflow wipes these on every prod
# deploy since they aren't part of dist/ — this script runs automatically
# as the step right after the sync (see .github/workflows/deploy.yml) to
# recreate them every time. Requires AWS credentials in the environment
# (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY), same as the sync step.
#
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

BUCKET="labodeludo.dev"
EMPTY_FILE="$(mktemp)"
trap 'rm -f "$EMPTY_FILE"' EXIT

# old-path (no leading/trailing slash) -> new slug
declare -A REDIRECTS=(
  ["cloud/automatiser-le-deploiement-de-son-reducteur-durl-avec-terraform"]="automatiser-le-deploiement-de-son-reducteur-durl-avec-terraform"
  ["cloud/creer-son-reducteur-durl-sur-aws"]="creer-son-reducteur-durl-sur-aws"
  ["cloud/decommissionner-un-serveur-dns-maison-de-ca-a-lair-simple-a-on-a-casse-sa-propre-resolution-dns"]="decommissionner-un-serveur-dns-maison-de-ca-a-lair-simple-a-on-a-casse-sa-propre-resolution-dns"
  ["cloud/deployer-sa-table-a-dessiner"]="deployer-sa-table-a-dessiner"
  ["cloud/deployer-un-site-web-statique-avec-wordpress-et-s3"]="deployer-un-site-web-statique-avec-wordpress-et-s3"
  ["cloud/ftp-prive-wireguard"]="ftp-prive-wireguard"
  ["cloud/gartner-confirme-le-leadership-daws-pour-2021"]="gartner-confirme-le-leadership-daws-pour-2021"
  ["cloud/retirer-pare-feu-tunnel-cloudflare"]="retirer-pare-feu-tunnel-cloudflare"
  ["devops/compartimentalisation-des-outils-de-console"]="compartimentalisation-des-outils-de-console"
  ["devops/construire-un-vrai-reseau-dalarme-pour-son-homelab-et-toutes-les-manieres-dont-ca-peut-foirer-en-silence"]="construire-un-vrai-reseau-dalarme-pour-son-homelab-et-toutes-les-manieres-dont-ca-peut-foirer-en-silence"
  ["devops/integration-de-plugins-asynchrones-avec-neovim"]="integration-de-plugins-asynchrones-avec-neovim"
  ["labo/le-move-qui-echouait-une-histoire-de-proxy-de-schema-http-et-dun-coffre-fort-presque-corrompu"]="le-move-qui-echouait-une-histoire-de-proxy-de-schema-http-et-dun-coffre-fort-presque-corrompu"
  ["labo/taper-a-la-vitesse-de-la-pensee"]="taper-a-la-vitesse-de-la-pensee"
  ["maison/ce-que-peut-faire-un-llm-local-sur-une-carte-a-300-mon-assistant-vocal-maison-avec-qwen3"]="ce-que-peut-faire-un-llm-local-sur-une-carte-a-300-mon-assistant-vocal-maison-avec-qwen3"
  ["maison/convention-ipv6-vlan-serveurs"]="convention-ipv6-vlan-serveurs"
  # page removed outright in the Astro site; send stray links home rather than 404
  ["politique-de-confidentialite"]=""
)

for old in "${!REDIRECTS[@]}"; do
  slug="${REDIRECTS[$old]}"
  target="/blog/${slug}/"
  if [ -z "$slug" ]; then
    target="/"
  fi
  echo "==> ${old}/  ->  ${target}"
  aws s3api put-object \
    --bucket "$BUCKET" \
    --key "${old}/index.html" \
    --website-redirect-location "$target" \
    --content-type "text/html; charset=UTF-8" \
    --body "$EMPTY_FILE"
done

echo "==> Done."
