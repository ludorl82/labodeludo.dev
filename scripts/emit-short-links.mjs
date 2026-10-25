#!/usr/bin/env node
//
// Checks the short links in dist/liens-courts.json (articles at /<code>,
// casts at /cast/<code>) and writes them to
// dist/_redirects, which Cloudflare Pages (staging) serves as 301s. Prod is
// S3 and ignores the file; scripts/redirect-short-links.sh reads the same
// JSON there.
//
// Fails the build on a code used twice, or on a code that is already a path
// of the site (labodeludo.dev/casts must stay the casts page): the redirect
// object would shadow it on S3, and Pages would serve the page and silently
// drop the redirect.
//
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const DIST = join(ROOT, "dist");
const SOURCE = join(DIST, "liens-courts.json");

if (!existsSync(SOURCE)) {
  console.error(`emit-short-links: expected ${SOURCE} to exist after the build`);
  process.exit(1);
}

const { links } = JSON.parse(readFileSync(SOURCE, "utf8"));
const errors = [];
const seen = new Map();
for (const { code, target } of links) {
  if (seen.has(code)) errors.push(`« ${code} » sert deux fois : ${seen.get(code)} et ${target}`);
  seen.set(code, target);
  // The S3 keys are <code> and <code>/index.html; either one existing in the
  // build means the code is a real path.
  if (existsSync(join(DIST, code)) || existsSync(join(DIST, `${code}.html`))) {
    errors.push(`« ${code} » est déjà une page du site (dist/${code})`);
  }
}
if (errors.length) {
  for (const e of errors) console.error(`emit-short-links: ${e}`);
  process.exit(1);
}

const lines = links.flatMap(({ code, target }) => [
  `/${code} ${target} 301`,
  `/${code}/ ${target} 301`,
]);
writeFileSync(join(DIST, "_redirects"), lines.join("\n") + "\n");
console.log(`emit-short-links: ${links.length} lien(s) court(s) dans dist/_redirects`);
