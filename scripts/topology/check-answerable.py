#!/usr/bin/env python3
"""Refuse a suggested question that Bob would not answer.

WHY THIS EXISTS. check-openers.py proves a question was really asked by a
visitor, verbatim. It cannot prove Bob has anything to say about it. On
2026-09-15 the panel was publishing « T'as un article sur Proxmox ? » — a
real question, correctly spelled, that production answers with « Ça, c'est
pas documenté — demande à Ludo. » A suggestion that leads to a refusal is
the worst thing the panel can produce: the visitor clicked the site's own
button and got a dead end.

So the check is the only one that can settle it: ask him, and drop what he
will not answer.

THREE VERDICTS, NOT TWO. "Did not answer" and "could not be asked" are
different facts and collapsing them is how a gate starts lying. The rate
limiter replies in 0.2 s with HTTP 429 and {"limited": true} — a structured
marker, so no sentence matching is needed to recognise it. A question that
came back inconclusive is retried, and if it stays inconclusive it is KEPT
rather than dropped: this gate exists to remove dead ends, and silently
deleting questions because the network hiccupped would be a worse failure
than the one it fixes. The count of inconclusive questions is reported, so
a broken endpoint shows up as a number instead of an empty panel.

DETECTING A REFUSAL. The refusal sentence is prescribed by the Worker's own
prompt (« ça, c'est pas documenté — demande à Ludo. »), so matching it is
matching a constant, not guessing at a model's mood. Even so, two signals
must agree — the marker AND a short reply carrying no links — because a real
answer can mention what is *not* documented on its way to saying what is.
That pairing is the same discipline the Worker uses for link detection.

Standing lesson this obeys: a keyword check is wrong more often than the
model it judges. So `--selftest` runs the detector against replies whose
verdict is known, including the traps, and refuses to be trusted until they
all pass.

Usage:
  check-answerable.py openers.json --filter     # drop the dead ends in place
  check-answerable.py openers.json              # verify only, non-zero if any
  check-answerable.py --selftest                # prove the detector first
"""
import argparse
import json
import re
import subprocess
import sys
import time

CHAT_URL = "https://labodeludo.dev/api/bob/chat"

# Spacing between questions. The limiter is per-IP and the daily job asks a
# handful in a row from one address; going flat out turns the whole batch into
# 429s, which the first run of this script did.
SPACING_S = 6.0
RETRY_BACKOFF_S = 25.0
TIMEOUT_S = 120

# The refusal, as the Worker's prompt prescribes it, in both languages. Kept
# loose on punctuation and accents because that is the part a model varies;
# the words are what it is told to say.
REFUSAL_MARKERS = (
    re.compile(r"pas\s+document", re.I),
    re.compile(r"\bnot\s+documented\b", re.I),
)
# Second signal: a refusal is terminal, so it is short and cites nothing. The
# prompt says so in as many words — "if you answer that something is not
# documented, stop there".
REFUSAL_MAX_CHARS = 240


def ask(question):
    """Return (reply, links, limited, error).

    curl rather than urllib: the shield in front of the site answers 403 to
    Python's default User-Agent. Transport is a detail, but a detail that
    would have made every question look unanswerable.
    """
    payload = json.dumps({"messages": [{"role": "user", "content": question}]})
    p = subprocess.run(
        ["curl", "-sS", "--max-time", str(TIMEOUT_S), "-w", "\n%{http_code}",
         "-X", "POST", CHAT_URL, "-H", "content-type: application/json",
         "--data-binary", payload],
        capture_output=True, text=True)
    if p.returncode != 0:
        return "", [], False, f"curl {p.returncode}: {p.stderr.strip()[:120]}"
    body, _, code = p.stdout.rpartition("\n")
    try:
        d = json.loads(body)
    except Exception:
        return "", [], False, f"non-JSON (HTTP {code})"
    limited = bool(d.get("limited")) or code.strip() == "429"
    return (d.get("answer") or d.get("reply") or ""), (d.get("links") or []), limited, ""


def is_refusal(reply, links):
    """Two signals must agree, so a real answer that merely mentions what is
    undocumented is not mistaken for a dead end."""
    if links:
        return False
    if len(reply) > REFUSAL_MAX_CHARS:
        return False
    return any(m.search(reply) for m in REFUSAL_MARKERS)


def verdict(question, asker=None):
    """ANSWERED / REFUSED / INCONCLUSIVE, with one retry past the limiter.

    `asker` is resolved at CALL time, not bound as a default: written
    `asker=ask`, the default freezes the function object at import and a test
    that replaces `ask` silently keeps talking to production. That is exactly
    what the first version of the tests did — they passed the network traffic
    off as a fake and reported the wrong verdicts.
    """
    asker = asker or ask
    for attempt in (1, 2):
        reply, links, limited, err = asker(question)
        if limited or err:
            if attempt == 1:
                time.sleep(RETRY_BACKOFF_S)
                continue
            return "INCONCLUSIVE", (err or "rate-limited twice")
        if not reply.strip():
            if attempt == 1:
                time.sleep(RETRY_BACKOFF_S)
                continue
            return "INCONCLUSIVE", "empty reply"
        return ("REFUSED" if is_refusal(reply, links) else "ANSWERED"), reply[:120]
    return "INCONCLUSIVE", "unreachable"


# --------------------------------------------------------------- selftest ---
# Replies captured from production on 2026-09-15, plus the traps that a naive
# check would get wrong. Ground truth is what the reply IS, not what the
# question looks like.
SELFTEST = [
    # the real refusal that started this
    ("Ça, c'est pas documenté — demande à Ludo.", [], True),
    ("That is not documented — ask Ludo.", [], True),
    # real answers captured from prod, none of them dead ends
    ("Here my friend, I run on qwen35-q4kl served by Ollama on a graphics "
     "card in the rack — that is me right now.", [], False),
    ("Y'a un article sur le montage du cluster k3s avec Claude Code pis "
     "celui où la grappe a fait une crise d'identité.", ["a", "b"], False),
    # TRAP: says "pas documenté" about one thing while answering about another,
    # and cites a link. Two signals disagree, so it is not a refusal.
    ("Le détail du BIOS n'est pas documenté, mais la conversion NixOS au "
     "complet est racontée ici.", ["a"], False),
    # TRAP: long reply mentioning the phrase in passing, no links. Length is
    # the second signal — a refusal stops, this one keeps going.
    ("Pas documenté officiellement, mais voici comment ça marche : le hook "
     "de game-mode draine le nœud, la HA bascule, la VM démarre, pis le "
     "passthrough attache la carte. Ça prend une trentaine de secondes en "
     "tout, pis le cluster reprend le travail après.", [], False),
    # TRAP: short, no links, and NOT a refusal — must not be swept up.
    ("Neuf nœuds.", [], False),
]


def selftest():
    bad = 0
    for reply, links, expected in SELFTEST:
        got = is_refusal(reply, links)
        if got != expected:
            bad += 1
            print(f"  MISMATCH expected refusal={expected} got={got}: {reply[:70]}")
    print(f"selftest: {len(SELFTEST) - bad}/{len(SELFTEST)} passed")
    return 1 if bad else 0


# ------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("openers", nargs="?")
    ap.add_argument("--filter", action="store_true",
                    help="rewrite the file keeping only the answerable questions")
    ap.add_argument("--min", type=int, default=1,
                    help="fail if fewer than this many survive")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.openers:
        ap.error("need an openers.json (or --selftest)")

    # The detector proves itself on every run. It is cheap, and a gate nobody
    # re-validates is how a saturated test survives for months.
    if selftest():
        print("check-answerable: SELFTEST FAILED — not trusting the verdicts")
        return 2

    doc = json.load(open(a.openers))
    questions = doc.get("openers", [])
    keep, dropped, unknown = [], [], []
    for i, q in enumerate(questions):
        if i:
            time.sleep(SPACING_S)
        v, detail = verdict(q)
        print(f"  {v:13} {q}\n                {detail}")
        (keep if v == "ANSWERED" else dropped if v == "REFUSED" else unknown).append(q)

    # Inconclusive is kept, deliberately: see the module docstring.
    keep += unknown
    print(f"check-answerable: {len(keep)} kept ({len(unknown)} unverified), "
          f"{len(dropped)} dropped as dead ends")

    if a.filter:
        doc["openers"] = keep
        with open(a.openers, "w") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")

    if len(keep) < a.min:
        print(f"check-answerable: only {len(keep)} left, need {a.min}")
        return 1
    return 0 if (a.filter or not dropped) else 1


if __name__ == "__main__":
    sys.exit(main())
