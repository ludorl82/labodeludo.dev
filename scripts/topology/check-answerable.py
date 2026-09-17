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
import datetime
import hashlib
import json
import os
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


# --------------------------------------------------------------------------
# Remembering verdicts
# --------------------------------------------------------------------------
#
# WHY. This gate asks production, and every ask costs six seconds of spacing
# against a per-IP limiter. The panel is largely the same eight questions from
# one night to the next — and on a low-traffic site it is mostly the CURATED
# list, which is a fixed file. Re-asking those every night buys nothing: the
# answer can only change when what Bob knows changes.
#
# KEYED ON THE GROUNDING, not on a clock alone. `bob-grounding.json` is what
# the Worker searches; if its bytes are unchanged, a question that was
# answered is still answered and one that was refused is still refused. When
# an article ships, the hash moves and every verdict is taken again.
#
# A TTL ON TOP, because the grounding is not the only thing that decides. The
# model behind the chat changes, and so do its prompt and its relevance floor,
# and none of those touch the grounding file. So a verdict also expires on its
# own after CACHE_TTL_DAYS — the same belt-and-braces shape as the periodic
# full pass in the nightly reconcile.
#
# INCONCLUSIVE IS NEVER CACHED. It means "could not be asked", which is not a
# fact about the question. Storing it would turn one bad network minute into a
# week of pretending to know.
CACHE_TTL_DAYS = 7


# Fields that move without anything Bob knows having changed. They are build
# stamps, and hashing them made the cache useless in production on its first
# night: arch-refresh.sh dispatches architecture.yml at the START of every run,
# which rebuilds the site and re-stamps `generated` — so the job invalidated
# its own cache every time, and two runs three minutes apart produced two
# different keys with identical content.
GROUNDING_STAMPS = ("generated", "fleetGenerated", "dispatchGenerated")


def grounding_key(path_or_text):
    """A short digest of what Bob currently knows, or "" when unavailable.

    Keyed on CONTENT, not on the file's bytes. The timestamps above are
    dropped; everything else is hashed canonically, so the key moves when an
    article ships, the fleet changes or the dispatch is rewritten — and stays
    put when the site is merely rebuilt.

    An empty key disables the cache rather than sharing one bucket for every
    grounding: a cache that cannot tell versions apart is worse than none.
    """
    if not path_or_text:
        return ""
    try:
        with open(path_or_text, "rb") as fh:
            raw = fh.read()
    except OSError:
        return ""
    try:
        doc = json.loads(raw)
        if isinstance(doc, dict):
            content = {k: v for k, v in doc.items() if k not in GROUNDING_STAMPS}
            raw = json.dumps(content, sort_keys=True,
                             ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    except (ValueError, TypeError):
        # Not the JSON we expect: hash the bytes rather than guess. A cache
        # that misses is slow; one keyed on a misparse is wrong.
        pass
    return hashlib.sha256(raw).hexdigest()[:16]


def cache_load(path):
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def cache_save(path, data):
    if not path:
        return
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
    except OSError as e:
        # A cache that cannot be written is a slow run, not a wrong one.
        print(f"check-answerable: could not write the cache: {e}", file=sys.stderr)


def cache_get(cache, key, question, now=None):
    """The remembered verdict, or None. Expiry and key mismatch both miss."""
    hit = cache.get(question)
    if not isinstance(hit, dict) or hit.get("grounding") != key or not key:
        return None
    try:
        when = datetime.datetime.fromisoformat(hit["at"])
    except (KeyError, ValueError):
        return None
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.timezone.utc)
    if (now - when).days >= CACHE_TTL_DAYS:
        return None
    v = hit.get("verdict")
    return v if v in ("ANSWERED", "REFUSED") else None


def cache_put(cache, key, question, verdict, now=None):
    if not key or verdict not in ("ANSWERED", "REFUSED"):
        return
    now = now or datetime.datetime.now(datetime.timezone.utc)
    cache[question] = {"grounding": key, "verdict": verdict,
                       "at": now.isoformat(timespec="seconds")}


def curl_argv(question):
    """The exact command used to ask, so a test can read it without a network.

    The Authorization header marks this as a CHECK rather than a question
    somebody wanted answered, and the Worker skips its popularity tally for it.
    Without that, this gate feeds the list it is meant to police: a question
    verified every morning gains a count every morning and climbs on the job's
    own traffic. The same secret already fetches the candidate list, and it
    buys nothing extra here — same answer, same rate limit.
    """
    payload = json.dumps({"messages": [{"role": "user", "content": question}]})
    argv = ["curl", "-sS", "--max-time", str(TIMEOUT_S), "-w", "\n%{http_code}",
            "-X", "POST", CHAT_URL, "-H", "content-type: application/json"]
    token = os.environ.get("BOB_POPULAR_TOKEN", "").strip()
    if token:
        argv += ["-H", f"authorization: Bearer {token}"]
    return argv + ["--data-binary", payload]


def ask(question):
    """Return (reply, links, limited, error).

    curl rather than urllib: the shield in front of the site answers 403 to
    Python's default User-Agent. Transport is a detail, but a detail that
    would have made every question look unanswerable.
    """
    p = subprocess.run(curl_argv(question), capture_output=True, text=True)
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
    ap.add_argument("--cache", help="file of remembered verdicts")
    ap.add_argument("--grounding",
                    help="bob-grounding.json — its digest keys the cache")
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
    key = grounding_key(a.grounding)
    cache = cache_load(a.cache)
    keep, dropped, unknown, remembered = [], [], [], 0
    asked = 0
    for q in questions:
        hit = cache_get(cache, key, q)
        if hit:
            remembered += 1
            v, detail = hit, "remembered (grounding unchanged)"
        else:
            # Spacing belongs to the ASK, not to the loop: a night that
            # remembers every verdict should cost no waiting at all, and
            # sleeping between cache hits would keep the six seconds while
            # removing the request they exist to space out.
            if asked:
                time.sleep(SPACING_S)
            asked += 1
            v, detail = verdict(q)
            cache_put(cache, key, q, v)
        print(f"  {v:13} {q}\n                {detail}")
        (keep if v == "ANSWERED" else dropped if v == "REFUSED" else unknown).append(q)
    cache_save(a.cache, cache)

    # Inconclusive is kept, deliberately: see the module docstring.
    keep += unknown
    print(f"check-answerable: {len(keep)} kept ({len(unknown)} unverified), "
          f"{len(dropped)} dropped as dead ends"
          + (f", {remembered} remembered" if remembered else ""))

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
