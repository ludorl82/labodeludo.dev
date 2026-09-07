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
 * A link says what it leads to before you click it.
 *
 * Bob cites articles and recordings in the same breath and the URL is the only
 * thing telling them apart — which asks a reader to parse a path mid-sentence.
 * The glyph carries it instead: a play triangle for something you watch, stacked
 * rules for something you read. Both are plain characters in the monospace face
 * the whole site already loads, so there is no icon font and nothing to fetch.
 *
 * U+25B8 rather than U+25B6 on purpose: the larger triangle has an emoji
 * presentation and turns into a colour glyph on iOS and Android.
 */
const KIND = {
  cast: { icon: "\u25B8", fr: "enregistrement", en: "recording" },
  article: { icon: "\u2261", fr: "article", en: "article" },
} as const;

/**
 * One anchor, built the same way for the two places links appear: inline where
 * Bob wrote the slug, and in the chip row for the ones he named without writing
 * out. Same shape both times, so a link looks like a link wherever it lands.
 *
 * The visible text is the title, not the path. Bob writes
 * `/blog/deplacer-mes-partages-nfs-sur-un-ssd-sans-toucher-a-kubernetes/` and a
 * reader should not have to decode that. The href still comes from the Worker
 * untouched — this changes what the link *reads* as, never where it goes.
 */
function makeLink(l: BobLink, lang: "fr" | "en"): HTMLAnchorElement {
  const k = KIND[l.kind === "cast" ? "cast" : "article"];
  const a = document.createElement("a");
  a.href = l.href;
  a.className = "bob-link";
  a.dataset.kind = l.kind === "cast" ? "cast" : "article";
  // The glyph is decoration; a screen reader gets the word instead, so "article"
  // and "enregistrement" are announced rather than "black right-pointing small
  // triangle".
  a.setAttribute("aria-label", `${k[lang]} : ${l.title}`);
  const ico = document.createElement("span");
  ico.className = "bob-link-ico";
  ico.setAttribute("aria-hidden", "true");
  ico.textContent = k.icon;
  a.append(ico, document.createTextNode(l.title));
  return a;
}

/**
 * Fill `target` with `text`, turning any slug the Worker validated into an
 * anchor. Links named but not written verbatim are appended as a chip row
 * after `target`, so they are still reachable.
 */
export function renderReply(
  target: HTMLElement,
  text: string,
  links: BobLink[] | undefined,
  lang: "fr" | "en" = "fr",
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
      target.append(makeLink(l, lang));
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
    for (const l of leftover) row.append(makeLink(l, lang));
    target.after(row);
  }
}
