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

// `--telephone`: the phone line's agent (« Bob téléphone », since 2026-10-26),
// also the office Voice PE's since 2026-10-27 (Ludo wanted the lab there).
// Same Bob, except the voice persona's last sentences send lab questions to
// the site's Bob — on the phone he HAS the lab tools (labo-mcp), so from that
// sentence to the end of the paragraph becomes telephone.txt. Rendered from
// the same persona, the phone prompt follows every persona change; a copy
// made by hand once would have drifted with nothing to say so.
const LABO = "Le labo, le cluster, les articles";
let identity = persona;
if (process.argv.includes("--telephone")) {
  const at = persona.indexOf(LABO);
  if (at < 0) throw new Error(`Voix: "${LABO}…" missing, nothing to swap for the phone`);
  const tel = readFileSync("scripts/voice/telephone.txt", "utf8").trim();
  identity = `${persona.slice(0, at)}${tel}`;
}
// No `/no_think` first line since 2026-10-26: that was Qwen's switch, and Bob
// now runs on Claude Haiku 5.5 (Home Assistant's OpenRouter integration).
process.stdout.write(`${identity}\n\n${rules}\n`);
