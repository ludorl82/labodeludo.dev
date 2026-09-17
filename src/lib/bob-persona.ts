/**
 * Bob's persona, read from ONE file and served in pieces.
 *
 * `src/data/bob-persona.md` is the canonical description of the character.
 * Nothing else is allowed to describe him: the grounding endpoint publishes
 * the sections the chat needs, the nightly prompts are rendered from it, and
 * the register check reads its banned list. This module is the only parser,
 * so a section heading typo fails the build here rather than silently
 * shipping an empty persona.
 */
import raw from "../data/bob-persona.md?raw";

export type PersonaSection =
  | "Noyau"
  | "Interdits"
  | "Chat"
  | "Voix"
  | "Articles"
  | "Scribe"
  | "Boutades";

const REQUIRED: PersonaSection[] = [
  "Noyau",
  "Interdits",
  "Chat",
  "Voix",
  "Articles",
  "Scribe",
  "Boutades",
];

function parse(md: string): Record<PersonaSection, string> {
  const out = {} as Record<PersonaSection, string>;
  const parts = md.split(/^## /m).slice(1);
  for (const part of parts) {
    const nl = part.indexOf("\n");
    const name = part.slice(0, nl).trim() as PersonaSection;
    out[name] = part.slice(nl + 1).trim();
  }
  for (const name of REQUIRED) {
    if (!out[name]) {
      throw new Error(`bob-persona.md: section "## ${name}" is missing or empty`);
    }
  }
  return out;
}

export const PERSONA = parse(raw);

/** The banned strings, one per "- " line of the Interdits section. */
export const BOB_BANNED: string[] = PERSONA.Interdits.split("\n")
  .filter((l) => /^- /.test(l))
  .map((l) => l.replace(/^-\s*/, "").trim())
  .filter(Boolean);

/** What the chat Worker prepends to its system message: the Chat section
 *  alone, verbatim. NOT the Noyau on top of it, and that is a budget decision,
 *  not an oversight: the Worker's num_ctx is 16384 and its worst case was
 *  measured at 15,324 tokens on 2026-09-12, 560 of headroom. The Noyau is
 *  ~600 tokens; prepending it would push the oldest turns out of the window
 *  without any warning. The Chat section already states who Bob is in its
 *  first lines, so the chat loses nothing. The Worker keeps its own copy as a
 *  fallback for a grounding published before this field existed. */
export const PERSONA_CHAT = PERSONA.Chat;

/** A short fingerprint so a drift check can compare what runs to what is written. */
export function personaFingerprint(): string {
  let h = 0;
  for (const c of PERSONA_CHAT) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return h.toString(16).padStart(8, "0");
}
