#!/usr/bin/env node
//
// Copies dist/en/404/index.html to dist/en/404.html so the English section
// keeps its own 404 page on Cloudflare Pages.
//
// Pages resolves a custom 404 by walking up the directory tree from the
// requested path looking for the nearest 404.html, ending at /404.html. Astro's
// directory build format flattens only the top-level 404 route to /404.html and
// emits the English one as /en/404/index.html, which that walk never matches —
// so without this file every /en/* miss would serve the French page. The k3s
// nginx staging container did the same job with an `error_page 404
// /en/404/index.html` block in a location /en/ { } stanza; this replaces it.
//
// Harmless for the prod S3 deploy, which has a single error-document setting
// and ignores the extra file.
//
import { copyFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SOURCE = join(ROOT, "dist/en/404/index.html");
const TARGET = join(ROOT, "dist/en/404.html");

// Fail loudly rather than silently shipping a build whose English 404s fall
// through to the French page.
if (!existsSync(SOURCE)) {
  console.error(`emit-nested-404: expected ${SOURCE} to exist after the build`);
  process.exit(1);
}

copyFileSync(SOURCE, TARGET);
console.log("emit-nested-404: wrote dist/en/404.html");
