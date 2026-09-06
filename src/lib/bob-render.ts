/**
 * Rendering Bob's answers safely. Shared by the chat widget and the command
 * palette — one implementation rather than two that drift.
 *
 * Two rules are load-bearing and neither is negotiable:
 *
 * 1. **DOM nodes, never innerHTML.** This is model output. Assembling markup
 *    from it is how you get an injection. Nothing here can produce an element
 *    the code did not explicitly create.
 * 2. **Never derive an href.** Every link comes from the Worker, which checked
 *    the slug against the real corpus first. A slug Bob invented stays plain
 *    text rather than becoming a clickable 404 — the site's whole asset is
 *    honesty, and a confident dead link spends it.
 *
 * Note what validation does *not* cover: a real slug cited for the wrong
 * article still renders as a working link. Observed during the 2026-09-06
 * bake-off, where a weaker model answered a BIOS question by citing a genuine
 * bastion-console slug. Validation catches dead links, not wrong ones.
 */

export interface BobLink {
  slug: string;
  title: string;
  href: string;
  kind?: string;
}

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/**
 * Fill `target` with `text`, turning any slug the Worker validated into an
 * anchor. Links named but not written verbatim are appended as a chip row
 * after `target`, so they are still reachable.
 */
export function renderReply(
  target: HTMLElement,
  text: string,
  links: BobLink[] | undefined,
): void {
  target.textContent = "";
  if (!links || !links.length) {
    target.textContent = text;
    return;
  }

  // First wins, and the Worker sends articles before casts: when a slug exists
  // as both, the inline link goes to the article and the cast twin falls
  // through to a chip below rather than hijacking the text.
  const bySlug = new Map<string, BobLink>();
  for (const l of links) if (!bySlug.has(l.slug)) bySlug.set(l.slug, l);

  // Longest first so one slug that prefixes another cannot win the match.
  const alts = links
    .map((l) => escapeRe(l.slug))
    .sort((a, b) => b.length - a.length)
    .join("|");
  const re = new RegExp(`(?:/(?:blog|casts)/)?(${alts})/?`, "g");

  const used = new Set<string>(); // hrefs rendered inline
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) target.append(document.createTextNode(text.slice(last, m.index)));
    const l = bySlug.get(m[1]);
    if (l) {
      const a = document.createElement("a");
      a.href = l.href;
      a.textContent = m[0];
      target.append(a);
      used.add(l.href);
    } else {
      target.append(document.createTextNode(m[0]));
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) target.append(document.createTextNode(text.slice(last)));

  const leftover = links.filter((l) => !used.has(l.href));
  if (leftover.length) {
    const row = document.createElement("div");
    row.className = "links";
    for (const l of leftover) {
      const a = document.createElement("a");
      a.href = l.href;
      a.textContent = l.title;
      row.append(a);
    }
    target.after(row);
  }
}
