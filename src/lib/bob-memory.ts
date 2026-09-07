/**
 * The conversation, carried from page to page.
 *
 * Bob is reached from two places — the command palette, on every page, and the
 * widget on his author page — and until now each kept its own memory that died
 * on navigation. Ask a question from an article, click through to another one,
 * ask a follow-up: he had forgotten. That reads as a bug, because the box looks
 * the same box either side of a page load, and it is the same Bob.
 *
 * `sessionStorage`, not `localStorage`, and the choice is the whole design:
 *
 * - It is per tab, so two tabs are two conversations, which is what someone
 *   opening a second tab means.
 * - It dies when the tab does. A question someone typed is not something to
 *   keep on their machine for weeks, and nobody should have to find a "clear
 *   history" button to be rid of it.
 * - It never leaves the browser. The Worker keeps no memory of its own — the
 *   transcript is sent with each request and forgotten — so this file is the
 *   only place the conversation exists, and it is the visitor's own disk.
 *
 * Everything here tolerates storage being unavailable (private windows, or a
 * browser set to refuse it). The failure mode is exactly the old behaviour:
 * Bob answers, he just does not remember. That is worth degrading to silently;
 * it is not worth an error message.
 */

export type Turn = { role: "user" | "assistant"; content: string };
export type Link = Record<string, unknown>;

/** Three exchanges. The Worker caps at the same number, so a longer array here
 *  would only be trimmed on arrival — and every turn is prompt you pay for. */
export const MAX_TURNS = 6;

const KEY = "bob:conversation";
/** What the palette used to write for a one-time handoff. Read for as long as
 *  a tab loaded before this shipped might still be open; never written. */
const LEGACY_KEY = "bob:handoff";

/** Anything read back from storage is treated as hostile: it survives page
 *  loads, it is trivially editable from a console, and it ends up in a prompt.
 *  Shape is checked, not assumed. */
function sanitize(turns: unknown): Turn[] {
  if (!Array.isArray(turns)) return [];
  return turns
    .filter(
      (m): m is Turn =>
        !!m &&
        typeof m === "object" &&
        ((m as Turn).role === "user" || (m as Turn).role === "assistant") &&
        typeof (m as Turn).content === "string" &&
        !!(m as Turn).content.trim(),
    )
    .slice(-MAX_TURNS);
}

export function loadConversation(): { turns: Turn[]; links: Link[] } {
  try {
    const raw = sessionStorage.getItem(KEY) ?? sessionStorage.getItem(LEGACY_KEY);
    if (!raw) return { turns: [], links: [] };
    const parsed = JSON.parse(raw);
    // The legacy shape was a single pair in two named fields.
    const turns = parsed?.turns
      ? sanitize(parsed.turns)
      : sanitize([
          { role: "user", content: parsed?.question },
          { role: "assistant", content: parsed?.reply },
        ]);
    return { turns, links: Array.isArray(parsed?.links) ? parsed.links : [] };
  } catch {
    return { turns: [], links: [] };
  }
}

export function saveConversation(turns: Turn[], links: Link[] = []): void {
  try {
    sessionStorage.removeItem(LEGACY_KEY);
    sessionStorage.setItem(
      KEY,
      JSON.stringify({ turns: turns.slice(-MAX_TURNS), links }),
    );
  } catch {
    // Storage refused. The turn still happened; it just will not outlive the
    // page — which is where this feature started.
  }
}

export function clearConversation(): void {
  try {
    sessionStorage.removeItem(KEY);
    sessionStorage.removeItem(LEGACY_KEY);
  } catch {
    /* nothing to clear if nothing could be stored */
  }
}
