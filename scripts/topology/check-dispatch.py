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

    # A dispatch that mentions nothing that changed is worse than no dispatch:
    # it is filler dressed as news. If the fleet moved, say which part.
    if vocabulary and not any(v.lower() in text.lower() for v in vocabulary):
        fail(f"names none of what actually changed: {vocabulary}")

    print(f"check-dispatch: ok ({len(text)} chars, vocabulary {vocabulary or '[]'})")


if __name__ == "__main__":
    main()
