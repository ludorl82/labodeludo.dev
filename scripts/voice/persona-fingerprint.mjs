// Prints the fingerprint of the persona the chat runs on, computed from the
// file. It is the same hash as personaFingerprint() in src/lib/bob-persona.ts,
// over the same text (the "## Chat" section, trimmed): that one is published
// in /bob-grounding.json by the build, this one is what a drift check reads
// from the checkout. The two agreeing means the persona that is live is the
// persona that is written. Kept as a script rather than importing the module
// because the module reads the file through Vite's ?raw import, which only
// exists inside an Astro build.
import { readFileSync } from "node:fs";

const md = readFileSync("src/data/bob-persona.md", "utf8");
const chat = md.split(/^## /m).slice(1).find((p) => p.startsWith("Chat\n"));
if (!chat) throw new Error("bob-persona.md: section Chat missing");
const text = chat.slice("Chat\n".length).trim();
let h = 0;
for (const c of text) h = (h * 31 + c.charCodeAt(0)) >>> 0;
process.stdout.write(h.toString(16).padStart(8, "0") + "\n");
