#!/usr/bin/env python3
"""What changed in the STRUCTURE the drawing depends on, since it was last drawn.

The weekly job used to open a model session for each drawing every time a
public snapshot moved, and ask it to decide whether anything structural had
changed. Most weeks nothing had: both components already compute their counts,
their rows and their layout from the data, so a new app or one more public name
redraws itself at build time. What a session is actually needed for is the
change the component cannot absorb — a node kind it has never seen, an edge
crossing layers in a new way, a fleet class or a network its label maps do not
know, a new rack.

This computes exactly that, deterministically, and hands the list to the
session, so the model is told what to fix instead of hunting for it — the shape
the dispatch already uses: the diff is computed, the drawing is written.

IT IS A HINT FOR B, NOT A REASON TO SKIP B. Replayed against the seven real
nightly redraws of the architecture (2026-08-07 → 08-23), it came back empty on
three of them. Two were changes today's component absorbs by itself (a new
hors-IaC box, a fleet dedup rule). The third was not: on 2026-08-08 the session
corrected a false sentence — "WireGuard, seul port exposé de la maison" — from
what it read in the SNAPSHOTS, a fact architecture.json does not carry. A skip
on an empty delta would have left that lie up. So B always gets its session
when the snapshots moved, and `skip` is only ever true for D.

D IS DIFFERENT: it reads fleet.json and nothing else. When the devices and the
racks are identical to what the last rack drawing was made from, and the prompt
has not changed either, there is nothing a session could learn — `skip: true`.

BASELINE. The data as it stood at the last commit that touched the component.
Nothing is stored between runs: the history is the state. A component with no
history at all is reported as changed.

Usage:
  diagram-delta.py --site <site-dir> --component B|D [--out delta.json]

Exit 0 whatever the answer (`empty` says it); non-zero only when it cannot
tell, and the driver treats that as "changed" rather than as "nothing to do".
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

COMPONENTS = {
    "B": "src/components/LiveArchDiagram.astro",
    "D": "src/components/RackDiagram.astro",
}
ARCH = "src/data/architecture.json"
FLEET = "src/data/fleet.json"
PROMPT_D = "scripts/topology/prompts/rack-diagram.md"


def git(site, *args):
    return subprocess.run(["git", "-C", site, *args], capture_output=True,
                          text=True, check=True).stdout


def load_at(site, rev, path):
    """The file at a revision, or None when it did not exist there."""
    try:
        return json.loads(git(site, "show", f"{rev}:{path}"))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def ns(node_id):
    return node_id.split(":", 1)[0]


def map_keys(source, name):
    """Keys of a `const NAME: Record<string, string> = { ... }` literal.

    The label maps ARE the component's vocabulary: a class or a network they do
    not know renders as its raw key, which is precisely the kind of change a
    build cannot flag and a reader notices.
    """
    m = re.search(rf"const {name}\b[^=]*=\s*\{{(.*?)\n\}};", source, re.S)
    if not m:
        return None
    return set(re.findall(r'^\s*"?([\w-]+)"?\s*:', m.group(1), re.M))


# ---------------------------------------------------------------------------
# signatures: sets of facts whose change the component cannot absorb alone
# ---------------------------------------------------------------------------
def arch_signature(arch, source):
    nodes = arch.get("nodes", []) if arch else []
    edges = arch.get("edges", []) if arch else []
    kind_of = {n["id"]: n.get("kind", ns(n["id"])) for n in nodes}
    hosts = [n for n in nodes if n.get("kind") == "host"]
    sig = {
        "types de nœuds": {n.get("kind", "?") for n in nodes},
        "types d'arêtes (type, de, vers)": {
            f'{e.get("kind")} {kind_of.get(e.get("from"), ns(e.get("from", "?")))}'
            f'→{kind_of.get(e.get("to"), ns(e.get("to", "?")))}'
            for e in edges
        },
        "classes de machines": {str(h.get("meta", {}).get("class")) for h in hosts},
        "rôles k3s par classe": {
            f'{h.get("meta", {}).get("k3sRole")}@{h.get("meta", {}).get("class")}'
            for h in hosts if h.get("meta", {}).get("k3sRole")
        },
        # the drawing asserts these are singular — "l'unique tunnel",
        # "l'unique control-plane"; a second one breaks a sentence, not a count
        "singletons": {
            f"{k}={sum(1 for n in nodes if n.get('kind') == k)}"
            for k in ("tunnel", "cluster")
        } | {f"cloud-vm={sum(1 for h in hosts if h.get('meta', {}).get('class') == 'cloud-vm')}"},
    }
    # ids and kinds the component names literally must still exist
    known_ids = set(kind_of)
    known_kinds = sig["types de nœuds"]
    sig["ids nommés par le composant, absents des données"] = {
        i for i in re.findall(r'byId\("([^"]+)"\)', source) if i not in known_ids
    }
    sig["types nommés par le composant, absents des données"] = {
        k for k in re.findall(r'kind\("([^"]+)"\)', source) if k not in known_kinds
    }
    return sig


def fleet_vocabulary(devices, source, maps):
    sig = {}
    for field, map_name in maps:
        values = {str(d[field]) for d in devices if d.get(field)}
        sig[f"valeurs de `{field}`"] = values
        known = map_keys(source, map_name) if map_name else None
        if known is not None:
            sig[f"`{field}` inconnus de {map_name}"] = values - known
    return sig


def fleet_signature_b(fleet, arch, source):
    # Only the devices the fleet band actually renders go through the label
    # maps: anything architecture.json already names is drawn above, by its
    # topology node, and never meets CLASS_FR. Same dedup as the component.
    drawn = {n.get("label") for n in (arch or {}).get("nodes", [])
             if n.get("kind") in ("host", "external")}
    ups_in_topology = any(n.get("id", "").startswith("external:ups")
                          for n in (arch or {}).get("nodes", []))
    extras = [d for d in (fleet or {}).get("devices", [])
              if d.get("name") not in drawn
              and not (d.get("class") == "ups" and ups_in_topology)]
    return fleet_vocabulary(extras, source,
                            [("class", "CLASS_FR"), ("network", "NET_FR")])


def fleet_signature_d(fleet, source):
    devices = (fleet or {}).get("devices", [])
    sig = fleet_vocabulary(devices, source, [("network", "NETWORK_LABEL"),
                                             ("class", None)])
    tones = map_keys(source, "NETWORK_TONE")
    if tones is not None:
        sig["`network` inconnus de NETWORK_TONE"] = sig["valeurs de `network`"] - tones
    racked = {d.get("location") for d in devices
              if isinstance(d.get("rackOrder"), (int, float)) and d.get("location")}
    sig["baies occupées"] = racked
    titles = map_keys(source, "RACK_TITLE")
    if titles is not None:
        sig["baies sans titre dans RACK_TITLE"] = racked - titles
    sig["clés de racks"] = set((fleet or {}).get("racks", {}).keys())
    # a new FIELD is a new kind of fact the drawing has never been asked to
    # show — reported only while the component does not read it at all
    sig["champs des appareils que le composant ne lit pas"] = {
        k for d in devices for k in d if not re.search(rf"\b{re.escape(k)}\b", source)}
    return sig


def compare(prev, cur):
    changes = []
    for key in sorted(set(prev) | set(cur)):
        a, b = prev.get(key, set()), cur.get(key, set())
        # "absent" sets are problems in their own right: report what is there
        # NOW, not only what moved, or a gap that predates the baseline hides
        if "absent" in key or "inconnus" in key or "sans titre" in key:
            if b:
                changes.append(f"{key} : {', '.join(sorted(b))}")
            continue
        added, removed = sorted(b - a), sorted(a - b)
        if added:
            changes.append(f"{key} — nouveau : {', '.join(added)}")
        if removed:
            changes.append(f"{key} — disparu : {', '.join(removed)}")
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--component", required=True, choices=sorted(COMPONENTS))
    ap.add_argument("--out")
    a = ap.parse_args()

    comp = COMPONENTS[a.component]
    site = a.site
    base = git(site, "log", "-1", "--format=%H", "--", comp).strip()
    cur_source = (Path(site) / comp).read_text(encoding="utf-8")
    cur_arch = json.loads((Path(site) / ARCH).read_text(encoding="utf-8"))
    fleet_path = Path(site) / FLEET
    cur_fleet = json.loads(fleet_path.read_text(encoding="utf-8")) if fleet_path.exists() else {}

    if not base:
        result = {"component": a.component, "base": None, "empty": False,
                  "skip": False,
                  "changes": ["aucun historique pour ce composant — pas de référence"]}
    else:
        prev_arch = load_at(site, base, ARCH) or {}
        prev_fleet = load_at(site, base, FLEET) or {}
        if a.component == "B":
            # judged against the CURRENT source on both sides: a label map the
            # session extended last week must not report its old gap forever
            prev = arch_signature(prev_arch, cur_source) | fleet_signature_b(prev_fleet, prev_arch, cur_source)
            cur = arch_signature(cur_arch, cur_source) | fleet_signature_b(cur_fleet, cur_arch, cur_source)
        else:
            prev = fleet_signature_d(prev_fleet, cur_source)
            cur = fleet_signature_d(cur_fleet, cur_source)
        changes = compare(prev, cur)
        skip = False
        if a.component == "D":
            strip = lambda f: {"devices": (f or {}).get("devices", []),
                               "racks": (f or {}).get("racks", {})}
            try:
                prompt_then = git(site, "show", f"{base}:{PROMPT_D}")
            except subprocess.CalledProcessError:
                prompt_then = None
            prompt_now = (Path(site) / PROMPT_D).read_text(encoding="utf-8") \
                if (Path(site) / PROMPT_D).exists() else None
            skip = (not changes and strip(prev_fleet) == strip(cur_fleet)
                    and prompt_then == prompt_now)
        result = {"component": a.component, "base": base[:12],
                  "empty": not changes, "skip": skip, "changes": changes}

    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
