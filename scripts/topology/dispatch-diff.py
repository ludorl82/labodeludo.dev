#!/usr/bin/env python3
"""What changed in the fleet between two architecture.json snapshots.

Usage: dispatch-diff.py <previous.json> <current.json>

Prints a JSON object on stdout and exits 0. An empty diff is a normal night —
the common case — and the caller decides to skip rather than this failing.

**The model does not compute this.** It phrases it. That split is the whole
point: a model asked "what changed in the fleet?" can produce a fluent,
plausible sentence about a node that does not exist, and nothing downstream
would catch it. A model handed a computed list of names can only phrase what it
was given, and `check-dispatch.py` then refuses any name that is not in the
list. Deterministic where the facts are, generative only where the prose is.

Noise, deliberately ignored:

- `generated`, `verified`, `sources`, `topologyVersion` — timestamps and
  provenance move every single night and mean nothing about the fleet.
- `source` and `repo` on a node — the file a node was derived from changes when
  a resource is moved between .tf files, which is a refactor, not an event.
- `meta` — mostly domains and free-form detail; a change there is usually the
  same node described slightly differently.

What survives is the set of things a person would actually mention: a node
appeared, a node is gone, a node was renamed, or the wiring between them moved.
"""
import json
import sys


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def nodes_by_id(doc):
    return {n["id"]: n for n in doc.get("nodes", []) if "id" in n}


def edge_key(e):
    return (e.get("from", ""), e.get("kind", ""), e.get("to", ""))


def describe(n):
    return {"id": n["id"], "label": n.get("label", n["id"]), "kind": n.get("kind", "")}


def main():
    if len(sys.argv) != 3:
        print("usage: dispatch-diff.py <previous.json> <current.json>", file=sys.stderr)
        return 2

    prev, cur = load(sys.argv[1]), load(sys.argv[2])
    pn, cn = nodes_by_id(prev), nodes_by_id(cur)

    added = [describe(cn[i]) for i in sorted(set(cn) - set(pn))]
    removed = [describe(pn[i]) for i in sorted(set(pn) - set(cn))]
    renamed = [
        {"id": i, "from": pn[i].get("label", i), "to": cn[i].get("label", i)}
        for i in sorted(set(pn) & set(cn))
        if pn[i].get("label") != cn[i].get("label")
    ]

    pe = {edge_key(e) for e in prev.get("edges", [])}
    ce = {edge_key(e) for e in cur.get("edges", [])}
    # Edges are reported as counts plus a couple of examples. A night that
    # rewires twenty links is not twenty sentences; it is one sentence with a
    # number in it, and the examples exist so the phrasing can be concrete.
    edges_added = sorted(ce - pe)
    edges_removed = sorted(pe - ce)

    out = {
        "added": added,
        "removed": removed,
        "renamed": renamed,
        "edgesAdded": len(edges_added),
        "edgesRemoved": len(edges_removed),
        "edgeExamples": [
            {"from": a, "kind": k, "to": b} for a, k, b in (edges_added[:3] + edges_removed[:3])
        ],
        # Every name the prose is allowed to use. check-dispatch.py holds the
        # sentence to exactly this vocabulary.
        "vocabulary": sorted(
            {n["label"] for n in added + removed}
            | {r["from"] for r in renamed}
            | {r["to"] for r in renamed}
        ),
    }
    out["empty"] = not (added or removed or renamed or edges_added or edges_removed)
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
