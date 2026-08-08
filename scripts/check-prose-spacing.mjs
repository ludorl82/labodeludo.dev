// Catch the whitespace Astro eats.
//
// When a line of prose ends with a word and the NEXT line starts with an
// inline tag, the newline between them is dropped rather than collapsed to
// a space — so `documentation\n<code>2001:db8…` renders as
// "documentation2001:db8…". It is invisible in the source, obvious on the
// page, and it shipped twice before this check existed.
//
// Run against the built site: `node scripts/check-prose-spacing.mjs dist`.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2] ?? "dist";
// Only the opening-tag direction, and only tags that carry prose. The
// reverse (`</span>Mot`) is normal here: decorative empty spans sit right
// against label text all over the site, and flagging those buried the real
// hits 235-to-0 the first time this ran.
const INLINE = "em|strong|a|code|abbr";
const GLUED = new RegExp(`[a-zà-ÿ,)]<(?:${INLINE})[ >]`, "gi");

function* htmlFiles(dir) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) yield* htmlFiles(p);
    else if (entry.endsWith(".html")) yield p;
  }
}

let bad = 0;
for (const file of htmlFiles(root)) {
  const html = readFileSync(file, "utf8")
    // <pre> holds deliberate terminal transcripts; SVG text has its own
    // spacing rules and no inline flow
    .replace(/<pre[\s\S]*?<\/pre>/g, "")
    .replace(/<svg[\s\S]*?<\/svg>/g, "");
  for (const m of html.matchAll(GLUED)) {
    // Footnote markers are deliberately glued: `Dockerfile[2](url)` renders
    // as `Dockerfile<a …>2</a>`, a citation superscript, not a lost space.
    const tail = html.slice(m.index, m.index + 600);
    if (/^.<a\b[^>]*>\s*\d+\s*<\/a>/.test(tail)) continue;
    const around = html.slice(Math.max(0, m.index - 45), m.index + 25);
    console.error(`${file}: ${around.replace(/\s+/g, " ")}`);
    bad++;
  }
}

if (bad) {
  console.error(`\ncheck-prose-spacing: ${bad} glued spot(s) — a newline ` +
    `before an inline tag is not a space. Keep the tag on its word's line.`);
  process.exit(1);
}
console.log("check-prose-spacing: no glued prose");
