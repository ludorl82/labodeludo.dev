// The register guard: nothing Bob signs may contain a banned string.
//
// The list lives in src/data/bob-persona.md under "## Interdits", one string
// per "- " line, matched case-insensitively. It covers the catchphrases that
// made the first Gratton attempt "distrayant" in July 2026 and the phonetic
// mockery banned from the English voice. Scanned: every article tagged `bob`
// (both languages), the quip pools, the nightly prompts and last night's
// dispatch. Runs in `npm run build`, so a regression fails the deploy rather
// than reaching a reader.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const md = readFileSync("src/data/bob-persona.md", "utf8");
const interdits = md.split(/^## /m).slice(1).find((p) => p.startsWith("Interdits\n"));
if (!interdits) throw new Error("bob-persona.md: section Interdits missing");
const banned = interdits
  .split("\n")
  .filter((l) => /^- /.test(l))
  .map((l) => l.replace(/^-\s*/, "").trim())
  .filter(Boolean);

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) yield* walk(p);
    else yield p;
  }
}

const targets = [];
for (const dir of ["src/content/blog", "src/content/blog-en"]) {
  for (const f of walk(dir)) {
    if (!/\.mdx?$/.test(f)) continue;
    const head = readFileSync(f, "utf8").slice(0, 2000);
    if (/^tags:.*"bob"/m.test(head)) targets.push(f);
  }
}
targets.push("src/lib/bob-humor.ts", "src/data/dispatch.json");
for (const f of walk("scripts/topology/prompts")) targets.push(f);

let bad = 0;
for (const f of targets) {
  const text = readFileSync(f, "utf8");
  const lower = text.toLowerCase();
  for (const b of banned) {
    const i = lower.indexOf(b.toLowerCase());
    if (i >= 0) {
      bad++;
      const line = text.slice(0, i).split("\n").length;
      console.error(`${f}:${line}: banned string ${JSON.stringify(b)}`);
    }
  }
}
if (bad) { console.error(`check-bob-register: ${bad} hit(s)`); process.exit(1); }
console.log(`check-bob-register: ${targets.length} files clean against ${banned.length} banned strings`);
