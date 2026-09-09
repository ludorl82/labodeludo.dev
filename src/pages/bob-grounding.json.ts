import type { APIRoute } from "astro";
import { getCollection } from "astro:content";
import fleet from "../data/fleet.json";
import { BOB_LOCAL_INTROS } from "../lib/bob-humor";
import architecture from "../data/architecture.json";
import dispatch from "../data/dispatch.json";
import { SITE_SELF } from "../data/site-self";
import { INVENTORY, type InventoryKey } from "../lib/inventory";
import { AUTHORS } from "../lib/author";

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

/**
 * Measured, not guessed: a 16,491-char prompt of this exact shape reported
 * 6,212 cached tokens from Bedrock on 2026-09-03, so French here runs about
 * 2.65 chars/token. The first guess of 3.2 undercounted by 17%. Re-derive this
 * from a real cache_read_input_tokens if the prompt's shape changes a lot —
 * device lines and pipe-delimited index rows tokenize worse than prose.
 */
const CHARS_PER_TOKEN = 2.65;

/**
 * Claude Haiku 4.5 will not cache a prefix under 4096 tokens, and it fails
 * silently — no error, just a bill that never drops.
 *
 * The floor is applied to the grounding ALONE, even though the Worker prepends
 * a persona that makes the real prefix bigger. Budgeting for the persona would
 * couple this assertion to the size of a string in another repo, so an edit
 * there could make this check quietly start lying. Treating the persona as
 * unearned margin keeps the check true on its own terms.
 *
 * This is still an estimate. The authoritative check is
 * cache_read_input_tokens > 0 against staging.
 */
const MIN_GROUNDING_TOKENS = 4096;

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

  // Counts, computed rather than left for the model to derive.
  //
  // Asked "combien de nœuds ?", every model tested guessed — Haiku said 37 of
  // 38 devices and invented a node list, two local models disagreed with both.
  // None of them was being stupid: nothing in fleet.json marks cluster
  // membership, so they were inferring it from French role prose. The cluster
  // edges in architecture.json say it exactly, so state it and stop asking a
  // language model to count.
  const k3sNodes = architecture.edges
    .filter((e: { kind: string; to: string }) => e.kind === "member-of" && e.to === "cluster:k3s")
    .map((e: { from: string }) => e.from.replace(/^host:/, ""))
    .sort();

  const byClass = new Map<string, number>();
  for (const d of fleet.devices as { class: string }[]) {
    byClass.set(d.class, (byClass.get(d.class) ?? 0) + 1);
  }
  const classCounts = [...byClass]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([k, n]) => `${k} ${n}`)
    .join(", ");

  const summary = [
    `Appareils au parc : ${fleet.devices.length}`,
    k3sNodes.length
      ? `Nœuds du cluster k3s : ${k3sNodes.length} — ${k3sNodes.join(", ")}`
      : `Nœuds du cluster k3s : inconnu (architecture.json sans arêtes member-of)`,
    `Par classe : ${classCounts}`,
    `Publications : ${(await getCollection("blog")).length} articles, ${(await getCollection("casts")).length} casts`,
  ].join("\n");

  const [posts, casts, postsEn, castsEn] = await Promise.all([
    getCollection("blog"),
    getCollection("casts"),
    getCollection("blogEn"),
    getCollection("castsEn"),
  ]);

  // FR and EN pair by identical id, so a set of ids is all that is needed to
  // know whether an English twin exists. Bob writes those translations, so when
  // he answers in English he should point at /en/blog/<slug>/ rather than
  // sending an English speaker to the French original.
  const twins = new Set([
    ...postsEn.map((e) => `article:${e.id}`),
    ...castsEn.map((e) => `cast:${e.id}`),
  ]);

  const entry = (kind: string) => (e: { id: string; data: Record<string, any> }) =>
    [
      kind,
      e.id, // there is no slug field in the schema — the id IS the slug
      e.data.pubDate.toISOString().slice(0, 10),
      (e.data.tags ?? []).join(","),
      oneLine(e.data.title),
      oneLine(e.data.description ?? "").slice(0, DESCRIPTION_CHARS),
      twins.has(`${kind}:${e.id}`) ? "en" : "",
    ].join("|");

  const corpus = [
    ...[...posts]
      .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
      .map(entry("article")),
    ...[...casts]
      .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
      .map(entry("cast")),
  ];

  // Every page of the site that is NOT a publication, so Bob can point at one.
  //
  // He had the article index and nothing else, so the only link he could ever
  // offer was /blog/<slug>/ — asked "c'est quoi ton architecture ?" the best he
  // could do was describe it, with /architecture/ sitting right there. Anything
  // he cited that was not a slug was dropped by the Worker's link check, which
  // is the correct behaviour for an unverified path and a bad answer to a fair
  // question.
  //
  // Derived, never hand-listed: the roles come from INVENTORY, the authors from
  // AUTHORS, the standalone pages from the `pages` collection. A route added
  // without touching this file still shows up; a role deleted stops being
  // offered. The only literals are the index routes, which are fixed files in
  // src/pages and change about once a year.
  const pagesCollection = await getCollection("pages");
  const siteMap: [string, string][] = [
    // No "/" entry on purpose. The home page adds nothing Bob can say that the
    // article index does not, and as a link target it is a hazard: the widget
    // linkifies inline by building one regex out of every slug, and a bare "/"
    // matches every slash in the reply — including the ones inside real paths.
    ["/architecture/", "Le schéma de l'architecture, redessiné chaque semaine à partir des dépôts"],
    ["/inventaire/", "L'inventaire : ce que chaque rôle du labo fait, et les articles écrits dessus"],
    ["/casts/", "Les enregistrements de terminal"],
    ["/auteurs/", "Qui écrit ici"],
    ["/en/", "English home — the translated half of the site"],
    ["/en/casts/", "Terminal recordings, English index"],
    ...(Object.keys(INVENTORY) as InventoryKey[]).map(
      (k) => [`/inventaire/${k}/`, `Rôle : ${INVENTORY[k].name}`] as [string, string],
    ),
    ...Object.entries(AUTHORS).map(
      ([id, a]) => [`/auteurs/${id}/`, `${a.name} — ${a.tagline}`] as [string, string],
    ),
    ...pagesCollection.map(
      (p) => [`/${p.id}/`, oneLine(p.data.title)] as [string, string],
    ),
  ];
  const pagesText = siteMap.map(([path, title]) => `${path}|${title}`).join("\n");

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
    corpusFields: "kind|slug|date|tags|title|description|en",
    // The non-publication pages, same idea: the Worker names the field order
    // in the prompt and verifies every path Bob cites against this list.
    pagesFields: "path|title",
    pages: pagesText,
    summary,
    // How this site is built. Not derivable from the fleet — those are the
    // machines in the basement, and the blog is a static artifact on someone
    // else's edge — so without it the most-asked question had nothing behind
    // it but improvisation. See src/data/site-self.ts.
    site: SITE_SELF,
    // Voice for the Worker's local-fallback mode. Lives in bob-humor.ts with
    // the other pools and rides along here so it is editable without a tofu
    // apply in cloudflare-iac.
    localIntros: BOB_LOCAL_INTROS,
    // What moved in the fleet last night, in one line, written by the nightly
    // job and gated before it lands (scripts/topology/check-dispatch.py holds
    // it to a computed diff, so it cannot name a machine that did not change).
    // Empty on a quiet night, which is most nights — the Worker omits the
    // section entirely rather than telling Bob that nothing happened, because
    // "nothing happened" is not something he should volunteer.
    dispatch: dispatch.dispatch || undefined,
    dispatchGenerated: dispatch.generated || undefined,
    fleet: fleetText,
    corpus: corpusText,
  };

  return new Response(JSON.stringify(payload), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
