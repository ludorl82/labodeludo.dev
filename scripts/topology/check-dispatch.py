#!/usr/bin/env python3
"""Hold the nightly dispatch to the diff it was given.

Usage: check-dispatch.py <dispatch.json> <diff.json>

`scan-public.py` already asks "does this leak?". This asks the other question:
"is this true?" — or as close to it as a mechanical check can get. The model is
handed a computed list of what changed and told to phrase it. This refuses the
result if the prose names a machine that is not on that list.

That is the failure worth guarding. A fluent sentence about a node that never
existed reads exactly like a fluent sentence about one that did, and Bob's
whole value is that he does not invent. The prose half of this feature is the
only place a hallucination could enter, so it gets a gate.

Machine-name-shaped tokens are what get checked — kebab-case (`access-audit`,
`gpu-01`) and letters-then-digits (`worker4`) — because those are how hosts,
workloads and nodes are named here. Ordinary technical vocabulary passes: a
dispatch may say "un nœud Kubernetes" without Kubernetes being a fleet node.
Exit 1 on the first violation, printing what and why. Read-only.
"""
import json
import re
import sys

# Generic technology names that are prose, not fleet identifiers. Kept short on
# purpose: every addition here is a hole in the gate, so a name belongs on this
# list only if it can never be a node in this topology.
TECH = {
    "home-assistant", "uptime-kuma", "cloudflare", "kubernetes", "k3s", "nixos",
    "opentofu", "wireguard", "ollama", "qwen3", "claude-code", "cloudflare-iac",
    "nixos-iac", "aws-iac", "k3s-iac", "labodeludo", "s3", "dns", "vlan",
}

# Hostname-shaped: kebab-case, or a word ending in digits.
NAMEISH = re.compile(r"\b(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)+|[a-z]{2,}[0-9]+)\b")

MAX_CHARS = 400


# Numbers the prose is allowed to use. Written out in French as well as in
# digits, because a dispatch says "quatre liens", not "4 liens".
NUM_WORDS = {
    "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7,
    "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12, "treize": 13,
    "quatorze": 14, "quinze": 15, "seize": 16, "vingt": 20,
}
# `un`/`une` are deliberately absent: in French they are articles far more
# often than numerals, and a check that cannot tell "un lien de plus" from
# "un nœud est apparu" would refuse correct prose. One is the one count this
# gate cannot verify.
#
# Digits inside a machine name are not numbers either — `gpu-01` is a name,
# and NAMEISH above has already vouched for it. Stripping those tokens first
# is what stops "01" from being read as a count.
DIGITS = re.compile(r"\b\d+\b")


def numbers_in(text: str) -> set:
    prose = NAMEISH.sub(" ", text.lower())
    found = {int(d) for d in DIGITS.findall(prose)}
    for word, value in NUM_WORDS.items():
        if re.search(rf"\b{word}\b", prose):
            found.add(value)
    return found


def fail(msg):
    print(f"check-dispatch: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("usage: check-dispatch.py <dispatch.json> <diff.json>", file=sys.stderr)
        sys.exit(1)

    dispatch = json.load(open(sys.argv[1], encoding="utf-8"))
    diff = json.load(open(sys.argv[2], encoding="utf-8"))

    text = (dispatch.get("dispatch") or "").strip()
    if not text:
        fail("dispatch text is empty")
    if len(text) > MAX_CHARS:
        fail(f"dispatch is {len(text)} chars, over the {MAX_CHARS} limit — it is a line, not a report")
    if "\n" in text:
        fail("dispatch must be a single paragraph, no newlines")

    vocabulary = diff.get("vocabulary", [])
    lower_vocab = " ".join(vocabulary).lower()

    # Every machine-shaped token must come from the diff.
    for token in sorted(set(NAMEISH.findall(text.lower()))):
        if token in TECH:
            continue
        if token not in lower_vocab:
            fail(
                f"names {token!r}, which is not in tonight's diff. "
                f"Allowed: {vocabulary or '(nothing changed)'}"
            )

    # Every COUNT in the prose must be one the diff actually contains. The
    # sentence is generated, the numbers are not: on 2026-09-08 a run wrote
    # "cinq liens en plus" for a diff of four, and this gate accepted it —
    # it vouched for machine names and nothing else. A wrong number reads
    # exactly like a right one, which is the whole reason the diff is computed
    # upstream instead of counted by a model.
    counts = diff.get("counts") or {
        "added": len(diff.get("added", [])),
        "removed": len(diff.get("removed", [])),
        "renamed": len(diff.get("renamed", [])),
        "edgesAdded": diff.get("edgesAdded", 0),
        "edgesRemoved": diff.get("edgesRemoved", 0),
    }
    allowed = {int(v) for v in counts.values() if isinstance(v, (int, float))}
    for n in sorted(numbers_in(text)):
        if n not in allowed:
            fail(
                f"says {n}, which is not a count in tonight's diff. "
                f"Allowed: {sorted(allowed)}"
            )

    # A dispatch that mentions nothing that changed is worse than no dispatch:
    # it is filler dressed as news. If the fleet moved, say which part.
    if vocabulary and not any(v.lower() in text.lower() for v in vocabulary):
        fail(f"names none of what actually changed: {vocabulary}")

    print(f"check-dispatch: ok ({len(text)} chars, vocabulary {vocabulary or '[]'})")


if __name__ == "__main__":
    main()
