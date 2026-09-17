// The voice assistant's system prompt, assembled from the one persona file.
//
// Home Assistant keeps this prompt in its own storage, where it was edited by
// hand until 2026-09-17 and said "Tu es Assist" while the wake word said
// "Ok Bob". Now: the first paragraph of "## Voix" in src/data/bob-persona.md
// is who Bob is when he speaks, voice-rules.txt is how the assistant must
// behave (tools, Jinja for the weather, spoken-answer formatting), and this
// script is the only thing that joins them. `apply-voice-prompt.sh` pushes
// the result and `--check` reports drift against what is live.
import { readFileSync } from "node:fs";

const md = readFileSync("src/data/bob-persona.md", "utf8");
const voix = md.split(/^## /m).slice(1).find((p) => p.startsWith("Voix\n"));
if (!voix) throw new Error("bob-persona.md: section Voix missing");
const persona = voix.slice("Voix\n".length).trim().split("\n\n")[0].trim();
if (!persona.startsWith("Tu es Bob")) throw new Error("Voix: first paragraph must be the spoken identity line");
const rules = readFileSync("scripts/voice/voice-rules.txt", "utf8").replace(/\s+$/, "");
process.stdout.write(`/no_think\n${persona}\n\n${rules}\n`);
