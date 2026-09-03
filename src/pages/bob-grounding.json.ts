import type { APIRoute } from "astro";
import { getCollection } from "astro:content";
import fleet from "../data/fleet.json";

export const prerender = true;

/**
 * The grounding half of Bob's chat prompt, published as a static artifact.
 *
 * The Worker that answers /api/bob/chat lives in the cloudflare-iac repo and
 * holds Bob's PERSONA; it fetches this file at request time and concatenates
 * the two. The split is deliberate: the persona is stable and belongs with the
 * code that is reviewed and hashed, while this half changes every time an
 * article ships or the nightly job rewrites fleet.json. Baking it into the
 * Worker would mean a tofu apply in another repo every time a post goes out.
 *
 * Everything here is already public — fleet.json renders the rack diagram and
 * the corpus is the blog itself. Nothing new is exposed by serving it as JSON.
 */

/** French runs denser than English; ~3.2 chars/token is the working estimate. */
const CHARS_PER_TOKEN = 3.2;

/**
 * Claude Haiku 4.5 will not cache a prefix under 4096 tokens, and it fails
 * silently — no error, just a bill that never drops. The persona adds roughly
 * 700 tokens on top of what we emit here, so requiring 3600 of grounding keeps
 * the assembled prompt clear of the floor with margin. This is an estimate, not
 * a tokenizer: the authoritative check is cache_read_input_tokens > 0 against
 * staging. This assertion only catches the loud failure — someone trimming the
 * corpus until caching quietly stops paying for itself.
 */
const MIN_GROUNDING_TOKENS = 3600;

/** Description text is indexed to help Bob choose, not to be recited back. */
const DESCRIPTION_CHARS = 80;

const oneLine = (s: string) => s.replace(/\s+/g, " ").trim();

export const GET: APIRoute = async () => {
  // One line per device: durable fields, then the French role sentence. The
  // raw JSON is mostly punctuation — this is about a third the tokens.
  const devices = fleet.devices.map((d: Record<string, unknown>) => {
    const parts: string[] = [
      String(d.name),
      String(d.class),
      String(d.network),
    ];
    for (const k of ["location", "model", "spec", "hostedBy", "power", "count"]) {
      if (d[k] !== undefined) parts.push(`${k}=${d[k]}`);
    }
    parts.push(d.iacDeclared ? "iac" : "hors-iac");
    parts.push(oneLine(String(d.role)));
    return parts.join(" | ");
  });

  const [posts, casts] = await Promise.all([
    getCollection("blog"),
    getCollection("casts"),
  ]);

  const entry = (kind: string) => (e: { id: string; data: Record<string, any> }) =>
    [
      kind,
      e.id, // there is no slug field in the schema — the id IS the slug
      e.data.pubDate.toISOString().slice(0, 10),
      (e.data.tags ?? []).join(","),
      oneLine(e.data.title),
      oneLine(e.data.description ?? "").slice(0, DESCRIPTION_CHARS),
    ].join("|");

  const corpus = [
    ...[...posts]
      .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
      .map(entry("article")),
    ...[...casts]
      .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
      .map(entry("cast")),
  ];

  const fleetText = devices.join("\n");
  const corpusText = corpus.join("\n");
  const approxTokens = Math.round(
    (fleetText.length + corpusText.length) / CHARS_PER_TOKEN,
  );

  if (approxTokens < MIN_GROUNDING_TOKENS) {
    throw new Error(
      `bob-grounding: ${approxTokens} tokens is under the ${MIN_GROUNDING_TOKENS} ` +
        `needed to keep the cached prefix above Haiku's 4096-token floor. ` +
        `Caching would stop paying silently. See the comment in this file.`,
    );
  }

  const payload = {
    schema: 1,
    generated: new Date().toISOString(),
    fleetGenerated: fleet.generated,
    counts: { devices: devices.length, corpus: corpus.length },
    approxTokens,
    // Field order in each corpus line, so the Worker's prompt can name it.
    corpusFields: "kind|slug|date|tags|title|description",
    fleet: fleetText,
    corpus: corpusText,
  };

  return new Response(JSON.stringify(payload), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
