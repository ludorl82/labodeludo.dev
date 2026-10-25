#!/usr/bin/env bash
#
# Creates the S3 redirect objects for the short links (labodeludo.dev/<code>
# -> the article), from dist/liens-courts.json, which the build writes from
# each article's `court` field.
#
# Same reason as redirect-old-urls.sh for running after every sync: the
# objects are not in dist/, so `aws s3 sync --delete` removes them each time.
# Two keys per code: S3's website endpoint answers /<code> from the key
# <code> with a single 301, where <code>/index.html alone would first 302 to
# /<code>/. That second key covers the trailing-slash form.
#
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

BUCKET="labodeludo.dev"
LINKS="dist/liens-courts.json"
EMPTY_FILE="$(mktemp)"
trap 'rm -f "$EMPTY_FILE"' EXIT

node -e '
  const { links } = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
  for (const l of links) console.log(`${l.code}\t${l.target}`);
' "$LINKS" | while IFS=$'\t' read -r code target; do
  for key in "${code}" "${code}/index.html"; do
    echo "==> ${key}  ->  ${target}"
    aws s3api put-object \
      --bucket "$BUCKET" \
      --key "$key" \
      --website-redirect-location "$target" \
      --content-type "text/html; charset=UTF-8" \
      --body "$EMPTY_FILE" >/dev/null
  done
done

echo "==> Done."
