// Every mechanism diagram on /architecture must link back to its article.
//
// That is the whole reason they sit on that page: the generated drawing
// says what the lab IS, and each of these says why one piece of it works
// the way it does — which is a story that lives in an article. A diagram
// with no way back to it is a dead end.
//
// Two of the eleven had drifted before this check existed, for two
// different reasons: one named its article in prose without linking it,
// and one took its caption from a <slot> the architecture page never
// filled. Both were invisible until someone scrolled past them.
//
// Run against the built site: `node scripts/check-diagram-links.mjs dist`.
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2] ?? "dist";
const page = join(root, "architecture", "index.html");

let html;
try {
  html = readFileSync(page, "utf8");
} catch {
  console.log("check-diagram-links: no /architecture page in this build");
  process.exit(0);
}

const sections = html.split('<section class="detail"').slice(1);
if (sections.length === 0) {
  console.error("check-diagram-links: no detail diagrams found — did the page change?");
  process.exit(1);
}

let missing = 0;
for (const section of sections) {
  const body = section.split("</section>")[0];
  const title = (body.match(/<h2[^>]*>(.*?)<\/h2>/s)?.[1] ?? "?")
    .replace(/<[^>]+>/g, "")
    .trim();
  if (!/href="\/(?:en\/)?blog\//.test(body)) {
    console.error(`  no article link: ${title}`);
    missing++;
  }
}

if (missing) {
  console.error(
    `\ncheck-diagram-links: ${missing} of ${sections.length} diagrams have no ` +
      `link to their article. Give the component a default caption for ` +
      `context="architecture" that links it.`,
  );
  process.exit(1);
}
console.log(`check-diagram-links: all ${sections.length} diagrams link their article`);
