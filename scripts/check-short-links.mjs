#!/usr/bin/env node
//
// Checks the short links in dist/liens-courts.json, which the `lbdl` Worker
// (cloudflare-iac) reads to serve lbdl.dev/<code> and lbdl.dev/cast/<code>.
//
// Fails the build on a code used twice: the Worker would silently keep one
// of the two targets. labodeludo.dev itself serves no short link, so a code
// may share its name with a page of the site.
//
import { existsSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SOURCE = join(ROOT, "dist", "liens-courts.json");

if (!existsSync(SOURCE)) {
  console.error(`check-short-links: expected ${SOURCE} to exist after the build`);
  process.exit(1);
}

const { links } = JSON.parse(readFileSync(SOURCE, "utf8"));
const errors = [];
const seen = new Map();
for (const { code, target } of links) {
  if (seen.has(code)) errors.push(`« ${code} » sert deux fois : ${seen.get(code)} et ${target}`);
  seen.set(code, target);
}
if (errors.length) {
  for (const e of errors) console.error(`check-short-links: ${e}`);
  process.exit(1);
}
console.log(`check-short-links: ${links.length} lien(s) court(s), servis par lbdl.dev`);
