// Render Bob's voice into the nightly prompts from the one canonical file.
//
// The "## Bob's voice" section of arch-diagram.md and rack-diagram.md used to
// be two hand-maintained copies of the same paragraph, and they drifted from
// the chat persona, the skill and the author bio without anyone noticing.
// Now the section is a rendered block between two markers, generated from
// src/data/bob-persona.md (sections Noyau + Scribe). `--check` fails the build
// when a prompt no longer matches the file, so the only way to change Bob's
// voice in the nightly job is to change the file.
import { readFileSync, writeFileSync } from "node:fs";

const CHECK = process.argv.includes("--check");
const PERSONA = "src/data/bob-persona.md";
const PROMPTS = [
  "scripts/topology/prompts/arch-diagram.md",
  "scripts/topology/prompts/rack-diagram.md",
];
const BEGIN = /<!-- bob-persona:begin[^>]*-->\n/;
const END = "<!-- bob-persona:end -->\n";

function section(md, name) {
  const m = md.split(/^## /m).slice(1).find((p) => p.startsWith(`${name}\n`));
  if (!m) throw new Error(`${PERSONA}: section "## ${name}" not found`);
  return m.slice(name.length + 1).trim();
}

const md = readFileSync(PERSONA, "utf8");
const block =
  `Rendered from ${PERSONA}. The prompt is in English; Bob's voice is\n` +
  `described in French, which is the language you write him in.\n\n` +
  section(md, "Noyau") + "\n\n" + section(md, "Scribe") + "\n";

let drift = 0;
for (const file of PROMPTS) {
  const text = readFileSync(file, "utf8");
  const b = text.match(BEGIN);
  const e = text.indexOf(END);
  if (!b || e < 0) throw new Error(`${file}: bob-persona markers missing`);
  const start = b.index + b[0].length;
  const rendered = text.slice(0, start) + block + text.slice(e);
  if (rendered !== text) {
    drift++;
    if (CHECK) console.error(`${file}: Bob's voice differs from ${PERSONA}; run node scripts/render-bob-prompts.mjs`);
    else { writeFileSync(file, rendered); console.log(`rendered ${file}`); }
  }
}
if (CHECK && drift) process.exit(1);
if (!drift) console.log("bob prompts up to date");
