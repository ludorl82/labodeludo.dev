#!/usr/bin/env python3
"""Pick tonight's slice of Ludo's own questions — the panel's third source.

WHY A THIRD SOURCE. The panel had two, and each answers a different question
about a string on the page. `check-openers.py` proves a visitor really typed
it, verbatim or not at all. `check-generated.py` proves Bob only wrote about
things the articles actually cover. Neither can express "Ludo thinks this one
is worth asking", and the request for one was reasonable — but it must not be
granted by feeding invented text into the verbatim half. The Worker says why
in as many words: that would launder invented text through the rule that is
the whole trust boundary.

So: a third list, with its own label in openers.json. Three sources, three
labels, none of them pretending to be another.

NO MODEL RUNS HERE. The other two halves ask one because they are choosing
from 40 counted candidates, or writing new text. This one selects from a list
a person already curated, so the only decisions left are which slice and
whether Bob can still answer it — and neither needs judgement. The selection
is a rotation keyed to the date: the same day gives the same slice on any
machine, consecutive days give different ones, and nothing has to be
remembered between runs.

THE ANSWERABILITY GATE STILL APPLIES, and it is the point. Every question here
was asked of production before being written down, but an article can be
unpublished and a retrieval floor can be retuned. `check-answerable.py` reposes
tonight's slice before it ships, exactly as it does for the other two sources.
A curated question that has gone stale is dropped like any other dead end.

Usage:
  openers-curated.py <curated.json> <out.json> [max-per-lang] [day-offset]
"""
import datetime
import json
import os
import sys


def load(path):
    """The list, as {"fr": [...], "en": [...]}. Missing is empty, not fatal.

    A site that has not written one yet is a normal state — the other two
    sources fill the panel exactly as they did before this existed.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {"fr": [], "en": []}
    out = {}
    for lang in ("fr", "en"):
        out[lang] = [q for q in doc.get(lang, [])
                     if isinstance(q, str) and q.strip()]
    return out


def rotate(items, offset, count):
    """`count` items starting at `offset`, wrapping once.

    Wrapping rather than clamping: a list shorter than the panel still fills
    what it can instead of showing the same head every night. Never repeats a
    question within one slice, which a naive modulo would do once the list is
    shorter than `count`.
    """
    if not items or count <= 0:
        return []
    n = len(items)
    picked, seen = [], set()
    for i in range(min(count, n)):
        q = items[(offset + i) % n]
        if q not in seen:
            seen.add(q)
            picked.append(q)
    return picked


def day_offset(today=None):
    """A rotation key with no stored state.

    The ordinal day number, so the slice is reproducible from the date alone:
    two machines running the same night agree, a re-run the same day is
    idempotent, and a job that skipped a night does not have to catch up.
    """
    return (today or datetime.date.today()).toordinal()


def main():
    if not 3 <= len(sys.argv) <= 5:
        print("usage: openers-curated.py <curated.json> <out.json> "
              "[max-per-lang] [day-offset]", file=sys.stderr)
        return 2
    src, out_p = sys.argv[1], sys.argv[2]
    per_lang = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    offset = int(sys.argv[4]) if len(sys.argv) > 4 else day_offset()

    lists = load(src)
    picked = []
    for lang in ("fr", "en"):
        picked += rotate(lists[lang], offset, per_lang)

    if not picked:
        # Not an error: an empty or missing list simply means this source has
        # nothing to say tonight, and the caller treats it as an empty half.
        print("openers-curated: nothing curated")

    with open(out_p, "w", encoding="utf-8") as fh:
        json.dump({"openers": picked}, fh, indent=2,
                  sort_keys=True, ensure_ascii=False)
        fh.write("\n")

    print(f"openers-curated: {len(picked)} question(s) — "
          f"{len(rotate(lists['en'], offset, per_lang))} en, "
          f"{len(rotate(lists['fr'], offset, per_lang))} fr "
          f"(rotation {offset % max(len(lists['fr']) or 1, 1)} "
          f"of {len(lists['fr'])} fr / {len(lists['en'])} en)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
