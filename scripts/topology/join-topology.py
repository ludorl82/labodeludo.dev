#!/usr/bin/env python3
"""Join the four public snapshots' topology.json into src/data/architecture.json.

Usage: join-topology.py <dir-with-checkouts> [out.json]

<dir-with-checkouts> holds clones of nixos-iac-public, k3s-iac-public,
aws-iac-public and cloudflare-iac-public. This script never sees the private
repos — the snapshots' sanitizers are the trust boundary (see README.md).

Beyond the mechanical merge it does three things:
1. Validates each file against the contract (version, layer, node shape,
   id namespaces) and refuses dangling edge endpoints after the merge.
2. Adds the cross-layer hostname joins: a `dns:` node whose hostname appears
   in a cluster route's `meta.hosts` gains a `serves` edge from that route —
   that is the "follow a request" seam between the edge and the cluster.
3. Runs a positive allowlist over every string in the output: only
   documentation addressing (RFC 5737 / 3849 / 198.18) and example-family
   domains may appear. It deliberately knows nothing about the real names —
   a denylist here would BE the leak — so anything outside the allowed
   shapes fails the build.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

EXPECTED = {
    "nixos-iac-public": "hardware",
    "k3s-iac-public": "cluster",
    "aws-iac-public": "cloud",
    "cloudflare-iac-public": "edge",
}
NODE_NS = ("host", "cluster", "app", "workload", "route", "instance",
           "lambda", "bucket", "tunnel", "dns", "access", "external")
ID_RE = re.compile(r"^[a-z]+:[A-Za-z0-9.:/@_-]+$")

def die(msg):
    print(f"join-topology: {msg}", file=sys.stderr)
    sys.exit(1)

if len(sys.argv) not in (2, 3):
    die("usage: join-topology.py <dir-with-checkouts> [out.json]")
base = sys.argv[1]
out_path = sys.argv[2] if len(sys.argv) == 3 else os.path.join(
    os.path.dirname(__file__), "..", "..", "src", "data", "architecture.json")

nodes, edges, sources = {}, [], {}
for repo, layer in EXPECTED.items():
    path = os.path.join(base, repo, "topology.json")
    if not os.path.isfile(path):
        die(f"{path} missing — snapshot not cloned or emitter never ran")
    data = json.load(open(path, encoding="utf-8"))
    if data.get("topologyVersion") != 1:
        die(f"{repo}: unknown topologyVersion {data.get('topologyVersion')}")
    if data.get("layer") != layer or data.get("repo") != repo:
        die(f"{repo}: layer/repo mismatch ({data.get('layer')}, "
            f"{data.get('repo')})")
    for n in data["nodes"]:
        for field in ("id", "kind", "label", "layer", "source"):
            if not isinstance(n.get(field), str) or not n[field]:
                die(f"{repo}: node missing {field}: {n}")
        if not ID_RE.match(n["id"]) or n["id"].split(":")[0] not in NODE_NS:
            die(f"{repo}: bad node id {n['id']}")
        if n["id"] in nodes:
            # external: hors-IaC hardware may legitimately be referenced by
            # several layers (the NAS from both k3s and nixos) — merge the
            # evidence instead of failing; any other namespace colliding is
            # still a contract violation
            if n["id"].startswith("external:"):
                prev_node = nodes[n["id"]]
                for k, v in n.get("meta", {}).items():
                    if k in prev_node["meta"] and prev_node["meta"][k] != v:
                        prev_node["meta"][k] = f"{prev_node['meta'][k]}; {v}"
                    else:
                        prev_node["meta"][k] = v
                seen_by = prev_node["meta"].setdefault(
                    "seenBy", [prev_node["repo"]])
                seen_by.append(repo)
                continue
            die(f"duplicate node id across snapshots: {n['id']}")
        n["repo"] = repo
        nodes[n["id"]] = n
    for e in data["edges"]:
        if not (isinstance(e.get("from"), str) and isinstance(e.get("to"), str)
                and isinstance(e.get("kind"), str)):
            die(f"{repo}: malformed edge {e}")
        edges.append(e)
    # provenance: the snapshot commit this layer was read from
    try:
        sha = subprocess.check_output(
            ["git", "-C", os.path.join(base, repo), "rev-parse",
             "--short", "HEAD"], text=True).strip()
        date = subprocess.check_output(
            ["git", "-C", os.path.join(base, repo), "log", "-1",
             "--format=%cI"], text=True).strip()
    except subprocess.CalledProcessError:
        sha, date = "unknown", "unknown"
    sources[repo] = {"commit": sha, "date": date}

for e in edges:
    for end in (e["from"], e["to"]):
        if end not in nodes:
            die(f"dangling edge endpoint: {end} ({e})")

# cross-layer hostname join: route.meta.hosts <-> dns nodes
hosts_to_route = {}
for n in nodes.values():
    if n["kind"] == "route":
        for h in n.get("meta", {}).get("hosts", []):
            hosts_to_route.setdefault(h, []).append(n["id"])
n_serves = 0
for n in nodes.values():
    if n["kind"] == "dns":
        for rid in hosts_to_route.get(n["label"], []):
            edges.append({"from": rid, "to": n["id"], "kind": "serves"})
            n_serves += 1

# ---------------------------------------------------------------------------
# Positive allowlist over every string in the merged output — shared with
# scan-public.py, see allowlist.py. Knows only what fictional data looks
# like, never what real data looks like.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from allowlist import Leak, walk  # noqa: E402

result = {
    "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "topologyVersion": 1,
    "sources": sources,
    "nodes": sorted(nodes.values(), key=lambda n: n["id"]),
    "edges": sorted(edges, key=lambda e: (e["from"], e["to"], e["kind"])),
}
try:
    walk({"nodes": result["nodes"], "edges": result["edges"],
          "sources": sources}, "$")
except Leak as e:
    die(str(e))

os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, sort_keys=True)
    f.write("\n")
print(f"join-topology: {len(result['nodes'])} nodes, "
      f"{len(result['edges'])} edges ({n_serves} cross-layer serves) "
      f"-> {out_path}")
