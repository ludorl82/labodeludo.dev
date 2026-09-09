// The one question the generated diagram's click answers: **le chemin** —
// which path through the system does this box sit on?
//
// Imported by BOTH the page (ArchGenerated.astro's client script) and the
// build-time checker (scripts/check-diagram-highlight.mjs). That sharing is
// the point: a checker that reimplements the traversal ends up attesting a
// logic the site no longer runs.
//
// WHAT THIS REPLACED, so it does not come back. The first version flattened
// every edge into an undirected adjacency, threw the eight edge kinds away,
// and bounded the walk with a hardcoded TERMINAL set of node namespaces plus
// a `cur !== start` exception. The blast radius then followed the density of
// the IaC graph rather than any meaning: `app:traefik` — the ingress six
// public names traverse — lit TWO boxes because its only edge was `part-of`
// the cluster, while a NAS lit seven. Nothing on screen explained either
// number.

export type Edge = { from: string; to: string; kind: string };
export type NodeKind = (id: string) => string;

/** Namespace of a node id: "app:traefik" -> "app". */
export const ns = (id: string): string => {
  const i = id.indexOf(":");
  return i === -1 ? id : id.slice(0, i);
};

// Nodes that everything is attached to. They LIGHT when a path reaches them
// but are never expanded, because walking through one connects every app in
// the lab to every other and turns any click into "the whole diagram".
// This is the honest, narrow version of the old TERMINAL hack: one hub, named
// and justified, instead of five namespaces chosen to stop an explosion.
const HUBS = new Set(["cluster"]);

/**
 * Orient one edge along the direction a request travels: public name first,
 * machine last. Returns [upstream, downstream].
 *
 * `part-of` is the subtle one — it is stored for two different relations and
 * they flow opposite ways. A route is an entry point INTO its app
 * (route -> app), while a workload is what the app runs once you are there
 * (app -> workload). Orienting both the same way is what would let a click
 * leak sideways from one app's route into another app's pods.
 */
function orient(e: Edge): [string, string] {
  switch (e.kind) {
    // dns -> tunnel | ingress app | external origin | bucket
    case "routes-to":
      return [e.from, e.to];
    // stored route -> dns; the request meets the name first
    case "serves":
      return [e.to, e.from];
    // access gate sits in front of the name it protects
    case "protects":
      return [e.from, e.to];
    case "part-of":
      return ns(e.from) === "workload" ? [e.to, e.from] : [e.from, e.to];
    case "pinned-to": // workload -> the machine it is pinned to
    case "member-of": // host -> cluster
    case "uses": // app|host -> bucket | external
    case "is": // instance -> host
      return [e.from, e.to];
    default:
      return [e.from, e.to];
  }
}

export type Graph = {
  down: Map<string, string[]>;
  up: Map<string, string[]>;
  /** oriented [upstream, downstream, kind], for explaining a hop */
  oriented: Array<[string, string, string]>;
};

export function buildGraph(edges: Edge[]): Graph {
  const down = new Map<string, string[]>();
  const up = new Map<string, string[]>();
  const oriented: Array<[string, string, string]> = [];
  for (const e of edges) {
    const [a, b] = orient(e);
    oriented.push([a, b, e.kind]);
    down.set(a, [...(down.get(a) ?? []), b]);
    up.set(b, [...(up.get(b) ?? []), a]);
  }
  return { down, up, oriented };
}

function walk(g: Graph, start: string, dir: "down" | "up"): Set<string> {
  const seen = new Set<string>();
  const q = [start];
  while (q.length) {
    const cur = q.shift()!;
    // a hub lights (it was added by its discoverer) but is never expanded
    if (cur !== start && HUBS.has(ns(cur))) continue;
    for (const n of g[dir].get(cur) ?? []) {
      if (n !== start && !seen.has(n)) {
        seen.add(n);
        q.push(n);
      }
    }
  }
  return seen;
}

/**
 * Every node on a path through `start`: what the request passed through to
 * get here, and where it goes next. Symmetric on purpose — clicking a public
 * name shows the machine it lands on, and clicking a machine shows which
 * public names end up on it. Both are the same question asked from two ends.
 */
export function pathThrough(g: Graph, start: string): Set<string> {
  const out = new Set<string>([start]);
  for (const id of walk(g, start, "down")) out.add(id);
  for (const id of walk(g, start, "up")) out.add(id);
  return out;
}

/** Nodes with no oriented edge at all — a click on one can only light itself. */
export function isolated(g: Graph, id: string): boolean {
  return !(g.down.get(id)?.length || g.up.get(id)?.length);
}
