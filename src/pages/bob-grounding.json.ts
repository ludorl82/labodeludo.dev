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
 * A CEILING now, where there used to be a floor.
 *
 * The floor was Claude Haiku 4.5 refusing to cache a prefix under 4096 tokens,
 * silently. That tier was removed on 2026-09-07 and the check outlived it: it
 * was still defending a bill nobody pays, and it defended it by demanding the
 * prompt stay BIG — the exact opposite of what the live tier needs.
 *
 * What the live tier needs is room. qwen35-q4kl runs at num_ctx 16384 and the
 * Worker fills it from several sides at once: this grounding, the persona, up
 * to five retrieved excerpts (~2300 tokens), twelve turns of history, and 500
 * reserved for the answer. A worst case measured against the model itself on
 * 2026-09-12 came to 15,324 of 16,384 — 560 tokens of headroom, with no alarm
 * anywhere that would have said so. Past the ceiling the model does not warn
 * either; the oldest part of the window simply stops being read.
 *
 * Like the floor it replaces, it is applied to the fleet and the index ALONE.
 * Budgeting for the persona would couple this assertion to the size of a
 * string in another repo, where an edit could make this check quietly start
 * lying. The rest of the budget is treated as fixed and this is what is
 * allowed to grow.
 *
 * ~5500 estimated tokens is about 900 above what the trimmed index and fleet
 * measure today: roughly two thousand characters of room, a year of writing at
 * the current pace. When it fires, trim a column out of the index rather than
 * raising the number — raising it spends headroom that was measured, not
 * guessed.
 */
const MAX_GROUNDING_TOKENS = 5500;

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

  // NO description and NO tags, and that is a deletion, not an oversight.
  //
  // The truncated description cost 1,153 tokens of the Worker's prompt —
  // measured with prompt_eval_count, not estimated — to do the job semantic
  // search now does far better: retrieval reads the WHOLE article, this read
  // the first eighty characters of a summary. The tags cost another 302 and
  // they are coarse sections (Labo, DevOps, Domotique), not topics: nobody
  // ever found an article about Kubernetes through them.
  //
  // What is left is what retrieval CANNOT replace, because it is what the
  // index alone is still asked for: the exact slug (a path Bob must never
  // improvise), the date (the newest, the oldest, "what did you publish in
  // August"), the title, and whether an English twin exists. The titles here
  // are full sentences, so choosing from them is not a downgrade.
  const entry = (kind: string) => (e: { id: string; data: Record<string, any> }) =>
    [
      kind,
      e.id, // there is no slug field in the schema — the id IS the slug
      e.data.pubDate.toISOString().slice(0, 10),
      oneLine(e.data.title),
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
    // THE NAME FIRST, then " : " or " — ", then whatever describes it.
    //
    // That shape is not editorial taste, it is the contract with the widget:
    // bob-render.ts puts `title.split(/ : | — /)[0]` inside the link pill and
    // keeps the whole string for the tooltip. Written the other way round, the
    // titles here produced two visible bugs at once — "/architecture/" had no
    // separator at all, so Bob saying "le schéma se redessine tout seul à
    // /architecture/" rendered as "…tout seul à ·Le schéma de l'architecture,
    // redessiné chaque semaine à partir des dépôts", a sentence that stops
    // making sense mid-way; and all fourteen role pages started with "Rôle : ",
    // so every single one of them showed a pill labelled "Rôle".
    ["/architecture/", "Le schéma de l'architecture — redessiné chaque semaine à partir des dépôts"],
    ["/inventaire/", "L'inventaire : ce que chaque rôle du labo fait, et les articles écrits dessus"],
    ["/casts/", "Les enregistrements de terminal"],
    ["/auteurs/", "Qui écrit ici"],
    ["/en/", "English home — the translated half of the site"],
    ["/en/casts/", "Terminal recordings — English index"],
    ...(Object.keys(INVENTORY) as InventoryKey[]).map(
      (k) => [`/inventaire/${k}/`, `${INVENTORY[k].name} — rôle du labo`] as [string, string],
    ),
    ...Object.entries(AUTHORS).map(
      ([id, a]) => [`/auteurs/${id}/`, `${a.name} — ${a.tagline}`] as [string, string],
    ),
    ...pagesCollection.map(
      (p) => [`/${p.id}/`, oneLine(p.data.title)] as [string, string],
    ),
  ];
  // The pill label, computed exactly the way bob-render.ts computes it, and
  // asserted here because nothing else can see both sides. Two rules, one for
  // each way this already broke: SHORT, because the label goes inline in the
  // middle of Bob's sentence, and UNIQUE, because fourteen role pages once
  // shared the prefix "Rôle : " and every one of them rendered as "Rôle".
  const PILL_MAX = 40;
  const pill = (title: string) => title.split(/ : | — /)[0];
  const seen = new Map<string, string>();
  for (const [path, title] of siteMap) {
    const label = pill(title);
    if (label.length > PILL_MAX) {
      throw new Error(
        `bob-grounding: ${path} would render a ${label.length}-character link pill ` +
          `(${JSON.stringify(label)}). Put the NAME first, then " : " or " — ", ` +
          `then the description. See the comment above siteMap.`,
      );
    }
    const clash = seen.get(label);
    if (clash) {
      throw new Error(
        `bob-grounding: ${path} and ${clash} would both render a pill labelled ` +
          `${JSON.stringify(label)}. The part before " : " or " — " has to name ` +
          `the page, not its category.`,
      );
    }
    seen.set(label, path);
  }

  const pagesText = siteMap.map(([path, title]) => `${path}|${title}`).join("\n");

  const fleetText = devices.join("\n");
  const corpusText = corpus.join("\n");
  const approxTokens = Math.round(
    (fleetText.length + corpusText.length) / CHARS_PER_TOKEN,
  );

  if (approxTokens > MAX_GROUNDING_TOKENS) {
    throw new Error(
      `bob-grounding: fleet + index estimate ${approxTokens} tokens, over the ` +
        `${MAX_GROUNDING_TOKENS} budgeted. The Worker's prompt shares num_ctx ` +
        `16384 with the excerpts, twelve turns of history and the answer. ` +
        `Trim a column out of the index; see the comment in this file.`,
    );
  }

  const payload = {
    schema: 1,
    generated: new Date().toISOString(),
    fleetGenerated: fleet.generated,
    counts: { devices: devices.length, corpus: corpus.length },
    approxTokens,
    // Field order in each corpus line, so the Worker's prompt can name it.
    corpusFields: "kind|slug|date|title|en",
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
