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

export type Link = Record<string, unknown>;
/** `links` belongs to the turn that produced it, never to the conversation.
 *  It was stored once, alongside the transcript, and a refresh therefore lost
 *  the links of every reply but the last — the earlier ones had nowhere to
 *  live. Only assistant turns carry it, and it never reaches the Worker: see
 *  toMessages(). */
export type Turn = { role: "user" | "assistant"; content: string; links?: Link[] };

/**
 * Six exchanges. The Worker caps at the same number, so a longer array here
 * would only be trimmed on arrival — and every turn is prompt you pay for.
 *
 * Raised from three on 2026-09-11, and the ceiling is arithmetic rather than
 * taste. The model runs at `num_ctx` 16384. The grounding is ~7300 tokens and
 * the retrieved excerpts up to ~2300, the answer reserves 500, which leaves
 * ~6300 for the transcript. A worst-case exchange is ~690 tokens — a question
 * capped at 500 characters plus a 500-token answer — so six exchanges fit with
 * room to spare and eight would not.
 *
 * Overflow is worth avoiding rather than surviving: when the prompt exceeds the
 * window it is the START that gets dropped, and the start is the grounding. Bob
 * would not fail, he would quietly begin improvising — the one thing he is
 * built not to do.
 */
export const MAX_TURNS = 12;

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
    .map((m) => ({
      role: m.role,
      content: m.content,
      // Dropped rather than trusted when it is not an array: the renderer
      // validates each href anyway, but a malformed value has no business
      // travelling this far.
      ...(Array.isArray(m.links) ? { links: m.links } : {}),
    }))
    .slice(-MAX_TURNS);
}

/** The wire format the Worker expects — role and content, nothing else.
 *  Stripping in one shared place rather than at each call site: there are two
 *  of them, and the one that forgot would send link objects into a prompt. */
export function toMessages(turns: Turn[]): { role: string; content: string }[] {
  return turns.map(({ role, content }) => ({ role, content }));
}

export function loadConversation(): { turns: Turn[] } {
  try {
    const raw = sessionStorage.getItem(KEY) ?? sessionStorage.getItem(LEGACY_KEY);
    if (!raw) return { turns: [] };
    const parsed = JSON.parse(raw);
    // The legacy shape was a single pair in two named fields.
    let turns = parsed?.turns
      ? sanitize(parsed.turns)
      : sanitize([
          { role: "user", content: parsed?.question },
          { role: "assistant", content: parsed?.reply },
        ]);
    // Older writes — and the legacy handoff — kept ONE links array for the
    // whole conversation, meaning the last reply's. Give it back to the last
    // assistant turn rather than dropping it, so a tab that stored the old
    // shape still shows its links after this ships.
    if (Array.isArray(parsed?.links) && parsed.links.length && !turns.some((t) => t.links)) {
      for (let i = turns.length - 1; i >= 0; i--) {
        if (turns[i].role === "assistant") {
          turns[i] = { ...turns[i], links: parsed.links };
          break;
        }
      }
    }
    return { turns };
  } catch {
    return { turns: [] };
  }
}

export function saveConversation(turns: Turn[]): void {
  try {
    sessionStorage.removeItem(LEGACY_KEY);
    sessionStorage.setItem(KEY, JSON.stringify({ turns: turns.slice(-MAX_TURNS) }));
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
