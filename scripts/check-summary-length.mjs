// Keep the « Résumé technique » short.
//
// The summary at the top of an article is for readers in a hurry. It had
// grown into a second article: a median of 250 words and 6 bullets in
// Ludo's posts, 285 words and 9 bullets in Bob's, 556 words at worst.
// Ludo set the ceiling on 2026-10-12: 5 bullets, 120 words.
//
// A summary is the blockquote that starts with `> **Résumé technique**`
// (or `> **Technical summary**`) and runs until the first line that is not
// a quote. Bullets are its `> -` lines. Words are counted on the text a
// reader sees: markdown marks, link targets and lone punctuation don't
// count, link text does.
//
// Run on the sources: `node scripts/check-summary-length.mjs`.
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

export const MAX_BULLETS = 5;
export const MAX_WORDS = 120;

const DIRS = ["src/content/blog", "src/content/blog-en"];
const HEAD = /^> \*\*(Résumé technique|Technical summary)\*\*.*$/m;

export function measure(source) {
  const m = HEAD.exec(source);
  if (!m) return null;
  const lines = [];
  for (const line of source.slice(m.index + m[0].length + 1).split("\n")) {
    if (!line.startsWith(">")) break;
    lines.push(line);
  }
  const bullets = lines.filter((l) => /^> -/.test(l)).length;
  const text = lines
    .join("\n")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[>*_`]/g, " ");
  // A token with no letter or digit is punctuation, not a word: French puts
  // a space before « : » and « ; », and those were counted.
  const words = text.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length;
  return { bullets, words };
}

let bad = 0;
let seen = 0;
for (const dir of DIRS) {
  for (const entry of readdirSync(dir).filter((e) => /\.mdx?$/.test(e))) {
    const r = measure(readFileSync(join(dir, entry), "utf8"));
    if (!r) continue;
    seen++;
    if (r.bullets > MAX_BULLETS || r.words > MAX_WORDS) {
      bad++;
      console.error(
        `check-summary-length: ${dir}/${entry}: ${r.bullets} puces, ${r.words} mots ` +
          `(au plus ${MAX_BULLETS} puces, ${MAX_WORDS} mots)`,
      );
    }
  }
}
if (bad) {
  console.error(`check-summary-length: ${bad} résumé(s) trop long(s) sur ${seen}`);
  process.exit(1);
}
console.log(`check-summary-length: ${seen} résumés, tous sous ${MAX_BULLETS} puces et ${MAX_WORDS} mots`);
