#!/usr/bin/env python3
"""Gate the suggested questions before any visitor sees them.

Usage: check-openers.py <openers.json> <candidates.json>

These are the only strings on this site that a stranger wrote. Everything else
— articles, diagrams, Bob's own answers — is either authored here or derived
from data that is. So this file is the whole trust boundary, and it is
deliberately paranoid: over-rejecting costs one fewer suggestion, and
under-rejecting puts someone else's words on a page with Ludo's name on it.

Four rules, in the order they matter:

1. **Verbatim.** Every published question must appear character-for-character
   in the candidate list the Worker produced. The session selects; it does not
   write, improve or merge. A question nobody asked cannot get through, and
   neither can a real question with a word quietly changed.
2. **Shape.** A question, in the length a button can hold, ending in a question
   mark, no newlines, no markup, no addresses.
3. **Vocabulary.** A blocklist of the obvious, because "obscene" has no
   mechanical definition and pretending otherwise would be worse than saying
   what this actually checks.
4. **Volume.** At most four. The panel has room for four.

What this cannot do is judge intent. A perfectly clean sentence can still be
someone using the suggestion slot as a billboard. That is why the session that
selects has instructions to reject anything that is not a question about this
homelab, why the result is a commit rather than a live write, and why the
commit is small enough to read.
"""
import json
import re
import sys

MAX_OPENERS = 4
MIN_LEN, MAX_LEN = 12, 70

# Deliberately short and blunt. This is a coarse net for the unmistakable; the
# session's judgment and the commit review are what catch everything subtler.
BLOCKED = re.compile(
    r"\b(fuck|shit|bitch|cunt|nigg|faggot|rape|porn|xxx|viagra|casino|crypto\s*giveaway"
    r"|osti|tabarnak|calisse|criss|estie|salope|encul)",
    re.IGNORECASE,
)
ADDRESSY = re.compile(r"(https?://|www\.|@|\+?\d[\d\s().-]{6,})", re.IGNORECASE)
MARKUP = re.compile(r"[<>{}\[\]\\|`]")


def fail(msg):
    print(f"check-openers: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("usage: check-openers.py <openers.json> <candidates.json>", file=sys.stderr)
        sys.exit(1)

    openers = json.load(open(sys.argv[1], encoding="utf-8")).get("openers", [])
    candidates = json.load(open(sys.argv[2], encoding="utf-8")).get("candidates", [])
    allowed = {c["text"] for c in candidates if isinstance(c, dict) and "text" in c}

    if not isinstance(openers, list):
        fail("openers must be a list")
    if len(openers) > MAX_OPENERS:
        fail(f"{len(openers)} openers, at most {MAX_OPENERS} fit the panel")
    if len(set(openers)) != len(openers):
        fail("the same question twice")

    for q in openers:
        if not isinstance(q, str):
            fail(f"not a string: {q!r}")
        if q not in allowed:
            fail(f"{q!r} is not verbatim in the candidates — selected, not written, is the rule")
        if not (MIN_LEN <= len(q) <= MAX_LEN):
            fail(f"{q!r} is {len(q)} chars, outside {MIN_LEN}–{MAX_LEN}")
        if "\n" in q:
            fail(f"{q!r} contains a newline")
        if not q.rstrip().endswith("?"):
            fail(f"{q!r} is not a question")
        if BLOCKED.search(q):
            fail(f"{q!r} hits the blocklist")
        if ADDRESSY.search(q):
            fail(f"{q!r} looks like an address or a link")
        if MARKUP.search(q):
            fail(f"{q!r} contains markup characters")

    print(f"check-openers: ok ({len(openers)} question(s), all verbatim from {len(allowed)} candidates)")


if __name__ == "__main__":
    main()
