// The generated diagram must stay CLICKABLE and its clicks must stay
// MEANINGFUL — checked against the built page, on every build.
//
// Why this exists. LiveArchDiagram.astro is rewritten by the weekly job, and
// the only guard on that rewrite was:
//
//     [ "$(grep -o 'data-node' "$ARCH" | wc -l)" -lt 10 ]
//
// a count of a string. It cannot tell whether the ids are REAL: a redraw that
// invented `host:coquile` would sail through and ship a box that lights
// nothing. That is precisely the defect this whole pass was about — boxes
// whose click means nothing — so the check has to run on meaning, not on
// spelling.
//
// It imports src/lib/arch-path.ts, the SAME traversal the page runs. A
// checker with its own copy drifts and ends up attesting logic the site
// retired.
//
// Run against the built site: `node scripts/check-diagram-highlight.mjs dist`.
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { buildGraph, pathThrough, isolated, ns } from "../src/lib/arch-path.ts";

const here = dirname(fileURLToPath(import.meta.url));
const root = process.argv[2] ?? "dist";
const page = join(root, "architecture", "index.html");

let html;
try {
  html = readFileSync(page, "utf8");
} catch {
  // prod builds without SHOW_LIVE_ARCH have no generated diagram; that is a
  // deliberate state, not a failure
  console.log("check-diagram-highlight: no /architecture page in this build");
  process.exit(0);
}
if (!html.includes('id="topo-edges"')) {
  console.log("check-diagram-highlight: diagram not enabled in this build");
  process.exit(0);
}

const arch = JSON.parse(
  readFileSync(join(here, "..", "src", "data", "architecture.json"), "utf8"),
);
const known = new Set(arch.nodes.map((n) => n.id));
const g = buildGraph(arch.edges);

const singles = [...html.matchAll(/data-node="([^"]+)"/g)].map((m) => m[1]);
const aggregates = [...html.matchAll(/data-nodes="([^"]+)"/g)].map((m) =>
  m[1].split(/\s+/).filter(Boolean),
);
const clickable = new Set([...singles, ...aggregates.flat()]);

const problems = [];

// 1. No ghost ids. The gap the old grep-count left wide open: a box that
//    names a node which does not exist lights nothing and says nothing.
for (const id of clickable) {
  if (!known.has(id)) problems.push(`unknown node id in the drawing: ${id}`);
}

// 2. The drawing must still be clickable at all.
if (singles.length < 10) {
  problems.push(
    `only ${singles.length} data-node boxes — the interactivity contract says a redraw must not strip them`,
  );
}

// 3. The request path needs entrances. Every public name is a starting
//    point; before this pass not one of the 14 was clickable, so the one
//    question a click answers had no way in. Written as a rule so the next
//    redraw cannot quietly drop them again.
const dnsNodes = arch.nodes.filter((n) => n.kind === "dns").map((n) => n.id);
const missingDns = dnsNodes.filter((id) => !clickable.has(id));
if (missingDns.length) {
  problems.push(
    `${missingDns.length}/${dnsNodes.length} public names are not clickable: ${missingDns.slice(0, 4).join(", ")}${missingDns.length > 4 ? "…" : ""}`,
  );
}

// 4. No box may light only itself without the page admitting it. An isolated
//    node is allowed — some hardware genuinely has no declared link — but it
//    must be isolated in the DATA, so the caption explains the dead click
//    instead of the reader concluding the page is broken.
for (const id of singles) {
  if (!known.has(id)) continue;
  if (pathThrough(g, id).size === 1 && !isolated(g, id)) {
    problems.push(`${id} lights only itself yet has edges — traversal bug`);
  }
}

// 5. A public name that DECLARES an origin must reach it, or the path stops
//    at the edge and the drawing has stopped describing the system. This is
//    the assertion that would have caught the original defect: app:traefik
//    had one edge, so six public names led nowhere.
//
//    Scoped to names with an origin on purpose. The Pages staging names are
//    served at the edge and have none — the first version of this rule failed
//    on them, and they were right and it was wrong.
const withOrigin = new Set(
  arch.edges
    .filter((e) => e.kind === "routes-to" && e.from.startsWith("dns:"))
    .map((e) => e.from),
);
const stranded = dnsNodes.filter((id) => {
  if (!withOrigin.has(id)) return false;
  const kinds = new Set([...pathThrough(g, id)].map(ns));
  return !(kinds.has("app") || kinds.has("external") || kinds.has("bucket"));
});
if (stranded.length) {
  problems.push(
    `public names whose path reaches nothing that serves them: ${stranded.join(", ")}`,
  );
}

// 6. The counts written on the drawing must match the data. The prompt asks
//    for this ("every COUNT comes from architecture.json"); nothing verified
//    it, and a stale number is the exact failure the generated page exists to
//    avoid.
const text = html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
const counts = [
  [arch.nodes.filter((n) => n.kind === "dns").length, "noms publics"],
  [arch.nodes.filter((n) => n.kind === "access").length, "apps Access"],
  [arch.nodes.filter((n) => n.kind === "app").length, "applications"],
];
for (const [n, label] of counts) {
  if (!text.includes(`${n} ${label}`)) {
    problems.push(`the drawing does not state "${n} ${label}" — count drifted`);
  }
}

// 7. The inventory bridge, both directions. It had rotted each way at once:
//    twelve nodes no role claimed (up from nine at launch, growing quietly
//    because roleForNode fails soft), and five ids claimed by roles that had
//    left the topology — which had emptied the `alimentation` role without
//    anyone noticing. Neither direction had a check.
//
//    The ceiling is 0 deliberately. A new app then breaks the build until
//    somebody decides where it belongs, which takes a minute; leaving it to
//    accumulate is what produced the pile in the first place. Raise this only
//    with a reason, never to make a build pass.
const UNCLAIMED_CEILING = 0;
const { INVENTORY, roleForNode } = await import("../src/lib/inventory.ts");
const GAP_KINDS = ["app", "host", "external", "instance", "cluster", "tunnel"];

const ghosts = Object.entries(INVENTORY).flatMap(([role, item]) =>
  (item.nodes ?? [])
    .filter((id) => !known.has(id))
    .map((id) => `${role} claims ${id}, which is not in the topology`),
);
problems.push(...ghosts);

const unclaimed = arch.nodes
  .filter((n) => GAP_KINDS.includes(n.kind) && !roleForNode(n.id))
  .map((n) => n.id);
if (unclaimed.length > UNCLAIMED_CEILING) {
  problems.push(
    `${unclaimed.length} node(s) no inventory role claims (ceiling ${UNCLAIMED_CEILING}): ${unclaimed.join(", ")}`,
  );
}

if (problems.length) {
  console.error("check-diagram-highlight: the generated diagram is not sound");
  for (const p of problems) console.error("  - " + p);
  process.exit(1);
}
console.log(
  `check-diagram-highlight: ${singles.length} boxes + ${aggregates.length} aggregates, ` +
    `${dnsNodes.length} public names clickable, all ids real`,
);
