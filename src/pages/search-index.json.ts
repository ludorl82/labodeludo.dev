import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const prerender = true;

/**
 * The command palette's corpus: everything navigable, in both languages.
 *
 * A deliberate sibling of `bob-grounding.json` rather than an extension of it.
 * That file is French-only, spends a fifth of its bytes on a fleet block no
 * palette needs, and is load-bearing for prompt caching — a minimum-token
 * assertion guards it and its chars-per-token constant was measured against a
 * real Bedrock cache read. Adding a language column there would invalidate the
 * Worker's cached prefix to serve an unrelated feature.
 *
 * Fetched by the palette on first open, never inlined: inlining ~11 KB into
 * every one of ~90 built pages costs every visitor, while fetching costs only
 * the ones who actually open it.
 */

/** Enough to recognise an entry in a result row; not enough to read it here. */
const DESCRIPTION_CHARS = 120;

const oneLine = (s: string) => s.replace(/\s+/g, " ").trim();

type Entry = {
  kind: "article" | "cast";
  lang: "fr" | "en";
  slug: string;
  title: string;
  desc: string;
  date: string;
  tags: string[];
  href: string;
};

export const GET: APIRoute = async () => {
  const [posts, postsEn, casts, castsEn] = await Promise.all([
    getCollection("blog"),
    getCollection("blogEn"),
    getCollection("casts"),
    getCollection("castsEn"),
  ]);

  const map = (
    entries: { id: string; data: Record<string, any> }[],
    kind: Entry["kind"],
    lang: Entry["lang"],
    base: string,
  ): Entry[] =>
    entries.map((e) => ({
      kind,
      lang,
      // There is no slug field in any collection schema — the entry id, which
      // comes from the filename, IS the slug. FR and EN pair by identical id,
      // which is what lets the palette offer a translation with no extra data.
      slug: e.id,
      title: oneLine(e.data.title),
      desc: oneLine(e.data.description ?? "").slice(0, DESCRIPTION_CHARS),
      date: e.data.pubDate.toISOString().slice(0, 10),
      // Casts have no tags in their schema; articles carry category chips plus
      // the author marker (ludo/bob), which are worth matching on.
      tags: e.data.tags ?? [],
      href: `${base}/${e.id}/`,
    }));

  const entries = [
    ...map(posts, "article", "fr", "/blog"),
    ...map(postsEn, "article", "en", "/en/blog"),
    ...map(casts, "cast", "fr", "/casts"),
    ...map(castsEn, "cast", "en", "/en/casts"),
  ].sort((a, b) => b.date.localeCompare(a.date));

  return new Response(
    JSON.stringify({
      schema: 1,
      generated: new Date().toISOString(),
      counts: {
        fr: entries.filter((e) => e.lang === "fr").length,
        en: entries.filter((e) => e.lang === "en").length,
      },
      entries,
    }),
    {
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        // Content-addressed by deploy, not by URL, so let the edge hold it but
        // make a browser revalidate rather than pin a stale corpus for a day.
        "Cache-Control": "public, max-age=300, must-revalidate",
      },
    },
  );
};
